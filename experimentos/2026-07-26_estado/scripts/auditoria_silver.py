"""AUDITORIA DEL SILVER: ¿cuanto de lo medido estos dias es fuga?

Si el chunk de origen es casi siempre el resultado #1 global, entonces:
 - toda politica que "mire" globalmente lo encuentra por construccion,
 - el recall medido no mide recuperacion sino la fuga titulo->chunk,
 - y NINGUN numero del silver sirve para comparar politicas.
"""
import sys, io, json, random
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

puesto1 = 0
en_top3 = 0
posiciones = []
sim_origen, sim_mejor_ajeno = [], []

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    uids = {r[0] for r in cur.fetchall()}
    q = embed_query(t)
    vec = "[" + ",".join(map(str, q)) + "]"
    cur.execute("SELECT chunk_uid, 1-(embedding <=> %s::vector) FROM chunks "
                "ORDER BY embedding <=> %s::vector LIMIT 20", (vec, vec))
    rank = cur.fetchall()
    pos = next((i for i, (u, _) in enumerate(rank, 1) if u in uids), None)
    if pos == 1:
        puesto1 += 1
    if pos and pos <= 3:
        en_top3 += 1
    posiciones.append(pos or 99)
    # similitud del chunk de origen vs el mejor que NO es de origen
    so = next((s for u, s in rank if u in uids), None)
    sa = next((s for u, s in rank if u not in uids), None)
    if so and sa:
        sim_origen.append(so)
        sim_mejor_ajeno.append(sa)

con.close()
n = len(consultas)
print(f"AUDITORIA DE FUGA DEL SILVER  ·  {n} consultas (el titulo del chunk como pregunta)")
print()
print(f"  el chunk de ORIGEN sale #1 en la busqueda global : {puesto1}/{n}  ({puesto1/n:.1%})")
print(f"  el chunk de ORIGEN esta en el top-3 global       : {en_top3}/{n}  ({en_top3/n:.1%})")
print(f"  posicion mediana del chunk de origen            : {int(np.median(posiciones))}")
print()
print(f"  similitud media del chunk de ORIGEN        : {np.mean(sim_origen):.3f}")
print(f"  similitud media del mejor chunk AJENO      : {np.mean(sim_mejor_ajeno):.3f}")
print(f"  ventaja artificial del origen              : {np.mean(sim_origen)-np.mean(sim_mejor_ajeno):+.3f}")
print()
print("  LECTURA: si el origen sale #1 en la mayoria de los casos, el 'recall' del silver")
print("  mide la FUGA (el titulo esta dentro del texto embebido), no la calidad del ruteo.")
