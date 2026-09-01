"""OBJECION DE LUCAS: "3.1 puntos es muy poco para tanto lio".

Correcta si el efecto fuera uniforme. Pero el 3.1 es el PROMEDIO sobre consultas
cualesquiera, y la tesis habla de las que COLISIONAN. Se estratifica:

  - consulta CLARA:      la evidencia del top-10 global vive en 1-2 silos
  - consulta EN COLISION: la evidencia del top-10 se reparte en 3-4 silos
    (varios dominios compiten por el mismo vocabulario = la definicion de colision)

Ademas: test de McNemar exacto para ver si 3.1 pp es siquiera significativo.
"""
import sys, io, random
from pathlib import Path
from collections import Counter

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
cur.execute("SELECT DISTINCT fuente, titulo FROM chunks WHERE LENGTH(titulo) BETWEEN 15 AND 70")
todo = [(f, t) for f, t in cur.fetchall() if f in DOM]
random.seed(7)
por_dom = {}
for f, t in todo:
    por_dom.setdefault(DOM[f], []).append((f, t))
consultas = []
for d, l in por_dom.items():
    consultas += [(f, t, d) for f, t in random.sample(l, min(40, len(l)))]

filas = []   # (n_silos_en_top10, hit_b0, hit_silo, cont_b0, cont_silo)
for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    uids = {u for u, _ in origen}
    silos_o = list({s for _, s in origen})
    q = embed_query(t)
    vec = "[" + ",".join(map(str, q)) + "]"

    cur.execute("SELECT chunk_uid, fuente, silo FROM chunks ORDER BY embedding <=> %s::vector LIMIT 10", (vec,))
    top10 = cur.fetchall()
    n_silos = len(set(s for _, _, s in top10))
    b0 = top10[:K]
    cur.execute("SELECT chunk_uid, fuente FROM chunks WHERE silo = ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (silos_o, vec, K))
    silo = cur.fetchall()
    filas.append((n_silos,
                  bool(uids & {u for u, _, _ in b0}),
                  bool(uids & {u for u, _ in silo}),
                  sum(1 for _, fu, _ in b0 if DOM.get(fu) != dom) / K,
                  sum(1 for _, fu in silo if DOM.get(fu) != dom) / max(len(silo), 1)))
con.close()

def resumen(sub, nombre):
    if not sub:
        return
    n = len(sub)
    hb = sum(r[1] for r in sub) / n
    hs = sum(r[2] for r in sub) / n
    cb = np.mean([r[3] for r in sub])
    cs = np.mean([r[4] for r in sub])
    print(f"  {nombre:34s} n={n:3d}  B0 {hb:5.1%} -> silo {hs:5.1%}  ({hs-hb:+5.1f} pp)"
          f"   sucio {cb:5.1%} -> {cs:5.1%} ({cs-cb:+5.1f} pp)")

print(f"EFECTO ESTRATIFICADO POR DIFICULTAD  ·  {len(filas)} consultas  ·  recall@{K}")
print()
resumen([r for r in filas], "TODAS (el promedio que cuestionas)")
print()
resumen([r for r in filas if r[0] <= 2], "CLARAS (top-10 en 1-2 silos)")
resumen([r for r in filas if r[0] == 3], "AMBIGUAS (top-10 en 3 silos)")
resumen([r for r in filas if r[0] >= 4], "EN COLISION (top-10 en 4 silos)")
print()

# McNemar exacto sobre TODAS
b01 = sum(1 for r in filas if r[1] and not r[2])   # B0 acierta, silo no
b10 = sum(1 for r in filas if r[2] and not r[1])   # silo acierta, B0 no
from math import comb
n_d = b01 + b10
p = sum(comb(n_d, i) for i in range(min(b01, b10) + 1)) / (2 ** n_d) * 2 if n_d else 1.0
print(f"  McNemar exacto (todas): discordantes {b10} a favor del silo, {b01} a favor de B0  ->  p = {min(p,1):.3f}")

sub = [r for r in filas if r[0] >= 4]
b01c = sum(1 for r in sub if r[1] and not r[2])
b10c = sum(1 for r in sub if r[2] and not r[1])
n_dc = b01c + b10c
pc = sum(comb(n_dc, i) for i in range(min(b01c, b10c) + 1)) / (2 ** n_dc) * 2 if n_dc else 1.0
print(f"  McNemar exacto (colision): {b10c} a favor del silo, {b01c} a favor de B0  ->  p = {min(pc,1):.3f}")
