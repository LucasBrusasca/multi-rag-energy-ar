"""FASE 3 v2 + FASE 4 v2 - Verified counts, and gaps declared UNKNOWN.

WHAT CHANGES FROM v1. v1 said the accounting and financial gaps were 40 each.
That number was produced by assigning every corporate document to BOTH domains
by fiat, and it was wrong in both directions: some of those documents carry no
accounting material at all, and others carry tax or regulatory material that v1
never counted. With the documents actually read, the membership counts are
different - and, more importantly, they are still PROPOSALS.

SO THE GAPS ARE NOT REPORTED AS NUMBERS. A gap is the distance between a target
and a verified count. There is no verified count yet: the human review of the 59
documents has not happened. Reporting `faltan 40` would state as measured
something that depends entirely on decisions nobody has made. The gaps are
reported as UNKNOWN, with the proposal that bounds them.

TWO TOTALS, AND THEY MEAN DIFFERENT THINGS. `198` is what is available without
touching quarantine. `209` is the ceiling if all 11 quarantine documents survive
review. Quarantine was set aside for a reason nobody recorded, so it cannot be
counted as available.

[ES] FASE 3 v2 + FASE 4 v2 - Conteos verificados, y brechas declaradas
DESCONOCIDAS.

QUE CAMBIA RESPECTO DE LA v1. La v1 decia que las brechas contable y financiera
eran de 40 cada una. Ese numero salia de asignar por decreto todo documento
empresarial a AMBOS dominios, y estaba mal en las dos direcciones: algunos de
esos documentos no traen materia contable, y otros traen materia impositiva o
regulatoria que la v1 nunca conto. Con los documentos efectivamente leidos, los
conteos de membresia son otros - y, mas importante, siguen siendo PROPUESTAS.

POR ESO LAS BRECHAS NO SE REPORTAN COMO NUMEROS. Una brecha es la distancia entre
un objetivo y un conteo verificado. Todavia no hay conteo verificado: la revision
humana de los 59 documentos no ocurrio. Reportar `faltan 40` afirmaria como
medido algo que depende enteramente de decisiones que nadie tomo. Las brechas se
reportan como DESCONOCIDAS, con la propuesta que las acota.

DOS TOTALES, Y SIGNIFICAN COSAS DISTINTAS. `198` es lo disponible sin tocar
cuarentena. `209` es el techo si los 11 documentos de cuarentena sobreviven la
revision. Cuarentena se aparto por un motivo que nadie registro, asi que no se
puede contar como disponible.
"""

import argparse
import collections
import csv
import json
from pathlib import Path

from multirag.paths import DATA_DIR, PROJECT_ROOT


RECETA_VERSION = "propuesta-fase4-v2"

CARACTERIZACION = DATA_DIR / "catalog" / "candidates" / "caracterizacion_fase3v2.jsonl"
SELECCION_F2 = DATA_DIR / "catalog" / "candidates" / "seleccion_fase2.jsonl"
ADQUISICION = DATA_DIR / "catalog" / "candidates" / "adquisicion_fase3.json"
CATALOGO = DATA_DIR / "catalog" / "metadatos_curados.csv"
CUARENTENA = DATA_DIR / "quarantine" / "descartados"

DOMINIOS = ("legal", "impositivo", "contable", "financiero")
OBJETIVO = 75


def _md(v) -> str:
    return str(v).replace("|", "\\|")


def cargar():
    caract = [json.loads(l) for l in CARACTERIZACION.open(encoding="utf-8")]
    fase2 = [json.loads(l) for l in SELECCION_F2.open(encoding="utf-8")]
    adq = json.loads(ADQUISICION.read_text(encoding="utf-8"))
    with CATALOGO.open(encoding="utf-8-sig", newline="") as f:
        catalogo = list(csv.DictReader(f))
    no_pdf = [
        p.name for p in sorted(CUARENTENA.iterdir())
        if p.is_file() and p.suffix.lower() != ".pdf"
    ]
    return caract, fase2, adq, catalogo, no_pdf


def escribir(ruta: Path, manifest, caract, fase2, adq, catalogo, no_pdf):
    L = []
    A = L.append
    nuevos = [r for r in caract if r["zona"] == "incoming_candidates"]
    cuar_pdf = [r for r in caract if r["zona"] == "cuarentena"]
    sha_cuar = {r["sha256"] for r in cuar_pdf}
    cuar_unicos = len(sha_cuar) + len(no_pdf)
    bloqueados = [r for r in adq["registros"] if r.get("resultado") == "bloqueado_por_robots"]

    A("# FASE 3 v2 + FASE 4 v2 — corpus candidato con conteos verificados")
    A("")
    A(f"**Receta:** `{manifest['receta']}` · **Fecha:** 29-ago-2026")
    A("")
    A("> **Reemplaza a la FASE 4 v1, que queda como borrador.** Los números de membresía")
    A("> por dominio de la v1 salían de asignar por decreto todo documento empresarial a")
    A("> `contable` **y** `financiero`. Con los documentos leídos, eso no se sostiene.")
    A("")
    A("> **PROPUESTA PREVIA A LA INGESTA.** No se ingirió, no se descargó nada nuevo, no")
    A("> se tocó PostgreSQL, nada se movió a `data/raw`.")
    A("")

    A("## Salvedades, antes de los números")
    A("")
    for s in manifest["salvedades"]:
        A(f"- {s}")
    A("")

    A("## 1 · Conteos: verificado, propuesto y pendiente")
    A("")
    A("| | documentos | qué significa |")
    A("|---|---:|---|")
    A(f"| activos | {len(catalogo)} | **verificado**: ingeridos, con catálogo curado |")
    A(f"| InfoLEG seleccionados | {len(fase2)} | **verificado** que existen y están "
      f"normalizados; su dominio es propuesta |")
    A(f"| empresariales nuevos | {len(nuevos)} | **verificado** que se descargaron y "
      f"se leyeron; su dominio es propuesta |")
    A(f"| **disponibles sin cuarentena** | **{len(catalogo) + len(fase2) + len(nuevos)}** | |")
    A(f"| cuarentena, sin revisar | {cuar_unicos} | **pendiente**: apartados por un "
      f"motivo que nadie registró |")
    A(f"| **máximo potencial** | **{len(catalogo) + len(fase2) + len(nuevos) + cuar_unicos}** "
      f"| techo si toda la cuarentena sobrevive la revisión |")
    A("")
    A(f"De los {cuar_unicos} de cuarentena, {len(no_pdf)} son planillas cuyo contenido")
    A("**no se leyó**: no hay lector liviano instalado y no se inventa una")
    A("caracterización a partir del nombre.")
    A("")

    A("## 2 · Membresías por dominio — PROPUESTAS, no verificadas")
    A("")
    A("Cada documento empresarial fue **leído**, y su dominio se propone solo cuando")
    A(f"aparecen al menos {manifest['umbral_terminos']} términos distintos de ese dominio,")
    A("con la cita y la página. Ya no se asigna `contable` + `financiero` por decreto.")
    A("")
    A("| dominio | objetivo | InfoLEG (propuesto) | empresariales (propuesto) | total propuesto |")
    A("|---|---:|---:|---:|---:|")
    infoleg_por_dom = {
        "legal": sum(1 for e in fase2 if e["dominio_candidato"] == "legal/regulatorio"),
        "impositivo": sum(1 for e in fase2 if e["dominio_candidato"] == "impositivo"),
        "contable": 0, "financiero": 0,
    }
    emp_por_dom = collections.Counter()
    for r in nuevos:
        for d in r["dominios_propuestos"]:
            emp_por_dom[d] += 1
    for dom in DOMINIOS:
        A(f"| `{dom}` | {OBJETIVO} | {infoleg_por_dom[dom]} | {emp_por_dom.get(dom, 0)} "
          f"| {infoleg_por_dom[dom] + emp_por_dom.get(dom, 0)} |")
    A("")
    A("**La columna `total propuesto` no es un conteo de membresías verificadas.** Los")
    A("dominios de InfoLEG salen del criterio de búsqueda; los empresariales, de un")
    A("umbral léxico. Los 59 documentos están sin revisar por una persona.")
    A("")
    A("### Cómo se distribuyen las combinaciones (empresariales leídos)")
    A("")
    A("Si todo documento empresarial fuera contable y financiero a la vez, esta tabla")
    A("tendría una sola fila. Tiene varias, y esa es la corrección.")
    A("")
    A("| combinación propuesta | documentos |")
    A("|---|---:|")
    combos = collections.Counter(
        tuple(sorted(r["dominios_propuestos"])) for r in caract
    )
    for combo, n in combos.most_common():
        A(f"| {', '.join(f'`{c}`' for c in combo) or '*(ninguno)*'} | {n} |")
    A("")

    A("## 3 · Brechas: DESCONOCIDAS hasta terminar la revisión")
    A("")
    A("| dominio | objetivo | brecha |")
    A("|---|---:|---|")
    for dom in DOMINIOS:
        A(f"| `{dom}` | {OBJETIVO} | **desconocida** |")
    A("")
    A("Una brecha es la distancia entre un objetivo y un conteo **verificado**. No hay")
    A("conteo verificado: la revisión humana de los 59 documentos no ocurrió. Decir")
    A("«faltan 40» afirmaría como medido algo que depende por completo de decisiones que")
    A("nadie tomó todavía.")
    A("")
    A("Lo que sí se puede acotar: para `contable` y `financiero`, los **264 documentos**")
    A("bloqueados por `robots.txt` siguen siendo la restricción material. Existen y son")
    A("públicos; su editor pidió que los clientes automáticos no los tomen.")
    A("")

    A("## 4 · Distribución de los empresariales leídos")
    A("")
    for campo, titulo, extractor in (
        ("sigla", "Por emisor", lambda r: r.get("sigla") or r.get("entidad_propuesta") or "?"),
        ("tipo_propuesto", "Por tipo documental propuesto", lambda r: r["tipo_propuesto"]),
        ("periodo", "Por período propuesto", lambda r: r.get("periodo_propuesto") or "sin período"),
        ("confianza", "Por confianza del período", lambda r: r.get("confianza", "?")),
    ):
        A(f"### {titulo}")
        A("")
        A("| valor | documentos |")
        A("|---|---:|")
        for k, n in collections.Counter(extractor(r) for r in caract).most_common():
            A(f"| {_md(str(k)[:60])} | {n} |")
        A("")

    A("## 5 · Pertinencia: candidatos a exclusión")
    A("")
    A("Marcados **solo** cuando el documento además no trae materia de dominio regulado,")
    A("o cuando su propio tipo es el no pertinente. Una `Memoria y EEFF` que dedica un")
    A("capítulo a sostenibilidad **no** se marca: excluirla tiraría uno de los documentos")
    A("más ricos del corpus.")
    A("")
    A("| documento | motivo |")
    A("|---|---|")
    for r in caract:
        if r.get("marcas_no_pertinente"):
            A(f"| `{_md(r['archivo'][:56])}` | {', '.join(r['marcas_no_pertinente'])} |")
    A("")

    A("## 6 · Deduplicación documental, más allá del SHA-256")
    A("")
    A("Clave: entidad + tipo + período + título normalizado + páginas. Más una huella")
    A("del texto extraído.")
    A("")
    por_texto = collections.defaultdict(list)
    for r in caract:
        if r.get("sha256_texto"):
            por_texto[r["sha256_texto"]].append(r["archivo"])
    dups = {k: v for k, v in por_texto.items() if len(v) > 1}
    A("| hallazgo | cantidad |")
    A("|---|---:|")
    A(f"| duplicados por texto extraído | {len(dups)} |")
    A(f"| duplicados por clave documental | {sum(1 for k, v in collections.Counter(r['clave_documental'] for r in caract).items() if v > 1)} |")
    A("")
    for k, v in dups.items():
        A(f"- Mismo texto: {', '.join(f'`{_md(x)}`' for x in v)}")
    A("")
    A("### Transener 31-03-2019 contra el documento activo")
    A("")
    t = next((r for r in caract if "31-03-2019" in r["archivo"]), None)
    if t:
        A("| | nuevo | activo |")
        A("|---|---|---|")
        A(f"| archivo | `{_md(t['archivo'])}` | `EEFF-ind-31-03-2019.pdf` |")
        A(f"| SHA-256 | `{t['sha256'][:16]}…` | `236dda16539b6c6d…` |")
        A(f"| bytes | {t['bytes']:,} | 1.130.180 |")
        A(f"| páginas | {t['paginas']} | 40 |")
        A("")
        A("**No son el mismo archivo ni el mismo texto.** Comparten fecha de cierre y, muy")
        A("probablemente, emisor. La diferencia de páginas sugiere individual contra")
        A("consolidado, o dos presentaciones del mismo cierre. **Esto lo decide la revisión")
        A("humana**: se marca como par a comparar, no como duplicado ni como documento")
        A("distinto.")
    A("")

    A("## 7 · Instrumento de revisión")
    A("")
    A("`experimentos/revision_corpus/revision_corpus.html` — offline, doble clic. Los 59")
    A("documentos en un solo lugar: 24 activos, 24 nuevos y 11 de cuarentena. Cada uno")
    A("con su evidencia citada, la confianza de cada propuesta, y correcciones")
    A("independientes de emisor, tipo, período y dominios.")
    A("")
    A("Revisarlos en tres instrumentos separados volvería la única comparación que")
    A("importa —¿es este documento nuevo el mismo que aquel activo?— la más difícil de")
    A("hacer.")
    A("")

    A("## 8 · Lo que esta propuesta NO afirma")
    A("")
    A("- **No afirma el dominio de ningún documento.** Todo es propuesta con evidencia.")
    A("- **No afirma un tamaño de corpus.** 198 disponibles, 209 como techo.")
    A("- **No afirma brechas.** Son desconocidas hasta que la revisión termine.")
    A("- **No afirma la entidad de varios documentos de cuarentena.** Se dedujo del")
    A("  texto y la confianza es baja en cuatro de ellos.")
    A("- **No leyó dos archivos de cuarentena**, por ser planillas.")
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
        default=PROJECT_ROOT / "reports" / "fase4_propuesta_corpus_v2_2026-08-29.md",
    )
    args = parser.parse_args()

    caract, fase2, adq, catalogo, no_pdf = cargar()
    nuevos = [r for r in caract if r["zona"] == "incoming_candidates"]
    cuar = {r["sha256"] for r in caract if r["zona"] == "cuarentena"}
    cuar_unicos = len(cuar) + len(no_pdf)

    manifest = {
        "receta": RECETA_VERSION,
        "reemplaza": "propuesta-fase4-v1 (borrador; membresias por decreto)",
        "objetivo_por_dominio": OBJETIVO,
        "umbral_terminos": 3,
        "activos": len(catalogo),
        "infoleg_seleccionados": len(fase2),
        "empresariales_nuevos": len(nuevos),
        "disponibles_sin_cuarentena": len(catalogo) + len(fase2) + len(nuevos),
        "cuarentena_unicos_sin_revisar": cuar_unicos,
        "maximo_potencial": len(catalogo) + len(fase2) + len(nuevos) + cuar_unicos,
        "bloqueados_por_robots": sum(
            1 for r in adq["registros"] if r.get("resultado") == "bloqueado_por_robots"
        ),
        "brechas_por_dominio": {d: "desconocida" for d in DOMINIOS},
        "salvedades": [
            "PROPUESTA. No se ingirio, no se descargo nada nuevo, no se toco PostgreSQL.",
            "Ningun documento tiene dominio verificado; todo es propuesta con evidencia.",
            "Las brechas son DESCONOCIDAS hasta terminar la revision humana de los 59.",
            "198 disponibles sin cuarentena; 209 como techo con los 11 sin revisar.",
            "robots.txt se cumplio con evaluacion RFC 9309 propia: la biblioteca "
            "estandar de Python da la respuesta contraria en el caso de Edenor.",
            "Dos archivos de cuarentena son planillas y no se leyo su contenido.",
        ],
    }

    escribir(args.reporte, manifest, caract, fase2, adq, catalogo, no_pdf)
    print(f"disponibles sin cuarentena  {manifest['disponibles_sin_cuarentena']}")
    print(f"maximo potencial            {manifest['maximo_potencial']}")
    print(f"brechas                     desconocidas hasta la revision")
    print(f"\nreporte  {args.reporte}")


if __name__ == "__main__":
    main()
