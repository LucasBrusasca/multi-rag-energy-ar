"""GOLDEN — PASO 2: sacar del corpus las ANCLAS de colision (articulos reales).

Por que asi (P2/P3 del PROTOCOLO_GOLDEN): la respuesta correcta NO la decide nadie por
criterio experto — sale del DATO. Se elige un chunk concreto, y el silo correcto es el
silo donde ESE chunk vive. Verificable, no opinable.

Lucas NO ejerce como contador: no se le puede pedir juicio de dominio. Lo unico que se
le pide (§4 paso 3 del protocolo) es COMPRENSION LECTORA: "¿este articulo responde esta
pregunta?". Por eso cada ancla se imprime con su TEXTO, para que pueda leerlo.

TERMINOS DE COLISION (descubiertos del corpus en el paso 1, no elegidos a dedo):
cada uno se usa MUCHO en exactamente dos silos y casi nada en los otros dos, y lo usan
VARIOS documentos distintos en cada silo (no es un documento a caballo).

Este script NO inventa preguntas: junta los pares de anclas (un chunk de cada silo del
par) para el mismo termino. La pregunta se redacta despues, sobre el texto del ancla.
"""
import sys, io, json, re
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
from db import conectar

# terminos que el paso 1 descubrio como colision genuina (no elegidos a mano)
TERMINOS = ["agentes", "compensación", "firme", "intereses", "plazos", "requisitos",
            "solicitud", "presentación", "constitución", "actualización"]
MIN_CHARS = 250          # el ancla tiene que tener sustancia para responder algo
MAX_POR_PAR = 3          # cuantos ejemplos mostrar por termino y silo

con = conectar(); cur = con.cursor()
cur.execute("SELECT id, silo, titulo, contenido, fuente, hierarchy FROM chunks")
filas = cur.fetchall(); con.close()
print(f"corpus {len(filas)} chunks\n")

# Un chunk sirve como ancla si el termino es CENTRAL (no incidental) y su articulo es
# PROPIO (no una referencia cruzada a otra norma).
#
# El articulo se acepta SOLO si aparece en los primeros CABEZA caracteres: un chunk que
# empieza con "ARTICULO 29 — ..." ES el articulo 29; uno que dice "...conforme con el
# Articulo 12, Seccion IV de las Normas de la CNV..." esta CITANDO otro articulo. La
# version anterior confundia las dos cosas y anclaba mal.
CABEZA = 120
RE_ART = re.compile(r"^\W{0,20}(?:ART[IÍ]CULO|Art\.)\s*\.?\s*(\d+)", re.I)

# Centralidad: cuantas veces aparece el termino por cada 1000 caracteres. Un chunk que
# lo nombra una vez de pasada no sirve para construir una pregunta sobre ese termino.
MIN_DENSIDAD = 1.2
BONUS_TITULO = 3.0        # si el termino esta en el titulo o la jerarquia, es EL tema

por_termino = defaultdict(lambda: defaultdict(list))
for cid, silo, tit, cont, fue, jer in filas:
    if len(cont) < MIN_CHARS:
        continue
    bajo = cont.lower()
    encabezado = (str(tit) + " " + " ".join(jer or [])).lower()
    m = RE_ART.match(cont.strip()[:CABEZA])
    art = m.group(1) if m else None
    for t in TERMINOS:
        veces = bajo.count(t)
        if not veces:
            continue
        densidad = veces * 1000.0 / len(cont)
        en_encabezado = t in encabezado
        if densidad < MIN_DENSIDAD and not en_encabezado:
            continue                      # lo menciona al pasar: no es el tema
        por_termino[t][silo].append({
            "id": cid, "silo": silo, "titulo": tit, "fuente": fue,
            "articulo": art, "jerarquia": jer or [], "texto": cont,
            "centralidad": round(densidad + (BONUS_TITULO if en_encabezado else 0), 2),
            "veces": veces,
        })

salida = []
for t in TERMINOS:
    silos = {s: v for s, v in por_termino[t].items() if v}
    if len(silos) < 2:
        continue
    # el par de colision = los dos silos con mas anclas para ese termino
    orden = sorted(silos, key=lambda s: -len(silos[s]))[:2]
    print("=" * 100)
    print(f"  «{t.upper()}»   {orden[0]} ⚔ {orden[1]}")
    print("=" * 100)
    for s in orden:
        # orden: primero los que tienen articulo PROPIO (anclaje (norma, articulo) =
        # clave primaria del protocolo), luego por centralidad del termino
        cands = sorted(silos[s], key=lambda c: (c["articulo"] is None, -c["centralidad"]))
        print(f"\n  --- SILO {s.upper()} ({len(silos[s])} anclas · "
              f"{sum(1 for c in silos[s] if c['articulo'])} con articulo propio) ---")
        for c in cands[:MAX_POR_PAR]:
            ident = f"Art. {c['articulo']}" if c["articulo"] else "(sin nro de art.)"
            print(f"\n   [id {c['id']}] {c['fuente']} · {ident} · "
                  f"centralidad {c['centralidad']} ({c['veces']}x)")
            if c["jerarquia"]:
                print(f"      seccion: {' > '.join(c['jerarquia'])}")
            frag = re.sub(r"\s+", " ", c["texto"])[:420]
            print(f"      «{frag}…»")
            salida.append({"termino": t, "par": orden, **{k: c[k] for k in
                          ("id", "silo", "titulo", "fuente", "articulo", "jerarquia")},
                          "texto": c["texto"][:1200]})
    print()

(SCR / "golden_anclas.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
print(f"\n{len(salida)} anclas guardadas en golden_anclas.json")
print(f"terminos con par completo: {len({a['termino'] for a in salida})}")
