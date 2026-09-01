"""DONDE EL MONOLITICO FALLA OPERATIVAMENTE — medicion a escala simulada.

Idea de Lucas: "si el monolitico es lento, aprovechar la segmentacion donde el
monolitico falla". Tus docs ya lo pedian (NOTAS §11: metricas operativas).

Simulacion: corpus duplicado 20x (54.180 vectores de 1024d) en una tabla scratch.
Se construyen: 1 indice HNSW GLOBAL vs 4 indices HNSW PARCIALES (uno por silo).
Se mide:
  - tiempo de CONSTRUCCION (global vs cada parcial)  -> localidad de mantenimiento:
    si cambia la normativa de UN dominio, ¿cuanto cuesta reindexar?
  - TAMAÑO de cada indice (RAM/disco)
  - LATENCIA de consulta: global vs un-silo vs fan-out de 4
⚠️ Duplicados exactos (sin ruido): valido para latencia/tamaño/build, NO para calidad.
⚠️ Tabla scratch `_escala_tmp`: se crea y SE BORRA al final. La tabla chunks NO se toca.
"""
import sys, io, time, json, random
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar

FACTOR = 20
con = conectar(); con.autocommit = True
cur = con.cursor()

print(f"ESCALA SIMULADA: corpus x{FACTOR}")
cur.execute("DROP TABLE IF EXISTS _escala_tmp")
t0 = time.perf_counter()
cur.execute(f"""CREATE UNLOGGED TABLE _escala_tmp AS
                SELECT silo, embedding FROM chunks CROSS JOIN generate_series(1, {FACTOR})""")
cur.execute("SELECT COUNT(*) FROM _escala_tmp")
n = cur.fetchone()[0]
print(f"  tabla scratch creada: {n} filas ({time.perf_counter()-t0:.0f}s)")
print()

# --- construccion de indices ---
tiempos = {}
print("CONSTRUCCION DE INDICES (el costo de re-indexar cuando cambia la normativa):")
t0 = time.perf_counter()
cur.execute("CREATE INDEX _e_global ON _escala_tmp USING hnsw (embedding vector_cosine_ops)")
tiempos["GLOBAL (todo)"] = time.perf_counter() - t0
print(f"  GLOBAL      : {tiempos['GLOBAL (todo)']:7.1f}s")
for s in ("legal", "impositivo", "contable", "financiero"):
    t0 = time.perf_counter()
    cur.execute(f"CREATE INDEX _e_{s} ON _escala_tmp USING hnsw (embedding vector_cosine_ops) "
                f"WHERE silo = '{s}'")
    tiempos[s] = time.perf_counter() - t0
    print(f"  parcial {s:11s}: {tiempos[s]:7.1f}s")
print()

# --- tamaños ---
print("TAMAÑO DE CADA INDICE (RAM/disco):")
tam = {}
for nombre, idx in [("GLOBAL", "_e_global"), ("legal", "_e_legal"), ("impositivo", "_e_impositivo"),
                    ("contable", "_e_contable"), ("financiero", "_e_financiero")]:
    cur.execute(f"SELECT pg_relation_size('{idx}')")
    tam[nombre] = cur.fetchone()[0]
    print(f"  {nombre:12s}: {tam[nombre]/1e6:8.1f} MB")
print()

# --- latencias ---
cur.execute("SELECT embedding::text FROM chunks ORDER BY RANDOM() LIMIT 40")
consultas = [r[0] for r in cur.fetchall()]
cur.execute("SET enable_seqscan = off")

def lat(sql, params_fn):
    ts = []
    for q in consultas:
        t0 = time.perf_counter()
        cur.execute(sql, params_fn(q))
        cur.fetchall()
        ts.append((time.perf_counter() - t0) * 1000)
    ts = np.array(ts)
    return np.median(ts), np.percentile(ts, 95)

print("LATENCIA DE CONSULTA (top-10, 40 consultas, mediana / p95):")
m, p = lat("SELECT silo FROM _escala_tmp ORDER BY embedding <=> %s::vector LIMIT 10",
           lambda q: (q,))
print(f"  GLOBAL (monolitico)          : {m:7.1f} ms  /  p95 {p:7.1f} ms")
m1, p1 = lat("SELECT silo FROM _escala_tmp WHERE silo = 'legal' "
             "ORDER BY embedding <=> %s::vector LIMIT 10", lambda q: (q,))
print(f"  UN silo (gobernanza sabe)    : {m1:7.1f} ms  /  p95 {p1:7.1f} ms")
ts = []
for q in consultas:
    t0 = time.perf_counter()
    for s in ("legal", "impositivo", "contable", "financiero"):
        cur.execute(f"SELECT silo FROM _escala_tmp WHERE silo = '{s}' "
                    "ORDER BY embedding <=> %s::vector LIMIT 10", (q,))
        cur.fetchall()
    ts.append((time.perf_counter() - t0) * 1000)
ts = np.array(ts)
print(f"  FAN-OUT 4 silos (= B0 exacto): {np.median(ts):7.1f} ms  /  p95 {np.percentile(ts,95):7.1f} ms")
print()

# --- resumen de mantenimiento ---
print("LOCALIDAD DE MANTENIMIENTO (cambia la normativa de UN dominio):")
print(f"  monolitico: reindexar TODO      = {tiempos['GLOBAL (todo)']:.0f}s")
print(f"  segregado : reindexar UN silo   = {min(tiempos[s] for s in ('legal','impositivo','contable','financiero')):.0f}"
      f"-{max(tiempos[s] for s in ('legal','impositivo','contable','financiero')):.0f}s segun el silo")
print()

cur.execute("DROP TABLE _escala_tmp")
print("tabla scratch eliminada — la base quedo como estaba.")
con.close()
