"""EL EXPERIMENTO QUE FALTABA: ¿el contexto mezclado SUPRIME la abstencion?

C.54 midio el caso donde la evidencia correcta ESTA presente -> el generador es robusto.
Pero ese es el mejor escenario para B0. El caso que importa es el INVERSO:

    preguntas SIN respuesta en el corpus.

HIPOTESIS (el corazon de la tesis, "saber cuando callarse"):
  - B0 mezcla dominios -> SIEMPRE encuentra algo semanticamente parecido de ALGUN dominio
    -> el generador ve "material relevante" -> RESPONDE (infraccion).
  - El sistema segregado busca en UN dominio -> si ahi no hay nada, el contexto es
    visiblemente pobre -> SE ABSTIENE (correcto).

Se mide: tasa de abstencion correcta de cada configuracion, mismo k, mismo generador.
"""
import sys, io, json, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from embedder import embed_query
from clasificador import _coseno, _softmax, _centroide_l2
from config import CLASIFICADOR_TEMP
from generador import generar_respuesta

SILOS = ["legal", "impositivo", "contable", "financiero"]
K, GAMMA = 3, 0.70

# Preguntas SIN respuesta en el corpus: plausibles en el dominio, pero el corpus NO las cubre.
# (el corpus tiene: 24.065/24.076 energia-gas, 11.683/821/RG830 fiscal, balances Transener/Neuquen/MSU)
SIN_RESPUESTA = [
    "¿Cuál es la alícuota del impuesto sobre los bienes personales para el período fiscal 2025?",
    "¿Qué requisitos exige el Código Penal para configurar el delito de evasión tributaria agravada?",
    "¿Cuál es el cuadro tarifario vigente de EDENOR para usuarios residenciales T1-R1?",
    "¿Qué establece la Ley de Contrato de Trabajo sobre el preaviso en despidos sin causa?",
    "¿Cuáles son los requisitos para inscribirse en el Registro de Generadores de Energía Renovable MATER?",
    "¿Qué porcentaje de aportes patronales corresponde al régimen de la seguridad social?",
    "¿Cuál fue el resultado neto de YPF en el ejercicio 2024?",
    "¿Qué dispone el Mercosur sobre el comercio transfronterizo de electricidad con Brasil?",
]

con = conectar(); cur = con.cursor()
cur.execute("SELECT silo, embedding::text FROM chunks")
E = {}
for s, v in cur.fetchall():
    E.setdefault(s, []).append(np.array(json.loads(v)))
proto = {s: np.array(_centroide_l2(v)) for s, v in E.items()}

def se_abstiene(r):
    t = r.strip().lower()
    return t.startswith("no tengo evidencia suficiente")

filas = []
print("¿EL CONTEXTO MEZCLADO SUPRIME LA ABSTENCION?")
print("preguntas SIN respuesta en el corpus · mismo k · mismo generador")
print()

for i, preg in enumerate(SIN_RESPUESTA, 1):
    q = np.array(embed_query(preg))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"
    # B0: top-k global (mezcla dominios)
    cur.execute("SELECT titulo, contenido, fuente, silo FROM chunks "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (vec, K))
    b0 = [{"titulo": a, "contenido": b, "fuente": c, "silo": d} for a, b, c, d in cur.fetchall()]
    # SEGREGADO: conjunto por cobertura acumulada (señal combinada)
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    mejor = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "ORDER BY embedding <=> %s::vector LIMIT 1", (vec, s, vec))
        r = cur.fetchone(); mejor[s] = float(r[0]) if r else 0.0
    comb = {s: dist[s] * max(mejor[s], 1e-6) for s in SILOS}
    tot = sum(comb.values()); p = {s: comb[s] / tot for s in SILOS}
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= GAMMA:
            break
    cur.execute("SELECT titulo, contenido, fuente, silo FROM chunks WHERE silo = ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (sel, vec, K))
    seg = [{"titulo": a, "contenido": b, "fuente": c, "silo": d} for a, b, c, d in cur.fetchall()]

    n_dom_b0 = len({DOMS := x["silo"] for x in b0})
    n_dom_seg = len({x["silo"] for x in seg})
    r_b0 = generar_respuesta(preg, b0); time.sleep(0.3)
    r_seg = generar_respuesta(preg, seg); time.sleep(0.3)
    a_b0, a_seg = se_abstiene(r_b0), se_abstiene(r_seg)
    filas.append({"pregunta": preg, "silos_b0": [x["silo"] for x in b0], "silos_seg": sel,
                  "abst_b0": a_b0, "abst_seg": a_seg, "resp_b0": r_b0, "resp_seg": r_seg})
    print(f"[{i}/{len(SIN_RESPUESTA)}] {preg[:58]}...")
    print(f"      B0  dominios={n_dom_b0}  ->  {'SE ABSTIENE (ok)' if a_b0 else '*** RESPONDE (infraccion) ***'}")
    print(f"      SEG silos={sel}  ->  {'SE ABSTIENE (ok)' if a_seg else '*** RESPONDE (infraccion) ***'}")
    print()

con.close()
n = len(filas)
out = Path(str(Path(__file__).resolve().parent.parent / "resultados") + r"\abstencion_resultados.json")
out.write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")
print("=" * 74)
print("ABSTENCION CORRECTA (deberia ser 100%: ninguna pregunta tiene respuesta en el corpus)")
print()
print(f"  B0 monolitico (contexto mezclado) : {sum(f['abst_b0'] for f in filas)}/{n}  ({sum(f['abst_b0'] for f in filas)/n:.0%})")
print(f"  SEGREGADO (contexto de 1-2 silos) : {sum(f['abst_seg'] for f in filas)}/{n}  ({sum(f['abst_seg'] for f in filas)/n:.0%})")
print()
disc = [(f['abst_seg'], f['abst_b0']) for f in filas if f['abst_seg'] != f['abst_b0']]
print(f"  casos discordantes: {len(disc)}  ·  a favor del segregado: {sum(1 for s,b in disc if s and not b)}"
      f"  ·  a favor de B0: {sum(1 for s,b in disc if b and not s)}")
