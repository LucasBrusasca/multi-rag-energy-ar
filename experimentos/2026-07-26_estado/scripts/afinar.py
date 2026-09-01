"""LOS 2.2 PUNTOS QUE FALTAN — palancas GRATIS sobre la señal de ruteo.

Hoy: score_silo = prototipo x mejor_evidencia(top-1)   -> 96.2% de acierto
Necesario para ganarle a B0: 98.4%

Palancas nunca probadas (ninguna necesita descargar nada):
  A. DENSIDAD: usar el promedio del top-3 del silo en vez del top-1 (Codex D_s)
  B. AGREGACIONES: max / media top-3 / suma top-3 / media ponderada
  C. PESO alpha: combinacion lineal calibrada en vez del producto fijo
  D. DETECTOR DE POLISEMIA: si la pregunta trae un termino colisionante y el margen
     es chico -> forzar la apertura del 2do silo (idea de Grok, usa dominio)

Metrica: acierto de ruteo (el silo con la evidencia esta en el conjunto), leave-one-out.
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
GAMMA = 0.70
POLISEMICOS = r"retenci[oó]n|tasa|sanci[oó]n|plazo|inter[eé]s|intereses|ajuste|vigencia|prescripci[oó]n|multa|resultado|activo|deuda"
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

# --- precomputar señales por consulta (una sola pasada, sin API) ---
datos = []
for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    correctos = {s for _, s in origen}
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    tops = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "AND NOT (chunk_uid = ANY(%s)) ORDER BY embedding <=> %s::vector LIMIT 5",
                    (vec, s, excluir, vec))
        tops[s] = [float(r[0]) for r in cur.fetchall()] or [0.0]
    datos.append({"correctos": correctos, "proto": dist, "tops": tops, "texto": t})
con.close()

def conjunto(p, gamma=GAMMA):
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= gamma:
            break
    return sel

def normalizar(d):
    tot = sum(d.values()) or 1.0
    return {k: v / tot for k, v in d.items()}

def evaluar(nombre, fn_score, forzar_polisemia=False):
    ok, tam = 0, []
    for d in datos:
        sc = fn_score(d)
        p = normalizar(sc)
        sel = conjunto(p)
        if forzar_polisemia and re.search(POLISEMICOS, d["texto"], re.I) and len(sel) == 1:
            orden = sorted(p, key=p.get, reverse=True)
            sel = orden[:2]
        ok += bool(d["correctos"] & set(sel)); tam.append(len(sel))
    print(f"  {nombre:44s} {ok/len(datos):7.1%}  silos={np.mean(tam):.2f}")
    return ok / len(datos)

print(f"ACIERTO DE RUTEO — {len(datos)} consultas · objetivo 98.4% para ganarle a B0")
print()
base = evaluar("ACTUAL: proto x top-1", lambda d: {s: d["proto"][s] * max(d["tops"][s][0], 1e-6) for s in SILOS})
print()
print("  --- A: densidad (usar mas evidencia por silo) ---")
evaluar("proto x media(top-3)", lambda d: {s: d["proto"][s] * max(np.mean(d["tops"][s][:3]), 1e-6) for s in SILOS})
evaluar("proto x media(top-5)", lambda d: {s: d["proto"][s] * max(np.mean(d["tops"][s][:5]), 1e-6) for s in SILOS})
evaluar("proto x suma(top-3)", lambda d: {s: d["proto"][s] * max(sum(d["tops"][s][:3]), 1e-6) for s in SILOS})
evaluar("proto x (top1 + media top3)/2",
        lambda d: {s: d["proto"][s] * max((d["tops"][s][0] + np.mean(d["tops"][s][:3])) / 2, 1e-6) for s in SILOS})
print()
print("  --- B: combinacion LINEAL con peso alpha (en vez del producto) ---")
for a in (0.2, 0.3, 0.5, 0.7):
    evaluar(f"alpha={a}: {a}*proto + {1-a:.1f}*evidencia",
            lambda d, a=a: {s: a * d["proto"][s] + (1 - a) * d["tops"][s][0] for s in SILOS})
print()
print("  --- C: solo evidencia, distintas agregaciones ---")
evaluar("solo top-1", lambda d: {s: max(d["tops"][s][0], 1e-6) for s in SILOS})
evaluar("solo media(top-3)", lambda d: {s: max(np.mean(d["tops"][s][:3]), 1e-6) for s in SILOS})
print()
print("  --- D: detector de polisemia sobre la mejor variante ---")
evaluar("proto x top-1  + POLISEMIA",
        lambda d: {s: d["proto"][s] * max(d["tops"][s][0], 1e-6) for s in SILOS}, forzar_polisemia=True)
evaluar("proto x media(top-3) + POLISEMIA",
        lambda d: {s: d["proto"][s] * max(np.mean(d["tops"][s][:3]), 1e-6) for s in SILOS}, forzar_polisemia=True)
print()
print("  --- E: barrido de gamma sobre la señal actual ---")
for g in (0.75, 0.80, 0.85):
    ok, tam = 0, []
    for d in datos:
        p = normalizar({s: d["proto"][s] * max(d["tops"][s][0], 1e-6) for s in SILOS})
        sel = conjunto(p, g)
        ok += bool(d["correctos"] & set(sel)); tam.append(len(sel))
    print(f"  {'gamma=' + str(g):44s} {ok/len(datos):7.1%}  silos={np.mean(tam):.2f}")
