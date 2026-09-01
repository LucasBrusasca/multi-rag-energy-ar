"""RE-ANALISIS del experimento de dosis con deteccion CORRECTA.

Bug del script original: detectaba "cita intrusa" buscando fuente.split('_')[0] = "ley",
"decreto" -> palabras comunisimas en cualquier respuesta juridica => falsos positivos.
Deteccion correcta: buscar el IDENTIFICADOR UNICO de cada norma (numero de ley/decreto/RG)
y el nombre exacto del archivo tal como el prompt pide citarlo.
"""
import sys, io, json, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = Path(str(Path(__file__).resolve().parent.parent / "resultados") + r"\dosis_resultados.json")
datos = json.loads(P.read_text(encoding="utf-8"))

# identificador UNICO por documento (numero de norma o nombre distintivo)
ID = {
    "Ley_24065_Energia_Electrica_TO": [r"24\.?065"],
    "Ley_24076_Gas_Natural_TO": [r"24\.?076"],
    "Decreto_1738_1992_Reglamentario_Gas": [r"1738"],
    "Decreto_1398_1992_Reglamentario_Electrico": [r"1398"],
    "Res_SE_61_1992_Los_Procedimientos": [r"\b61/9?2?\b", r"Res_SE_61", r"Procedimientos"],
    "Res_SE_137_1992": [r"\b137\b", r"Res_SE_137"],
    "ENRE_Resolucion_544_2024": [r"544"],
    "Ley_11683_Procedimiento_Fiscal_TO": [r"11\.?683"],
    "Decreto_821_1998_TO_Ley_11683": [r"\b821\b", r"11\.?683"],
    "RG_AFIP_830": [r"\b830\b", r"AFIP"],
    "Estados_Contables_Neuquen": [r"Neuqu"],
    "EEFF-ind-31-03-2019": [r"EEFF"],
    "FS-31-03-2019": [r"FS-31"],
    "TR-consolidado-03-2026_VF-Clean": [r"TR-consolidado"],
    "MSU_ON_ClaseIV": [r"MSU"],
    "Transener_Calificacion_FIX": [r"Transener_Calificacion", r"FIX"],
    "Transener-Company-Presentation-April-2026": [r"Company.Presentation", r"Transener-Company"],
}

def menciona(resp, doc):
    for pat in ID.get(doc, []):
        if re.search(pat, resp, re.I):
            return True
    return doc.lower() in resp.lower()

def abstiene_total(resp):
    """abstencion TOTAL = la formula exacta del prompt, no una mencion parcial"""
    r = resp.strip().lower()
    return r.startswith("no tengo evidencia suficiente")

filas = {}
for d in datos:
    if d["respuesta"].startswith("__ERROR__"):
        continue
    dosis = d["dosis"]
    correcta = menciona(d["respuesta"], d["doc_correcto"])
    intrusa = any(menciona(d["respuesta"], x) for x in d["intrusos"])
    abst = abstiene_total(d["respuesta"])
    filas.setdefault(dosis, []).append((correcta, intrusa, abst, d))

print("CURVA DE DAÑO — deteccion corregida (identificador unico de cada norma)")
print()
print(f"  {'dosis':>6s} {'n':>4s} {'cita la CORRECTA':>18s} {'cita la INTRUSA':>17s} {'abstencion total':>18s}")
for dz in sorted(filas):
    f = filas[dz]
    n = len(f)
    print(f"  {dz:6d} {n:4d} {sum(a for a,_,_,_ in f)/n:17.0%} "
          f"{sum(b for _,b,_,_ in f)/n:16.0%} {sum(c for _,_,c,_ in f)/n:17.0%}")

print()
print("CASOS donde la contaminacion METIO una norma del dominio equivocado:")
print()
vistos = 0
for dz in sorted(filas):
    if dz == 0:
        continue
    for correcta, intrusa, abst, d in filas[dz]:
        if intrusa and vistos < 4:
            vistos += 1
            print(f"  [dosis {dz}] {d['pregunta'][:60]}")
            print(f"     correcto: {d['doc_correcto']}   intrusos: {d['intrusos']}")
            frag = re.sub(r"\s+", " ", d["respuesta"])[:260]
            print(f"     respuesta: {frag}...")
            print()

# ¿la contaminacion cambia el TAMAÑO de la respuesta? (proxy de dilucion)
import statistics
print("longitud media de la respuesta por dosis (proxy de dilucion del contexto):")
for dz in sorted(filas):
    largos = [len(d["respuesta"]) for _, _, _, d in filas[dz]]
    print(f"  dosis {dz}: {statistics.mean(largos):.0f} chars")
