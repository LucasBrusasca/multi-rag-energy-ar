"""LA IDEA DE LUCAS: "proyectar los vectores, armar una montaña y usar el gradiente".

Mapea a MEAN-SHIFT (ascenso por gradiente sobre la densidad, busca modas).
Hipotesis: alrededor de una consulta de UN dominio la densidad tiene UN pico; alrededor
de una consulta que necesita DOS dominios tiene DOS picos, y la consulta cae en el medio
-> el top-k se va entero al pico mas cercano (= el fallo medido en C.62).

Si contar picos separa preguntas de 1 dominio de las de 2, se obtiene un DETECTOR de
multi-dominio SIN router y SIN etiquetas: pura geometria. Y el nº de picos da el cupo.

Implementacion determinista (sin sklearn): mean-shift con kernel gaussiano sobre los
N vecinos mas cercanos a la consulta, arrancando desde cada vecino; se cuentan las modas
distintas a las que converge.
"""
import sys, io, json, random
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from embedder import embed_query

DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}

MULTI = [
    ("¿Cómo se registra contablemente el impuesto a las ganancias determinado según el régimen fiscal?", 2),
    ("¿Qué efecto tiene una sanción del ente regulador sobre los estados contables de la distribuidora?", 2),
    ("¿Cómo impactan las retenciones impositivas en el flujo de fondos de la compañía?", 2),
    ("¿Qué tratamiento contable corresponde a las previsiones por contingencias fiscales?", 2),
    ("¿Cómo se refleja en el estado de resultados el pago de penalidades regulatorias?", 2),
    ("¿Qué obligaciones fiscales genera la emisión de una obligación negociable?", 2),
    ("¿Cómo afecta el marco regulatorio del transporte eléctrico a la valuación de los activos?", 2),
    ("¿Qué impacto tiene el endeudamiento financiero en la determinación del impuesto a las ganancias?", 2),
]
UNO = [
    ("¿Qué obligaciones tiene el transportista de energía eléctrica?", 1),
    ("¿Cuándo comienza a correr el término de prescripción de los impuestos?", 1),
    ("¿Qué porcentaje corresponde retener sobre los pagos alcanzados por el régimen?", 1),
    ("¿Cómo se compone el estado de situación patrimonial al cierre?", 1),
    ("¿Qué facultades tiene el ente nacional regulador de la electricidad?", 1),
    ("¿Cómo se determina de oficio la materia imponible?", 1),
    ("¿Qué se informa en el estado de flujo de efectivo?", 1),
    ("¿Cómo se remunera la potencia en el mercado mayorista?", 1),
]

con = conectar(); cur = con.cursor()
cur.execute("SELECT silo, fuente, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
silo = np.array([r[0] for r in filas]); fue = np.array([r[1] for r in filas])
X = np.array([json.loads(r[2]) for r in filas]); X = X / np.linalg.norm(X, axis=1, keepdims=True)

N_VEC = 40          # vecindario sobre el que se estima la densidad
BW = 0.10           # ancho de banda del kernel (en distancia coseno)
TOL_MODA = 0.05     # dos modas mas cercanas que esto se consideran la misma

def modas(q, n_vec=N_VEC, bw=BW):
    """mean-shift sobre los n_vec vecinos de q: devuelve las modas distintas y su dominio."""
    sims = X @ q
    vec = np.argpartition(-sims, n_vec)[:n_vec]
    P = X[vec]
    finales = []
    for p0 in P:                                  # arranca desde cada vecino
        p = p0.copy()
        for _ in range(25):                       # iteracion de mean-shift
            d = 1 - P @ p
            w = np.exp(-(d ** 2) / (2 * bw ** 2))
            nuevo = (w[:, None] * P).sum(axis=0) / w.sum()
            nuevo /= np.linalg.norm(nuevo)
            if 1 - float(nuevo @ p) < 1e-6:
                break
            p = nuevo
        finales.append(p)
    # agrupar modas cercanas
    reps = []
    for p in finales:
        if not any(1 - float(p @ r) < TOL_MODA for r in reps):
            reps.append(p)
    # dominio de cada moda: el del vecino mas cercano a la moda
    doms = []
    for r in reps:
        j = vec[int(np.argmax(P @ r))]
        doms.append(DOM.get(fue[j]))
    return len(reps), doms, vec

print("DETECTOR DE MULTI-DOMINIO POR MEAN-SHIFT (la 'montaña' de Lucas)")
print(f"  vecindario={N_VEC} · ancho de banda={BW} · tolerancia de moda={TOL_MODA}")
print()
res = {1: [], 2: []}
for grupo, etiqueta in ((UNO, "UN dominio"), (MULTI, "DOS dominios")):
    print(f"  --- preguntas de {etiqueta} ---")
    for preg, esperado in grupo:
        q = np.array(embed_query(preg))
        k, doms, vec = modas(q)
        dom_distintos = len(set(d for d in doms if d))
        # mezcla de dominios en el vecindario (referencia simple)
        mezcla = len(set(DOM.get(fue[j]) for j in vec if DOM.get(fue[j])))
        res[esperado].append((k, dom_distintos, mezcla))
        print(f"     modas={k:2d}  dominios entre modas={dom_distintos}  "
              f"dominios en vecindario={mezcla}   \"{preg[:44]}...\"")
    print()

print("=" * 74)
print(f"  {'':26s} {'modas (media)':>14s} {'dom entre modas':>17s} {'dom en vecindario':>19s}")
for e, nom in ((1, "preguntas de 1 dominio"), (2, "preguntas de 2 dominios")):
    a = np.array(res[e])
    print(f"  {nom:26s} {a[:,0].mean():13.2f} {a[:,1].mean():16.2f} {a[:,2].mean():18.2f}")
print()
sep = lambda col: (np.array(res[2])[:, col].mean() - np.array(res[1])[:, col].mean())
print(f"  separacion (2dom - 1dom):  modas {sep(0):+.2f}  ·  dom entre modas {sep(1):+.2f}  "
      f"·  dom en vecindario {sep(2):+.2f}")
