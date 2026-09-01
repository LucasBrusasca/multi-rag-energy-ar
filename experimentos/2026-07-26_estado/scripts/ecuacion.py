"""LA ECUACION DEL PROBLEMA: ¿que acierto de ruteo hace falta para superar a B0?

recall_total = acc * recall_si_acierta + (1-acc) * recall_si_falla

Se miden los dos terminos por separado y se despeja el acierto necesario.
Ademas: ¿cuanto recall da abrir N silos con acierto perfecto? (para ver si conviene
abrir mas o menos).
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

acierta_hit = [0, 0]   # [aciertos, casos] cuando el silo correcto ESTA en el conjunto
falla_hit = [0, 0]     # cuando NO esta
b0_hit = 0

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    uids = {u for u, _ in origen}
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
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= GAMMA:
            break
    cur.execute("SELECT chunk_uid FROM chunks WHERE silo = ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (sel, vec, K))
    h = bool(uids & {r[0] for r in cur.fetchall()})
    if correctos & set(sel):
        acierta_hit[0] += h; acierta_hit[1] += 1
    else:
        falla_hit[0] += h; falla_hit[1] += 1
    cur.execute("SELECT chunk_uid FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s", (vec, K))
    b0_hit += bool(uids & {r[0] for r in cur.fetchall()})

# ¿cuanto da abrir exactamente N silos con acierto PERFECTO?
print("PARTE 1 — la ecuacion")
print()
ra = acierta_hit[0] / max(acierta_hit[1], 1)
rf = falla_hit[0] / max(falla_hit[1], 1)
n = len(consultas)
b0 = b0_hit / n
acc = acierta_hit[1] / n
print(f"  acierto de ruteo actual              : {acc:.1%}  ({acierta_hit[1]}/{n})")
print(f"  recall CUANDO el ruteo acierta       : {ra:.1%}")
print(f"  recall CUANDO el ruteo falla         : {rf:.1%}   ({falla_hit[1]} casos)")
print(f"  recall total = {acc:.3f}*{ra:.3f} + {1-acc:.3f}*{rf:.3f} = {acc*ra+(1-acc)*rf:.1%}")
print(f"  B0 monolitico                        : {b0:.1%}")
print()
if ra > rf:
    necesario = (b0 - rf) / (ra - rf)
    print(f"  >>> ACIERTO NECESARIO PARA IGUALAR A B0: {necesario:.1%}")
    print(f"  >>> hoy estamos en {acc:.1%}  ->  faltan {(necesario-acc)*100:.1f} puntos de ACIERTO DE RUTEO")
print()
print("PARTE 2 — ¿conviene abrir mas o menos silos? (con acierto perfecto, oraculo)")
cur.execute("SELECT COUNT(*) FROM chunks")
con.close()
print("  (medido antes, C.46): oraculo 1.11 silos -> 87.5% · B0 4 silos -> 84.4%")
print("  => abrir MAS silos converge a B0 (84.4%) por definicion. Superarlo exige")
print("     abrir POCOS silos con acierto MUY alto. No hay otra via aritmetica.")
