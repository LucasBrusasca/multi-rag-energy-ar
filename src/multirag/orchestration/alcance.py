"""Retrievable scope: assignment variants A0/A1/A2 and documentary expansion E0/E1.

This module holds the part of retrieval that does NOT touch PostgreSQL: variant
validation, the SQL filter of the assignment variant, deduplication by
`chunk_uid`, documentary expansion and the final trim to `k`. `retriever.py`
supplies the actual database access.

Two independent dimensions:

- assignment (A): how a chunk becomes associated with domains.
  A0 = one mandatory label, read from the legacy column `chunks.silo`.
  A1 = calibrated set of domains, read from `chunk_domain_membership` under an
       explicit `assignment_version`.
  A2 = A1 plus the materiality gate of `chunk_materiality`.
- expansion (E): how the candidate set grows before reranking.
  E0 = no expansion. E1 = siblings of the same `document_id` are enabled.

E1 is NOT called A2: A2 already designates the materiality gate.

Neither dimension may grant a variant more final context than another: every
path ends with the same final `k`.

[ES] Alcance recuperable: variantes de asignación A0/A1/A2 y expansión
documental E0/E1.

Este módulo contiene la parte de la recuperación que NO toca PostgreSQL:
validación de variantes, filtro SQL de la variante de asignación,
deduplicación por `chunk_uid`, expansión documental y recorte final a `k`.
`retriever.py` aporta el acceso real a la base.

Dos dimensiones independientes:

- asignación (A): cómo un chunk queda asociado a dominios.
  A0 = una etiqueta obligatoria, leída de la columna heredada `chunks.silo`.
  A1 = conjunto calibrado de dominios, leído de `chunk_domain_membership` bajo
       una `assignment_version` explícita.
  A2 = A1 más la compuerta de materialidad de `chunk_materiality`.
- expansión (E): cómo crece el conjunto de candidatos antes del reranking.
  E0 = sin expansión. E1 = se habilitan hermanos del mismo `document_id`.

E1 NO se llama A2: A2 ya designa la compuerta de materialidad.

Ninguna dimensión puede entregar a una variante más contexto final que a otra:
todos los caminos terminan con el mismo `k` final.
"""

from multirag.config import RETRIEVAL_TOP_K, SILOS


# --- Assignment variants (A) / [ES] Variantes de asignación (A) ---

VARIANTE_ASIGNACION_PREDETERMINADA = "A0"

VARIANTES_ASIGNACION = (
    "A0",
    "A1",
    "A2",
)


# --- Documentary expansion variants (E) / [ES] Variantes de expansión (E) ---

VARIANTE_EXPANSION_PREDETERMINADA = "E0"

VARIANTES_EXPANSION = (
    "E0",
    "E1",
)


# --- Review state of a membership / [ES] Estado de revisión de una membresía ---

ESTADOS_REVISION = (
    "automatic",
    "confirmed",
    "rejected",
)

ESTADO_REVISION_RECHAZADO = "rejected"


# --- Retrieval origin / [ES] Origen de recuperación ---

ORIGEN_DOMINIO = "dominio"

ORIGEN_EXPANSION = "expansion"

ORIGEN_AMBOS = "ambos"


# Materiality values excluded by the A2 gate. A chunk WITHOUT a materiality row
# for the requested version is not excluded: the gate only removes what was
# explicitly judged non-material, so partial coverage never shrinks the corpus
# silently.
#
# [ES] Valores de materialidad excluidos por la compuerta A2. Un chunk SIN fila
# de materialidad para la versión pedida no se excluye: la compuerta solo retira
# lo que fue juzgado explícitamente como no material, de modo que una cobertura
# parcial nunca reduce el corpus en silencio.
MATERIALIDADES_EXCLUIDAS_PREDETERMINADAS = (
    "administrativo_no_material",
)


class ErrorDeAlcance(ValueError):
    """Invalid retrievable scope configuration.

    [ES] Configuración inválida del alcance recuperable.
    """


def validar_variante_asignacion(variante) -> str:
    """Validate the assignment variant.

    [ES] Valida la variante de asignación.
    """
    if variante not in VARIANTES_ASIGNACION:
        raise ErrorDeAlcance(
            f"Variante de asignación desconocida: {variante!r}. "
            "Las variantes válidas son "
            + ", ".join(VARIANTES_ASIGNACION)
            + ". La expansión documental se declara aparte como "
            + ", ".join(VARIANTES_EXPANSION)
            + "; A2 designa la compuerta de materialidad, no la expansión."
        )

    return variante


def validar_variante_expansion(variante) -> str:
    """Validate the documentary expansion variant.

    [ES] Valida la variante de expansión documental.
    """
    if variante not in VARIANTES_EXPANSION:
        raise ErrorDeAlcance(
            f"Variante de expansión documental desconocida: {variante!r}. "
            "Las variantes válidas son "
            + ", ".join(VARIANTES_EXPANSION)
            + ". La expansión documental no se nombra A2: A2 es la compuerta "
            "de materialidad de la dimensión de asignación."
        )

    return variante


def validar_k(k) -> int:
    """Validate the final number of retrieved chunks.

    [ES] Valida la cantidad final de chunks recuperados.
    """
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ErrorDeAlcance(
            f"k debe ser un entero mayor que cero; se recibió {k!r}."
        )

    return k


def validar_dominios(dominios) -> tuple[str, ...]:
    """Validate a set of domains and remove repetitions preserving order.

    [ES] Valida un conjunto de dominios y quita repeticiones conservando el
    orden.
    """
    if not dominios:
        raise ErrorDeAlcance(
            "Debe indicarse al menos un dominio para la recuperación "
            "multidominio."
        )

    if isinstance(dominios, str):
        raise ErrorDeAlcance(
            "Los dominios deben indicarse como una secuencia, no como una "
            f"cadena: se recibió {dominios!r}."
        )

    unicos: list[str] = []

    for dominio in dominios:
        if dominio not in unicos:
            unicos.append(dominio)

    desconocidos = [
        dominio
        for dominio in unicos
        if dominio not in SILOS
    ]

    if desconocidos:
        raise ErrorDeAlcance(
            "Dominios desconocidos: "
            + ", ".join(map(str, desconocidos))
            + ". Los dominios vigentes son "
            + ", ".join(SILOS)
            + "."
        )

    return tuple(unicos)


def _validar_version(valor, nombre: str, variante: str) -> str:
    """Demand an explicit, non-empty version.

    [ES] Exige una versión explícita y no vacía.
    """
    if valor is None or not str(valor).strip():
        raise ErrorDeAlcance(
            f"La variante {variante} exige una {nombre} explícita. "
            "La recuperación no elige automáticamente la última versión: "
            "mezclar versiones históricas de las asignaciones invalidaría la "
            f"comparación. Indique {nombre} de forma explícita."
        )

    return str(valor)


def validar_versiones_de_asignacion(
    *,
    variante_asignacion: str,
    assignment_version: str | None = None,
    taxonomy_version: str | None = None,
    materiality_version: str | None = None,
) -> str:
    """Check that the declared versions match the assignment variant.

    It runs before touching the database so that an A1 call without an explicit
    version fails immediately, instead of silently picking an arbitrary one.

    [ES] Verifica que las versiones declaradas correspondan con la variante de
    asignación.

    Se ejecuta antes de tocar la base para que una llamada A1 sin versión
    explícita falle de inmediato, en lugar de elegir una arbitraria en
    silencio.
    """
    variante = validar_variante_asignacion(variante_asignacion)

    if variante == "A0":
        for nombre, valor in (
            ("assignment_version", assignment_version),
            ("taxonomy_version", taxonomy_version),
            ("materiality_version", materiality_version),
        ):
            if valor is not None:
                raise ErrorDeAlcance(
                    f"La variante A0 no utiliza {nombre}: la pertenencia "
                    "proviene de la columna heredada chunks.silo. Para "
                    "recuperar mediante membresías versionadas use A1 o A2."
                )

        return variante

    _validar_version(
        assignment_version,
        "assignment_version",
        variante,
    )

    if taxonomy_version is not None:
        _validar_version(
            taxonomy_version,
            "taxonomy_version",
            variante,
        )

    if variante == "A1":
        if materiality_version is not None:
            raise ErrorDeAlcance(
                "La variante A1 no aplica compuerta de materialidad: "
                "materiality_version pertenece a A2."
            )

        return variante

    _validar_version(
        materiality_version,
        "materiality_version",
        variante,
    )

    return variante


def construir_filtro_asignacion(
    *,
    variante_asignacion: str = VARIANTE_ASIGNACION_PREDETERMINADA,
    dominio: str | None = None,
    assignment_version: str | None = None,
    taxonomy_version: str | None = None,
    materiality_version: str | None = None,
    materialidades_excluidas=MATERIALIDADES_EXCLUIDAS_PREDETERMINADAS,
    consulta_procedimental: bool = False,
) -> tuple[list[str], list]:
    """Build the SQL conditions of the assignment variant over `chunks`.

    Returns the list of conditions and their parameters, in order.

    A0 reads the legacy column `chunks.silo`: current behaviour, unchanged.
    A1 reads `chunk_domain_membership` under an explicit `assignment_version`,
    and never lets a rejected membership participate.
    A2 adds the materiality gate of `chunk_materiality`; an explicitly
    procedural query disables the gate, as the protocol requires.

    [ES] Construye las condiciones SQL de la variante de asignación sobre
    `chunks`.

    Devuelve la lista de condiciones y sus parámetros, en orden.

    A0 lee la columna heredada `chunks.silo`: comportamiento actual, sin
    cambios. A1 lee `chunk_domain_membership` bajo una `assignment_version`
    explícita, y nunca deja participar a una membresía rechazada. A2 agrega la
    compuerta de materialidad de `chunk_materiality`; una consulta
    explícitamente procedimental desactiva la compuerta, como exige el
    protocolo.
    """
    variante = validar_versiones_de_asignacion(
        variante_asignacion=variante_asignacion,
        assignment_version=assignment_version,
        taxonomy_version=taxonomy_version,
        materiality_version=materiality_version,
    )

    condiciones: list[str] = []
    parametros: list = []

    if variante == "A0":
        if dominio:
            condiciones.append("silo = %s")
            parametros.append(dominio)

        return condiciones, parametros

    # A1 and A2 / [ES] A1 y A2
    version_asignacion = str(assignment_version)

    membresia = [
        "m.chunk_uid = chunks.chunk_uid",
        "m.assignment_version = %s",
        "m.review_status <> %s",
    ]
    parametros_membresia: list = [
        version_asignacion,
        ESTADO_REVISION_RECHAZADO,
    ]

    if dominio:
        membresia.append("m.domain_id = %s")
        parametros_membresia.append(dominio)

    if taxonomy_version is not None:
        membresia.append("m.taxonomy_version = %s")
        parametros_membresia.append(str(taxonomy_version))

    condiciones.append(
        "EXISTS (SELECT 1 FROM chunk_domain_membership AS m WHERE "
        + " AND ".join(membresia)
        + ")"
    )
    parametros.extend(parametros_membresia)

    if variante == "A1":
        return condiciones, parametros

    # A2 / [ES] A2
    version_materialidad = str(materiality_version)

    excluidas = tuple(materialidades_excluidas or ())

    if consulta_procedimental or not excluidas:
        # An explicitly procedural query keeps administrative content
        # available: A2 does not delete anything, it only changes eligibility.
        #
        # [ES] Una consulta explícitamente procedimental mantiene disponible el
        # contenido administrativo: A2 no borra nada, solo cambia la
        # elegibilidad.
        return condiciones, parametros

    condiciones.append(
        "NOT EXISTS (SELECT 1 FROM chunk_materiality AS mat WHERE "
        "mat.chunk_uid = chunks.chunk_uid "
        "AND mat.materiality_version = %s "
        "AND mat.review_status <> %s "
        "AND mat.materiality = ANY(%s))"
    )
    parametros.extend(
        [
            version_materialidad,
            ESTADO_REVISION_RECHAZADO,
            list(excluidas),
        ]
    )

    return condiciones, parametros


# Columns every retrieval returns, in the order the rows are unpacked.
# [ES] Columnas que devuelve toda recuperación, en el orden en que se
# desempaquetan las filas.
COLUMNAS_RECUPERADAS = (
    "chunk_uid",
    "silo",
    "titulo",
    "contenido",
    "fuente",
    "document_id",
    "instrument_id",
    "artifact_id",
)


def construir_consulta_vectorial(
    *,
    vector_literal: str,
    k: int,
    condiciones=(),
    parametros_filtro=(),
    documentos=None,
) -> tuple[str, list]:
    """Build the vector query and its parameters, in order.

    It is the single source of the executed SQL: the retriever runs it and the
    diagnostic probe plans it, so what is measured cannot drift from what is
    executed.

    [ES] Construye la consulta vectorial y sus parámetros, en orden.

    Es la fuente única del SQL ejecutado: el recuperador lo corre y la sonda de
    diagnóstico lo planifica, así que lo medido no puede divergir de lo
    ejecutado.
    """
    validar_k(k)

    condiciones = list(condiciones)
    parametros = list(parametros_filtro)

    if documentos:
        condiciones.append("document_id = ANY(%s)")
        parametros.append(list(documentos))

    filtro = (
        "WHERE " + " AND ".join(condiciones)
        if condiciones
        else ""
    )

    sql = (
        "SELECT "
        + ", ".join(COLUMNAS_RECUPERADAS)
        + ", 1 - (embedding <=> %s::vector) AS similitud "
        "FROM chunks "
        + (filtro + " " if filtro else "")
        + "ORDER BY embedding <=> %s::vector "
        "LIMIT %s"
    )

    return sql, [vector_literal] + parametros + [vector_literal, k]


def combinar_origen(primero: str, segundo: str) -> str:
    """Combine two retrieval origins of the same chunk.

    [ES] Combina dos orígenes de recuperación del mismo chunk.
    """
    if primero == segundo:
        return primero

    if ORIGEN_AMBOS in (primero, segundo):
        return ORIGEN_AMBOS

    if {primero, segundo} == {ORIGEN_DOMINIO, ORIGEN_EXPANSION}:
        return ORIGEN_AMBOS

    return primero or segundo


def marcar_origen(
    registro: dict,
    *,
    origen: str,
    dominio: str | None = None,
) -> dict:
    """Copy a record declaring the path it arrived by in THIS step.

    The origin is set, not combined: `buscar()` always stamps its records with
    the domain origin, so combining here would turn every sibling into
    "ambos". Combining origins is the job of `fusionar_candidatos`, which is
    the only place that knows a chunk arrived through two different paths.

    The original record is not mutated: the caller may be reusing it.

    [ES] Copia un registro declarando el camino por el que llegó en ESTE paso.

    El origen se fija, no se combina: `buscar()` siempre marca sus registros
    con el origen de dominio, así que combinar aquí convertiría a todo hermano
    en "ambos". Combinar orígenes es tarea de `fusionar_candidatos`, el único
    lugar que sabe que un chunk llegó por dos caminos distintos.

    El registro original no se muta: quien llama puede estar reutilizándolo.
    """
    marcado = dict(registro)

    dominios = list(
        marcado.get("dominios_recuperacion") or []
    )

    if dominio and dominio not in dominios:
        dominios.append(dominio)

    marcado["dominios_recuperacion"] = dominios
    marcado["origen_recuperacion"] = origen

    return marcado


def _similitud(registro: dict) -> float:
    """Read the similarity of a record as a comparable number.

    [ES] Lee la similitud de un registro como un número comparable.
    """
    valor = registro.get("similitud")

    if valor is None:
        return float("-inf")

    return float(valor)


def fusionar_candidatos(candidatos) -> list[dict]:
    """Merge candidates deduplicating by `chunk_uid`.

    The same chunk retrieved through several domains or through expansion
    appears exactly once, keeping the best similarity, every domain it was
    retrieved through and the combined origin. The physical chunk is never
    duplicated.

    A record without `chunk_uid` cannot be identified, so it is kept as is
    instead of being merged with an unrelated record.

    [ES] Fusiona candidatos deduplicando por `chunk_uid`.

    El mismo chunk recuperado por varios dominios o por expansión aparece una
    sola vez, conservando la mejor similitud, todos los dominios por los que fue
    recuperado y el origen combinado. El chunk físico nunca se duplica.

    Un registro sin `chunk_uid` no puede identificarse, así que se conserva tal
    cual en lugar de fusionarse con un registro ajeno.
    """
    fusionados: dict[str, dict] = {}
    ordenados: list[dict] = []

    for candidato in candidatos:
        registro = dict(candidato)
        registro.setdefault("dominios_recuperacion", [])
        registro.setdefault(
            "origen_recuperacion",
            ORIGEN_DOMINIO,
        )

        uid = registro.get("chunk_uid")

        if not uid:
            ordenados.append(registro)
            continue

        previo = fusionados.get(uid)

        if previo is None:
            fusionados[uid] = registro
            ordenados.append(registro)
            continue

        if _similitud(registro) > _similitud(previo):
            previo["similitud"] = registro["similitud"]

        for dominio in registro["dominios_recuperacion"]:
            if dominio not in previo["dominios_recuperacion"]:
                previo["dominios_recuperacion"].append(dominio)

        previo["origen_recuperacion"] = combinar_origen(
            previo["origen_recuperacion"],
            registro["origen_recuperacion"],
        )

        for clave, valor in registro.items():
            if clave in (
                "similitud",
                "dominios_recuperacion",
                "origen_recuperacion",
            ):
                continue

            if previo.get(clave) is None and valor is not None:
                previo[clave] = valor

    return ordenados


def ordenar_y_recortar(registros, k: int) -> list[dict]:
    """Rerank by similarity and trim to the same final budget.

    [ES] Rerankea por similitud y recorta al mismo presupuesto final.
    """
    validar_k(k)

    materializados = list(registros)

    ordenados = sorted(
        enumerate(materializados),
        key=lambda par: (
            -_similitud(par[1]),
            par[0],
        ),
    )

    return [
        registro
        for _, registro in ordenados[:k]
    ]


def kwargs_de_asignacion(
    *,
    variante_asignacion: str = VARIANTE_ASIGNACION_PREDETERMINADA,
    assignment_version: str | None = None,
    taxonomy_version: str | None = None,
    materiality_version: str | None = None,
    consulta_procedimental: bool = False,
) -> dict:
    """Build the assignment arguments forwarded to the retrieval function.

    The versions are validated here, before any database access: an A1 or A2
    call without an explicit version fails immediately instead of reaching the
    query and picking an arbitrary version.

    [ES] Construye los argumentos de asignación que se reenvían a la función de
    recuperación.

    Las versiones se validan aquí, antes de cualquier acceso a la base: una
    llamada A1 o A2 sin versión explícita falla de inmediato, en lugar de
    llegar a la consulta y elegir una versión arbitraria.
    """
    return {
        "variante_asignacion": validar_versiones_de_asignacion(
            variante_asignacion=variante_asignacion,
            assignment_version=assignment_version,
            taxonomy_version=taxonomy_version,
            materiality_version=materiality_version,
        ),
        "assignment_version": assignment_version,
        "taxonomy_version": taxonomy_version,
        "materiality_version": materiality_version,
        "consulta_procedimental": consulta_procedimental,
    }


def recuperar_multidominio(
    *,
    pregunta: str,
    dominios,
    buscar_fn,
    k: int = RETRIEVAL_TOP_K,
    variante_asignacion: str = VARIANTE_ASIGNACION_PREDETERMINADA,
    assignment_version: str | None = None,
    taxonomy_version: str | None = None,
    materiality_version: str | None = None,
    consulta_procedimental: bool = False,
) -> list[dict]:
    """Retrieve from a set of domains under a single final budget.

    Each domain contributes at most `k` candidates, exactly as the current B1
    arm does. Then the union is deduplicated by `chunk_uid`, reranked and cut
    back to `k`: a multilabel variant never receives more final context than
    the exclusive one.

    [ES] Recupera desde un conjunto de dominios bajo un único presupuesto
    final.

    Cada dominio aporta a lo sumo `k` candidatos, exactamente como hace hoy el
    brazo B1. Después la unión se deduplica por `chunk_uid`, se rerankea y se
    recorta a `k`: una variante multietiqueta nunca recibe más contexto final
    que la exclusiva.
    """
    dominios_validados = validar_dominios(dominios)
    validar_k(k)

    asignacion = kwargs_de_asignacion(
        variante_asignacion=variante_asignacion,
        assignment_version=assignment_version,
        taxonomy_version=taxonomy_version,
        materiality_version=materiality_version,
        consulta_procedimental=consulta_procedimental,
    )

    candidatos: list[dict] = []

    for dominio in dominios_validados:
        for registro in buscar_fn(
            pregunta,
            silo=dominio,
            k=k,
            **asignacion,
        ):
            candidatos.append(
                marcar_origen(
                    registro,
                    origen=ORIGEN_DOMINIO,
                    dominio=dominio,
                )
            )

    return ordenar_y_recortar(
        fusionar_candidatos(candidatos),
        k,
    )


def documentos_de(semillas) -> list[str]:
    """Distinct `document_id` values of the seeds, preserving order.

    A chunk without `document_id` simply contributes no document: it does not
    break the execution and it is not lost as a seed.

    [ES] Valores distintos de `document_id` de las semillas, conservando el
    orden.

    Un chunk sin `document_id` sencillamente no aporta documento: no rompe la
    ejecución y no se pierde como semilla.
    """
    documentos: list[str] = []

    for semilla in semillas:
        documento = semilla.get("document_id")

        if not documento:
            continue

        if documento not in documentos:
            documentos.append(documento)

    return documentos


def expandir_por_documento(
    *,
    pregunta: str,
    semillas,
    buscar_fn,
    k: int = RETRIEVAL_TOP_K,
    k_hermanos: int | None = None,
    variante_asignacion: str = VARIANTE_ASIGNACION_PREDETERMINADA,
    assignment_version: str | None = None,
    taxonomy_version: str | None = None,
    materiality_version: str | None = None,
    consulta_procedimental: bool = False,
) -> list[dict]:
    """E1: enable siblings of the seeds' documents, dedupe, rerank and trim.

    The complete document is NOT incorporated. Siblings are candidates queried
    with the SAME question and bounded by `k_hermanos`; then seeds and siblings
    are merged by `chunk_uid`, reranked with that same question and cut to the
    same final `k` as E0.

    The eligibility filter of the assignment variant still applies to siblings
    (minus the domain restriction, which is precisely what expansion relaxes),
    so E1 cannot smuggle past the A2 gate what A2 excluded.

    [ES] E1: habilita hermanos de los documentos de las semillas, deduplica,
    rerankea y recorta.

    NO se incorpora el documento completo. Los hermanos son candidatos
    consultados con la MISMA pregunta y acotados por `k_hermanos`; luego
    semillas y hermanos se fusionan por `chunk_uid`, se rerankean con esa misma
    pregunta y se recortan al mismo `k` final que E0.

    El filtro de elegibilidad de la variante de asignación sigue aplicándose a
    los hermanos (menos la restricción de dominio, que es justamente lo que la
    expansión relaja), de modo que E1 no puede colar por la compuerta A2 lo que
    A2 excluyó.
    """
    validar_k(k)

    semillas_marcadas = [
        marcar_origen(
            semilla,
            origen=ORIGEN_DOMINIO,
        )
        for semilla in semillas
    ]

    documentos = documentos_de(semillas_marcadas)

    if not documentos:
        return ordenar_y_recortar(
            fusionar_candidatos(semillas_marcadas),
            k,
        )

    asignacion = kwargs_de_asignacion(
        variante_asignacion=variante_asignacion,
        assignment_version=assignment_version,
        taxonomy_version=taxonomy_version,
        materiality_version=materiality_version,
        consulta_procedimental=consulta_procedimental,
    )

    hermanos = buscar_fn(
        pregunta,
        silo=None,
        k=validar_k(k_hermanos if k_hermanos else k),
        documentos=documentos,
        **asignacion,
    )

    candidatos = list(semillas_marcadas)

    for hermano in hermanos:
        candidatos.append(
            marcar_origen(
                hermano,
                origen=ORIGEN_EXPANSION,
            )
        )

    return ordenar_y_recortar(
        fusionar_candidatos(candidatos),
        k,
    )


def recuperar(
    *,
    pregunta: str,
    buscar_fn,
    dominios=None,
    k: int = RETRIEVAL_TOP_K,
    variante_asignacion: str = VARIANTE_ASIGNACION_PREDETERMINADA,
    variante_expansion: str = VARIANTE_EXPANSION_PREDETERMINADA,
    assignment_version: str | None = None,
    taxonomy_version: str | None = None,
    materiality_version: str | None = None,
    consulta_procedimental: bool = False,
    k_hermanos: int | None = None,
) -> list[dict]:
    """Retrieve declaring both dimensions: assignment (A) and expansion (E).

    Without `dominios` the scope is monolithic; the assignment variant still
    governs eligibility, so the control arm can be compared under the same
    policy.

    [ES] Recupera declarando ambas dimensiones: asignación (A) y expansión (E).

    Sin `dominios` el alcance es monolítico; la variante de asignación sigue
    gobernando la elegibilidad, para que el brazo de control pueda compararse
    bajo la misma política.
    """
    validar_variante_asignacion(variante_asignacion)
    validar_variante_expansion(variante_expansion)
    validar_k(k)

    asignacion = kwargs_de_asignacion(
        variante_asignacion=variante_asignacion,
        assignment_version=assignment_version,
        taxonomy_version=taxonomy_version,
        materiality_version=materiality_version,
        consulta_procedimental=consulta_procedimental,
    )

    if dominios:
        semillas = recuperar_multidominio(
            pregunta=pregunta,
            dominios=dominios,
            buscar_fn=buscar_fn,
            k=k,
            **asignacion,
        )
    else:
        semillas = ordenar_y_recortar(
            fusionar_candidatos(
                marcar_origen(
                    registro,
                    origen=ORIGEN_DOMINIO,
                )
                for registro in buscar_fn(
                    pregunta,
                    silo=None,
                    k=k,
                    **asignacion,
                )
            ),
            k,
        )

    if variante_expansion == "E0":
        return semillas

    return expandir_por_documento(
        pregunta=pregunta,
        semillas=semillas,
        buscar_fn=buscar_fn,
        k=k,
        k_hermanos=k_hermanos,
        **asignacion,
    )
