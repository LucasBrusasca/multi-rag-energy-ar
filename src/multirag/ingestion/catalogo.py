"""Discover the source files available for corpus ingestion.

A source may contain text, tables, images, charts, or visual structure.
This module does not interpret the content or determine its modalities yet.

[ES] Descubre los archivos fuente disponibles para la ingesta del corpus.

Una fuente puede contener texto, tablas, imágenes, gráficos o estructura visual.
Este módulo todavía no interpreta el contenido ni determina sus modalidades.
"""

import argparse
import hashlib
import json
from pathlib import Path

import filetype

from multirag.paths import DATA_DIR

DIRECTORIO_FUENTES = DATA_DIR / "raw"


def listar_fuentes_directorio(directorio: Path) -> list[Path]:
    """Return every source file found recursively inside a directory.

    The function does not filter by extension or assume which content
    modalities are present.

    [ES] Devuelve todos los archivos fuente encontrados recursivamente
    dentro de un directorio.

    La función no filtra por extensión ni presupone qué modalidades
    están presentes en el contenido.
    """

    if not directorio.is_dir():
        raise NotADirectoryError(
            f"No existe el directorio de fuentes: {directorio}"
        )


    fuentes = [
        ruta
        for ruta in directorio.rglob("*")
        if ruta.is_file()

    ]

    return sorted(
        fuentes,
        key=lambda ruta: ruta.relative_to(directorio).as_posix().casefold()
    )


def calcular_sha256(ruta: Path) -> str:
    """Calculate the SHA-256 fingerprint of a source file.

    Python manages bounded binary reads internally, so the complete file
    does not need to be loaded into memory at once.

    [ES] Calcula la huella SHA-256 de un archivo fuente.

    Python administra internamente la lectura binaria acotada, por lo que
    no es necesario cargar el archivo completo en memoria.
    """

    if not ruta.is_file():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    with ruta.open("rb") as archivo:
        huella = hashlib.file_digest(archivo, hashlib.sha256)

    return huella.hexdigest()

def construir_artifact_id(huella_sha256: str) -> str:
    """Build an artifact identifier from a SHA-256 fingerprint.

    The identifier represents the exact binary file, not the conceptual
    document or its editorial version.

    [ES] Construye un identificador de artefacto a partir de una huella
    SHA-256.

    El identificador representa el archivo binario exacto, no el documento
    conceptual ni su versión editorial.
    """
    referencia_sha256 = hashlib.sha256()

    try:
        huella_binaria = bytes.fromhex(huella_sha256)
    except ValueError as error:
        raise ValueError(
            "La huella SHA-256 contiene caracteres no hexadecimales."
        ) from error

    representacion_canonica = huella_binaria.hex()

    if (
        len(huella_binaria) != referencia_sha256.digest_size
        or representacion_canonica != huella_sha256.lower()
    ):
        raise ValueError(
            "La huella no tiene una representación SHA-256 válida."
        )

    nombre_algoritmo = referencia_sha256.name.upper()
    return f"ART-{nombre_algoritmo}-{huella_sha256.upper()}"

def detectar_mime_por_firma(ruta: Path) -> str | None:
    """Detect a source MIME type from its binary signature.

    An unknown signature is represented by None and does not imply that
    the source is invalid or unsupported.


    [ES] Detecta el tipo MIME de una fuente mediante su firma binaria.

    Una firma desconocida se representa con None y no implica que la
    fuente sea inválida o no soportada.
    """
    if not ruta.is_file():
        raise FileNotFoundError(f"No existe el archivo fuente: {ruta}")

    tipo_detectado = filetype.guess(str(ruta))

    if tipo_detectado is None:
        return None

    return tipo_detectado.mime

def construir_registro_fuente(
        ruta: Path,
        directorio_base: Path,
) -> dict[str, str | int | None]:
    """Build an objective catalog record for a source file.

    Absolute local paths and inferred semantic metadata are intentionally
    excluded from the record.


    [ES] Construye un registro objetivo de catálogo para un archivo fuente.


    Las rutas locales absolutas y los metadatos semánticos inferidos se
    excluyen intencionalmente del registro.
    """
    if not ruta.is_file():
        raise FileNotFoundError(f"No existe el archivo fuente: {ruta}")

    if not directorio_base.is_dir():
        raise NotADirectoryError(
            f"No existe el directorio base: {directorio_base}"
        )

    ruta = ruta.resolve()
    directorio_base = directorio_base.resolve()

    try:
        ruta_relativa = ruta.relative_to(directorio_base)
    except ValueError as error:
        raise ValueError(
            f"El archivo {ruta} no pertenece a {directorio_base}."
        ) from error

    huella = calcular_sha256(ruta)
    artifact_id = construir_artifact_id(huella)
    mime_firma = detectar_mime_por_firma(ruta)


    return {
        "artifact_id": artifact_id,
        "fuente": ruta.stem,
        "archivo_relativo": ruta_relativa.as_posix(),
        "nombre_archivo": ruta.name,
        "extension": ruta.suffix.lower(),
        "mime_firma": mime_firma,
        "tamano_bytes": ruta.stat().st_size,
        "sha256": huella
    }


def construir_catalogo_objetivo(
        directorio: Path
) -> list[dict[str, str | int | None]]:
    """Build the objective records for every source in a directory

    The function preserves every source occurrence, including files with
    identical content, and does not print or persist the records.

    [ES] Construye los registros objetivos de todas las fuentes de un
    directorio,

    La función conserva cada aparición de una fuente, incluso cuando dos
    archivos tiene contenido idéntico, y no imprime ni persiste los
    registros.
    """
    fuentes = listar_fuentes_directorio(directorio)

    return [
        construir_registro_fuente(
            ruta=fuente,
            directorio_base=directorio
        )
        for fuente in fuentes
    ]


def serializar_catalogo_jsonl(
        registros: list[dict[str, str | int | None]]
) -> str:
    """Serialize objective catalog records as deterministic JSON Lines.

    Each source record occupies one line. The function only builds and
    returns text; it does not write files.

    [ES] Serializa los registros objetivos del catálogo como JSON Lines
    determinista.

    Cada registro de fuente ocuá una línea. La función solamente construye
    y devuelve texto; no escribe archivos.
    """

    lineas = [
        json.dumps(
            registro,
            ensure_ascii=False,
            sort_keys=True
        )
        for registro in registros
    ]

    if not lineas:
        return ""

    return "\n".join(lineas) + "\n"


def guardar_catalogo_jsonl(
    registros: list[dict[str, str | int | None]],
    ruta_salida: Path,
) -> Path:
    """Persist objective catalog records atomically as UTF-8 JSON Lines.

    The destination is provided by the caller. Human-curated metadata must
    be stored separately and is never modified by this function.

    [ES] Persiste atómicamente los registros objetivos del catálogo como
    JSON Lines con codificación UTF-8.

    El destino lo proporciona quien llama a la función. Los metadatos
    curados humanamente deben almacenarse por separado y esta función
    nunca los modifica.
    """

    texto = serializar_catalogo_jsonl(registros)
    ruta_salida = ruta_salida.resolve()
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    ruta_temporal = ruta_salida.with_name(
        f".{ruta_salida.name}.tmp"
    )

    try:
        ruta_temporal.write_text(
            texto,
            encoding="utf-8",
            newline="\n"
        )
        ruta_temporal.replace(ruta_salida)
    finally:
        if ruta_temporal.exists():
            ruta_temporal.unlink()

    return ruta_salida


def construir_parser_argumentos() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    [ES] Construye el analizador de argumentos de línea de comandos.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Cataloga objetivamente las fuentes del corpus "
            "y guarda el inventario como JSONL."
        )
    )
    parser.add_argument(
        "--fuentes",
        type=Path,
        default=DIRECTORIO_FUENTES,
        help=(
            "Directorio raíz que contiene las fuentes. "
            "Por defecto se utiliza data/raw."
        )
    )
    parser.add_argument(
        "--salida",
        type=Path,
        required=True,
        help="Ruta del archivo JSONL que se generará."
    )

    return parser


def main() -> None:
    """Build and persist the objective corpus catalog.

    [ES] Construye y persiste el catálogo objetivo del corpus.
    """

    parser = construir_parser_argumentos()
    argumentos = parser.parse_args()

    directorio_fuentes = argumentos.fuentes.resolve()
    ruta_salida = argumentos.salida.resolve()

    try:
        ruta_salida.relative_to(directorio_fuentes)
    except ValueError:
        pass
    else:
        parser.error(
            "--salida no puede estar dentro del directorio de fuentes."
        )

    registros = construir_catalogo_objetivo(directorio_fuentes)
    ocurrencias_por_artefacto: dict[str, list[str]] = {}

    for registro in registros:
        artifact_id = str(registro["artifact_id"])
        archivo_relativo = str(registro["archivo_relativo"])

        ocurrencias_por_artefacto.setdefault(
            artifact_id,
            []
        ).append(archivo_relativo)

    duplicados = {
        artifact_id: rutas
        for artifact_id, rutas in ocurrencias_por_artefacto.items()
        if len(rutas) > 1
    }

    ruta_guardada = guardar_catalogo_jsonl(
        registros=registros,
        ruta_salida=ruta_salida
    )

    print(f"Directorio de fuentes: {directorio_fuentes}")
    print(f"Fuentes encontradas: {len(registros)}")
    print(
        "Artefactos únicos por contenido: "
        f"{len(ocurrencias_por_artefacto)}"
    )
    print(f"Grupos duplicados: {len(duplicados)}")
    print(f"Catálogo guardado en: {ruta_guardada}")

    for artifact_id, rutas in duplicados.items():
        print(f"Contenido duplicado: {artifact_id}")
        for ruta in rutas:
            print(f"  - {ruta}")


if __name__ == "__main__":
    main()
