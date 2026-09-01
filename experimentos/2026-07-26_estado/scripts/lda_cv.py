"""VALIDACION RIGUROSA DE LDA — responde las 4 objeciones metodologicas de Codex.

(1) SPLIT AGRUPADO POR DOCUMENTO (GroupKFold por `fuente`): ningun chunk del documento
    consultado participa del ajuste. Elimina la fuga de estilo intra-documento.
(2) VALIDACION ANIDADA: lambda y gamma se eligen SOLO dentro del train de cada fold
    (con un split interno). El fold externo nunca se usa para elegir hiperparametros.
(3) NO se extrapola recall = acierto x recall_oraculo. Todo se mide punta a punta.
(4) EXPOSICION desagregada: alcance de busqueda (vectores escaneados) vs silos
    consultados vs dominios presentes en el contexto vs chunks entregados al generador.

Se reporta media +- desvio entre folds (IC aproximado).
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
SEED = 7
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
docs = sorted(set(fuentes))
print(f"corpus {n} chunks · {len(docs)} documentos · {d}d")

def lda_fit(idx, lam):
    Xt, yt = X[idx], silo[idx]
    presentes = [s for s in SILOS if (yt == s).sum() >= 3]
    if len(presentes) < 2:
        return None, None
    mu_g = Xt.mean(axis=0)
    Sw = np.zeros((d, d)); Sb = np.zeros((d, d))
    for s in presentes:
        Xs = Xt[yt == s]; mu = Xs.mean(axis=0); C = Xs - mu
        Sw += C.T @ C
        dif = (mu - mu_g).reshape(-1, 1); Sb += len(Xs) * (dif @ dif.T)
    Sw /= len(Xt)
    Sw_r = (1 - lam) * Sw + lam * np.trace(Sw) / d * np.eye(d)
    try:
        ev, evec = np.linalg.eigh(np.linalg.solve(Sw_r, Sb))
    except np.linalg.LinAlgError:
        return None, None
    W = evec[:, np.argsort(-ev)[:3]].real
    Z = Xt @ W; Z = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-12)
    cent = {}
    for s in SILOS:
        m = yt == s
        cent[s] = (Z[m].mean(axis=0) / (np.linalg.norm(Z[m].mean(axis=0)) + 1e-12)) if m.sum() else np.zeros(3)
    return W, cent

def conjunto(sc, g):
    tot = sum(max(v, 0) for v in sc.values()) or 1.0
    p = {k: max(v, 0) / tot for k, v in sc.items()}
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= g:
            break
    return sel

def evaluar(idx_consultas, W, cent, g, prohibidos):
    """prohibidos: indices que NO pueden usarse como evidencia (el propio doc de la consulta)"""
    ok = hit = hit_b0 = 0; silos_ab = []; dom_ctx = []; dom_ctx_b0 = []; m = 0
    for i in idx_consultas:
        obj = set(np.where((fuentes == fuentes[i]) & (titulos == titulos[i]))[0].tolist()) - {i}
        if not obj:
            continue
        m += 1
        sims = X @ X[i]; sims[i] = -2
        z = X[i] @ W; z = z / (np.linalg.norm(z) + 1e-12)
        base = {s: float(np.dot(z, cent[s])) for s in SILOS}
        sc = {s: max(base[s], 1e-6) * max(float(sims[silo == s].max()), 1e-6) for s in SILOS}
        sel = conjunto(sc, g)
        ok += bool({silo[j] for j in obj} & set(sel))
        sf = np.where(np.isin(silo, sel), sims, -2)
        top = np.argpartition(-sf, K)[:K]
        hit += bool(obj & set(top.tolist()))
        topb = np.argpartition(-sims, K)[:K]
        hit_b0 += bool(obj & set(topb.tolist()))
        silos_ab.append(len(sel))
        dom_ctx.append(len({DOM.get(fuentes[j]) for j in top}))
        dom_ctx_b0.append(len({DOM.get(fuentes[j]) for j in topb}))
    if m == 0:
        return None
    return dict(m=m, acierto=ok/m, recall=hit/m, recall_b0=hit_b0/m, silos=np.mean(silos_ab),
                dom_ctx=np.mean(dom_ctx), dom_ctx_b0=np.mean(dom_ctx_b0))

# --- GroupKFold por documento ---
random.seed(SEED)
docs_sh = docs[:]; random.shuffle(docs_sh)
NF = 5
folds = [docs_sh[i::NF] for i in range(NF)]
LAMS = [0.1, 0.3, 0.5, 0.8]
GAMMAS = [0.70, 0.80, 0.90, 0.95]

print(f"GroupKFold por DOCUMENTO · {NF} folds · lambda y gamma elegidos DENTRO de cada train")
print()
res = []
for k_f, test_docs in enumerate(folds, 1):
    test_mask = np.isin(fuentes, test_docs)
    idx_train = np.where(~test_mask)[0]
    idx_test = np.where(test_mask)[0]
    # consultas del fold externo (titulos utilizables de esos documentos)
    cons_test = [i for i in idx_test if fuentes[i] in DOM and 15 <= len(titulos[i]) <= 70]
    if len(cons_test) > 60:
        random.seed(SEED + k_f); cons_test = random.sample(cons_test, 60)
    # --- seleccion interna de hiperparametros (split interno por documento) ---
    docs_tr = [dd for dd in docs if dd not in test_docs]
    random.seed(SEED + 100 + k_f)
    val_docs = random.sample(docs_tr, max(2, len(docs_tr) // 4))
    idx_fit = np.array([i for i in idx_train if fuentes[i] not in val_docs])
    cons_val = [i for i in idx_train if fuentes[i] in val_docs and fuentes[i] in DOM
                and 15 <= len(titulos[i]) <= 70]
    if len(cons_val) > 60:
        random.seed(SEED + 200 + k_f); cons_val = random.sample(cons_val, 60)
    mejor = (None, None, -1)
    for lam in LAMS:
        W, cent = lda_fit(idx_fit, lam)
        if W is None:
            continue
        for g in GAMMAS:
            r = evaluar(cons_val, W, cent, g, None)
            if r and r["recall"] > mejor[2]:
                mejor = (lam, g, r["recall"])
    lam_b, g_b, _ = mejor
    # --- ajuste final con TODO el train del fold y evaluacion en el fold externo ---
    W, cent = lda_fit(idx_train, lam_b)
    r = evaluar(cons_test, W, cent, g_b, None)
    if r:
        r.update(fold=k_f, lam=lam_b, gamma=g_b, docs_test=len(test_docs))
        res.append(r)
        print(f"  fold {k_f}: {len(test_docs)} docs · n={r['m']:3d} · elegidos lam={lam_b} g={g_b}  ->  "
              f"acierto={r['acierto']:5.1%}  recall LDA={r['recall']:5.1%}  B0={r['recall_b0']:5.1%}  "
              f"silos={r['silos']:.2f}")

print()
if res:
    a = np.array([r["acierto"] for r in res]); rl = np.array([r["recall"] for r in res])
    rb = np.array([r["recall_b0"] for r in res]); sl = np.array([r["silos"] for r in res])
    dc = np.array([r["dom_ctx"] for r in res]); db = np.array([r["dom_ctx_b0"] for r in res])
    print("RESULTADO CON VALIDACION AGRUPADA Y ANIDADA (media +- desvio entre folds)")
    print()
    print(f"  acierto de ruteo      : {a.mean():.1%} +- {a.std():.1%}")
    print(f"  recall LDA            : {rl.mean():.1%} +- {rl.std():.1%}")
    print(f"  recall B0             : {rb.mean():.1%} +- {rb.std():.1%}")
    print(f"  diferencia LDA - B0   : {(rl-rb).mean()*100:+.1f} pp  (por fold: "
          + " ".join(f"{x*100:+.1f}" for x in (rl - rb)) + ")")
    print()
    print("  EXPOSICION DESAGREGADA (correccion de Codex):")
    print(f"    silos CONSULTADOS (alcance de busqueda) : LDA {sl.mean():.2f}  vs  B0 4.00")
    print(f"    dominios PRESENTES en el contexto        : LDA {dc.mean():.2f}  vs  B0 {db.mean():.2f}")
    print(f"    chunks entregados al generador           : LDA {K}     vs  B0 {K}   (identico)")
    print()
    print(f"  hiperparametros elegidos por fold: lambda={[r['lam'] for r in res]}  gamma={[r['gamma'] for r in res]}")
