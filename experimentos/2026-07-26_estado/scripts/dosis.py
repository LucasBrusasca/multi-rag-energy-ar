"""DOSIS-RESPUESTA: ¿el contexto contaminado da vuelta la respuesta?

Diseño controlado (no observacional):
  - La evidencia CORRECTA esta SIEMPRE presente, en primer lugar.
  - Se inyectan 0/1/2/3 chunks del DOMINIO EQUIVOCADO, elegidos por ser los MAS
    parecidos a la pregunta (los peores intrusos posibles = colision real).
  - Se mide en la respuesta: ¿cita la norma correcta? ¿cita la incorrecta? ¿se abstiene?

Es la premisa del §1 de la tesis, medida por primera vez.
Salida: JSON con todas las respuestas para auditar a mano y para etiquetar spans.
"""
import sys, io, json, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
from db import conectar
from embedder import embed_query
from generador import generar_respuesta

DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}

# 10 preguntas de COLISION: vocabulario compartido, respuesta anclada en un dominio
CASOS = [
    ("¿Qué ocurre si una empresa del sector eléctrico incumple las obligaciones que le impone el marco regulatorio?",
     "Ley_24065_Energia_Electrica_TO", "legal", "impositivo"),
    ("¿Desde cuándo empieza a correr el término para que el fisco reclame un tributo?",
     "Ley_11683_Procedimiento_Fiscal_TO", "impositivo", "legal"),
    ("¿Qué facultades tiene el organismo de control del servicio eléctrico?",
     "Ley_24065_Energia_Electrica_TO", "legal", "impositivo"),
    ("¿Cómo se determina de oficio la materia imponible cuando el contribuyente no presenta la declaración?",
     "Ley_11683_Procedimiento_Fiscal_TO", "impositivo", "legal"),
    ("¿Qué porcentaje corresponde retener sobre los pagos alcanzados por el régimen?",
     "RG_AFIP_830", "impositivo", "legal"),
    ("¿Cómo se remunera la energía en el mercado mayorista?",
     "Res_SE_61_1992_Los_Procedimientos", "legal", "financiero"),
    ("¿Qué obligaciones tiene el transportista respecto del sistema de transporte?",
     "Res_SE_137_1992", "legal", "impositivo"),
    ("¿Cómo se compone el patrimonio neto al cierre del ejercicio?",
     "Estados_Contables_Neuquen", "contable", "impositivo"),
    ("¿Qué régimen se aplica a la distribución y comercialización de gas natural?",
     "Ley_24076_Gas_Natural_TO", "legal", "impositivo"),
    ("¿Qué sucede ante la falta de presentación de la declaración jurada en término?",
     "Decreto_821_1998_TO_Ley_11683", "impositivo", "legal"),
]

con = conectar(); cur = con.cursor()
resultados = []
print("DOSIS-RESPUESTA — el chunk correcto SIEMPRE presente, se inyectan intrusos")
print()

for i, (pregunta, doc_correcto, dom_correcto, dom_intruso) in enumerate(CASOS, 1):
    vec = "[" + ",".join(map(str, embed_query(pregunta))) + "]"
    # chunk CORRECTO: el mejor del documento ancla
    cur.execute("""SELECT titulo, contenido, fuente FROM chunks WHERE fuente = %s
                   ORDER BY embedding <=> %s::vector LIMIT 1""", (doc_correcto, vec))
    r = cur.fetchone()
    if not r:
        continue
    correcto = {"titulo": r[0], "contenido": r[1], "fuente": r[2]}
    # INTRUSOS: los mas parecidos a la pregunta pero de documentos del dominio equivocado
    docs_intrusos = [d for d, dm in DOM.items() if dm == dom_intruso]
    cur.execute("""SELECT titulo, contenido, fuente FROM chunks WHERE fuente = ANY(%s)
                   ORDER BY embedding <=> %s::vector LIMIT 3""", (docs_intrusos, vec))
    intrusos = [{"titulo": a, "contenido": b, "fuente": c} for a, b, c in cur.fetchall()]

    print(f"[{i}/10] {pregunta[:62]}...")
    print(f"        correcto: {correcto['titulo'][:34]} ({doc_correcto[:26]})")
    for dosis in (0, 1, 2, 3):
        ctx = [correcto] + intrusos[:dosis]
        try:
            resp = generar_respuesta(pregunta, ctx)
        except Exception as e:
            resp = f"__ERROR__ {e}"
        cita_correcta = doc_correcto.split("_")[0].lower() in resp.lower() or correcto["titulo"][:14].lower() in resp.lower()
        cita_intrusa = any(x["fuente"].split("_")[0].lower() in resp.lower() for x in intrusos[:dosis]) if dosis else False
        abstiene = "no tengo evidencia suficiente" in resp.lower()
        resultados.append({"caso": i, "pregunta": pregunta, "dosis": dosis,
                           "doc_correcto": doc_correcto, "intrusos": [x["fuente"] for x in intrusos[:dosis]],
                           "respuesta": resp, "cita_correcta": cita_correcta,
                           "cita_intrusa": cita_intrusa, "abstiene": abstiene})
        print(f"        dosis {dosis}: correcta={'SI' if cita_correcta else 'no'}  "
              f"intrusa={'SI' if cita_intrusa else 'no'}  abstiene={'SI' if abstiene else 'no'}  "
              f"[{len(resp)} chars]")
        time.sleep(0.4)
    print()

con.close()
out = Path(str(Path(__file__).resolve().parent.parent / "resultados") + r"\dosis_resultados.json")
out.write_text(json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")

print("=" * 74)
print("CURVA DE DAÑO")
print()
print(f"  {'dosis':>6s} {'cita la correcta':>18s} {'cita la INTRUSA':>17s} {'se abstiene':>13s}")
for d in (0, 1, 2, 3):
    sub = [r for r in resultados if r["dosis"] == d and not r["respuesta"].startswith("__ERROR__")]
    if not sub:
        continue
    n = len(sub)
    print(f"  {d:6d} {sum(r['cita_correcta'] for r in sub)/n:17.0%} "
          f"{sum(r['cita_intrusa'] for r in sub)/n:16.0%} {sum(r['abstiene'] for r in sub)/n:12.0%}")
print()
print(f"  respuestas guardadas en: {out.name}")
