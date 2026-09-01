"""Link persisted chunks with the curated documentary identity catalog.

The source name is used only as a transitional bridge for historical chunks.
Stable traceability is provided by instrument_id, document_id and artifact_id.

[ES] Vincula los chunks persistidos con el catálogo curado de identidad
documental.

El nombre de fuente se utiliza únicamente como puente transitorio para los
chunks históricos. La trazabilidad estable queda representada mediante
instrument_id, document_id y artifact_id.
"""

import argparse
import csv
from pathlib import Path

from psycopg2.extras import execute_values


from multirag.db import conectar
from multirag.paths import DATA_DIR


RUTA_METADATOS_PREDETERMINADA = (
    DATA_DIR
    / "catalog"
    / "metadatos_curados.csv"
)

CAMPOS_IDENTIDAD = (
    "instrument_id",
    "document_id",
    "artifact_id",
    "fuente",
)


def cargar_identidades_por_fuente(
    ruta_metadatos: Path,
) -> dict[str, dict[str, str]]:
    """Load and validate documentary identities indexed by source name.

    [ES] Carga y valida las identidades documentales indexadas por fuente.
    """

    ruta_metadatos = ruta_metadatos.resolve()

    if not ruta_metadatos.is_file():
        raise FileNotFoundError(
            f"No existe el catálogo curado: {ruta_metadatos}"
        )

    identidades: dict[str, dict[str, str]] = {}
    artifact_ids: set[str] = set()

    with ruta_metadatos.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as archivo:
        lector = csv.DictReader(archivo)

        if lector.fieldnames is None:
            raise ValueError(
                "El catálogo curado no contiene encabezado."
            )

        campos_faltantes = [
            campo
            for campo in CAMPOS_IDENTIDAD
            if campo not in lector.fieldnames
        ]

        if campos_faltantes:
            raise ValueError(
                "Faltan columnas de identidad en el catálogo: "
                f"{campos_faltantes}"
            )

        for numero_linea, fila in enumerate(lector, start=2):
            identidad = {
                campo: (fila.get(campo) or "").strip()
                for campo in CAMPOS_IDENTIDAD
            }

            valores_vacios = [
                campo
                for campo, valor in identidad.items()
                if not valor
            ]

            if valores_vacios:
                raise ValueError(
                    f"La línea {numero_linea} tiene campos "
                    f"de identidad vacíos: {valores_vacios}"
                )

            fuente = identidad["fuente"]
            artifact_id = identidad["artifact_id"]

            if fuente in identidades:
                raise ValueError(
                    "La fuente aparece más de una vez en el "
                    f"catálogo curado: {fuente}"
                )

            if artifact_id in artifact_ids:
                raise ValueError(
                    "El artifact_id aparece más de una vez en el "
                    f"catálogo curado: {artifact_id}"
                )

            identidades[fuente] = identidad
            artifact_ids.add(artifact_id)

    return identidades


def obtener_chunks_por_fuente(
    conexion,
) -> dict[str, int]:
    """Count persisted chunks grouped by their historical source name.

    [ES] Cuenta los chunks persistidos agrupados por su nombre histórico
    de fuente.
    """

    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT fuente, COUNT(*)
            FROM chunks
            GROUP BY fuente
            ORDER BY fuente
            """
        )
        filas = cursor.fetchall()

    if any(fuente is None for fuente, _ in filas):
        raise ValueError(
            "Existen chunks sin fuente y no pueden vincularse "
            "automáticamente."
        )

    return {
        str(fuente): int(cantidad)
        for fuente, cantidad in filas
    }


def construir_plan_vinculacion(
    chunks_por_fuente: dict[str, int],
    identidades_por_fuente: dict[str, dict[str, str]],
) -> tuple[list[tuple[str, str, str, str]], list[str]]:
    """Build the identity update plan without modifying PostgreSQL.

    [ES] Construye el plan de actualización de identidades sin modificar
    PostgreSQL.
    """

    fuentes_sin_identidad = sorted(
        set(chunks_por_fuente)
        - set(identidades_por_fuente)
    )

    if fuentes_sin_identidad:
        raise ValueError(
            "Hay fuentes persistidas sin identidad curada: "
            f"{fuentes_sin_identidad}"
        )

    fuentes_no_ingeridas = sorted(
        set(identidades_por_fuente)
        - set(chunks_por_fuente)
    )

    plan = []

    for fuente in sorted(chunks_por_fuente):
        identidad = identidades_por_fuente[fuente]

        plan.append(
            (
                fuente,
                identidad["instrument_id"],
                identidad["document_id"],
                identidad["artifact_id"],
            )
        )

    return plan, fuentes_no_ingeridas


def aplicar_plan_vinculacion(
    conexion,
    plan: list[tuple[str, str, str, str]],
    cantidad_esperada: int,
) -> int:
    """Apply the documentary identities atomically.

    Existing non-null identities are never silently replaced by different
    values.

    [ES] Aplica atómicamente las identidades documentales.

    Las identidades existentes no nulas nunca son reemplazadas
    silenciosamente por valores diferentes.
    """

    if not plan:
        return 0

    with conexion:
        with conexion.cursor() as cursor:
            resultado = execute_values(
                cursor,
                """
                UPDATE chunks AS chunk
                SET instrument_id = identidad.instrument_id,
                    document_id = identidad.document_id,
                    artifact_id = identidad.artifact_id
                FROM (VALUES %s) AS identidad(
                    fuente,
                    instrument_id,
                    document_id,
                    artifact_id
                )
                WHERE chunk.fuente = identidad.fuente
                  AND (
                      chunk.instrument_id IS NULL
                      OR chunk.instrument_id = identidad.instrument_id
                  )
                  AND (
                      chunk.document_id IS NULL
                      OR chunk.document_id = identidad.document_id
                  )
                  AND (
                      chunk.artifact_id IS NULL
                      OR chunk.artifact_id = identidad.artifact_id
                  )
                RETURNING chunk.id
                """,
                plan,
                fetch=True,
            )

            cantidad_actualizada = len(resultado)

            if cantidad_actualizada != cantidad_esperada:
                raise RuntimeError(
                    "La actualización fue cancelada porque existen "
                    "chunks con identidades incompatibles. "
                    f"Esperados: {cantidad_esperada}. "
                    f"Actualizables: {cantidad_actualizada}."
                )

    return cantidad_actualizada


def construir_parser_argumentos() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    [ES] Construye el analizador de argumentos de línea de comandos.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Vincula los chunks existentes con la identidad documental "
            "del catálogo curado."
        )
    )
    parser.add_argument(
        "--metadatos",
        type=Path,
        default=RUTA_METADATOS_PREDETERMINADA,
        help=(
            "Ruta del catálogo curado CSV. Por defecto se utiliza "
            "data/catalog/metadatos_curados.csv."
        ),
    )
    parser.add_argument(
        "--aplicar",
        action="store_true",
        help=(
            "Aplica la vinculación en PostgreSQL. Si se omite, "
            "solo se realiza una simulación."
        ),
    )

    return parser


def main() -> None:
    """Validate, plan and optionally apply the documentary linkage.

    [ES] Valida, planifica y opcionalmente aplica la vinculación
    documental.
    """

    parser = construir_parser_argumentos()
    argumentos = parser.parse_args()

    identidades_por_fuente = cargar_identidades_por_fuente(
        argumentos.metadatos
    )

    conexion = conectar()

    try:
        chunks_por_fuente = obtener_chunks_por_fuente(conexion)
        plan, fuentes_no_ingeridas = construir_plan_vinculacion(
            chunks_por_fuente=chunks_por_fuente,
            identidades_por_fuente=identidades_por_fuente,
        )

        cantidad_chunks = sum(chunks_por_fuente.values())

        print(
            f"Identidades disponibles: "
            f"{len(identidades_por_fuente)}"
        )
        print(
            f"Fuentes persistidas vinculables: "
            f"{len(plan)}"
        )
        print(f"Chunks vinculables: {cantidad_chunks}")
        print(
            f"Fuentes catalogadas aún no ingeridas: "
            f"{len(fuentes_no_ingeridas)}"
        )

        for fuente in fuentes_no_ingeridas:
            print(f"  - {fuente}")

        if not argumentos.aplicar:
            print(
                "SIMULACIÓN: no se modificó PostgreSQL. "
                "Utilice --aplicar para confirmar."
            )
            return

        cantidad_actualizada = aplicar_plan_vinculacion(
            conexion=conexion,
            plan=plan,
            cantidad_esperada=cantidad_chunks,
        )

        print(
            f"VINCULACIÓN APLICADA: "
            f"{cantidad_actualizada} chunks actualizados."
        )
    finally:
        conexion.close()


if __name__ == "__main__":
    main()
