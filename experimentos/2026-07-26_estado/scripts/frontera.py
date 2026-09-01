"""LA CURVA REAL DE LA TESIS: cuanto se puede RESTRINGIR antes de perder evidencia.

B0 es el techo de recall (verificado 100/100). Entonces el criterio de exito NO es recall:
es "igualar el recall de B0 exponiendo MENOS dominio al generador".

Se mide, para cada politica de seleccion de silos:
  - recall@3 del chunk de origen
  - EXPOSICION: cuantos silos se abren
  - CONTAMINACION: % del contexto entregado que NO es del dominio de la pregunta
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

BRAZOS = ["B0 monolitico", "B1 prototipo top-2 (HOY)", "sonda 1 silo", "sonda 2 silos", "ORACULO 1 silo"]
acierto = {b: 0 for b in BRAZOS}
contam = {b: [] for b in BRAZOS}
expos = {b: [] for b in BRAZOS}

def recuperar(vec, silos):
    if silos is None:
        cur.execute("SELECT chunk_uid, silo FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s", (vec, K))
    else:
        cur.execute("SELECT chunk_uid, silo FROM chunks WHERE silo = ANY(%s) "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (silos, vec, K))
    return cur.fetchall()

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    uids = {r[0] for r in cur.fetchall()}
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"

    d = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    top2 = sorted(d, key=d.get, reverse=True)[:2]
    cur.execute("SELECT silo FROM chunks ORDER BY embedding <=> %s::vector LIMIT 10", (vec,))
    sonda = list(dict.fromkeys(r[0] for r in cur.fetchall()))

    planes = {"B0 monolitico": None, "B1 prototipo top-2 (HOY)": top2,
              "sonda 1 silo": sonda[:1], "sonda 2 silos": sonda[:2], "ORACULO 1 silo": [dom]}
    for b, silos in planes.items():
        r = recuperar(vec, silos)
        acierto[b] += bool(uids & {u for u, _ in r})
        contam[b].append(sum(1 for _, s in r if s != dom) / max(len(r), 1))
        expos[b].append(4 if silos is None else len(silos))

con.close()
n = len(consultas)
print(f"FRONTERA COBERTURA <-> EXPOSICION  ·  {n} consultas silver  ·  recall@{K}")
print()
print(f"  {'politica':28s} {'recall':>8s} {'silos':>7s} {'contaminacion del contexto':>28s}")
for b in BRAZOS:
    print(f"  {b:28s} {acierto[b]/n:7.1%} {np.mean(expos[b]):7.2f} {np.mean(contam[b]):27.1%}")
print()
print("  contaminacion = % de los chunks entregados al generador que NO son del dominio de la pregunta")
print("  (con el GT debil del silver: 'dominio' = dominio nominal del documento de origen)")
