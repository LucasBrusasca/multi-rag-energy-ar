"""Audit an acquired InfoLEG batch before cataloguing or ingestion.

The audit compares the reproducible selection with the files that actually
exist on disk. It detects missing and unexpected files, exact binary copies,
empty responses, content that does not look like HTML, and common HTTP error
pages. It never modifies the acquired sources or PostgreSQL.

[ES] Audita un lote adquirido de InfoLEG antes de catalogarlo o ingerirlo.

La auditoría compara la selección reproducible con los archivos que realmente
existen en disco. Detecta faltantes, archivos inesperados, copias binarias
exactas, respuestas vacías, contenido que no parece HTML y páginas comunes de
error HTTP. Nunca modifica las fuentes adquiridas ni PostgreSQL.
"""

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from multirag.acquisition.providers.infoleg.download import nombre_archivo
from multirag.paths import DATA_DIR


DIRECTORIO = DATA_DIR / "incoming" / "infoleg"
SELECCION = DIRECTORIO / "seleccion.csv"
TEXTOS = DIRECTORIO / "textos"
SALIDA = DATA_DIR / "catalog" / "candidates" / "infoleg_audit.json"

MARCADORES_ERROR_HTTP = (
    b"403 forbidden",
    b"404 not found",
    b"access denied",
    b"service unavailable",
)


def calcular_sha256(ruta: Path, tamano_bloque: int = 1024 * 1024) -> str:
    """Return the complete SHA-256 digest without loading the file at once.
    [ES] Devuelve el SHA-256 completo sin cargar todo el archivo a la vez."""
    huella = hashlib.sha256()

    with ruta.open("rb") as archivo:
        while bloque := archivo.read(tamano_bloque):
            huella.update(bloque)

    return huella.hexdigest()


def cargar_seleccion(ruta_seleccion: Path) -> list[dict[str, str]]:
    """Read and minimally validate the selection contract.
    [ES] Lee y valida mínimamente el contrato de selección."""
    if not ruta_seleccion.is_file():
        raise FileNotFoundError(f"No existe la selección: {ruta_seleccion}")

    with ruta_seleccion.open(encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    campos_requeridos = {"dominio", "criterio", "id_norma"}

    if not filas:
        raise ValueError("La selección no contiene registros.")

    faltantes = campos_requeridos - set(filas[0])

    if faltantes:
        raise ValueError(
            "La selección no contiene los campos requeridos: "
            f"{', '.join(sorted(faltantes))}"
        )

    nombres = [nombre_archivo(fila) for fila in filas]
    repetidos = sorted(
        nombre
        for nombre, cantidad in Counter(nombres).items()
        if cantidad > 1
    )

    if repetidos:
        raise ValueError(
            "La selección genera nombres de archivo repetidos: "
            f"{', '.join(repetidos)}"
        )

    return filas


def _parece_html(ruta: Path) -> bool:
    """Check the file signature without trusting its extension.
    [ES] Comprueba la firma del archivo sin confiar en su extensión."""
    cabecera = ruta.read_bytes()[:4096].lstrip().lower()
    return b"<html" in cabecera or b"<!doctype html" in cabecera


def _contiene_error_http(ruta: Path) -> bool:
    """Flag common error-page markers; this is a warning, not a verdict.
    [ES] Marca indicadores comunes de error; es una alerta, no un veredicto."""
    contenido = ruta.read_bytes().lower()
    return any(marcador in contenido for marcador in MARCADORES_ERROR_HTTP)


def auditar_lote(
    ruta_seleccion: Path,
    directorio_textos: Path,
) -> dict:
    """Compare selected norms with acquired files and return an audit report.
    [ES] Compara normas seleccionadas con archivos adquiridos y reporta."""
    filas = cargar_seleccion(ruta_seleccion)

    if not directorio_textos.is_dir():
        raise NotADirectoryError(
            f"No existe el directorio de textos: {directorio_textos}"
        )

    esperados_por_nombre = {
        nombre_archivo(fila): fila
        for fila in filas
    }
    archivos = sorted(
        (ruta for ruta in directorio_textos.rglob("*") if ruta.is_file()),
        key=lambda ruta: ruta.relative_to(directorio_textos).as_posix().casefold(),
    )
    presentes_por_ruta = {
        ruta.relative_to(directorio_textos).as_posix(): ruta
        for ruta in archivos
    }

    nombres_esperados = set(esperados_por_nombre)
    rutas_presentes = set(presentes_por_ruta)
    faltantes = sorted(nombres_esperados - rutas_presentes)
    extras = sorted(rutas_presentes - nombres_esperados)
    coincidentes = sorted(nombres_esperados & rutas_presentes)

    vacios = sorted(
        ruta_relativa
        for ruta_relativa, ruta in presentes_por_ruta.items()
        if ruta.stat().st_size == 0
    )
    firma_no_html = sorted(
        ruta_relativa
        for ruta_relativa, ruta in presentes_por_ruta.items()
        if ruta.stat().st_size > 0 and not _parece_html(ruta)
    )
    posibles_errores_http = sorted(
        ruta_relativa
        for ruta_relativa, ruta in presentes_por_ruta.items()
        if ruta.stat().st_size > 0 and _contiene_error_http(ruta)
    )

    rutas_por_huella: dict[str, list[str]] = defaultdict(list)

    for ruta_relativa, ruta in presentes_por_ruta.items():
        rutas_por_huella[calcular_sha256(ruta)].append(ruta_relativa)

    grupos_duplicados = [
        {
            "sha256": huella,
            "archivos": sorted(rutas),
            "seleccionados": sorted(
                ruta for ruta in rutas if ruta in nombres_esperados
            ),
            "extras": sorted(
                ruta for ruta in rutas if ruta not in nombres_esperados
            ),
        }
        for huella, rutas in sorted(rutas_por_huella.items())
        if len(rutas) > 1
    ]

    grupos = sorted(
        {(fila["dominio"], fila["criterio"]) for fila in filas}
    )
    composicion = []

    for dominio, criterio in grupos:
        nombres_grupo = {
            nombre_archivo(fila)
            for fila in filas
            if fila["dominio"] == dominio and fila["criterio"] == criterio
        }
        composicion.append(
            {
                "dominio_adquisicion": dominio,
                "criterio": criterio,
                "seleccionados": len(nombres_grupo),
                "presentes": len(nombres_grupo & rutas_presentes),
                "faltantes": len(nombres_grupo - rutas_presentes),
            }
        )

    return {
        "schema_version": 1,
        "seleccion": str(ruta_seleccion.resolve()),
        "directorio_textos": str(directorio_textos.resolve()),
        "resumen": {
            "registros_seleccionados": len(filas),
            "archivos_esperados": len(nombres_esperados),
            "archivos_presentes": len(archivos),
            "archivos_seleccionados_presentes": len(coincidentes),
            "archivos_faltantes": len(faltantes),
            "archivos_extras": len(extras),
            "archivos_vacios": len(vacios),
            "archivos_firma_no_html": len(firma_no_html),
            "posibles_paginas_error_http": len(posibles_errores_http),
            "grupos_con_contenido_duplicado": len(grupos_duplicados),
        },
        "composicion_seleccion": composicion,
        "faltantes": faltantes,
        "extras": extras,
        "vacios": vacios,
        "firma_no_html": firma_no_html,
        "posibles_paginas_error_http": posibles_errores_http,
        "grupos_duplicados": grupos_duplicados,
    }


def guardar_informe(informe: dict, ruta_salida: Path) -> Path:
    """Write the report atomically as deterministic UTF-8 JSON.
    [ES] Guarda el informe atómicamente como JSON UTF-8 determinista."""
    destino = ruta_salida.resolve()
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(f".{destino.name}.tmp")
    contenido = json.dumps(
        informe,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"

    temporal.write_text(contenido, encoding="utf-8", newline="\n")
    temporal.replace(destino)
    return destino


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.
    [ES] Construye la interfaz de línea de comandos."""
    parser = argparse.ArgumentParser(
        description=(
            "Audita un lote InfoLEG sin modificar fuentes ni PostgreSQL."
        )
    )
    parser.add_argument(
        "--seleccion",
        type=Path,
        default=SELECCION,
        help="CSV reproducible que define los archivos esperados.",
    )
    parser.add_argument(
        "--textos",
        type=Path,
        default=TEXTOS,
        help="Directorio que contiene los textos adquiridos.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=SALIDA,
        help="Ruta del informe JSON que se generará.",
    )
    return parser


def main() -> None:
    """Run the read-only audit and persist only its derived report.
    [ES] Ejecuta la auditoría y persiste únicamente su informe derivado."""
    argumentos = construir_parser().parse_args()
    informe = auditar_lote(
        ruta_seleccion=argumentos.seleccion,
        directorio_textos=argumentos.textos,
    )
    ruta = guardar_informe(informe, argumentos.salida)
    resumen = informe["resumen"]

    print(f"seleccionados : {resumen['registros_seleccionados']}")
    print(f"presentes     : {resumen['archivos_seleccionados_presentes']}")
    print(f"faltantes     : {resumen['archivos_faltantes']}")
    print(f"extras        : {resumen['archivos_extras']}")
    print(f"vacíos        : {resumen['archivos_vacios']}")
    print(f"no HTML       : {resumen['archivos_firma_no_html']}")
    print(f"error HTTP    : {resumen['posibles_paginas_error_http']}")
    print(f"duplicados    : {resumen['grupos_con_contenido_duplicado']}")
    print(f"informe       : {ruta}")


if __name__ == "__main__":
    main()
