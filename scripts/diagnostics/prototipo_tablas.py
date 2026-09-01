"""Table-aware prototype: what the pipeline stores today vs what it could store.

STRICTLY READ-ONLY. It converts documents into a cache directory and writes a
report. It does not connect to the database, does not re-ingest, does not touch
a single `chunk_uid` and does not modify the snapshot.

The "before" column is not a reconstruction: it is the text HybridChunker
produces for that same table, which is literally what `chunks.contenido` holds
today.

[ES] Prototipo table-aware: lo que el pipeline guarda hoy contra lo que podria
guardar.

ESTRICTAMENTE DE SOLO LECTURA. Convierte documentos a un directorio de cache y
escribe un informe. No se conecta a la base, no reingiere, no toca ningun
`chunk_uid` y no modifica el snapshot.

La columna "antes" no es una reconstruccion: es el texto que HybridChunker
produce para esa misma tabla, que es literalmente lo que hoy guarda
`chunks.contenido`.

Uso:

    python -m scripts.diagnostics.prototipo_tablas \
        --pdf data/raw/Transener_Calificacion_FIX.pdf \
        --excel data/quarantine/descartados/1Q26.xlsx \
        --hojas "EERR-C ing" "BCE ing"
"""

from __future__ import annotations

import argparse
import json
from importlib import metadata
from pathlib import Path

from multirag.ingestion.tablas.adaptadores import (
    segmentos_desde_docling,
    segmentos_desde_excel,
)
from multirag.ingestion.tablas.hechos import hechos_de_documento
from multirag.ingestion.tablas.modelo import EXTRACCION_VERSION
from multirag.paths import DATA_DIR, EXPERIMENTS_DIR


SALIDA_PREDETERMINADA = EXPERIMENTS_DIR / "prototipo_tablas"
CACHE_PREDETERMINADA = EXPERIMENTS_DIR / "auditoria_tablas" / "docling_export"

# How many facts of each segment to show in the report. The full set always
# goes to the JSONL; the report is for a human to read.
# [ES] Cuantos hechos de cada segmento se muestran en el informe. El conjunto
# completo siempre va al JSONL; el informe es para que lo lea una persona.
HECHOS_POR_SEGMENTO = 6


def version_de(paquete: str) -> str:
    try:
        return f"{paquete} {metadata.version(paquete)}"
    except metadata.PackageNotFoundError:
        return f"{paquete} (version desconocida)"


def entidades_declaradas(valores: list[str], entradas: list[Path]) -> dict[str, str]:
    """Read `--entidad`: either `archivo=Nombre`, or a bare name for a single file.

    Attaching one entity to every input would be wrong the moment two documents
    of different companies are processed in the same run.

    [ES] Lee `--entidad`: o `archivo=Nombre`, o un nombre suelto si hay un solo
    archivo.

    Pegarle una entidad a todas las entradas seria incorrecto apenas se procesen
    dos documentos de companias distintas en la misma corrida.
    """
    mapa: dict[str, str] = {}
    for valor in valores or []:
        if "=" in valor:
            archivo, nombre = valor.split("=", 1)
            mapa[archivo.strip()] = nombre.strip()
        elif len(entradas) == 1:
            mapa[entradas[0].name] = valor.strip()
        else:
            raise SystemExit(
                "Con mas de un archivo, --entidad necesita la forma "
                f"archivo=Nombre; se recibio {valor!r}"
            )
    return mapa


def identidad_de(ruta: Path, metadatos: Path, entidad: str | None) -> dict:
    """Resolve documentary identity from the catalog, by artifact fingerprint.

    The entity of the FIGURES is not read from `emisor_nombre`: in a rating
    report the issuer is the agency and the subject is the rated company, and
    reading one as the other would attribute Transener's cash flow to FIX SCR.
    While the catalog has no field for it, it stays null unless declared with
    `--entidad`.

    [ES] Resuelve la identidad documental desde el catalogo, por huella del
    artefacto.

    La entidad de las CIFRAS no se lee de `emisor_nombre`: en un informe de
    calificacion el emisor es la calificadora y el sujeto es la compania
    calificada, y leer uno por el otro le atribuiria a FIX SCR el flujo de caja
    de Transener. Mientras el catalogo no tenga un campo para eso, queda en null
    salvo que se declare con `--entidad`.
    """
    identidad = {"fuente": ruta.stem, "entidad": entidad}
    try:
        from multirag.ingestion.pipeline import resolver_identidad_documental
        from multirag.ingestion.vincular_identidad import (
            cargar_identidades_por_fuente,
        )

        curada = resolver_identidad_documental(
            ruta, cargar_identidades_por_fuente(metadatos)
        )
        identidad.update(
            {
                "document_id": curada.get("document_id"),
                "artifact_id": curada.get("artifact_id"),
                "fuente": curada.get("fuente", ruta.stem),
            }
        )
    except Exception as error:                                   # noqa: BLE001
        identidad["aviso"] = f"sin identidad curada: {error}"
    return identidad


def documento_docling(ruta: Path, cache: Path) -> dict:
    """Convert once, reuse afterwards. Same recipe as the ingestion pipeline.

    [ES] Convertir una vez, reutilizar despues. Misma receta que el pipeline de
    ingesta.
    """
    cache.mkdir(parents=True, exist_ok=True)
    destino = cache / f"{ruta.stem}.docling.json"
    if destino.is_file():
        return json.loads(destino.read_text(encoding="utf-8"))

    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    from multirag.ingestion.chunker import _necesita_ocr

    opciones = PdfPipelineOptions()
    opciones.do_ocr = _necesita_ocr(str(ruta))
    opciones.do_table_structure = True
    convertidor = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=opciones, backend=PyPdfiumDocumentBackend
            )
        }
    )
    resultado = convertidor.convert(str(ruta), raises_on_error=False)
    if resultado.status.name != "SUCCESS":
        raise RuntimeError(f"Conversion INCOMPLETA de {ruta}: {resultado.status.name}")

    documento = resultado.document.export_to_dict()
    destino.write_text(json.dumps(documento, ensure_ascii=False), encoding="utf-8")
    return documento


def linea_base(documento: dict) -> dict[str, list[str]]:
    """What today's pipeline stores for each table: the chunk text itself.

    [ES] Lo que el pipeline de hoy guarda para cada tabla: el texto del chunk.
    """
    from docling.chunking import HybridChunker
    from docling_core.transforms.chunker.tokenizer.huggingface import (
        HuggingFaceTokenizer,
    )
    from docling_core.types.doc.document import DoclingDocument

    from multirag.config import CHUNK_MAX_TOKENS, EMBEDDING_MODEL

    dl_doc = DoclingDocument.model_validate(documento)
    troceador = HybridChunker(
        tokenizer=HuggingFaceTokenizer.from_pretrained(
            model_name=EMBEDDING_MODEL, max_tokens=CHUNK_MAX_TOKENS
        )
    )
    por_tabla: dict[str, list[str]] = {}
    for ch in troceador.chunk(dl_doc=dl_doc):
        for item in ch.meta.doc_items or []:
            ref = getattr(item, "self_ref", "")
            if ref.startswith("#/tables/"):
                por_tabla.setdefault(ref, []).append(ch.text)
    return por_tabla


def bloque_de_segmento(segmento, hechos, antes: list[str] | None) -> list[str]:
    lineas = [
        f"### `{segmento.ancla}`",
        "",
        f"- **procedencia:** paginas {list(segmento.source_pages) or '—'}"
        + (f", hoja `{segmento.hoja}`" if segmento.hoja else ""),
        f"- **table_uid:** `{segmento.table_uid}`",
        f"- **table_segment_uid:** `{segmento.table_segment_uid}`",
        f"- **continuation_of:** "
        + (f"`{segmento.continuation_of}`" if segmento.continuation_of else "—"),
        f"- **banda de encabezado inferida:** {list(segmento.banda_encabezado) or 'ninguna'}",
        f"- **unidad:** {segmento.unidad.legible() or '—'} "
        f"(origen `{segmento.unidad.origen}`"
        + (f", evidencia `{segmento.unidad.evidencia_ref}`" if segmento.unidad.evidencia_ref else "")
        + ")",
        f"- **extraction_warnings:** {segmento.extraction_warnings or '—'}",
        f"- **reglas:** {[r for r in segmento.reglas if r.startswith('continuidad')] or '—'}",
        "",
    ]

    if antes is not None:
        lineas += ["**ANTES** — lo que hoy guarda `chunks.contenido`:", "", "```text"]
        lineas += [(t[:700] + (" […]" if len(t) > 700 else "")) for t in antes[:2]] or ["(sin chunk)"]
        lineas += ["```", ""]

    propios = [h for h in hechos if h.table_segment_uid == segmento.table_segment_uid]
    lineas += [
        f"**DESPUES** — hechos recuperables ({len(propios)} en total, "
        f"se muestran {min(len(propios), HECHOS_POR_SEGMENTO)}):",
        "",
        "```text",
    ]
    lineas += [f"{h.afirmacion()}   [confianza: {h.confianza}]" for h in propios[:HECHOS_POR_SEGMENTO]]
    lineas += ["```", ""]
    return lineas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pdf", nargs="*", type=Path, default=[])
    parser.add_argument("--excel", nargs="*", type=Path, default=[])
    parser.add_argument("--hojas", nargs="*", default=None)
    parser.add_argument(
        "--entidad",
        nargs="*",
        default=[],
        help="entidad de las CIFRAS, como archivo=Nombre (o un nombre suelto "
        "si se procesa un solo archivo)",
    )
    parser.add_argument("--metadatos", type=Path, default=None)
    parser.add_argument("--cache", type=Path, default=CACHE_PREDETERMINADA)
    parser.add_argument("--salida", type=Path, default=SALIDA_PREDETERMINADA)
    parser.add_argument(
        "--sin-linea-base",
        action="store_true",
        help="omite la columna ANTES (evita cargar el tokenizer del embedder)",
    )
    argumentos = parser.parse_args()

    if argumentos.metadatos is None:
        from multirag.ingestion.vincular_identidad import (
            RUTA_METADATOS_PREDETERMINADA,
        )

        argumentos.metadatos = RUTA_METADATOS_PREDETERMINADA

    entidades = entidades_declaradas(
        argumentos.entidad, list(argumentos.pdf) + list(argumentos.excel)
    )

    argumentos.salida.mkdir(parents=True, exist_ok=True)
    informe = [
        "# Prototipo de representacion table-aware",
        "",
        f"- receta de extraccion: `{EXTRACCION_VERSION}`",
        f"- corpus base: `{DATA_DIR}`",
        "- **de solo lectura**: no se conecto a la base, no se reingirio, "
        "no se modifico ningun `chunk_uid`.",
        "",
    ]
    todos = []

    for ruta in argumentos.pdf:
        identidad = identidad_de(ruta, argumentos.metadatos, entidades.get(ruta.name))
        documento = documento_docling(ruta, argumentos.cache)
        segmentos = segmentos_desde_docling(
            documento, version_de("docling"), identidad
        )
        hechos = hechos_de_documento(segmentos)
        todos += hechos
        antes = None if argumentos.sin_linea_base else linea_base(documento)

        informe += [
            f"## PDF — `{ruta.name}`",
            "",
            f"- identidad: `{identidad.get('document_id')}` / `{identidad.get('artifact_id')}`"
            + (f"  ⚠️ {identidad['aviso']}" if "aviso" in identidad else ""),
            f"- entidad de las cifras: {identidad.get('entidad') or '**no declarada**'}",
            f"- tablas detectadas: {len(segmentos)} — hechos emitidos: {len(hechos)}",
            "",
        ]
        for segmento in segmentos:
            informe += bloque_de_segmento(
                segmento, hechos, None if antes is None else antes.get(segmento.ancla, [])
            )

    for ruta in argumentos.excel:
        identidad = identidad_de(ruta, argumentos.metadatos, entidades.get(ruta.name))
        segmentos = segmentos_desde_excel(
            ruta,
            version_de("openpyxl"),
            identidad,
            tuple(argumentos.hojas) if argumentos.hojas else None,
        )
        hechos = hechos_de_documento(segmentos)
        todos += hechos
        informe += [
            f"## Planilla — `{ruta.name}`",
            "",
            "- leida con **openpyxl**, sin Docling y sin OCR.",
            f"- identidad: `{identidad.get('document_id')}` / `{identidad.get('artifact_id')}`"
            + (f"  ⚠️ {identidad['aviso']}" if "aviso" in identidad else ""),
            f"- bloques detectados: {len(segmentos)} — hechos emitidos: {len(hechos)}",
            "",
        ]
        for segmento in segmentos:
            informe += bloque_de_segmento(segmento, hechos, None)

    reparto = {}
    for hecho in todos:
        reparto[hecho.confianza] = reparto.get(hecho.confianza, 0) + 1
    informe += [
        "## Resumen",
        "",
        f"- hechos totales: **{len(todos)}**",
        f"- por confianza: {reparto or '—'}",
        f"- hechos con advertencia que limita el dato: "
        f"{sum(1 for h in todos if [a for a in h.extraction_warnings if not a.startswith('nota:')])}",
        f"- hechos donde nuestra inferencia de encabezado difiere de la del "
        f"parser: {sum(1 for h in todos if any(a.startswith('nota:encabezado_discrepa') for a in h.extraction_warnings))}",
        "",
        "El ultimo numero no es un defecto de la extraccion: mide cada cuanto "
        "las marcas de encabezado de Docling no coinciden con la inferencia "
        "propia. Es el hallazgo que motivo esta representacion, y se guarda "
        "para poder contarlo.",
        "",
    ]

    (argumentos.salida / "informe.md").write_text("\n".join(informe), encoding="utf-8")
    with (argumentos.salida / "hechos.jsonl").open("w", encoding="utf-8") as archivo:
        for hecho in todos:
            archivo.write(json.dumps(hecho.como_dict(), ensure_ascii=False) + "\n")

    print(f"informe -> {argumentos.salida / 'informe.md'}")
    print(f"hechos  -> {argumentos.salida / 'hechos.jsonl'} ({len(todos)} hechos)")


if __name__ == "__main__":
    main()
