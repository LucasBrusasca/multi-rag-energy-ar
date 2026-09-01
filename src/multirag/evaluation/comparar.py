"""Compare the B0, B1 and B2 retrieval arms.

The `B` arms are NOT renamed: they compare retrieval architectures. The
comparison may additionally declare, orthogonally, which assignment variant
(A0/A1/A2) and which documentary expansion variant (E0/E1) it runs under, plus
the membership and materiality versions used. Without those parameters the
behaviour is exactly the historical one.

[ES] Compara los brazos de recuperación B0, B1 y B2.

Los brazos `B` NO se renombran: comparan arquitecturas de recuperación. La
comparación puede además declarar, de forma ortogonal, bajo qué variante de
asignación (A0/A1/A2) y de expansión documental (E0/E1) se ejecuta, junto con
las versiones de membresías y de materialidad utilizadas. Sin esos parámetros
el comportamiento es exactamente el histórico.
"""

import argparse


from multirag.config import RETRIEVAL_TOP_K, SILOS
from multirag.orchestration.alcance import (
    VARIANTE_ASIGNACION_PREDETERMINADA,
    VARIANTE_EXPANSION_PREDETERMINADA,
    kwargs_de_asignacion,
    recuperar,
    validar_variante_asignacion,
    validar_variante_expansion,
)


CARACTERES_VISTA_PREVIA = 300


def cargar_recuperadores():
    """Load the real retrieval functions only when necessary.

    [ES] Carga las funciones reales de recuperación solo cuando son necesarias.
    """
    from multirag.orchestration.retriever import buscar, buscar_ruteado

    return buscar, buscar_ruteado


def comparar_recuperacion(
    pregunta: str,
    silos_oraculo: tuple[str, ...] | list[str],
    k: int = RETRIEVAL_TOP_K,
    buscar_fn=None,
    buscar_ruteado_fn=None,
    variante_asignacion: str = VARIANTE_ASIGNACION_PREDETERMINADA,
    variante_expansion: str = VARIANTE_EXPANSION_PREDETERMINADA,
    assignment_version: str | None = None,
    taxonomy_version: str | None = None,
    materiality_version: str | None = None,
    consulta_procedimental: bool = False,
) -> dict:
    """Run B0, B1 and B2 with the same question and final top-k.

    B0 searches the complete corpus.
    B1 searches the oracle silos.
    B2 uses the real router and gate.

    The declared variants are orthogonal to the arms: `variante_asignacion`
    says how a chunk becomes associated with domains (A0/A1/A2) and
    `variante_expansion` whether documentary expansion is enabled (E0/E1).
    With the default values A0/E0 and no versions, the execution path is
    literally the historical one.

    [ES] Ejecuta B0, B1 y B2 con la misma pregunta y el mismo top-k final.

    Las variantes declaradas son ortogonales a los brazos:
    `variante_asignacion` indica cómo un chunk queda asociado a dominios
    (A0/A1/A2) y `variante_expansion` si se habilita la expansión documental
    (E0/E1). Con los valores predeterminados A0/E0 y sin versiones, el camino
    de ejecución es literalmente el histórico.
    """
    if not pregunta.strip():
        raise ValueError(
            "La pregunta no puede estar vacía."
        )

    if k <= 0:
        raise ValueError(
            "k debe ser mayor que cero."
        )

    if not silos_oraculo:
        raise ValueError(
            "Debe indicarse al menos un silo oráculo."
        )

    silos_desconocidos = [
        silo
        for silo in silos_oraculo
        if silo not in SILOS
    ]

    if silos_desconocidos:
        raise ValueError(
            "Silos oráculo desconocidos: "
            + ", ".join(silos_desconocidos)
        )

    validar_variante_asignacion(variante_asignacion)
    validar_variante_expansion(variante_expansion)

    versiones_declaradas = (
        assignment_version,
        taxonomy_version,
        materiality_version,
    )

    # Historical path: exclusive assignment and no documentary expansion. Kept
    # literally identical so that the current comparison does not change while
    # the multilabel pilot is not measured.
    #
    # [ES] Camino histórico: asignación exclusiva y sin expansión documental.
    # Se conserva literalmente idéntico para que la comparación vigente no
    # cambie mientras el piloto multietiqueta no esté medido.
    camino_historico = (
        variante_asignacion == "A0"
        and variante_expansion == "E0"
        and not any(versiones_declaradas)
        and not consulta_procedimental
    )

    if buscar_fn is None or buscar_ruteado_fn is None:
        buscar_real, buscar_ruteado_real = (
            cargar_recuperadores()
        )
        buscar_fn = buscar_fn or buscar_real
        buscar_ruteado_fn = (
            buscar_ruteado_fn
            or buscar_ruteado_real
        )

    if camino_historico:
        resultados_b0 = buscar_fn(
            pregunta,
            silo=None,
            k=k,
        )

        candidatos_b1 = []

        for silo in silos_oraculo:
            candidatos_b1.extend(
                buscar_fn(
                    pregunta,
                    silo=silo,
                    k=k,
                )
            )

        resultados_b1 = sorted(
            candidatos_b1,
            key=lambda registro: float(
                registro["similitud"]
            ),
            reverse=True,
        )[:k]
    else:
        # Declared path: the same final k, with deduplication by chunk_uid,
        # record of the retrieval domains and, if E1, documentary expansion.
        #
        # [ES] Camino declarado: el mismo k final, con deduplicación por
        # chunk_uid, registro de los dominios de recuperación y, si es E1,
        # expansión documental.
        opciones = kwargs_de_asignacion(
            variante_asignacion=variante_asignacion,
            assignment_version=assignment_version,
            taxonomy_version=taxonomy_version,
            materiality_version=materiality_version,
            consulta_procedimental=consulta_procedimental,
        )

        resultados_b0 = recuperar(
            pregunta=pregunta,
            buscar_fn=buscar_fn,
            dominios=None,
            k=k,
            variante_expansion=variante_expansion,
            **opciones,
        )

        resultados_b1 = recuperar(
            pregunta=pregunta,
            buscar_fn=buscar_fn,
            dominios=silos_oraculo,
            k=k,
            variante_expansion=variante_expansion,
            **opciones,
        )

    # B2 keeps using the real router and gate. Wiring the declared variants
    # into the router is a separate step of the pilot and is not claimed here.
    #
    # [ES] B2 sigue usando el router y el gate reales. Conectar las variantes
    # declaradas dentro del router es un paso posterior del piloto y no se
    # afirma aquí.
    resultados_b2 = buscar_ruteado_fn(
        pregunta,
        k=k,
    )

    return {
        "pregunta": pregunta,
        "k": k,
        "silos_oraculo": list(silos_oraculo),
        "variante_asignacion": variante_asignacion,
        "variante_expansion": variante_expansion,
        "assignment_version": assignment_version,
        "taxonomy_version": taxonomy_version,
        "materiality_version": materiality_version,
        "B0": resultados_b0,
        "B1": resultados_b1,
        "B2": resultados_b2,
    }


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    [ES] Construye el analizador de argumentos de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Compara B0, B1 y B2 utilizando la misma "
            "pregunta y el mismo top-k final."
        )
    )
    parser.add_argument(
        "--pregunta",
        required=True,
        help=(
            "Pregunta que se utilizará "
            "en los tres brazos."
        ),
    )
    parser.add_argument(
        "--silos-oraculo",
        nargs="+",
        required=True,
        choices=tuple(SILOS),
        help=(
            "Silo o silos donde vive la evidencia "
            "de referencia para B1."
        ),
    )
    parser.add_argument(
        "--k",
        type=int,
        default=RETRIEVAL_TOP_K,
        help=(
            "Cantidad final de chunks recuperados por brazo. "
            f"Valor provisional predeterminado: "
            f"{RETRIEVAL_TOP_K}."
        ),
    )
    parser.add_argument(
        "--variante-asignacion",
        default=VARIANTE_ASIGNACION_PREDETERMINADA,
        choices=("A0", "A1", "A2"),
        help=(
            "Cómo queda asociado un chunk a dominios. "
            "A0 usa la columna heredada chunks.silo; "
            "A1 usa las membresías versionadas; "
            "A2 agrega la compuerta de materialidad."
        ),
    )
    parser.add_argument(
        "--variante-expansion",
        default=VARIANTE_EXPANSION_PREDETERMINADA,
        choices=("E0", "E1"),
        help=(
            "Expansión documental. E0 no expande; "
            "E1 habilita hermanos del mismo document_id, "
            "deduplica, rerankea y recorta al mismo k final."
        ),
    )
    parser.add_argument(
        "--assignment-version",
        default=None,
        help=(
            "Versión explícita de las membresías. "
            "Obligatoria con A1 y A2: no se elige "
            "automáticamente la última versión."
        ),
    )
    parser.add_argument(
        "--taxonomy-version",
        default=None,
        help=(
            "Versión de la taxonomía de dominios, si se "
            "quiere restringir la consulta a una."
        ),
    )
    parser.add_argument(
        "--materiality-version",
        default=None,
        help=(
            "Versión explícita de la materialidad. "
            "Obligatoria con A2."
        ),
    )
    parser.add_argument(
        "--consulta-procedimental",
        action="store_true",
        help=(
            "Declara la consulta como explícitamente "
            "procedimental: A2 no aplica la compuerta de "
            "materialidad. No borra ni altera ningún chunk."
        ),
    )
    return parser


def mostrar_resultados(resultado: dict) -> None:
    """Print a readable comparison.

    [ES] Imprime una comparación legible.
    """
    print(
        f"Pregunta: {resultado['pregunta']}"
    )
    print(
        f"k final: {resultado['k']}"
    )
    print(
        "Silos oráculo: "
        + ", ".join(resultado["silos_oraculo"])
    )
    print(
        "Variante de asignación: "
        f"{resultado.get('variante_asignacion')}"
        " · variante de expansión: "
        f"{resultado.get('variante_expansion')}"
    )
    print(
        "assignment_version: "
        f"{resultado.get('assignment_version')}"
        " · taxonomy_version: "
        f"{resultado.get('taxonomy_version')}"
        " · materiality_version: "
        f"{resultado.get('materiality_version')}"
    )

    for brazo in ("B0", "B1", "B2"):
        print(f"\n{brazo}")

        for posicion, registro in enumerate(
            resultado[brazo],
            start=1,
        ):
            similitud = float(
                registro["similitud"]
            )
            titulo = str(
                registro.get("titulo", "")
            ).strip()
            contenido = " ".join(
                str(
                    registro.get("contenido", "")
                ).split()
            )
            vista_previa = contenido[
                :CARACTERES_VISTA_PREVIA
            ]

            if len(contenido) > CARACTERES_VISTA_PREVIA:
                vista_previa += "..."

            dominios = registro.get(
                "dominios_recuperacion"
            )

            print(
                f"{posicion:02d}. "
                f"silo={registro.get('silo')} "
                f"similitud={similitud:.3f}"
            )

            if dominios is not None:
                print(
                    "    dominios de recuperación: "
                    + (", ".join(dominios) or "-")
                    + " · origen: "
                    + str(
                        registro.get(
                            "origen_recuperacion",
                            "",
                        )
                    )
                )

            print(
                f"    fuente: "
                f"{registro.get('fuente', '')}"
            )
            print(
                f"    chunk_uid: "
                f"{registro.get('chunk_uid', '')}"
            )
            print(
                f"    document_id: "
                f"{registro.get('document_id', '')}"
                f" · instrument_id: "
                f"{registro.get('instrument_id', '')}"
                f" · artifact_id: "
                f"{registro.get('artifact_id', '')}"
            )
            print(
                f"    título: {titulo}"
            )
            print(
                f"    contenido: {vista_previa}"
            )


def main() -> None:
    """Run the command-line comparison.

    [ES] Ejecuta la comparación desde la línea de comandos.
    """
    parser = construir_parser()
    argumentos = parser.parse_args()

    resultado = comparar_recuperacion(
        pregunta=argumentos.pregunta,
        silos_oraculo=argumentos.silos_oraculo,
        k=argumentos.k,
        variante_asignacion=argumentos.variante_asignacion,
        variante_expansion=argumentos.variante_expansion,
        assignment_version=argumentos.assignment_version,
        taxonomy_version=argumentos.taxonomy_version,
        materiality_version=argumentos.materiality_version,
        consulta_procedimental=(
            argumentos.consulta_procedimental
        ),
    )

    mostrar_resultados(resultado)


if __name__ == "__main__":
    main()
