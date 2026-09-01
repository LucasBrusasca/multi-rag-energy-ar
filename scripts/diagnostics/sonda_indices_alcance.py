"""Read-only probe: which retrieval shapes actually use an index, and is the
database ready for the multilabel pilot.

It answers three questions that cannot be answered by reading the code:

1. Does each retrieval shape (A0 by silo, A0 monolithic, A1, A2) use an index
   scan or a sequential scan? If some arms search approximately (HNSW) and
   others exactly (sequential scan), a latency comparison between them measures
   indexing, not architecture — and the returned chunks may differ too, because
   HNSW is approximate.
2. Is migration 002 applicable? Its foreign key needs a UNIQUE constraint on
   chunks.chunk_uid, and a chunk with a NULL chunk_uid could never hold a
   membership.
3. If the pilot tables already exist, how many rows does each version hold.

STRICTLY READ-ONLY. It opens a read-only transaction, uses EXPLAIN without
ANALYZE (so nothing is executed) and never writes. It does not apply any
migration.

[ES] Sonda de solo lectura: qué formas de recuperación usan índice realmente, y
si la base está lista para el piloto multietiqueta.

Responde tres preguntas que no pueden responderse leyendo el código:

1. ¿Cada forma de recuperación (A0 por silo, A0 monolítica, A1, A2) usa índice o
   recorrido secuencial? Si unos brazos buscan de forma aproximada (HNSW) y
   otros de forma exacta (recorrido secuencial), una comparación de latencia
   entre ellos mide indexación, no arquitectura — y los chunks devueltos también
   pueden diferir, porque HNSW es aproximado.
2. ¿La migración 002 es aplicable? Su clave foránea necesita una restricción
   UNIQUE en chunks.chunk_uid, y un chunk con chunk_uid NULL nunca podría tener
   una membresía.
3. Si las tablas del piloto ya existen, cuántas filas tiene cada versión.

ESTRICTAMENTE DE SOLO LECTURA. Abre una transacción de solo lectura, usa EXPLAIN
sin ANALYZE (así no ejecuta nada) y nunca escribe. No aplica ninguna migración.
"""

import argparse
import re

from multirag.config import RETRIEVAL_TOP_K, SILOS
from multirag.db import conectar
from multirag.orchestration.alcance import (
    construir_consulta_vectorial,
    construir_filtro_asignacion,
)


DIMENSION_EMBEDDING = 1024

VERSION_FICTICIA_ASIGNACION = "sonda-assignment-version"

VERSION_FICTICIA_MATERIALIDAD = "sonda-materiality-version"


# Access paths worth naming in the report.
# [ES] Caminos de acceso que vale nombrar en el informe.
PATRON_ACCESO = re.compile(
    r"(?:Parallel )?(?:Seq Scan on \w+"
    r"|Bitmap Heap Scan on \w+"
    r"|Bitmap Index Scan on \w+"
    r"|Index Scan using \w+"
    r"|Index Only Scan using \w+)"
)


# Access methods that answer an ORDER BY approximately.
# [ES] Métodos de acceso que responden un ORDER BY de forma aproximada.
METODOS_VECTORIALES = ("hnsw", "ivfflat")


def vector_ficticio() -> str:
    """A constant vector, only to make the planner produce a plan.

    Nothing is executed, so its value is irrelevant.

    [ES] Un vector constante, solo para que el planificador produzca un plan.

    No se ejecuta nada, así que su valor es irrelevante.
    """
    return "[" + ",".join(["0"] * DIMENSION_EMBEDDING) + "]"


def formas_de_recuperacion(dominio: str, k: int) -> list[tuple[str, dict]]:
    """The retrieval shapes worth comparing, with their assignment arguments.

    [ES] Las formas de recuperación que vale comparar, con sus argumentos de
    asignación.
    """
    return [
        (
            f"A0 por silo ({dominio}) — brazo B1/B2",
            {
                "variante_asignacion": "A0",
                "dominio": dominio,
            },
        ),
        (
            "A0 monolítica (sin filtro) — brazo B0",
            {
                "variante_asignacion": "A0",
                "dominio": None,
            },
        ),
        (
            f"A1 por membresías ({dominio})",
            {
                "variante_asignacion": "A1",
                "dominio": dominio,
                "assignment_version": VERSION_FICTICIA_ASIGNACION,
            },
        ),
        (
            f"A2 con compuerta de materialidad ({dominio})",
            {
                "variante_asignacion": "A2",
                "dominio": dominio,
                "assignment_version": VERSION_FICTICIA_ASIGNACION,
                "materiality_version": VERSION_FICTICIA_MATERIALIDAD,
            },
        ),
        (
            "E1 — consulta de hermanos por document_id",
            {
                "variante_asignacion": "A0",
                "dominio": None,
                "_documentos": ["DOC-EJEMPLO"],
            },
        ),
    ]


def caminos_de_acceso(plan: str) -> list[str]:
    """Access paths the plan uses over `chunks`.

    [ES] Caminos de acceso que el plan usa sobre `chunks`.
    """
    return PATRON_ACCESO.findall(plan)


def ordena_por_distancia(plan: str) -> bool:
    """Whether the plan sorts explicitly by the vector distance.

    An explicit `Sort` over the candidate rows is EXACT ordering: every
    candidate's distance is computed and compared. It is the opposite of
    letting an approximate index return an already ordered stream.

    [ES] Si el plan ordena explícitamente por la distancia vectorial.

    Un `Sort` explícito sobre las filas candidatas es orden EXACTO: se calcula y
    compara la distancia de cada candidata. Es lo contrario de dejar que un
    índice aproximado devuelva un flujo ya ordenado.
    """
    return any(
        "Sort Key:" in linea and "<=>" in linea
        for linea in plan.splitlines()
    )


def usa_indice_vectorial(plan: str, indices_vectoriales) -> bool:
    """Whether the plan reads through an approximate vector index.

    The index must be named as the one serving the scan. Matching a bare
    substring is not enough: `Bitmap Index Scan on chunks_silo_idx` contains
    "Index Scan" and has nothing to do with HNSW.

    [ES] Si el plan lee a través de un índice vectorial aproximado.

    El índice debe aparecer nombrado como el que sirve el recorrido. Buscar una
    subcadena suelta no alcanza: `Bitmap Index Scan on chunks_silo_idx`
    contiene "Index Scan" y no tiene nada que ver con HNSW.
    """
    return any(
        f"using {nombre}" in plan or f"on {nombre}" in plan
        for nombre in indices_vectoriales
    )


def clasificar_plan(plan: str, indices_vectoriales=()) -> str:
    """Say whether the search is exact or approximate, and through what.

    [ES] Dice si la búsqueda es exacta o aproximada, y a través de qué.
    """
    caminos = ", ".join(caminos_de_acceso(plan)) or "sin camino identificado"
    vectorial = usa_indice_vectorial(plan, indices_vectoriales)
    ordena = ordena_por_distancia(plan)

    if vectorial and not ordena:
        return f"APROXIMADA (índice vectorial) — {caminos}"

    if vectorial and ordena:
        return (
            "INDETERMINADA (usa índice vectorial y además ordena por "
            f"distancia) — {caminos}"
        )

    if ordena:
        return f"EXACTA (ordena por distancia las candidatas) — {caminos}"

    return f"indeterminada — {caminos}"


def explicar(cursor, sql: str, params: list) -> str:
    """Return the query plan without executing the query.

    [ES] Devuelve el plan de la consulta sin ejecutarla.
    """
    cursor.execute("EXPLAIN " + sql, params)

    return "\n".join(fila[0] for fila in cursor.fetchall())


def tabla_existe(cursor, nombre: str) -> bool:
    """Whether a table exists in the current database.

    [ES] Si una tabla existe en la base actual.
    """
    cursor.execute("SELECT to_regclass(%s) IS NOT NULL", (nombre,))

    return bool(cursor.fetchone()[0])


def indices_de_chunks(cursor) -> list[str]:
    """Index definitions on the chunks table.

    [ES] Definiciones de índices de la tabla chunks.
    """
    cursor.execute(
        """
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'chunks'
        ORDER BY indexname
        """
    )

    return [
        f"{nombre}: {definicion}"
        for nombre, definicion in cursor.fetchall()
    ]


def indices_vectoriales_de_chunks(cursor) -> list[str]:
    """Names of the approximate vector indexes on chunks.

    [ES] Nombres de los índices vectoriales aproximados sobre chunks.
    """
    cursor.execute(
        """
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'chunks'
        ORDER BY indexname
        """
    )

    return [
        nombre
        for nombre, definicion in cursor.fetchall()
        if any(
            f"using {metodo}" in definicion.lower()
            for metodo in METODOS_VECTORIALES
        )
    ]


def chunk_uid_es_unico(cursor) -> bool:
    """Whether chunks.chunk_uid carries a unique constraint or unique index.

    Migration 002 cannot create its foreign key without it.

    [ES] Si chunks.chunk_uid tiene restricción o índice único.

    La migración 002 no puede crear su clave foránea sin eso.
    """
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM pg_index AS i
            JOIN pg_class AS t ON t.oid = i.indrelid
            JOIN pg_attribute AS a
                ON a.attrelid = t.oid
               AND a.attnum = ANY (i.indkey)
            WHERE t.relname = 'chunks'
              AND a.attname = 'chunk_uid'
              AND i.indisunique
              AND i.indnatts = 1
        )
        """
    )

    return bool(cursor.fetchone()[0])


def conteo_chunks(cursor) -> tuple[int, int]:
    """Total chunks and how many carry no chunk_uid.

    [ES] Chunks totales y cuántos no tienen chunk_uid.
    """
    cursor.execute(
        """
        SELECT count(*), count(*) FILTER (WHERE chunk_uid IS NULL)
        FROM chunks
        """
    )

    return tuple(cursor.fetchone())


def filas_por_version(cursor, tabla: str, columna_version: str) -> list[tuple]:
    """Rows of a pilot table grouped by version and review state.

    [ES] Filas de una tabla del piloto agrupadas por versión y estado de
    revisión.
    """
    cursor.execute(
        f"""
        SELECT {columna_version}, review_status, count(*)
        FROM {tabla}
        GROUP BY {columna_version}, review_status
        ORDER BY {columna_version}, review_status
        """
    )

    return cursor.fetchall()


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    [ES] Construye el analizador de argumentos de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Sonda de solo lectura sobre índices y preparación del piloto "
            "multietiqueta. No escribe ni aplica migraciones."
        )
    )
    parser.add_argument(
        "--dominio",
        default=next(iter(SILOS)),
        choices=tuple(SILOS),
        help="Dominio usado en las formas filtradas.",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=RETRIEVAL_TOP_K,
        help="k de la consulta planificada.",
    )
    parser.add_argument(
        "--planes",
        action="store_true",
        help="Imprime el plan completo de cada forma.",
    )
    return parser


def main() -> None:
    """Run the probe.

    [ES] Ejecuta la sonda.
    """
    argumentos = construir_parser().parse_args()

    literal = vector_ficticio()
    conexion = conectar()

    try:
        with conexion.cursor() as cursor:
            # Read-only transaction: the probe cannot modify the snapshot even
            # by accident.
            # [ES] Transacción de solo lectura: la sonda no puede modificar el
            # snapshot ni por accidente.
            cursor.execute("SET TRANSACTION READ ONLY")

            total, sin_uid = conteo_chunks(cursor)

            print("=== Preparación para la migración 002 ===")
            print(f"chunks totales: {total}")
            print(f"chunks sin chunk_uid: {sin_uid}")

            if sin_uid:
                print(
                    "  ADVERTENCIA: esos chunks no podrían tener membresías "
                    "(la clave foránea apunta a chunk_uid)."
                )

            unico = chunk_uid_es_unico(cursor)

            print(
                "chunk_uid tiene restricción única: "
                + ("sí" if unico else "NO")
            )

            if not unico:
                print(
                    "  BLOQUEANTE: la migración 002 fallaría. Su clave foránea "
                    "exige un índice único de una sola columna sobre "
                    "chunks.chunk_uid."
                )

            existen = {
                tabla: tabla_existe(cursor, tabla)
                for tabla in (
                    "chunk_domain_membership",
                    "chunk_materiality",
                )
            }

            for tabla, existe in existen.items():
                print(
                    f"tabla {tabla}: "
                    + ("existe" if existe else "no existe todavía")
                )

            print("\n=== Índices de chunks ===")

            for definicion in indices_de_chunks(cursor):
                print(f"  {definicion}")

            vectoriales = indices_vectoriales_de_chunks(cursor)

            print(
                "\níndices vectoriales aproximados: "
                + (", ".join(vectoriales) or "ninguno")
            )

            print("\n=== Forma de búsqueda por variante ===")
            print(
                "Si unas variantes buscan de forma aproximada y otras de forma "
                "exacta, la comparación entre ellas mide el método de búsqueda "
                "y no la arquitectura: pueden diferir tanto la latencia como "
                "los chunks devueltos.\n"
            )

            usadas: list[str] = []

            for etiqueta, argumentos_forma in formas_de_recuperacion(
                argumentos.dominio,
                argumentos.k,
            ):
                documentos = argumentos_forma.pop("_documentos", None)

                if (
                    argumentos_forma["variante_asignacion"] != "A0"
                    and not all(existen.values())
                ):
                    print(
                        f"{etiqueta}: no se puede planificar todavía "
                        "(faltan las tablas del piloto)."
                    )
                    continue

                condiciones, parametros = construir_filtro_asignacion(
                    **argumentos_forma
                )

                sql, params = construir_consulta_vectorial(
                    vector_literal=literal,
                    k=argumentos.k,
                    condiciones=condiciones,
                    parametros_filtro=parametros,
                    documentos=documentos,
                )

                plan = explicar(cursor, sql, params)
                clasificacion = clasificar_plan(plan, vectoriales)
                usadas.append(clasificacion.split(" —")[0])

                print(f"{etiqueta}: {clasificacion}")

                if argumentos.planes:
                    for linea in plan.splitlines():
                        print(f"    {linea}")

            distintas = set(usadas)

            print()

            if len(distintas) > 1:
                print(
                    "ATENCIÓN: las formas planificadas NO usan el mismo método "
                    "de búsqueda. Antes de comparar latencia o resultados entre "
                    "ellas hay que igualar la condición o declarar la asimetría."
                )
            else:
                print(
                    "Todas las formas planificadas usan el mismo método de "
                    f"búsqueda ({usadas[0] if usadas else 'ninguna'}), así que "
                    "no introducen asimetría entre sí. Volver a correr esta "
                    "sonda después de crecer el corpus o aplicar la migración "
                    "002: el planificador puede cambiar de camino sin aviso."
                )

            for tabla, columna in (
                ("chunk_domain_membership", "assignment_version"),
                ("chunk_materiality", "materiality_version"),
            ):
                if not existen[tabla]:
                    continue

                print(f"\n=== {tabla} por versión ===")

                filas = filas_por_version(cursor, tabla, columna)

                if not filas:
                    print("  sin filas.")

                for version, estado, cantidad in filas:
                    print(f"  {version} · {estado}: {cantidad}")

        conexion.rollback()
    finally:
        conexion.close()


if __name__ == "__main__":
    main()
