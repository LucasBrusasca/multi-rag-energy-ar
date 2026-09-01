"""¿EL VALOR DE LA SEGREGACION DEPENDE DE LA CALIDAD DEL EMBEDDER?

Hipotesis: la colision semantica que la tesis describe es REAL, pero un embedder SOTA
(bge-m3, 2024) ya separa los dominios en su geometria -> la segregacion explicita es
redundante. Con un embedder debil (MiniLM multilingue, 2021) la separacion NO estaria
en la geometria -> ahi la segregacion SI deberia aportar.

Se mide, con la MISMA particion de silos (la ontologia no cambia) en los DOS espacios:
  1. pureza de vecindario (¿los silos son regiones?)
  2. recall@3 de B0 (global) vs SILO CORRECTO (oraculo) -> ¿cuanto aporta filtrar?

Si la brecha B0->silo es grande en MiniLM y chica en bge-m3, la tesis tiene su hallazgo.
"""
import sys, io, json, random
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from sentence_transformers import SentenceTransformer

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
cur.execute("SELECT chunk_uid, silo, titulo, contenido, fuente, embedding::text FROM chunks")
filas = cur.fetchall()
con.close()
uids = np.array([r[0] for r in filas])
silo = np.array([r[1] for r in filas])
titulos = [r[2] for r in filas]
textos = [f"{r[2]}\n{r[3]}" for r in filas]        # mismo formato que usa la ingesta
fuentes = np.array([r[4] for r in filas])
X_bge = np.array([json.loads(r[5]) for r in filas])
X_bge = X_bge / np.linalg.norm(X_bge, axis=1, keepdims=True)
n = len(filas)
print(f"corpus: {n} chunks · bge-m3 {X_bge.shape[1]}d ya en la base")

print("re-embebiendo con MiniLM (2021, 384d)... puede tardar unos minutos", flush=True)
mini = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
X_min = mini.encode(textos, batch_size=64, show_progress_bar=False, convert_to_numpy=True)
X_min = X_min / np.linalg.norm(X_min, axis=1, keepdims=True)
print(f"listo: MiniLM {X_min.shape[1]}d")
print()

# consultas: los mismos 160 titulos
random.seed(7)
idx_por_dom = {}
for i, f in enumerate(fuentes):
    if f in DOM and 15 <= len(titulos[i]) <= 70:
        idx_por_dom.setdefault(DOM[f], []).append(i)
consultas = []
for d, l in idx_por_dom.items():
    consultas += random.sample(l, min(40, len(l)))

def analizar(nombre, X, modelo_query=None):
    print(f"=== {nombre} ===")
    # 1) pureza de vecindario
    random.seed(3)
    muestra = random.sample(range(n), 600)
    pur = {s: [] for s in SILOS}
    for i in muestra:
        sims = X @ X[i]; sims[i] = -2
        vec = np.argpartition(-sims, 5)[:5]
        pur[silo[i]].append((silo[vec] == silo[i]).mean())
    glob = np.mean([v for l in pur.values() for v in l])
    print(f"  pureza de vecindario (k=5): GLOBAL {glob:.1%}   " +
          " ".join(f"{s[:4]}={np.mean(pur[s]):.0%}" for s in SILOS))
    # 2) recall B0 vs silo correcto (oraculo) — usando el titulo como consulta
    hit_b0 = hit_si = 0
    cont_b0, cont_si = [], []
    for i in consultas:
        q = X[i] if modelo_query is None else None
        sims = X @ X[i]
        sims[i] = -2                                  # leave-one-out: el propio chunk fuera
        # el "correcto" son los chunks del mismo titulo+fuente (puede haber varios)
        objetivo = np.where((fuentes == fuentes[i]) & (np.array(titulos) == titulos[i]))[0]
        objetivo = set(objetivo) - {i}
        if not objetivo:
            continue
        top = np.argpartition(-sims, K)[:K]
        top = top[np.argsort(-sims[top])]
        hit_b0 += bool(objetivo & set(top.tolist()))
        cont_b0.append(np.mean([DOM.get(fuentes[j]) != DOM.get(fuentes[i]) for j in top]))
        # filtrado al silo donde vive el objetivo
        silos_ok = {silo[j] for j in objetivo}
        mascara = np.isin(silo, list(silos_ok))
        sims_f = np.where(mascara, sims, -2)
        topf = np.argpartition(-sims_f, K)[:K]
        topf = topf[np.argsort(-sims_f[topf])]
        hit_si += bool(objetivo & set(topf.tolist()))
        cont_si.append(np.mean([DOM.get(fuentes[j]) != DOM.get(fuentes[i]) for j in topf]))
    m = len(cont_b0)
    print(f"  recall@{K} sobre {m} consultas:")
    print(f"     B0 global      : {hit_b0/m:6.1%}   sucio {np.mean(cont_b0):.1%}")
    print(f"     SILO correcto  : {hit_si/m:6.1%}   sucio {np.mean(cont_si):.1%}")
    print(f"     >>> APORTE DE FILTRAR: {(hit_si-hit_b0)/m*100:+.1f} pp de recall · "
          f"{(np.mean(cont_si)-np.mean(cont_b0))*100:+.1f} pp de suciedad")
    print()
    return glob, hit_b0/m, hit_si/m

p_b, b0_b, si_b = analizar("bge-m3 (2024, 1024d) — el actual", X_bge)
p_m, b0_m, si_m = analizar("MiniLM multilingue (2021, 384d) — el viejo", X_min)

print("=" * 72)
print("COMPARACION")
print()
print(f"  {'':28s} {'bge-m3':>12s} {'MiniLM':>12s}")
print(f"  {'pureza de vecindario':28s} {p_b:11.1%} {p_m:11.1%}")
print(f"  {'recall B0':28s} {b0_b:11.1%} {b0_m:11.1%}")
print(f"  {'recall con silo correcto':28s} {si_b:11.1%} {si_m:11.1%}")
print(f"  {'APORTE DE SEGREGAR':28s} {(si_b-b0_b)*100:+10.1f}pp {(si_m-b0_m)*100:+10.1f}pp")
print()
if (si_m - b0_m) > (si_b - b0_b):
    print("  >>> HALLAZGO: la segregacion aporta MAS con el embedder debil.")
    print("      El valor de segregar DEPENDE de la calidad de la representacion.")
else:
    print("  >>> El aporte de segregar NO crece con el embedder debil.")
