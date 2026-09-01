"""Build human-curated metadata records for corpus documents.

This module keeps semantic and administrative metadata separate from the
objective source inventory. It does not infer or classify values. Persistence
only writes records supplied by the caller.


[ES] Construye registros de metadatos curados humanamente para los
documentos del corpus.

Este módulo mantiene los metadatos semánticos y administrativos separados
del inventario objetivo de fuentes. No infiere ni clasifica valores. La
persistencia solo escribe registros proporcionados por quien llama.
"""

import argparse
import csv
import io
import json
from collections.abc import Iterable, Mapping
from pathlib import Path


CAMPOS_METADATOS_CURADOS = (
    "instrument_id",
    "document_id",
    "artifact_id",
    "archivo_referencia",
    "fuente",
    "sha256",
    "titulo_oficial",
    "emisor_id",
    "emisor_nombre",
    "tipo_documento",
    "fecha_documento",
    "jurisdiccion",
    "dominios_documentales",
    "origen_fuente",
    "url_origen",
    "modalidades_esperadas",
    "estado_inclusion",
    "motivo_exclusion",
    "observaciones",
)


def cargar_catalogo_objetivo_jsonl(
        ruta_catalogo: Path
) -> list[dict[str, object]]:
    """Load objective catalog records from a UTF-8 JSON Lines file.

    [ES] Carga los registros del catálogo objetivo desde un archivo
    JSON Lines con codificación UTF-8.
    """

    ruta_catalogo = ruta_catalogo.resolve()

    if not ruta_catalogo.is_file():
        raise FileNotFoundError(
            f"No existe el catálogo objetivo: {ruta_catalogo}"
        )

    registros: list[dict[str, object]] = []

    with ruta_catalogo.open(
        "r",
        encoding="utf-8-sig",
    ) as archivo:
        for numero_linea, linea in enumerate(archivo, start=1):
            if not linea.strip():
                continue

            try:
                registro = json.loads(linea)
            except json.JSONDecodeError as error:
                raise ValueError(
                    "El catálogo contiene JSON inválido "
                    f"en la línea {numero_linea}."
                ) from error

            if not isinstance(registro, dict):
                raise ValueError(
                    "Cada línea del catálogo debe contener "
                    f"un objeto JSON. Línea: {numero_linea}."
                )

            registros.append(registro)

    return registros



def construir_registro_metadatos(
        registro_objetivo: Mapping[str, object]
) -> dict[str, str]:
    """Build an empty human-curation record linked to an objective record.

    [ES] Construye un registro vacío de curación humana vinculado con un
    registro objetivo.
    """

    artifact_id = registro_objetivo.get("artifact_id")
    archivo_relativo = registro_objetivo.get("archivo_relativo")
    fuente = registro_objetivo.get("fuente")
    huella_sha256 = registro_objetivo.get("sha256")

    if not isinstance(artifact_id, str) or not artifact_id.strip():
        raise ValueError(
            "El registro objetivo no contiene un artifact_id válido."
        )

    if (
        not isinstance(archivo_relativo, str)
        or not archivo_relativo.strip()
    ):
        raise ValueError(
            "El registro objetivo no contiene un archivo_relativo válido."
        )

    if not isinstance(fuente, str) or not fuente.strip():
        raise ValueError(
            "El registro objetivo no contiene una fuente válida."
        )

    if (
        not isinstance(huella_sha256, str)
        or not huella_sha256.strip()
    ):
        raise ValueError(
            "El registro objetivo no contiene una huella sha256 válida."
        )

    registro_metadatos = {
        campo: ""
        for campo in CAMPOS_METADATOS_CURADOS
    }

    registro_metadatos["artifact_id"] = artifact_id
    registro_metadatos["archivo_referencia"] = archivo_relativo
    registro_metadatos["fuente"] = fuente
    registro_metadatos["sha256"] = huella_sha256

    return registro_metadatos



def construir_plantilla_metadatos(
        registros_objetivos: Iterable[Mapping[str, object]]
) -> list[dict[str, str]]:
    """Build one human-curation record per unique artifact identifier.

    The first objective occurrence is retained as the reference path.
    Input order is preserved.

    [ES] Construye un registro de curación humana por cada identificador
    de artefacto único.

    Se conserva la primera aparición objetiva como ruta de referencia y
    se mantiene el orden de entrada.
    """

    registros_por_artefacto: dict[str, dict[str, str]] = {}

    for registro_objetivo in registros_objetivos:
        registro_metadatos = construir_registro_metadatos(
            registro_objetivo
        )
        artifact_id = registro_metadatos["artifact_id"]

        registros_por_artefacto.setdefault(
            artifact_id,
            registro_metadatos,
        )

    return list(registros_por_artefacto.values())


def serializar_plantilla_csv(
        registros_metadatos: Iterable[Mapping[str, str]]
) -> str:
    """ Serialize curated metadata records as deterministic CSV text.

    The function builds and returns text without writing files.

    [ES] Serializa los registros de metadatos curados como texto CSV
    determinista.

    La función construye y devuelve el texto sin escribir archivos.
    """

    salida = io.StringIO(newline="")
    escritor = csv.DictWriter(
        salida,
        fieldnames=CAMPOS_METADATOS_CURADOS,
        extrasaction="raise",
        lineterminator="\n"
    )

    escritor.writeheader()

    for registro_metadatos in registros_metadatos:
        escritor.writerow(registro_metadatos)

    return salida.getvalue()


def guardar_plantilla_csv(
        registros_metadatos: Iterable[Mapping[str, str]],
        ruta_salida: Path,
) -> Path:
    """Persist curated metadata records atomically as UTF-8 CSV.

    [ES] Persiste atómicamente los registros de metadatos curados
    como CSV con codificación UTF-8.
    """

    ruta_salida = ruta_salida.resolve()

    if ruta_salida.exists():
        raise FileExistsError(
            f"La plantilla de metadatos ya existe: {ruta_salida}"
        )

    texto = serializar_plantilla_csv(registros_metadatos)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    ruta_temporal = ruta_salida.with_name(
        f".{ruta_salida.name}.tmp"
    )

    try:
        ruta_temporal.write_text(
            texto,
            encoding="utf-8",
            newline="\n",
        )
        ruta_temporal.replace(ruta_salida)
    finally:
        if ruta_temporal.exists():
            ruta_temporal.unlink()

    return ruta_salida

def generar_plantilla_metadatos(
        ruta_catalogo: Path,
        ruta_salida: Path,
) -> Path:
    """Generate a Silver metadata template from a Bronze catalog.

    [ES] Genera una plantilla Silver de metadatos a partir de un
    catálogo Bronze."""


    registros_objetivos = cargar_catalogo_objetivo_jsonl(
        ruta_catalogo
    )
    registros_metadatos = construir_plantilla_metadatos(
        registros_objetivos
    )

    return guardar_plantilla_csv(
        registros_metadatos=registros_metadatos,
        ruta_salida=ruta_salida,
    )

def construir_parser_argumentos() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    [ES] Construye el analizador de argumentos de línea de comandos.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Genera una plantilla Silver de metadatos "
            "desde un catálogo Bronze."
        )
    )
    parser.add_argument(
        "--catalogo",
        type=Path,
        required=True,
        help="Ruta del catálogo objetivo JSONL de entrada.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        required=True,
        help="Ruta del archivo CSV que se generará.",
    )

    return parser

def main() -> None:
    """Generate the Silver metadata template from the command line.

    [ES] Genera la plantilla Silver de metadatos desde la línea de comandos
    """

    parser = construir_parser_argumentos()
    argumentos = parser.parse_args()

    try:
        ruta_guardada = generar_plantilla_metadatos(
            ruta_catalogo=argumentos.catalogo,
            ruta_salida=argumentos.salida,
        )
    except (
        FileExistsError,
        FileNotFoundError,
        ValueError,
    ) as error:
        parser.error(str(error))

    print(f"Plantilla de metadatos guardada en: {ruta_guardada}")



if __name__ == "__main__":
    main()
