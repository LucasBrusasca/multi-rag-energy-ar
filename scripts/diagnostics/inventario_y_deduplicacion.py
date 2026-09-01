"""FASE 1 - Inventory and deduplication across every documentary zone.

WHAT IT ANSWERS. Before growing a corpus to ~300 documents, how many documents
are there actually, and how many of them are the same document twice? A corpus
counted by files is not a corpus counted by documents, and the difference is
what turns a 300-document claim into a 260-document reality.

ZONES AUDITED, TOGETHER AND NOT SEPARATELY:
  activo                 data/raw                        the 24 in use
  infoleg_esperado       data/incoming/infoleg/textos     the 398 of the selection
  infoleg_extra          data/incoming/infoleg/textos     historical extras, other naming
  infoleg_normalizado    data/staged/infoleg/textos       the 398 normalised
  cuarentena             data/quarantine/descartados      set aside, undecided

FIVE LEVELS OF DUPLICATION, and they are not the same claim:
  1. binary        identical SHA-256. This is proof.
  2. texto         same normalised text, different bytes. Proof for HTML.
  3. logico        same InfoLEG norm id under different names. Proof.
  4. titulo        same normalised title. A CANDIDATE, not proof.
  5. tamano        byte-identical size among PDFs of different hash. A HINT.

Levels 4 and 5 are reported as candidates for human review and never as
conclusions. There is no lightweight PDF text extractor installed here, so PDF
near-duplication cannot be established by content, and this script says so
rather than guessing.

IT DOES NOT INGEST, DOES NOT MOVE FILES AND DOES NOT DOWNLOAD. It reads bytes and
writes a report.

[ES] FASE 1 - Inventario y deduplicacion sobre todas las zonas documentales.

QUE RESPONDE. Antes de crecer un corpus a ~300 documentos: cuantos documentos
hay realmente, y cuantos de ellos son el mismo documento dos veces? Un corpus
contado por archivos no es un corpus contado por documentos, y esa diferencia es
lo que convierte una afirmacion de 300 documentos en una realidad de 260.

ZONAS AUDITADAS, JUNTAS Y NO POR SEPARADO:
  activo                 data/raw                        los 24 en uso
  infoleg_esperado       data/incoming/infoleg/textos     los 398 de la seleccion
  infoleg_extra          data/incoming/infoleg/textos     extras historicos, otra nomenclatura
  infoleg_normalizado    data/staged/infoleg/textos       los 398 normalizados
  cuarentena             data/quarantine/descartados      apartados, sin decidir

CINCO NIVELES DE DUPLICACION, y no son la misma afirmacion:
  1. binario       SHA-256 identico. Esto es prueba.
  2. texto         mismo texto normalizado, distintos bytes. Prueba para HTML.
  3. logico        misma norma de InfoLEG con distinto nombre. Prueba.
  4. titulo        mismo titulo normalizado. CANDIDATO, no prueba.
  5. tamano        mismo tamano exacto entre PDF de distinto hash. INDICIO.

Los niveles 4 y 5 se reportan como candidatos a revision humana y nunca como
conclusiones. Aca no hay instalado ningun extractor liviano de texto de PDF, asi
que la casi-duplicacion de PDF no se puede establecer por contenido, y este
script lo dice en lugar de adivinarlo.

NO INGIERE, NO MUEVE ARCHIVOS Y NO DESCARGA. Lee bytes y escribe un reporte.
"""

import argparse
import collections
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from multirag.paths import DATA_DIR, PROJECT_ROOT


RECETA_VERSION = "inventario-fase1-v1"

ZONAS = {
    "activo": DATA_DIR / "raw",
    "infoleg_incoming": DATA_DIR / "incoming" / "infoleg" / "textos",
    "infoleg_normalizado": DATA_DIR / "staged" / "infoleg" / "textos",
    "cuarentena": DATA_DIR / "quarantine" / "descartados",
}

SELECCION = DATA_DIR / "incoming" / "infoleg" / "seleccion.csv"
CATALOGO = DATA_DIR / "catalog" / "metadatos_curados.csv"

# `{dominio}_{criterio}_{id}.htm` is the naming of the reproducible selection.
# Anything else in that folder is a leftover from an earlier run.
# [ES] `{dominio}_{criterio}_{id}.htm` es la nomenclatura de la seleccion
# reproducible. Cualquier otra cosa en esa carpeta sobro de una corrida anterior.
NOMBRE_ESPERADO = re.compile(r"^(energia|impositivo)_(materia|organismo)_(\d+)\.html?$", re.I)
NOMBRE_EXTRA = re.compile(r"^(energia|impositivo)_(\d+)\.html?$", re.I)


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def _plano(texto: str) -> str:
    d = unicodedata.normalize("NFKD", texto or "")
    sin = "".join(c for c in d if not unicodedata.combining(c))
    return " ".join(sin.lower().split())


def texto_de_html(ruta: Path):
    """Visible text and title of an HTML file, normalised.

    Two InfoLEG downloads of the same norm differ in bytes -session ids, dates
    in a footer- and are the same document. Comparing normalised text finds
    that; comparing bytes does not.

    [ES] Texto visible y titulo de un HTML, normalizados.

    Dos descargas de InfoLEG de la misma norma difieren en bytes -ids de sesion,
    fechas en un pie- y son el mismo documento. Comparar texto normalizado lo
    encuentra; comparar bytes no.
    """
    from bs4 import BeautifulSoup

    crudo = ruta.read_bytes()
    for codificacion in ("utf-8", "cp1252", "latin-1"):
        try:
            html = crudo.decode(codificacion)
            break
        except UnicodeDecodeError:
            continue
    else:
        html = crudo.decode("utf-8", errors="replace")

    sopa = BeautifulSoup(html, "lxml")
    for etiqueta in sopa(["script", "style"]):
        etiqueta.decompose()
    texto = _plano(sopa.get_text(" "))
    titulo = _plano(sopa.title.get_text()) if sopa.title else ""
    if not titulo:
        cabeza = sopa.find(["h1", "h2"])
        titulo = _plano(cabeza.get_text()) if cabeza else ""
    return texto, titulo


def metadatos_de_pdf(ruta: Path) -> dict:
    """Title and creation date from the PDF Info dictionary, read by pattern.

    No PDF library is installed beyond docling, which is far too heavy to run
    over the whole corpus just to deduplicate. This reads the classic
    uncompressed Info entries and returns nothing when they are not there,
    instead of pretending.

    [ES] Titulo y fecha de creacion del diccionario Info del PDF, leidos por
    patron.

    No hay instalada ninguna biblioteca de PDF salvo docling, demasiado pesada
    para correrla sobre todo el corpus solo para deduplicar. Esto lee las
    entradas Info clasicas sin comprimir y no devuelve nada cuando no estan, en
    lugar de aparentar.
    """
    crudo = ruta.read_bytes()[:2_000_000] + ruta.read_bytes()[-400_000:]
    salida = {}
    for clave in ("Title", "Author", "CreationDate", "Producer"):
        m = re.search(rf"/{clave}\s*\(((?:[^()\\]|\\.)*)\)".encode(), crudo)
        if m:
            try:
                valor = m.group(1).decode("latin-1", errors="replace").strip()
            except Exception:
                continue
            if valor:
                salida[clave.lower()] = valor
    return salida


def clasificar_infoleg(nombre: str):
    """Which InfoLEG family a file belongs to, and its norm id.

    [ES] A que familia de InfoLEG pertenece un archivo, y su id de norma.
    """
    m = NOMBRE_ESPERADO.match(nombre)
    if m:
        return "infoleg_esperado", m.group(3), m.group(1), m.group(2)
    m = NOMBRE_EXTRA.match(nombre)
    if m:
        return "infoleg_extra", m.group(2), m.group(1), None
    return "infoleg_desconocido", None, None, None


def inventariar() -> list:
    registros = []
    for zona, carpeta in ZONAS.items():
        if not carpeta.exists():
            continue
        for ruta in sorted(carpeta.iterdir()):
            if not ruta.is_file():
                continue
            registro = {
                "zona": zona,
                "ruta": str(ruta.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "nombre": ruta.name,
                "extension": ruta.suffix.lower().lstrip("."),
                "bytes": ruta.stat().st_size,
                "sha256": sha256_de(ruta),
                "texto_sha256": None,
                "titulo": None,
                "id_norma": None,
                "dominio_adquisicion": None,
                "criterio_adquisicion": None,
                "familia": None,
            }
            if zona.startswith("infoleg"):
                familia, id_norma, dominio, criterio = clasificar_infoleg(ruta.name)
                registro.update(
                    {
                        "familia": familia,
                        "id_norma": id_norma,
                        "dominio_adquisicion": dominio,
                        "criterio_adquisicion": criterio,
                    }
                )
            if registro["extension"] in ("htm", "html"):
                texto, titulo = texto_de_html(ruta)
                registro["texto_sha256"] = hashlib.sha256(texto.encode()).hexdigest()
                registro["titulo"] = titulo[:300]
                registro["caracteres_texto"] = len(texto)
            elif registro["extension"] == "pdf":
                meta = metadatos_de_pdf(ruta)
                registro["titulo"] = _plano(meta.get("title", ""))[:300] or None
                registro["pdf_meta"] = meta
            registros.append(registro)
    return registros


def agrupar(registros, clave, filtro=None) -> dict:
    """Groups of two or more records sharing a key. Singletons are not findings.

    [ES] Grupos de dos o mas registros que comparten una clave. Los solitarios no
    son hallazgos.
    """
    indice = collections.defaultdict(list)
    for r in registros:
        if filtro and not filtro(r):
            continue
        valor = r.get(clave)
        if valor:
            indice[valor].append(r)
    return {k: v for k, v in indice.items() if len(v) > 1}


def clasificar_grupo(miembros) -> str:
    """Is this duplication a defect, or the pipeline working as designed?

    The same document in `incoming` and in `staged` is normalisation doing its
    job: one document, two zones, on purpose. Reporting those 398 pairs beside a
    real duplicate would bury the thirteen findings that matter under four
    hundred that do not.

    [ES] Esta duplicacion es un defecto, o el pipeline funcionando como fue
    disenado?

    El mismo documento en `incoming` y en `staged` es la normalizacion haciendo
    su trabajo: un documento, dos zonas, a proposito. Reportar esos 398 pares al
    lado de un duplicado real enterraria los trece hallazgos que importan bajo
    cuatrocientos que no.
    """
    zonas = collections.Counter(m["zona"] for m in miembros)
    if any(n > 1 for n in zonas.values()):
        return "real"
    if set(zonas) == {"infoleg_incoming", "infoleg_normalizado"}:
        return "esperado_incoming_staged"
    return "real"


def duplicados(registros) -> dict:
    """The five levels, kept apart because they are not the same claim.

    [ES] Los cinco niveles, separados porque no son la misma afirmacion.
    """
    es_html = lambda r: r["extension"] in ("htm", "html")
    es_pdf = lambda r: r["extension"] == "pdf"

    por_tamano = agrupar(
        [dict(r, tamano=str(r["bytes"])) for r in registros if es_pdf(r)], "tamano"
    )
    # A size collision only matters when the bytes differ: identical bytes are
    # already reported as a binary duplicate and would be counted twice.
    # [ES] Una coincidencia de tamano solo importa si los bytes difieren: los
    # bytes identicos ya se reportan como duplicado binario y se contarian dos
    # veces.
    por_tamano = {
        k: v for k, v in por_tamano.items() if len({r["sha256"] for r in v}) > 1
    }

    crudos = {
        "binario": agrupar(registros, "sha256"),
        "texto_normalizado": agrupar(registros, "texto_sha256", es_html),
        "documento_logico": agrupar(registros, "id_norma"),
        "titulo_normalizado": agrupar(registros, "titulo"),
        "mismo_tamano_pdf": por_tamano,
    }
    salida = {}
    for nivel, grupos in crudos.items():
        reales, esperados = {}, {}
        for clave, miembros in grupos.items():
            destino = reales if clasificar_grupo(miembros) == "real" else esperados
            destino[clave] = miembros
        salida[nivel] = {"real": reales, "esperado_incoming_staged": esperados}
    return salida


def leer_seleccion() -> list:
    if not SELECCION.exists():
        return []
    with SELECCION.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def leer_catalogo() -> list:
    if not CATALOGO.exists():
        return []
    with CATALOGO.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def cobertura_de_seleccion(registros, seleccion) -> dict:
    """Which of the 400 selected norms actually arrived, and which did not.

    [ES] Cuales de las 400 normas seleccionadas llegaron efectivamente, y cuales
    no.
    """
    esperados = {r["id_norma"] for r in seleccion}
    presentes = {
        r["id_norma"] for r in registros
        if r["zona"] == "infoleg_incoming" and r["familia"] == "infoleg_esperado"
    }
    normalizados = {
        r["id_norma"] for r in registros if r["zona"] == "infoleg_normalizado"
    }
    return {
        "seleccionados": len(esperados),
        "presentes_incoming": len(esperados & presentes),
        "normalizados": len(esperados & normalizados),
        "faltantes": sorted(esperados - presentes),
        "normalizados_faltantes": sorted(esperados - normalizados),
    }


def _md(valor) -> str:
    return str(valor).replace("|", "\\|")


def escribir_reporte(ruta: Path, manifest, registros, dups, cobertura, seleccion) -> None:
    L = []
    A = L.append
    A("# FASE 1 — Inventario y deduplicación del material documental")
    A("")
    A(f"**Receta:** `{manifest['receta']}` · **Fecha:** 29-ago-2026")
    A("")
    A("**No se ingirió nada, no se movió ningún archivo y no se descargó nada.**")
    A("Este es el paso previo a decidir la composición del corpus ampliado.")
    A("")
    A("## Salvedades, antes de los números")
    A("")
    for aviso in manifest["salvedades"]:
        A(f"- {aviso}")
    A("")

    A("## 1 · Inventario por zona")
    A("")
    A("| zona | archivos | únicos por SHA-256 | bytes | formatos |")
    A("|---|---:|---:|---:|---|")
    for zona in ZONAS:
        de_zona = [r for r in registros if r["zona"] == zona]
        if not de_zona:
            A(f"| `{zona}` | 0 | 0 | 0 | — |")
            continue
        formatos = collections.Counter(r["extension"] for r in de_zona)
        A(
            f"| `{zona}` | {len(de_zona)} | {len({r['sha256'] for r in de_zona})} "
            f"| {sum(r['bytes'] for r in de_zona) / 1e6:.1f} MB "
            f"| {', '.join(f'{k} {v}' for k, v in formatos.most_common())} |"
        )
    total = len(registros)
    A(f"| **total** | **{total}** | **{len({r['sha256'] for r in registros})}** "
      f"| **{sum(r['bytes'] for r in registros) / 1e6:.1f} MB** | |")
    A("")

    A("### Familias dentro de InfoLEG")
    A("")
    A("| familia | archivos | qué es |")
    A("|---|---:|---|")
    familias = collections.Counter(
        r["familia"] for r in registros if r["zona"] == "infoleg_incoming"
    )
    explicacion = {
        "infoleg_esperado": "nomenclatura de la selección reproducible",
        "infoleg_extra": "extras históricos, nomenclatura anterior",
        "infoleg_desconocido": "no coincide con ningún patrón conocido",
    }
    for fam, n in familias.most_common():
        A(f"| `{fam}` | {n} | {explicacion.get(fam, '—')} |")
    A("")

    A("## 2 · Cobertura de la selección de 400 normas")
    A("")
    A("| | |")
    A("|---|---:|")
    A(f"| normas seleccionadas | {cobertura['seleccionados']} |")
    A(f"| presentes en incoming | {cobertura['presentes_incoming']} |")
    A(f"| normalizadas en staged | {cobertura['normalizados']} |")
    A(f"| faltantes | {len(cobertura['faltantes'])} |")
    A("")
    if cobertura["faltantes"]:
        A("**Faltantes** (no descargadas): "
          + ", ".join(f"`{i}`" for i in cobertura["faltantes"]) + ".")
        A("")
        A("Estas normas respondieron HTTP `403 Forbidden` en la adquisición. **No se")
        A("intenta evadir el 403.** Se documentan acá y la FASE 2 las sustituye por el")
        A("mismo criterio reproducible, no por elección manual.")
        A("")

    A("## 3 · Duplicación")
    A("")
    A("Cinco niveles, separados porque **no son la misma afirmación**. Los dos últimos")
    A("son candidatos a revisión humana, no conclusiones.")
    A("")
    A("| nivel | grupos REALES | esperados (incoming↔staged) | fuerza |")
    A("|---|---:|---:|---|")
    fuerza = {
        "binario": "**prueba** — SHA-256 idéntico",
        "texto_normalizado": "**prueba** para HTML — mismo texto, distintos bytes",
        "documento_logico": "**prueba** — misma norma InfoLEG",
        "titulo_normalizado": "candidato — mismo título",
        "mismo_tamano_pdf": "indicio — mismo tamaño, distinto hash",
    }
    for nivel, partes in dups.items():
        A(f"| `{nivel}` | **{len(partes['real'])}** "
          f"| {len(partes['esperado_incoming_staged'])} | {fuerza[nivel]} |")
    A("")
    A("La columna **esperados** son pares del mismo documento en `incoming` y en")
    A("`staged`: eso es la normalización haciendo su trabajo, no duplicación. Solo la")
    A("primera columna son hallazgos.")
    A("")

    for nivel in ("binario", "texto_normalizado", "documento_logico"):
        grupos = dups[nivel]["real"]
        if not grupos:
            continue
        A(f"### Duplicados por `{nivel}` — {len(grupos)} grupo(s)")
        A("")
        A("| clave | archivos |")
        A("|---|---|")
        for clave, miembros in sorted(grupos.items(), key=lambda kv: -len(kv[1]))[:40]:
            rutas = "<br>".join(f"`{_md(m['ruta'])}`" for m in miembros)
            A(f"| `{clave[:16]}…` | {rutas} |")
        if len(grupos) > 40:
            A(f"| … | y {len(grupos) - 40} grupo(s) más, en el JSONL |")
        A("")

    for nivel in ("titulo_normalizado", "mismo_tamano_pdf"):
        grupos = dups[nivel]["real"]
        if not grupos:
            continue
        A(f"### Candidatos por `{nivel}` — {len(grupos)} grupo(s), a revisar")
        A("")
        A("| clave | archivos |")
        A("|---|---|")
        for clave, miembros in sorted(grupos.items(), key=lambda kv: -len(kv[1]))[:25]:
            rutas = "<br>".join(f"`{_md(m['ruta'])}`" for m in miembros)
            A(f"| {_md(str(clave)[:70])} | {rutas} |")
        A("")

    A("## 4 · Documentos únicos disponibles hoy")
    A("")
    A("Contados por documento, no por archivo: un mismo documento en `incoming` y en")
    A("`staged` es **uno**, no dos.")
    A("")
    activos = [r for r in registros if r["zona"] == "activo"]
    cuarentena = [r for r in registros if r["zona"] == "cuarentena"]
    normas_unicas = {
        r["id_norma"] for r in registros
        if r["zona"] == "infoleg_incoming" and r["id_norma"]
    }
    A("| origen | documentos únicos | estado |")
    A("|---|---:|---|")
    A(f"| corpus activo | {len({r['sha256'] for r in activos})} | en uso, **no se toca** |")
    A(f"| InfoLEG (normas distintas) | {len(normas_unicas)} | descargadas, sin ingerir |")
    A(f"| cuarentena | {len({r['sha256'] for r in cuarentena})} | apartadas, sin decidir |")
    A("")

    A("## 5 · Cuarentena, documento por documento")
    A("")
    A("Es el material empresarial ya disponible: la FASE 3 empieza acá antes de")
    A("descargar nada nuevo.")
    A("")
    A("| archivo | MB | SHA-256 | título embebido en el PDF |")
    A("|---|---:|---|---|")
    for r in sorted(cuarentena, key=lambda x: x["nombre"]):
        titulo = r.get("titulo") or "(sin /Title en el PDF)"
        A(f"| `{_md(r['nombre'])}` | {r['bytes'] / 1e6:.1f} | `{r['sha256'][:12]}…` "
          f"| {_md(titulo[:60])} |")
    A("")

    A("## 6 · Lo que este inventario NO puede afirmar")
    A("")
    A("- **Casi-duplicación entre PDF.** No hay instalado un extractor liviano de texto")
    A("  de PDF; solo `docling`, demasiado pesado para correr sobre todo el corpus con")
    A("  el único fin de deduplicar. Los pares de PDF se detectan por hash exacto y se")
    A("  *sugieren* por tamaño y título embebido. Dos PDF del mismo documento con")
    A("  distinta compresión **no** serían detectados acá.")
    A("- **Dominio de los documentos.** La pertenencia de adquisición (`energia`,")
    A("  `impositivo`) es un criterio de búsqueda, **no** una etiqueta de dominio")
    A("  verificada. No se promueve a verdad.")
    A("- **Inclusión en el corpus.** Nada de lo listado queda incluido por aparecer acá.")
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
        default=PROJECT_ROOT / "reports" / "fase1_inventario_2026-08-29.md",
    )
    parser.add_argument(
        "--jsonl", type=Path,
        default=DATA_DIR / "catalog" / "candidates" / "inventario_fase1.jsonl",
    )
    args = parser.parse_args()

    print("inventariando y hasheando ...", flush=True)
    registros = inventariar()
    seleccion = leer_seleccion()
    dups = duplicados(registros)
    cobertura = cobertura_de_seleccion(registros, seleccion)

    manifest = {
        "receta": RECETA_VERSION,
        "zonas": {k: str(v.relative_to(PROJECT_ROOT)).replace("\\", "/") for k, v in ZONAS.items()},
        "archivos": len(registros),
        "sha256_unicos": len({r["sha256"] for r in registros}),
        "grupos_duplicados_reales": {k: len(v["real"]) for k, v in dups.items()},
        "grupos_esperados_incoming_staged": {
            k: len(v["esperado_incoming_staged"]) for k, v in dups.items()
        },
        "cobertura_seleccion": cobertura,
        "salvedades": [
            "No se ingirio, no se movio ningun archivo y no se descargo nada.",
            "La pertenencia de adquisicion (energia/impositivo) es criterio de "
            "busqueda, NO etiqueta de dominio verificada.",
            "Los niveles `titulo_normalizado` y `mismo_tamano_pdf` son CANDIDATOS a "
            "revision humana, no duplicados probados.",
            "No hay extractor liviano de PDF instalado: la casi-duplicacion entre PDF "
            "no se puede establecer por contenido y no se afirma.",
            "Los 24 documentos activos no se modifican.",
        ],
    }

    args.jsonl.parent.mkdir(parents=True, exist_ok=True)
    with args.jsonl.open("w", encoding="utf-8") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    escribir_reporte(args.reporte, manifest, registros, dups, cobertura, seleccion)

    print(f"archivos            {len(registros)}")
    print(f"sha256 unicos       {len({r['sha256'] for r in registros})}")
    for nivel, partes in dups.items():
        print(f"  {nivel:22} {len(partes['real']):3} real(es) / "
              f"{len(partes['esperado_incoming_staged']):3} esperado(s)")
    print(f"faltantes seleccion {len(cobertura['faltantes'])} {cobertura['faltantes']}")
    print()
    print(f"reporte  {args.reporte}")
    print(f"jsonl    {args.jsonl}")


if __name__ == "__main__":
    main()
