"""EL ESLABON QUE FALTA: detectar que el router se equivoco y CORREGIR.

Modo de falla real: el router elige mal -> la evidencia recuperada es POBRE comparada con
la que habia disponible. Eso es DETECTABLE sin saber la respuesta: si el mejor chunk del
silo elegido puntua mucho peor que el mejor chunk global, el ruteo probablemente fallo.

Dos mecanismos nuevos (ninguno medido antes):
  A. RESCATE EN SELECCION: ademas del score combinado, entra todo silo cuya EVIDENCIA CRUDA
     este a <= epsilon del mejor global (aunque el prototipo lo haya hundido).
  B. SUFICIENCIA + EXPANSION: se recupera del conjunto; si el mejor resultado esta a mas de
     delta por debajo del mejor global disponible -> se abre un silo mas y se reintenta.

Señales del router con leave-one-out (sin fuga). Recuperacion sobre corpus completo.
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

BR = ["B0 monolitico", "cobertura g=0.70 (C.50)",
      "+ RESCATE eps=0.03", "+ RESCATE eps=0.05",
      "+ SUFICIENCIA d=0.03", "RESCATE + SUFICIENCIA", "ORACULO (techo)"]
hit = {b: 0 for b in BR}
cont = {b: [] for b in BR}
expo = {b: [] for b in BR}

def recuperar(silos, vec, k=K):
    cur.execute("SELECT chunk_uid, fuente, 1 - (embedding <=> %s::vector) FROM chunks "
                "WHERE silo = ANY(%s) ORDER BY embedding <=> %s::vector LIMIT %s", (vec, silos, vec, k))
    return cur.fetchall()

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    uids = {u for u, _ in origen}
    silos_reales = list({s for _, s in origen})
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"

    # señales (leave-one-out)
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    mejor = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "AND NOT (chunk_uid = ANY(%s)) ORDER BY embedding <=> %s::vector LIMIT 1",
                    (vec, s, excluir, vec))
        r = cur.fetchone()
        mejor[s] = float(r[0]) if r else 0.0
    mejor_global = max(mejor.values())
    comb = {s: dist[s] * max(mejor[s], 1e-6) for s in SILOS}
    tot = sum(comb.values())
    p = {s: comb[s] / tot for s in SILOS}
    orden = sorted(p, key=p.get, reverse=True)

    base, acum = [], 0.0
    for s in orden:
        base.append(s); acum += p[s]
        if acum >= GAMMA:
            break

    def con_rescate(eps):
        """Entra todo silo cuya EVIDENCIA CRUDA este a <= eps del mejor global."""
        return list(dict.fromkeys(base + [s for s in SILOS if mejor[s] >= mejor_global - eps]))

    def con_suficiencia(sel, delta):
        """Si lo recuperado es mucho peor que lo disponible, abre un silo mas."""
        r = recuperar(sel, vec)
        if r and r[0][2] >= mejor_global - delta:
            return sel, r
        faltan = [s for s in orden if s not in sel]
        if faltan:
            sel = sel + [faltan[0]]
        return sel, recuperar(sel, vec)

    planes = {}
    cur.execute("SELECT chunk_uid, fuente, 1 - (embedding <=> %s::vector) FROM chunks "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (vec, vec, K))
    planes["B0 monolitico"] = (["*"] * 4, cur.fetchall())
    planes["cobertura g=0.70 (C.50)"] = (base, recuperar(base, vec))
    for eps in (0.03, 0.05):
        sel = con_rescate(eps)
        planes[f"+ RESCATE eps={eps:.2f}"] = (sel, recuperar(sel, vec))
    sel_s, r_s = con_suficiencia(base, 0.03)
    planes["+ SUFICIENCIA d=0.03"] = (sel_s, r_s)
    sel_rs, r_rs = con_suficiencia(con_rescate(0.03), 0.03)
    planes["RESCATE + SUFICIENCIA"] = (sel_rs, r_rs)
    planes["ORACULO (techo)"] = (silos_reales, recuperar(silos_reales, vec))

    for b, (sel, r) in planes.items():
        hit[b] += bool(uids & {x[0] for x in r})
        if r:
            cont[b].append(sum(1 for x in r if DOM.get(x[1]) != dom) / len(r))
        expo[b].append(len(sel))

con.close()
n = len(consultas)
print(f"DETECTAR Y CORREGIR EL ERROR DE RUTEO  ·  {n} consultas  ·  recall@{K}")
print()
print(f"  {'politica':28s} {'encuentra':>10s} {'sucio':>8s} {'silos':>7s}")
for b in BR:
    m = "  <-- SUPERA A B0" if b not in ("B0 monolitico", "ORACULO (techo)") and hit[b] > hit["B0 monolitico"] else ""
    print(f"  {b:28s} {hit[b]/n:9.1%} {np.mean(cont[b]):7.1%} {np.mean(expo[b]):7.2f}{m}")
