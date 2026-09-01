"""Prepare a small, explicit identity catalog for controlled ingestion.

The operation selects already cataloged artifacts and allocates administrative
identifiers after the maxima present in the canonical catalog. It does not
classify domains, interpret the documents, ingest content, or access
PostgreSQL.

[ES] Prepara un catalogo pequeno y explicito de identidades para una ingesta
controlada.

La operacion selecciona artefactos ya catalogados y asigna identificadores
administrativos posteriores a los maximos del catalogo canonico. No clasifica
dominios, no interpreta documentos, no ingiere contenido ni accede a
PostgreSQL.
"""

import argparse
import csv
import re
from pathlib import Path

from multirag.ingestion.vincular_identidad import CAMPOS_IDENTIDAD


PATRON_IDENTIFICADOR = re.compile(r"^(INS|DOC)-([0-9]+)$")


def cargar_filas_csv(ruta: Path) -> list[dict[str, str]]:
    """Load a non-empty UTF-8 CSV file.

    [ES] Carga un archivo CSV UTF-8 no vacio.
    """
    ruta = ruta.resolve()

    if not ruta.is_file():
        raise FileNotFoundError(f"No existe el CSV: {ruta}")

    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)

        if lector.fieldnames is None:
            raise ValueError(f"El CSV no contiene encabezado: {ruta}")

        filas = [
            {
                clave: (valor or "").strip()
                for clave, valor in fila.items()
            }
            for fila in lector
        ]

    if not filas:
        raise ValueError(f"El CSV no contiene filas: {ruta}")

    return filas


def siguiente_numero_identidad(
    filas_existentes: list[dict[str, str]],
    campo: str,
    prefijo: str,
) -> int:
    """Return the integer immediately after the largest registered ID.

    [ES] Devuelve el entero posterior al mayor ID registrado.
    """
    numeros = []

    for fila in filas_existentes:
        valor = fila.get(campo, "").strip()

        if not valor:
            continue

        coincidencia = PATRON_IDENTIFICADOR.fullmatch(valor)

        if coincidencia is None or coincidencia.group(1) != prefijo:
            raise ValueError(
                f"El campo {campo} contiene un identificador invalido: "
                f"{valor}"
            )

        numeros.append(int(coincidencia.group(2)))

    return max(numeros, default=0) + 1


def seleccionar_candidatos(
    candidatos: list[dict[str, str]],
    fuentes: list[str],
) -> list[dict[str, str]]:
    """Select candidates in the exact order requested by the operator.

    [ES] Selecciona candidatos en el orden exacto pedido por el operador.
    """
    fuentes_limpias = [fuente.strip() for fuente in fuentes]

    if any(not fuente for fuente in fuentes_limpias):
        raise ValueError("La seleccion contiene una fuente vacia.")

    if len(fuentes_limpias) != len(set(fuentes_limpias)):
        raise ValueError("La seleccion contiene fuentes repetidas.")

    indice: dict[str, dict[str, str]] = {}

    for candidato in candidatos:
        fuente = candidato.get("fuente", "").strip()

        if not fuente:
            raise ValueError("Existe un candidato sin fuente.")

        if fuente in indice:
            raise ValueError(f"La fuente candidata esta repetida: {fuente}")

        indice[fuente] = candidato

    faltantes = [fuente for fuente in fuentes_limpias if fuente not in indice]

    if faltantes:
        raise ValueError(f"Las fuentes no existen entre los candidatos: {faltantes}")

    return [indice[fuente] for fuente in fuentes_limpias]


def construir_identidades_piloto(
    candidatos: list[dict[str, str]],
    existentes: list[dict[str, str]],
    fuentes: list[str],
) -> list[dict[str, str]]:
    """Allocate one new instrument and document identity per selected source.

    This function is appropriate for a pilot whose selected artifacts were
    manually confirmed to represent distinct normative instruments. Reusing
    an instrument across editions requires explicit curation and is outside
    this allocator.

    [ES] Asigna una nueva identidad de instrumento y documento por cada fuente
    seleccionada.

    La funcion corresponde a un piloto cuyos artefactos fueron confirmados
    manualmente como instrumentos normativos distintos. Reutilizar un
    instrumento entre ediciones requiere curacion explicita y queda fuera de
    este asignador.
    """
    seleccionados = seleccionar_candidatos(candidatos, fuentes)
    siguiente_instrumento = siguiente_numero_identidad(
        existentes,
        campo="instrument_id",
        prefijo="INS",
    )
    siguiente_documento = siguiente_numero_identidad(
        existentes,
        campo="document_id",
        prefijo="DOC",
    )
    artifact_ids_existentes = {
        fila.get("artifact_id", "").strip()
        for fila in existentes
        if fila.get("artifact_id", "").strip()
    }
    fuentes_existentes = {
        fila.get("fuente", "").strip()
        for fila in existentes
        if fila.get("fuente", "").strip()
    }
    identidades = []

    for desplazamiento, candidato in enumerate(seleccionados):
        fuente = candidato.get("fuente", "").strip()
        artifact_id = candidato.get("artifact_id", "").strip()

        if not artifact_id:
            raise ValueError(f"El candidato {fuente} no tiene artifact_id.")

        if fuente in fuentes_existentes:
            raise ValueError(f"La fuente ya existe en el catalogo canonico: {fuente}")

        if artifact_id in artifact_ids_existentes:
            raise ValueError(
                "El artefacto ya existe en el catalogo canonico: "
                f"{artifact_id}"
            )

        identidades.append(
            {
                "instrument_id": f"INS-{siguiente_instrumento + desplazamiento:04d}",
                "document_id": f"DOC-{siguiente_documento + desplazamiento:04d}",
                "artifact_id": artifact_id,
                "fuente": fuente,
            }
        )

    return identidades


def guardar_identidades(
    identidades: list[dict[str, str]],
    ruta_salida: Path,
) -> Path:
    """Persist the identity catalog atomically without overwriting files.

    [ES] Persiste atomicamente el catalogo sin sobrescribir archivos.
    """
    ruta_salida = ruta_salida.resolve()

    if ruta_salida.exists():
        raise FileExistsError(f"El catalogo piloto ya existe: {ruta_salida}")

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_temporal = ruta_salida.with_name(f".{ruta_salida.name}.tmp")

    try:
        with ruta_temporal.open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(
                archivo,
                fieldnames=CAMPOS_IDENTIDAD,
                lineterminator="\n",
            )
            escritor.writeheader()
            escritor.writerows(identidades)

        ruta_temporal.replace(ruta_salida)
    finally:
        if ruta_temporal.exists():
            ruta_temporal.unlink()

    return ruta_salida


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line contract.

    [ES] Construye el contrato de linea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Genera un catalogo de identidad separado para una ingesta "
            "piloto; no asigna dominios ni toca PostgreSQL."
        )
    )
    parser.add_argument("--candidatos", type=Path, required=True)
    parser.add_argument("--existentes", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument(
        "--fuente",
        action="append",
        required=True,
        help="Fuente candidata que se incluira; se puede repetir.",
    )
    return parser


def main() -> None:
    """Prepare the pilot catalog requested on the command line.

    [ES] Prepara el catalogo piloto solicitado por linea de comandos.
    """
    parser = construir_parser()
    argumentos = parser.parse_args()

    try:
        candidatos = cargar_filas_csv(argumentos.candidatos)
        existentes = cargar_filas_csv(argumentos.existentes)
        identidades = construir_identidades_piloto(
            candidatos=candidatos,
            existentes=existentes,
            fuentes=argumentos.fuente,
        )
        salida = guardar_identidades(identidades, argumentos.salida)
    except (FileExistsError, FileNotFoundError, ValueError) as error:
        parser.error(str(error))

    print(f"identidades creadas : {len(identidades)}")
    for identidad in identidades:
        print(
            f"  - {identidad['fuente']}: "
            f"{identidad['instrument_id']} / {identidad['document_id']}"
        )
    print(f"salida              : {salida}")
    print("dominios            : no asignados")
    print("PostgreSQL          : no modificado")


if __name__ == "__main__":
    main()
