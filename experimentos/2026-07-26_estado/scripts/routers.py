"""¿COMO SE OPTIMIZA EL ROUTER? — comparacion de politicas, SIN circularidad.

Truco anti-fuga (leave-one-out): se EXCLUYE de la busqueda el chunk de origen de la
consulta. Asi el router no puede "encontrarse a si mismo": debe acertar el silo usando
el RESTO de la evidencia. Es el escenario real (una pregunta nueva cuyo chunk exacto
no esta indexado como respuesta obvia).

Acierto = el silo donde vive el chunk de origen esta en el conjunto elegido.
"""
import sys, io, json, random
from pathlib import Path
from collections import Counter

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

POLITICAS = ["proto top-1", "proto top-2 (HOY)", "sonda top-1 (mejor global)",
             "sonda VOTO (top-10)", "sonda MEJOR-POR-SILO", "COMBINADA proto+evidencia",
             "sonda VOTO 2 silos", "COMBINADA 2 silos"]
ok = {p: 0 for p in POLITICAS}
tam = {p: [] for p in POLITICAS}

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    silos_correctos = {s for _, s in origen}          # donde vive la evidencia
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"

    # --- señal 1: prototipo ---
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    orden_p = sorted(dist, key=dist.get, reverse=True)

    # --- señal 2: evidencia real, EXCLUYENDO el chunk de origen ---
    cur.execute("SELECT silo FROM chunks WHERE NOT (chunk_uid = ANY(%s)) "
                "ORDER BY embedding <=> %s::vector LIMIT 10", (excluir, vec))
    top10 = [r[0] for r in cur.fetchall()]
    voto = Counter(top10)
    mejor_por_silo = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks "
                    "WHERE silo = %s AND NOT (chunk_uid = ANY(%s)) "
                    "ORDER BY embedding <=> %s::vector LIMIT 1", (vec, s, excluir, vec))
        r = cur.fetchone()
        mejor_por_silo[s] = float(r[0]) if r else 0.0
    orden_e = sorted(mejor_por_silo, key=mejor_por_silo.get, reverse=True)

    # --- señal 3: combinada (rangos: suma de posiciones, menor = mejor) ---
    rango = {s: orden_p.index(s) + orden_e.index(s) for s in SILOS}
    orden_c = sorted(rango, key=rango.get)

    planes = {
        "proto top-1": orden_p[:1],
        "proto top-2 (HOY)": orden_p[:2],
        "sonda top-1 (mejor global)": top10[:1],
        "sonda VOTO (top-10)": [voto.most_common(1)[0][0]],
        "sonda MEJOR-POR-SILO": orden_e[:1],
        "COMBINADA proto+evidencia": orden_c[:1],
        "sonda VOTO 2 silos": [s for s, _ in voto.most_common(2)],
        "COMBINADA 2 silos": orden_c[:2],
    }
    for p, sel in planes.items():
        ok[p] += bool(silos_correctos & set(sel))
        tam[p].append(len(sel))

con.close()
n = len(consultas)
print(f"ACIERTO DEL ROUTER (sin fuga: el chunk de origen esta EXCLUIDO)  ·  {n} consultas")
print()
print(f"  {'politica de ruteo':32s} {'acierta el silo':>16s} {'silos':>7s}")
for p in sorted(POLITICAS, key=lambda x: -ok[x]/n):
    print(f"  {p:32s} {ok[p]/n:15.1%} {np.mean(tam[p]):7.2f}")
