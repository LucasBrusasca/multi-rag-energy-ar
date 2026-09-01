"""PALANCAS PARA AGRANDAR EL GAP — dos que se miden sin LLM.

PALANCA A: k mas chico. La ventaja se achicaba al subir k (3->20). ¿Y bajando a 1-2?
PALANCA B: metrica graduada. recall@3 es BINARIO: no ve que el silo mueva la respuesta
           del puesto 3 al 1. MRR y la mejora de PUESTO si lo ven, y para el generador
           la posicion importa (lost-in-the-middle: lo del medio se ignora).
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

pos_b0, pos_si = [], []
for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    uids = {u for u, _ in origen}
    silos_o = list({s for _, s in origen})
    q = embed_query(t)
    vec = "[" + ",".join(map(str, q)) + "]"
    cur.execute("SELECT chunk_uid FROM chunks ORDER BY embedding <=> %s::vector LIMIT 100", (vec,))
    g = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT chunk_uid FROM chunks WHERE silo = ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT 100", (silos_o, vec))
    s = [r[0] for r in cur.fetchall()]
    pos_b0.append(next((i for i, u in enumerate(g, 1) if u in uids), 999))
    pos_si.append(next((i for i, u in enumerate(s, 1) if u in uids), 999))
con.close()

n = len(consultas)
pb, ps = np.array(pos_b0), np.array(pos_si)
print(f"PALANCA A — ¿la ventaja crece con k mas chico?  ·  {n} consultas")
print()
print(f"  {'k':>3s} {'B0':>8s} {'SILO':>8s} {'ventaja':>9s}")
for k in (1, 2, 3, 5, 10):
    a, b = (pb <= k).mean(), (ps <= k).mean()
    print(f"  {k:3d} {a:7.1%} {b:7.1%} {(b-a)*100:+8.1f} pp")
print()
print("PALANCA B — metrica graduada (ve lo que recall@3 no ve)")
mrr_b = np.mean([1/p if p < 999 else 0 for p in pb])
mrr_s = np.mean([1/p if p < 999 else 0 for p in ps])
print(f"  MRR (1/puesto)          B0 {mrr_b:.3f}  ->  SILO {mrr_s:.3f}   ({(mrr_s-mrr_b)/mrr_b*100:+.1f}% relativo)")
val = [(a, b) for a, b in zip(pb, ps) if a < 999 and b < 999]
mejora = [a - b for a, b in val]
print(f"  puesto promedio         B0 {np.mean([a for a,_ in val]):.2f}  ->  SILO {np.mean([b for _,b in val]):.2f}")
print(f"  consultas que MEJORAN de puesto: {sum(1 for m in mejora if m>0)}/{len(val)} "
      f"({sum(1 for m in mejora if m>0)/len(val):.1%})   ·  empeoran: {sum(1 for m in mejora if m<0)}")
print(f"  mejora media de puesto (solo las que mejoran): {np.mean([m for m in mejora if m>0]):.1f} posiciones")
print()
print(f"  respuesta en el PUESTO 1:   B0 {(pb==1).mean():.1%}  ->  SILO {(ps==1).mean():.1%}"
      f"   ({((ps==1).mean()-(pb==1).mean())*100:+.1f} pp)")
