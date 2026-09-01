"""Build a blinded annotation worksheet from a classifier pilot report.

The worksheet excludes document identities, stored silos, predictions and
scores. Its purpose is to collect an independent human reference.

[ES] Construye una planilla ciega de anotación desde el informe piloto.

La planilla excluye identidades documentales, silos persistidos, predicciones
y scores. Su propósito es obtener una referencia humana independiente.
"""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


CAMPOS_SALIDA = (
    "version_anotacion",
    "orden_anotacion",
    "chunk_uid",
    "titulo",
    "contenido",
    "dominios_chunk_referencia",
    "materialidad_referencia",
    "justificacion_breve",
    "requiere_revision_experta",
    "anotador",
    "fecha_revision",
)

CAMPOS_REQUERIDOS_CHUNK = (
    "chunk_uid",
    "titulo",
    "contenido",
)


def cargar_informe(ruta_informe: Path) -> dict[str, object]:
    """Load and validate the exploratory classifier report.

    [ES] Carga y valida el informe exploratorio del clasificador.
    """
    ruta_resuelta = ruta_informe.resolve()

    if not ruta_resuelta.is_file():
        raise FileNotFoundError(
            f"No existe el informe: {ruta_resuelta}"
        )

    try:
        informe = json.loads(
            ruta_resuelta.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            f"El informe no contiene JSON válido: {error}"
        ) from error

    if not isinstance(informe, dict):
        raise ValueError(
            "La raíz del informe debe ser un objeto JSON."
        )

    chunks = informe.get("chunks")

    if not isinstance(chunks, list) or not chunks:
        raise ValueError(
            "El informe debe contener una lista no vacía de chunks."
        )

    chunk_uids: set[str] = set()

    for numero, chunk in enumerate(chunks, start=1):
        if not isinstance(chunk, dict):
            raise ValueError(
                f"El chunk {numero} no es un objeto JSON."
            )

        faltantes = [
            campo
            for campo in CAMPOS_REQUERIDOS_CHUNK
            if campo not in chunk
        ]

        if faltantes:
            raise ValueError(
                f"Al chunk {numero} le faltan campos: {faltantes}"
            )

        chunk_uid = chunk["chunk_uid"]
        contenido = chunk["contenido"]

        if not isinstance(chunk_uid, str) or not chunk_uid.strip():
            raise ValueError(
                f"El chunk {numero} tiene un chunk_uid inválido."
            )

        if chunk_uid in chunk_uids:
            raise ValueError(
                f"El chunk_uid está repetido: {chunk_uid}"
            )

        if not isinstance(contenido, str) or not contenido.strip():
            raise ValueError(
                f"El chunk {numero} no tiene contenido."
            )

        chunk_uids.add(chunk_uid)

    return informe


def calcular_clave_ciega(
    chunk_uid: str,
    version_anotacion: str,
) -> str:
    """Return a deterministic blinded ordering key.

    [ES] Devuelve una clave determinista para ordenar los chunks a ciegas.
    """
    contenido_clave = (
        f"{version_anotacion}|{chunk_uid}"
    ).encode("utf-8")

    return hashlib.sha256(contenido_clave).hexdigest()


def construir_plantilla(
    informe: dict[str, object],
    version_anotacion: str,
) -> list[dict[str, object]]:
    """Build rows without exposing classifier or document information.

    [ES] Construye filas sin exponer el clasificador ni el documento.
    """
    version_limpia = version_anotacion.strip()

    if not version_limpia:
        raise ValueError(
            "La versión de anotación no puede estar vacía."
        )

    if "\n" in version_limpia or "\r" in version_limpia:
        raise ValueError(
            "La versión de anotación no puede contener saltos de línea."
        )

    chunks_ordenados = sorted(
        informe["chunks"],
        key=lambda chunk: calcular_clave_ciega(
            chunk_uid=chunk["chunk_uid"],
            version_anotacion=version_limpia,
        ),
    )

    plantilla = []

    for orden, chunk in enumerate(chunks_ordenados, start=1):
        plantilla.append(
            {
                "version_anotacion": version_limpia,
                "orden_anotacion": orden,
                "chunk_uid": chunk["chunk_uid"],
                "titulo": chunk["titulo"],
                "contenido": chunk["contenido"],
                "dominios_chunk_referencia": "",
                "materialidad_referencia": "",
                "justificacion_breve": "",
                "requiere_revision_experta": "",
                "anotador": "",
                "fecha_revision": "",
            }
        )

    return plantilla


def serializar_plantilla_csv(
    registros: list[dict[str, object]],
) -> str:
    """Serialize the annotation worksheet as deterministic CSV.

    [ES] Serializa la planilla de anotación como CSV determinista.
    """
    salida = io.StringIO(newline="")

    escritor = csv.DictWriter(
        salida,
        fieldnames=CAMPOS_SALIDA,
        extrasaction="raise",
        lineterminator="\n",
    )
    escritor.writeheader()
    escritor.writerows(registros)

    return salida.getvalue()


def guardar_plantilla_csv(
    registros: list[dict[str, object]],
    ruta_salida: Path,
) -> Path:
    """Save the CSV atomically without overwriting an existing worksheet.

    [ES] Guarda el CSV atómicamente sin sobrescribir una planilla existente.
    """
    ruta_resuelta = ruta_salida.resolve()

    if ruta_resuelta.exists():
        raise FileExistsError(
            f"La salida ya existe y no será sobrescrita: {ruta_resuelta}"
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
            f"Existe una salida temporal pendiente: {ruta_temporal}"
        )

    texto_csv = serializar_plantilla_csv(registros)

    ruta_temporal.write_text(
        texto_csv,
        encoding="utf-8-sig",
        newline="",
    )
    ruta_temporal.replace(ruta_resuelta)

    return ruta_resuelta


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.

    [ES] Construye la interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Genera una planilla ciega para anotar los chunks "
            "del piloto del clasificador."
        )
    )
    parser.add_argument(
        "--informe",
        type=Path,
        required=True,
        help="Informe JSON producido por la ablación del clasificador.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        required=True,
        help="Archivo CSV nuevo donde se guardará la planilla.",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Identificador de la versión de anotación.",
    )
    return parser


def main() -> None:
    """Run the blinded worksheet preparation.

    [ES] Ejecuta la preparación de la planilla ciega.
    """
    argumentos = construir_parser().parse_args()

    informe = cargar_informe(argumentos.informe)
    plantilla = construir_plantilla(
        informe=informe,
        version_anotacion=argumentos.version,
    )
    ruta_guardada = guardar_plantilla_csv(
        registros=plantilla,
        ruta_salida=argumentos.salida,
    )

    print(f"Chunks preparados : {len(plantilla)}")
    print(f"Columnas           : {len(CAMPOS_SALIDA)}")
    print(f"Planilla ciega     : {ruta_guardada}")
    print("Predicciones       : no incluidas")
    print("PostgreSQL         : no consultado")
    print("Fuente del informe : no modificada")


if __name__ == "__main__":
    main()