"""¿HACE FALTA PAGAR A14? — se prueba el MECANISMO gratis antes de gastar USD 114.

HIPOTESIS DE A14: el router falla porque los chunks no dicen de que documento son
("...de acuerdo con las disposiciones de esta ley..." — ¿cual ley?). Si el texto que se
embebe llevara la identidad del documento, los centroides por silo se volverian mas
distintivos y el router acertaria mas.

HALLAZGO: esa identidad YA ESTA EN LA BASE y NO se esta usando para embeber.
  · `fuente`    = 'Ley_11683_Procedimiento_Fiscal_TO'   (identidad de la norma)
  · `hierarchy` = ['Defraudación -Sanciones']            (seccion; poblado en 100%)
Hoy `embedder.py` embebe solo `titulo + contenido`. Tirar fuente+jerarquia adentro
cuesta CERO y prueba el mecanismo.

Lo que esto NO reemplaza: el LLM de A14 ademas RESUELVE referencias internas
("el inciso anterior", "dicho organismo", "el mismo plazo"). Eso solo lo puede hacer
leyendo el documento. Si este experimento sube la pureza, pagar A14 esta justificado;
si no la mueve, la hipotesis del mecanismo era falsa y hay que decirlo.

METRICA: PUREZA DE VECINDARIO (k=5) — de los 5 vecinos mas cercanos de un chunk,
cuantos son de su mismo silo. Es la metrica correcta en alta dimension (el silhouette
enga\u00f1a: dio 0.123 cuando la pureza era 89.2%). Linea base a batir: 89.2% (C.57).

NO ESCRIBE NADA EN LA BASE. Solo lee, re-embebe en memoria y mide.
"""
import sys, io, json, random, re
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar

K_VECINOS = 5
MUESTRA_POR_SILO = 200          # puntos de consulta por silo para medir pureza
SEED = 7

con = conectar(); cur = con.cursor()
cur.execute("SELECT silo, titulo, contenido, fuente, hierarchy, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
silo = np.array([r[0] for r in filas])
SILOS = sorted(set(silo.tolist()))
n = len(filas)
print(f"corpus {n} chunks · silos {SILOS}", flush=True)

# ---------- vectores ACTUALES (los que ya estan en la base) ----------
X_actual = np.array([json.loads(r[5]) for r in filas])
X_actual = X_actual / np.linalg.norm(X_actual, axis=1, keepdims=True)


def legible(fuente: str) -> str:
    """'Ley_11683_Procedimiento_Fiscal_TO' -> 'Ley 11.683 Procedimiento Fiscal TO'.
    Convierte el nombre de archivo en texto que el embedder pueda aprovechar:
    separadores a espacios y numeros de norma con punto de miles."""
    t = re.sub(r"[_\-]+", " ", fuente).strip()
    # 11683 -> 11.683 · 24065 -> 24.065  (numeros de ley de 5 digitos)
    t = re.sub(r"\b(\d{2})(\d{3})\b", r"\1.\2", t)
    return t


# ---------- variantes de texto a embeber ----------
def texto_actual(r):
    return f"{r[1]}\n{r[2]}"                                    # titulo + contenido (HOY)

def texto_con_fuente(r):
    return f"{legible(r[3])}\n{r[1]}\n{r[2]}"                   # + identidad del documento

def texto_con_jerarquia(r):
    ruta = " > ".join(r[4] or [])
    return f"{ruta}\n{r[1]}\n{r[2]}"                            # + ruta de seccion

def texto_completo(r):
    ruta = " > ".join(r[4] or [])
    cab = " > ".join(x for x in (legible(r[3]), ruta) if x)
    return f"{cab}\n{r[1]}\n{r[2]}"                             # A14 GRATIS: fuente + jerarquia

# Se corre SOLO la variante que decide: si el paquete completo no mueve la pureza,
# descomponerlo en "+fuente" y "+jerarquia" por separado no aporta nada. Si SI la mueve,
# ahi vale descomponer para saber cual de las dos hace el trabajo.
# (re-embeber 2709 chunks en CPU tarda ~90 min por pasada: una, no tres)
VARIANTES = [
    ("HOY (titulo + contenido)", texto_actual),
    ("A14-GRATIS (fuente > jerarquia)", texto_completo),
]

from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
print(f"cargando {EMBEDDING_MODEL}...", flush=True)
modelo = SentenceTransformer(EMBEDDING_MODEL)

random.seed(SEED)
consultas = []
for s in SILOS:
    idx = [i for i in range(n) if silo[i] == s]
    consultas += random.sample(idx, min(MUESTRA_POR_SILO, len(idx)))
print(f"puntos de medicion: {len(consultas)} ({MUESTRA_POR_SILO} por silo, seed={SEED})\n", flush=True)


def pureza(X):
    """De los K vecinos mas cercanos de cada punto, que fraccion es del mismo silo."""
    por_silo = {s: [] for s in SILOS}
    for i in consultas:
        sims = X @ X[i]
        sims[i] = -2
        vec = np.argpartition(-sims, K_VECINOS)[:K_VECINOS]
        por_silo[silo[i]].append(float((silo[vec] == silo[i]).mean()))
    glob = float(np.mean([v for l in por_silo.values() for v in l]))
    return glob, {s: float(np.mean(l)) for s, l in por_silo.items()}


resultados = []
for nombre, fn in VARIANTES:
    if nombre.startswith("HOY"):
        X = X_actual                       # se reusa lo que ya esta en la base
        print(f"[{nombre}] usando los vectores existentes", flush=True)
    else:
        textos = [fn(r) for r in filas]
        print(f"[{nombre}] re-embebiendo {n} textos por lotes...", flush=True)
        import time
        t0 = time.time(); partes = []
        LOTE = 256
        for ini in range(0, n, LOTE):
            partes.append(modelo.encode(textos[ini:ini + LOTE], batch_size=16,
                                        show_progress_bar=False, normalize_embeddings=True))
            hechos = min(ini + LOTE, n)
            transcurrido = time.time() - t0
            resta = transcurrido / hechos * (n - hechos)
            print(f"   {hechos}/{n}  ({transcurrido/60:.1f} min · faltan ~{resta/60:.1f} min)", flush=True)
        X = np.vstack(partes)
    g, pr = pureza(X)
    resultados.append((nombre, g, pr))
    print(f"   pureza global: {g:.1%}", flush=True)

print()
print("=" * 84)
print(f"  PUREZA DE VECINDARIO (k={K_VECINOS})  ·  linea base de C.57 = 89.2%")
print("=" * 84)
print(f"  {'variante':34s} {'global':>8s} " + "".join(f"{s[:9]:>10s}" for s in SILOS))
base = resultados[0][1]
for nombre, g, pr in resultados:
    delta = "" if nombre.startswith("HOY") else f"  ({(g-base)*100:+.1f} pp)"
    print(f"  {nombre:34s} {g:7.1%} " + "".join(f"{pr[s]:9.1%} " for s in SILOS) + delta)

print()
mejor = max(resultados[1:], key=lambda x: x[1])
if mejor[1] > base + 0.005:
    print(f"  ⇒ EL MECANISMO ES REAL: '{mejor[0]}' sube la pureza {(mejor[1]-base)*100:+.1f} pp GRATIS.")
    print(f"    Justifica (a) hacer este cambio ya, sin costo, y (b) pagar A14 completo,")
    print(f"    que ademas resuelve las referencias internas que esto NO toca.")
elif mejor[1] < base - 0.005:
    print(f"  ⇒ EMPEORA. Meter fuente/jerarquia en el vector agrega ruido, no señal.")
    print(f"    La hipotesis del mecanismo queda REFUTADA por este lado.")
else:
    print(f"  ⇒ NO SE MUEVE (mejor: {(mejor[1]-base)*100:+.1f} pp). La identidad del documento")
    print(f"    NO es lo que le falta al vector. Antes de pagar USD 114 por A14 hay que")
    print(f"    revisar la hipotesis: quizas el problema del router no es la identidad")
    print(f"    del documento sino la resolucion de referencias internas (eso SI lo")
    print(f"    necesita el LLM) — o el router no se arregla por el lado del embedding.")

(SCR / "a14_gratis_pureza.json").write_text(
    json.dumps([{"variante": nm, "global": g, "por_silo": pr} for nm, g, pr in resultados],
               ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n  guardado en a14_gratis_pureza.json")
