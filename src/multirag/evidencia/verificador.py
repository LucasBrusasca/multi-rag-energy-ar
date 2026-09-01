"""Deterministic integrity verifier: is the evidence enough to sustain the fact?

This answers a question that Hit/Recall/MRR/nDCG cannot: the right document can
be ranked first and the fact still be unusable, because the amount has no scale,
or the column has no period. The verifier finds that out with rules, never with
a model.

Three separations hold this together, and each one is a mistake this file
refuses to make:

1. COMPLETENESS IS NOT CONFIDENCE. `confianza` is copied from the extractor and
   never touched. The 53 facts with `confianza: alta` and `escala_ausente` are
   meant to come out of here as high-confidence AND incomplete, both at once.
   Lowering their confidence would hide the finding instead of reporting it.

2. COMPLETENESS IS NOT ACCURACY. A populated field can be wrong. Measuring
   accuracy needs a human reference against the source document; the extractor
   cannot be its own ground truth.

3. THE TYPE IS NOT INFERRED FROM WHAT IS BEING MEASURED. Classifying a fact as
   monetary because it has a currency, and then measuring whether it has a
   currency, measures nothing. `clasificar_tipo` therefore receives only the
   FORM of the value and the LEXICON of the labels - never scale, currency,
   period or entity. That restriction is enforced by the signature itself, and
   tested.

[ES] Verificador determinista de integridad: alcanza la evidencia para sostener
el hecho?

Responde una pregunta que Hit/Recall/MRR/nDCG no pueden: el documento correcto
puede quedar primero y el hecho ser igualmente inutilizable, porque el importe
no tiene escala, o la columna no tiene periodo. El verificador lo averigua con
reglas, nunca con un modelo.

Tres separaciones lo sostienen, y cada una es un error que este archivo se
niega a cometer:

1. COMPLETITUD NO ES CONFIANZA. `confianza` se copia del extractor y no se toca.
   Los 53 hechos con `confianza: alta` y `escala_ausente` tienen que salir de
   aca como de confianza alta E incompletos, las dos cosas a la vez. Bajarles la
   confianza ocultaria el hallazgo en lugar de reportarlo.

2. COMPLETITUD NO ES EXACTITUD. Un campo poblado puede estar mal. Medir
   exactitud exige una referencia humana contra el documento fuente; el
   extractor no puede ser su propia verdad.

3. EL TIPO NO SE INFIERE DE LO QUE SE ESTA MIDIENDO. Clasificar un hecho como
   monetario porque tiene moneda, y despues medir si tiene moneda, no mide nada.
   Por eso `clasificar_tipo` recibe unicamente la FORMA del valor y el LEXICO de
   las etiquetas - nunca escala, moneda, periodo ni entidad. Esa restriccion la
   impone la propia firma de la funcion, y se prueba.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Optional, Sequence

from multirag.evidencia.contrato import Especificacion, Evidencia, MODALIDAD_TABLA


# --------------------------------------------------------------------------
# Fact types / Tipos de hecho
# --------------------------------------------------------------------------

MONETARIO = "monetario_presunto"
PORCENTAJE_RATIO = "porcentaje_ratio"
CONTEO = "conteo"
TEMPORAL = "temporal"
NO_INTERPRETABLE = "no_interpretable"

TIPOS = (MONETARIO, PORCENTAJE_RATIO, CONTEO, TEMPORAL, NO_INTERPRETABLE)

# Version of the typology. It is NOT ratified: see
# reports/completitud_hechos.md, section 1, and docs/PENDIENTES_DIRECTOR.md.
# Changing it changes every exact-integrity number, so it travels with them.
# [ES] Version de la tipologia. NO esta ratificada: ver
# reports/completitud_hechos.md, seccion 1, y docs/PENDIENTES_DIRECTOR.md.
# Cambiarla cambia todos los numeros de integridad exacta, asi que viaja con
# ellos.
TIPOLOGIA_VERSION = "tipologia-v0.2-no-ratificada"


# --------------------------------------------------------------------------
# Components / Componentes
# --------------------------------------------------------------------------

ENTIDAD = "entidad"
CONCEPTO = "concepto"
VALOR = "valor"
ESCALA = "escala"
MONEDA = "moneda"
PERIODO = "periodo"

DOCUMENTO = "documento"
UBICACION = "ubicacion"
TABLA = "tabla"
FILA = "fila"
COLUMNA = "columna"

COMPONENTES_SEMANTICOS = (ENTIDAD, CONCEPTO, VALOR, ESCALA, MONEDA, PERIODO)
COMPONENTES_PROCEDENCIA = (DOCUMENTO, UBICACION, TABLA, FILA, COLUMNA)


# --------------------------------------------------------------------------
# Abstention / insufficiency reasons / Motivos de abstencion o insuficiencia
# --------------------------------------------------------------------------

ENTIDAD_AUSENTE = "entidad_ausente"
PERIODO_AUSENTE = "periodo_ausente"
UNIDAD_AUSENTE = "unidad_ausente"
ESCALA_AUSENTE = "escala_ausente"
MONEDA_AMBIGUA = "moneda_ambigua"
VALOR_AUSENTE = "valor_ausente"
CONCEPTO_AUSENTE = "concepto_ausente"
EVIDENCIA_NO_LOCALIZADA = "evidencia_no_localizada"
FUENTES_EN_CONFLICTO = "fuentes_en_conflicto"

# Structural completeness does not prove that the evidence answers the question.
# A chunk with a heading and a page is perfectly locatable and may be about
# something else entirely. Until a human reference, a specific rule or a support
# evaluation says otherwise, the honest outcome is that support is UNKNOWN - not
# that it holds.
# [ES] La completitud estructural no prueba que la evidencia responda la
# pregunta. Un chunk con titulo y pagina es perfectamente localizable y puede
# hablar de otra cosa. Hasta que una referencia humana, una regla especifica o
# una evaluacion de soporte digan lo contrario, el resultado honesto es que el
# soporte es DESCONOCIDO - no que se cumple.
SOPORTE_NO_VERIFICADO = "soporte_no_verificado"

# Two figures are only in conflict if they are claims about the same thing.
# Pesos against dollars, consolidated against individual, or restated against
# nominal are not disagreements: they are different statements. When what makes
# them comparable is not declared, that is what gets reported.
# [ES] Dos cifras solo estan en conflicto si son afirmaciones sobre lo mismo.
# Pesos contra dolares, consolidado contra individual, o reexpresado contra
# nominal no son desacuerdos: son afirmaciones distintas. Cuando lo que las
# vuelve comparables no esta declarado, eso es lo que se reporta.
COMPARABILIDAD_INDETERMINADA = "comparabilidad_indeterminada"

# The evidence is complete, located and traceable - and it is about a different
# concept than the one the claim declared. Belonging to the same logical table
# proves adjacency, not aboutness: sales and costs sit in neighbouring rows and
# are equally impeccable.
# [ES] La evidencia esta completa, localizada y es trazable - y trata de un
# concepto distinto del que declaro la afirmacion. Pertenecer a la misma tabla
# logica prueba adyacencia, no pertinencia: ventas y costos estan en filas
# contiguas y son igual de impecables.
ALINEACION_NO_VERIFICADA = "alineacion_no_verificada"

# Two linked donors offered different values for the same component. Picking one
# would make the result depend on the order the pieces arrived in.
# [ES] Dos donantes vinculados ofrecieron valores distintos para el mismo
# componente. Elegir uno haria que el resultado dependiera del orden en que
# llegaron las piezas.
APORTE_AMBIGUO = "aporte_ambiguo"

MOTIVOS = (
    ENTIDAD_AUSENTE,
    PERIODO_AUSENTE,
    UNIDAD_AUSENTE,
    ESCALA_AUSENTE,
    MONEDA_AMBIGUA,
    VALOR_AUSENTE,
    CONCEPTO_AUSENTE,
    EVIDENCIA_NO_LOCALIZADA,
    FUENTES_EN_CONFLICTO,
    SOPORTE_NO_VERIFICADO,
    COMPARABILIDAD_INDETERMINADA,
    ALINEACION_NO_VERIFICADA,
    APORTE_AMBIGUO,
)


# --------------------------------------------------------------------------
# Support / Soporte
# --------------------------------------------------------------------------

SOSTIENE = "sostiene"
NO_SOSTIENE = "no_sostiene"
NO_VERIFICADO = "no_verificado"

SOPORTES = (SOSTIENE, NO_SOSTIENE, NO_VERIFICADO)

# A missing component maps to exactly one reason. `moneda_ambigua` is NOT here:
# it fires while the currency IS present, so it can never come from absence.
# [ES] Un componente faltante corresponde a exactamente un motivo.
# `moneda_ambigua` NO esta aca: se dispara con la moneda PRESENTE, asi que nunca
# puede venir de una ausencia.
MOTIVO_POR_COMPONENTE = {
    ENTIDAD: ENTIDAD_AUSENTE,
    CONCEPTO: CONCEPTO_AUSENTE,
    VALOR: VALOR_AUSENTE,
    ESCALA: ESCALA_AUSENTE,
    MONEDA: UNIDAD_AUSENTE,
    PERIODO: PERIODO_AUSENTE,
}


# --------------------------------------------------------------------------
# Requirement recipes / Recetas de obligatoriedad
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Receta:
    """Which components each type requires. Named and versioned on purpose.

    Two candidate readings coexist and neither is ratified, so the code holds
    both instead of silently choosing:

    - `RECETA_TESIS` follows PRIORIDADES 7.1, whose exact fact integrity is
      `(entidad, periodo, unidad, moneda, valor)` - entity INCLUDED. Since the
      extractor populates `entidad` in 0 % of cases, every exact integrity under
      this recipe is 0 % until curated metadata is linked. That is the honest
      reading of the current state, not a defect of the measurement.
    - `RECETA_REPORTE_V0` follows reports/completitud_hechos.md, section 1,
      which does not require the entity. It exists so the numbers already
      reported stay comparable.

    Reporting both is what keeps the entity gap visible instead of buried in a
    choice of recipe.

    [ES] Que componentes exige cada tipo. Con nombre y version a proposito.

    Conviven dos lecturas candidatas y ninguna esta ratificada, asi que el
    codigo sostiene las dos en lugar de elegir en silencio:

    - `RECETA_TESIS` sigue PRIORIDADES 7.1, cuya integridad exacta del hecho es
      `(entidad, periodo, unidad, moneda, valor)` - con la entidad INCLUIDA.
      Como el extractor puebla `entidad` en el 0 % de los casos, toda integridad
      exacta bajo esta receta da 0 % hasta vincular metadatos curados. Esa es la
      lectura honesta del estado actual, no un defecto de la medicion.
    - `RECETA_REPORTE_V0` sigue reports/completitud_hechos.md, seccion 1, que no
      exige la entidad. Existe para que los numeros ya reportados sigan siendo
      comparables.

    Reportar las dos es lo que mantiene visible el hueco de entidad en vez de
    enterrarlo en una eleccion de receta.
    """

    nombre: str
    requeridos: dict
    tipologia_version: str = TIPOLOGIA_VERSION

    def para(self, tipo: str) -> tuple[str, ...]:
        return self.requeridos.get(tipo, ())


RECETA_TESIS = Receta(
    nombre="tesis-7.1",
    requeridos={
        MONETARIO: (ENTIDAD, CONCEPTO, VALOR, ESCALA, MONEDA, PERIODO),
        PORCENTAJE_RATIO: (ENTIDAD, CONCEPTO, VALOR, PERIODO),
        CONTEO: (ENTIDAD, CONCEPTO, VALOR, PERIODO),
        TEMPORAL: (ENTIDAD, CONCEPTO, VALOR),
        NO_INTERPRETABLE: (CONCEPTO,),
    },
)

RECETA_REPORTE_V0 = Receta(
    nombre="reporte-completitud-v0",
    requeridos={
        MONETARIO: (CONCEPTO, VALOR, ESCALA, MONEDA, PERIODO),
        PORCENTAJE_RATIO: (CONCEPTO, VALOR, PERIODO),
        CONTEO: (CONCEPTO, VALOR, PERIODO),
        TEMPORAL: (CONCEPTO,),
        NO_INTERPRETABLE: (CONCEPTO,),
    },
)

RECETAS = {r.nombre: r for r in (RECETA_TESIS, RECETA_REPORTE_V0)}
RECETA_PREDETERMINADA = RECETA_TESIS


# --------------------------------------------------------------------------
# Type classification / Clasificacion del tipo
# --------------------------------------------------------------------------

# Lexicon that makes a figure a rate or a ratio rather than an amount. Read on
# the labels, which are text, not on the unit, which is measured.
# [ES] Lexico que vuelve tasa o ratio a una cifra en lugar de un importe. Se lee
# sobre las etiquetas, que son texto, no sobre la unidad, que se mide.
LEXICO_PORCENTAJE = (
    "%",
    "porcentaje",
    "por ciento",
    "tasa",
    "alicuota",
    "ratio",
    "margen",
    "indice",
    "coeficiente",
    "participacion",
    "proporcion",
    "rentabilidad",
    "apalancamiento",
)

LEXICO_CONTEO = (
    "cantidad",
    "cantidades",
    "numero de",
    "nro",
    "n de unidades",
    "unidades",
    "acciones en circulacion",
    "empleados",
    "dotacion",
    "personal",
    "pozos",
    "equipos",
    "clientes",
    "usuarios",
    "votos",
)

# A value that IS a date. The period of a fact is a different thing: this is the
# value itself being temporal.
# [ES] Un valor que ES una fecha. El periodo de un hecho es otra cosa: aca el
# valor mismo es temporal.
FORMA_FECHA = re.compile(
    r"^\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\s*$"
)


def _plano(texto: str) -> str:
    """Lowercase without accents, so 'Alicuota' and 'alicuota' are one word.

    [ES] Minusculas sin acentos, para que 'Alicuota' y 'alicuota' sean una sola
    palabra.
    """
    descompuesto = unicodedata.normalize("NFKD", texto or "")
    sin_tildes = "".join(c for c in descompuesto if not unicodedata.combining(c))
    return sin_tildes.lower()


def clasificar_tipo(
    valor: Optional[float],
    valor_crudo: Optional[str],
    lexico: Sequence[str],
) -> str:
    """Decide the fact type from the FORM of the value and the LEXICON only.

    The signature is the guarantee. This function cannot see `escala`,
    `moneda`, `periodo` or `entidad`, so it cannot decide the obligation from
    the very field whose absence is about to be counted.

    Order matters and is declared:

    1. no value at all -> not interpretable;
    2. the value is a date -> temporal;
    3. per-cent sign or rate lexicon -> percentage/ratio;
    4. counting lexicon over a whole number -> count;
    5. everything else in a financial statement -> presumed monetary.

    Step 5 is a PRESUMPTION, and named as one. It is not evidence that the
    figure is money; it is the default under which an amount without scale
    counts as incomplete rather than as fine.

    [ES] Decide el tipo de hecho solo por la FORMA del valor y el LEXICO.

    La garantia es la firma. Esta funcion no puede ver `escala`, `moneda`,
    `periodo` ni `entidad`, asi que no puede decidir la obligatoriedad a partir
    del mismisimo campo cuya ausencia esta por contarse.

    El orden importa y esta declarado:

    1. sin valor -> no interpretable;
    2. el valor es una fecha -> temporal;
    3. signo de porcentaje o lexico de tasa -> porcentaje/ratio;
    4. lexico de conteo sobre un numero entero -> conteo;
    5. todo lo demas en un estado contable -> monetario presunto.

    El paso 5 es una PRESUNCION, y se llama asi. No es evidencia de que la cifra
    sea dinero; es el default bajo el cual un importe sin escala cuenta como
    incompleto en lugar de como correcto.
    """
    crudo = (valor_crudo or "").strip()

    if valor is None:
        return NO_INTERPRETABLE

    if FORMA_FECHA.match(crudo):
        return TEMPORAL

    contexto = _plano(" | ".join(str(t) for t in lexico))
    crudo_plano = _plano(crudo)

    if "%" in crudo_plano or "%" in contexto:
        return PORCENTAJE_RATIO
    if any(marca in contexto for marca in LEXICO_PORCENTAJE):
        return PORCENTAJE_RATIO

    es_entero = float(valor).is_integer()
    if es_entero and any(marca in contexto for marca in LEXICO_CONTEO):
        return CONTEO

    return MONETARIO


def tipo_de(evidencia: Evidencia) -> str:
    """Classify one piece of evidence, handing the classifier only what it may see.

    [ES] Clasifica una evidencia, entregandole al clasificador solo lo que puede
    ver.
    """
    return clasificar_tipo(evidencia.valor, evidencia.valor_crudo, evidencia.lexico)


# --------------------------------------------------------------------------
# Presence of each component / Presencia de cada componente
# --------------------------------------------------------------------------


def presencia(evidencia: Evidencia) -> dict:
    """Which components are populated, with sentinels already discounted.

    `valor` is the one place where 0 is NOT absence: a balance sheet line can
    legitimately be zero, and treating it as missing would invent an incomplete
    fact out of a complete one.

    [ES] Que componentes estan poblados, con los centinelas ya descontados.

    `valor` es el unico lugar donde 0 NO es ausencia: una linea de balance puede
    valer cero legitimamente, y tratarla como faltante inventaria un hecho
    incompleto a partir de uno completo.
    """
    loc = evidencia.localizacion
    return {
        ENTIDAD: evidencia.entidad is not None,
        CONCEPTO: evidencia.concepto is not None,
        VALOR: evidencia.valor is not None,
        ESCALA: evidencia.escala is not None,
        MONEDA: evidencia.moneda is not None,
        PERIODO: evidencia.periodo is not None,
        DOCUMENTO: evidencia.document_id is not None or evidencia.artifact_id is not None,
        UBICACION: loc.localizable(),
        TABLA: evidencia.table_uid is not None and evidencia.table_segment_uid is not None,
        FILA: loc.fila is not None,
        COLUMNA: loc.columna is not None,
    }


def _procedencia_requerida(evidencia: Evidencia) -> tuple[str, ...]:
    """Provenance obligations depend on the representation, not on the type.

    A text chunk has no row or column and demanding them would report a defect
    that does not exist.

    [ES] Las obligaciones de procedencia dependen de la representacion, no del
    tipo. Un chunk de texto no tiene fila ni columna y exigirselas reportaria un
    defecto inexistente.
    """
    if evidencia.modalidad == MODALIDAD_TABLA:
        return COMPONENTES_PROCEDENCIA
    return (DOCUMENTO, UBICACION)


# --------------------------------------------------------------------------
# Verdict / Veredicto
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Veredicto:
    """The full result of verifying one piece of evidence.

    It carries the reasons, not just a boolean, because an abstention that
    cannot say why is indistinguishable from a failure.

    [ES] El resultado completo de verificar una evidencia.

    Lleva los motivos, no solo un booleano, porque una abstencion que no puede
    decir por que es indistinguible de una falla.
    """

    tipo: str
    receta: str
    tipologia_version: str

    componentes_requeridos: tuple[str, ...]
    componentes_presentes: tuple[str, ...]
    componentes_faltantes: tuple[str, ...]
    integridad_por_componente: dict

    integridad_exacta: bool
    procedencia_requerida: tuple[str, ...]
    procedencia_faltante: tuple[str, ...]
    procedencia_exacta: bool

    advertencias: tuple[str, ...]
    motivos: tuple[str, ...]

    # Three different things, kept apart because collapsing them is how a
    # locatable fragment turns into an answer it does not support:
    #   procedencia_exacta   -> a human could go and reopen this
    #   integridad_exacta    -> the components the type requires are all there
    #   soporte              -> it actually sustains the claim
    # [ES] Tres cosas distintas, separadas porque colapsarlas es como un
    # fragmento localizable se convierte en una respuesta que no sostiene:
    #   procedencia_exacta   -> un humano podria ir a reabrirlo
    #   integridad_exacta    -> estan todos los componentes que el tipo exige
    #   soporte              -> efectivamente sostiene la afirmacion
    soporte: str = NO_VERIFICADO

    # Copied from the extractor, untouched. Kept next to the integrity result so
    # the disagreement between the two can be read off a single record.
    # [ES] Copiada del extractor, intacta. Se guarda al lado del resultado de
    # integridad para poder leer el desacuerdo entre ambos en un solo registro.
    confianza_declarada: Optional[str] = None

    document_id: Optional[str] = None
    referencia_evidencia: Optional[str] = None

    def suficiente(self) -> bool:
        """Enough to answer: complete, locatable, unambiguous AND sustaining.

        The last condition is the one that used to be missing. Without it, an
        irrelevant text chunk that happens to have a heading and a page number
        came out as sufficient: it had no value, so its type demanded nothing,
        so it was "exactly complete". Structural completeness of an empty
        requirement is not evidence.

        [ES] Alcanza para responder: completo, localizable, sin ambiguedad Y que
        sostenga.

        La ultima condicion es la que faltaba. Sin ella, un chunk de texto
        irrelevante que casualmente tuviera titulo y numero de pagina salia como
        suficiente: no tenia valor, asi que su tipo no exigia nada, asi que
        estaba "exactamente completo". La completitud estructural de una
        exigencia vacia no es evidencia.
        """
        return (
            self.integridad_exacta
            and self.procedencia_exacta
            and self.soporte == SOSTIENE
            and not self.motivos
        )

    def indeterminado(self) -> bool:
        """Complete and locatable, but nobody has established that it sustains.

        [ES] Completo y localizable, pero nadie establecio que sostenga.
        """
        return (
            self.integridad_exacta
            and self.procedencia_exacta
            and self.soporte == NO_VERIFICADO
        )

    def confianza_alta_con_integridad_incompleta(self) -> bool:
        """The witness case: the extractor is sure, and the fact is unusable.

        [ES] El caso testigo: el extractor esta seguro, y el hecho es
        inutilizable.
        """
        return self.confianza_declarada == "alta" and not self.integridad_exacta


def _normalizado_para_alineacion(texto: str) -> str:
    """Lowercase, accent-free, with internal whitespace collapsed.

    This is the ONLY liberty taken with a label: "Ventas  Netas" and "ventas
    netas" are the same string typed differently, not two different concepts.

    [ES] Minusculas, sin acentos, con los espacios internos colapsados.

    Es la UNICA libertad que se toma con una etiqueta: "Ventas  Netas" y "ventas
    netas" son la misma cadena escrita distinto, no dos conceptos distintos.
    """
    return " ".join(_plano(texto).split())


def _concepto_coincide(concepto: Optional[str], aceptados: Sequence[str]) -> bool:
    """Exact match against a declared form. Nothing else.

    ONE rule: equality after normalising case, accents and whitespace. No
    prefixes, no substrings, no fuzzy matching, no embeddings, no model.

    An earlier version accepted a label that STARTED with a declared form, so a
    claim about "Ventas" was answered by "Ventas netas". That looks harmless and
    is not: "Resultado" would equally have matched "Resultado financiero", which
    is a different line of the same statement, and the system would have been
    inventing the synonymy itself. Deciding that two labels mean the same thing
    is a domain judgement, and this layer has no standing to make it.

    The claim can always declare the forms it accepts - that is what
    `Especificacion.conceptos` is a tuple for. Declaring
    `("Ventas", "Ventas netas")` is one line of the Golden, it is auditable, and
    a reviewer can see exactly which labels were admitted for this claim. An
    inferred prefix rule is none of those things.

    [ES] Coincidencia exacta contra una forma declarada. Nada mas.

    UNA regla: igualdad tras normalizar mayusculas, acentos y espacios. Sin
    prefijos, sin subcadenas, sin fuzzy matching, sin embeddings, sin modelo.

    Una version anterior aceptaba una etiqueta que EMPEZARA con una forma
    declarada, asi que una afirmacion sobre "Ventas" se respondia con "Ventas
    netas". Parece inofensivo y no lo es: "Resultado" habria coincidido igual con
    "Resultado financiero", que es otra linea del mismo estado, y el sistema
    habria estado inventando la sinonimia por su cuenta. Decidir que dos
    etiquetas significan lo mismo es un juicio de dominio, y esta capa no tiene
    autoridad para hacerlo.

    La afirmacion siempre puede declarar las formas que acepta: para eso
    `Especificacion.conceptos` es una tupla. Declarar
    `("Ventas", "Ventas netas")` es una linea del Golden, es auditable, y un
    revisor puede ver exactamente que etiquetas se admitieron para esta
    afirmacion. Una regla de prefijo inferida no es nada de eso.
    """
    if concepto is None:
        return False
    etiqueta = _normalizado_para_alineacion(concepto)
    if not etiqueta:
        return False
    return any(
        etiqueta == _normalizado_para_alineacion(aceptado)
        for aceptado in aceptados
        if _normalizado_para_alineacion(aceptado)
    )


def alineada(evidencia: Evidencia, especificacion: Especificacion) -> bool:
    """Is this fact ABOUT what the claim asked, checked by rule and not by a model?

    Belonging to the same logical table authorises DONATING a component. It says
    nothing about whether the fact answers the question: a table holds sales and
    costs in adjacent rows, and both are equally complete, equally located and
    equally traceable.

    Entity and period are only checked when the claim declared them. Checking
    what nobody asked about would reject correct evidence.

    [ES] Trata este hecho de lo que pregunto la afirmacion, comprobado por regla
    y no por un modelo?

    Pertenecer a la misma tabla logica autoriza a DONAR un componente. No dice
    nada sobre si el hecho responde la pregunta: una tabla tiene ventas y costos
    en filas contiguas, y los dos son igual de completos, igual de localizados e
    igual de trazables.

    La entidad y el periodo se comprueban solo si la afirmacion los declaro.
    Comprobar lo que nadie pregunto rechazaria evidencia correcta.
    """
    if not especificacion.declarada():
        return False
    if not _concepto_coincide(evidencia.concepto, especificacion.conceptos):
        return False
    if especificacion.entidad is not None:
        if evidencia.entidad is None:
            return False
        if _normalizado_para_alineacion(evidencia.entidad) != _normalizado_para_alineacion(
            especificacion.entidad
        ):
            return False
    if especificacion.periodo is not None:
        if evidencia.periodo is None:
            return False
        if _normalizado_para_alineacion(evidencia.periodo) != _normalizado_para_alineacion(
            especificacion.periodo
        ):
            return False
    return True


def determinar_soporte(
    evidencia: Evidencia,
    tipo: str,
    integridad_exacta: bool,
    especificacion: Optional[Especificacion] = None,
) -> str:
    """Does this evidence sustain THE CLAIM? Deterministically, or not at all.

    Structural completeness is necessary and NOT sufficient. A complete fact
    sustains its own statement; whether that statement is the one being claimed
    is a separate question, and it is the one that used to be skipped.

    The order is the argument:

    1. incomplete, unlocatable or uninterpretable -> not verified. Nothing to
       sustain anything with;
    2. text -> not verified. A chunk can be locatable, well titled and about a
       different subject, and no deterministic rule can tell;
    3. no claim specification -> not verified. Without knowing what was asked,
       "this fact answers it" is not a finding, it is an assumption;
    4. the fact aligns with the declared specification -> sustains;
    5. anything else -> not verified.

    There are exactly five steps and no sixth. THERE IS NO EXTERNAL SUPPORT
    BYPASS: alignment against the declared specification is the only route to
    `sostiene`.

    NO HUMAN REFERENCE APPEARS HERE, and none may. The Gold label used to enter
    at the top and decide the outcome; the system read the answer key and was
    then scored against it. The reference now enters only in
    `metricas.evaluar_calidad`, after the prediction exists.

    No LLM participates either. If alignment cannot be established by rule, it
    stays unknown - which yields `indeterminado`, never `responder`.

    [ES] Sostiene esta evidencia LA AFIRMACION? De forma deterministica, o no.

    La completitud estructural es necesaria y NO suficiente. Un hecho completo
    sostiene su propio enunciado; si ese enunciado es el que se esta afirmando es
    otra pregunta, y es la que se estaba salteando.

    El orden es el argumento:

    1. incompleto, no localizable o no interpretable -> no verificado. No hay con
       que sostener nada;
    2. texto -> no verificado. Un chunk puede ser localizable, estar bien titulado
       y hablar de otro tema, y ninguna regla deterministica lo distingue;
    3. sin especificacion de la afirmacion -> no verificado. Sin saber que se
       pregunto, "este hecho lo responde" no es un hallazgo, es un supuesto;
    4. el hecho se alinea con la especificacion declarada -> sostiene;
    5. cualquier otra cosa -> no verificado.

    Son cinco pasos y no hay un sexto. NO HAY VALVULA DE SOPORTE EXTERNO: la
    alineacion contra la especificacion declarada es la unica via a `sostiene`.

    ACA NO APARECE NINGUNA REFERENCIA HUMANA, y no puede aparecer. La etiqueta
    del Golden entraba arriba de todo y decidia el resultado; el sistema leia la
    hoja de respuestas y despues se puntuaba contra ella. La referencia entra
    ahora solo en `metricas.evaluar_calidad`, despues de que existe la
    prediccion.

    Tampoco interviene ningun LLM. Si la alineacion no se puede establecer por
    regla, queda desconocida - lo que da `indeterminado`, nunca `responder`.

    Por que no hay valvula externa, y que exigiria una: ver la nota de
    `contrato.Evidencia`. Un `soporte_declarado` sin productor, metodo, version
    ni procedencia era una valvula sin auditar con forma de pista de auditoria, y
    se elimino.
    """
    if not integridad_exacta:
        return NO_VERIFICADO
    if tipo == NO_INTERPRETABLE:
        return NO_VERIFICADO
    if evidencia.modalidad != MODALIDAD_TABLA:
        return NO_VERIFICADO
    if especificacion is None:
        return NO_VERIFICADO
    if alineada(evidencia, especificacion):
        return SOSTIENE
    return NO_VERIFICADO


def verificar(
    evidencia: Evidencia,
    receta: Receta = RECETA_PREDETERMINADA,
    requeridos_extra: Sequence[str] = (),
    especificacion: Optional[Especificacion] = None,
) -> Veredicto:
    """Verify one piece of evidence against the requirements of its type.

    `requeridos_extra` is what the QUESTION demands beyond the type. A question
    about a period requires a period even when the type would not.

    [ES] Verifica una evidencia contra las exigencias de su tipo.

    `requeridos_extra` es lo que exige la PREGUNTA por encima del tipo. Una
    pregunta por un periodo exige periodo aunque el tipo no lo exigiera.
    """
    tipo = tipo_de(evidencia)
    presentes = presencia(evidencia)

    requeridos = tuple(
        dict.fromkeys(tuple(receta.para(tipo)) + tuple(requeridos_extra))
    )
    faltantes = tuple(c for c in requeridos if not presentes[c])

    proc_requerida = _procedencia_requerida(evidencia)
    proc_faltante = tuple(c for c in proc_requerida if not presentes[c])

    motivos: list[str] = [MOTIVO_POR_COMPONENTE[c] for c in faltantes]

    if proc_faltante:
        motivos.append(EVIDENCIA_NO_LOCALIZADA)

    # Ambiguity is not absence. In Argentina "$" is read as pesos by default,
    # but the same symbol is used for dollars; the extractor says so with
    # `moneda_inferida_de_simbolo_pesos`. The currency IS present, and it is
    # still not safe to answer with it.
    # [ES] La ambiguedad no es ausencia. En Argentina "$" se lee pesos por
    # defecto, pero el mismo simbolo se usa para dolares; el extractor lo dice
    # con `moneda_inferida_de_simbolo_pesos`. La moneda ESTA presente, y aun asi
    # no es seguro responder con ella.
    if MONEDA in requeridos and presentes[MONEDA]:
        if "moneda_inferida_de_simbolo_pesos" in evidencia.advertencias_extraccion:
            motivos.append(MONEDA_AMBIGUA)

    integridad_exacta = not faltantes

    soporte = determinar_soporte(evidencia, tipo, integridad_exacta, especificacion)

    # Ambiguity raised while composing: two linked donors disagreed, so the
    # component was deliberately left missing rather than resolved by order.
    # [ES] Ambiguedad levantada al componer: dos donantes vinculados no
    # coincidieron, asi que el componente quedo faltante a proposito en lugar de
    # resolverse por orden.
    if any(a.startswith(APORTE_AMBIGUO) for a in evidencia.advertencias_extraccion):
        motivos.append(APORTE_AMBIGUO)

    # The reason is added only when the missing-component reasons do NOT already
    # explain the insufficiency. Piling `soporte_no_verificado` on top of
    # `escala_ausente` would bury the actionable reason under a generic one.
    #
    # When the claim DID declare what it is about and the fact does not match
    # it, the reason is more specific and says so: the evidence is complete, and
    # it is about something else.
    #
    # [ES] El motivo se agrega solo cuando los motivos por componente faltante NO
    # explican ya la insuficiencia. Apilar `soporte_no_verificado` sobre
    # `escala_ausente` enterraria el motivo accionable bajo uno generico.
    #
    # Cuando la afirmacion SI declaro de que trata y el hecho no coincide, el
    # motivo es mas especifico y lo dice: la evidencia esta completa, y habla de
    # otra cosa.
    if integridad_exacta and soporte != SOSTIENE:
        if (
            especificacion is not None
            and especificacion.declarada()
            and evidencia.modalidad == MODALIDAD_TABLA
            and tipo != NO_INTERPRETABLE
        ):
            motivos.append(ALINEACION_NO_VERIFICADA)
        else:
            motivos.append(SOPORTE_NO_VERIFICADO)

    return Veredicto(
        soporte=soporte,
        tipo=tipo,
        receta=receta.nombre,
        tipologia_version=receta.tipologia_version,
        componentes_requeridos=tuple(requeridos),
        componentes_presentes=tuple(c for c in requeridos if presentes[c]),
        componentes_faltantes=faltantes,
        integridad_por_componente={c: presentes[c] for c in requeridos},
        integridad_exacta=integridad_exacta,
        procedencia_requerida=proc_requerida,
        procedencia_faltante=proc_faltante,
        procedencia_exacta=not proc_faltante,
        advertencias=tuple(evidencia.advertencias_extraccion),
        motivos=tuple(dict.fromkeys(motivos)),
        confianza_declarada=evidencia.confianza,
        document_id=evidencia.document_id,
        referencia_evidencia=evidencia.table_segment_uid or evidencia.chunk_uid,
    )


# --------------------------------------------------------------------------
# Conflict between sources / Conflicto entre fuentes
# --------------------------------------------------------------------------


# Scale factors as exact integers. A float would make 0.1 + 0.2 arithmetic decide
# whether two accounting figures agree, and an accounting identity is exact or it
# is nothing.
# [ES] Factores de escala como enteros exactos. Un float haria que la aritmetica
# de 0.1 + 0.2 decidiera si dos cifras contables coinciden, y una identidad
# contable es exacta o no es nada.
FACTORES_DE_ESCALA = {
    "unidades": Decimal(1),
    "miles": Decimal(1000),
    "millones": Decimal(1000000),
    "miles_de_millones": Decimal(1000000000),
}


def _identidad_de_afirmacion(evidencia: Evidencia) -> Optional[tuple]:
    """What makes two facts claims about the SAME thing, before comparing numbers.

    Entity, concept and period are the minimum. Without them there is nothing to
    compare, and comparing anyway would manufacture conflicts out of unrelated
    rows.

    [ES] Que vuelve a dos hechos afirmaciones sobre LO MISMO, antes de comparar
    numeros. Entidad, concepto y periodo son el minimo. Sin ellos no hay nada que
    comparar, y compararlos igual fabricaria conflictos entre filas sin relacion.
    """
    if evidencia.entidad is None or evidencia.concepto is None:
        return None
    if evidencia.periodo is None:
        return None
    return (
        _plano(evidencia.entidad),
        _plano(evidencia.concepto),
        _plano(evidencia.periodo),
    )


def _valor_canonico(evidencia: Evidencia) -> Optional[Decimal]:
    """The value brought to units, exactly, as a Decimal.

    Returns None when the scale is unknown: two figures of unknown scale are not
    in conflict, they are incomparable.

    [ES] El valor llevado a unidades, exactamente, como Decimal.

    Devuelve None si la escala es desconocida: dos cifras de escala desconocida
    no estan en conflicto, son incomparables.
    """
    if evidencia.valor is None:
        return None
    # str() first: Decimal(float) would carry the binary representation error
    # into an exact comparison.
    # [ES] str() primero: Decimal(float) arrastraria el error de la
    # representacion binaria a una comparacion exacta.
    crudo = Decimal(str(evidencia.valor))
    if evidencia.es_porcentaje:
        return crudo
    if evidencia.escala is None:
        return None
    factor = FACTORES_DE_ESCALA.get(evidencia.escala)
    return None if factor is None else crudo * factor


def _dimensiones_de_comparacion(evidencia: Evidencia) -> dict:
    """Everything that has to match before two numbers may be compared at all.

    Pesos against dollars is not a disagreement. Consolidated against individual
    is not a disagreement. Restated against nominal is not a disagreement. Each
    of these is a DIFFERENT claim, and treating them as one manufactures a
    finding out of correct data.

    [ES] Todo lo que tiene que coincidir antes de siquiera comparar dos numeros.

    Pesos contra dolares no es un desacuerdo. Consolidado contra individual no es
    un desacuerdo. Reexpresado contra nominal no es un desacuerdo. Cada uno de
    esos es una afirmacion DISTINTA, y tratarlos como una sola fabrica un
    hallazgo a partir de datos correctos.
    """
    return {
        "moneda": evidencia.moneda,
        "alcance": evidencia.alcance,
        "base_contable": evidencia.base_contable,
        "escenario": evidencia.escenario,
    }


def detectar_conflicto(evidencias: Iterable[Evidencia]) -> dict:
    """Classify each claim identity: conflict, incomparable, or neither.

    Returns a mapping from claim identity to the reason it earned, so the reason
    can be attached only to the pieces actually involved instead of smeared over
    the whole set.

    Three outcomes, and the difference between them matters:

    - `fuentes_en_conflicto`: same claim, same currency, same scope, same basis,
      same scenario - and different exact values. This is a real contradiction;
    - `comparabilidad_indeterminada`: same claim identity, but a dimension that
      would make them comparable is not declared. Today `alcance` is never
      extracted, so this is the normal outcome, and saying so is the finding;
    - nothing: the dimensions differ explicitly, so they are simply different
      statements. Two figures in ARS and USD are not in conflict, and no
      conversion is invented to force them into one.

    [ES] Clasifica cada identidad de afirmacion: conflicto, incomparable, o
    ninguna de las dos.

    Devuelve un mapeo de identidad de afirmacion al motivo que le corresponde,
    para poder adjuntar el motivo solo a las piezas realmente involucradas en
    lugar de embadurnar todo el conjunto.

    Tres resultados, y la diferencia entre ellos importa:

    - `fuentes_en_conflicto`: misma afirmacion, misma moneda, mismo alcance,
      misma base, mismo escenario - y valores exactos distintos. Es una
      contradiccion real;
    - `comparabilidad_indeterminada`: misma identidad de afirmacion, pero alguna
      dimension que las volveria comparables no esta declarada. Hoy `alcance`
      nunca se extrae, asi que este es el resultado normal, y decirlo es el
      hallazgo;
    - nada: las dimensiones difieren explicitamente, asi que son afirmaciones
      distintas. Dos cifras en ARS y USD no estan en conflicto, y no se inventa
      ninguna conversion para forzarlas a serlo.
    """
    por_identidad: dict = {}
    for e in evidencias:
        identidad = _identidad_de_afirmacion(e)
        if identidad is None:
            continue
        valor = _valor_canonico(e)
        if valor is None:
            continue
        por_identidad.setdefault(identidad, []).append((e, valor))

    motivos: dict = {}
    for identidad, piezas in por_identidad.items():
        if len(piezas) < 2:
            continue

        dimensiones = [_dimensiones_de_comparacion(e) for e, _ in piezas]

        # An explicitly different dimension means different claims: no conflict,
        # no complaint.
        # [ES] Una dimension explicitamente distinta significa afirmaciones
        # distintas: ni conflicto, ni queja.
        declaradas_distintas = any(
            len({d[k] for d in dimensiones if d[k] is not None}) > 1
            for k in ("moneda", "alcance", "base_contable", "escenario")
        )
        if declaradas_distintas:
            continue

        # A dimension nobody declared cannot be assumed equal. `alcance` is the
        # live case: the extractor does not produce it.
        # [ES] Una dimension que nadie declaro no se puede suponer igual.
        # `alcance` es el caso vivo: el extractor no lo produce.
        sin_declarar = [
            k
            for k in ("moneda", "alcance", "base_contable", "escenario")
            if any(d[k] is None for d in dimensiones)
        ]

        valores = {v for _, v in piezas}
        if len(valores) <= 1:
            continue

        motivos[identidad] = (
            COMPARABILIDAD_INDETERMINADA if sin_declarar else FUENTES_EN_CONFLICTO
        )

    return motivos


def verificar_conjunto(
    evidencias: Sequence[Evidencia],
    receta: Receta = RECETA_PREDETERMINADA,
    requeridos_extra: Sequence[str] = (),
    especificacion: Optional[Especificacion] = None,
) -> tuple[Veredicto, ...]:
    """Verify a set, adding the reasons that only exist across pieces.

    A conflict cannot be seen in one fact alone, so it is attached here - and
    only to the pieces that share the identity in question, not to the whole
    set.

    [ES] Verifica un conjunto, agregando los motivos que solo existen entre
    piezas. Un conflicto no se ve en un hecho aislado, asi que se adjunta aca - y
    solo a las piezas que comparten la identidad en cuestion, no a todo el
    conjunto.
    """
    veredictos = [
        verificar(e, receta, requeridos_extra, especificacion) for e in evidencias
    ]
    motivos_por_identidad = detectar_conflicto(evidencias)
    if not motivos_por_identidad:
        return tuple(veredictos)

    from dataclasses import replace as _replace

    salida = []
    for evidencia, veredicto in zip(evidencias, veredictos):
        identidad = _identidad_de_afirmacion(evidencia)
        motivo = motivos_por_identidad.get(identidad)
        if motivo is None:
            salida.append(veredicto)
            continue
        salida.append(
            _replace(veredicto, motivos=tuple(dict.fromkeys(veredicto.motivos + (motivo,))))
        )
    return tuple(salida)
