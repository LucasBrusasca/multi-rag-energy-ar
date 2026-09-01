"""PRERREQUISITO DEL GRAFO: ¿existe el hueco multi-dominio?

Hallazgo de hoy: B0 entrega 1.02 dominios en el contexto. Para preguntas de UN dominio
eso esta perfecto. La hipotesis es que para preguntas que NECESITAN DOS dominios, B0
colapsa al dominio dominante y pierde el otro por completo.

Si el hueco NO existe, el grafo de expansion no sirve -> no construir nada.
Si existe, queda medido cuanto y se justifica el mecanismo.

Se comparan 3 estrategias a MISMO k (k=4, para que quepan 2 por dominio):
  B0        : top-k global
  SEGREGADO : conjunto por cobertura (gamma) -> top-k dentro
  CUPO      : fuerza k/2 chunks de cada uno de los 2 silos mas probables
Metrica: ¿el contexto cubre AMBOS dominios requeridos?
"""
import sys, io, json
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
K = 4
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

# preguntas que REQUIEREN dos dominios (el corpus tiene material de los dos lados)
CASOS = [
    ("¿Cómo se registra contablemente el impuesto a las ganancias determinado según el régimen fiscal?",
     {"impositivo", "contable"}),
    ("¿Qué efecto tiene una sanción del ente regulador sobre los estados contables de la distribuidora?",
     {"legal", "contable"}),
    ("¿Cómo impactan las retenciones impositivas en el flujo de fondos de la compañía?",
     {"impositivo", "financiero"}),
    ("¿Qué tratamiento contable corresponde a las previsiones por contingencias fiscales?",
     {"impositivo", "contable"}),
    ("¿Cómo se refleja en el estado de resultados el pago de penalidades regulatorias?",
     {"legal", "contable"}),
    ("¿Qué obligaciones fiscales genera la emisión de una obligación negociable?",
     {"impositivo", "financiero"}),
    ("¿Cómo afecta el marco regulatorio del transporte eléctrico a la valuación de los activos?",
     {"legal", "contable"}),
    ("¿Qué impacto tiene el endeudamiento financiero en la determinación del impuesto a las ganancias?",
     {"impositivo", "financiero"}),
]

con = conectar(); cur = con.cursor()
cur.execute("SELECT silo, embedding::text FROM chunks")
E = {}
for s, v in cur.fetchall():
    E.setdefault(s, []).append(np.array(json.loads(v)))
proto = {s: np.array(_centroide_l2(v)) for s, v in E.items()}

def dominios(rows):
    return {DOM.get(f) for _, f in rows if DOM.get(f)}

print(f"¿EXISTE EL HUECO MULTI-DOMINIO?  ·  {len(CASOS)} preguntas que requieren 2 dominios  ·  k={K}")
print()
res = {"B0": [], "SEG": [], "CUPO": []}
for preg, requeridos in CASOS:
    q = np.array(embed_query(preg))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"
    # B0
    cur.execute("SELECT titulo, fuente FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s", (vec, K))
    b0 = cur.fetchall()
    # SEGREGADO (cobertura acumulada)
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    ev = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "ORDER BY embedding <=> %s::vector LIMIT 1", (vec, s, vec))
        r = cur.fetchone(); ev[s] = float(r[0]) if r else 0.0
    comb = {s: dist[s] * max(ev[s], 1e-6) for s in SILOS}
    tot = sum(comb.values()); p = {s: comb[s] / tot for s in SILOS}
    orden = sorted(p, key=p.get, reverse=True)
    sel, ac = [], 0.0
    for s in orden:
        sel.append(s); ac += p[s]
        if ac >= GAMMA:
            break
    cur.execute("SELECT titulo, fuente FROM chunks WHERE silo = ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (sel, vec, K))
    seg = cur.fetchall()
    # CUPO: k/2 de cada uno de los 2 silos mas probables
    cupo = []
    for s in orden[:2]:
        cur.execute("SELECT titulo, fuente FROM chunks WHERE silo = %s "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (s, vec, K // 2))
        cupo += cur.fetchall()

    db0, dsg, dcu = dominios(b0), dominios(seg), dominios(cupo)
    ok = lambda d: requeridos <= d
    res["B0"].append(ok(db0)); res["SEG"].append(ok(dsg)); res["CUPO"].append(ok(dcu))
    print(f"  \"{preg[:56]}...\"")
    print(f"     requiere {sorted(requeridos)}")
    print(f"     B0    ctx={sorted(db0)}  {'CUBRE' if ok(db0) else '*** PIERDE UN DOMINIO ***'}")
    print(f"     SEG   ctx={sorted(dsg)}  silos={sel}  {'CUBRE' if ok(dsg) else '*** PIERDE UN DOMINIO ***'}")
    print(f"     CUPO  ctx={sorted(dcu)}  silos={orden[:2]}  {'CUBRE' if ok(dcu) else '*** PIERDE UN DOMINIO ***'}")
    print()
con.close()
n = len(CASOS)
print("=" * 74)
print(f"  cobertura de AMBOS dominios requeridos (k={K} para los tres):")
for k_, v in res.items():
    print(f"     {k_:6s} {sum(v)}/{n}  ({sum(v)/n:.0%})")
