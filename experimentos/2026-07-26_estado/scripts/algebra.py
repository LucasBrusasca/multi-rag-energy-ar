"""ATACAR LA TENAZA CON ALGEBRA: señal mas nitida => alto acierto con POCOS silos.

La tenaza medida: acierto de ruteo se compra abriendo silos, y abrir silos -> B0.
Existe porque la señal (coseno crudo en 1024d) es ruidosa. Si la señal separa mejor,
se puede tener alto acierto con 1-1.5 silos -> ahi SI se supera a B0 (0.98 x 87.5% = 85.8%).

TECNICAS (todas deterministas y auditables):
  A. LDA / proyeccion discriminante: aprender las direcciones que MAXIMIZAN la separacion
     entre silos y rutear en ese subespacio (reduccion de dimensionalidad SUPERVISADA).
  B. MAHALANOBIS: usar la covarianza de cada silo (su FORMA), no solo su centroide.
  C. BAYES: P(silo|q) con prior por tamaño de silo y verosimilitud gaussiana.
  D. combinaciones.

EVALUACION HONESTA: split train/test de chunks. Las proyecciones y covarianzas se estiman
SOLO con train; las consultas de test nunca participan del ajuste.
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
silo = np.array([r[0] for r in filas])
titulos = np.array([r[1] for r in filas])
fuentes = np.array([r[2] for r in filas])
X = np.array([json.loads(r[3]) for r in filas])
X = X / np.linalg.norm(X, axis=1, keepdims=True)
n, d = X.shape
print(f"corpus {n} chunks x {d}d · reparto {dict(Counter(silo))}")

# --- consultas de test: 160 titulos (los chunks-objetivo quedan FUERA del ajuste) ---
random.seed(7)
por_dom = {}
for i, f in enumerate(fuentes):
    if f in DOM and 15 <= len(titulos[i]) <= 70:
        por_dom.setdefault(DOM[f], []).append(i)
consultas = []
for dd, l in por_dom.items():
    consultas += random.sample(l, min(40, len(l)))
test_idx = set()
for i in consultas:
    test_idx |= set(np.where((fuentes == fuentes[i]) & (titulos == titulos[i]))[0].tolist())
train = np.array([i for i in range(n) if i not in test_idx])
print(f"ajuste con {len(train)} chunks (train) · {len(consultas)} consultas de test (sus chunks EXCLUIDOS del ajuste)")
print()

Xtr, ytr = X[train], silo[train]

# ---------- A. LDA / proyeccion discriminante (con shrinkage) ----------
mu_glob = Xtr.mean(axis=0)
Sw = np.zeros((d, d)); Sb = np.zeros((d, d))
medias = {}
for s in SILOS:
    Xs = Xtr[ytr == s]
    mu = Xs.mean(axis=0); medias[s] = mu
    C = Xs - mu
    Sw += C.T @ C
    dif = (mu - mu_glob).reshape(-1, 1)
    Sb += len(Xs) * (dif @ dif.T)
Sw /= len(Xtr)
lam = 0.5                                  # shrinkage (regularizacion, d >> n_clases)
Sw_r = (1 - lam) * Sw + lam * np.trace(Sw) / d * np.eye(d)
evals, evecs = np.linalg.eigh(np.linalg.solve(Sw_r, Sb))
W = evecs[:, np.argsort(-evals)[:3]].real          # 3 direcciones discriminantes (4 clases - 1)
print(f"A. LDA: proyeccion {d}d -> 3d  (autovalores top: {np.sort(evals)[::-1][:3].real.round(2)})")

def proyectar(V):
    Z = V @ W
    return Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-12)

Ztr = proyectar(Xtr)
cent_lda = {s: Ztr[ytr == s].mean(axis=0) for s in SILOS}
cent_lda = {s: v / (np.linalg.norm(v) + 1e-12) for s, v in cent_lda.items()}

# ---------- B. Mahalanobis por silo (covarianza regularizada en el subespacio LDA) ----------
inv_cov = {}
for s in SILOS:
    Zs = Ztr[ytr == s]
    C = np.cov(Zs.T) + 1e-3 * np.eye(3)
    inv_cov[s] = np.linalg.inv(C)
mu_lda = {s: Ztr[ytr == s].mean(axis=0) for s in SILOS}
prior = {s: (ytr == s).mean() for s in SILOS}
logdet = {s: np.linalg.slogdet(np.linalg.inv(inv_cov[s]))[1] for s in SILOS}

# ---------- señales ----------
cent_raw = {s: Xtr[ytr == s].mean(axis=0) for s in SILOS}
cent_raw = {s: v / np.linalg.norm(v) for s, v in cent_raw.items()}

def sig_actual(i):
    """coseno al centroide crudo x mejor evidencia del silo (la de produccion)"""
    sims = X @ X[i]
    sc = {}
    for s in SILOS:
        m = np.isin(silo, [s]) & ~np.isin(np.arange(n), list(test_idx & set(np.where(titulos == titulos[i])[0].tolist())))
        ev = sims[np.isin(silo, [s])].max()
        sc[s] = float(np.dot(X[i], cent_raw[s])) * float(ev)
    return sc

def sig_lda(i):
    z = proyectar(X[i].reshape(1, -1))[0]
    return {s: float(np.dot(z, cent_lda[s])) for s in SILOS}

def sig_maha(i):
    z = proyectar(X[i].reshape(1, -1))[0]
    sc = {}
    for s in SILOS:
        dlt = z - mu_lda[s]
        m2 = float(dlt @ inv_cov[s] @ dlt)
        sc[s] = -0.5 * m2 - 0.5 * logdet[s] + np.log(prior[s])   # log-verosimilitud gaussiana + prior (Bayes)
    mx = max(sc.values())
    return {s: float(np.exp(v - mx)) for s, v in sc.items()}     # -> pseudo-probabilidad

def sig_lda_ev(i):
    """LDA x mejor evidencia real del silo"""
    z = proyectar(X[i].reshape(1, -1))[0]
    sims = X @ X[i]; sims[i] = -2
    sc = {}
    for s in SILOS:
        ev = float(sims[silo == s].max())
        sc[s] = max(float(np.dot(z, cent_lda[s])), 1e-6) * max(ev, 1e-6)
    return sc

def sig_maha_ev(i):
    p = sig_maha(i)
    sims = X @ X[i]; sims[i] = -2
    return {s: p[s] * max(float(sims[silo == s].max()), 1e-6) for s in SILOS}

def conjunto(sc, g):
    tot = sum(max(v, 0) for v in sc.values()) or 1.0
    p = {k: max(v, 0) / tot for k, v in sc.items()}
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= g:
            break
    return sel

def evaluar(nombre, fn, gammas=(0.60, 0.70, 0.80, 0.90)):
    for g in gammas:
        ok, hit, exp, cont = 0, 0, [], []
        for i in consultas:
            objetivo = set(np.where((fuentes == fuentes[i]) & (titulos == titulos[i]))[0].tolist()) - {i}
            if not objetivo:
                continue
            sel = conjunto(fn(i), g)
            ok += bool({silo[j] for j in objetivo} & set(sel))
            sims = X @ X[i]; sims[i] = -2
            mask = np.isin(silo, sel)
            sf = np.where(mask, sims, -2)
            top = np.argpartition(-sf, K)[:K]
            hit += bool(objetivo & set(top.tolist()))
            cont.append(np.mean([DOM.get(fuentes[j]) != DOM.get(fuentes[i]) for j in top]))
            exp.append(len(sel))
        m = len(exp)
        print(f"  {nombre:28s} g={g:.2f}  acierto={ok/m:6.1%}  recall={hit/m:6.1%}  "
              f"sucio={np.mean(cont):5.1%}  silos={np.mean(exp):.2f}")

# B0 de referencia
hb, cb, m = 0, [], 0
for i in consultas:
    objetivo = set(np.where((fuentes == fuentes[i]) & (titulos == titulos[i]))[0].tolist()) - {i}
    if not objetivo:
        continue
    sims = X @ X[i]; sims[i] = -2
    top = np.argpartition(-sims, K)[:K]
    hb += bool(objetivo & set(top.tolist()))
    cb.append(np.mean([DOM.get(fuentes[j]) != DOM.get(fuentes[i]) for j in top])); m += 1
print(f"\n  {'B0 monolitico (referencia)':28s}          {'':16s} recall={hb/m:6.1%}  sucio={np.mean(cb):5.1%}  silos=4.00\n")
evaluar("A. LDA solo", sig_lda)
print()
evaluar("B. Mahalanobis+Bayes", sig_maha)
print()
evaluar("C. LDA x evidencia", sig_lda_ev)
print()
evaluar("D. Maha+Bayes x evidencia", sig_maha_ev)
