"""VERIFICACION TOTAL del proyecto: no lee codigo, lo EJECUTA.

La auditoria de C.76 leyo los archivos. Leer no alcanza: el bug de `<==>` estaba a la
vista y solo se probo que rompia cuando se lo ejecuto. Este script EJECUTA:

  1. importa cada modulo (un import roto se ve al instante)
  2. valida TODOS los operadores pgvector de todos los SQL del proyecto
  3. corre el camino de produccion de punta a punta: clasificar -> gate -> buscar ->
     buscar_ruteado, con consultas reales
  4. audita la integridad de la base (dimensiones, nulos, silos, silo_scores, uid)
  5. verifica que schema.sql y el INSERT de pipeline.py coincidan con la tabla real
  6. verifica que cada constante importada de config exista

No escribe NADA. Solo lee y ejecuta lecturas.
"""
import sys, io, re, json, traceback
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
ING = RAIZ / "src" / "ingestion"
sys.path.insert(0, str(ING))

fallos, avisos, oks = [], [], []


def marca(estado, msg):
    (fallos if estado == "FALLA" else avisos if estado == "AVISO" else oks).append(msg)
    icono = {"FALLA": "[FALLA]", "AVISO": "[AVISO]", "OK": "[ ok  ]"}[estado]
    print(f"{icono} {msg}", flush=True)


# ---------------- 1. IMPORTS ----------------
print("\n--- 1. IMPORTS de cada modulo ---")
MODULOS = ["db", "config", "embedder", "chunker", "clasificador", "gate",
           "retriever", "generador", "llm", "veto", "self_training"]
importados = {}
for m in MODULOS:
    try:
        importados[m] = __import__(m)
        marca("OK", f"import {m}")
    except Exception as e:
        marca("FALLA", f"import {m} -> {type(e).__name__}: {e}")

# contextualizador es de A14: puede no existir todavia
try:
    __import__("contextualizador")
    marca("OK", "import contextualizador (A14 ya construido)")
except ModuleNotFoundError:
    marca("AVISO", "contextualizador.py no existe todavia (A14 pendiente) - esperado")
except Exception as e:
    marca("FALLA", f"import contextualizador -> {type(e).__name__}: {e}")

# ---------------- 2. OPERADORES pgvector EN TODO EL SQL ----------------
print("\n--- 2. operadores pgvector en todos los .py y .sql ---")
VALIDOS = {"<->", "<=>", "<#>", "<+>", "<~>", "<%>"}
patron = re.compile(r"<[=#+~%\-]{1,3}>")
encontrados = 0
for arch in sorted(list(ING.glob("*.py")) + list(ING.glob("*.sql"))):
    texto = arch.read_text(encoding="utf-8", errors="replace")
    for i, linea in enumerate(texto.splitlines(), 1):
        for op in patron.findall(linea):
            if "embedding" not in linea and "vector" not in linea:
                continue
            encontrados += 1
            if op not in VALIDOS:
                marca("FALLA", f"{arch.name}:{i} operador INVALIDO '{op}' -> {linea.strip()[:70]}")
if encontrados:
    marca("OK", f"{encontrados} operador(es) pgvector revisado(s)")

# ---------------- 3. CAMINO DE PRODUCCION, EJECUTADO ----------------
print("\n--- 3. camino de produccion ejecutado con consultas reales ---")
CONSULTAS = [
    "¿Qué obligaciones tienen los agentes de retención?",
    "¿Cómo se compone el patrimonio neto al cierre del ejercicio?",
    "¿Qué facultades tiene el ENRE sobre la calidad del servicio?",
]
try:
    from clasificador import clasificar
    from gate import evaluar_incertidumbre
    from retriever import buscar, buscar_ruteado
    from config import SILOS

    for q in CONSULTAS:
        r = clasificar(q)
        assert abs(sum(r["silo_scores"].values()) - 1.0) < 1e-6, "silo_scores no suma 1"
        assert r["silo"] in SILOS, f"silo desconocido {r['silo']}"
        g = evaluar_incertidumbre(r["silo_scores"])
        assert 0.0 <= g["entropia"] <= 1.0, f"entropia fuera de rango: {g['entropia']}"
        marca("OK", f"clasificar+gate: '{q[:38]}...' -> {r['silo']} (H={g['entropia']}, "
                    f"{'S2' if g['ambiguo'] else 'S1'})")

    # buscar() monolitico
    res = buscar(CONSULTAS[0])
    assert len(res) > 0, "buscar() devolvio 0 resultados"
    assert all(0.0 <= x["similitud"] <= 1.0 for x in res), "similitud fuera de [0,1]"
    assert res == sorted(res, key=lambda x: -x["similitud"]), "resultados NO ordenados por similitud"
    marca("OK", f"buscar() monolitico -> {len(res)} chunks, mejor sim={res[0]['similitud']:.3f}, ordenado")

    # buscar() con filtro de silo
    for s in SILOS:
        rs = buscar(CONSULTAS[0], silo=s)
        assert all(x["silo"] == s for x in rs), f"el filtro de silo '{s}' NO filtro"
    marca("OK", f"buscar(silo=...) filtra correctamente en los {len(SILOS)} silos")

    # buscar_ruteado() = S1/S2
    rr = buscar_ruteado(CONSULTAS[0])
    assert len(rr) > 0, "buscar_ruteado() devolvio 0"
    marca("OK", f"buscar_ruteado() -> {len(rr)} chunks (camino S1/S2 completo)")

    # la sonda de evidencia
    from retriever import _evidencia_por_silo
    from embedder import embed_query
    ev = _evidencia_por_silo(embed_query(CONSULTAS[0]))
    assert set(ev) == set(SILOS), f"_evidencia_por_silo devolvio silos {set(ev)}"
    marca("OK", f"_evidencia_por_silo() aislada -> {len(ev)} silos")
except Exception:
    marca("FALLA", "camino de produccion ROTO:\n" + traceback.format_exc()[-700:])

# ---------------- 4. INTEGRIDAD DE LA BASE ----------------
print("\n--- 4. integridad de la base ---")
try:
    from db import conectar
    from config import SILOS
    con = conectar(); cur = con.cursor()

    cur.execute("SELECT count(*) FROM chunks")
    n = cur.fetchone()[0]
    marca("OK" if n > 0 else "FALLA", f"{n} chunks en la tabla")

    cur.execute("SELECT count(*) FROM chunks WHERE embedding IS NULL")
    k = cur.fetchone()[0]
    marca("FALLA" if k else "OK", f"chunks sin embedding: {k}")

    cur.execute("SELECT DISTINCT vector_dims(embedding) FROM chunks")
    dims = sorted(r[0] for r in cur.fetchall())
    marca("FALLA" if len(dims) != 1 else "OK", f"dimension del embedding: {dims} (debe ser [1024])")

    cur.execute("SELECT DISTINCT silo FROM chunks")
    silos_db = {r[0] for r in cur.fetchall()}
    desconocidos = silos_db - set(SILOS)
    marca("FALLA" if desconocidos else "OK",
          f"silos en la base: {sorted(silos_db)}")

    cur.execute("SELECT count(*) FROM chunks WHERE silo_scores IS NULL")
    k = cur.fetchone()[0]
    marca("AVISO" if k else "OK", f"chunks sin silo_scores: {k}")

    # el silo guardado debe ser el argmax de silo_scores (si no, estan desincronizados)
    cur.execute("SELECT silo, silo_scores FROM chunks WHERE silo_scores IS NOT NULL")
    desync = 0
    for s, sc in cur.fetchall():
        d = sc if isinstance(sc, dict) else json.loads(sc)
        if d and max(d, key=d.get) != s:
            desync += 1
    marca("FALLA" if desync else "OK", f"chunks donde silo != argmax(silo_scores): {desync}")

    cur.execute("SELECT count(*), count(DISTINCT chunk_uid) FROM chunks")
    tot, uni = cur.fetchone()
    marca("FALLA" if tot != uni else "OK", f"chunk_uid unicos: {uni}/{tot}")

    cur.execute("SELECT count(*) FROM chunks WHERE contenido IS NULL OR length(trim(contenido))=0")
    k = cur.fetchone()[0]
    marca("FALLA" if k else "OK", f"chunks con contenido vacio: {k}")

    cur.execute("SELECT indexname FROM pg_indexes WHERE tablename='chunks'")
    idxs = [r[0] for r in cur.fetchall()]
    hnsw = [i for i in idxs if "hnsw" in i.lower()]
    marca("OK" if len(hnsw) >= 4 else "AVISO",
          f"indices HNSW por silo: {len(hnsw)} encontrados")

    # ---------------- 5. schema real vs INSERT de pipeline ----------------
    print("\n--- 5. schema real vs codigo ---")
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='chunks'")
    cols_reales = {r[0] for r in cur.fetchall()}
    sql_schema = (ING / "schema.sql").read_text(encoding="utf-8", errors="replace")
    cols_schema = set(re.findall(r"^\s{4}(\w+)\s+", sql_schema, re.M))
    falta_en_db = cols_schema - cols_reales
    marca("FALLA" if falta_en_db else "OK",
          f"columnas de schema.sql ausentes en la base real: {sorted(falta_en_db) or 'ninguna'}")

    pipe = (ING / "pipeline.py").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"INSERT INTO chunks \(([^)]+)\)", pipe)
    if m:
        cols_insert = {c.strip() for c in m.group(1).split(",")}
        falta = cols_insert - cols_reales
        marca("FALLA" if falta else "OK",
              f"columnas del INSERT de pipeline.py ausentes en la base: {sorted(falta) or 'ninguna'}")
        # placeholders del template vs cantidad de columnas
        t = re.search(r'template="\(([^"]+)\)"', pipe)
        if t:
            nph = t.group(1).count("%s")
            marca("FALLA" if nph != len(cols_insert) else "OK",
                  f"INSERT: {len(cols_insert)} columnas vs {nph} placeholders del template")
    con.close()
except Exception:
    marca("FALLA", "auditoria de base ROTA:\n" + traceback.format_exc()[-700:])

# ---------------- 6. constantes de config referenciadas ----------------
print("\n--- 6. constantes de config referenciadas por el codigo ---")
try:
    import config
    usadas = set()
    for arch in ING.glob("*.py"):
        if arch.name == "config.py":
            continue
        for m in re.finditer(r"from config import ([^\n#]+)", arch.read_text(encoding="utf-8", errors="replace")):
            for nombre in m.group(1).split(","):
                usadas.add((nombre.strip(), arch.name))
    faltantes = [(nm, a) for nm, a in usadas if nm and not hasattr(config, nm)]
    for nm, a in faltantes:
        marca("FALLA", f"{a} importa config.{nm} que NO EXISTE")
    if not faltantes:
        marca("OK", f"{len({n for n,_ in usadas})} constantes importadas, todas existen")
    # muertas
    definidas = {k for k in vars(config) if k.isupper()}
    muertas = definidas - {n for n, _ in usadas}
    if muertas:
        marca("AVISO", f"constantes de config que nadie usa: {sorted(muertas)}")
except Exception:
    marca("FALLA", "chequeo de config ROTO:\n" + traceback.format_exc()[-500:])

# ---------------- RESUMEN ----------------
print("\n" + "=" * 78)
print(f"  RESULTADO:  {len(fallos)} FALLAS  ·  {len(avisos)} avisos  ·  {len(oks)} chequeos OK")
print("=" * 78)
if fallos:
    print("\n  FALLAS que hay que arreglar:")
    for f in fallos:
        print(f"   - {f.splitlines()[0]}")
else:
    print("\n  Ninguna falla. El camino de produccion corre de punta a punta.")
if avisos:
    print("\n  Avisos (no rompen, pero conviene saberlo):")
    for a in avisos:
        print(f"   - {a}")
