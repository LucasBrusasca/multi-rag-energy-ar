"""LOS 1.5 PUNTOS FINALES — afinado de la proyeccion discriminante.

Estado: LDA g=0.90 -> 96.8% acierto con 1.49 silos · recall 76.6% · B0 77.7%
Punto de equilibrio calculado: 98.3% de acierto a ~1.5 silos.

Se barre: shrinkage (regularizacion), fusion con evidencia real, y gamma alto.
Evaluacion honesta: los chunks de las consultas de test quedan FUERA del ajuste.
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
silo = np.array([r[0] for r in filas]); titulos = np.array([r[1] for r in filas])
fuentes = np.array([r[2] for r in filas])
X = np.array([json.loads(r[3]) for r in filas]); X = X / np.linalg.norm(X, axis=1, keepdims=True)
n, d = X.shape
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
Xtr, ytr = X[train], silo[train]

def hacer_lda(lam):
    mu_g = Xtr.mean(axis=0)
    Sw = np.zeros((d, d)); Sb = np.zeros((d, d))
    for s in SILOS:
        Xs = Xtr[ytr == s]; mu = Xs.mean(axis=0); C = Xs - mu
        Sw += C.T @ C
        dif = (mu - mu_g).reshape(-1, 1); Sb += len(Xs) * (dif @ dif.T)
    Sw /= len(Xtr)
    Sw_r = (1 - lam) * Sw + lam * np.trace(Sw) / d * np.eye(d)
    ev, evec = np.linalg.eigh(np.linalg.solve(Sw_r, Sb))
    W = evec[:, np.argsort(-ev)[:3]].real
    Z = Xtr @ W; Z = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-12)
    cent = {s: Z[ytr == s].mean(axis=0) for s in SILOS}
    cent = {s: v / (np.linalg.norm(v) + 1e-12) for s, v in cent.items()}
    return W, cent

# B0 referencia
hb, cb, m = 0, [], 0
objetivos = {}
for i in consultas:
    o = set(np.where((fuentes == fuentes[i]) & (titulos == titulos[i]))[0].tolist()) - {i}
    if not o:
        continue
    objetivos[i] = o
    sims = X @ X[i]; sims[i] = -2
    top = np.argpartition(-sims, K)[:K]
    hb += bool(o & set(top.tolist()))
    cb.append(np.mean([DOM.get(fuentes[j]) != DOM.get(fuentes[i]) for j in top])); m += 1
B0 = hb / m
print(f"B0 monolitico: recall {B0:.1%} · sucio {np.mean(cb):.1%} · {m} consultas")
print()

def conjunto(sc, g):
    tot = sum(max(v, 0) for v in sc.values()) or 1.0
    p = {k: max(v, 0) / tot for k, v in sc.items()}
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= g:
            break
    return sel

def correr(W, cent, modo, g, temp=1.0):
    ok = hit = 0; exp = []; cont = []
    for i, o in objetivos.items():
        z = X[i] @ W; z = z / (np.linalg.norm(z) + 1e-12)
        base = {s: float(np.dot(z, cent[s])) for s in SILOS}
        if temp != 1.0:                      # afila la distribucion (softmax con temperatura)
            v = np.array([base[s] for s in SILOS]) / temp
            e = np.exp(v - v.max()); base = {s: float(x) for s, x in zip(SILOS, e / e.sum())}
        sims = X @ X[i]; sims[i] = -2
        if modo == "lda":
            sc = base
        elif modo == "lda_ev":
            sc = {s: max(base[s], 1e-6) * max(float(sims[silo == s].max()), 1e-6) for s in SILOS}
        sel = conjunto(sc, g)
        ok += bool({silo[j] for j in o} & set(sel))
        sf = np.where(np.isin(silo, sel), sims, -2)
        top = np.argpartition(-sf, K)[:K]
        hit += bool(o & set(top.tolist()))
        cont.append(np.mean([DOM.get(fuentes[j]) != DOM.get(fuentes[i]) for j in top]))
        exp.append(len(sel))
    return ok / len(objetivos), hit / len(objetivos), np.mean(cont), np.mean(exp)

print(f"  {'config':44s} {'acierto':>8s} {'recall':>8s} {'sucio':>7s} {'silos':>6s}")
mejores = []
for lam in (0.1, 0.3, 0.5, 0.8):
    W, cent = hacer_lda(lam)
    for modo in ("lda", "lda_ev"):
        for temp in (1.0, 0.1):
            for g in (0.90, 0.95, 0.98):
                a, r, c, e = correr(W, cent, modo, g, temp)
                nom = f"lam={lam} {modo} T={temp} g={g}"
                marca = "  <<< SUPERA B0" if r > B0 else ("  = B0" if r == B0 else "")
                if r >= B0 - 0.02:
                    print(f"  {nom:44s} {a:7.1%} {r:8.1%} {c:6.1%} {e:6.2f}{marca}")
                mejores.append((nom, a, r, c, e))
print()
gan = [x for x in mejores if x[2] > B0]
print(f"  >>> SUPERAN a B0: {len(gan)}")
for nom, a, r, c, e in sorted(gan, key=lambda x: -x[2])[:8]:
    print(f"       {nom:44s} recall {r:.1%} vs {B0:.1%} · acierto {a:.1%} · {e:.2f} silos · sucio {c:.1%}")
if not gan:
    top5 = sorted(mejores, key=lambda x: -x[2])[:5]
    print("  (ninguna supera; las 5 mejores:)")
    for nom, a, r, c, e in top5:
        print(f"       {nom:44s} recall {r:.1%} (B0 {B0:.1%}) · acierto {a:.1%} · {e:.2f} silos")
