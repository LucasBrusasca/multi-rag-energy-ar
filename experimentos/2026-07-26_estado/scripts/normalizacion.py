"""RECUPERAR LA BRECHA 39.4% -> 81.9%: normalizar puntajes entre espacios propios.

C.72: con espacios propios por silo el TECHO sube a 81.9% (+4.3 pp sobre B0), pero la
fusion ingenua da 39.4% porque los cosenos de espacios distintos NO son comparables.

Se prueban formas de hacerlos comparables (todas deterministas, sin entrenar):
  1. RRF puro (baseline de C.72)
  2. Z-SCORE por silo: cuantos desvios sobre la media de similitudes de ESE silo
  3. CUANTIL empirico: en que percentil cae el resultado dentro de su propio silo
  4. MAX-NORM: dividir por el maximo alcanzable del silo
  5. Z-SCORE + seleccion (solo los silos cuyo mejor z supera un umbral)
  6. ReDDE-like: puntuar el SILO por cuanta evidencia buena tiene, elegir, y recuperar ahi

Referencia: B0 77.7% · techo con silo correcto 81.9%.
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
n = len(filas)
random.seed(7)
pd_ = {}
for i, f in enumerate(fue):
    if f in DOM and 15 <= len(tit[i]) <= 70:
        pd_.setdefault(DOM[f], []).append(i)
consultas = []
for dd, l in pd_.items():
    consultas += random.sample(l, min(40, len(l)))
objetivos = {i: (set(np.where((fue == fue[i]) & (tit == tit[i]))[0].tolist()) - {i}) for i in consultas}
objetivos = {i: o for i, o in objetivos.items() if o}

# --- espacios propios por silo (idéntico a C.72) ---
def espacio(idx, lam=0.3, dim=128):
    Xs = X[idx]; mu = Xs.mean(axis=0); C = Xs - mu
    U, S, Vt = np.linalg.svd(C, full_matrices=False)
    dim = min(dim, len(S)); W = Vt[:dim].T
    var = (S[:dim] ** 2) / len(Xs)
    esc = 1.0 / np.sqrt((1 - lam) * var + lam * var.mean() + 1e-9)
    return mu, W, esc

E = {}
for s in SILOS:
    idx = np.where(silo == s)[0]
    mu, W, esc = espacio(idx)
    Z = (X[idx] - mu) @ W * esc
    Z = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-12)
    E[s] = {"idx": idx, "Z": Z, "mu": mu, "W": W, "esc": esc}

# estadisticas de referencia por silo: distribucion de similitudes de consultas aleatorias
print("calibrando estadisticas por silo (distribucion de similitudes de fondo)...")
random.seed(23)
muestra_q = random.sample(range(n), 300)
for s in SILOS:
    e = E[s]
    tops = []
    for i in muestra_q:
        z = (X[i] - e["mu"]) @ e["W"] * e["esc"]; z /= (np.linalg.norm(z) + 1e-12)
        sims = e["Z"] @ z
        tops.append(np.max(sims))
    e["mu_top"] = float(np.mean(tops)); e["sd_top"] = float(np.std(tops) + 1e-9)
    e["dist_top"] = np.sort(np.array(tops))
    print(f"   {s:12s} mejor-similitud tipica: {e['mu_top']:.3f} ± {e['sd_top']:.3f}")
print()

def buscar_silo(q, s, k, excluir):
    e = E[s]
    z = (q - e["mu"]) @ e["W"] * e["esc"]; z /= (np.linalg.norm(z) + 1e-12)
    sims = e["Z"] @ z
    orden = np.argsort(-sims)
    out = []
    for j in orden:
        gi = e["idx"][j]
        if gi in excluir:
            continue
        out.append((gi, float(sims[j])))
        if len(out) >= k:
            break
    return out

def cuantil(s, v):
    d = E[s]["dist_top"]
    return float(np.searchsorted(d, v) / len(d))

BRAZOS = ["B0 global (compartido)", "1. RRF puro", "2. Z-SCORE por silo", "3. CUANTIL empirico",
          "4. MAX-NORM", "5. Z-SCORE + seleccion", "6. ReDDE-like (elige silo)",
          "TECHO: silo correcto"]
hit = {b: 0 for b in BRAZOS}; cont = {b: [] for b in BRAZOS}; nsil = {b: [] for b in BRAZOS}

for i, obj in objetivos.items():
    q = X[i]; excl = {i}
    sims_g = X @ q; sims_g[i] = -2
    top = np.argpartition(-sims_g, K)[:K]
    hit["B0 global (compartido)"] += bool(obj & set(top.tolist()))
    cont["B0 global (compartido)"].append(np.mean([DOM.get(fue[j]) != DOM.get(fue[i]) for j in top]))
    nsil["B0 global (compartido)"].append(4)

    por_silo = {s: buscar_silo(q, s, K, excl) for s in SILOS}

    # 1. RRF puro
    sc = {}
    for s in SILOS:
        for r, (j, _) in enumerate(por_silo[s], 1):
            sc[j] = sc.get(j, 0) + 1 / (60 + r)
    f1 = sorted(sc, key=sc.get, reverse=True)[:K]
    # 2. z-score por silo
    cand = [(j, (v - E[s]["mu_top"]) / E[s]["sd_top"]) for s in SILOS for j, v in por_silo[s]]
    f2 = [j for j, _ in sorted(cand, key=lambda x: -x[1])[:K]]
    # 3. cuantil
    cand3 = [(j, cuantil(s, v)) for s in SILOS for j, v in por_silo[s]]
    f3 = [j for j, _ in sorted(cand3, key=lambda x: -x[1])[:K]]
    # 4. max-norm
    cand4 = [(j, v / (E[s]["dist_top"][-1] + 1e-9)) for s in SILOS for j, v in por_silo[s]]
    f4 = [j for j, _ in sorted(cand4, key=lambda x: -x[1])[:K]]
    # 5. z-score + seleccion (solo silos cuyo mejor z >= 1.0)
    zsilo = {s: (por_silo[s][0][1] - E[s]["mu_top"]) / E[s]["sd_top"] if por_silo[s] else -9 for s in SILOS}
    sel5 = [s for s in SILOS if zsilo[s] >= 1.0] or [max(zsilo, key=zsilo.get)]
    cand5 = [(j, (v - E[s]["mu_top"]) / E[s]["sd_top"]) for s in sel5 for j, v in por_silo[s]]
    f5 = [j for j, _ in sorted(cand5, key=lambda x: -x[1])[:K]]
    # 6. ReDDE-like: puntuar el silo por su masa de evidencia (suma de z de su top-3), elegir el mejor
    masa = {s: sum(max((v - E[s]["mu_top"]) / E[s]["sd_top"], 0) for _, v in por_silo[s]) for s in SILOS}
    smax = max(masa, key=masa.get)
    f6 = [j for j, _ in por_silo[smax][:K]]
    # techo
    silos_ok = list({silo[j] for j in obj})
    cand7 = [(j, (v - E[s]["mu_top"]) / E[s]["sd_top"]) for s in silos_ok for j, v in por_silo[s]]
    f7 = [j for j, _ in sorted(cand7, key=lambda x: -x[1])[:K]]

    for nom, f, ns in (("1. RRF puro", f1, 4), ("2. Z-SCORE por silo", f2, 4),
                       ("3. CUANTIL empirico", f3, 4), ("4. MAX-NORM", f4, 4),
                       ("5. Z-SCORE + seleccion", f5, len(sel5)), ("6. ReDDE-like (elige silo)", f6, 1),
                       ("TECHO: silo correcto", f7, len(silos_ok))):
        hit[nom] += bool(obj & set(f))
        cont[nom].append(np.mean([DOM.get(fue[j]) != DOM.get(fue[i]) for j in f]) if f else 0)
        nsil[nom].append(ns)

m = len(objetivos)
b0 = hit["B0 global (compartido)"] / m
print(f"NORMALIZACION ENTRE ESPACIOS PROPIOS · {m} consultas · recall@{K}")
print()
print(f"  {'metodo':32s} {'recall':>8s} {'sucio':>8s} {'silos':>7s} {'vs B0':>8s}")
for b in BRAZOS:
    marca = "  <<<" if hit[b]/m > b0 and b != "B0 global (compartido)" else ""
    print(f"  {b:32s} {hit[b]/m:7.1%} {np.mean(cont[b]):7.1%} {np.mean(nsil[b]):6.2f} "
          f"{(hit[b]/m-b0)*100:+7.1f}{marca}")
