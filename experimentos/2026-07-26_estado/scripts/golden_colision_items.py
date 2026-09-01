"""GOLDEN — PASO 3: items de COLISION con verificacion 100% automatica.

Lucas NO ejerce como contador ([[lucas-no-es-experto-dominio]]): no se le puede pedir
juicio de dominio NI verificacion de lectura. Todo control tiene que ser mecanico.

TRES CONTROLES, NINGUNO OPINABLE:

  1. ¿El articulo responde la pregunta?
     GARANTIZADO POR CONSTRUCCION: la pregunta se redacta DESDE el texto del articulo,
     y la etiqueta de silo es el silo donde ESE chunk vive (P2/P3 del protocolo). No es
     un juicio: es un hecho sobre la base.

  2. ¿La pregunta copia el texto? (fuga, P1)
     OVERLAP LEXICO = |palabras_pregunta ∩ palabras_chunk| / |palabras_pregunta|,
     sobre palabras de contenido. Numero, se declara por item. Si es alto, la pregunta
     se gana por coincidencia de palabras y no mide nada.

  3. ¿La pregunta es realmente de COLISION?
     Se la da al buscador SIN filtro de silo y se mira DONDE cae el top-1:
       · si cae en el silo del ancla -> la pregunta es FACIL, el monolitico ya la
         resuelve, NO sirve como item de colision (se marca, no se borra: sirve de
         control negativo)
       · si cae en OTRO silo -> es una colision REAL: el monolitico se equivoca y hay
         algo que medir. Estos son los items valiosos.
     Esto es exactamente el fenomeno que la tesis afirma, medido item por item.

Las preguntas se generan con el LLM local (Ollama, gratis) a partir del texto del
ancla, con temperatura 0. No hay API ni costo.
"""
import sys, io, json, re, time, urllib.request
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar

MODELO = "gemma4:latest"
OLLAMA = "http://localhost:11434/api/generate"
SEMILLA = 7
MAX_OVERLAP = 0.45        # por encima de esto la pregunta copia demasiado el texto
POR_SILO_TERMINO = 2      # cuantas anclas tomar por cada (termino, silo)

anclas = json.loads((SCR / "golden_anclas.json").read_text(encoding="utf-8"))
# se prioriza tener articulo propio y centralidad alta; y se limita por (termino, silo)
por_par = {}
for a in anclas:
    k = (a["termino"], a["silo"])
    por_par.setdefault(k, []).append(a)
elegidas = []
for k, v in por_par.items():
    v.sort(key=lambda a: (a["articulo"] is None, -a.get("centralidad", 0)))
    elegidas += v[:POR_SILO_TERMINO]
print(f"anclas elegidas: {len(elegidas)} sobre {len(anclas)} candidatas\n")

PROMPT = """Sos un redactor de preguntas de evaluación para un sistema documental.

A continuación tenés el texto de un artículo normativo argentino:

<articulo>
{texto}
</articulo>

Escribí UNA pregunta que este artículo responda, como la haría un profesional que
NO tiene el texto delante.

Reglas estrictas:
- La pregunta debe poder responderse SOLO con este artículo.
- Usá el término «{termino}» en la pregunta.
- NO copies frases del artículo: reformulá con otras palabras.
- NO menciones el número de artículo, ni el nombre de la norma, ni el organismo.
- Una sola oración, terminada en signo de pregunta.

Respondé SOLO la pregunta, sin comillas ni preámbulo."""


def generar(texto, termino):
    cuerpo = json.dumps({
        "model": MODELO, "prompt": PROMPT.format(texto=texto[:1500], termino=termino),
        "stream": False, "think": False,
        "options": {"temperature": 0, "seed": SEMILLA, "num_predict": 120},
    }).encode()
    try:
        p = urllib.request.Request(OLLAMA, data=cuerpo, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(p, timeout=600) as r:
            d = json.loads(r.read())
        if d.get("done_reason") == "length":
            return None, "TRUNCADO"
        t = (d.get("response") or "").strip().strip('"').strip()
        t = t.split("\n")[0].strip()
        if not t.endswith("?") or len(t) < 25:
            return None, f"MAL_FORMATO:{t[:60]}"
        return t, "OK"
    except Exception as e:
        return None, f"ERROR:{type(e).__name__}"


PAL = re.compile(r"[a-záéíóúñü]{4,}")
VACIAS = None   # no hace falta lista: se descartan por frecuencia documental abajo


def overlap(pregunta, texto, comunes):
    """fraccion de las palabras de contenido de la pregunta que estan en el chunk"""
    pp = {w for w in PAL.findall(pregunta.lower()) if w not in comunes}
    if not pp:
        return 1.0
    tt = set(PAL.findall(texto.lower()))
    return round(len(pp & tt) / len(pp), 3)


# ---------- corpus y buscador (mismo instrumento de produccion) ----------
con = conectar(); cur = con.cursor()
cur.execute("SELECT id, silo, titulo, contenido, fuente, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
ids = np.array([r[0] for r in filas])
silo = np.array([r[1] for r in filas])
X = np.array([json.loads(r[5]) for r in filas])
X = X / np.linalg.norm(X, axis=1, keepdims=True)
pos = {int(i): k for k, i in enumerate(ids)}

# palabras "comunes" = las que aparecen en mas del 20% de los chunks (sin lista a mano)
df = Counter()
for _, _, t, c, _, _ in filas:
    df.update(set(PAL.findall((str(t) + " " + c).lower())))
comunes = {w for w, k in df.items() if k > 0.20 * len(filas)}
print(f"palabras comunes descartadas del overlap: {len(comunes)}\n")

from embedder import embed_query

items, k = [], 0
print(f"{'#':>3s} {'termino':14s} {'silo':11s} {'ovl':>5s} {'top1':11s} {'veredicto'}")
for a in elegidas:
    k += 1
    q, motivo = generar(a["texto"], a["termino"])
    if motivo != "OK":
        print(f"{k:3d} {a['termino']:14s} {a['silo']:11s}   --   {'-':11s} descartado ({motivo[:40]})")
        continue
    ovl = overlap(q, a["texto"], comunes)
    # ¿donde cae el buscador SIN filtro de silo? (el monolitico)
    v = np.array(embed_query(q)); v /= np.linalg.norm(v)
    sims = X @ v
    orden = np.argsort(-sims)[:3]
    top1_silo = silo[orden[0]]
    encontro_ancla = int(ids[orden[0]]) == a["id"] or a["id"] in [int(ids[j]) for j in orden]
    if ovl > MAX_OVERLAP:
        ver = "FUGA (overlap alto)"
    elif top1_silo == a["silo"]:
        ver = "facil (control negativo)"
    else:
        ver = "*** COLISION REAL ***"
    items.append({"termino": a["termino"], "pregunta": q, "silo_correcto": a["silo"],
                  "fuente": a["fuente"], "articulo": a["articulo"], "chunk_id": a["id"],
                  "overlap": ovl, "top1_silo_monolitico": str(top1_silo),
                  "ancla_en_top3": bool(encontro_ancla), "veredicto": ver})
    print(f"{k:3d} {a['termino']:14s} {a['silo']:11s} {ovl:5.2f} {str(top1_silo):11s} {ver}")

(SCR / "golden_colision_items.json").write_text(
    json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")

print("\n" + "=" * 82)
c = Counter(i["veredicto"] for i in items)
print(f"  {len(items)} items generados de {k} anclas")
for v, n in c.most_common():
    print(f"     {n:3d}  {v}")
colisiones = [i for i in items if "COLISION" in i["veredicto"]]
print(f"\n  ITEMS DE COLISION UTILES: {len(colisiones)}")
print(f"  (el monolitico manda el top-1 al silo EQUIVOCADO -> hay algo que medir)")
if colisiones:
    print(f"  overlap medio de esos: {np.mean([i['overlap'] for i in colisiones]):.2f}")
    print(f"  el ancla igual aparece en el top-3: "
          f"{sum(i['ancla_en_top3'] for i in colisiones)}/{len(colisiones)}")
print(f"\n  guardado en golden_colision_items.json")
