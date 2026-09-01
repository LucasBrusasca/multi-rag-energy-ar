"""Enrich pending metadata with facts published by InfoLEG.

This provider adapter joins the objective catalog template with the acquisition
selection by the stable source name. It copies source facts, but it does not
assign documentary domains, canonical entity identifiers, or Golden labels.

[ES] Enriquece metadatos pendientes con hechos publicados por InfoLEG.

El adaptador cruza la plantilla objetiva con la seleccion de adquisicion por el
nombre estable de fuente. Copia hechos de origen, pero no asigna dominios
documentales, identificadores canonicos de entidad ni etiquetas Golden.
"""

import argparse
import csv
import re
import unicodedata
from pathlib import Path

from multirag.acquisition.providers.infoleg.audit import cargar_seleccion
from multirag.acquisition.providers.infoleg.download import nombre_archivo
from multirag.ingestion.metadatos import guardar_plantilla_csv
from multirag.ingestion.validar_metadatos import (
    RUTA_CONFIGURACION_CATALOGO,
    cargar_configuracion_catalogo,
)
from multirag.paths import DATA_DIR


DIRECTORIO_INFOLEG = DATA_DIR / "incoming" / "infoleg"
SELECCION = DIRECTORIO_INFOLEG / "seleccion.csv"
PLANTILLA = (
    DATA_DIR
    / "catalog"
    / "candidates"
    / "infoleg_metadatos_pendientes.csv"
)
SALIDA = (
    DATA_DIR
    / "catalog"
    / "candidates"
    / "infoleg_metadatos_candidatos.csv"
)


def normalizar_valor_taxonomico(valor: str) -> str:
    """Convert a source label into a comparable taxonomy token.
    [ES] Convierte una etiqueta de origen en un token taxonomico comparable."""
    sin_tildes = "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", valor)
        if not unicodedata.combining(caracter)
    )
    return re.sub(
        r"[^a-z0-9]+",
        "_",
        sin_tildes.casefold(),
    ).strip("_")


def cargar_plantilla(ruta: Path) -> list[dict[str, str]]:
    """Load the pending metadata template.
    [ES] Carga la plantilla de metadatos pendientes."""
    if not ruta.is_file():
        raise FileNotFoundError(f"No existe la plantilla: {ruta}")

    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    if not filas:
        raise ValueError("La plantilla de metadatos no contiene filas.")

    fuentes = [fila.get("fuente", "").strip() for fila in filas]

    if any(not fuente for fuente in fuentes):
        raise ValueError("La plantilla contiene una fuente vacia.")

    if len(fuentes) != len(set(fuentes)):
        raise ValueError("La plantilla contiene fuentes repetidas.")

    return filas


def construir_indice_seleccion(
    filas_seleccion: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    """Index InfoLEG selection rows by normalized artifact source.
    [ES] Indexa la seleccion InfoLEG por la fuente del artefacto normalizado."""
    indice: dict[str, dict[str, str]] = {}

    for fila in filas_seleccion:
        fuente = Path(nombre_archivo(fila)).stem

        if fuente in indice:
            raise ValueError(f"La seleccion repite la fuente: {fuente}")

        indice[fuente] = fila

    return indice


def construir_titulo_candidato(fila: dict[str, str]) -> str:
    """Build a traceable title candidate from literal source fields.
    [ES] Construye un titulo candidato trazable desde campos de origen."""
    tipo = fila["tipo_norma"].strip()
    numero = fila["numero_norma"].strip()
    resumen = fila["titulo_resumido"].strip()
    identificacion = " ".join(parte for parte in (tipo, numero) if parte)

    if identificacion and resumen:
        return f"{identificacion} — {resumen}"

    return identificacion or resumen


def enriquecer_registro(
    registro: dict[str, str],
    seleccion: dict[str, str],
    tipos_permitidos: set[str],
) -> dict[str, str]:
    """Copy source-backed facts into one still-pending metadata record.
    [ES] Copia hechos respaldados por la fuente en un registro aun pendiente."""
    enriquecido = dict(registro)
    tipo_origen = seleccion["tipo_norma"].strip()
    tipo_candidato = normalizar_valor_taxonomico(tipo_origen)
    tipo_registrado = tipo_candidato in tipos_permitidos
    estrato = f"{seleccion['dominio']}/{seleccion['criterio']}"
    observaciones = (
        "Metadatos candidatos derivados de la seleccion reproducible de "
        f"InfoLEG; id_norma={seleccion['id_norma']}; "
        f"estrato_adquisicion={estrato}. El estrato de adquisicion no es "
        "una etiqueta canonica del documento ni del chunk."
    )

    if not tipo_registrado:
        observaciones += (
            f" Tipo de origen pendiente de taxonomia: {tipo_origen}."
        )

    enriquecido.update(
        {
            "titulo_oficial": construir_titulo_candidato(seleccion),
            "emisor_nombre": seleccion["organismo_origen"].strip(),
            "tipo_documento": (
                tipo_candidato if tipo_registrado else "no_identificado"
            ),
            "fecha_documento": seleccion["fecha_sancion"].strip(),
            "jurisdiccion": "argentina_nacional",
            "dominios_documentales": "",
            "origen_fuente": "publica",
            "url_origen": seleccion["url"].strip(),
            "modalidades_esperadas": "texto|estructura_visual",
            "estado_inclusion": "pendiente_revision",
            "observaciones": observaciones,
        }
    )
    return enriquecido


def enriquecer_plantilla(
    registros: list[dict[str, str]],
    filas_seleccion: list[dict[str, str]],
    tipos_permitidos: set[str],
) -> tuple[list[dict[str, str]], dict[str, object]]:
    """Join all template records and summarize unresolved source rows.
    [ES] Cruza la plantilla completa y resume filas de origen no resueltas."""
    indice = construir_indice_seleccion(filas_seleccion)
    enriquecidos = []
    fuentes_usadas = set()

    for registro in registros:
        fuente = registro["fuente"].strip()
        seleccion = indice.get(fuente)

        if seleccion is None:
            raise ValueError(
                "No existe una fila de seleccion para la fuente: "
                f"{fuente}"
            )

        enriquecidos.append(
            enriquecer_registro(registro, seleccion, tipos_permitidos)
        )
        fuentes_usadas.add(fuente)

    fuentes_sin_artefacto = sorted(set(indice) - fuentes_usadas)
    tipos_pendientes = sorted(
        {
            fila["tipo_norma"].strip()
            for fila in filas_seleccion
            if normalizar_valor_taxonomico(fila["tipo_norma"])
            not in tipos_permitidos
        }
    )
    resumen = {
        "plantilla": len(registros),
        "enriquecidos": len(enriquecidos),
        "seleccion_sin_artefacto": fuentes_sin_artefacto,
        "tipos_pendientes": tipos_pendientes,
    }
    return enriquecidos, resumen


def tipos_documento_permitidos(configuracion: dict) -> set[str]:
    """Flatten registered document types from catalog configuration.
    [ES] Reune los tipos documentales registrados en la configuracion."""
    familias = configuracion["tipos_documento_por_familia"]
    return {
        tipo
        for tipos in familias.values()
        for tipo in tipos
    }


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.
    [ES] Construye la interfaz de linea de comandos."""
    parser = argparse.ArgumentParser(
        description=(
            "Enriquece la plantilla candidata con metadatos publicados por "
            "InfoLEG; no asigna dominios ni toca PostgreSQL."
        )
    )
    parser.add_argument("--plantilla", type=Path, default=PLANTILLA)
    parser.add_argument("--seleccion", type=Path, default=SELECCION)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    return parser


def main() -> None:
    """Enrich and persist the candidate CSV.
    [ES] Enriquece y persiste el CSV candidato."""
    argumentos = construir_parser().parse_args()
    registros = cargar_plantilla(argumentos.plantilla)
    seleccion = cargar_seleccion(argumentos.seleccion)
    configuracion = cargar_configuracion_catalogo(
        RUTA_CONFIGURACION_CATALOGO
    )
    enriquecidos, resumen = enriquecer_plantilla(
        registros=registros,
        filas_seleccion=seleccion,
        tipos_permitidos=tipos_documento_permitidos(configuracion),
    )
    salida = guardar_plantilla_csv(enriquecidos, argumentos.salida)
    print(f"plantilla              : {resumen['plantilla']}")
    print(f"enriquecidos           : {resumen['enriquecidos']}")
    print(
        "seleccion sin artefacto: "
        f"{len(resumen['seleccion_sin_artefacto'])}"
    )
    for fuente in resumen["seleccion_sin_artefacto"]:
        print(f"  - {fuente}")
    print(f"tipos pendientes       : {resumen['tipos_pendientes']}")
    print(f"salida                  : {salida}")
    print("dominios documentales  : no asignados")
    print("PostgreSQL              : no modificado")


if __name__ == "__main__":
    main()
