"""COMPARACION A PARIDAD DE PRESUPUESTO — la unica justa.

En produccion, un RAG monolitico recupera tipicamente k=5..10 chunks (no 3).
Pregunta de Lucas: contra ESO, ¿la tesis gana?
Se compara B0 vs SILO al MISMO k (mismo presupuesto de contexto para el generador).
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

KS = [3, 5, 10, 20]
hit = {("B0", k): 0 for k in KS}
hit.update({("SILO", k): 0 for k in KS})
cont = {("B0", k): [] for k in KS}
cont.update({("SILO", k): [] for k in KS})

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    uids = {u for u, _ in origen}
    silos_o = list({s for _, s in origen})
    q = embed_query(t)
    vec = "[" + ",".join(map(str, q)) + "]"

    cur.execute("SELECT chunk_uid, fuente FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s",
                (vec, max(KS)))
    glob = cur.fetchall()
    cur.execute("SELECT chunk_uid, fuente FROM chunks WHERE silo = ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (silos_o, vec, max(KS)))
    dentro = cur.fetchall()

    for k in KS:
        for nombre, lista in (("B0", glob[:k]), ("SILO", dentro[:k])):
            hit[(nombre, k)] += bool(uids & {u for u, _ in lista})
            if lista:
                cont[(nombre, k)].append(sum(1 for _, fu in lista if DOM.get(fu) != dom) / len(lista))

con.close()
n = len(consultas)
print(f"A PARIDAD DE PRESUPUESTO — mismo k para los dos  ·  {n} consultas")
print()
print(f"  {'k':>3s} | {'B0 encuentra':>13s} {'B0 sucio':>9s} | {'SILO encuentra':>15s} {'SILO sucio':>11s} | {'ventaja':>8s}")
for k in KS:
    hb, hs = hit[("B0", k)]/n, hit[("SILO", k)]/n
    cb, cs = np.mean(cont[("B0", k)]), np.mean(cont[("SILO", k)])
    print(f"  {k:3d} | {hb:12.1%} {cb:9.1%} | {hs:14.1%} {cs:11.1%} | {hs-hb:+7.1%}")
print()
print("  'sucio' = % del material entregado que viene de documentos de OTRO dominio")
print("  SILO = filtrado al silo donde esta la evidencia (techo de un router perfecto)")
