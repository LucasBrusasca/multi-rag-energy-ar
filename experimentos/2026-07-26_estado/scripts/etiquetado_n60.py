"""CONTEXTO ETIQUETADO — replica con n=40 (C.68 tenia n=10, p=0.50, sin poder).

Diseño PAREADO: cada caso se genera dos veces con EL MISMO contexto (mismos chunks):
  A) plano (produccion actual)
  B) etiquetado por dominio + instruccion anti-mezcla
20 preguntas x 2 dominios intrusos distintos = 40 pares. McNemar exacto sobre los pares.
"""
import sys, io, json, time, re
from pathlib import Path
from math import comb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
from db import conectar
from embedder import embed_query
from generador import generar_respuesta, INSTRUCCIONES
from llm import llamar_llm

DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}
NOMBRE = {"legal": "REGULATORIO-ENERGÉTICO", "impositivo": "IMPOSITIVO-FISCAL",
          "contable": "CONTABLE", "financiero": "FINANCIERO"}
ID = {"Ley_24065_Energia_Electrica_TO": [r"24\.?065"], "Ley_24076_Gas_Natural_TO": [r"24\.?076"],
      "Decreto_1738_1992_Reglamentario_Gas": [r"1738"], "Decreto_1398_1992_Reglamentario_Electrico": [r"1398"],
      "Res_SE_61_1992_Los_Procedimientos": [r"\b61/9?2?\b", r"Res_SE_61", r"Los Procedimientos"],
      "Res_SE_137_1992": [r"\b137\b"], "ENRE_Resolucion_544_2024": [r"544"],
      "Ley_11683_Procedimiento_Fiscal_TO": [r"11\.?683"], "Decreto_821_1998_TO_Ley_11683": [r"\b821\b", r"11\.?683"],
      "RG_AFIP_830": [r"\b830\b", r"AFIP"], "Estados_Contables_Neuquen": [r"Neuqu"],
      "EEFF-ind-31-03-2019": [r"EEFF"], "FS-31-03-2019": [r"FS-31"],
      "TR-consolidado-03-2026_VF-Clean": [r"TR-consolidado"], "MSU_ON_ClaseIV": [r"MSU"],
      "Transener_Calificacion_FIX": [r"Transener_Calificacion", r"\bFIX\b"],
      "Transener-Company-Presentation-April-2026": [r"Company.Presentation"]}

# 20 preguntas (pregunta, documento correcto, [2 dominios intrusos])
BASE = [
 ("¿Qué ocurre si una empresa del sector eléctrico incumple las obligaciones del marco regulatorio?", "Ley_24065_Energia_Electrica_TO", ["impositivo","contable"]),
 ("¿Desde cuándo empieza a correr el término para que el fisco reclame un tributo?", "Ley_11683_Procedimiento_Fiscal_TO", ["legal","financiero"]),
 ("¿Qué facultades tiene el organismo de control del servicio eléctrico?", "Ley_24065_Energia_Electrica_TO", ["impositivo","financiero"]),
 ("¿Cómo se determina de oficio la materia imponible cuando no se presenta la declaración?", "Ley_11683_Procedimiento_Fiscal_TO", ["legal","contable"]),
 ("¿Qué porcentaje corresponde retener sobre los pagos alcanzados por el régimen?", "RG_AFIP_830", ["legal","financiero"]),
 ("¿Cómo se remunera la energía en el mercado mayorista?", "Res_SE_61_1992_Los_Procedimientos", ["financiero","impositivo"]),
 ("¿Qué obligaciones tiene el transportista respecto del sistema de transporte?", "Res_SE_137_1992", ["impositivo","contable"]),
 ("¿Cómo se compone el patrimonio neto al cierre del ejercicio?", "Estados_Contables_Neuquen", ["impositivo","legal"]),
 ("¿Qué régimen se aplica a la distribución y comercialización de gas natural?", "Ley_24076_Gas_Natural_TO", ["impositivo","contable"]),
 ("¿Qué sucede ante la falta de presentación de la declaración jurada en término?", "Decreto_821_1998_TO_Ley_11683", ["legal","financiero"]),
 ("¿Qué establece la reglamentación sobre el ente regulador del gas?", "Decreto_1738_1992_Reglamentario_Gas", ["impositivo","contable"]),
 ("¿Qué recursos puede interponer el contribuyente contra una determinación?", "Ley_11683_Procedimiento_Fiscal_TO", ["legal","contable"]),
 ("¿Cómo se calcula el despacho de cargas en el sistema eléctrico?", "Res_SE_61_1992_Los_Procedimientos", ["contable","impositivo"]),
 ("¿Qué información contiene el estado de flujo de efectivo?", "FS-31-03-2019", ["impositivo","legal"]),
 ("¿Qué condiciones tiene la emisión de obligaciones negociables?", "MSU_ON_ClaseIV", ["legal","contable"]),
 ("¿Qué sanciones prevé el régimen para las infracciones formales?", "Decreto_821_1998_TO_Ley_11683", ["legal","financiero"]),
 ("¿Cómo se valúan los bienes de uso en los estados contables?", "EEFF-ind-31-03-2019", ["impositivo","legal"]),
 ("¿Qué establece la resolución del ente sobre la calidad del servicio?", "ENRE_Resolucion_544_2024", ["impositivo","financiero"]),
 ("¿Qué factores considera la calificación crediticia de la compañía?", "Transener_Calificacion_FIX", ["impositivo","legal"]),
 ("¿Qué reglamenta el decreto sobre el marco eléctrico?", "Decreto_1398_1992_Reglamentario_Electrico", ["impositivo","contable"]),
]
TODOS = ["legal","impositivo","contable","financiero"]
CASOS = [(p, d, i) for p, d, ints in BASE for i in TODOS if DOM.get(d) != i]

EXTRA = """

## Regímenes normativos (CRÍTICO)
El contexto está organizado por DOMINIO NORMATIVO (rótulos ###). Cada dominio es un régimen
jurídico DISTINTO e INDEPENDIENTE.
- Respondé usando EXCLUSIVAMENTE el/los dominio(s) que la pregunta requiere.
- PROHIBIDO aplicar o mencionar normas de un dominio que la pregunta no pide, aunque estén
  en el contexto: material de otro régimen presente NO implica que sea aplicable.
- Si la pregunta es genuinamente ambigua entre regímenes, presentá cada régimen POR SEPARADO."""

def menciona(r, doc):
    return any(re.search(p, r, re.I) for p in ID.get(doc, [])) or doc.lower() in r.lower()

def ctx_etiquetado(chunks):
    g = {}
    for c in chunks:
        g.setdefault(DOM.get(c["fuente"], "otro"), []).append(c)
    return "\n\n".join(
        f"### EVIDENCIA — DOMINIO {NOMBRE.get(d, d.upper())}:\n" +
        "\n\n".join(f"[{c['titulo']} - {c['fuente']}]\n{c['contenido']}" for c in cs)
        for d, cs in g.items())

con = conectar(); cur = con.cursor()
pares = []
print(f"CONTEXTO ETIQUETADO vs PLANO · n={len(CASOS)} pares · diseño pareado (mismo contexto)")
print()
for i, (preg, doc_ok, dom_int) in enumerate(CASOS, 1):
    vec = "[" + ",".join(map(str, embed_query(preg))) + "]"
    cur.execute("SELECT titulo, contenido, fuente FROM chunks WHERE fuente = %s "
                "ORDER BY embedding <=> %s::vector LIMIT 1", (doc_ok, vec))
    r = cur.fetchone()
    if not r:
        continue
    correcto = {"titulo": r[0], "contenido": r[1], "fuente": r[2]}
    docs_i = [d for d, dm in DOM.items() if dm == dom_int]
    cur.execute("SELECT titulo, contenido, fuente FROM chunks WHERE fuente = ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT 2", (docs_i, vec))
    intr = [{"titulo": a, "contenido": b, "fuente": c} for a, b, c in cur.fetchall()]
    ctx = [correcto] + intr
    ra = generar_respuesta(preg, ctx); time.sleep(0.25)
    rb = llamar_llm(f"{INSTRUCCIONES}{EXTRA}\n\n### Contexto:\n{ctx_etiquetado(ctx)}"
                    f"\n\n### Pregunta:\n{preg}\n\n### Respuesta:"); time.sleep(0.25)
    ia = any(menciona(ra, x["fuente"]) for x in intr)
    ib = any(menciona(rb, x["fuente"]) for x in intr)
    pares.append((menciona(ra, doc_ok), ia, menciona(rb, doc_ok), ib))
    if i % 5 == 0:
        print(f"  {i}/{len(CASOS)} …", flush=True)
con.close()

n = len(pares)
ok_a = sum(p[0] for p in pares); in_a = sum(p[1] for p in pares)
ok_b = sum(p[2] for p in pares); in_b = sum(p[3] for p in pares)
b01 = sum(1 for p in pares if p[1] and not p[3])   # plano cita intrusa, etiquetado no -> a favor
b10 = sum(1 for p in pares if p[3] and not p[1])   # etiquetado cita intrusa, plano no -> en contra
nd = b01 + b10
pval = (sum(comb(nd, k) for k in range(min(b01, b10) + 1)) / (2 ** nd) * 2) if nd else 1.0
print()
print("=" * 64)
print(f"  {'brazo':16s} {'cita la correcta':>17s} {'cita la INTRUSA':>17s}")
print(f"  {'plano':16s} {ok_a}/{n:<15d} {in_a}/{n:<15d} ({in_a/n:.0%})")
print(f"  {'etiquetado':16s} {ok_b}/{n:<15d} {in_b}/{n:<15d} ({in_b/n:.0%})")
print()
print(f"  McNemar exacto (pareado): {b01} a favor del etiquetado · {b10} en contra · n discordantes={nd}")
print(f"  p = {min(pval,1.0):.4f}   ->  {'SIGNIFICATIVO (p<0.05)' if pval < 0.05 else 'NO significativo'}")
print(f"  reduccion absoluta de citas intrusas: {(in_a-in_b)/n*100:+.1f} pp")
