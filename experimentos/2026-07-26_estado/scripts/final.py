"""EL NUMERO DECISIVO: con el router optimizado, ¿se le gana a B0 punta a punta?

Diseño honesto (sin fuga en la decision de ruteo):
  - el ROUTER decide con señales calculadas EXCLUYENDO el chunk de origen (no se ve a si mismo)
  - la RECUPERACION corre sobre el corpus COMPLETO (escenario real: la respuesta esta indexada)
Asi la decision no esta contaminada y la medicion de recall es realista.
"""
import sys, io, json, random
from pathlib import Path
from collections import Counter

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
K = 3

con = conectar()
cur = con.cursor()
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

BRAZOS = ["B0 monolitico", "B1 proto top-2 (HOY)", "ROUTER COMBINADO 2 silos",
          "ROUTER VOTO 2 silos", "ORACULO (silo real)"]
hit = {b: 0 for b in BRAZOS}
cont = {b: [] for b in BRAZOS}
expo = {b: [] for b in BRAZOS}

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    uids = {u for u, _ in origen}
    silos_reales = list({s for _, s in origen})
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"

    # --- DECISION DE RUTEO: señales SIN el chunk de origen ---
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    orden_p = sorted(dist, key=dist.get, reverse=True)
    cur.execute("SELECT silo FROM chunks WHERE NOT (chunk_uid = ANY(%s)) "
                "ORDER BY embedding <=> %s::vector LIMIT 10", (excluir, vec))
    top10 = [r[0] for r in cur.fetchall()]
    voto = Counter(top10)
    mejor = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "AND NOT (chunk_uid = ANY(%s)) ORDER BY embedding <=> %s::vector LIMIT 1",
                    (vec, s, excluir, vec))
        r = cur.fetchone()
        mejor[s] = float(r[0]) if r else 0.0
    orden_e = sorted(mejor, key=mejor.get, reverse=True)
    orden_c = sorted(SILOS, key=lambda s: orden_p.index(s) + orden_e.index(s))

    planes = {"B0 monolitico": None, "B1 proto top-2 (HOY)": orden_p[:2],
              "ROUTER COMBINADO 2 silos": orden_c[:2],
              "ROUTER VOTO 2 silos": [s for s, _ in voto.most_common(2)],
              "ORACULO (silo real)": silos_reales}

    # --- RECUPERACION: corpus COMPLETO ---
    for b, silos in planes.items():
        if silos is None:
            cur.execute("SELECT chunk_uid, fuente FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s",
                        (vec, K))
        else:
            cur.execute("SELECT chunk_uid, fuente FROM chunks WHERE silo = ANY(%s) "
                        "ORDER BY embedding <=> %s::vector LIMIT %s", (silos, vec, K))
        r = cur.fetchall()
        hit[b] += bool(uids & {u for u, _ in r})
        cont[b].append(sum(1 for _, fu in r if DOM.get(fu) != dom) / max(len(r), 1))
        expo[b].append(4 if silos is None else len(silos))

con.close()
n = len(consultas)
print(f"PUNTA A PUNTA — decision de ruteo SIN fuga  ·  {n} consultas  ·  recall@{K}")
print()
print(f"  {'sistema':30s} {'encuentra':>10s} {'sucio':>8s} {'silos':>7s}")
for b in BRAZOS:
    print(f"  {b:30s} {hit[b]/n:9.1%} {np.mean(cont[b]):7.1%} {np.mean(expo[b]):7.2f}")
print()
b0 = hit["B0 monolitico"]/n
for b in BRAZOS[1:]:
    print(f"  {b:30s} vs B0: {hit[b]/n - b0:+.1%} recall, "
          f"{np.mean(cont[b]) - np.mean(cont['B0 monolitico']):+.1f} pp sucio")
