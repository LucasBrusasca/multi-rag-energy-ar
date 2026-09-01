"""OBJECION DE LUCAS: "¿y si el monolitico simplemente muestra MAS resultados?"

Si B0 con k=10 recupera lo que perdia con k=3, la ventaja del silo seria un artefacto
del corte. Se mide: recall Y contaminacion del contexto entregado, a distintos k.
El costo de subir k es que el generador recibe MAS material de otros dominios.
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
hit_b0 = {k: 0 for k in KS}
cont_b0 = {k: [] for k in KS}
hit_silo = 0
cont_silo = []
K_SILO = 3

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
    for k in KS:
        top = glob[:k]
        hit_b0[k] += bool(uids & {u for u, _ in top})
        cont_b0[k].append(sum(1 for _, fu in top if DOM.get(fu) != dom) / len(top))

    # silo correcto (donde el chunk esta guardado), k=3
    cur.execute("SELECT chunk_uid, fuente FROM chunks WHERE silo = ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (silos_o, vec, K_SILO))
    r = cur.fetchall()
    hit_silo += bool(uids & {u for u, _ in r})
    cont_silo.append(sum(1 for _, fu in r if DOM.get(fu) != dom) / max(len(r), 1))

con.close()
n = len(consultas)
print(f"¿ALCANZA CON QUE EL MONOLITICO MUESTRE MAS?  ·  {n} consultas")
print()
print(f"  {'sistema':34s} {'encuentra':>10s} {'textos al generador':>21s} {'de otro dominio':>17s}")
for k in KS:
    print(f"  {'B0 monolitico, top-' + str(k):34s} {hit_b0[k]/n:9.1%} {k:21d} {np.mean(cont_b0[k]):16.1%}")
print(f"  {'SILO correcto, top-' + str(K_SILO):34s} {hit_silo/n:9.1%} {K_SILO:21d} {np.mean(cont_silo):16.1%}")
print()
print("  'de otro dominio' = % del material entregado que viene de documentos de OTRO dominio")
