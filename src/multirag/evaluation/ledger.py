"""Write the execution ledger: query -> decision -> evidence -> answer -> veto.

It is the verifiable evidence trail the plan commits to (pp. 6-7). Its purpose
is that, months later, anyone can ask "why did the system answer THIS to THIS
question?" and get an answer from the record instead of running everything
again.

Three design decisions worth stating, because they are what make it usable as
evidence rather than as a log:

1. The run records the frozen configuration, not a description of it. Which
   model, which k, which prompt fingerprint, which classifier recipe. A number
   in the thesis without its configuration is not reproducible.
2. The evidence copies the documentary identity at delivery time. It does not
   point at `chunks`: the ledger of an executed run must survive a
   re-ingestion of the snapshot.
3. The veto stores the flagged spans, not only a score. A veto that cannot be
   inspected cannot be defended.

The functions build the rows and validate them; persisting them is a separate,
explicit step, so the ledger can be assembled and reviewed before touching the
database.

[ES] Escribe el ledger de ejecucion: consulta -> decision -> evidencia ->
respuesta -> veto.

Es la pista de evidencia verificable que compromete el plan (pp. 6-7). Su
proposito es que, meses despues, cualquiera pueda preguntar "por que el sistema
respondio ESTO a ESTA pregunta" y obtener la respuesta del registro, en lugar de
volver a correr todo.

Tres decisiones de diseno que conviene explicitar, porque son las que lo vuelven
utilizable como evidencia y no como un log:

1. La corrida registra la configuracion congelada, no una descripcion de ella.
   Que modelo, que k, que huella de prompt, que receta de clasificador. Un
   numero de la tesis sin su configuracion no es reproducible.
2. La evidencia copia la identidad documental al momento de la entrega. No
   apunta a `chunks`: el ledger de una corrida ejecutada tiene que sobrevivir a
   una reingesta del snapshot.
3. El veto guarda los tramos marcados, no solo un score. Un veto que no se puede
   inspeccionar no se puede defender.

Las funciones arman las filas y las validan; persistirlas es un paso separado y
explicito, para que el ledger pueda armarse y revisarse antes de tocar la base.
"""

import json

from multirag.orchestration.alcance import (
    VARIANTES_ASIGNACION,
    VARIANTES_EXPANSION,
)


ETAPAS = (
    "desarrollo",
    "piloto",
    "confirmatorio",
)

BRAZOS = (
    "B0",
    "B1",
    "B2",
)


class ErrorDeLedger(ValueError):
    """The ledger record is incomplete or inconsistent.

    [ES] El registro del ledger esta incompleto o es inconsistente.
    """


def _exigir(valor, nombre: str):
    """Demand a non-empty value.

    [ES] Exige un valor no vacio.
    """
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ErrorDeLedger(
            f"El ledger exige {nombre}: sin ese dato la corrida no se puede "
            "reconstruir después."
        )

    return valor


def construir_corrida(
    *,
    corrida_id: str,
    brazos,
    k_final: int,
    etapa: str,
    variante_asignacion: str = "A0",
    variante_expansion: str = "E0",
    assignment_version: str | None = None,
    materiality_version: str | None = None,
    receta_clasificador_sha256: str | None = None,
    modelo_generador: str | None = None,
    modelo_router: str | None = None,
    modelo_embedding: str | None = None,
    prompt_generador_sha256: str | None = None,
    veto_mecanismo: str | None = None,
    veto_umbral: float | None = None,
    conjunto_preguntas: str | None = None,
    semilla: int | None = None,
    snapshot: str | None = None,
    observaciones: str | None = None,
) -> dict:
    """Build the row of a run, validating what makes it reconstructible.

    [ES] Arma la fila de una corrida, validando lo que la vuelve
    reconstruible.
    """
    _exigir(corrida_id, "corrida_id")

    if etapa not in ETAPAS:
        raise ErrorDeLedger(
            f"Etapa desconocida: {etapa!r}. Las etapas válidas son "
            + ", ".join(ETAPAS)
            + ". Mezclar desarrollo con confirmatorio invalida el test."
        )

    brazos = list(brazos or [])

    if not brazos:
        raise ErrorDeLedger(
            "Debe declararse al menos un brazo."
        )

    desconocidos = [b for b in brazos if b not in BRAZOS]

    if desconocidos:
        raise ErrorDeLedger(
            "Brazos desconocidos: " + ", ".join(desconocidos)
        )

    if variante_asignacion not in VARIANTES_ASIGNACION:
        raise ErrorDeLedger(
            f"Variante de asignación desconocida: {variante_asignacion!r}."
        )

    if variante_expansion not in VARIANTES_EXPANSION:
        raise ErrorDeLedger(
            f"Variante de expansión desconocida: {variante_expansion!r}."
        )

    if variante_asignacion != "A0" and not assignment_version:
        raise ErrorDeLedger(
            f"La variante {variante_asignacion} exige registrar "
            "assignment_version: sin ella no se sabe qué membresías gobernaron "
            "la corrida."
        )

    if not isinstance(k_final, int) or k_final <= 0:
        raise ErrorDeLedger(
            f"k_final debe ser un entero mayor que cero; se recibió "
            f"{k_final!r}."
        )

    return {
        "corrida_id": corrida_id,
        "brazos": brazos,
        "variante_asignacion": variante_asignacion,
        "variante_expansion": variante_expansion,
        "assignment_version": assignment_version,
        "materiality_version": materiality_version,
        "receta_clasificador_sha256": receta_clasificador_sha256,
        "k_final": k_final,
        "modelo_generador": modelo_generador,
        "modelo_router": modelo_router,
        "modelo_embedding": modelo_embedding,
        "prompt_generador_sha256": prompt_generador_sha256,
        "veto_mecanismo": veto_mecanismo,
        "veto_umbral": veto_umbral,
        "conjunto_preguntas": conjunto_preguntas,
        "etapa": etapa,
        "semilla": semilla,
        "snapshot": snapshot,
        "observaciones": observaciones,
    }


def construir_consulta(
    *,
    corrida_id: str,
    pregunta: str,
    brazo: str,
    item_golden: str | None = None,
    estrato: str | None = None,
    silos_abiertos=None,
    router_scores: dict | None = None,
    router_modo: str | None = None,
    router_entropia: float | None = None,
    router_margen: float | None = None,
    respuesta: str | None = None,
    abstuvo: bool | None = None,
    veto_activado: bool | None = None,
    veto_spans=None,
    faithfulness: float | None = None,
    latencia_ms: int | None = None,
    tokens_entrada: int | None = None,
    tokens_salida: int | None = None,
    costo_usd: float | None = None,
) -> dict:
    """Build the row of one question answered by one arm.

    [ES] Arma la fila de una pregunta respondida por un brazo.
    """
    _exigir(corrida_id, "corrida_id")
    _exigir(pregunta, "pregunta")

    if brazo not in BRAZOS:
        raise ErrorDeLedger(
            f"Brazo desconocido: {brazo!r}. Los brazos son "
            + ", ".join(BRAZOS)
            + "."
        )

    return {
        "corrida_id": corrida_id,
        "item_golden": item_golden,
        "estrato": estrato,
        "pregunta": pregunta,
        "brazo": brazo,
        "silos_abiertos": list(silos_abiertos or []),
        "router_scores": router_scores,
        "router_modo": router_modo,
        "router_entropia": router_entropia,
        "router_margen": router_margen,
        "respuesta": respuesta,
        "abstuvo": abstuvo,
        "veto_activado": veto_activado,
        "veto_spans": list(veto_spans) if veto_spans is not None else None,
        "faithfulness": faithfulness,
        "latencia_ms": latencia_ms,
        "tokens_entrada": tokens_entrada,
        "tokens_salida": tokens_salida,
        "costo_usd": costo_usd,
    }


def construir_evidencia(resultados) -> list[dict]:
    """Build the evidence rows from what retrieval actually delivered.

    The order is the delivered order, and it is preserved: a rank-aware metric
    cannot be computed over an unordered set.

    [ES] Arma las filas de evidencia a partir de lo que la recuperación
    entregó realmente.

    El orden es el de entrega y se conserva: una métrica sensible al rango no
    se puede calcular sobre un conjunto sin orden.
    """
    filas = []

    for posicion, registro in enumerate(resultados, start=1):
        chunk_uid = registro.get("chunk_uid")

        if not chunk_uid:
            raise ErrorDeLedger(
                f"La evidencia en la posición {posicion} no tiene chunk_uid: "
                "sin identidad no se puede auditar qué se entregó."
            )

        filas.append(
            {
                "posicion": posicion,
                "chunk_uid": chunk_uid,
                "document_id": registro.get("document_id"),
                "instrument_id": registro.get("instrument_id"),
                "artifact_id": registro.get("artifact_id"),
                "fuente": registro.get("fuente"),
                "silo": registro.get("silo"),
                "dominios_recuperacion": list(
                    registro.get("dominios_recuperacion") or []
                ),
                "origen_recuperacion": registro.get("origen_recuperacion"),
                "similitud": (
                    float(registro["similitud"])
                    if registro.get("similitud") is not None
                    else None
                ),
            }
        )

    return filas


COLUMNAS_CORRIDA = (
    "corrida_id",
    "brazos",
    "variante_asignacion",
    "variante_expansion",
    "assignment_version",
    "materiality_version",
    "receta_clasificador_sha256",
    "k_final",
    "modelo_generador",
    "modelo_router",
    "modelo_embedding",
    "prompt_generador_sha256",
    "veto_mecanismo",
    "veto_umbral",
    "conjunto_preguntas",
    "etapa",
    "semilla",
    "snapshot",
    "observaciones",
)

COLUMNAS_CONSULTA = (
    "corrida_id",
    "item_golden",
    "estrato",
    "pregunta",
    "brazo",
    "silos_abiertos",
    "router_scores",
    "router_modo",
    "router_entropia",
    "router_margen",
    "respuesta",
    "abstuvo",
    "veto_activado",
    "veto_spans",
    "faithfulness",
    "latencia_ms",
    "tokens_entrada",
    "tokens_salida",
    "costo_usd",
)

COLUMNAS_EVIDENCIA = (
    "consulta_id",
    "posicion",
    "chunk_uid",
    "document_id",
    "instrument_id",
    "artifact_id",
    "fuente",
    "silo",
    "dominios_recuperacion",
    "origen_recuperacion",
    "similitud",
)

# Columns that travel as JSONB and must be serialised before the INSERT.
# [ES] Columnas que viajan como JSONB y hay que serializar antes del INSERT.
COLUMNAS_JSON = (
    "router_scores",
    "veto_spans",
)


def _valores(fila: dict, columnas) -> list:
    """Order the values as the INSERT expects, serialising the JSON ones.

    [ES] Ordena los valores como los espera el INSERT, serializando los que
    son JSON.
    """
    return [
        json.dumps(fila.get(columna), ensure_ascii=False)
        if columna in COLUMNAS_JSON and fila.get(columna) is not None
        else fila.get(columna)
        for columna in columnas
    ]


def _sentencia(tabla: str, columnas, devolver_id: bool = False) -> str:
    """Build the parameterised INSERT.

    [ES] Arma el INSERT parametrizado.
    """
    marcadores = ", ".join(
        "%s::jsonb" if columna in COLUMNAS_JSON else "%s"
        for columna in columnas
    )

    return (
        f"INSERT INTO {tabla} ("
        + ", ".join(columnas)
        + f") VALUES ({marcadores})"
        + (" RETURNING id" if devolver_id else "")
    )


def registrar_corrida(cursor, corrida: dict) -> None:
    """Persist the run. Its configuration is written once and does not change.

    [ES] Persiste la corrida. Su configuración se escribe una vez y no cambia.
    """
    cursor.execute(
        _sentencia("ledger_corrida", COLUMNAS_CORRIDA),
        _valores(corrida, COLUMNAS_CORRIDA),
    )


def registrar_consulta(cursor, consulta: dict, evidencia) -> int:
    """Persist a question with the evidence delivered, in one transaction.

    Returns the id of the query, so the trail can be walked from a number of
    the thesis back to the exact fragments that produced it.

    [ES] Persiste una pregunta con la evidencia entregada, en una sola
    transacción.

    Devuelve el id de la consulta, para poder recorrer la pista desde un número
    de la tesis hasta los fragmentos exactos que lo produjeron.
    """
    cursor.execute(
        _sentencia("ledger_consulta", COLUMNAS_CONSULTA, devolver_id=True),
        _valores(consulta, COLUMNAS_CONSULTA),
    )

    consulta_id = cursor.fetchone()[0]

    for fila in evidencia:
        completa = dict(fila)
        completa["consulta_id"] = consulta_id
        cursor.execute(
            _sentencia("ledger_evidencia", COLUMNAS_EVIDENCIA),
            _valores(completa, COLUMNAS_EVIDENCIA),
        )

    return consulta_id
