"""LA REGLA: si hay que abrir CASI TODOS los silos, la segregacion no aporta -> abrir TODOS.

Hallazgo: las 6 fallas abren 3 de 4 silos (n_sel=3.000 exacto) vs 2.81 en las que funcionan.
Excluir 1 de 4 da casi CERO aislamiento pero conserva el riesgo TOTAL de perder la evidencia
(recall 0% cuando falla). Es el peor punto de la curva: todo el riesgo, nada del beneficio.

REGLA (escalable): si |S| / n_silos >= UMBRAL_RENUNCIA -> abrir todos y DECLARARLO.
Con 4 silos y umbral 0.75 => "si ibas a abrir 3, abri 4".
Es una decision de GOBERNANZA auditable: el sistema declara "no puedo segregar esta consulta".
"""
import sys, io, json, random
from pathlib import Path

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
K, GAMMA = 3, 0.70
con = conectar(); cur = con.cursor()
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

BR = ["B0 monolitico", "cobertura g=0.70", "+ RENUNCIA (>=3 de 4 -> abrir 4)", "ORACULO (techo)"]
hit = {b: 0 for b in BR}; cont = {b: [] for b in BR}; expo = {b: [] for b in BR}
renuncias = 0

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]; uids = {u for u, _ in origen}
    silos_reales = list({s for _, s in origen})
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    mejor = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "AND NOT (chunk_uid = ANY(%s)) ORDER BY embedding <=> %s::vector LIMIT 1",
                    (vec, s, excluir, vec))
        r = cur.fetchone(); mejor[s] = float(r[0]) if r else 0.0
    comb = {s: dist[s] * max(mejor[s], 1e-6) for s in SILOS}
    tot = sum(comb.values()); p = {s: comb[s] / tot for s in SILOS}
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= GAMMA:
            break
    sel_r = SILOS[:] if len(sel) / len(SILOS) >= 0.75 else sel
    if sel_r is not sel and len(sel_r) != len(sel):
        renuncias += 1

    def rec(silos):
        cur.execute("SELECT chunk_uid, fuente FROM chunks WHERE silo = ANY(%s) "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (silos, vec, K))
        return cur.fetchall()
    cur.execute("SELECT chunk_uid, fuente FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s", (vec, K))
    planes = {"B0 monolitico": (SILOS, cur.fetchall()), "cobertura g=0.70": (sel, rec(sel)),
              "+ RENUNCIA (>=3 de 4 -> abrir 4)": (sel_r, rec(sel_r)),
              "ORACULO (techo)": (silos_reales, rec(silos_reales))}
    for b, (s_, r) in planes.items():
        hit[b] += bool(uids & {x[0] for x in r})
        if r: cont[b].append(sum(1 for x in r if DOM.get(x[1]) != dom) / len(r))
        expo[b].append(len(s_))
con.close()
n = len(consultas)
print(f"REGLA DE RENUNCIA A LA SEGREGACION  ·  {n} consultas  ·  recall@{K}")
print()
print(f"  {'politica':34s} {'encuentra':>10s} {'sucio':>8s} {'silos':>7s}")
for b in BR:
    m = "  <-- SUPERA A B0" if b not in ("B0 monolitico", "ORACULO (techo)") and hit[b] > hit["B0 monolitico"] else \
        ("  = B0" if b not in ("B0 monolitico","ORACULO (techo)") and hit[b] == hit["B0 monolitico"] else "")
    print(f"  {b:34s} {hit[b]/n:9.1%} {np.mean(cont[b]):7.1%} {np.mean(expo[b]):7.2f}{m}")
print()
print(f"  renuncias (consultas donde el sistema declara 'no puedo segregar'): {renuncias}/{n} ({renuncias/n:.1%})")
