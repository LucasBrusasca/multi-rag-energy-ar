"""CURVA DE COMPRESION — ¿cuanto se achican los 1024d antes de que caiga el recall?

La version SIN entrenamiento de la idea IsoCompress: PCA (proyeccion lineal optima en
varianza) a distintas dimensiones, midiendo recall@3 y pureza de vecindario en cada una.

Es el argumento de ESCALABILIDAD ya listado en 00_CONTEXTO §10: si el corpus aguanta en
256d, el indice pesa 4x menos y la busqueda es mas rapida, con la MISMA calidad.
No es un intento de superar a B0 (una proyeccion que preserva la geometria no puede).
"""
import sys, io, json, random
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar

DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}
K = 3
con = conectar(); cur = con.cursor()
cur.execute("SELECT silo, titulo, fuente, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
silo = np.array([r[0] for r in filas]); titulos = np.array([r[1] for r in filas])
fuentes = np.array([r[2] for r in filas])
X = np.array([json.loads(r[3]) for r in filas]); X = X / np.linalg.norm(X, axis=1, keepdims=True)
n, d = X.shape

# consultas: protocolo silver estandar (160 titulos, seed 7)
random.seed(7)
por_dom = {}
for i, f in enumerate(fuentes):
    if f in DOM and 15 <= len(titulos[i]) <= 70:
        por_dom.setdefault(DOM[f], []).append(i)
consultas = []
for dd, l in por_dom.items():
    consultas += random.sample(l, min(40, len(l)))
objetivos = {}
for i in consultas:
    o = set(np.where((fuentes == fuentes[i]) & (titulos == titulos[i]))[0].tolist()) - {i}
    if o:
        objetivos[i] = o

# PCA sobre el corpus (centrado); componentes por SVD
mu = X.mean(axis=0)
Xc = X - mu
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
var_acum = np.cumsum(S ** 2) / np.sum(S ** 2)

def evaluar(dim):
    if dim >= d:
        Z = X
    else:
        Z = Xc @ Vt[:dim].T
        Z = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-12)
    hit = 0
    pur = []
    random.seed(3)
    muestra = random.sample(range(n), 400)
    for i in objetivos:
        sims = Z @ Z[i]; sims[i] = -2
        top = np.argpartition(-sims, K)[:K]
        hit += bool(objetivos[i] & set(top.tolist()))
    for i in muestra:
        sims = Z @ Z[i]; sims[i] = -2
        vec = np.argpartition(-sims, 5)[:5]
        pur.append((silo[vec] == silo[i]).mean())
    return hit / len(objetivos), np.mean(pur)

print(f"CURVA DE COMPRESION (PCA) · {n} chunks · {len(objetivos)} consultas · recall@{K}")
print()
print(f"  {'dim':>5s} {'var.explicada':>14s} {'recall@3':>9s} {'pureza k=5':>11s} {'memoria':>9s}")
base = None
for dim in (1024, 512, 256, 128, 64, 48, 32, 16):
    r, p = evaluar(dim)
    if base is None:
        base = r
    ve = var_acum[min(dim, len(var_acum)) - 1] if dim < d else 1.0
    print(f"  {dim:5d} {ve:13.1%} {r:8.1%} {p:10.1%} {d/dim:7.1f}x   {'<- base' if dim==1024 else ('OK' if r >= base - 0.02 else 'CAE')}")
