"""RECALCULO DE LA DOSIS-RESPUESTA con detector de cita corregido.

`dosis.py:85` detectaba la cita intrusa asi:
    any(x["fuente"].split("_")[0].lower() in resp.lower() for x in intrusos[:dosis])
El primer token de la fuente es "ley" / "decreto" / "res" / "rg" -> palabras que
aparecen en CASI CUALQUIER respuesta juridica en castellano. Falsos positivos masivos.
Por eso `dosis_resultados.json` marca 70-80% de cita intrusa: no es la señal, es el bug.

Aca se recalcula sobre las MISMAS respuestas crudas guardadas (sin volver a llamar al
LLM, costo cero) usando IDENTIFICADORES UNICOS de norma.

TRES CATEGORIAS DE CASO, declaradas y contadas por separado:
  · EVALUABLE       : el intruso tiene identificador propio distinguible del correcto
  · NO EVALUABLE    : el intruso y el documento correcto son LA MISMA NORMA
                      (Decreto 821/1998 ES el texto ordenado de la Ley 11.683; citar
                      "11.683" es correcto en las dos lecturas) o comparten entidad
                      (los dos documentos de Transener). Excluidos, no contados como
                      negativos: contarlos como "no cito" seria el error simetrico al bug.
  · SIN IDENTIFICADOR: el documento no tiene un identificador citable en texto.

Los numeros bare ("830", "544") exigen contexto normativo cercano para no confundirlos
con importes o articulos.
"""
import sys, io, json, re
from pathlib import Path
from math import comb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SCR = Path(__file__).resolve().parent.parent / "resultados"

# identificador unico por documento. None = no citable en texto.
IDENT = {
    "Ley_24065_Energia_Electrica_TO":            r"24\s*\.?\s*065",
    "Ley_24076_Gas_Natural_TO":                  r"24\s*\.?\s*076",
    "Decreto_1738_1992_Reglamentario_Gas":       r"1\s*\.?\s*738",
    "Decreto_1398_1992_Reglamentario_Electrico": r"1\s*\.?\s*398",
    "Res_SE_61_1992_Los_Procedimientos":         r"(?:resoluci[oó]n\w*\s*(?:s\.?e\.?\s*)?n?[°º]?\s*61\b|\bLos\s+Procedimientos\b)",
    "Res_SE_137_1992":                           r"(?:resoluci[oó]n\w*\s*(?:s\.?e\.?\s*)?n?[°º]?\s*137\b)",
    "ENRE_Resolucion_544_2024":                  r"(?:resoluci[oó]n\w*\s*(?:enre\s*)?n?[°º]?\s*544\b|enre\s*n?[°º]?\s*544)",
    "Ley_11683_Procedimiento_Fiscal_TO":         r"11\s*\.?\s*683",
    "Decreto_821_1998_TO_Ley_11683":             r"(?:decreto\s*n?[°º]?\s*821\b|821\s*/\s*98|821\s*/\s*1998)",
    "RG_AFIP_830":                               r"(?:r\.?\s*g\.?\s*(?:afip\s*)?n?[°º]?\s*830\b|resoluci[oó]n\s+general\s*n?[°º]?\s*830\b)",
    "Estados_Contables_Neuquen":                 r"neuqu[eé]n",
    "MSU_ON_ClaseIV":                            r"\bmsu\b",
    "Transener_Calificacion_FIX":                r"\btransener\b",
    "Transener-Company-Presentation-April-2026": r"\btransener\b",
    "EEFF-ind-31-03-2019":                       None,
    "FS-31-03-2019":                             None,
    "TR-consolidado-03-2026_VF-Clean":           None,
}
# grupos que son la MISMA norma o entidad: su identificador no los distingue
GRUPOS = [{"Ley_11683_Procedimiento_Fiscal_TO", "Decreto_821_1998_TO_Ley_11683"},
          {"Transener_Calificacion_FIX", "Transener-Company-Presentation-April-2026"}]


def mismo_grupo(a, b):
    return a == b or any(a in g and b in g for g in GRUPOS)


def cita(resp, doc):
    pat = IDENT.get(doc)
    return None if pat is None else bool(re.search(pat, resp, re.I))


d = json.loads((SCR / "dosis_resultados.json").read_text(encoding="utf-8"))
print("=" * 78)
print("  DOSIS-RESPUESTA RECALCULADA  ·  detector por identificador unico de norma")
print("=" * 78)

for r in d:
    resp = r["respuesta"]
    intr = r["intrusos"][:r["dosis"]]
    # clasificar el caso
    utiles = [x for x in intr if not mismo_grupo(x, r["doc_correcto"]) and IDENT.get(x) is not None]
    ambig = [x for x in intr if mismo_grupo(x, r["doc_correcto"])]
    sin_id = [x for x in intr if IDENT.get(x) is None and not mismo_grupo(x, r["doc_correcto"])]
    r["_utiles"] = utiles; r["_ambig"] = ambig; r["_sinid"] = sin_id
    r["_evaluable"] = (r["dosis"] == 0) or bool(utiles)
    r["_intrusa_ok"] = any(cita(resp, x) for x in utiles) if utiles else False
    r["_correcta_ok"] = cita(resp, r["doc_correcto"])

print(f"\n  {'dosis':>5s} {'n':>3s} {'evaluables':>11s} {'CITA INTRUSA':>16s} {'excluidos':>10s}")
por = {}
for r in d:
    por.setdefault(r["dosis"], []).append(r)


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    ph = k / n; dd = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / dd
    h = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5) / dd
    return (max(0, c - h), min(1, c + h))


tabla = []
for k in sorted(por):
    g = por[k]
    ev = [r for r in g if r["_evaluable"]]
    ci = sum(r["_intrusa_ok"] for r in ev)
    lo, hi = wilson(ci, len(ev))
    exc = len(g) - len(ev)
    tabla.append((k, len(ev), ci))
    print(f"  {k:5d} {len(g):3d} {len(ev):11d} {ci:6d}/{len(ev):<3d}={ci/len(ev) if ev else 0:5.0%} "
          f"[{lo:.0%},{hi:.0%}] {exc:10d}")

print(f"\n  ANTES (detector con bug 'ley'/'decreto'): dosis 1-3 marcaban 70%, 70%, 80%")
print(f"  AHORA (identificador unico)             : ", end="")
print(" · ".join(f"dosis {k}: {c}/{n}={c/n:.0%}" for k, n, c in tabla if k > 0))

# ---- por que se excluyeron casos ----
amb = sum(1 for r in d if r["_ambig"])
sid = sum(1 for r in d if r["_sinid"] and not r["_ambig"])
print(f"\n  EXCLUSIONES (declaradas, no contadas como negativos):")
print(f"     {amb} casos donde el intruso ES LA MISMA NORMA que el documento correcto")
print(f"        (Decreto 821/1998 es el texto ordenado de la Ley 11.683 -> citar '11.683'")
print(f"         es correcto en las dos lecturas; el caso es indecidible por diseño)")
print(f"     {sid} casos donde el intruso no tiene identificador citable en texto")
if amb or sid:
    print(f"  ⇒ Defecto de CONSTRUCCION del set ademas del de deteccion: se sortearon")
    print(f"    intrusos sin verificar que fueran distinguibles del documento correcto.")
else:
    print(f"  ⇒ NINGUNA exclusion: la construccion del set SI era correcta (los intrusos")
    print(f"    se sortearon de dominios distintos al del documento correcto, asi que")
    print(f"    nunca coincidieron con su norma). El defecto era SOLO de deteccion.")

# ---- test de tendencia exacto ----
def fisher(a, b, c, e):
    f1, f2 = a + b, c + e; c1, t = a + c, a + b + c + e
    pr = lambda x: comb(f1, x) * comb(f2, c1 - x) / comb(t, c1)
    p0 = pr(a); lo = max(0, c1 - f2)
    return min(sum(pr(x) for x in range(lo, min(f1, c1) + 1) if pr(x) <= p0 * (1 + 1e-9)), 1.0)


print(f"\n{'-'*78}")
n0 = [r for r in por[0] if r["_evaluable"]]
altos = [r for r in d if r["dosis"] >= 2 and r["_evaluable"]]
a = sum(r["_intrusa_ok"] for r in n0); b = len(n0) - a
c = sum(r["_intrusa_ok"] for r in altos); e = len(altos) - c
p = fisher(a, b, c, e)
print(f"  Fisher exacto  dosis 0 (n={len(n0)}, {a} intrusas)  vs  dosis>=2 (n={len(altos)}, {c} intrusas)")
print(f"     p = {p:.4f}")
if p < 0.05:
    print(f"     ⇒ CATEGORIA (A): SIGNIFICATIVO incluso con el detector corregido.")
else:
    print(f"     ⇒ CATEGORIA (B): NO SIGNIFICATIVO con el detector corregido.")
    print(f"       El p=0.0007 reportado antes era ARTEFACTO DEL BUG DE DETECCION.")
    print(f"       Con n={len(n0)} vs n={len(altos)} evaluables el test tiene poca potencia:")
    print(f"       la afirmacion 'mas intrusos -> mas citas intrusas' queda SIN RESPALDO.")

print(f"\n  cita CORRECTA (control de que el sistema seguia funcionando):")
for k in sorted(por):
    g = [r for r in por[k] if r["_correcta_ok"] is not None]
    ok = sum(bool(r["_correcta_ok"]) for r in g)
    print(f"     dosis {k}: {ok}/{len(g)} = {ok/len(g):.0%}" if g else f"     dosis {k}: sin identificador")
