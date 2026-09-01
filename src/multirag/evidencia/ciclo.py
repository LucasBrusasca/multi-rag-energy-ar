"""Bounded reflexive cycle: verify, retry ONCE, then answer or abstain.

This is the decision logic only. It does not know what a database is, it never
opens a connection and it never calls a model. How each retry action is actually
executed against PostgreSQL is left to an adapter, so the policy can be tested
in full before any of it touches the canonical retriever.

WHY EXACTLY ONE RETRY. An agent that may retry "until it works" cannot be
measured: its cost is unbounded and its failures become invisible, because
enough attempts eventually surface something that looks like evidence. One
retry is a budget that both arms of the experiment can share. The limit is not
a convention here - the adapter is wrapped so that a second call raises. Code
that tries to loop fails loudly instead of quietly costing more.

WHY ABSTAINING IS AN OUTCOME, NOT AN ERROR. If the scale of an amount is not in
the document, no amount of retrieval will produce it. Answering anyway would be
the failure. The cycle returns `abstener` WITH the reason, so a reviewer can
tell a well-founded abstention from a retrieval that simply did not work.

[ES] Ciclo reflexivo acotado: verificar, reintentar UNA vez, y responder o
abstenerse.

Esto es solo la logica de decision. No sabe que es una base de datos, nunca abre
una conexion y nunca llama a un modelo. Como se ejecuta realmente cada accion de
reintento contra PostgreSQL queda en un adaptador, para poder probar la politica
completa antes de que nada de esto toque el retriever canonico.

POR QUE EXACTAMENTE UN REINTENTO. Un agente que puede reintentar "hasta que
salga" no se puede medir: su costo no tiene cota y sus fallas se vuelven
invisibles, porque con suficientes intentos siempre aparece algo que parece
evidencia. Un reintento es un presupuesto que los dos brazos del experimento
pueden compartir. Aca el limite no es una convencion: el adaptador se envuelve
para que una segunda llamada levante excepcion. El codigo que intente iterar
falla a gritos en lugar de costar mas en silencio.

POR QUE ABSTENERSE ES UN RESULTADO, NO UN ERROR. Si la escala de un importe no
esta en el documento, ninguna recuperacion la va a producir. Responder igual
seria la falla. El ciclo devuelve `abstener` CON el motivo, para que un revisor
distinga una abstencion bien fundada de una recuperacion que simplemente no
funciono.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Protocol, Sequence

from multirag.evidencia.composicion import HechoCompuesto, anclada, componer
from multirag.evidencia.contrato import Afirmacion, Evidencia
from multirag.evidencia.verificador import (
    ALINEACION_NO_VERIFICADA,
    APORTE_AMBIGUO,
    COMPARABILIDAD_INDETERMINADA,
    CONCEPTO_AUSENTE,
    ENTIDAD_AUSENTE,
    ESCALA_AUSENTE,
    EVIDENCIA_NO_LOCALIZADA,
    FUENTES_EN_CONFLICTO,
    MONEDA_AMBIGUA,
    PERIODO_AUSENTE,
    RECETA_PREDETERMINADA,
    Receta,
    SOPORTE_NO_VERIFICADO,
    UNIDAD_AUSENTE,
    VALOR_AUSENTE,
    Veredicto,
    verificar_conjunto,
)


# The whole budget, PER CLAIM. Not configurable on purpose: making it a
# parameter is how a bounded cycle quietly becomes an unbounded one.
#
# The unit matters as much as the number. A budget spent per FACT lets an item
# holding five facts spend five retries without anyone deciding to; the bound
# belongs to the question, not to how many rows happened to be retrieved. That
# is why the cycle takes an `Afirmacion` and runs exactly once over it.
#
# [ES] Todo el presupuesto, POR AFIRMACION. A proposito no es configurable:
# volverlo parametro es la forma en que un ciclo acotado se convierte en silencio
# en uno sin cota.
#
# La unidad importa tanto como el numero. Un presupuesto gastado por HECHO
# permite que un item con cinco hechos gaste cinco reintentos sin que nadie lo
# decida; la cota pertenece a la pregunta, no a cuantas filas se hayan
# recuperado. Por eso el ciclo recibe una `Afirmacion` y corre exactamente una
# vez sobre ella.
MAX_REINTENTOS = 1


# --- Decisions / Decisiones ---
RESPONDER = "responder"
ABSTENER = "abstener"
PEDIR_ACLARACION = "pedir_aclaracion"

# Complete, locatable, and nobody established that it sustains the claim. It is
# NOT an abstention: abstaining says "the evidence does not support this", and
# this says "it is not known whether it does". Collapsing the two would let an
# unevaluated case be scored as a correct abstention.
# [ES] Completo, localizable, y nadie establecio que sostenga la afirmacion. NO
# es una abstencion: abstenerse dice "la evidencia no sostiene esto", y esto dice
# "no se sabe si lo sostiene". Colapsar las dos permitiria puntuar como
# abstencion correcta un caso que nunca se evaluo.
INDETERMINADO = "indeterminado"

DECISIONES = (RESPONDER, ABSTENER, PEDIR_ACLARACION, INDETERMINADO)


# --- Retry actions / Acciones de reintento ---
# Reuse the vocabulary that already exists: `expandir_hermanos_documentales` is
# the E1 variant of orchestration/alcance.py, and `abrir_dominios_adicionales`
# is that module's multi-domain retrieval. Naming them differently here would
# create a second vocabulary for the same thing.
# [ES] Se reutiliza el vocabulario que ya existe:
# `expandir_hermanos_documentales` es la variante E1 de
# orchestration/alcance.py, y `abrir_dominios_adicionales` es la recuperacion
# multidominio de ese modulo. Nombrarlos distinto aca crearia un segundo
# vocabulario para lo mismo.
CONSULTAR_HECHOS_TABULARES = "consultar_hechos_tabulares"
EXPANDIR_HERMANOS_DOCUMENTALES = "expandir_hermanos_documentales"
EXPANDIR_DOCUMENTO = "expandir_documento"
ABRIR_DOMINIOS_ADICIONALES = "abrir_dominios_adicionales"
ACCION_PEDIR_ACLARACION = "pedir_aclaracion"

ACCIONES = (
    CONSULTAR_HECHOS_TABULARES,
    EXPANDIR_HERMANOS_DOCUMENTALES,
    EXPANDIR_DOCUMENTO,
    ABRIR_DOMINIOS_ADICIONALES,
    ACCION_PEDIR_ACLARACION,
)


class ErrorDeCiclo(RuntimeError):
    """Raised when something tries to spend more than the one allowed retry.

    [ES] Se levanta cuando algo intenta gastar mas del unico reintento
    permitido.
    """


# Which action can plausibly supply each missing component. Declared as an
# ordered table rather than as branching code, so the policy can be read and
# argued about without following control flow.
#
# The reasoning behind each row:
# - a conflict is not solved by retrieving more: two sources already disagree,
#   and choosing between them is a human call;
# - scale, currency, period and value live in the header of the table segment,
#   so the table facts are where to look;
# - the entity is declared on the cover or the heading of the document, never in
#   the cell, so the whole document has to be opened;
# - evidence that cannot be located, or a row with no label, is a defect of the
#   fragment, and the sibling fragments of the same document are the cheapest
#   place to repair it.
#
# [ES] Que accion puede plausiblemente aportar cada componente faltante.
# Declarado como tabla ordenada y no como codigo con ramas, para que la politica
# se pueda leer y discutir sin seguir un flujo de control.
#
# El razonamiento de cada fila:
# - un conflicto no se resuelve recuperando mas: dos fuentes ya se contradicen,
#   y elegir entre ellas es una decision humana;
# - escala, moneda, periodo y valor viven en el encabezado del segmento de
#   tabla, asi que los hechos tabulares son donde hay que mirar;
# - la entidad se declara en la caratula o el encabezado del documento, nunca en
#   la celda, asi que hay que abrir el documento entero;
# - una evidencia que no se puede localizar, o una fila sin etiqueta, es un
#   defecto del fragmento, y los fragmentos hermanos del mismo documento son el
#   lugar mas barato para repararlo.
PRIORIDAD_DE_MOTIVOS = (
    (FUENTES_EN_CONFLICTO, ACCION_PEDIR_ACLARACION),
    (ESCALA_AUSENTE, CONSULTAR_HECHOS_TABULARES),
    (UNIDAD_AUSENTE, CONSULTAR_HECHOS_TABULARES),
    (MONEDA_AMBIGUA, CONSULTAR_HECHOS_TABULARES),
    (PERIODO_AUSENTE, CONSULTAR_HECHOS_TABULARES),
    (VALOR_AUSENTE, CONSULTAR_HECHOS_TABULARES),
    (ENTIDAD_AUSENTE, EXPANDIR_DOCUMENTO),
    (CONCEPTO_AUSENTE, EXPANDIR_HERMANOS_DOCUMENTALES),
    (EVIDENCIA_NO_LOCALIZADA, EXPANDIR_HERMANOS_DOCUMENTALES),
    # What would make two figures comparable - the consolidated/individual
    # scope above all - is declared on the cover and the notes, not in the cell.
    # [ES] Lo que volveria comparables dos cifras - el alcance
    # consolidado/individual ante todo - se declara en la caratula y las notas,
    # no en la celda.
    (COMPARABILIDAD_INDETERMINADA, EXPANDIR_DOCUMENTO),
    # Support that no rule can establish over text may still be establishable
    # over a table: a structured fact sustains its own claim, a paragraph does
    # not. Asking for the tabular facts is the one move that can change the
    # answer here.
    # [ES] Un soporte que ninguna regla puede establecer sobre texto todavia
    # puede establecerse sobre una tabla: un hecho estructurado sostiene su
    # propia afirmacion, un parrafo no. Pedir los hechos tabulares es la unica
    # jugada que puede cambiar la respuesta aca.
    (SOPORTE_NO_VERIFICADO, CONSULTAR_HECHOS_TABULARES),
    # The evidence is complete and about something else. What could change the
    # answer is another fact of this table, not more of the same one.
    # [ES] La evidencia esta completa y habla de otra cosa. Lo que podria cambiar
    # la respuesta es otro hecho de esta tabla, no mas de este mismo.
    (ALINEACION_NO_VERIFICADA, CONSULTAR_HECHOS_TABULARES),
    # Two linked donors disagreed on the unit. Only the document can say which
    # one governs this row.
    # [ES] Dos donantes vinculados discreparon en la unidad. Solo el documento
    # puede decir cual gobierna esta fila.
    (APORTE_AMBIGUO, EXPANDIR_DOCUMENTO),
)


@dataclass(frozen=True)
class Plan:
    """The single retry that is going to be attempted, and why.

    [ES] El unico reintento que se va a intentar, y por que.
    """

    accion: str
    motivo: str
    document_ids: tuple[str, ...] = ()
    table_uids: tuple[str, ...] = ()
    dominios_sugeridos: tuple[str, ...] = ()


class AdaptadorDeReintento(Protocol):
    """What a real retrieval backend must offer to serve one retry.

    Deliberately one method. The cycle decides WHAT to ask for; the adapter
    decides HOW, and only the adapter is allowed to know about PostgreSQL.

    [ES] Lo que un backend de recuperacion real debe ofrecer para servir un
    reintento.

    Un solo metodo, a proposito. El ciclo decide QUE pedir; el adaptador decide
    COMO, y solo el adaptador tiene permitido saber de PostgreSQL.
    """

    def ejecutar(self, plan: Plan) -> Sequence[Evidencia]:
        ...


class _AdaptadorDeUnSoloUso:
    """Wrapper that makes a second retry impossible rather than discouraged.

    [ES] Envoltorio que vuelve imposible un segundo reintento, en lugar de
    desaconsejarlo.
    """

    def __init__(self, interno: AdaptadorDeReintento) -> None:
        self._interno = interno
        self.usos = 0

    def ejecutar(self, plan: Plan) -> Sequence[Evidencia]:
        if self.usos >= MAX_REINTENTOS:
            raise ErrorDeCiclo(
                f"el ciclo permite {MAX_REINTENTOS} reintento; "
                f"se intento el numero {self.usos + 1}"
            )
        self.usos += 1
        return self._interno.ejecutar(plan)


@dataclass(frozen=True)
class Resultado:
    """Everything a reviewer needs to audit one decision, for ONE claim.

    `veredicto_gobernante` is the one the answer rests on. Without it, a
    reviewer reading a `responder` cannot tell WHICH piece was answered with -
    and after a retry, the piece that repaired the claim is usually not the
    first one in the list.

    [ES] Todo lo que un revisor necesita para auditar una decision, de UNA
    afirmacion.

    `veredicto_gobernante` es aquel sobre el que se apoya la respuesta. Sin el,
    un revisor que lee un `responder` no puede saber CON QUE pieza se respondio
    - y despues de un reintento, la pieza que reparo la afirmacion normalmente no
    es la primera de la lista.
    """

    item_id: str
    decision: str
    motivos: tuple[str, ...]
    veredictos_iniciales: tuple[Veredicto, ...]
    veredictos_finales: tuple[Veredicto, ...]
    evidencias_finales: tuple[Evidencia, ...]
    hechos_compuestos: tuple[HechoCompuesto, ...] = field(default_factory=tuple)
    plan: Optional[Plan] = None
    reintentos_usados: int = 0
    evidencia_suficiente: tuple[Veredicto, ...] = field(default_factory=tuple)

    def abstuvo(self) -> bool:
        """Only an actual abstention. `indeterminado` is NOT one.

        [ES] Solo una abstencion real. `indeterminado` NO lo es.
        """
        return self.decision in (ABSTENER, PEDIR_ACLARACION)

    def respondio(self) -> bool:
        return self.decision == RESPONDER

    def veredicto_gobernante(self) -> Optional[Veredicto]:
        """The verdict the decision rests on, chosen after the retry, not before.

        If something is sufficient, that is the one. Otherwise it is the closest
        to being sufficient - fewest missing components - so the reported reason
        is the most actionable one available, not whichever piece happened to
        arrive first.

        [ES] El veredicto sobre el que se apoya la decision, elegido despues del
        reintento, no antes.

        Si algo alcanza, ese es. Si no, el que este mas cerca de alcanzar -menos
        componentes faltantes- para que el motivo reportado sea el mas accionable
        disponible, y no el de la pieza que casualmente llego primero.
        """
        if not self.veredictos_finales:
            return None
        suficientes = [v for v in self.veredictos_finales if v.suficiente()]
        if suficientes:
            return suficientes[0]
        return min(
            self.veredictos_finales,
            key=lambda v: (len(v.componentes_faltantes), len(v.motivos)),
        )

    def evidencia_gobernante(self) -> Optional[Evidencia]:
        """The piece behind the governing verdict, matched by claim reference.

        [ES] La pieza detras del veredicto gobernante, apareada por la referencia
        de la afirmacion.
        """
        veredicto = self.veredicto_gobernante()
        if veredicto is None:
            return None
        for compuesto in self.hechos_compuestos:
            referencia = (
                compuesto.efectiva.table_segment_uid or compuesto.efectiva.chunk_uid
            )
            if referencia == veredicto.referencia_evidencia:
                return compuesto.efectiva
        return self.evidencias_finales[0] if self.evidencias_finales else None


def motivos_de(veredictos: Sequence[Veredicto]) -> tuple[str, ...]:
    """The reasons of the pieces that are NOT sufficient, deduplicated.

    A set with one usable fact and four unusable ones is answerable: only the
    reasons of the pieces that fail are collected.

    [ES] Los motivos de las piezas que NO alcanzan, sin duplicados.

    Un conjunto con un hecho utilizable y cuatro inutilizables se puede
    responder: solo se juntan los motivos de las piezas que fallan.
    """
    motivos: list[str] = []
    for v in veredictos:
        if v.suficiente():
            continue
        motivos.extend(v.motivos)
    return tuple(dict.fromkeys(motivos))


def hay_evidencia_suficiente(veredictos: Sequence[Veredicto]) -> bool:
    """At least one piece of evidence sustains the claim on its own.

    [ES] Al menos una pieza de evidencia sostiene la afirmacion por si sola.
    """
    return any(v.suficiente() for v in veredictos)


def planificar_reintento(
    veredictos: Sequence[Veredicto],
    evidencias: Sequence[Evidencia] = (),
) -> Optional[Plan]:
    """Choose the ONE retry worth making, or None if none is.

    Returns None when the evidence is already sufficient: planning a retry that
    is not needed would spend budget to change nothing.

    [ES] Elige el UNICO reintento que vale la pena, o None si ninguno lo vale.

    Devuelve None cuando la evidencia ya alcanza: planificar un reintento que no
    hace falta gastaria presupuesto para no cambiar nada.
    """
    if hay_evidencia_suficiente(veredictos):
        return None

    motivos = motivos_de(veredictos)
    if not motivos:
        return None

    documentos = tuple(
        dict.fromkeys(e.document_id for e in evidencias if e.document_id)
    )
    tablas = tuple(dict.fromkeys(e.table_uid for e in evidencias if e.table_uid))

    for motivo, accion in PRIORIDAD_DE_MOTIVOS:
        if motivo not in motivos:
            continue
        # Expanding by document or by sibling needs a document to expand from.
        # With none, the only move left is to widen the domains.
        # [ES] Expandir por documento o por hermanos necesita un documento del
        # cual expandir. Sin ninguno, lo unico que queda es abrir dominios.
        if accion in (EXPANDIR_DOCUMENTO, EXPANDIR_HERMANOS_DOCUMENTALES):
            if not documentos:
                accion = ABRIR_DOMINIOS_ADICIONALES
        return Plan(
            accion=accion,
            motivo=motivo,
            document_ids=documentos,
            table_uids=tablas,
        )

    return Plan(
        accion=ABRIR_DOMINIOS_ADICIONALES,
        motivo=motivos[0],
        document_ids=documentos,
        table_uids=tablas,
    )


def _decision_final(
    veredictos: Sequence[Veredicto],
    gobernables: Optional[Sequence[Veredicto]] = None,
) -> tuple[str, tuple[str, ...]]:
    """Answer, ask, defer as unknown, or abstain - and say why.

    The order encodes four different situations that must not be collapsed:

    1. something sustains the claim -> answer;
    2. two comparable sources contradict each other -> ask. The system DID find
       the evidence; what is missing is a human decision about which one
       governs;
    3. nothing establishes whether the evidence sustains the claim, or whether
       two figures are even comparable -> undetermined. This is NOT an
       abstention. Scoring it as one would credit the system for a judgement it
       never made;
    4. a component the claim needs is simply not there -> abstain.

    [ES] Responder, preguntar, dejar en desconocido, o abstenerse - y decir por
    que.

    El orden codifica cuatro situaciones distintas que no deben colapsarse:

    1. algo sostiene la afirmacion -> responder;
    2. dos fuentes comparables se contradicen -> preguntar. El sistema SI
       encontro la evidencia; lo que falta es una decision humana sobre cual
       manda;
    3. nada establece si la evidencia sostiene la afirmacion, ni si dos cifras
       son siquiera comparables -> indeterminado. Esto NO es una abstencion.
       Puntuarlo como tal le acreditaria al sistema un juicio que nunca hizo;
    4. un componente que la afirmacion necesita simplemente no esta ->
       abstenerse.
    """
    # Answering is decided over the pieces ALLOWED to answer; the reasons are
    # gathered over all of them, so a donor that is itself broken still reports
    # why.
    # [ES] Responder se decide sobre las piezas HABILITADAS a responder; los
    # motivos se juntan sobre todas, para que un donante roto igual informe por
    # que lo esta.
    if hay_evidencia_suficiente(veredictos if gobernables is None else gobernables):
        return RESPONDER, ()

    motivos = motivos_de(veredictos)

    if FUENTES_EN_CONFLICTO in motivos:
        return PEDIR_ACLARACION, motivos
    if COMPARABILIDAD_INDETERMINADA in motivos:
        return INDETERMINADO, motivos
    if ALINEACION_NO_VERIFICADA in motivos:
        return INDETERMINADO, motivos
    if any(v.indeterminado() for v in veredictos):
        return INDETERMINADO, motivos
    return ABSTENER, motivos


def como_afirmacion(entrada, item_id: str = "item-anonimo") -> Afirmacion:
    """Accept an `Afirmacion` or a bare sequence of evidence, always return one.

    A bare sequence is still ONE claim: whoever calls with a list is asking one
    question, so it gets one retry budget. This is the guarantee that no caller
    can spend N retries by holding N facts.

    [ES] Acepta una `Afirmacion` o una secuencia suelta de evidencia, y siempre
    devuelve una.

    Una secuencia suelta sigue siendo UNA afirmacion: quien llama con una lista
    esta haciendo una pregunta, asi que recibe un presupuesto de reintento. Esta
    es la garantia de que ningun invocante puede gastar N reintentos por tener N
    hechos.
    """
    if isinstance(entrada, Afirmacion):
        return entrada
    return Afirmacion(item_id=item_id, evidencias=tuple(entrada))


def _verificar_afirmacion(
    afirmacion: Afirmacion, evidencias: Sequence[Evidencia], receta: Receta
) -> tuple[tuple[HechoCompuesto, ...], tuple[Veredicto, ...]]:
    """Compose first, then verify. Never the other way round.

    Verifying before composing reports as missing a component the document does
    declare, only in a neighbouring cell. Composing is what turns "the amount
    has no scale" into "the amount has the scale its table declares".

    [ES] Componer primero, verificar despues. Nunca al reves.

    Verificar antes de componer reporta como faltante un componente que el
    documento si declara, solo que en una celda vecina. Componer es lo que
    convierte "el importe no tiene escala" en "el importe tiene la escala que
    declara su tabla".
    """
    compuestos = componer(evidencias)
    veredictos = verificar_conjunto(
        [c.efectiva for c in compuestos],
        receta,
        afirmacion.componentes_requeridos,
        afirmacion.especificacion_efectiva(),
    )
    return compuestos, veredictos


def ejecutar_ciclo(
    afirmacion,
    adaptador: Optional[AdaptadorDeReintento] = None,
    receta: Receta = RECETA_PREDETERMINADA,
) -> Resultado:
    """Run the bounded cycle ONCE over ONE claim.

    The sequence is fixed: compose, verify the whole set, plan at most one
    retry, add the evidence it brings, RECOMPOSE, verify again, decide. The
    recomposition is not decoration - the retry usually brings the header that
    completes a fact, and without composing again that header would be counted
    as one more incomplete row.

    With no adapter there is no retry available, and the cycle degrades to the
    single-pass behaviour of `I1`. That is not a fallback: it is how the arms of
    the integrity study differ from one another.

    [ES] Corre el ciclo acotado UNA vez sobre UNA afirmacion.

    La secuencia es fija: componer, verificar el conjunto completo, planificar
    como maximo un reintento, agregar la evidencia que traiga, RECOMPONER,
    volver a verificar, decidir. La recomposicion no es adorno: el reintento
    suele traer el encabezado que completa un hecho, y sin volver a componer ese
    encabezado se contaria como una fila incompleta mas.

    Sin adaptador no hay reintento disponible, y el ciclo degrada al
    comportamiento de una sola pasada de `I1`. No es un plan B: es exactamente
    en lo que difieren los brazos del estudio de integridad.
    """
    afirmacion = como_afirmacion(afirmacion)
    evidencias = afirmacion.evidencias

    compuestos, iniciales = _verificar_afirmacion(afirmacion, evidencias, receta)

    if hay_evidencia_suficiente(iniciales):
        return Resultado(
            item_id=afirmacion.item_id,
            decision=RESPONDER,
            motivos=(),
            veredictos_iniciales=iniciales,
            veredictos_finales=iniciales,
            evidencias_finales=tuple(c.efectiva for c in compuestos),
            hechos_compuestos=compuestos,
            plan=None,
            reintentos_usados=0,
            evidencia_suficiente=tuple(v for v in iniciales if v.suficiente()),
        )

    plan = planificar_reintento(iniciales, evidencias)

    if plan is None or adaptador is None or plan.accion == ACCION_PEDIR_ACLARACION:
        decision, motivos = _decision_final(iniciales)
        if plan is not None and plan.accion == ACCION_PEDIR_ACLARACION:
            decision = PEDIR_ACLARACION
        return Resultado(
            item_id=afirmacion.item_id,
            decision=decision,
            motivos=motivos,
            veredictos_iniciales=iniciales,
            veredictos_finales=iniciales,
            evidencias_finales=tuple(c.efectiva for c in compuestos),
            hechos_compuestos=compuestos,
            plan=plan,
            reintentos_usados=0,
        )

    una_sola_vez = _AdaptadorDeUnSoloUso(adaptador)
    agregadas = tuple(una_sola_vez.ejecutar(plan) or ())

    # The retry ADDS evidence, it does not replace it. Discarding the initial
    # set would let a worse retry look like an improvement.
    # [ES] El reintento AGREGA evidencia, no la reemplaza. Descartar el conjunto
    # inicial permitiria que un reintento peor pareciera una mejora.
    finales_evidencia = tuple(evidencias) + agregadas
    compuestos_finales, finales = _verificar_afirmacion(
        afirmacion, finales_evidencia, receta
    )

    # Everything the retry brought may DONATE a component; only what is anchored
    # to the claim may ANSWER it. Without this, an unrelated complete row from
    # elsewhere would silently turn an abstention into an answer.
    # [ES] Todo lo que trajo el reintento puede DONAR un componente; solo lo
    # anclado a la afirmacion puede RESPONDERLA. Sin esto, una fila completa e
    # inconexa de otro lado convertiria en silencio una abstencion en respuesta.
    gobernables = tuple(
        veredicto
        for compuesto, veredicto in zip(compuestos_finales, finales)
        if anclada(compuesto.base, evidencias)
    )

    decision, motivos = _decision_final(finales, gobernables)

    return Resultado(
        item_id=afirmacion.item_id,
        decision=decision,
        motivos=motivos,
        veredictos_iniciales=iniciales,
        veredictos_finales=finales,
        evidencias_finales=tuple(c.efectiva for c in compuestos_finales),
        hechos_compuestos=compuestos_finales,
        plan=plan,
        reintentos_usados=una_sola_vez.usos,
        evidencia_suficiente=tuple(v for v in finales if v.suficiente()),
    )


def adaptador_de_prueba(
    respuesta: Callable[[Plan], Sequence[Evidencia]]
) -> AdaptadorDeReintento:
    """Build an adapter from a plain function, for tests and fixtures.

    [ES] Arma un adaptador a partir de una funcion comun, para pruebas y
    fixtures.
    """

    class _Doble:
        def __init__(self) -> None:
            self.planes: list[Plan] = []

        def ejecutar(self, plan: Plan) -> Sequence[Evidencia]:
            self.planes.append(plan)
            return respuesta(plan)

    return _Doble()
