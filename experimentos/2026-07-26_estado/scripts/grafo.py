"""IDEA DE LUCAS: ¿y si metemos grafo? — se prueba la arista mas barata primero.

Señal tipo-grafo SIN infraestructura nueva (solo un JOIN): en vez de votar por el SILO
de cada chunk recuperado, votar por su DOCUMENTO y despues abrir los silos donde vive
ese documento. Un documento es una unidad coherente: si la respuesta esta en la Ley 24.065,
conviene abrir TODOS los silos donde quedaron sus chunks (aunque esten repartidos).

Criterio: si la señal gana, DESPUES se discute materializarla como grafo. Nunca al reves.
Todo con leave-one-out (chunk de origen excluido) -> sin circularidad.
"""
import sys, io, json, random
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from embedder import embed_query
from clasificador import _coseno, _softmax, _centroide_l2
from config import CLASIFICADOR_TEMP

DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}
SILOS = ["legal", "impositivo", "contable", "financiero"]

con = conectar()
cur = con.cursor()
# mapa documento -> reparto de silos (la "arista" documento->silo, precalculable)
cur.execute("SELECT fuente, silo, COUNT(*) FROM chunks GROUP BY fuente, silo")
doc_silos = defaultdict(dict)
for fu, s, c in cur.fetchall():
    doc_silos[fu][s] = c

cur.execute("SELECT DISTINCT fuente, titulo FROM chunks WHERE LENGTH(titulo) BETWEEN 15 AND 70")
todo = [(f, t) for f, t in cur.fetchall() if f in DOM]
random.seed(7)
por_dom = {}
for f, t in todo:
    por_dom.setdefault(DOM[f], []).append((f, t))
consultas = []
for d, l in por_dom.items():
    consultas += [(f, t, d) for f, t in random.sample(l, min(40, len(l)))]

cur.execute("SELECT silo, embedding::text FROM chunks")
E = {}
for s, v in cur.fetchall():
    E.setdefault(s, []).append(np.array(json.loads(v)))
proto = {s: np.array(_centroide_l2(v)) for s, v in E.items()}

POL = ["proto top-2 (HOY)", "COMBINADA (C.47)", "voto por SILO (C.47)",
       "GRAFO doc->silo", "GRAFO + prototipo", "GRAFO + COMBINADA"]
ok = {p: 0 for p in POL}
tam = {p: [] for p in POL}

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    correctos = {s for _, s in origen}
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"

    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    orden_p = sorted(dist, key=dist.get, reverse=True)

    cur.execute("SELECT silo, fuente FROM chunks WHERE NOT (chunk_uid = ANY(%s)) "
                "ORDER BY embedding <=> %s::vector LIMIT 10", (excluir, vec))
    top10 = cur.fetchall()
    voto_silo = Counter(s for s, _ in top10)

    mejor = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "AND NOT (chunk_uid = ANY(%s)) ORDER BY embedding <=> %s::vector LIMIT 1",
                    (vec, s, excluir, vec))
        r = cur.fetchone()
        mejor[s] = float(r[0]) if r else 0.0
    orden_e = sorted(mejor, key=mejor.get, reverse=True)
    orden_c = sorted(SILOS, key=lambda s: orden_p.index(s) + orden_e.index(s))

    # --- SEÑAL GRAFO: votar por DOCUMENTO, propagar a los silos donde vive ese documento ---
    voto_doc = Counter(fu for _, fu in top10)
    peso_silo = defaultdict(float)
    for fu, veces in voto_doc.items():
        reparto = doc_silos.get(fu, {})
        total = sum(reparto.values()) or 1
        for s, c in reparto.items():
            peso_silo[s] += veces * (c / total)      # propagacion doc -> silos
    orden_g = sorted(SILOS, key=lambda s: -peso_silo.get(s, 0.0))
    orden_gp = sorted(SILOS, key=lambda s: orden_g.index(s) + orden_p.index(s))
    orden_gc = sorted(SILOS, key=lambda s: orden_g.index(s) + orden_c.index(s))

    planes = {"proto top-2 (HOY)": orden_p[:2], "COMBINADA (C.47)": orden_c[:2],
              "voto por SILO (C.47)": [s for s, _ in voto_silo.most_common(2)],
              "GRAFO doc->silo": orden_g[:2], "GRAFO + prototipo": orden_gp[:2],
              "GRAFO + COMBINADA": orden_gc[:2]}
    for p, sel in planes.items():
        ok[p] += bool(correctos & set(sel))
        tam[p].append(len(sel))

con.close()
n = len(consultas)
print(f"¿SIRVE LA SEÑAL DE GRAFO? — acierto del router, sin fuga  ·  {n} consultas")
print()
print(f"  {'politica':28s} {'acierta':>9s} {'silos':>7s}")
for p in sorted(POL, key=lambda x: -ok[x]/n):
    print(f"  {p:28s} {ok[p]/n:8.1%} {np.mean(tam[p]):7.2f}")
