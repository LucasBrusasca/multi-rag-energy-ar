"""Ingest cataloged corpus artifacts and persist their classified chunks.

Every ingested artifact must already have a curated documentary identity.

[ES] Ingiere artefactos catalogados del corpus y persiste sus chunks
clasificados.

Todo artefacto ingerido debe contar previamente con una identidad documental
curada.
"""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from psycopg2.extras import execute_values


from multirag.db import conectar
from multirag.ingestion.catalogo import calcular_sha256, construir_artifact_id
from multirag.ingestion.vincular_identidad import (
    RUTA_METADATOS_PREDETERMINADA,
    cargar_identidades_por_fuente,
)


def resolver_identidad_documental(
    ruta: Path,
    identidades_por_fuente: dict[str, dict[str, str]],
) -> dict[str, str]:
    """Resolve documentary identity from the exact binary artifact.

    The filename is not used as identity. The lookup is performed with the
    artifact_id derived from the complete SHA-256 fingerprint.

    [ES] Resuelve la identidad documental a partir del artefacto binario
    exacto.

    El nombre del archivo no se utiliza como identidad. La búsqueda se
    realiza mediante el artifact_id derivado de la huella SHA-256 completa.
    """

    ruta = ruta.resolve()

    if not ruta.is_file():
        raise FileNotFoundError(
            f"No existe el archivo que se quiere ingerir: {ruta}"
        )

    huella_sha256 = calcular_sha256(ruta)
    artifact_id = construir_artifact_id(huella_sha256)

    coincidencias = [
        identidad
        for identidad in identidades_por_fuente.values()
        if identidad["artifact_id"] == artifact_id
    ]

    if not coincidencias:
        raise ValueError(
            "El artefacto no tiene identidad documental curada. "
            "Primero debe incorporarse al catálogo: "
            f"{ruta.name} ({artifact_id})"
        )

    if len(coincidencias) > 1:
        raise ValueError(
            "El artifact_id aparece asociado con más de una identidad: "
            f"{artifact_id}"
        )

    return coincidencias[0]


# Order of the values in the INSERT. Declared once so the row, the column list
# and the template cannot drift apart silently.
# [ES] Orden de los valores del INSERT. Declarado una sola vez para que la fila,
# la lista de columnas y el template no puedan separarse en silencio.
COLUMNAS_INSERT = (
    "silo",
    "silo_scores",
    "titulo",
    "contenido",
    "embedding",
    "fuente",
    "instrument_id",
    "document_id",
    "artifact_id",
    "hierarchy",
    "chunk_uid",
    "paginas",
    "doc_refs",
    "offset_desde",
    "offset_hasta",
)


def _rango_de_paginas(procedencia: dict) -> list[int]:
    """The pages a chunk occupies, as a sorted list without repetitions.

    A merged chunk can span several pages, and a repeated text appears on
    several. Storing a list instead of a single number is what lets the citation
    say "pages 3 and 12" instead of silently choosing one.

    [ES] Las páginas que ocupa un chunk, como lista ordenada y sin repetir.

    Un chunk fusionado puede abarcar varias páginas, y un texto repetido aparece
    en varias. Guardar una lista en lugar de un número único es lo que permite
    que la cita diga «páginas 3 y 12» en vez de elegir una en silencio.
    """
    desde = procedencia.get("pagina_desde")
    hasta = procedencia.get("pagina_hasta")

    if desde is None and hasta is None:
        return []

    if desde is None:
        desde = hasta

    if hasta is None:
        hasta = desde

    return list(range(int(desde), int(hasta) + 1))


def _acumular_procedencia(fila: dict, procedencia: dict) -> None:
    """Merge into an existing row the location of a repeated occurrence.

    [ES] Fusiona en una fila existente la ubicación de una aparición repetida.
    """
    for pagina in _rango_de_paginas(procedencia):
        if pagina not in fila["paginas"]:
            fila["paginas"].append(pagina)

    fila["paginas"].sort()

    for ref in procedencia["doc_refs"]:
        if ref not in fila["doc_refs"]:
            fila["doc_refs"].append(ref)

    # The offsets keep the FIRST occurrence: they describe a position in the
    # reading order, and a repeated text has more than one. The full set of
    # locations lives in `paginas` and `doc_refs`.
    # [ES] Los offsets conservan la PRIMERA aparición: describen una posición en
    # el orden de lectura, y un texto repetido tiene más de una. El conjunto
    # completo de ubicaciones vive en `paginas` y `doc_refs`.


def guardar_chunks(
    chunks: list[dict],
    conexion,
    identidad: dict[str, str],
) -> int:
    """Persist chunks with their stable documentary identity.

    The operation is idempotent for the same artifact: its previous chunks
    are replaced atomically. Exact intra-artifact duplicates are discarded.

    [ES] Persiste chunks junto con su identidad documental estable.

    La operación es idempotente para un mismo artefacto: sus chunks previos
    se reemplazan atómicamente. Los duplicados exactos dentro del artefacto
    se descartan.
    """

    fuente = identidad["fuente"]
    instrument_id = identidad["instrument_id"]
    document_id = identidad["document_id"]
    artifact_id = identidad["artifact_id"]

    filas = []
    # chunk_uid -> position in `filas`, to merge the provenance of a repeated
    # text instead of discarding it.
    # [ES] chunk_uid -> posición en `filas`, para fusionar la procedencia de un
    # texto repetido en lugar de descartarlo.
    vistos: dict[str, int] = {}
    repetidos = 0

    for chunk in chunks:
        contenido = chunk["content"]
        hierarchy = chunk["hierarchy"]

        chunk_uid = hashlib.sha256(
            (
                f"{fuente}|"
                f"{'/'.join(hierarchy)}|"
                f"{contenido}"
            ).encode("utf-8")
        ).hexdigest()

        procedencia = {
            "pagina_desde": chunk.get("pagina_desde"),
            "pagina_hasta": chunk.get("pagina_hasta"),
            "doc_refs": list(chunk.get("doc_refs") or []),
            "offset_desde": chunk.get("offset_desde"),
            "offset_hasta": chunk.get("offset_hasta"),
        }

        if chunk_uid in vistos:
            # The same text under the same source and section appears more than
            # once — a repeated header, an identical table row on two pages.
            # Discarding the second one loses WHERE it also appeared, and the
            # citation would then point only at the first occurrence.
            #
            # The chunk is not duplicated: its provenance is. It is the same
            # principle already adopted for domains — one chunk, several
            # relations — applied to location instead of to meaning.
            #
            # [ES] El mismo texto bajo la misma fuente y sección aparece más de
            # una vez: un encabezado repetido, una fila de tabla idéntica en dos
            # páginas. Descartar la segunda pierde DÓNDE apareció también, y la
            # cita quedaría apuntando solo a la primera aparición.
            #
            # No se duplica el chunk: se acumula su procedencia. Es el mismo
            # principio ya adoptado para los dominios —un chunk, varias
            # relaciones— aplicado a la ubicación en lugar de al significado.
            repetidos += 1
            _acumular_procedencia(filas[vistos[chunk_uid]], procedencia)
            continue

        vistos[chunk_uid] = len(filas)

        filas.append(
            {
                "silo": chunk["silo"],
                "silo_scores": json.dumps(chunk["silo_scores"]),
                "titulo": chunk["title"],
                "contenido": contenido,
                "embedding": (
                    "["
                    + ",".join(
                        map(str, chunk["embedding"])
                    )
                    + "]"
                ),
                "fuente": fuente,
                "instrument_id": instrument_id,
                "document_id": document_id,
                "artifact_id": artifact_id,
                "hierarchy": hierarchy,
                "chunk_uid": chunk_uid,
                "paginas": (
                    _rango_de_paginas(procedencia)
                ),
                "doc_refs": procedencia["doc_refs"],
                "offset_desde": procedencia["offset_desde"],
                "offset_hasta": procedencia["offset_hasta"],
            }
        )

    if not filas:
        raise ValueError(
            f"No se generaron chunks persistibles para {fuente}."
        )

    if repetidos:
        print(
            f"[pipeline] {repetidos} texto(s) repetido(s) en '{fuente}': "
            f"se fusionó su procedencia, no se descartaron."
        )

    with conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM chunks
                WHERE artifact_id = %s
                """,
                (artifact_id,),
            )

            execute_values(
                cursor,
                """
                INSERT INTO chunks (
                    silo,
                    silo_scores,
                    titulo,
                    contenido,
                    embedding,
                    fuente,
                    instrument_id,
                    document_id,
                    artifact_id,
                    hierarchy,
                    chunk_uid,
                    paginas,
                    doc_refs,
                    offset_desde,
                    offset_hasta
                )
                VALUES %s
                """,
                [
                    tuple(fila[columna] for columna in COLUMNAS_INSERT)
                    for fila in filas
                ],
                template=(
                    "("
                    "%s, %s::jsonb, %s, %s, %s::vector, "
                    "%s, %s, %s, %s, %s::text[], %s, "
                    "%s::integer[], %s::text[], %s, %s"
                    ")"
                ),
            )

    return len(filas)


def cargar_documento(
    ruta: Path,
    identidad: dict[str, str],
) -> None:
    """Run the complete ingestion pipeline for a cataloged artifact.

    [ES] Ejecuta el pipeline completo de ingesta para un artefacto
    catalogado.
    """

    from multirag.ingestion.chunker import chunk_with_docling
    from multirag.ingestion.embedder import embed_chunks
    from multirag.orchestration.clasificador import clasificar_vector

    fuente = identidad["fuente"]

    chunks = chunk_with_docling(
        str(ruta),
        source=fuente,
    )
    chunks = embed_chunks(chunks)

    for chunk in chunks:
        clasificacion = clasificar_vector(
            chunk["embedding"]
        )
        chunk["silo"] = clasificacion["silo"]
        chunk["silo_scores"] = clasificacion["silo_scores"]

    reparto = Counter(
        chunk["silo"]
        for chunk in chunks
    )
    print(f"Reparto por silo: {dict(reparto)}")

    conexion = conectar()

    try:
        cantidad = guardar_chunks(
            chunks=chunks,
            conexion=conexion,
            identidad=identidad,
        )
        print(
            f"OK: {cantidad} chunks de '{fuente}' guardados "
            f"con document_id={identidad['document_id']}."
        )
    finally:
        conexion.close()


def construir_parser() -> argparse.ArgumentParser:
    """Build an explicit ingestion command-line contract.

    [ES] Construye un contrato explicito de linea de comandos para la ingesta.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Ingiere artefactos con identidad documental previamente curada."
        )
    )
    parser.add_argument(
        "--metadatos",
        type=Path,
        default=RUTA_METADATOS_PREDETERMINADA,
        help=(
            "CSV de identidades documentales. Por defecto utiliza "
            "data/catalog/metadatos_curados.csv."
        ),
    )
    parser.add_argument(
        "documentos",
        type=Path,
        nargs="+",
        help="Uno o mas artefactos catalogados para ingerir.",
    )
    return parser


def main() -> None:
    """Ingest every cataloged artifact supplied on the command line.

    [ES] Ingiere cada artefacto catalogado recibido por línea de comandos.
    """

    argumentos = construir_parser().parse_args()

    identidades_por_fuente = cargar_identidades_por_fuente(
        argumentos.metadatos
    )

    fallidos = []

    for documento in argumentos.documentos:
        ruta = documento.resolve()
        print(f"\n=== {ruta.name} ===")

        try:
            identidad = resolver_identidad_documental(
                ruta=ruta,
                identidades_por_fuente=identidades_por_fuente,
            )
            cargar_documento(
                ruta=ruta,
                identidad=identidad,
            )
        except Exception as error:
            print(
                f"[pipeline] FALLÓ '{ruta.name}': {error}"
            )
            fallidos.append(ruta.name)

    if fallidos:
        print(
            f"\n[pipeline] {len(fallidos)} documento(s) "
            f"no ingresaron: {fallidos}"
        )


if __name__ == "__main__":
    main()
