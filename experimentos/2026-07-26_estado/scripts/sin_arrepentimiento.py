"""¿COMO SUPERAR A B0 DE VERDAD? — estrategia SIN ARREPENTIMIENTO.

Problema: cuando el router se equivoca de silo, el brazo segregado rinde MUCHO menos que
B0. Idea: reservar cupos para el mejor resultado GLOBAL (venga del silo que venga) y
llenar el resto con los silos elegidos. Asi el sistema no puede quedar por debajo de B0
en esos cupos, y suma la ganancia del filtro en los demas.

Variantes: 1 cupo global + resto silo · 2 cupos globales + resto silo.
Todo a MISMO k (mismo presupuesto de contexto) y con señales leave-one-out.
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
K = 3
GAMMA = 0.70
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

BR = ["B0 monolitico", "COBERTURA g=0.70 (C.50)", "SIN-ARREP. 1 global + 2 silo",
      "SIN-ARREP. 2 global + 1 silo", "ORACULO (techo)"]
hit = {b: 0 for b in BR}
cont = {b: [] for b in BR}

def fusionar(listas, k=K):
    vistos, out = set(), []
    for l in listas:
        for u, fu, d in l:
            if u not in vistos:
                vistos.add(u); out.append((u, fu, d))
    out.sort(key=lambda r: r[2])
    return out[:k]

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    uids = {u for u, _ in origen}
    silos_reales = list({s for _, s in origen})
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"

    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    mejor = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "AND NOT (chunk_uid = ANY(%s)) ORDER BY embedding <=> %s::vector LIMIT 1",
                    (vec, s, excluir, vec))
        r = cur.fetchone()
        mejor[s] = float(r[0]) if r else 0.0
    comb = {s: dist[s] * max(mejor[s], 1e-6) for s in SILOS}
    tot = sum(comb.values())
    p = {s: comb[s] / tot for s in SILOS}
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= GAMMA:
            break

    def glob(n):
        cur.execute("SELECT chunk_uid, fuente, embedding <=> %s::vector FROM chunks "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (vec, vec, n))
        return cur.fetchall()

    def dentro(silos, n):
        cur.execute("SELECT chunk_uid, fuente, embedding <=> %s::vector FROM chunks "
                    "WHERE silo = ANY(%s) ORDER BY embedding <=> %s::vector LIMIT %s",
                    (vec, silos, vec, n))
        return cur.fetchall()

    planes = {
        "B0 monolitico": glob(K),
        "COBERTURA g=0.70 (C.50)": dentro(sel, K),
        "SIN-ARREP. 1 global + 2 silo": fusionar([glob(1), dentro(sel, K)]),
        "SIN-ARREP. 2 global + 1 silo": fusionar([glob(2), dentro(sel, K)]),
        "ORACULO (techo)": dentro(silos_reales, K),
    }
    for b, r in planes.items():
        hit[b] += bool(uids & {x[0] for x in r})
        if r:
            cont[b].append(sum(1 for x in r if DOM.get(x[1]) != dom) / len(r))

con.close()
n = len(consultas)
print(f"¿SE PUEDE SUPERAR A B0? — estrategia sin arrepentimiento  ·  {n} consultas  ·  k={K}")
print()
print(f"  {'sistema':32s} {'encuentra':>10s} {'sucio':>8s}")
for b in BR:
    marca = "  <-- supera a B0" if hit[b] > hit["B0 monolitico"] else ""
    print(f"  {b:32s} {hit[b]/n:9.1%} {np.mean(cont[b]):7.1%}{marca}")
