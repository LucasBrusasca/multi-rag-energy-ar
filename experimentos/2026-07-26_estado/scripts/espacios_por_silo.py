"""EL EXPERIMENTO QUE FALTABA (version sin etiquetas ni API): ESPACIOS DISTINTOS POR SILO.

C.70: el plan pide "un modelo de embeddings ajustado a la terminologia de cada area, lo que
permite busquedas en espacios semanticos DIFERENCIADOS". Se construyo con UN embedder
compartido -> un solo espacio -> el filtro no agrega informacion -> los 35 empates.

El fine-tuning por dominio esta bloqueado (no hay datos etiquetados). Pero hay una version
NO SUPERVISADA de "espacio especializado": darle a cada silo su propia TRANSFORMACION
aprendida solo con SUS chunks (centrado + blanqueo/PCA por silo). Cada silo queda con su
propia metrica, adaptada a la estructura de varianza de su dominio. Sin etiquetas, sin API.

PROBLEMA NUEVO (el que resucita resource selection, C.29): con espacios distintos, un
coseno 0.7 en legal y 0.7 en contable NO son comparables. Se resuelve con fusion por RANGO
(RRF), que es libre de escala.

Se compara, con el MISMO arnés (160 consultas silver, seed 7):
  B0        : espacio compartido, busqueda global            (el monolitico)
  S1-comp   : espacio compartido, filtrado por silo          (lo medido en C.30-C.69)
  S1-esp    : ESPACIO PROPIO POR SILO + fusion por rango     (lo que el plan pide, aprox.)
  oraculo   : idem pero con el silo correcto dado            (techo)
⚠️ Protocolo silver (fuga) -> comparar entre brazos, no absolutos.
"""
import sys, io, json, random
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar

SILOS = ["legal", "impositivo", "contable", "financiero"]
K = 3
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
cur.execute("SELECT silo, titulo, fuente, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
silo = np.array([r[0] for r in filas]); tit = np.array([r[1] for r in filas])
fue = np.array([r[2] for r in filas])
X = np.array([json.loads(r[3]) for r in filas]); X = X / np.linalg.norm(X, axis=1, keepdims=True)
n, d = X.shape

random.seed(7)
por_dom = {}
for i, f in enumerate(fue):
    if f in DOM and 15 <= len(tit[i]) <= 70:
        por_dom.setdefault(DOM[f], []).append(i)
consultas = []
for dd, l in por_dom.items():
    consultas += random.sample(l, min(40, len(l)))
objetivos = {}
for i in consultas:
    o = set(np.where((fue == fue[i]) & (tit == tit[i]))[0].tolist()) - {i}
    if o:
        objetivos[i] = o
print(f"corpus {n} chunks · {len(objetivos)} consultas evaluables · recall@{K}")
print()

# ---------- espacio propio por silo: centrado + blanqueo con shrinkage, SOLO con sus chunks ----------
def espacio_silo(idx_silo, lam=0.3, dim=128):
    Xs = X[idx_silo]
    mu = Xs.mean(axis=0)
    C = Xs - mu
    # PCA local del silo (sus direcciones de mayor varianza) + blanqueo
    U, S, Vt = np.linalg.svd(C, full_matrices=False)
    dim = min(dim, len(S))
    W = Vt[:dim].T                                   # proyeccion a las direcciones del silo
    var = (S[:dim] ** 2) / len(Xs)
    # blanqueo con shrinkage: no dividir por varianzas casi nulas
    esc = 1.0 / np.sqrt((1 - lam) * var + lam * var.mean() + 1e-9)
    return mu, W, esc

espacios = {}
for s in SILOS:
    idx = np.where(silo == s)[0]
    espacios[s] = (idx, *espacio_silo(idx))

def proyectar(v, s):
    mu, W, esc = espacios[s][1], espacios[s][2], espacios[s][3]
    z = (v - mu) @ W * esc
    return z / (np.linalg.norm(z, axis=-1, keepdims=True) + 1e-12)

# pre-proyectar los chunks de cada silo a SU espacio
Zsilo = {}
for s in SILOS:
    idx = espacios[s][0]
    Zsilo[s] = (idx, proyectar(X[idx], s))

def top_en_silo(q, s, k):
    idx, Z = Zsilo[s]
    zq = proyectar(q.reshape(1, -1), s)[0]
    sims = Z @ zq
    kk = min(k, len(sims) - 1)
    top = np.argpartition(-sims, kk)[:kk + 1]
    top = top[np.argsort(-sims[top])]
    return [(idx[j], float(sims[j])) for j in top]

def rrf(listas, k=60):
    """fusion por RANGO: libre de escala, resuelve la incomparabilidad entre espacios"""
    score = {}
    for l in listas:
        for r, (j, _) in enumerate(l, 1):
            score[j] = score.get(j, 0) + 1 / (k + r)
    return [j for j in sorted(score, key=score.get, reverse=True)]

hits = {"B0 (espacio compartido, global)": 0, "S1 compartido (filtro por silo)": 0,
        "S1-ESP espacios propios + RRF": 0, "S1-ESP silo correcto (techo)": 0}
cont = {k_: [] for k_ in hits}

for i, obj in objetivos.items():
    q = X[i]
    sims = X @ q; sims[i] = -2
    # B0
    top = np.argpartition(-sims, K)[:K]
    hits["B0 (espacio compartido, global)"] += bool(obj & set(top.tolist()))
    cont["B0 (espacio compartido, global)"].append(np.mean([DOM.get(fue[j]) != DOM.get(fue[i]) for j in top]))
    # S1 compartido: filtro al silo del objetivo (techo del compartido = oraculo de C.36)
    silos_ok = list({silo[j] for j in obj})
    sf = np.where(np.isin(silo, silos_ok), sims, -2)
    tops = np.argpartition(-sf, K)[:K]
    hits["S1 compartido (filtro por silo)"] += bool(obj & set(tops.tolist()))
    cont["S1 compartido (filtro por silo)"].append(np.mean([DOM.get(fue[j]) != DOM.get(fue[i]) for j in tops]))
    # S1-ESP: buscar en CADA espacio propio y fusionar por rango
    listas = [ [(j, sc) for j, sc in top_en_silo(q, s, K) if j != i] for s in SILOS ]
    fus = rrf(listas)[:K]
    hits["S1-ESP espacios propios + RRF"] += bool(obj & set(fus))
    cont["S1-ESP espacios propios + RRF"].append(np.mean([DOM.get(fue[j]) != DOM.get(fue[i]) for j in fus]))
    # S1-ESP con el silo correcto dado (techo)
    listas_ok = [ [(j, sc) for j, sc in top_en_silo(q, s, K) if j != i] for s in silos_ok ]
    fus2 = rrf(listas_ok)[:K]
    hits["S1-ESP silo correcto (techo)"] += bool(obj & set(fus2))
    cont["S1-ESP silo correcto (techo)"].append(np.mean([DOM.get(fue[j]) != DOM.get(fue[i]) for j in fus2]))

m = len(objetivos)
print(f"  {'sistema':38s} {'recall@3':>9s} {'sucio':>8s}")
for k_ in hits:
    print(f"  {k_:38s} {hits[k_]/m:8.1%} {np.mean(cont[k_]):7.1%}")
print()
b0 = hits["B0 (espacio compartido, global)"] / m
for k_ in list(hits)[1:]:
    print(f"  {k_:38s} vs B0: {(hits[k_]/m - b0)*100:+5.1f} pp")

# ---------- ¿los espacios propios separan MEJOR los dominios? ----------
print()
print("  PUREZA DE VECINDARIO (k=5) — ¿el espacio propio de cada silo es mas 'suyo'?")
random.seed(3)
for s in SILOS:
    idx, Z = Zsilo[s]
    # pureza medida en el espacio COMPARTIDO para los chunks de este silo
    mu_p = []
    for j in random.sample(range(len(idx)), min(150, len(idx))):
        sims = X @ X[idx[j]]; sims[idx[j]] = -2
        vec = np.argpartition(-sims, 5)[:5]
        mu_p.append((silo[vec] == s).mean())
    print(f"     {s:12s} compartido: {np.mean(mu_p):.1%}   (dim propia usada: {Z.shape[1]})")
