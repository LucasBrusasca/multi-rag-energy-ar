"""Diagnostic audit of how table information survives the pipeline.

It answers one question: when a number loses its unit, its period or its
entity, WHERE was it lost? Four stages are traced:

1. the original document;
2. Docling's structured output, BEFORE HybridChunker;
3. the chunks produced and what got persisted;
4. what retrieval returns for a numeric question.

Each loss is classified:

- **A. OCR** — characters or digits misread.
- **B. Structure** — Docling produced the table but related cells or headers
  wrongly (a header row not flagged, two values merged into one cell).
- **C. Chunking / serialisation** — Docling HAD the relation and our pipeline
  dropped it.
- **D. Retrieval** — the representation was complete but the search did not
  bring it back.

The distinction that matters is B versus C: B is fixed by changing the parser,
C is fixed by changing our own code, and they are indistinguishable from the
chunk text alone. That is why this reads `resultado.document.tables` directly
and never assumes `ch.text` represents everything Docling knows.

STRICTLY READ-ONLY. It converts documents into a scratch directory, reads the
database and writes a report. It does not re-ingest, does not touch the UIDs,
does not modify the snapshot.

[ES] Auditoría diagnóstica de cómo sobrevive la información tabular al pipeline.

Responde una sola pregunta: cuando un número pierde su unidad, su período o su
entidad, ¿DÓNDE se perdió? Se rastrean cuatro etapas:

1. el documento original;
2. la salida estructurada de Docling, ANTES de HybridChunker;
3. los chunks producidos y lo que quedó persistido;
4. lo que devuelve la recuperación ante una pregunta numérica.

Cada pérdida se clasifica:

- **A. OCR** — caracteres o dígitos mal reconocidos.
- **B. Estructura** — Docling produjo la tabla pero relacionó mal celdas o
  encabezados (una fila de encabezado sin marcar, dos valores fusionados en una
  celda).
- **C. Chunking / serialización** — Docling TENÍA la relación y nuestro
  pipeline la perdió.
- **D. Retrieval** — la representación estaba completa pero la búsqueda no la
  recuperó.

La distinción que importa es B contra C: B se arregla cambiando el parser, C se
arregla cambiando nuestro propio código, y desde el texto del chunk son
indistinguibles. Por eso esto lee `resultado.document.tables` directamente y
nunca asume que `ch.text` representa todo lo que Docling sabe.

ESTRICTAMENTE DE SOLO LECTURA. Convierte documentos a un directorio de trabajo,
lee la base y escribe un informe. No reingiere, no toca los UID, no modifica el
snapshot.
"""

import argparse
import contextlib
import json
import re
from pathlib import Path

from multirag.config import CHUNK_MAX_TOKENS, EMBEDDING_MODEL
from multirag.db import conectar
from multirag.paths import DATA_DIR, EXPERIMENTS_DIR


CACHE = EXPERIMENTS_DIR / "auditoria_tablas" / "docling"

SALIDA_PREDETERMINADA = EXPERIMENTS_DIR / "auditoria_tablas" / "informe.md"


# Documents chosen to cover the requested variety, from smallest to largest.
# [ES] Documentos elegidos para cubrir la variedad pedida, de menor a mayor.
CASOS = (
    ("Transener_Calificacion_FIX.pdf", "PDF digital, informe de calificacion"),
    ("Pampa_EEFF_Consolidado_1Q2026.pdf", "PDF digital, estado contable"),
    ("MSU_ON_ClaseIV.pdf", "PDF digital, prospecto de ON"),
    ("Edenor_EEFF_Consolidado_2025_09.pdf", "PDF digital, estado contable (caso DOC-0004)"),
    ("TGS_EEFF_2025_09.pdf", "PDF digital, estado contable complejo"),
    ("Decreto_1398_1992_Reglamentario_Electrico.pdf", "PDF ESCANEADO (unico con OCR)"),
)


# Signals of the three pieces of context a number needs to be interpretable.
# [ES] Señales de las tres piezas de contexto que un número necesita para ser
# interpretable.
PATRON_UNIDAD = re.compile(
    r"millones|miles\s+de|\$\s*millones|en\s+pesos|moneda\s+constante|"
    r"expresad[oa]s?\s+en",
    re.IGNORECASE,
)

PATRON_PERIODO = re.compile(
    r"\b(19|20)\d{2}\b|\b\d{2}[/.]\d{2}[/.]\d{2,4}\b|"
    r"trimestre|ejercicio|per[ií]odo|meses",
    re.IGNORECASE,
)

PATRON_MONEDA = re.compile(
    r"pesos|\$|dolar|d[óo]lares|US\$|USD|ARS", re.IGNORECASE
)

# A cell holding two numbers separated by whitespace is two columns collapsed
# into one: a structure failure that our serialisation cannot undo.
# [ES] Una celda con dos números separados por espacio son dos columnas
# colapsadas en una: una falla de estructura que nuestra serialización no puede
# deshacer.
PATRON_VALORES_PEGADOS = re.compile(
    r"^\(?\d[\d.,]*\)?\s+\(?\d[\d.,]*\)?$"
)

# Replacement characters and mojibake: the fingerprint of an OCR or encoding
# failure, which is stage A and not ours.
# [ES] Caracteres de reemplazo y mojibake: la huella de una falla de OCR o de
# codificación, que es la etapa A y no la nuestra.
PATRON_OCR_SOSPECHOSO = re.compile(r"[�]|\bl\d{3,}|\bO\d{3,}")


@contextlib.contextmanager
def _cursor(conexion):
    """Yield a cursor, or None when there is no connection.

    [ES] Entrega un cursor, o None cuando no hay conexión.
    """
    if conexion is None:
        yield None
        return

    with conexion.cursor() as cursor:
        yield cursor


def convertir(ruta: Path, destino: Path, con_documento: bool = False):
    """Convert a document with Docling and cache its structure as JSON.

    The conversion uses the SAME options as the pipeline, otherwise the audit
    would describe a different parser than the one in production.

    [ES] Convierte un documento con Docling y cachea su estructura como JSON.

    La conversión usa las MISMAS opciones que el pipeline; si no, la auditoría
    describiría un parser distinto del que está en producción.
    """
    if destino.is_file() and not con_documento:
        return json.loads(destino.read_text(encoding="utf-8")), None

    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    from multirag.ingestion.chunker import _necesita_ocr

    ocr = _necesita_ocr(str(ruta))

    opciones = PdfPipelineOptions()
    opciones.do_ocr = ocr
    opciones.do_table_structure = True

    convertidor = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=opciones,
                backend=PyPdfiumDocumentBackend,
            )
        }
    )

    resultado = convertidor.convert(str(ruta), raises_on_error=False)

    documento = {
        "archivo": ruta.name,
        "ocr": ocr,
        "estado": resultado.status.name,
        "tablas": [],
        "textos": [
            {"self_ref": t.self_ref, "text": t.text}
            for t in resultado.document.texts
        ],
    }

    for tabla in resultado.document.tables:
        datos = tabla.data
        documento["tablas"].append(
            {
                "self_ref": tabla.self_ref,
                "caption": tabla.caption_text(resultado.document) or "",
                "num_rows": datos.num_rows,
                "num_cols": datos.num_cols,
                "paginas": sorted(
                    {p.page_no for p in (tabla.prov or [])}
                ),
                "celdas": [
                    {
                        "fila": c.start_row_offset_idx,
                        "fila_fin": c.end_row_offset_idx,
                        "col": c.start_col_offset_idx,
                        "col_fin": c.end_col_offset_idx,
                        "col_span": c.col_span,
                        "row_span": c.row_span,
                        "es_encabezado_col": bool(c.column_header),
                        "es_encabezado_fila": bool(c.row_header),
                        "es_seccion": bool(c.row_section),
                        "texto": c.text,
                    }
                    for c in datos.table_cells
                ],
            }
        )

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(documento, ensure_ascii=False),
        encoding="utf-8",
    )

    return documento, resultado.document


def trocear(documento):
    """Run the project's chunker over an ALREADY converted document.

    It receives the document instead of a path so the audit converts each file
    once. Converting twice would double the cost and, worse, would risk
    auditing a different parse than the one described in stage 2.

    [ES] Corre el chunker del proyecto sobre un documento YA convertido.

    Recibe el documento en lugar de una ruta para que la auditoria convierta
    cada archivo una sola vez. Convertir dos veces duplicaria el costo y, peor,
    arriesgaria auditar un parseo distinto del descrito en la etapa 2.
    """
    from docling.chunking import HybridChunker
    from docling_core.transforms.chunker.tokenizer.huggingface import (
        HuggingFaceTokenizer,
    )

    troceador = HybridChunker(
        tokenizer=HuggingFaceTokenizer.from_pretrained(
            model_name=EMBEDDING_MODEL,
            max_tokens=CHUNK_MAX_TOKENS,
        )
    )

    return [
        {
            "texto": ch.text,
            "titulo": (ch.meta.headings or [""])[-1],
            "refs": [it.self_ref for it in (ch.meta.doc_items or [])],
        }
        for ch in troceador.chunk(dl_doc=documento)
    ]


def analizar_tabla(tabla: dict) -> dict:
    """Determine what Docling knows about one table, and what it got wrong.

    [ES] Determina qué sabe Docling de una tabla, y qué relacionó mal.
    """
    celdas = tabla["celdas"]
    textos = [c["texto"] for c in celdas]
    todo = " ".join(textos)

    encabezados_col = [c for c in celdas if c["es_encabezado_col"]]
    encabezados_fila = [c for c in celdas if c["es_encabezado_fila"]]

    # A header row that Docling did not flag: the first row holding dates while
    # no cell of that row is marked as a column header.
    # [ES] Una fila de encabezado que Docling no marcó: la primera fila con
    # fechas sin que ninguna celda de esa fila esté marcada como encabezado.
    filas_con_fecha = {
        c["fila"]
        for c in celdas
        if PATRON_PERIODO.search(c["texto"] or "")
    }
    filas_marcadas = {c["fila"] for c in encabezados_col}
    fechas_sin_marcar = sorted(filas_con_fecha - filas_marcadas)

    pegadas = [
        c["texto"]
        for c in celdas
        if PATRON_VALORES_PEGADOS.match((c["texto"] or "").strip())
    ]

    sospecha_ocr = [
        c["texto"]
        for c in celdas
        if PATRON_OCR_SOSPECHOSO.search(c["texto"] or "")
    ]

    return {
        "self_ref": tabla["self_ref"],
        "paginas": tabla["paginas"],
        "filas": tabla["num_rows"],
        "columnas": tabla["num_cols"],
        "celdas": len(celdas),
        "caption": tabla["caption"],
        "unidad_en_tabla": bool(PATRON_UNIDAD.search(todo)),
        "periodo_en_tabla": bool(PATRON_PERIODO.search(todo)),
        "moneda_en_tabla": bool(PATRON_MONEDA.search(todo)),
        "encabezados_col": len(encabezados_col),
        "encabezados_fila": len(encabezados_fila),
        "fechas_sin_marcar": fechas_sin_marcar,
        "valores_pegados": pegadas[:3],
        "n_valores_pegados": len(pegadas),
        "sospecha_ocr": sospecha_ocr[:3],
        "n_sospecha_ocr": len(sospecha_ocr),
        "abarca_paginas": len(tabla["paginas"]) > 1,
    }


def analizar_chunks(chunks, self_ref: str) -> dict:
    """What the chunks that contain this table preserve of its context.

    [ES] Qué conservan de su contexto los chunks que contienen esta tabla.
    """
    propios = [c for c in chunks if self_ref in c["refs"]]

    if not propios:
        return {"chunks": 0}

    texto = " ".join(c["texto"] for c in propios)
    titulos = " ".join(c["titulo"] or "" for c in propios)

    return {
        "chunks": len(propios),
        "unidad_en_chunk": bool(PATRON_UNIDAD.search(texto)),
        "unidad_en_titulo": bool(PATRON_UNIDAD.search(titulos)),
        "periodo_en_chunk": bool(PATRON_PERIODO.search(texto)),
        "periodo_en_titulo": bool(PATRON_PERIODO.search(titulos)),
        "muestra": " ".join(propios[0]["texto"].split())[:180],
    }


def clasificar(tabla: dict, chunk: dict) -> list[str]:
    """Assign the failure classes of one case.

    [ES] Asigna las clases de falla de un caso.
    """
    fallas = []

    if tabla["n_sospecha_ocr"]:
        fallas.append("A")

    if tabla["fechas_sin_marcar"] or tabla["n_valores_pegados"]:
        fallas.append("B")

    # C is the decisive one: Docling had it and the chunk does not.
    # [ES] C es la decisiva: Docling la tenía y el chunk no.
    if chunk.get("chunks"):
        perdio_unidad = tabla["unidad_en_tabla"] and not (
            chunk.get("unidad_en_chunk") or chunk.get("unidad_en_titulo")
        )
        perdio_periodo = tabla["periodo_en_tabla"] and not (
            chunk.get("periodo_en_chunk") or chunk.get("periodo_en_titulo")
        )

        if perdio_unidad or perdio_periodo:
            fallas.append("C")

    return fallas or ["ok"]


def persistido(cursor, fuente: str) -> dict:
    """What survived into the database for this source.

    Returns an empty result when there is no database: stage 3 is reported as
    unavailable instead of being silently counted as zero.

    [ES] Qué sobrevivió en la base para esta fuente.

    Devuelve un resultado vacío cuando no hay base: la etapa 3 se informa como
    no disponible en lugar de contarse en silencio como cero.
    """
    if cursor is None:
        return {"chunks": None, "tabulares": None, "con_unidad": None}

    # The literal % of the LIKE patterns must be doubled: psycopg2 reads a
    # single % as the start of a placeholder when the query carries parameters.
    # [ES] Los % literales de los LIKE tienen que ir duplicados: psycopg2 lee un
    # % suelto como inicio de un marcador cuando la consulta lleva parámetros.
    cursor.execute(
        """
        SELECT count(*),
               count(*) FILTER (
                   WHERE contenido LIKE '%%= %%' AND contenido LIKE '%%,%%'
               ),
               count(*) FILTER (
                   WHERE contenido ILIKE '%%millones%%'
                      OR contenido ILIKE '%%moneda constante%%'
               )
        FROM chunks WHERE fuente = %s
        """,
        (fuente,),
    )

    total, tabulares, con_unidad = cursor.fetchone()

    return {
        "chunks": total,
        "tabulares": tabulares,
        "con_unidad": con_unidad,
    }


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.

    [ES] Construye la interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Auditoría diagnóstica de la representación tabular. "
            "Solo lectura: no reingiere ni modifica el snapshot."
        )
    )
    parser.add_argument(
        "--documentos",
        nargs="*",
        default=None,
        help="Archivos a auditar. Por defecto, el conjunto representativo.",
    )
    parser.add_argument(
        "--tablas-por-documento",
        type=int,
        default=3,
        help="Cuántas tablas auditar por documento.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=SALIDA_PREDETERMINADA,
        help="Informe markdown a generar.",
    )
    parser.add_argument(
        "--solo-convertir",
        action="store_true",
        help="Solo convierte y cachea, sin analizar.",
    )
    return parser


def main() -> None:
    """Run the audit and write the report.

    [ES] Corre la auditoría y escribe el informe.
    """
    argumentos = construir_parser().parse_args()

    archivos = argumentos.documentos or [nombre for nombre, _ in CASOS]
    descripcion = dict(CASOS)

    filas = []
    resumen = {"A": 0, "B": 0, "C": 0, "D": 0, "ok": 0}

    # Stages 1 to 3 do not need the database: they live in the document and in
    # Docling. Only the "persisted" column does. If PostgreSQL is down the audit
    # continues and says so, instead of losing the whole run.
    # [ES] Las etapas 1 a 3 no necesitan la base: viven en el documento y en
    # Docling. Solo la columna "persistido" la usa. Si PostgreSQL esta caido la
    # auditoria continua y lo declara, en lugar de perder toda la corrida.
    try:
        conexion = conectar()
    except Exception as error:
        print(f"[auditoria] sin base ({type(error).__name__}): "
              "se auditan las etapas 1-3; la columna 'persistido' queda vacia.")
        conexion = None

    try:
        with _cursor(conexion) as cursor:
            if cursor is not None:
                cursor.execute("SET TRANSACTION READ ONLY")

            for nombre in archivos:
                ruta = DATA_DIR / "raw" / nombre

                if not ruta.is_file():
                    print(f"[auditoria] no existe: {ruta}")
                    continue

                print(f"[auditoria] {nombre} ...", flush=True)

                documento, vivo = convertir(
                    ruta, CACHE / f"{ruta.stem}.json", con_documento=True
                )

                if documento["estado"] != "SUCCESS":
                    print(f"  conversion {documento['estado']}")

                if not documento["tablas"]:
                    print("  sin tablas")
                    continue

                chunks = trocear(vivo)
                base = persistido(cursor, ruta.stem)

                elegidas = sorted(
                    documento["tablas"],
                    key=lambda t: -len(t["celdas"]),
                )[: argumentos.tablas_por_documento]

                for tabla in elegidas:
                    analisis = analizar_tabla(tabla)
                    enchunk = analizar_chunks(chunks, tabla["self_ref"])
                    clases = clasificar(analisis, enchunk)

                    for clase in clases:
                        resumen[clase] = resumen.get(clase, 0) + 1

                    filas.append(
                        {
                            "archivo": nombre,
                            "descripcion": descripcion.get(nombre, ""),
                            "ocr": documento["ocr"],
                            "tabla": analisis,
                            "chunk": enchunk,
                            "clases": clases,
                            "base": base,
                        }
                    )

        if conexion is not None:
            conexion.rollback()
    finally:
        if conexion is not None:
            conexion.close()

    salida = Path(argumentos.salida).resolve()
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(
        redactar_informe(filas, resumen),
        encoding="utf-8",
        newline="\n",
    )

    print(f"\ntablas auditadas: {len(filas)}")
    print(f"clases: {resumen}")
    print(f"informe: {salida}")


def redactar_informe(filas, resumen) -> str:
    """Write the report.

    [ES] Redacta el informe.
    """
    lineas = [
        "# Auditoria diagnostica de la representacion tabular",
        "",
        "Solo lectura. No se reingirio, no se modificaron UID ni el snapshot.",
        "",
        "## Diagnostico agregado",
        "",
        "| clase | que significa | tablas |",
        "|---|---|---|",
        f"| A | OCR: caracteres o digitos mal reconocidos | {resumen.get('A', 0)} |",
        f"| B | Estructura: Docling relaciono mal celdas o encabezados | {resumen.get('B', 0)} |",
        f"| C | Chunking: Docling la tenia y el pipeline la perdio | {resumen.get('C', 0)} |",
        f"| D | Retrieval: representacion completa, busqueda fallida | {resumen.get('D', 0)} |",
        f"| ok | sin perdida detectada | {resumen.get('ok', 0)} |",
        "",
        "## Casos auditados",
        "",
    ]

    for fila in filas:
        t = fila["tabla"]
        c = fila["chunk"]

        lineas.append(f"### {fila['archivo']} - {t['self_ref']}")
        lineas.append("")
        lineas.append(f"_{fila['descripcion']}_ - OCR: {'si' if fila['ocr'] else 'no'}")
        lineas.append("")
        lineas.append("| que | valor |")
        lineas.append("|---|---|")
        lineas.append(f"| paginas | {t['paginas']}{' (abarca varias)' if t['abarca_paginas'] else ''} |")
        lineas.append(f"| dimensiones | {t['filas']} x {t['columnas']}, {t['celdas']} celdas |")
        lineas.append(f"| caption | {t['caption'] or '(sin caption)'} |")
        lineas.append(f"| **Docling: unidad en la tabla** | {'SI' if t['unidad_en_tabla'] else 'NO'} |")
        lineas.append(f"| **Docling: periodo en la tabla** | {'SI' if t['periodo_en_tabla'] else 'NO'} |")
        lineas.append(f"| Docling: moneda en la tabla | {'SI' if t['moneda_en_tabla'] else 'NO'} |")
        lineas.append(f"| celdas marcadas encabezado de columna | {t['encabezados_col']} |")
        lineas.append(f"| celdas marcadas encabezado de fila | {t['encabezados_fila']} |")
        lineas.append(f"| filas con fecha SIN marcar como encabezado | {t['fechas_sin_marcar'] or 'ninguna'} |")
        lineas.append(f"| celdas con dos valores pegados | {t['n_valores_pegados']} {t['valores_pegados'] or ''} |")
        lineas.append(f"| celdas con sospecha de OCR | {t['n_sospecha_ocr']} {t['sospecha_ocr'] or ''} |")
        lineas.append(f"| chunks que contienen la tabla | {c.get('chunks', 0)} |")
        lineas.append(f"| **chunk: conserva la unidad** | {'SI' if c.get('unidad_en_chunk') or c.get('unidad_en_titulo') else 'NO'} |")
        lineas.append(f"| **chunk: conserva el periodo** | {'SI' if c.get('periodo_en_chunk') or c.get('periodo_en_titulo') else 'NO'} |")
        lineas.append(f"| persistido en la base (fuente) | " + (f"{fila['base']['chunks']} chunks, {fila['base']['tabulares']} tabulares, {fila['base']['con_unidad']} con unidad |" if fila['base']['chunks'] is not None else "base no disponible durante la auditoria |"))
        lineas.append(f"| **clasificacion** | **{', '.join(fila['clases'])}** |")
        lineas.append("")

        if c.get("muestra"):
            lineas.append(f"Muestra de lo que quedo en el chunk:")
            lineas.append("")
            lineas.append(f"> {c['muestra']}...")
            lineas.append("")

    return "\n".join(lineas)


if __name__ == "__main__":
    main()
