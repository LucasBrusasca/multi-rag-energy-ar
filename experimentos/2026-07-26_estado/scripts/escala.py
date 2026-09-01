"""IDEA PARA MEJORAR EL NUMERO: ¿el efecto CRECE con el tamaño del corpus?

Hipotesis: la ventaja del silo viene de sacar competidores de otros dominios. Con 17
documentos hay pocos competidores. Con un corpus grande hay muchos mas -> B0 se degrada
mas rapido que el silo -> la brecha se ABRE.

Si la curva sube, el 3.1% de hoy es un PISO, no un techo: es el efecto medido en el
corpus mas chico posible. Eso cambia por completo la lectura del numero.
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
K = 3
con = conectar()
cur = con.cursor()

# tamaño en CHUNKS de cada documento (para escalar por volumen real, no por cantidad de archivos)
cur.execute("SELECT fuente, COUNT(*) FROM chunks GROUP BY fuente")
tam_doc = dict(cur.fetchall())

cur.execute("SELECT DISTINCT fuente, titulo FROM chunks WHERE LENGTH(titulo) BETWEEN 15 AND 70")
todo = [(f, t) for f, t in cur.fetchall() if f in DOM]
random.seed(7)
por_dom = {}
for f, t in todo:
    por_dom.setdefault(DOM[f], []).append((f, t))
consultas = []
for d, l in por_dom.items():
    consultas += [(f, t, d) for f, t in random.sample(l, min(30, len(l)))]

# cache de embeddings de las consultas (se reusan en todas las escalas)
print("embebiendo consultas...", flush=True)
CACHE = {}
for f, t, d in consultas:
    v = embed_query(t)
    CACHE[t] = "[" + ",".join(map(str, v)) + "]"

# subcorpus crecientes: se agregan documentos de a uno, rotando dominios
orden_docs = []
por_d = {d: [f for f in DOM if DOM[f] == d] for d in ("legal", "impositivo", "contable", "financiero")}
i = 0
while any(por_d.values()):
    for d in ("legal", "impositivo", "contable", "financiero"):
        if por_d[d]:
            orden_docs.append(por_d[d].pop(0))
    i += 1

ESCALAS = [4, 8, 12, len(orden_docs)]
print()
print(f"  {'docs':>5s} {'chunks':>8s} {'consultas':>10s} {'B0':>8s} {'SILO':>8s} {'brecha':>8s}")
for m in ESCALAS:
    sub = orden_docs[:m]
    n_chunks = sum(tam_doc.get(f, 0) for f in sub)
    hb = hs = n = 0
    for f, t, dom in consultas:
        if f not in sub:
            continue
        n += 1
        vec = CACHE[t]
        cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
        origen = cur.fetchall()
        uids = {u for u, _ in origen}
        silos_o = list({s for _, s in origen})
        cur.execute("SELECT chunk_uid FROM chunks WHERE fuente = ANY(%s) "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (sub, vec, K))
        hb += bool(uids & {r[0] for r in cur.fetchall()})
        cur.execute("SELECT chunk_uid FROM chunks WHERE fuente = ANY(%s) AND silo = ANY(%s) "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (sub, silos_o, vec, K))
        hs += bool(uids & {r[0] for r in cur.fetchall()})
    if n:
        print(f"  {m:5d} {n_chunks:8d} {n:10d} {hb/n:7.1%} {hs/n:7.1%} {(hs-hb)*100:+7.1f} pp")
con.close()
print()
print("  (mismas consultas, corpus creciente: se agregan documentos rotando dominios)")
