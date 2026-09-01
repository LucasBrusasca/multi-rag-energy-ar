"""LAS 6 FALLAS: ¿son detectables SIN saber la respuesta?

Todo el gap contra B0 son 6 consultas de 160 donde el router excluye el silo correcto
y el recall cae a CERO. Se inspecciona cada una y se busca una señal que las distinga
de las 154 que funcionan.
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
K, GAMMA = 3, 0.70
con = conectar(); cur = con.cursor()
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

fallas, ok = [], []
for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    correctos = {s for _, s in origen}
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
    orden = sorted(p, key=p.get, reverse=True)
    sel, acum = [], 0.0
    for s in orden:
        sel.append(s); acum += p[s]
        if acum >= GAMMA:
            break
    # señales SIN saber la respuesta
    mejor_sel = max(mejor[s] for s in sel)
    mejor_fuera = max([mejor[s] for s in SILOS if s not in sel], default=0.0)
    señales = {"cobertura_alcanzada": acum, "p_top": p[orden[0]],
               "mejor_en_seleccion": mejor_sel, "mejor_fuera": mejor_fuera,
               "brecha_dentro_fuera": mejor_sel - mejor_fuera, "n_sel": len(sel)}
    reg = (t, f, dom, sel, list(correctos), señales)
    (ok if (correctos & set(sel)) else fallas).append(reg)
con.close()

print(f"LAS {len(fallas)} FALLAS (el router excluyo el silo donde vive la evidencia)")
print()
for t, f, dom, sel, cor, s in fallas:
    print(f'  "{t[:52]}"')
    print(f'     doc={f[:30]}  evidencia en={cor}  router abrio={sel}')
    print(f'     mejor evidencia DENTRO={s["mejor_en_seleccion"]:.3f}  FUERA={s["mejor_fuera"]:.3f}  '
          f'brecha={s["brecha_dentro_fuera"]:+.3f}')
print()
print("¿HAY SEÑAL QUE LAS SEPARE? (media en fallas vs media en las 154 que funcionan)")
print()
for k in ("cobertura_alcanzada", "p_top", "mejor_en_seleccion", "mejor_fuera", "brecha_dentro_fuera", "n_sel"):
    a = np.mean([r[5][k] for r in fallas])
    b = np.mean([r[5][k] for r in ok])
    print(f"  {k:24s} fallas={a:7.3f}   ok={b:7.3f}   dif={a-b:+7.3f}")
print()
# ¿una regla simple las atrapa?
print("REGLA CANDIDATA: si la mejor evidencia FUERA del conjunto supera a la de DENTRO -> abrir mas")
atrapa = sum(1 for r in fallas if r[5]["brecha_dentro_fuera"] < 0)
falsos = sum(1 for r in ok if r[5]["brecha_dentro_fuera"] < 0)
print(f"  atrapa {atrapa}/{len(fallas)} fallas   ·   falsas alarmas {falsos}/{len(ok)} ({falsos/len(ok):.1%})")
