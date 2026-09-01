"""Build a blinded review worksheet for context-policy disagreements.

The worksheet selects decisions changed by a paired comparison and can include
additional explicitly requested chunks. Model predictions, stored silos and
document identities are excluded from the reviewer-facing CSV.

[ES] Construye una planilla ciega para revisar desacuerdos entre políticas.

La planilla selecciona decisiones modificadas por una comparación pareada y
permite incluir chunks adicionales explícitos. El CSV no expone predicciones,
silos persistidos ni identidades documentales.
"""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


CAMPOS_SALIDA = (
    "version_revision",
    "orden_revision",
    "chunk_uid",
    "titulo_objetivo",
    "contenido_objetivo",
    "titulo_anterior",
    "contenido_anterior",
    "titulo_siguiente",
    "contenido_siguiente",
    "estado_asignacion_referencia",
    "dominios_referencia",
    "materialidad_referencia",
    "justificacion_referencia",
    "requiere_revision_experta",
    "anotador",
    "fecha_revision",
)


def cargar_objeto_json(
    ruta: Path,
    descripcion: str,
) -> dict[str, object]:
    """Load one required JSON object.

    [ES] Carga un objeto JSON requerido.
    """
    ruta_resuelta = ruta.resolve()

    if not ruta_resuelta.is_file():
        raise FileNotFoundError(
            f"No existe {descripcion}: {ruta_resuelta}"
        )

    try:
        objeto = json.loads(
            ruta_resuelta.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            f"{descripcion} no contiene JSON válido: {error}"
        ) from error

    if not isinstance(objeto, dict):
        raise ValueError(
            f"La raíz de {descripcion} debe ser un objeto JSON."
        )

    return objeto


def cargar_transiciones(
    comparacion: dict[str, object],
) -> list[dict[str, object]]:
    """Validate and return paired comparison transitions.

    [ES] Valida y devuelve las transiciones de la comparación.
    """
    bloque_comparacion = comparacion.get("comparacion")

    if not isinstance(bloque_comparacion, dict):
        raise ValueError(
            "El informe no contiene el bloque 'comparacion'."
        )

    transiciones = bloque_comparacion.get("transiciones")

    if not isinstance(transiciones, list) or not transiciones:
        raise ValueError(
            "La comparación no contiene transiciones."
        )

    chunk_uids: set[str] = set()

    for numero, transicion in enumerate(
        transiciones,
        start=1,
    ):
        if not isinstance(transicion, dict):
            raise ValueError(
                f"La transición {numero} no es un objeto."
            )

        chunk_uid = transicion.get("chunk_uid")

        if not isinstance(chunk_uid, str) or not chunk_uid.strip():
            raise ValueError(
                f"La transición {numero} no tiene chunk_uid válido."
            )

        if chunk_uid in chunk_uids:
            raise ValueError(
                f"chunk_uid repetido en transiciones: {chunk_uid}"
            )

        if not isinstance(
            transicion.get("cambio_etiqueta"),
            bool,
        ):
            raise ValueError(
                f"La transición {numero} no declara cambio_etiqueta."
            )

        if not isinstance(
            transicion.get("cambio_revision"),
            bool,
        ):
            raise ValueError(
                f"La transición {numero} no declara cambio_revision."
            )

        chunk_uids.add(chunk_uid)

    return transiciones


def cargar_chunks_contexto(
    informe: dict[str, object],
) -> list[dict[str, object]]:
    """Validate chunks used to reconstruct documentary adjacency.

    [ES] Valida chunks para reconstruir la vecindad documental.
    """
    chunks = informe.get("chunks")

    if not isinstance(chunks, list) or not chunks:
        raise ValueError(
            "El informe de contexto no contiene chunks."
        )

    campos_requeridos = {
        "chunk_uid",
        "document_id",
        "id_db",
        "titulo",
        "contenido",
    }
    chunk_uids: set[str] = set()

    for numero, chunk in enumerate(
        chunks,
        start=1,
    ):
        if not isinstance(chunk, dict):
            raise ValueError(
                f"El chunk {numero} no es un objeto."
            )

        faltantes = campos_requeridos.difference(chunk)

        if faltantes:
            raise ValueError(
                f"Al chunk {numero} le faltan campos: "
                f"{sorted(faltantes)}"
            )

        chunk_uid = chunk["chunk_uid"]

        if not isinstance(chunk_uid, str) or not chunk_uid.strip():
            raise ValueError(
                f"El chunk {numero} tiene chunk_uid inválido."
            )

        if chunk_uid in chunk_uids:
            raise ValueError(
                f"chunk_uid repetido en contexto: {chunk_uid}"
            )

        if not isinstance(chunk["id_db"], int):
            raise ValueError(
                f"El chunk {numero} tiene id_db inválido."
            )

        if (
            not isinstance(chunk["contenido"], str)
            or not chunk["contenido"].strip()
        ):
            raise ValueError(
                f"El chunk {numero} no contiene texto."
            )

        chunk_uids.add(chunk_uid)

    return chunks


def seleccionar_chunk_uids(
    transiciones: list[dict[str, object]],
    adicionales: list[str],
) -> tuple[set[str], set[str]]:
    """Select changed decisions plus explicit additional chunks.

    [ES] Selecciona decisiones modificadas y chunks adicionales.
    """
    seleccion_por_cambio = {
        str(transicion["chunk_uid"])
        for transicion in transiciones
        if (
            transicion["cambio_etiqueta"]
            or transicion["cambio_revision"]
        )
    }

    adicionales_limpios = {
        chunk_uid.strip()
        for chunk_uid in adicionales
        if chunk_uid.strip()
    }

    if len(adicionales_limpios) != len(adicionales):
        raise ValueError(
            "Los chunk_uid adicionales no pueden estar vacíos "
            "ni repetirse."
        )

    return (
        seleccion_por_cambio,
        adicionales_limpios,
    )


def construir_vecindad(
    chunks: list[dict[str, object]],
) -> dict[str, dict[str, dict[str, object] | None]]:
    """Build previous and next neighbours within each document.

    [ES] Construye vecinos anterior y siguiente dentro de cada documento.
    """
    por_documento: dict[str, list[dict[str, object]]] = {}

    for chunk in chunks:
        document_id = str(chunk["document_id"])
        por_documento.setdefault(
            document_id,
            [],
        ).append(chunk)

    vecindad = {}

    for chunks_documento in por_documento.values():
        chunks_ordenados = sorted(
            chunks_documento,
            key=lambda chunk: int(chunk["id_db"]),
        )

        for indice, chunk in enumerate(chunks_ordenados):
            anterior = (
                chunks_ordenados[indice - 1]
                if indice > 0
                else None
            )
            siguiente = (
                chunks_ordenados[indice + 1]
                if indice < len(chunks_ordenados) - 1
                else None
            )

            vecindad[str(chunk["chunk_uid"])] = {
                "anterior": anterior,
                "siguiente": siguiente,
            }

    return vecindad


def calcular_clave_ciega(
    version_revision: str,
    chunk_uid: str,
) -> str:
    """Return a deterministic blinded ordering key.

    [ES] Devuelve una clave determinista de ordenamiento ciego.
    """
    contenido = (
        f"{version_revision}|{chunk_uid}"
    ).encode("utf-8")

    return hashlib.sha256(contenido).hexdigest()


def construir_planilla(
    transiciones: list[dict[str, object]],
    chunks: list[dict[str, object]],
    adicionales: list[str],
    version_revision: str,
) -> tuple[list[dict[str, object]], int, int]:
    """Build blinded review rows without model predictions.

    [ES] Construye filas ciegas sin predicciones del modelo.
    """
    version_limpia = version_revision.strip()

    if not version_limpia:
        raise ValueError(
            "La versión de revisión no puede estar vacía."
        )

    if "\n" in version_limpia or "\r" in version_limpia:
        raise ValueError(
            "La versión no puede contener saltos de línea."
        )

    seleccion_cambios, seleccion_adicional = (
        seleccionar_chunk_uids(
            transiciones=transiciones,
            adicionales=adicionales,
        )
    )
    seleccion_total = seleccion_cambios.union(
        seleccion_adicional
    )

    chunks_por_uid = {
        str(chunk["chunk_uid"]): chunk
        for chunk in chunks
    }
    faltantes = sorted(
        seleccion_total.difference(chunks_por_uid)
    )

    if faltantes:
        raise ValueError(
            "No existe contexto para estos chunks seleccionados: "
            f"{faltantes}"
        )

    vecindad = construir_vecindad(chunks)

    seleccion_ordenada = sorted(
        seleccion_total,
        key=lambda chunk_uid: calcular_clave_ciega(
            version_revision=version_limpia,
            chunk_uid=chunk_uid,
        ),
    )
    filas = []

    for orden, chunk_uid in enumerate(
        seleccion_ordenada,
        start=1,
    ):
        objetivo = chunks_por_uid[chunk_uid]
        vecinos = vecindad[chunk_uid]
        anterior = vecinos["anterior"]
        siguiente = vecinos["siguiente"]

        filas.append(
            {
                "version_revision": version_limpia,
                "orden_revision": orden,
                "chunk_uid": chunk_uid,
                "titulo_objetivo": objetivo["titulo"],
                "contenido_objetivo": objetivo["contenido"],
                "titulo_anterior": (
                    anterior["titulo"]
                    if anterior is not None
                    else ""
                ),
                "contenido_anterior": (
                    anterior["contenido"]
                    if anterior is not None
                    else ""
                ),
                "titulo_siguiente": (
                    siguiente["titulo"]
                    if siguiente is not None
                    else ""
                ),
                "contenido_siguiente": (
                    siguiente["contenido"]
                    if siguiente is not None
                    else ""
                ),
                "estado_asignacion_referencia": "",
                "dominios_referencia": "",
                "materialidad_referencia": "",
                "justificacion_referencia": "",
                "requiere_revision_experta": "",
                "anotador": "",
                "fecha_revision": "",
            }
        )

    return (
        filas,
        len(seleccion_cambios),
        len(seleccion_adicional.difference(
            seleccion_cambios
        )),
    )


def serializar_csv(
    filas: list[dict[str, object]],
) -> str:
    """Serialize the blinded worksheet deterministically.

    [ES] Serializa determinísticamente la planilla ciega.
    """
    salida = io.StringIO(newline="")

    escritor = csv.DictWriter(
        salida,
        fieldnames=CAMPOS_SALIDA,
        extrasaction="raise",
        lineterminator="\n",
    )
    escritor.writeheader()
    escritor.writerows(filas)

    return salida.getvalue()


def guardar_csv(
    filas: list[dict[str, object]],
    ruta_salida: Path,
) -> Path:
    """Save UTF-8 CSV atomically without overwriting.

    [ES] Guarda el CSV UTF-8 atómicamente sin sobrescribir.
    """
    ruta_resuelta = ruta_salida.resolve()

    if ruta_resuelta.exists():
        raise FileExistsError(
            f"La salida ya existe y no será sobrescrita: "
            f"{ruta_resuelta}"
        )

    ruta_resuelta.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    ruta_temporal = ruta_resuelta.with_name(
        f".{ruta_resuelta.name}.tmp"
    )

    if ruta_temporal.exists():
        raise FileExistsError(
            f"Existe una salida temporal pendiente: "
            f"{ruta_temporal}"
        )

    try:
        ruta_temporal.write_text(
            serializar_csv(filas),
            encoding="utf-8-sig",
            newline="",
        )
        ruta_temporal.replace(ruta_resuelta)
    finally:
        if ruta_temporal.exists():
            ruta_temporal.unlink()

    return ruta_resuelta


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.

    [ES] Construye la interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Prepara una planilla ciega para revisar cambios "
            "entre políticas de contexto."
        )
    )
    parser.add_argument(
        "--comparacion",
        type=Path,
        required=True,
        help="Informe JSON de comparación pareada.",
    )
    parser.add_argument(
        "--informe-contexto",
        type=Path,
        required=True,
        help="Informe JSON que contiene los chunks y su orden.",
    )
    parser.add_argument(
        "--incluir-chunk-uid",
        action="append",
        default=[],
        help=(
            "Chunk adicional para revisión; se puede repetir."
        ),
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Versión explícita de la planilla de revisión.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        required=True,
        help="Ruta nueva de la planilla CSV.",
    )
    return parser


def main() -> None:
    """Build and persist the blinded review worksheet.

    [ES] Construye y persiste la planilla ciega de revisión.
    """
    argumentos = construir_parser().parse_args()

    try:
        comparacion = cargar_objeto_json(
            argumentos.comparacion,
            "la comparación",
        )
        informe_contexto = cargar_objeto_json(
            argumentos.informe_contexto,
            "el informe de contexto",
        )
        transiciones = cargar_transiciones(comparacion)
        chunks = cargar_chunks_contexto(informe_contexto)
        filas, cambios, adicionales = construir_planilla(
            transiciones=transiciones,
            chunks=chunks,
            adicionales=argumentos.incluir_chunk_uid,
            version_revision=argumentos.version,
        )
        salida = guardar_csv(
            filas=filas,
            ruta_salida=argumentos.salida,
        )
    except (
        FileExistsError,
        FileNotFoundError,
        ValueError,
    ) as error:
        raise SystemExit(f"ERROR: {error}") from error

    print(f"Casos por cambios : {cambios}")
    print(f"Casos adicionales : {adicionales}")
    print(f"Total revisión    : {len(filas)}")
    print(f"Planilla ciega    : {salida}")
    print("Predicciones      : no incluidas")
    print("PostgreSQL        : no consultado")


if __name__ == "__main__":
    main()