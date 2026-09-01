"""PALANCA D — ASIGNACION PROPORCIONAL (estilo DFAMS) vs apertura BINARIA.

Idea: en vez de decidir QUE silos abrir (todo o nada), repartir el presupuesto k
entre los silos segun su score. Con k=3: p.ej. 2 slots al silo 1, 1 al silo 2.
Ventaja teorica: el silo 3 nunca queda estructuralmente en cero si tiene score.

Se compara contra: B0, binario top-2 (hoy), binario COMBINADO (C.47), y el oraculo.
Score = combinacion prototipo + evidencia (la mejor señal medida, C.47).
Leave-one-out en las señales -> sin circularidad en la decision.
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

BR = ["B0 monolitico", "binario top-2 (HOY)", "binario COMBINADO", "PROPORCIONAL", "ORACULO"]
hit = {b: 0 for b in BR}
cont = {b: [] for b in BR}

def top_de(silos_slots, vec):
    """silos_slots: {silo: n_slots} -> recupera n de cada uno y fusiona por similitud."""
    out = []
    for s, n in silos_slots.items():
        if n <= 0:
            continue
        cur.execute("SELECT chunk_uid, fuente, embedding <=> %s::vector FROM chunks WHERE silo = %s "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (vec, s, vec, n))
        out += cur.fetchall()
    out.sort(key=lambda r: r[2])
    return [(u, f) for u, f, _ in out[:K]]

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    uids = {u for u, _ in origen}
    silos_reales = list({s for _, s in origen})
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"

    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    orden_p = sorted(dist, key=dist.get, reverse=True)
    mejor = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "AND NOT (chunk_uid = ANY(%s)) ORDER BY embedding <=> %s::vector LIMIT 1",
                    (vec, s, excluir, vec))
        r = cur.fetchone()
        mejor[s] = float(r[0]) if r else 0.0
    orden_e = sorted(mejor, key=mejor.get, reverse=True)
    orden_c = sorted(SILOS, key=lambda s: orden_p.index(s) + orden_e.index(s))

    # PROPORCIONAL: reparto de K slots por peso combinado (softmax de la evidencia * prob prototipo)
    peso = {s: dist[s] * max(mejor[s], 0.0) for s in SILOS}
    tot = sum(peso.values()) or 1.0
    crudo = {s: K * peso[s] / tot for s in SILOS}
    slots = {s: int(crudo[s]) for s in SILOS}
    resto = K - sum(slots.values())
    for s in sorted(SILOS, key=lambda x: -(crudo[x] - int(crudo[x])))[:resto]:
        slots[s] += 1

    planes = {
        "B0 monolitico": None,
        "binario top-2 (HOY)": {s: K for s in orden_p[:2]},
        "binario COMBINADO": {s: K for s in orden_c[:2]},
        "PROPORCIONAL": slots,
        "ORACULO": {s: K for s in silos_reales},
    }
    for b, plan in planes.items():
        if plan is None:
            cur.execute("SELECT chunk_uid, fuente FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s",
                        (vec, K))
            r = cur.fetchall()
        else:
            r = top_de(plan, vec)
        hit[b] += bool(uids & {u for u, _ in r})
        if r:
            cont[b].append(sum(1 for _, fu in r if DOM.get(fu) != dom) / len(r))

con.close()
n = len(consultas)
print(f"PALANCA D — asignacion PROPORCIONAL vs binaria  ·  {n} consultas  ·  recall@{K}")
print()
print(f"  {'sistema':24s} {'encuentra':>10s} {'sucio':>8s}")
for b in BR:
    print(f"  {b:24s} {hit[b]/n:9.1%} {np.mean(cont[b]):7.1%}")
