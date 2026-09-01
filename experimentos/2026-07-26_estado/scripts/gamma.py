"""LA REGLA FINAL — cobertura acumulada: abrir silos en orden de score hasta sumar >= gamma.

Reemplaza el "siempre 2". Tamaño variable automatico, un solo parametro (gamma), que se
CALIBRA con el Golden. Aca se barre gamma para ver la forma de la curva y elegir un
punto de arranque declarado como provisional.

Score por silo = combinacion prototipo + evidencia (la mejor señal medida, C.47),
normalizada a distribucion. Señales con leave-one-out (sin fuga en la decision).
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
cur.execute("SELECT silo, embedding::text FROM chunks")
E = {}
for s, v in cur.fetchall():
    E.setdefault(s, []).append(np.array(json.loads(v)))
proto = {s: np.array(_centroide_l2(v)) for s, v in E.items()}

GAMMAS = [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 1.00]
datos = []   # por consulta: (orden de silos, distribucion, uids, dom, vec)

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    uids = {u for u, _ in origen}
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
    # score combinado -> distribucion (producto de las dos señales, normalizado)
    comb = {s: dist[s] * max(mejor[s], 1e-6) for s in SILOS}
    tot = sum(comb.values())
    p = {s: comb[s] / tot for s in SILOS}
    orden = sorted(p, key=p.get, reverse=True)
    datos.append((orden, p, uids, dom, vec))

print(f"REGLA DE COBERTURA ACUMULADA  ·  {len(datos)} consultas  ·  recall@{K}")
print()
print(f"  {'gamma':>6s} {'encuentra':>10s} {'silos':>7s} {'sucio':>8s}   reparto de tamaños")
for g in GAMMAS:
    hit = 0
    tam = []
    cont = []
    from collections import Counter
    rep = Counter()
    for orden, p, uids, dom, vec in datos:
        acum, sel = 0.0, []
        for s in orden:
            sel.append(s)
            acum += p[s]
            if acum >= g:
                break
        cur.execute("SELECT chunk_uid, fuente FROM chunks WHERE silo = ANY(%s) "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (sel, vec, K))
        r = cur.fetchall()
        hit += bool(uids & {u for u, _ in r})
        tam.append(len(sel)); rep[len(sel)] += 1
        if r:
            cont.append(sum(1 for _, fu in r if DOM.get(fu) != dom) / len(r))
    print(f"  {g:6.2f} {hit/len(datos):9.1%} {np.mean(tam):7.2f} {np.mean(cont):7.1%}   {dict(sorted(rep.items()))}")
con.close()
print()
print("  referencia: B0 84.4% / 4.00 silos / 17.3% sucio  ·  top-2 fijo HOY 70.0% / 2.00 / 25.8%")
