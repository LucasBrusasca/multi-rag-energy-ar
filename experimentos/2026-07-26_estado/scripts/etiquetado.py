"""IDEA B: ¿el CONTEXTO ETIQUETADO por regimen reduce la incorporacion del regimen equivocado?

C.54 midio: con contexto contaminado (dosis 2), el generador incorpora el regimen que no
aplica ~30% de las veces (deteccion por identificador unico de norma).

Hipotesis: si los chunks van ROTULADOS por dominio + instruccion de no mezclar regimenes,
ese 30% cae. Es gobernanza a nivel GENERACION usando los stickers — la capa nunca optimizada.

Mismos 10 casos de C.54, dosis fija = 2 intrusos, dos brazos:
  A) contexto PLANO (identico a C.54)  — replica el baseline
  B) contexto ETIQUETADO por dominio + instruccion anti-mezcla
"""
import sys, io, json, time, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
from db import conectar
from embedder import embed_query
from generador import generar_respuesta, INSTRUCCIONES, _formatear_contexto
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
NOMBRE_DOM = {"legal": "REGULATORIO-ENERGÉTICO", "impositivo": "IMPOSITIVO-FISCAL",
              "contable": "CONTABLE", "financiero": "FINANCIERO"}

CASOS = [
    ("¿Qué ocurre si una empresa del sector eléctrico incumple las obligaciones que le impone el marco regulatorio?",
     "Ley_24065_Energia_Electrica_TO", "impositivo"),
    ("¿Desde cuándo empieza a correr el término para que el fisco reclame un tributo?",
     "Ley_11683_Procedimiento_Fiscal_TO", "legal"),
    ("¿Qué facultades tiene el organismo de control del servicio eléctrico?",
     "Ley_24065_Energia_Electrica_TO", "impositivo"),
    ("¿Cómo se determina de oficio la materia imponible cuando el contribuyente no presenta la declaración?",
     "Ley_11683_Procedimiento_Fiscal_TO", "legal"),
    ("¿Qué porcentaje corresponde retener sobre los pagos alcanzados por el régimen?",
     "RG_AFIP_830", "legal"),
    ("¿Cómo se remunera la energía en el mercado mayorista?",
     "Res_SE_61_1992_Los_Procedimientos", "financiero"),
    ("¿Qué obligaciones tiene el transportista respecto del sistema de transporte?",
     "Res_SE_137_1992", "impositivo"),
    ("¿Cómo se compone el patrimonio neto al cierre del ejercicio?",
     "Estados_Contables_Neuquen", "impositivo"),
    ("¿Qué régimen se aplica a la distribución y comercialización de gas natural?",
     "Ley_24076_Gas_Natural_TO", "impositivo"),
    ("¿Qué sucede ante la falta de presentación de la declaración jurada en término?",
     "Decreto_821_1998_TO_Ley_11683", "legal"),
]
ID = {"Ley_24065_Energia_Electrica_TO": [r"24\.?065"], "Ley_24076_Gas_Natural_TO": [r"24\.?076"],
      "Decreto_1738_1992_Reglamentario_Gas": [r"1738"], "Decreto_1398_1992_Reglamentario_Electrico": [r"1398"],
      "Res_SE_61_1992_Los_Procedimientos": [r"\b61/9?2?\b", r"Res_SE_61", r"Procedimientos"],
      "Res_SE_137_1992": [r"\b137\b"], "ENRE_Resolucion_544_2024": [r"544"],
      "Ley_11683_Procedimiento_Fiscal_TO": [r"11\.?683"], "Decreto_821_1998_TO_Ley_11683": [r"\b821\b", r"11\.?683"],
      "RG_AFIP_830": [r"\b830\b", r"AFIP"], "Estados_Contables_Neuquen": [r"Neuqu"],
      "EEFF-ind-31-03-2019": [r"EEFF"], "FS-31-03-2019": [r"FS-31"],
      "TR-consolidado-03-2026_VF-Clean": [r"TR-consolidado"], "MSU_ON_ClaseIV": [r"MSU"],
      "Transener_Calificacion_FIX": [r"Transener_Calificacion", r"FIX"],
      "Transener-Company-Presentation-April-2026": [r"Company.Presentation"]}

def menciona(resp, doc):
    return any(re.search(p, resp, re.I) for p in ID.get(doc, [])) or doc.lower() in resp.lower()

INSTRUCCION_EXTRA = """

## Regímenes normativos (CRÍTICO)
El contexto está organizado por DOMINIO NORMATIVO (rótulos ###). Cada dominio es un régimen
jurídico DISTINTO e INDEPENDIENTE.
- Respondé usando EXCLUSIVAMENTE el/los dominio(s) que la pregunta requiere.
- PROHIBIDO aplicar o mencionar normas de un dominio que la pregunta no pide, aunque estén
  en el contexto: material de otro régimen presente en el contexto NO implica que sea aplicable.
- Si la pregunta es genuinamente ambigua entre regímenes, presentá cada régimen POR SEPARADO,
  indicando explícitamente a cuál corresponde cada afirmación."""

def contexto_etiquetado(chunks):
    grupos = {}
    for c in chunks:
        grupos.setdefault(DOM.get(c["fuente"], "otro"), []).append(c)
    bloques = []
    for d, cs in grupos.items():
        etiqueta = NOMBRE_DOM.get(d, d.upper())
        cuerpo = "\n\n".join(f"[{c['titulo']} - {c['fuente']}]\n{c['contenido']}" for c in cs)
        bloques.append(f"### EVIDENCIA — DOMINIO {etiqueta}:\n{cuerpo}")
    return "\n\n".join(bloques)

con = conectar(); cur = con.cursor()
res = {"plano": [], "etiquetado": []}
print("CONTEXTO ETIQUETADO vs PLANO — dosis fija de 2 intrusos · 10 casos x 2 brazos")
print()
for i, (preg, doc_ok, dom_intruso) in enumerate(CASOS, 1):
    vec = "[" + ",".join(map(str, embed_query(preg))) + "]"
    cur.execute("SELECT titulo, contenido, fuente FROM chunks WHERE fuente = %s "
                "ORDER BY embedding <=> %s::vector LIMIT 1", (doc_ok, vec))
    r = cur.fetchone()
    correcto = {"titulo": r[0], "contenido": r[1], "fuente": r[2]}
    docs_intr = [d for d, dm in DOM.items() if dm == dom_intruso]
    cur.execute("SELECT titulo, contenido, fuente FROM chunks WHERE fuente = ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT 2", (docs_intr, vec))
    intrusos = [{"titulo": a, "contenido": b, "fuente": c} for a, b, c in cur.fetchall()]
    ctx_chunks = [correcto] + intrusos

    # brazo A: plano (identico a C.54)
    ra = generar_respuesta(preg, ctx_chunks); time.sleep(0.3)
    # brazo B: etiquetado + instruccion anti-mezcla
    prompt = (f"{INSTRUCCIONES}{INSTRUCCION_EXTRA}\n\n### Contexto:\n{contexto_etiquetado(ctx_chunks)}"
              f"\n\n### Pregunta:\n{preg}\n\n### Respuesta:")
    rb = llamar_llm(prompt); time.sleep(0.3)

    for nombre, resp in (("plano", ra), ("etiquetado", rb)):
        c_ok = menciona(resp, doc_ok)
        c_intr = any(menciona(resp, x["fuente"]) for x in intrusos)
        res[nombre].append((c_ok, c_intr))
    a_ok, a_in = res["plano"][-1]; b_ok, b_in = res["etiquetado"][-1]
    print(f"  [{i:2d}] plano: correcta={'SI' if a_ok else 'no'} intrusa={'SI' if a_in else 'no'}   "
          f"etiquetado: correcta={'SI' if b_ok else 'no'} intrusa={'SI' if b_in else 'no'}")
con.close()
print()
n = len(CASOS)
print("=" * 60)
print(f"  {'brazo':14s} {'cita la correcta':>17s} {'cita la INTRUSA':>16s}")
for nombre in ("plano", "etiquetado"):
    ok = sum(a for a, _ in res[nombre]); intr = sum(b for _, b in res[nombre])
    print(f"  {nombre:14s} {ok}/{n:14d} {intr}/{n:>13d}")
