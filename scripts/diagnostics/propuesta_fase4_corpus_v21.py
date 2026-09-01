"""FASE 3 v2.1 + FASE 4 v2.1 - after reading the documents properly.

WHAT CHANGED FROM v2, AND WHY THE NUMBERS MOVED. v2 counted domain memberships
with substring matching and no materiality floor. `iva` was found inside
`comparativa`, `arca` inside `abarca`, and `percepcion de corrupcion` counted as
tax material. With lexical boundaries and a materiality threshold, `impositivo`
went from 23 memberships to 7. The corpus did not change; the instrument did.

The two quarantine spreadsheets were reported as unreadable. They were not:
`openpyxl` is already a dependency and reads them directly. Declaring a file
unreadable when the reader is installed is a gap in the instrument, not caution.
Both are now read, and both turn out to be relevant and different from each
other.

THE GAPS REMAIN UNKNOWN, AND NOW FOR TWO REASONS. The first stands: no human has
reviewed anything. The second was missing from v2 - the review interface covers
59 documents, and the 150 selected InfoLEG norms are not among them. Finishing
the 59 would still leave `legal` and `impositivo` resting on an acquisition
filter nobody has audited.

[ES] FASE 3 v2.1 + FASE 4 v2.1 - despues de leer los documentos como corresponde.

QUE CAMBIO RESPECTO DE LA v2, Y POR QUE SE MOVIERON LOS NUMEROS. La v2 contaba
membresias de dominio con busqueda por subcadena y sin piso de materialidad.
`iva` aparecia dentro de `comparativa`, `arca` dentro de `abarca`, y `percepcion
de corrupcion` contaba como materia impositiva. Con limites lexicos y un umbral
de materialidad, `impositivo` paso de 23 membresias a 7. El corpus no cambio; el
instrumento si.

Las dos planillas de cuarentena se reportaban como ilegibles. No lo eran:
`openpyxl` ya es dependencia y las lee directamente. Declarar ilegible un archivo
cuando el lector esta instalado es un hueco del instrumento, no cautela. Ahora se
leen las dos, y resultan relevantes y distintas entre si.

LAS BRECHAS SIGUEN SIENDO DESCONOCIDAS, Y AHORA POR DOS MOTIVOS. El primero se
mantiene: nadie reviso nada. El segundo faltaba en la v2: la interfaz de revision
abarca 59 documentos, y las 150 normas InfoLEG seleccionadas no estan entre
ellos. Terminar los 59 dejaria igual a `legal` e `impositivo` apoyados en un
filtro de adquisicion que nadie audito.
"""

import argparse
import collections
import csv
import json
from pathlib import Path

from multirag.paths import DATA_DIR, PROJECT_ROOT


RECETA_VERSION = "propuesta-fase4-v2.1"

CARACTERIZACION = DATA_DIR / "catalog" / "candidates" / "caracterizacion_fase3v2.jsonl"
SELECCION_F2 = DATA_DIR / "catalog" / "candidates" / "seleccion_fase2.jsonl"
ADQUISICION = DATA_DIR / "catalog" / "candidates" / "adquisicion_fase3.json"
CATALOGO = DATA_DIR / "catalog" / "metadatos_curados.csv"

DOMINIOS = ("legal", "impositivo", "contable", "financiero")
OBJETIVO = 75

# Stratified audit of the 150 InfoLEG norms: reading all of them is not the
# point, and skipping them entirely leaves half the corpus unverified. A
# stratified sample bounds the error rate of the acquisition filter.
# [ES] Auditoria estratificada de las 150 normas InfoLEG: leerlas todas no es el
# punto, y saltearlas por completo deja media corpus sin verificar. Una muestra
# estratificada acota la tasa de error del filtro de adquisicion.
AUDITORIA_INFOLEG = {
    "estratos": "dominio de adquisicion x criterio (materia/organismo) x decada",
    "por_estrato": 4,
    "total_aproximado": 32,
    "pregunta": (
        "el criterio de busqueda de InfoLEG (`energia` / `impositivo`) coincide "
        "con el dominio real de la norma?"
    ),
    "salida": (
        "tasa de acuerdo por estrato, con la que se puede acotar cuantas de las "
        "150 estarian mal clasificadas sin leerlas todas"
    ),
}


def _md(v) -> str:
    return str(v).replace("|", "\\|")


def cargar():
    caract = [json.loads(l) for l in CARACTERIZACION.open(encoding="utf-8")]
    fase2 = [json.loads(l) for l in SELECCION_F2.open(encoding="utf-8")]
    adq = json.loads(ADQUISICION.read_text(encoding="utf-8"))
    with CATALOGO.open(encoding="utf-8-sig", newline="") as f:
        catalogo = list(csv.DictReader(f))
    return caract, fase2, adq, catalogo


def escribir(ruta: Path, manifest, caract, fase2, adq, catalogo):
    L = []
    A = L.append
    nuevos = [r for r in caract if r["zona"] == "incoming_candidates"]
    cuar = [r for r in caract if r["zona"] == "cuarentena"]
    cuar_unicos = len({r["sha256"] for r in cuar})
    bloqueados = [r for r in adq["registros"] if r.get("resultado") == "bloqueado_por_robots"]
    planillas = [r for r in caract if r.get("formato") == "xlsx"]

    A("# FASE 3 v2.1 + FASE 4 v2.1 — corpus candidato")
    A("")
    A(f"**Receta:** `{manifest['receta']}` · **Fecha:** 29-ago-2026")
    A("")
    A("> **Reemplaza a la v2.** Los conteos de membresía de la v2 estaban inflados por")
    A("> búsqueda por subcadena; las dos planillas de cuarentena figuraban como")
    A("> ilegibles y no lo eran.")
    A("")
    A("> **PROPUESTA PREVIA A LA INGESTA.** No se ingirió, no se descargó nada, no se")
    A("> tocó PostgreSQL, nada se movió a `data/raw`.")
    A("")
    A("## Salvedades, antes de los números")
    A("")
    for s in manifest["salvedades"]:
        A(f"- {s}")
    A("")

    A("## 1 · Qué cambió respecto de la v2, y por qué se movieron los números")
    A("")
    A("| # | Defecto de la v2 | Corrección | Efecto medido |")
    A("|---|---|---|---|")
    A("| 1 | Términos buscados como **subcadena**: `iva` dentro de `comparativa`, "
      "`arca` dentro de `abarca`, `percepción de corrupción` como materia impositiva "
      "| Límites léxicos | `impositivo` bajó de **23 a 7** membresías |")
    A("| 2 | Una mención incidental bastaba para proponer un dominio | Materialidad "
      "mínima: ≥3 términos distintos, ≥6 menciones, algún término en ≥2 páginas "
      "| combinaciones distintas siguen siendo 10, con menos ruido |")
    A("| 3 | Las dos planillas figuraban como no leídas | Se leen con `openpyxl`: "
      "hojas, celdas, unidades | 2 documentos más caracterizados |")
    A("| 4 | `2025 Annual Report.pdf` fechado `2T2026` | El nombre de archivo tiene "
      "prioridad para el tipo, y un anual no acepta trimestre | ahora `2025` |")
    A("| 5 | Entidad = oración (`To the shareholders of…`) | Recorte de oración, "
      "rechazo de dígitos, y se elige la razón social **más frecuente** "
      "| 0 entidades que sean oraciones |")
    A("| 6 | Fechas de cierre como texto libre (`31 DE MARZO DE 2026`) | ISO "
      "`YYYY-MM-DD` | **0** períodos no normalizados (eran 14) |")
    A("")

    A("## 2 · Conteos")
    A("")
    A("| | documentos | qué significa |")
    A("|---|---:|---|")
    A(f"| activos | {len(catalogo)} | **verificado**: ingeridos, con catálogo curado |")
    A(f"| InfoLEG seleccionados | {len(fase2)} | **verificado** que existen; su dominio "
      f"es propuesta **sin auditar** |")
    A(f"| empresariales nuevos | {len(nuevos)} | **verificado** que se descargaron y "
      f"se leyeron |")
    A(f"| **disponibles sin cuarentena** | **{len(catalogo) + len(fase2) + len(nuevos)}** | |")
    A(f"| cuarentena, únicos | {cuar_unicos} | **pendiente** |")
    A(f"| **máximo potencial** | **{len(catalogo) + len(fase2) + len(nuevos) + cuar_unicos}** | |")
    A("")

    A("## 3 · Membresías por dominio — PROPUESTAS, y ahora sin falsos positivos")
    A("")
    A("| dominio | objetivo | InfoLEG (sin auditar) | empresariales (leídos) | brecha |")
    A("|---|---:|---:|---:|---|")
    infoleg = {
        "legal": sum(1 for e in fase2 if e["dominio_candidato"] == "legal/regulatorio"),
        "impositivo": sum(1 for e in fase2 if e["dominio_candidato"] == "impositivo"),
        "contable": 0, "financiero": 0,
    }
    emp = collections.Counter()
    for r in caract:
        for d in r["dominios_propuestos"]:
            emp[d] += 1
    for dom in DOMINIOS:
        A(f"| `{dom}` | {OBJETIVO} | {infoleg[dom]} | {emp.get(dom, 0)} "
          f"| **desconocida** |")
    A("")
    A("### Por qué las brechas siguen desconocidas — ahora por DOS motivos")
    A("")
    A("1. **Nadie revisó nada.** Una brecha es la distancia a un conteo *verificado*, y")
    A("   los 59 documentos están sin revisar por una persona.")
    A("2. **La revisión de los 59 no alcanza.** La interfaz cubre 24 activos + 24")
    A("   nuevos + 11 de cuarentena. Las **150 normas InfoLEG no están incluidas**, y")
    A("   son la totalidad de las membresías `legal` e `impositivo` propuestas.")
    A("   Terminar los 59 dejaría esos dos dominios apoyados en un filtro de búsqueda")
    A("   que nadie auditó.")
    A("")

    A("## 4 · Auditoría estratificada de InfoLEG — definida, no ejecutada")
    A("")
    A("Leer las 150 no es el punto y saltearlas deja media propuesta sin verificar. Una")
    A("muestra estratificada acota la tasa de error del filtro de adquisición sin")
    A("leerlas todas.")
    A("")
    A("| | |")
    A("|---|---|")
    for k, v in AUDITORIA_INFOLEG.items():
        A(f"| {k} | {_md(v)} |")
    A("")
    A("Con ~32 normas revisadas se puede estimar, con su intervalo, cuántas de las 150")
    A("estarían mal clasificadas. **No se ejecutó**: es la propuesta del próximo paso.")
    A("")

    A("## 5 · Las dos planillas de cuarentena, ahora leídas")
    A("")
    A("La v2 las declaraba ilegibles «porque no hay lector liviano». `openpyxl` ya es")
    A("dependencia del proyecto y las lee. **Son archivos distintos y ambos relevantes.**")
    A("")
    A("| archivo | hojas | unidades | dominios propuestos | evidencia de celda |")
    A("|---|---|---|---|---|")
    for r in planillas:
        hojas = ", ".join(h["hoja"] for h in (r.get("hojas") or [])[:6])
        celda = (r.get("celdas_muestra") or [{}])[0]
        ref = (f"`{celda.get('hoja')}!{celda.get('coordenada')}`: "
               f"{_md(str(celda.get('texto', ''))[:40])}") if celda else "—"
        A(f"| `{_md(r['archivo'])}` | {_md(hojas)} "
          f"| {', '.join(r.get('unidades_detectadas', [])) or '—'} "
          f"| {', '.join(r['dominios_propuestos']) or '(ninguno)'} | {ref} |")
    A("")

    A("## 6 · Distribución de los documentos leídos")
    A("")
    for titulo, extractor in (
        ("Por tipo documental propuesto", lambda r: r["tipo_propuesto"]),
        ("Por período propuesto", lambda r: r.get("periodo_propuesto") or "sin período"),
        ("Por confianza del período", lambda r: r.get("confianza", "?")),
        ("Por confianza de la entidad", lambda r: r.get("confianza_entidad", "?")),
        ("Por combinación de dominios",
         lambda r: ", ".join(sorted(r["dominios_propuestos"])) or "(ninguno)"),
    ):
        A(f"### {titulo}")
        A("")
        A("| valor | documentos |")
        A("|---|---:|")
        for k, n in collections.Counter(extractor(r) for r in caract).most_common():
            A(f"| {_md(str(k)[:60])} | {n} |")
        A("")

    A("## 7 · Pertinencia y duplicación")
    A("")
    A("| documento | motivo de exclusión propuesto |")
    A("|---|---|")
    for r in caract:
        if r.get("marcas_no_pertinente"):
            A(f"| `{_md(r['archivo'][:56])}` | {', '.join(r['marcas_no_pertinente'])} |")
    A("")
    por_texto = collections.defaultdict(list)
    for r in caract:
        if r.get("sha256_texto"):
            por_texto[r["sha256_texto"]].append(r["archivo"])
    for k, v in por_texto.items():
        if len(v) > 1:
            A(f"- Mismo texto extraído: {', '.join(f'`{_md(x)}`' for x in v)}")
    A("")
    t = next((r for r in caract if "31-03-2019" in r["archivo"]), None)
    if t:
        A("**Transener 31-03-2019 contra el activo:** distinto SHA-256, "
          f"{t['paginas']} páginas contra 40, distinto texto. Mismo cierre "
          f"(`{t['periodo_propuesto']}`), probablemente individual contra consolidado. "
          "**Par a comparar en la revisión**, no duplicado ni documento distinto.")
    A("")

    A("## 8 · robots.txt")
    A("")
    A(f"`{len(bloqueados)}` documentos públicos quedaron sin descargar porque su editor")
    A("los prohíbe a clientes automáticos. La evaluación se corrigió a RFC 9309 con")
    A("token de producto exacto, percent-encoding canónico, especificidad por octetos")
    A("coincidentes y grupos vacíos distinguidos de grupos ausentes. **No se volvió a**")
    A("**descargar nada.**")
    A("")

    A("## 9 · Lo que esta propuesta NO afirma")
    A("")
    A("- **No afirma el dominio de ningún documento.**")
    A("- **No afirma brechas.** Desconocidas por dos motivos, no uno.")
    A("- **No afirma que revisar los 59 cierre la cuestión.** Faltan las 150 InfoLEG.")
    A("- **No afirma la entidad de 6 documentos**, con confianza baja o ausente.")
    A("- **No incluyó nada en el corpus.**")
    A("")
    A("## Manifest")
    A("")
    A("```json")
    A(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    A("```")
    A("")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(L), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--reporte", type=Path,
        default=PROJECT_ROOT / "reports" / "fase4_propuesta_corpus_v21_2026-08-29.md",
    )
    args = parser.parse_args()

    caract, fase2, adq, catalogo = cargar()
    nuevos = [r for r in caract if r["zona"] == "incoming_candidates"]
    cuar_unicos = len({r["sha256"] for r in caract if r["zona"] == "cuarentena"})
    emp = collections.Counter()
    for r in caract:
        for d in r["dominios_propuestos"]:
            emp[d] += 1

    manifest = {
        "receta": RECETA_VERSION,
        "reemplaza": "propuesta-fase4-v2 (membresias infladas por subcadena)",
        "documentos_caracterizados": len(caract),
        "activos": len(catalogo),
        "infoleg_seleccionados_sin_auditar": len(fase2),
        "empresariales_nuevos": len(nuevos),
        "cuarentena_unicos": cuar_unicos,
        "disponibles_sin_cuarentena": len(catalogo) + len(fase2) + len(nuevos),
        "maximo_potencial": len(catalogo) + len(fase2) + len(nuevos) + cuar_unicos,
        "membresias_empresariales_propuestas": dict(emp),
        "brechas_por_dominio": {d: "desconocida" for d in DOMINIOS},
        "alcance_de_la_revision": {
            "documentos_en_la_interfaz": 59,
            "infoleg_no_incluidos": len(fase2),
            "nota": "terminar los 59 NO vuelve conocidas las brechas",
        },
        "auditoria_infoleg_propuesta": AUDITORIA_INFOLEG,
        "salvedades": [
            "PROPUESTA. No se ingirio, no se descargo nada, no se toco PostgreSQL.",
            "Ningun documento tiene dominio verificado.",
            "Las brechas son DESCONOCIDAS por dos motivos: nadie reviso, y la "
            "revision de los 59 no cubre las 150 normas InfoLEG.",
            "Los conteos de membresia de la v2 estaban inflados por busqueda por "
            "subcadena; `impositivo` paso de 23 a 7.",
            "Las dos planillas de cuarentena ahora se leen con openpyxl y son "
            "distintas entre si.",
            "La revision humana es CIEGA en dos etapas y registra si la decision "
            "cambio al ver la propuesta automatica.",
        ],
    }

    escribir(args.reporte, manifest, caract, fase2, adq, catalogo)
    print(f"caracterizados            {len(caract)}")
    print(f"disponibles sin cuarentena {manifest['disponibles_sin_cuarentena']}")
    print(f"maximo potencial          {manifest['maximo_potencial']}")
    print(f"membresias empresariales  {dict(emp)}")
    print(f"brechas                   desconocidas (2 motivos)")
    print(f"\nreporte  {args.reporte}")


if __name__ == "__main__":
    main()
