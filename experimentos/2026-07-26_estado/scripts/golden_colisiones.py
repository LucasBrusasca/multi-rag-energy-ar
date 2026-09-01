"""GOLDEN — PASO 1: encontrar los TERMINOS DE COLISION reales del corpus.

⚠️ CORRECCION DE LA v1 (fallida): rankear por ENTROPIA premia las palabras GENERICAS
("excepto", "respectivamente", "fueron"): una palabra que aparece parejo en los 4 silos
tiene entropia maxima y NO es una colision, es vocabulario comun. Ademas la v1 conto
ocurrencias CRUDAS sin normalizar por el tamaño de cada silo, que son muy distintos.

CRITERIO CORREGIDO — un termino de colision se usa MUCHO en exactamente DOS silos y
CASI NADA en los otros dos. Eso es bimodalidad, no uniformidad:

  r[s] = (chunks del silo s que contienen el termino) / (total de chunks del silo s)
         ^ PREVALENCIA dentro del silo: corrige que los silos tengan tamaños distintos

  ordenados r1 >= r2 >= r3 >= r4:
    BALANCE      = r2 / r1        -> cerca de 1: los dos silos lo usan parecido
    EXCLUSIVIDAD = r2 / r3        -> alto: los otros dos silos NO lo usan
    score        = EXCLUSIVIDAD, filtrando por BALANCE >= BALANCE_MIN

  Una palabra generica ("excepto") tiene EXCLUSIVIDAD ~1 -> se cae sola.
  No hace falta lista de stopwords: el criterio las elimina por construccion.

Se privilegian n-gramas de 2-3 palabras: son menos ambiguos para redactar la pregunta
("valor residual" es interpretable; "valor" no).

SALIDA: candidatos con prevalencia por silo + ejemplos de chunk de CADA silo del par,
para que Lucas verifique LEYENDO que el sentido cambia entre silos (P3 del protocolo).
"""
import sys, io, json, re
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
from db import conectar

# --------- parametros del criterio (declarados, ninguno clavado adentro) ---------
N_MAX = 3             # n-gramas de 1 a 3 palabras
MIN_CHUNKS_SILO = 4   # al menos tantos chunks EN CADA UNO de los dos silos del par
MAX_DF = 0.10         # si aparece en >10% del corpus es vocabulario comun
BALANCE_MIN = 0.45    # r2/r1: los dos silos lo tienen que usar parecido
EXCL_MIN = 3.0        # r2/r3: los otros dos silos lo usan al menos 3x menos
MIN_LARGO = 5         # largo minimo de palabra
TOP = 30
# --------- filtros que distinguen COLISION REAL de DOCUMENTO A CABALLO ---------
# Hallazgo de la v2: los terminos que mas puntuaban eran boilerplate del MISMO documento
# repartido entre dos silos ("period ended march", nombres de sindicos). Eso NO es
# polisemia inter-dominio: es un documento que el clasificador partio en dos.
# Un termino de dominio GENUINO lo usan VARIOS documentos distintos en cada silo.
MIN_DOCS_SILO = 2     # >= tantos documentos DISTINTOS aportando el termino en cada silo
MAX_JACCARD_DOCS = 0.34  # los documentos de un silo y del otro tienen que ser distintos

con = conectar(); cur = con.cursor()
cur.execute("SELECT silo, titulo, contenido, fuente FROM chunks")
filas = cur.fetchall(); con.close()
SILOS = sorted({r[0] for r in filas})
n = len(filas)
N_SILO = Counter(r[0] for r in filas)
print(f"corpus {n} chunks · tamaño por silo: " + " · ".join(f"{s}={N_SILO[s]}" for s in SILOS))
print(f"criterio: df<{MAX_DF:.0%} · >={MIN_CHUNKS_SILO} chunks en cada silo del par · "
      f"balance>={BALANCE_MIN} · exclusividad>={EXCL_MIN}x")
print()

PAL = re.compile(r"[a-záéíóúñü]{%d,}" % MIN_LARGO)
df = Counter()
por_silo = defaultdict(Counter)
docs_silo = defaultdict(lambda: defaultdict(set))   # termino -> silo -> {documentos}
ejemplos = defaultdict(lambda: defaultdict(list))

en_titulo = Counter()   # termino -> en cuantos TITULOS (encabezados) aparece
for silo, tit, cont, fue in filas:
    tpals = PAL.findall(tit.lower())
    tgrams = set()
    for k in range(1, N_MAX + 1):
        for i in range(len(tpals) - k + 1):
            t = tpals[i:i + k]
            if len(set(t)) == len(t):
                tgrams.add(" ".join(t))
    for g in tgrams:
        en_titulo[g] += 1

    pals = PAL.findall(f"{tit} {cont}".lower())
    grams = set()
    for k in range(1, N_MAX + 1):
        for i in range(len(pals) - k + 1):
            t = pals[i:i + k]
            if len(set(t)) < len(t):        # token repetido -> artefacto de OCR
                continue                     # ("incumpli miento incumpli")
            grams.add(" ".join(t))
    for g in grams:
        df[g] += 1
        por_silo[g][silo] += 1
        docs_silo[g][silo].add(fue)
        if len(ejemplos[g][silo]) < 2:
            ejemplos[g][silo].append({"titulo": tit[:70], "fuente": fue,
                                      "frag": cont[:180].replace("\n", " ")})

cands = []
for g, d in df.items():
    if d > MAX_DF * n:
        continue
    dist = por_silo[g]
    if len(dist) < 2:
        continue
    # PREVALENCIA dentro de cada silo (corrige tamaños distintos)
    r = {s: dist.get(s, 0) / N_SILO[s] for s in SILOS}
    orden = sorted(SILOS, key=lambda s: -r[s])
    s1, s2 = orden[0], orden[1]
    r1, r2 = r[s1], r[s2]
    r3 = r[orden[2]]
    if dist.get(s1, 0) < MIN_CHUNKS_SILO or dist.get(s2, 0) < MIN_CHUNKS_SILO:
        continue
    if r1 == 0:
        continue
    balance = r2 / r1
    excl = r2 / r3 if r3 > 0 else float("inf")
    if balance < BALANCE_MIN or excl < EXCL_MIN:
        continue
    # --- filtro COLISION REAL vs DOCUMENTO A CABALLO ---
    d1, d2 = docs_silo[g][s1], docs_silo[g][s2]
    if len(d1) < MIN_DOCS_SILO or len(d2) < MIN_DOCS_SILO:
        continue                                  # boilerplate de un solo documento
    jac = len(d1 & d2) / len(d1 | d2)
    if jac > MAX_JACCARD_DOCS:
        continue                                  # los mismos documentos en los dos silos
    cands.append({
        "termino": g, "df": d, "par": sorted([s1, s2]),
        "balance": round(balance, 3),
        "exclusividad": round(min(excl, 999.0), 2),
        "prevalencia": {s: round(r[s] * 100, 2) for s in SILOS},
        "chunks": {s: dist.get(s, 0) for s in SILOS},
        "docs": {s1: sorted(d1), s2: sorted(d2)},
        "jaccard_docs": round(jac, 3),
        "n_palabras": g.count(" ") + 1,
        "en_titulo": en_titulo[g],
    })

cands.sort(key=lambda c: (-c["en_titulo"], -c["n_palabras"], -c["df"]))
print(f"candidatos que pasan el criterio: {len(cands)}")
multi = [c for c in cands if c["n_palabras"] >= 2]
print(f"   de los cuales de 2-3 palabras (los mas utiles): {len(multi)}")
print()

def mostrar(lst, titulo):
    print("=" * 100)
    print(f"  {titulo}")
    print("=" * 100)
    print(f"  {'titul':>5s} {'bal':>5s} " + "".join(f"{s[:6]:>8s}" for s in SILOS) + "   termino")
    print(f"  {'':5s} {'':5s} " + "".join(f"{'%':>8s}" for s in SILOS))
    for c in lst:
        pv = "".join(f"{c['prevalencia'][s]:8.2f}" for s in SILOS)
        print(f"  {c['en_titulo']:5d} {c['balance']:5.2f} {pv}   {c['termino']}")

mostrar([c for c in multi if c["en_titulo"] > 0][:TOP], f"CONCEPTOS DE COLISION (2-3 palabras que ENCABEZAN secciones -> son conceptos, no muletillas)")
print()
mono = [c for c in cands if c["n_palabras"] == 1]
mostrar([c for c in mono if c["en_titulo"] >= 2][:20], "CONCEPTOS DE UNA PALABRA que encabezan secciones (>=2 titulos)")

print()
print("=" * 100)
print("  AGRUPADO POR PAR DE SILOS  ·  de aca se arma el estrato de colision")
print("=" * 100)
pares = defaultdict(list)
for c in cands:
    pares[tuple(c["par"])].append(c)
for par, lst in sorted(pares.items(), key=lambda x: -len(x[1])):
    m = [c for c in lst if c["en_titulo"] > 0]
    print(f"\n  {par[0]} ⚔ {par[1]}   ({len(lst)} terminos · {len(m)} multipalabra)")
    for c in m[:10]:
        print(f"     titulos={c['en_titulo']:2d} df={c['df']:3d}  {c['termino']}")

for c in cands:
    c["ejemplos"] = {s: ejemplos[c["termino"]][s] for s in c["par"]}
salida = SCR / "golden_colisiones.json"
salida.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n  {len(cands)} candidatos guardados en {salida.name} (con fragmentos de los 2 silos)")
