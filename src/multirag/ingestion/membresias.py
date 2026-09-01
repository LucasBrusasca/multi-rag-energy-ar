"""Turn a frozen proposal artifact into versioned Silver membership rows.

The input is one of the JSONL artifacts already produced by the project
(`proponer_asignacion_semantica.py`, `revisar_semantica_ciega.py`): one record
per chunk, with the proposed domains, the proposed materiality and a
self-declared confidence.

The output is a `.sql` file. **This module never connects to PostgreSQL.**
Applying the file is a separate, conscious decision, exactly like a migration.

What the Silver labels are and are not:

- They are automatic proposals. `review_status` is written as `automatic`.
- They are NOT human truth and NOT Golden. A proposal never promotes itself.
- `score` is the model's self-declared confidence, so `score_kind` says so
  explicitly. It is not a calibrated probability.

A chunk with zero domains is a legitimate result, not a failure: it may be
administrative content without substantive matter, or substantive matter
outside the current ontology.

[ES] Convierte un artefacto congelado de propuestas en filas Silver de
membresía versionadas.

La entrada es uno de los artefactos JSONL que el proyecto ya produce
(`proponer_asignacion_semantica.py`, `revisar_semantica_ciega.py`): un registro
por chunk, con los dominios propuestos, la materialidad propuesta y una
confianza autodeclarada.

La salida es un archivo `.sql`. **Este módulo nunca se conecta a PostgreSQL.**
Aplicar el archivo es una decisión separada y consciente, igual que una
migración.

Qué son y qué no son las etiquetas Silver:

- Son propuestas automáticas. `review_status` se escribe como `automatic`.
- NO son verdad humana ni Golden. Una propuesta no se promueve a sí misma.
- `score` es la confianza autodeclarada del modelo, así que `score_kind` lo
  dice explícitamente. No es una probabilidad calibrada.

Un chunk con cero dominios es un resultado legítimo, no una falla: puede ser
contenido administrativo sin materia sustantiva, o materia sustantiva ajena a
la ontología vigente.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

from multirag.config import MATERIALIDADES, SILOS


# Every membership produced here is automatic. Promoting one to 'confirmed' or
# demoting it to 'rejected' is a human act, never a side effect of this module.
#
# [ES] Toda membresía producida aquí es automática. Promoverla a 'confirmed' o
# degradarla a 'rejected' es un acto humano, nunca un efecto lateral de este
# módulo.
REVIEW_STATUS_SILVER = "automatic"


# The score is what the model declared about itself. Naming it prevents reading
# it later as a calibrated probability.
#
# [ES] El score es lo que el modelo declaró sobre sí mismo. Nombrarlo evita
# leerlo después como una probabilidad calibrada.
SCORE_KIND_PREDETERMINADO = "confianza_autodeclarada_llm"


# States that assign domains. The remaining ones legitimately produce a chunk
# with zero domains.
#
# [ES] Estados que asignan dominios. Los demás producen legítimamente un chunk
# con cero dominios.
ESTADO_ASIGNA_DOMINIOS = "asignado"


# Accepted field names, in order of preference: the proposal artifact and the
# blind-review artifact name the same thing differently.
#
# [ES] Nombres de campo aceptados, en orden de preferencia: el artefacto de
# propuestas y el de revisión ciega nombran lo mismo de forma distinta.
CAMPOS_DOMINIOS = (
    "dominios_propuestos",
    "dominios_revision",
)

CAMPOS_MATERIALIDAD = (
    "materialidad_propuesta",
    "materialidad_revision",
)

CAMPOS_ESTADO = (
    "estado_asignacion",
    "estado_revision",
)

CAMPOS_MODELO = (
    "modelo_resuelto",
    "modelo",
    "modelo_solicitado",
)

CAMPOS_SCORE = (
    "score",
    "confianza_autodeclarada",
)


# Versions and methods travel inside a generated SQL literal, so they are
# restricted to a character set that cannot alter the statement.
#
# [ES] Las versiones y los métodos viajan dentro de un literal SQL generado,
# así que se restringen a un conjunto de caracteres que no puede alterar la
# sentencia.
PATRON_IDENTIFICADOR_SEGURO = re.compile(r"^[A-Za-z0-9._:@+-]{1,120}$")

PATRON_CHUNK_UID = re.compile(r"^[0-9a-f]{64}$")


class ErrorDeMembresias(ValueError):
    """Invalid input for producing Silver memberships.

    [ES] Entrada inválida para producir membresías Silver.
    """


def _primer_campo(registro: dict, candidatos: tuple[str, ...]):
    """Return the first present field among the accepted names.

    [ES] Devuelve el primer campo presente entre los nombres aceptados.
    """
    for campo in candidatos:
        if campo in registro:
            return registro[campo]

    return None


def validar_identificador(valor, nombre: str) -> str:
    """Validate a version or method that will travel inside SQL.

    [ES] Valida una versión o método que viajará dentro del SQL.
    """
    if valor is None or not str(valor).strip():
        raise ErrorDeMembresias(
            f"Falta {nombre}. No se elige automáticamente ninguna versión: "
            "debe declararse de forma explícita."
        )

    texto = str(valor).strip()

    if not PATRON_IDENTIFICADOR_SEGURO.match(texto):
        raise ErrorDeMembresias(
            f"{nombre} solo admite letras, dígitos y los signos . _ : @ + -"
            f" (hasta 120 caracteres); se recibió {texto!r}."
        )

    return texto


def cargar_propuestas(ruta: Path) -> list[dict]:
    """Load and validate the frozen proposal artifact.

    [ES] Carga y valida el artefacto congelado de propuestas.
    """
    ruta_resuelta = Path(ruta).resolve()

    if not ruta_resuelta.is_file():
        raise ErrorDeMembresias(
            f"No existe el artefacto de propuestas: {ruta_resuelta}"
        )

    registros: list[dict] = []
    vistos: set[str] = set()

    with ruta_resuelta.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as archivo:
        for numero, linea in enumerate(archivo, start=1):
            if not linea.strip():
                continue

            try:
                registro = json.loads(linea)
            except json.JSONDecodeError as error:
                raise ErrorDeMembresias(
                    f"La línea {numero} no es JSON válido: {error}"
                ) from error

            if not isinstance(registro, dict):
                raise ErrorDeMembresias(
                    f"La línea {numero} no es un objeto JSON."
                )

            chunk_uid = registro.get("chunk_uid")

            if not isinstance(chunk_uid, str) or not PATRON_CHUNK_UID.match(
                chunk_uid
            ):
                raise ErrorDeMembresias(
                    f"La línea {numero} no tiene un chunk_uid válido "
                    f"(64 hexadecimales): {chunk_uid!r}"
                )

            if chunk_uid in vistos:
                raise ErrorDeMembresias(
                    f"El chunk_uid está repetido en el artefacto: {chunk_uid}"
                )

            vistos.add(chunk_uid)
            registros.append(registro)

    if not registros:
        raise ErrorDeMembresias(
            f"El artefacto no contiene propuestas: {ruta_resuelta}"
        )

    return registros


def huella_del_artefacto(ruta: Path) -> str:
    """SHA-256 of the artifact, so the emitted SQL is traceable to its source.

    [ES] SHA-256 del artefacto, para que el SQL emitido sea trazable a su
    origen.
    """
    return hashlib.sha256(
        Path(ruta).resolve().read_bytes()
    ).hexdigest()


def metodo_de_asignacion(registros: list[dict], metodo=None) -> str:
    """Resolve `assignment_method`: the declared one, or the artifact's model.

    [ES] Resuelve `assignment_method`: el declarado, o el modelo del artefacto.
    """
    if metodo:
        return validar_identificador(metodo, "assignment_method")

    modelos = {
        str(_primer_campo(registro, CAMPOS_MODELO)).strip()
        for registro in registros
        if _primer_campo(registro, CAMPOS_MODELO)
    }

    if len(modelos) != 1:
        raise ErrorDeMembresias(
            "No se puede deducir assignment_method: el artefacto declara "
            f"{len(modelos)} modelo(s) {sorted(modelos)}. Indíquelo de forma "
            "explícita."
        )

    return validar_identificador(
        modelos.pop(),
        "assignment_method",
    )


def _score(registro: dict, dominio: str | None = None):
    """Read the score of the record, or of one of its domains.

    A record may carry one score for the whole decision (a self-declared LLM
    confidence) or one score per domain (a distribution). `score_kind` is what
    says which of the two it is.

    [ES] Lee el score del registro, o el de uno de sus dominios.

    Un registro puede traer un score para toda la decisión (una confianza
    autodeclarada del LLM) o un score por dominio (una distribución).
    `score_kind` es lo que dice cuál de los dos es.
    """
    por_dominio = registro.get("scores_por_dominio")

    if dominio is not None and isinstance(por_dominio, dict):
        if dominio in por_dominio:
            return _numero(
                por_dominio[dominio],
                f"scores_por_dominio[{dominio}]",
            )

    valor = _primer_campo(registro, CAMPOS_SCORE)

    if valor is None:
        return None

    return _numero(valor, "score")


def _numero(valor, nombre: str):
    """Validate a score in the [0, 1] range.

    [ES] Valida un score en el rango [0, 1].
    """
    try:
        numero = float(valor)
    except (TypeError, ValueError) as error:
        raise ErrorDeMembresias(
            f"{nombre} no es numérico: {valor!r}"
        ) from error

    if not 0.0 <= numero <= 1.0:
        raise ErrorDeMembresias(
            f"{nombre} debe estar entre 0 y 1; se recibió {numero!r}."
        )

    return numero


def conjunto_por_umbral(scores: dict, umbral: float) -> list[str]:
    """A1 rule: every domain reaching the threshold.

    It may return several domains, one, or **none**, which is exactly what the
    decision allows. The threshold is a declared parameter, not a calibrated
    one: calibrating it requires human truth that does not exist yet.

    [ES] Regla A1: todo dominio que alcance el umbral.

    Puede devolver varios dominios, uno o **ninguno**, que es exactamente lo
    que la decisión permite. El umbral es un parámetro declarado, no
    calibrado: calibrarlo exige verdad humana que todavía no existe.
    """
    if not 0.0 < umbral <= 1.0:
        raise ErrorDeMembresias(
            f"El umbral debe estar en (0, 1]; se recibió {umbral!r}."
        )

    elegidos = [
        dominio
        for dominio, score in scores.items()
        if dominio in SILOS and _numero(score, dominio) >= umbral
    ]

    return sorted(
        elegidos,
        key=lambda dominio: (-float(scores[dominio]), dominio),
    )


def conjunto_por_margen(scores: dict, margen: float) -> list[str]:
    """A1 rule: the winner, plus every domain indistinguishable from it.

    A domain enters only when its score is within `margen` of the top one, so
    the set grows exactly where the classifier cannot tell two domains apart
    and stays at one domain everywhere else. Unlike the coverage rule, its
    output does not drift with the parameter for chunks whose winner is clearly
    ahead: those stay at one domain for any reasonable margin.

    The winner is always included, so this rule never loses the A0 label.

    [ES] Regla A1: el ganador, más todo dominio indistinguible de él.

    Un dominio entra solo cuando su score está a menos de `margen` del mayor,
    así que el conjunto crece exactamente donde el clasificador no puede
    separar dos dominios y se queda en uno en todo el resto. A diferencia de la
    regla de cobertura, su salida no se corre con el parámetro para los chunks
    cuyo ganador está claramente adelante: esos se quedan en un dominio con
    cualquier margen razonable.

    El ganador siempre se incluye, así que esta regla nunca pierde la etiqueta
    A0.
    """
    if not 0.0 <= margen < 1.0:
        raise ErrorDeMembresias(
            f"El margen debe estar en [0, 1); se recibió {margen!r}."
        )

    ordenados = sorted(
        (
            (dominio, _numero(score, dominio))
            for dominio, score in scores.items()
            if dominio in SILOS
        ),
        key=lambda par: (-par[1], par[0]),
    )

    if not ordenados:
        return []

    mayor = ordenados[0][1]

    return [
        dominio
        for dominio, score in ordenados
        if mayor - score <= margen
    ]


def conjunto_por_cobertura(scores: dict, cobertura: float) -> list[str]:
    """A1 rule: the smallest set of domains reaching the accumulated coverage.

    The set grows when the distribution is flat and shrinks when it is sharp,
    so its size responds to the uncertainty instead of being a fixed top-2.

    [ES] Regla A1: el conjunto más chico de dominios que alcanza la cobertura
    acumulada.

    El conjunto crece cuando la distribución es plana y se achica cuando es
    puntiaguda, así que su tamaño responde a la incertidumbre en lugar de ser
    un top-2 fijo.
    """
    if not 0.0 < cobertura <= 1.0:
        raise ErrorDeMembresias(
            f"La cobertura debe estar en (0, 1]; se recibió {cobertura!r}."
        )

    ordenados = sorted(
        (
            (dominio, _numero(score, dominio))
            for dominio, score in scores.items()
            if dominio in SILOS
        ),
        key=lambda par: (-par[1], par[0]),
    )

    elegidos: list[str] = []
    acumulado = 0.0

    for dominio, score in ordenados:
        elegidos.append(dominio)
        acumulado += score

        if acumulado >= cobertura:
            break

    return elegidos


def filas_de_membresia(
    registros: list[dict],
    *,
    assignment_version: str,
    taxonomy_version: str,
    assignment_method: str,
    score_kind: str = SCORE_KIND_PREDETERMINADO,
) -> list[dict]:
    """Build the `chunk_domain_membership` rows.

    A chunk contributes one row per proposed domain: zero, one or several. The
    chunk is never duplicated — only the relation is.

    [ES] Construye las filas de `chunk_domain_membership`.

    Un chunk aporta una fila por dominio propuesto: cero, uno o varios. El
    chunk nunca se duplica: se duplica solo la relación.
    """
    version = validar_identificador(
        assignment_version,
        "assignment_version",
    )
    taxonomia = validar_identificador(
        taxonomy_version,
        "taxonomy_version",
    )
    metodo = validar_identificador(
        assignment_method,
        "assignment_method",
    )
    tipo_score = validar_identificador(score_kind, "score_kind")

    filas: list[dict] = []

    for registro in registros:
        dominios = _primer_campo(registro, CAMPOS_DOMINIOS)
        estado = _primer_campo(registro, CAMPOS_ESTADO)

        if dominios is None:
            dominios = []

        if not isinstance(dominios, list):
            raise ErrorDeMembresias(
                f"Los dominios del chunk {registro['chunk_uid']} no son una "
                f"lista: {dominios!r}"
            )

        desconocidos = [
            dominio
            for dominio in dominios
            if dominio not in SILOS
        ]

        if desconocidos:
            raise ErrorDeMembresias(
                f"El chunk {registro['chunk_uid']} propone dominios "
                f"desconocidos: {desconocidos}"
            )

        if len(dominios) != len(set(dominios)):
            raise ErrorDeMembresias(
                f"El chunk {registro['chunk_uid']} repite un dominio."
            )

        if estado is not None and estado != ESTADO_ASIGNA_DOMINIOS and dominios:
            raise ErrorDeMembresias(
                f"El chunk {registro['chunk_uid']} declara el estado "
                f"{estado!r} y aun así asigna dominios."
            )

        for dominio in dominios:
            score = _score(registro, dominio)

            filas.append(
                {
                    "chunk_uid": registro["chunk_uid"],
                    "domain_id": dominio,
                    "score": score,
                    "score_kind": None if score is None else tipo_score,
                    "assignment_method": metodo,
                    "review_status": REVIEW_STATUS_SILVER,
                    "assignment_version": version,
                    "taxonomy_version": taxonomia,
                }
            )

    return filas


def filas_de_materialidad(
    registros: list[dict],
    *,
    materiality_version: str,
    assignment_method: str,
    score_kind: str = SCORE_KIND_PREDETERMINADO,
) -> list[dict]:
    """Build the `chunk_materiality` rows: one per chunk that declares it.

    Materiality is a property of the chunk, so there is at most one row per
    chunk and version.

    [ES] Construye las filas de `chunk_materiality`: una por chunk que la
    declare.

    La materialidad es una propiedad del chunk, así que hay a lo sumo una fila
    por chunk y versión.
    """
    version = validar_identificador(
        materiality_version,
        "materiality_version",
    )
    metodo = validar_identificador(
        assignment_method,
        "assignment_method",
    )
    tipo_score = validar_identificador(score_kind, "score_kind")

    filas: list[dict] = []

    for registro in registros:
        materialidad = _primer_campo(registro, CAMPOS_MATERIALIDAD)

        if materialidad is None:
            continue

        if materialidad not in MATERIALIDADES:
            raise ErrorDeMembresias(
                f"El chunk {registro['chunk_uid']} declara una materialidad "
                f"fuera del vocabulario: {materialidad!r}. Los valores "
                "válidos son " + ", ".join(MATERIALIDADES) + "."
            )

        score = _score(registro)

        filas.append(
            {
                "chunk_uid": registro["chunk_uid"],
                "materiality": materialidad,
                "score": score,
                "score_kind": None if score is None else tipo_score,
                "assignment_method": metodo,
                "review_status": REVIEW_STATUS_SILVER,
                "materiality_version": version,
            }
        )

    return filas


def _literal(valor) -> str:
    """Render a value as a SQL literal.

    Every text that reaches this point was already validated against a
    restricted character set or is a fixed vocabulary value, so doubling the
    single quote is enough and there is no injection surface left.

    [ES] Representa un valor como literal SQL.

    Todo texto que llega hasta aquí fue validado contra un conjunto restringido
    de caracteres o es un valor de vocabulario fijo, así que duplicar la comilla
    simple alcanza y no queda superficie de inyección.
    """
    if valor is None:
        return "NULL"

    if isinstance(valor, bool):
        return "TRUE" if valor else "FALSE"

    if isinstance(valor, (int, float)):
        return repr(valor)

    return "'" + str(valor).replace("'", "''") + "'"


def sentencias_sql(
    filas_membresia: list[dict],
    filas_materialidad: list[dict],
    *,
    origen: str,
    huella: str,
) -> str:
    """Render the idempotent SQL that loads the Silver rows.

    `ON CONFLICT DO NOTHING` is deliberate: re-running must never overwrite a
    membership a human already confirmed or rejected. A corrected run gets a
    NEW `assignment_version`; that is what versioning is for.

    [ES] Representa el SQL idempotente que carga las filas Silver.

    `ON CONFLICT DO NOTHING` es deliberado: repetir la corrida nunca debe pisar
    una membresía que un humano ya confirmó o rechazó. Una corrida corregida
    recibe una `assignment_version` NUEVA; para eso existe el versionado.
    """
    columnas_membresia = (
        "chunk_uid",
        "domain_id",
        "score",
        "score_kind",
        "assignment_method",
        "review_status",
        "assignment_version",
        "taxonomy_version",
    )
    columnas_materialidad = (
        "chunk_uid",
        "materiality",
        "score",
        "score_kind",
        "assignment_method",
        "review_status",
        "materiality_version",
    )

    lineas = [
        "-- Etiquetas Silver generadas automáticamente. NO son verdad humana",
        "-- ni Golden: review_status queda en 'automatic' hasta que una",
        "-- persona confirme o rechace cada membresía.",
        f"-- Artefacto de origen: {origen}",
        f"-- SHA-256 del artefacto: {huella}",
        f"-- Filas de membresía: {len(filas_membresia)}",
        f"-- Filas de materialidad: {len(filas_materialidad)}",
        "-- Requiere la migración 002 aplicada. No la aplica por su cuenta.",
        "",
        "BEGIN;",
        "",
    ]

    for tabla, columnas, filas, conflicto in (
        (
            "chunk_domain_membership",
            columnas_membresia,
            filas_membresia,
            "(chunk_uid, domain_id, assignment_version)",
        ),
        (
            "chunk_materiality",
            columnas_materialidad,
            filas_materialidad,
            "(chunk_uid, materiality_version)",
        ),
    ):
        if not filas:
            lineas.append(f"-- Sin filas para {tabla}.")
            lineas.append("")
            continue

        lineas.append(
            f"INSERT INTO {tabla} ("
            + ", ".join(columnas)
            + ")"
        )
        lineas.append("VALUES")

        valores = [
            "    ("
            + ", ".join(
                _literal(fila[columna])
                for columna in columnas
            )
            + ")"
            for fila in filas
        ]

        lineas.append(",\n".join(valores))
        lineas.append(f"ON CONFLICT {conflicto} DO NOTHING;")
        lineas.append("")

    lineas.append("COMMIT;")
    lineas.append("")

    return "\n".join(lineas)


def guardar_sql(contenido: str, ruta_salida: Path) -> Path:
    """Write the SQL atomically, without overwriting an existing file.

    [ES] Escribe el SQL atómicamente, sin sobrescribir un archivo existente.
    """
    ruta_resuelta = Path(ruta_salida).resolve()

    if ruta_resuelta.exists():
        raise ErrorDeMembresias(
            f"La salida ya existe y no será sobrescrita: {ruta_resuelta}"
        )

    ruta_resuelta.parent.mkdir(parents=True, exist_ok=True)

    ruta_temporal = ruta_resuelta.with_name(
        f".{ruta_resuelta.name}.tmp"
    )

    ruta_temporal.write_text(
        contenido,
        encoding="utf-8",
        newline="\n",
    )
    ruta_temporal.replace(ruta_resuelta)

    return ruta_resuelta


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.

    [ES] Construye la interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Convierte un artefacto congelado de propuestas en SQL de "
            "membresías Silver versionadas. No se conecta a PostgreSQL: "
            "aplicar el SQL es una decisión separada."
        )
    )
    parser.add_argument(
        "--propuestas",
        type=Path,
        required=True,
        help="Artefacto JSONL de propuestas o revisión.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        required=True,
        help="Archivo .sql a generar. No sobrescribe.",
    )
    parser.add_argument(
        "--assignment-version",
        required=True,
        help=(
            "Versión explícita de esta corrida de asignación. "
            "Una corrida corregida usa una versión NUEVA."
        ),
    )
    parser.add_argument(
        "--taxonomy-version",
        required=True,
        help="Versión de la taxonomía de dominios utilizada.",
    )
    parser.add_argument(
        "--materiality-version",
        default=None,
        help=(
            "Versión de la materialidad. Si se omite, no se "
            "generan filas de materialidad."
        ),
    )
    parser.add_argument(
        "--assignment-method",
        default=None,
        help=(
            "Método de asignación. Si se omite, se deduce del "
            "modelo declarado en el artefacto."
        ),
    )
    parser.add_argument(
        "--score-kind",
        default=SCORE_KIND_PREDETERMINADO,
        help=(
            "Qué significa el score. El valor predeterminado "
            "declara que es una confianza autodeclarada, no una "
            "probabilidad calibrada."
        ),
    )
    return parser


def main() -> None:
    """Generate the Silver SQL from the command line.

    [ES] Genera el SQL Silver desde la línea de comandos.
    """
    argumentos = construir_parser().parse_args()

    registros = cargar_propuestas(argumentos.propuestas)
    metodo = metodo_de_asignacion(
        registros,
        argumentos.assignment_method,
    )

    membresias = filas_de_membresia(
        registros,
        assignment_version=argumentos.assignment_version,
        taxonomy_version=argumentos.taxonomy_version,
        assignment_method=metodo,
        score_kind=argumentos.score_kind,
    )

    materialidades = (
        filas_de_materialidad(
            registros,
            materiality_version=argumentos.materiality_version,
            assignment_method=metodo,
            score_kind=argumentos.score_kind,
        )
        if argumentos.materiality_version
        else []
    )

    contenido = sentencias_sql(
        membresias,
        materialidades,
        origen=str(Path(argumentos.propuestas).resolve()),
        huella=huella_del_artefacto(argumentos.propuestas),
    )

    ruta = guardar_sql(contenido, argumentos.salida)

    sin_dominio = len(registros) - len(
        {fila["chunk_uid"] for fila in membresias}
    )

    print(f"Chunks en el artefacto: {len(registros)}")
    print(f"Filas de membresía: {len(membresias)}")
    print(f"Filas de materialidad: {len(materialidades)}")
    print(
        f"Chunks con cero dominios: {sin_dominio} "
        "(resultado legítimo, no una falla)"
    )
    print(f"SQL generado: {ruta}")
    print(
        "Las etiquetas son Silver: review_status='automatic'. "
        "No son verdad humana ni Golden."
    )


if __name__ == "__main__":
    main()
