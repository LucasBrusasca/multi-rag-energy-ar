"""COMPUERTA DE DENSIDAD: abstenerse ANTES del generador (idea de Gemini+Grok).

Mecanismo: si el mejor chunk del conjunto elegido no llega a un umbral tau,
NO se llama al LLM. Abstencion determinista, costo cero, cero alucinacion posible.

DESVENTAJA ESTRUCTURAL DE B0 (la hipotesis): B0 busca en los 4 silos -> siempre encuentra
algo MAS parecido -> supera el umbral mas seguido -> contesta cuando no debe.
El segregado mira UN silo -> si ahi no hay nada, la evidencia es visiblemente pobre.

Se mide SIN API: distribucion de la mejor similitud en preguntas CON respuesta vs SIN
respuesta, para B0 y para el segregado. Si las distribuciones se separan mejor en el
segregado, la compuerta funciona mejor ahi -> ventaja categorica y calibrable.
"""
import sys, io, json, random
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from embedder import embed_query
from clasificador import _coseno, _softmax, _centroide_l2
from config import CLASIFICADOR_TEMP

SILOS = ["legal", "impositivo", "contable", "financiero"]
GAMMA = 0.70
DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}

SIN_RESPUESTA = [
    "¿Cuál es la alícuota del impuesto sobre los bienes personales para el período fiscal 2025?",
    "¿Qué requisitos exige el Código Penal para configurar el delito de evasión tributaria agravada?",
    "¿Cuál es el cuadro tarifario vigente de EDENOR para usuarios residenciales T1-R1?",
    "¿Qué establece la Ley de Contrato de Trabajo sobre el preaviso en despidos sin causa?",
    "¿Cuáles son los requisitos para inscribirse en el Registro MATER de energías renovables?",
    "¿Qué porcentaje de aportes patronales corresponde al régimen de la seguridad social?",
    "¿Cuál fue el resultado neto de YPF en el ejercicio 2024?",
    "¿Qué dispone el Mercosur sobre el comercio transfronterizo de electricidad con Brasil?",
    "¿Cómo se calcula el impuesto a la ganancia mínima presunta?",
    "¿Qué requisitos pide la CNV para la oferta pública de acciones?",
    "¿Cuál es el salario mínimo vital y móvil vigente?",
    "¿Qué establece el Código Civil sobre la prescripción adquisitiva de inmuebles?",
]

con = conectar(); cur = con.cursor()
cur.execute("SELECT silo, embedding::text FROM chunks")
E = {}
for s, v in cur.fetchall():
    E.setdefault(s, []).append(np.array(json.loads(v)))
proto = {s: np.array(_centroide_l2(v)) for s, v in E.items()}

# preguntas CON respuesta: titulos reales del corpus (proxy)
cur.execute("SELECT DISTINCT fuente, titulo FROM chunks WHERE LENGTH(titulo) BETWEEN 20 AND 60")
todo = [(f, t) for f, t in cur.fetchall() if f in DOM]
random.seed(11)
CON_RESPUESTA = [t for _, t in random.sample(todo, 40)]

def medir(preg):
    q = np.array(embed_query(preg))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"
    cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks "
                "ORDER BY embedding <=> %s::vector LIMIT 1", (vec, vec))
    b0 = float(cur.fetchone()[0])
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    mejor = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "ORDER BY embedding <=> %s::vector LIMIT 1", (vec, s, vec))
        r = cur.fetchone(); mejor[s] = float(r[0]) if r else 0.0
    comb = {s: dist[s] * max(mejor[s], 1e-6) for s in SILOS}
    tot = sum(comb.values()); p = {s: comb[s] / tot for s in SILOS}
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= GAMMA:
            break
    return b0, max(mejor[s] for s in sel)

sin_b0, sin_sg, con_b0, con_sg = [], [], [], []
for pr in SIN_RESPUESTA:
    a, b = medir(pr); sin_b0.append(a); sin_sg.append(b)
for pr in CON_RESPUESTA:
    a, b = medir(pr); con_b0.append(a); con_sg.append(b)
con.close()

print("COMPUERTA DE DENSIDAD — ¿se separan las distribuciones?")
print(f"  {len(CON_RESPUESTA)} preguntas CON respuesta  ·  {len(SIN_RESPUESTA)} SIN respuesta")
print()
print(f"  {'':12s} {'CON respuesta':>16s} {'SIN respuesta':>16s} {'SEPARACION':>12s}")
for nom, c, s in (("B0 global", con_b0, sin_b0), ("SEGREGADO", con_sg, sin_sg)):
    mc, ms = np.mean(c), np.mean(s)
    # d de Cohen: cuanto se separan en desvios estandar
    sd = np.sqrt((np.var(c) + np.var(s)) / 2)
    print(f"  {nom:12s} {mc:15.3f} {ms:15.3f} {(mc-ms)/sd:11.2f} d")
print()
print("  BARRIDO DE UMBRAL (que pasa con cada tau):")
print(f"  {'tau':>6s} | {'B0: responde SIN respuesta':>27s} {'pierde CON':>11s} | "
      f"{'SEG: responde SIN resp':>23s} {'pierde CON':>11s}")
for tau in (0.45, 0.50, 0.55, 0.60, 0.65):
    fp_b0 = sum(1 for x in sin_b0 if x >= tau) / len(sin_b0)
    fn_b0 = sum(1 for x in con_b0 if x < tau) / len(con_b0)
    fp_sg = sum(1 for x in sin_sg if x >= tau) / len(sin_sg)
    fn_sg = sum(1 for x in con_sg if x < tau) / len(con_sg)
    print(f"  {tau:6.2f} | {fp_b0:26.0%} {fn_b0:10.0%} | {fp_sg:22.0%} {fn_sg:10.0%}")
print()
print("  'responde SIN respuesta' = INFRACCION (contesta algo que no esta en el corpus)")
print("  'pierde CON' = falso veto (se calla teniendo la respuesta)")
