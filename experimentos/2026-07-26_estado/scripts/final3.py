"""PUNTA A PUNTA con la señal LEXICA (BM25) incorporada al ruteo.

Hallazgo: BM25 por silo da 89.4% de acierto con solo 1.80 silos (vs 96.2% con 2.82).
Menos silos = mas beneficio de filtrado. La pregunta es si el saldo neto gana.
Se mide recall@3 real de cada combinacion, con barrido de gamma.
"""
import sys, io, json, random, re
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

casos = []
for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    uids = {u for u, _ in origen}
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    ev, bm = {}, {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "AND NOT (chunk_uid = ANY(%s)) ORDER BY embedding <=> %s::vector LIMIT 1",
                    (vec, s, excluir, vec))
        r = cur.fetchone(); ev[s] = float(r[0]) if r else 0.0
        cur.execute("""SELECT COALESCE(MAX(ts_rank(to_tsvector('spanish', contenido),
                              plainto_tsquery('spanish', %s))), 0)
                       FROM chunks WHERE silo = %s AND NOT (chunk_uid = ANY(%s))""", (t, s, excluir))
        bm[s] = float(cur.fetchone()[0])
    casos.append({"vec": vec, "uids": uids, "dom": dom, "proto": dist, "ev": ev, "bm": bm})

def norm(d):
    tot = sum(d.values())
    return {k: (v / tot if tot > 0 else 1.0 / len(d)) for k, v in d.items()}

def conjunto(p, g):
    p = norm(p)
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= g:
            break
    return sel

def recuperar(vec, silos):
    if silos is None:
        cur.execute("SELECT chunk_uid, fuente FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s", (vec, K))
    else:
        cur.execute("SELECT chunk_uid, fuente FROM chunks WHERE silo = ANY(%s) "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (silos, vec, K))
    return cur.fetchall()

hb, cb = 0, []
for c in casos:
    r = recuperar(c["vec"], None)
    hb += bool(c["uids"] & {u for u, _ in r})
    cb.append(sum(1 for _, fu in r if DOM.get(fu) != c["dom"]) / max(len(r), 1))
n = len(casos)
b0h, b0c = hb / n, np.mean(cb)

SEÑALES = {
    "actual (proto x evid)": lambda c: {s: c["proto"][s] * max(c["ev"][s], 1e-6) for s in SILOS},
    "solo BM25": lambda c: {s: max(c["bm"][s], 1e-9) for s in SILOS},
    "actual x BM25": lambda c: {s: c["proto"][s] * max(c["ev"][s], 1e-6) * max(c["bm"][s], 1e-4) for s in SILOS},
    "actual + BM25 (suma norm)": lambda c: {s: norm({k: c["proto"][k] * max(c["ev"][k], 1e-6) for k in SILOS})[s]
                                              + norm({k: max(c["bm"][k], 1e-9) for k in SILOS})[s] for s in SILOS},
    "evid + BM25 (suma norm)": lambda c: {s: norm({k: max(c["ev"][k], 1e-6) for k in SILOS})[s]
                                            + norm({k: max(c["bm"][k], 1e-9) for k in SILOS})[s] for s in SILOS},
}

print(f"PUNTA A PUNTA con señal lexica · {n} consultas · recall@{K}")
print(f"  B0 monolitico: recall {b0h:.1%} · sucio {b0c:.1%} · 4.00 silos")
print()
print(f"  {'configuracion':36s} {'gamma':>6s} {'recall':>8s} {'sucio':>8s} {'silos':>7s}")
mejores = []
for nom, fn in SEÑALES.items():
    for g in (0.60, 0.70, 0.80, 0.90):
        hit, cont, exp = 0, [], []
        for c in casos:
            sel = conjunto(fn(c), g)
            r = recuperar(c["vec"], sel)
            hit += bool(c["uids"] & {u for u, _ in r})
            if r: cont.append(sum(1 for _, fu in r if DOM.get(fu) != c["dom"]) / len(r))
            exp.append(len(sel))
        rec, suc, ex = hit / n, np.mean(cont), np.mean(exp)
        marca = "  <<< SUPERA A B0" if rec > b0h else ("  = B0" if rec == b0h else "")
        print(f"  {nom:36s} {g:6.2f} {rec:8.1%} {suc:8.1%} {ex:7.2f}{marca}")
        mejores.append((nom, g, rec, suc, ex))
    print()
con.close()
gan = [m for m in mejores if m[2] > b0h]
print(f"  >>> SUPERAN a B0: {len(gan)}")
for nom, g, rec, suc, ex in sorted(gan, key=lambda x: -x[2]):
    print(f"       {nom} (gamma={g}): recall {rec:.1%} vs {b0h:.1%} · sucio {suc:.1%} vs {b0c:.1%} · {ex:.2f} silos")
