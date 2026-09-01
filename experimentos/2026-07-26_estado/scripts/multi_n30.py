"""¿EL HUECO MULTI-DOMINIO AGUANTA CON MAS n? — replica de C.62 con 30 preguntas.

C.62 midio 8 preguntas: B0 cubre ambos dominios 1/8 (12%), cupo-con-dominios-correctos 8/8.
Con n=8 eso puede ser casualidad. Se replica con 30 preguntas construidas sistematicamente
sobre los 6 pares de dominios posibles (5 por par).

⚠️ Las preguntas siguen siendo de Claude. Esto NO valida el hallazgo: mide si es ESTABLE.
"""
import sys, io, json
from pathlib import Path

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
K = 4

CASOS = [
    # legal + contable
    ("¿Qué efecto tiene una sanción del ente regulador sobre los estados contables de la distribuidora?", {"legal","contable"}),
    ("¿Cómo se refleja en el estado de resultados el pago de penalidades regulatorias?", {"legal","contable"}),
    ("¿Cómo afecta el marco regulatorio del transporte eléctrico a la valuación de los activos?", {"legal","contable"}),
    ("¿Qué previsiones contables corresponden por incumplimientos del contrato de concesión?", {"legal","contable"}),
    ("¿Cómo se registra el canon de concesión que exige la normativa energética?", {"legal","contable"}),
    # legal + financiero
    ("¿Qué impacto tiene el régimen tarifario regulado sobre la proyección de ingresos?", {"legal","financiero"}),
    ("¿Cómo influye el marco regulatorio en la calificación crediticia de una transportista?", {"legal","financiero"}),
    ("¿Qué riesgos regulatorios deben informarse a los inversores de una emisora energética?", {"legal","financiero"}),
    ("¿Cómo afecta una resolución del ENRE al flujo de fondos de la concesionaria?", {"legal","financiero"}),
    ("¿Qué garantías exige el marco regulatorio para el financiamiento de obras de transporte?", {"legal","financiero"}),
    # impositivo + contable
    ("¿Cómo se registra contablemente el impuesto a las ganancias determinado según el régimen fiscal?", {"impositivo","contable"}),
    ("¿Qué tratamiento contable corresponde a las previsiones por contingencias fiscales?", {"impositivo","contable"}),
    ("¿Cómo se contabilizan las retenciones sufridas por el contribuyente?", {"impositivo","contable"}),
    ("¿Qué asiento corresponde por el devengamiento de intereses resarcitorios impositivos?", {"impositivo","contable"}),
    ("¿Cómo se expone en el balance el saldo a favor de impuestos?", {"impositivo","contable"}),
    # impositivo + financiero
    ("¿Cómo impactan las retenciones impositivas en el flujo de fondos de la compañía?", {"impositivo","financiero"}),
    ("¿Qué obligaciones fiscales genera la emisión de una obligación negociable?", {"impositivo","financiero"}),
    ("¿Qué impacto tiene el endeudamiento financiero en la determinación del impuesto a las ganancias?", {"impositivo","financiero"}),
    ("¿Cómo tributan los intereses pagados a inversores del exterior?", {"impositivo","financiero"}),
    ("¿Qué efecto fiscal tiene la colocación de deuda en el mercado de capitales?", {"impositivo","financiero"}),
    # contable + financiero
    ("¿Cómo se vincula el resultado del ejercicio con la generación de caja operativa?", {"contable","financiero"}),
    ("¿Qué información contable sustenta el cálculo del nivel de endeudamiento?", {"contable","financiero"}),
    ("¿Cómo se refleja la deuda financiera en el estado de situación patrimonial?", {"contable","financiero"}),
    ("¿Qué relación hay entre las provisiones registradas y el riesgo financiero informado?", {"contable","financiero"}),
    ("¿Cómo impactan los intereses devengados en el resultado y en el flujo de efectivo?", {"contable","financiero"}),
    # legal + impositivo
    ("¿Qué régimen sancionatorio aplica al incumplimiento de obligaciones formales del sector energético?", {"legal","impositivo"}),
    ("¿Cómo se articulan las facultades del ente regulador con las del fisco ante un mismo hecho?", {"legal","impositivo"}),
    ("¿Qué plazos de prescripción rigen para las obligaciones regulatorias y para las fiscales?", {"legal","impositivo"}),
    ("¿Qué tributos alcanzan a la actividad de distribución de gas natural?", {"legal","impositivo"}),
    ("¿Cómo se recurre una determinación que involucra tanto materia regulatoria como fiscal?", {"legal","impositivo"}),
]

dpd = {}
for d in ("legal", "impositivo", "contable", "financiero"):
    dpd[d] = [k for k, v in DOM.items() if v == d]

con = conectar(); cur = con.cursor()
print(f"REPLICA DEL HUECO MULTI-DOMINIO CON n={len(CASOS)}  ·  k={K}")
print("  (6 pares de dominios x 5 preguntas · preguntas de Claude, sin validar)")
print()
ok_b0 = ok_cupo = 0
por_par = {}
brechas = []
for preg, req in CASOS:
    v = embed_query(preg); lit = "[" + ",".join(map(str, v)) + "]"
    cur.execute("SELECT fuente FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s", (lit, K))
    db0 = {DOM.get(f) for (f,) in cur.fetchall()}
    ctx = []
    for d in sorted(req):
        cur.execute("SELECT fuente FROM chunks WHERE fuente = ANY(%s) "
                    "ORDER BY embedding <=> %s::vector LIMIT %s", (dpd[d], lit, K // 2))
        ctx += [f for (f,) in cur.fetchall()]
    dcu = {DOM.get(f) for f in ctx}
    a, b = req <= db0, req <= dcu
    ok_b0 += a; ok_cupo += b
    par = "+".join(sorted(req))
    por_par.setdefault(par, [0, 0, 0])
    por_par[par][0] += a; por_par[par][1] += b; por_par[par][2] += 1
    # brecha: cuanto peor es el mejor chunk del dominio perdido vs el mejor global
    if not a:
        cur.execute("SELECT 1-(embedding <=> %s::vector) FROM chunks ORDER BY embedding <=> %s::vector LIMIT 1", (lit, lit))
        g = float(cur.fetchone()[0])
        falta = req - db0
        for d in falta:
            cur.execute("SELECT 1-(embedding <=> %s::vector) FROM chunks WHERE fuente = ANY(%s) "
                        "ORDER BY embedding <=> %s::vector LIMIT 1", (lit, dpd[d], lit))
            brechas.append(g - float(cur.fetchone()[0]))
con.close()
n = len(CASOS)
print(f"  {'par de dominios':26s} {'B0':>10s} {'CUPO':>10s}")
for par, (a, b, t) in sorted(por_par.items()):
    print(f"  {par:26s} {a}/{t:<8d} {b}/{t}")
print()
print("=" * 62)
print(f"  B0 monolitico            {ok_b0}/{n}  ({ok_b0/n:.0%})")
print(f"  CUPO (dominios dados)    {ok_cupo}/{n}  ({ok_cupo/n:.0%})")
print()
if brechas:
    br = np.array(brechas)
    print(f"  brecha de similitud del dominio perdido (n={len(br)}):")
    print(f"     mediana {np.median(br):+.3f} · media {br.mean():+.3f} · max {br.max():+.3f}")
    print(f"     casos con brecha < 0.08 (material competitivo): {(br<0.08).sum()}/{len(br)} ({(br<0.08).mean():.0%})")
