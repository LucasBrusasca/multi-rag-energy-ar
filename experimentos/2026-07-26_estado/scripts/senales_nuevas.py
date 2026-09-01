"""INFORMACION QUE LA BUSQUEDA NO TIENE — dos señales de ruteo ortogonales al coseno.

Diagnostico: el router y el retriever usan el MISMO coseno bge-m3 -> el router no puede
saber mas que el retriever -> empate estructural. Para romperlo hace falta informacion
de otra naturaleza.

SEÑAL 1 — ANCLAS LEXICAS: entidades y normas nombradas en la pregunta (ENRE, ENARGAS,
CAMMESA, AFIP/ARCA, Ley 24.065, RG 830...). El embedding las diluye en 1024 dims; un
regex las ve directo y son casi determinantes del dominio.

SEÑAL 2 — BM25 POR SILO: relevancia lexica (Postgres FTS) calculada dentro de cada silo.
Ortogonal al coseno: capta el termino exacto, no el parecido semantico.

Se mide el acierto de ruteo de cada señal sola y combinada con la actual.
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
DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}

# SEÑAL 1: anclas lexicas -> silo (conocimiento de dominio, explicito y auditable)
ANCLAS = [
    (r"\bENRE\b|ENARGAS|CAMMESA|Secretar[ií]a de Energ[ií]a|mercado el[eé]ctrico mayorista|MEM\b|distribuidora|transportista|concesionari", "legal"),
    (r"\bAFIP\b|\bARCA\b|Tribunal Fiscal|contribuyente|declaraci[oó]n jurada|hecho imponible|al[ií]cuota|IVA|Ganancias|retenci[oó]n(es)? impositiv|RG\s*\d+", "impositivo"),
    (r"estados? contables?|balance|patrimonio neto|activo corriente|pasivo|asiento|RT\s*\d+|NIIF|auditor[ií]a", "contable"),
    (r"flujo de fondos|obligaci[oó]n negociable|tasa de inter[eé]s|calificaci[oó]n|EBITDA|endeudamiento|inversores|emisi[oó]n", "financiero"),
    (r"Ley\s*N?[º°]?\s*24\.?065|24065|energ[ií]a el[eé]ctrica", "legal"),
    (r"Ley\s*N?[º°]?\s*11\.?683|11683|procedimiento fiscal", "impositivo"),
    (r"Ley\s*N?[º°]?\s*24\.?076|24076|gas natural", "legal"),
]

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

datos = []
n_con_ancla = 0
for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    excluir = [u for u, _ in origen]
    correctos = {s for _, s in origen}
    q = np.array(embed_query(t))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    ev = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "AND NOT (chunk_uid = ANY(%s)) ORDER BY embedding <=> %s::vector LIMIT 1",
                    (vec, s, excluir, vec))
        r = cur.fetchone(); ev[s] = float(r[0]) if r else 0.0
    # SEÑAL 1: anclas
    anclas = {s: 0.0 for s in SILOS}
    for pat, silo in ANCLAS:
        if re.search(pat, t, re.I):
            anclas[silo] += 1.0
    if sum(anclas.values()) > 0:
        n_con_ancla += 1
    # SEÑAL 2: BM25 por silo (Postgres FTS)
    bm = {}
    for s in SILOS:
        cur.execute("""SELECT COALESCE(MAX(ts_rank(to_tsvector('spanish', contenido),
                              plainto_tsquery('spanish', %s))), 0)
                       FROM chunks WHERE silo = %s AND NOT (chunk_uid = ANY(%s))""",
                    (t, s, excluir))
        bm[s] = float(cur.fetchone()[0])
    datos.append({"correctos": correctos, "proto": dist, "ev": ev, "anclas": anclas, "bm": bm})
con.close()

def norm(d):
    tot = sum(d.values())
    return {k: (v / tot if tot > 0 else 1.0 / len(d)) for k, v in d.items()}

def conjunto(p, gamma=GAMMA):
    p = norm(p)
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= gamma:
            break
    return sel

def ev_(nombre, fn):
    ok, tam = 0, []
    for d in datos:
        sel = conjunto(fn(d))
        ok += bool(d["correctos"] & set(sel)); tam.append(len(sel))
    print(f"  {nombre:46s} {ok/len(datos):7.1%}  silos={np.mean(tam):.2f}")
    return ok / len(datos)

n = len(datos)
print(f"SEÑALES NUEVAS — {n} consultas · objetivo 98.4% con POCOS silos")
print(f"  consultas con ancla lexica detectada: {n_con_ancla}/{n} ({n_con_ancla/n:.0%})")
print()
ev_("ACTUAL: proto x evidencia", lambda d: {s: d["proto"][s] * max(d["ev"][s], 1e-6) for s in SILOS})
print()
print("  --- señal 1: ANCLAS LEXICAS ---")
ev_("solo anclas (sin ancla -> uniforme)", lambda d: {s: d["anclas"][s] + 1e-6 for s in SILOS})
ev_("actual + ancla como bonus (x2 si hay ancla)",
    lambda d: {s: d["proto"][s] * max(d["ev"][s], 1e-6) * (2.0 if d["anclas"][s] > 0 else 1.0) for s in SILOS})
ev_("actual + ancla fuerte (x5)",
    lambda d: {s: d["proto"][s] * max(d["ev"][s], 1e-6) * (5.0 if d["anclas"][s] > 0 else 1.0) for s in SILOS})
print()
print("  --- señal 2: BM25 por silo ---")
ev_("solo BM25", lambda d: {s: max(d["bm"][s], 1e-9) for s in SILOS})
ev_("actual x BM25", lambda d: {s: d["proto"][s] * max(d["ev"][s], 1e-6) * max(d["bm"][s], 1e-4) for s in SILOS})
ev_("actual + BM25 normalizado (suma)",
    lambda d: {s: norm({k: d["proto"][k] * max(d["ev"][k], 1e-6) for k in SILOS})[s]
                  + norm({k: max(d["bm"][k], 1e-9) for k in SILOS})[s] for s in SILOS})
print()
print("  --- las TRES juntas ---")
ev_("proto x evid x BM25 x ancla(x2)",
    lambda d: {s: d["proto"][s] * max(d["ev"][s], 1e-6) * max(d["bm"][s], 1e-4)
                  * (2.0 if d["anclas"][s] > 0 else 1.0) for s in SILOS})
ev_("suma normalizada de las 3 + ancla(x2)",
    lambda d: {s: (norm({k: d["proto"][k] * max(d["ev"][k], 1e-6) for k in SILOS})[s]
                   + norm({k: max(d["bm"][k], 1e-9) for k in SILOS})[s])
                  * (2.0 if d["anclas"][s] > 0 else 1.0) for s in SILOS})
