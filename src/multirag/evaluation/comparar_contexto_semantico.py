"""Compare two provisional semantic-assignment arms.

The comparison verifies experimental compatibility and describes transitions
between both arms. Without an independent curated reference, its results
measure sensitivity to the changed policy, not classification accuracy.

[ES] Compara dos brazos de asignación semántica provisional.

La comparación verifica compatibilidad experimental y describe las
transiciones entre ambos brazos. Sin una referencia curada independiente,
los resultados miden sensibilidad a la política modificada, no exactitud.
"""

import argparse
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path


CAMPOS_REQUERIDOS = {
    "version_propuesta",
    "politica_contexto",
    "orden_anotacion",
    "chunk_uid",
    "estado_asignacion",
    "dominios_propuestos",
    "materialidad_propuesta",
    "confianza_autodeclarada",
    "requiere_revision_experta",
    "contexto_proporcionado",
    "rol_modelo",
    "modelo",
    "prompt_sha256",
}


def calcular_sha256(ruta: Path) -> str:
    """Calculate the SHA-256 digest of one artifact.

    [ES] Calcula la huella SHA-256 de un artefacto.
    """
    huella = hashlib.sha256()

    with ruta.open("rb") as archivo:
        for bloque in iter(
            lambda: archivo.read(1024 * 1024),
            b"",
        ):
            huella.update(bloque)

    return huella.hexdigest()


def validar_registro(
    registro: object,
    numero_linea: int,
) -> dict[str, object]:
    """Validate one semantic-assignment record.

    [ES] Valida un registro de asignación semántica.
    """
    if not isinstance(registro, dict):
        raise ValueError(
            f"La línea {numero_linea} no contiene un objeto JSON."
        )

    faltantes = CAMPOS_REQUERIDOS.difference(registro)

    if faltantes:
        raise ValueError(
            f"A la línea {numero_linea} le faltan campos: "
            f"{sorted(faltantes)}"
        )

    chunk_uid = registro["chunk_uid"]

    if not isinstance(chunk_uid, str) or not chunk_uid.strip():
        raise ValueError(
            f"La línea {numero_linea} tiene un chunk_uid inválido."
        )

    orden = registro["orden_anotacion"]

    if isinstance(orden, bool) or not isinstance(orden, int):
        raise ValueError(
            f"La línea {numero_linea} tiene un orden inválido."
        )

    dominios = registro["dominios_propuestos"]

    if (
        not isinstance(dominios, list)
        or any(not isinstance(dominio, str) for dominio in dominios)
    ):
        raise ValueError(
            f"La línea {numero_linea} tiene dominios inválidos."
        )

    confianza = registro["confianza_autodeclarada"]

    if (
        isinstance(confianza, bool)
        or not isinstance(confianza, (int, float))
        or not 0 <= confianza <= 1
    ):
        raise ValueError(
            f"La línea {numero_linea} tiene confianza inválida."
        )

    if not isinstance(
        registro["requiere_revision_experta"],
        bool,
    ):
        raise ValueError(
            f"La línea {numero_linea} tiene revisión inválida."
        )

    if not isinstance(
        registro["contexto_proporcionado"],
        list,
    ):
        raise ValueError(
            f"La línea {numero_linea} tiene contexto inválido."
        )

    return registro


def cargar_jsonl(ruta: Path) -> list[dict[str, object]]:
    """Load and validate one JSONL assignment artifact.

    [ES] Carga y valida un artefacto JSONL de asignaciones.
    """
    ruta_resuelta = ruta.resolve()

    if not ruta_resuelta.is_file():
        raise FileNotFoundError(
            f"No existe el artefacto: {ruta_resuelta}"
        )

    lineas = ruta_resuelta.read_text(
        encoding="utf-8"
    ).splitlines()

    if not lineas:
        raise ValueError(
            f"El artefacto está vacío: {ruta_resuelta}"
        )

    registros = []
    chunk_uids: set[str] = set()
    ordenes: set[int] = set()

    for numero_linea, linea in enumerate(
        lineas,
        start=1,
    ):
        if not linea.strip():
            raise ValueError(
                f"La línea {numero_linea} está vacía."
            )

        try:
            objeto = json.loads(linea)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"JSON inválido en la línea {numero_linea}: "
                f"{error}"
            ) from error

        registro = validar_registro(
            objeto,
            numero_linea,
        )
        chunk_uid = str(registro["chunk_uid"])
        orden = int(registro["orden_anotacion"])

        if chunk_uid in chunk_uids:
            raise ValueError(
                f"chunk_uid repetido: {chunk_uid}"
            )

        if orden in ordenes:
            raise ValueError(
                f"orden_anotacion repetido: {orden}"
            )

        chunk_uids.add(chunk_uid)
        ordenes.add(orden)
        registros.append(registro)

    return sorted(
        registros,
        key=lambda registro: int(
            registro["orden_anotacion"]
        ),
    )


def obtener_valor_unico(
    registros: list[dict[str, object]],
    campo: str,
) -> object:
    """Return one invariant value shared by all records.

    [ES] Devuelve un valor invariante compartido por los registros.
    """
    valores = {
        json.dumps(
            registro[campo],
            ensure_ascii=False,
            sort_keys=True,
        )
        for registro in registros
    }

    if len(valores) != 1:
        raise ValueError(
            f"El campo {campo!r} no es constante en el brazo."
        )

    return registros[0][campo]


def normalizar_dominios(
    registro: dict[str, object],
) -> tuple[str, ...]:
    """Return a deterministic domain tuple.

    [ES] Devuelve una tupla determinista de dominios.
    """
    return tuple(
        sorted(
            str(dominio)
            for dominio in registro["dominios_propuestos"]
        )
    )


def resumir_brazo(
    registros: list[dict[str, object]],
) -> dict[str, object]:
    """Summarize one arm without interpreting it as accuracy.

    [ES] Resume un brazo sin interpretarlo como exactitud.
    """
    confianzas = [
        float(registro["confianza_autodeclarada"])
        for registro in registros
    ]

    estados = Counter(
        str(registro["estado_asignacion"])
        for registro in registros
    )
    materialidades = Counter(
        str(registro["materialidad_propuesta"])
        for registro in registros
    )
    combinaciones_dominios = Counter(
        "|".join(normalizar_dominios(registro))
        or "sin_dominio"
        for registro in registros
    )

    return {
        "cantidad_registros": len(registros),
        "politica_contexto": obtener_valor_unico(
            registros,
            "politica_contexto",
        ),
        "estados": dict(sorted(estados.items())),
        "materialidades": dict(
            sorted(materialidades.items())
        ),
        "combinaciones_dominios": dict(
            sorted(combinaciones_dominios.items())
        ),
        "requieren_revision_experta": sum(
            bool(registro["requiere_revision_experta"])
            for registro in registros
        ),
        "asignaciones_multidominio": sum(
            len(normalizar_dominios(registro)) > 1
            for registro in registros
        ),
        "contextos_proporcionados": sum(
            bool(registro["contexto_proporcionado"])
            for registro in registros
        ),
        "cantidad_total_vecinos": sum(
            len(registro["contexto_proporcionado"])
            for registro in registros
        ),
        "confianza_media_autodeclarada": statistics.mean(
            confianzas
        ),
        "confianza_mediana_autodeclarada": statistics.median(
            confianzas
        ),
    }


def validar_compatibilidad(
    brazo_a: list[dict[str, object]],
    brazo_b: list[dict[str, object]],
) -> None:
    """Validate that both arms form a paired comparison.

    [ES] Valida que ambos brazos formen una comparación pareada.
    """
    ids_a = {
        str(registro["chunk_uid"])
        for registro in brazo_a
    }
    ids_b = {
        str(registro["chunk_uid"])
        for registro in brazo_b
    }

    if ids_a != ids_b:
        faltan_en_b = sorted(ids_a.difference(ids_b))
        faltan_en_a = sorted(ids_b.difference(ids_a))

        raise ValueError(
            "Los brazos no contienen los mismos chunks. "
            f"Faltan en B={faltan_en_b}; "
            f"faltan en A={faltan_en_a}."
        )

    mapa_b = {
        str(registro["chunk_uid"]): registro
        for registro in brazo_b
    }

    for registro_a in brazo_a:
        chunk_uid = str(registro_a["chunk_uid"])
        registro_b = mapa_b[chunk_uid]

        if (
            registro_a["orden_anotacion"]
            != registro_b["orden_anotacion"]
        ):
            raise ValueError(
                f"El orden difiere para el chunk {chunk_uid}."
            )

    for campo in (
        "version_propuesta",
        "rol_modelo",
        "modelo",
    ):
        valor_a = obtener_valor_unico(
            brazo_a,
            campo,
        )
        valor_b = obtener_valor_unico(
            brazo_b,
            campo,
        )

        if valor_a != valor_b:
            raise ValueError(
                f"Los brazos difieren en {campo!r}: "
                f"{valor_a!r} frente a {valor_b!r}."
            )

    politica_a = obtener_valor_unico(
        brazo_a,
        "politica_contexto",
    )
    politica_b = obtener_valor_unico(
        brazo_b,
        "politica_contexto",
    )

    if politica_a == politica_b:
        raise ValueError(
            "Los brazos declaran la misma política de contexto."
        )


def comparar_brazos(
    brazo_a: list[dict[str, object]],
    brazo_b: list[dict[str, object]],
) -> dict[str, object]:
    """Compare paired decisions and confidence descriptively.

    [ES] Compara descriptivamente decisiones pareadas y confianza.
    """
    validar_compatibilidad(
        brazo_a,
        brazo_b,
    )

    mapa_b = {
        str(registro["chunk_uid"]): registro
        for registro in brazo_b
    }

    transiciones = []
    cambios_etiqueta = 0
    cambios_revision = 0
    aumentos_confianza = 0
    disminuciones_confianza = 0
    confianzas_iguales = 0

    for registro_a in brazo_a:
        chunk_uid = str(registro_a["chunk_uid"])
        registro_b = mapa_b[chunk_uid]

        dominios_a = normalizar_dominios(registro_a)
        dominios_b = normalizar_dominios(registro_b)

        cambio_etiqueta = any(
            (
                registro_a["estado_asignacion"]
                != registro_b["estado_asignacion"],
                dominios_a != dominios_b,
                registro_a["materialidad_propuesta"]
                != registro_b["materialidad_propuesta"],
            )
        )
        cambio_revision = (
            registro_a["requiere_revision_experta"]
            != registro_b["requiere_revision_experta"]
        )

        confianza_a = float(
            registro_a["confianza_autodeclarada"]
        )
        confianza_b = float(
            registro_b["confianza_autodeclarada"]
        )
        delta_confianza = confianza_b - confianza_a

        if cambio_etiqueta:
            cambios_etiqueta += 1

        if cambio_revision:
            cambios_revision += 1

        if delta_confianza > 0:
            aumentos_confianza += 1
        elif delta_confianza < 0:
            disminuciones_confianza += 1
        else:
            confianzas_iguales += 1

        transiciones.append(
            {
                "orden_anotacion": registro_a[
                    "orden_anotacion"
                ],
                "chunk_uid": chunk_uid,
                "brazo_a": {
                    "estado_asignacion": registro_a[
                        "estado_asignacion"
                    ],
                    "dominios_propuestos": list(dominios_a),
                    "materialidad_propuesta": registro_a[
                        "materialidad_propuesta"
                    ],
                    "requiere_revision_experta": registro_a[
                        "requiere_revision_experta"
                    ],
                    "confianza_autodeclarada": confianza_a,
                    "cantidad_vecinos": len(
                        registro_a["contexto_proporcionado"]
                    ),
                },
                "brazo_b": {
                    "estado_asignacion": registro_b[
                        "estado_asignacion"
                    ],
                    "dominios_propuestos": list(dominios_b),
                    "materialidad_propuesta": registro_b[
                        "materialidad_propuesta"
                    ],
                    "requiere_revision_experta": registro_b[
                        "requiere_revision_experta"
                    ],
                    "confianza_autodeclarada": confianza_b,
                    "cantidad_vecinos": len(
                        registro_b["contexto_proporcionado"]
                    ),
                },
                "cambio_etiqueta": cambio_etiqueta,
                "cambio_revision": cambio_revision,
                "delta_confianza_autodeclarada": delta_confianza,
            }
        )

    return {
        "cantidad_pares": len(transiciones),
        "coincidencias_de_etiqueta": (
            len(transiciones) - cambios_etiqueta
        ),
        "cambios_de_etiqueta": cambios_etiqueta,
        "cambios_de_revision": cambios_revision,
        "aumentos_de_confianza_autodeclarada": (
            aumentos_confianza
        ),
        "disminuciones_de_confianza_autodeclarada": (
            disminuciones_confianza
        ),
        "confianzas_autodeclaradas_iguales": (
            confianzas_iguales
        ),
        "transiciones": transiciones,
    }


def construir_informe(
    ruta_a: Path,
    ruta_b: Path,
) -> dict[str, object]:
    """Build the reproducible exploratory comparison report.

    [ES] Construye el informe exploratorio reproducible.
    """
    brazo_a = cargar_jsonl(ruta_a)
    brazo_b = cargar_jsonl(ruta_b)
    comparacion = comparar_brazos(
        brazo_a,
        brazo_b,
    )

    return {
        "estado": "exploratorio_sin_verdad_curada",
        "restriccion_interpretativa": (
            "La comparación mide sensibilidad a la política de "
            "contexto. Sin una referencia independiente no mide "
            "exactitud ni demuestra que un brazo sea superior."
        ),
        "compatibilidad": {
            "version_propuesta": obtener_valor_unico(
                brazo_a,
                "version_propuesta",
            ),
            "rol_modelo": obtener_valor_unico(
                brazo_a,
                "rol_modelo",
            ),
            "modelo": obtener_valor_unico(
                brazo_a,
                "modelo",
            ),
            "mismos_chunks": True,
            "comparacion_pareada": True,
        },
        "artefactos_entrada": {
            "brazo_a": {
                "ruta": str(ruta_a.resolve()),
                "sha256": calcular_sha256(
                    ruta_a.resolve()
                ),
            },
            "brazo_b": {
                "ruta": str(ruta_b.resolve()),
                "sha256": calcular_sha256(
                    ruta_b.resolve()
                ),
            },
        },
        "resumen_brazo_a": resumir_brazo(brazo_a),
        "resumen_brazo_b": resumir_brazo(brazo_b),
        "comparacion": comparacion,
    }


def guardar_informe(
    informe: dict[str, object],
    ruta_salida: Path,
) -> Path:
    """Save the report atomically without overwriting.

    [ES] Guarda el informe atómicamente sin sobrescribir.
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
            json.dumps(
                informe,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
            newline="\n",
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
            "Compara dos brazos pareados de asignación semántica "
            "sin afirmar exactitud."
        )
    )
    parser.add_argument(
        "--brazo-a",
        type=Path,
        required=True,
        help="Primer artefacto JSONL.",
    )
    parser.add_argument(
        "--brazo-b",
        type=Path,
        required=True,
        help="Segundo artefacto JSONL.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        required=True,
        help="Informe JSON nuevo.",
    )
    return parser


def main() -> None:
    """Run and persist the paired comparison.

    [ES] Ejecuta y persiste la comparación pareada.
    """
    argumentos = construir_parser().parse_args()

    try:
        informe = construir_informe(
            ruta_a=argumentos.brazo_a,
            ruta_b=argumentos.brazo_b,
        )
        salida = guardar_informe(
            informe=informe,
            ruta_salida=argumentos.salida,
        )
    except (
        FileExistsError,
        FileNotFoundError,
        ValueError,
    ) as error:
        raise SystemExit(f"ERROR: {error}") from error

    resumen_a = informe["resumen_brazo_a"]
    resumen_b = informe["resumen_brazo_b"]
    comparacion = informe["comparacion"]

    print(
        "Políticas          : "
        f"{resumen_a['politica_contexto']} -> "
        f"{resumen_b['politica_contexto']}"
    )
    print(
        f"Pares comparados   : "
        f"{comparacion['cantidad_pares']}"
    )
    print(
        f"Cambios etiqueta   : "
        f"{comparacion['cambios_de_etiqueta']}"
    )
    print(
        f"Cambios revisión   : "
        f"{comparacion['cambios_de_revision']}"
    )
    print(
        f"Revisión experta   : "
        f"{resumen_a['requieren_revision_experta']} -> "
        f"{resumen_b['requieren_revision_experta']}"
    )
    print(
        "Interpretación     : sensibilidad, no exactitud"
    )
    print(f"Informe            : {salida}")
    print("PostgreSQL         : no consultado")


if __name__ == "__main__":
    main()