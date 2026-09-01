"""¿EL 99.4% DE ACIERTO SE TRADUCE EN GANARLE A B0? — medicion punta a punta.

Se probaron las configuraciones que superan el 98.4% de acierto de ruteo:
  - producto proto x top-1, gamma=0.85   -> 99.4% acierto, 3.50 silos
  - lineal alpha=0.2,       gamma=0.70   -> 98.1% acierto, 3.00 silos
  + barrido fino de gamma para la lineal

Decision de ruteo con leave-one-out (sin fuga). Recuperacion sobre corpus completo.
Metrica: recall@3 del chunk de origen + contaminacion + silos abiertos.
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

SILOS = ["legal", "impositivo", "contable", "financiero"]
K = 3
DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}

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

# precomputar señales + resultados de recuperacion por subconjunto (cache)
casos = []
for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    uids = {u for u, _ in origen}
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    tops = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "AND NOT (chunk_uid = ANY(%s)) ORDER BY embedding <=> %s::vector LIMIT 3",
                    (vec, s, excluir, vec))
        tops[s] = [float(r[0]) for r in cur.fetchall()] or [0.0]
    casos.append({"vec": vec, "uids": uids, "dom": dom, "proto": dist, "tops": tops})

def recuperar(vec, silos):
    if silos is None:
        cur.execute("SELECT chunk_uid, fuente FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s", (vec, K))
    else:
        cur.execute("SELECT chunk_uid, fuente FROM chunks WHERE silo = ANY(%s) "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (silos, vec, K))
    return cur.fetchall()

def conjunto(p, gamma):
    tot = sum(p.values()) or 1.0
    p = {k: v / tot for k, v in p.items()}
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= gamma:
            break
    return sel

def correr(nombre, fn, gamma):
    hit, cont, exp = 0, [], []
    for c in casos:
        sel = conjunto(fn(c), gamma)
        r = recuperar(c["vec"], sel)
        hit += bool(c["uids"] & {u for u, _ in r})
        if r: cont.append(sum(1 for _, fu in r if DOM.get(fu) != c["dom"]) / len(r))
        exp.append(len(sel))
    n = len(casos)
    marca = ""
    print(f"  {nombre:38s} {hit/n:8.1%} {np.mean(cont):8.1%} {np.mean(exp):7.2f}{marca}")
    return hit / n, np.mean(cont), np.mean(exp)

# B0
hb, cb, _ = 0, [], None
for c in casos:
    r = recuperar(c["vec"], None)
    hb += bool(c["uids"] & {u for u, _ in r})
    cb.append(sum(1 for _, fu in r if DOM.get(fu) != c["dom"]) / max(len(r), 1))
n = len(casos)
b0_hit, b0_cont = hb / n, np.mean(cb)

print(f"PUNTA A PUNTA — {n} consultas · recall@{K}")
print()
print(f"  {'configuracion':38s} {'recall':>8s} {'sucio':>8s} {'silos':>7s}")
print(f"  {'B0 monolitico (referencia)':38s} {b0_hit:8.1%} {b0_cont:8.1%} {4.00:7.2f}")
print()
prod = lambda c: {s: c["proto"][s] * max(c["tops"][s][0], 1e-6) for s in SILOS}
lin02 = lambda c: {s: 0.2 * c["proto"][s] + 0.8 * c["tops"][s][0] for s in SILOS}
lin03 = lambda c: {s: 0.3 * c["proto"][s] + 0.7 * c["tops"][s][0] for s in SILOS}
mix = lambda c: {s: c["proto"][s] * max((c["tops"][s][0] + np.mean(c["tops"][s][:3])) / 2, 1e-6) for s in SILOS}

resultados = []
for g in (0.70, 0.80, 0.85, 0.90):
    resultados.append((f"producto, gamma={g}", *correr(f"producto, gamma={g}", prod, g)))
print()
for g in (0.60, 0.70, 0.80, 0.85):
    resultados.append((f"lineal a=0.2, gamma={g}", *correr(f"lineal a=0.2, gamma={g}", lin02, g)))
print()
for g in (0.70, 0.80, 0.85):
    resultados.append((f"lineal a=0.3, gamma={g}", *correr(f"lineal a=0.3, gamma={g}", lin03, g)))
print()
for g in (0.80, 0.85):
    resultados.append((f"prod+densidad, gamma={g}", *correr(f"prod+densidad, gamma={g}", mix, g)))
con.close()
print()
ganan = [r for r in resultados if r[1] > b0_hit]
igualan = [r for r in resultados if r[1] == b0_hit]
print(f"  >>> configuraciones que SUPERAN a B0 en recall: {len(ganan)}")
for nom, h, c, e in ganan:
    print(f"        {nom:34s} recall {h:.1%} (vs {b0_hit:.1%})  sucio {c:.1%} (vs {b0_cont:.1%})  silos {e:.2f}")
print(f"  >>> configuraciones que lo IGUALAN: {len(igualan)}")
for nom, h, c, e in igualan:
    print(f"        {nom:34s} sucio {c:.1%} (vs {b0_cont:.1%})  silos {e:.2f}")
