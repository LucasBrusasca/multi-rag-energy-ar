"""LA GEOMETRIA DE LOS SILOS — ¿son regiones separadas o se superponen?

Pregunta de Lucas: los silos, ¿estan realmente ubicados en zonas distintas del espacio
vectorial? Si se superponen, filtrar por silo no saca nada util de encima -> eso
EXPLICARIA la ley empirica (recall depende de cuantos silos, no de cuales).

Se mide:
  1. SILHOUETTE de la particion por silo (que tan bien separados estan)
  2. PUREZA DE VECINDARIO: de los k vecinos mas cercanos de un chunk, ¿que fraccion es
     de su mismo silo? (si es ~25% = azar => los silos NO son regiones)
  3. distancia intra-silo vs inter-silo
  4. lo mismo por PAR de silos (donde esta la superposicion)
"""
import sys, io, json, random
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar

SILOS = ["legal", "impositivo", "contable", "financiero"]
con = conectar(); cur = con.cursor()
cur.execute("SELECT chunk_uid, silo, embedding::text FROM chunks")
filas = cur.fetchall()
con.close()

uids = [r[0] for r in filas]
silo = np.array([r[1] for r in filas])
X = np.array([json.loads(r[2]) for r in filas])
X = X / np.linalg.norm(X, axis=1, keepdims=True)   # L2-norm -> coseno = producto punto
n = len(X)
print(f"GEOMETRIA DE LOS SILOS · {n} chunks · {X.shape[1]} dimensiones")
print(f"  reparto: {dict(Counter(silo))}")
print()

# --- 2. PUREZA DE VECINDARIO (la prueba mas directa) ---
print("1) PUREZA DE VECINDARIO — de los k vecinos mas cercanos, ¿cuantos son del mismo silo?")
print("   (si fuera ~el % del silo en el corpus = AZAR => los silos NO son regiones separadas)")
print()
random.seed(3)
muestra = random.sample(range(n), 600)
base = {s: (silo == s).mean() for s in SILOS}   # proporcion en el corpus = linea de azar
for k in (5, 10, 25):
    pureza = {s: [] for s in SILOS}
    for i in muestra:
        sims = X @ X[i]
        sims[i] = -2
        vecinos = np.argpartition(-sims, k)[:k]
        mismo = (silo[vecinos] == silo[i]).mean()
        pureza[silo[i]].append(mismo)
    glob = np.mean([v for l in pureza.values() for v in l])
    print(f"   k={k:2d}  GLOBAL: {glob:.1%}   " +
          "  ".join(f"{s[:4]}={np.mean(pureza[s]):.0%}(azar {base[s]:.0%})" for s in SILOS))
print()

# --- 1. SILHOUETTE ---
print("2) SILHOUETTE de la particion por silo (1=perfectamente separados, 0=indistinguibles, <0=mal)")
sub = random.sample(range(n), 900)
Xs, ys = X[sub], silo[sub]
D = 1 - Xs @ Xs.T
sil = []
for i in range(len(sub)):
    mismo = ys == ys[i]
    mismo[i] = False
    if mismo.sum() == 0:
        continue
    a = D[i][mismo].mean()
    b = min(D[i][ys == o].mean() for o in SILOS if o != ys[i])
    sil.append((b - a) / max(a, b))
print(f"   silhouette medio = {np.mean(sil):.3f}")
print()

# --- 3-4. distancias intra vs inter, por par ---
print("3) SIMILITUD MEDIA intra-silo vs inter-silo (coseno)")
cent = {s: X[silo == s].mean(axis=0) for s in SILOS}
cent = {s: v / np.linalg.norm(v) for s, v in cent.items()}
print()
print(f"   {'':12s} " + " ".join(f"{o[:10]:>10s}" for o in SILOS))
for s in SILOS:
    fila = []
    for o in SILOS:
        m = float(X[silo == s] @ cent[o]).__class__ and float(np.mean(X[silo == s] @ cent[o]))
        fila.append(f"{m:10.3f}")
    print(f"   {s:12s} " + " ".join(fila))
print()
print("   (diagonal = similitud al propio centroide · fuera = a los otros)")
print()
intra = np.mean([np.mean(X[silo == s] @ cent[s]) for s in SILOS])
inter = np.mean([np.mean(X[silo == s] @ cent[o]) for s in SILOS for o in SILOS if o != s])
print(f"   intra-silo medio = {intra:.3f}   ·   inter-silo medio = {inter:.3f}   ·   brecha = {intra-inter:.3f}")
print()

# --- ¿el vecino mas cercano de cada chunk es de su silo? ---
print("4) ¿El vecino MAS CERCANO de cada chunk es de su mismo silo?")
ok = 0
for i in muestra:
    sims = X @ X[i]; sims[i] = -2
    ok += silo[int(np.argmax(sims))] == silo[i]
print(f"   {ok}/{len(muestra)} = {ok/len(muestra):.1%}")
