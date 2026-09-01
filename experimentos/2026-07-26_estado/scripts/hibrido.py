"""PALANCA C: busqueda HIBRIDA (denso + BM25 con RRF) — plan A7.

HIPOTESIS: BM25 matchea por PALABRA. "sancion", "plazo", "prescripcion" aparecen
literalmente en los dos dominios -> BM25 inyecta colisiones LEXICAS que el denso
no tenia. Si es cierto, B0 hibrido se ensucia mas y la ventaja del silo CRECE.

Todo con Postgres FTS (sin instalar nada). Fusion por RRF (k=60, estandar).
"""
import sys, io, random
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from embedder import embed_query

DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}
K, RRF_K, POOL = 3, 60, 30
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

def denso(vec, silos):
    if silos:
        cur.execute("SELECT chunk_uid, fuente FROM chunks WHERE silo = ANY(%s) "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (silos, vec, POOL))
    else:
        cur.execute("SELECT chunk_uid, fuente FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s",
                    (vec, POOL))
    return cur.fetchall()

def lexico(q, silos):
    if silos:
        cur.execute("""SELECT chunk_uid, fuente FROM chunks
                       WHERE silo = ANY(%s) AND to_tsvector('spanish', contenido) @@ plainto_tsquery('spanish', %s)
                       ORDER BY ts_rank(to_tsvector('spanish', contenido), plainto_tsquery('spanish', %s)) DESC
                       LIMIT %s""", (silos, q, q, POOL))
    else:
        cur.execute("""SELECT chunk_uid, fuente FROM chunks
                       WHERE to_tsvector('spanish', contenido) @@ plainto_tsquery('spanish', %s)
                       ORDER BY ts_rank(to_tsvector('spanish', contenido), plainto_tsquery('spanish', %s)) DESC
                       LIMIT %s""", (q, q, POOL))
    return cur.fetchall()

def rrf(*listas):
    score, meta = {}, {}
    for l in listas:
        for i, (u, fu) in enumerate(l, 1):
            score[u] = score.get(u, 0) + 1 / (RRF_K + i)
            meta[u] = fu
    orden = sorted(score, key=score.get, reverse=True)
    return [(u, meta[u]) for u in orden]

res = {n: {"hit": 0, "cont": []} for n in ("B0 denso", "B0 HIBRIDO", "SILO denso", "SILO HIBRIDO")}
for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    uids = {u for u, _ in origen}
    silos_o = list({s for _, s in origen})
    vec = "[" + ",".join(map(str, embed_query(t))) + "]"

    planes = {
        "B0 denso": denso(vec, None)[:K],
        "B0 HIBRIDO": rrf(denso(vec, None), lexico(t, None))[:K],
        "SILO denso": denso(vec, silos_o)[:K],
        "SILO HIBRIDO": rrf(denso(vec, silos_o), lexico(t, silos_o))[:K],
    }
    for nom, r in planes.items():
        res[nom]["hit"] += bool(uids & {u for u, _ in r})
        if r:
            res[nom]["cont"].append(sum(1 for _, fu in r if DOM.get(fu) != dom) / len(r))
con.close()

n = len(consultas)
print(f"PALANCA C — HIBRIDO (denso + BM25 con RRF)  ·  {n} consultas  ·  recall@{K}")
print()
print(f"  {'sistema':16s} {'encuentra':>10s} {'sucio':>8s}")
for nom in ("B0 denso", "B0 HIBRIDO", "SILO denso", "SILO HIBRIDO"):
    print(f"  {nom:16s} {res[nom]['hit']/n:9.1%} {np.mean(res[nom]['cont']):7.1%}")
print()
g_d = (res["SILO denso"]["hit"] - res["B0 denso"]["hit"]) / n
g_h = (res["SILO HIBRIDO"]["hit"] - res["B0 HIBRIDO"]["hit"]) / n
print(f"  ventaja del silo con DENSO   : {g_d*100:+.1f} pp")
print(f"  ventaja del silo con HIBRIDO : {g_h*100:+.1f} pp   <-- ¿crece?")
c_d = np.mean(res["B0 denso"]["cont"]) - np.mean(res["SILO denso"]["cont"])
c_h = np.mean(res["B0 HIBRIDO"]["cont"]) - np.mean(res["SILO HIBRIDO"]["cont"])
print(f"  limpieza ganada con DENSO    : {c_d*100:+.1f} pp")
print(f"  limpieza ganada con HIBRIDO  : {c_h*100:+.1f} pp")
