"""Integrity metrics for the working arms I0 / I1 / I2.

WHAT THE UNIT IS. The CLAIM (`item_id`), and for aggregation the document.
Never the fact and never the table segment. Indexing by `table_segment_uid`
collapses every row of one table into a single reference, so two different
claims are counted as one; and running the cycle per fact lets an item holding
five facts spend five retries that nobody budgeted.

WHAT THESE NUMBERS ARE. Completeness and locatability of evidence, plus what
the cycle decided. Nothing here measures whether a value is CORRECT: a populated
field can be wrong, and the extractor cannot be its own ground truth. `exactitud`
stays None instead of being quietly replaced by completeness.

WHAT NEEDS A HUMAN REFERENCE. Every quality-of-abstention figure. Their
denominators are the point:

- precision of abstention  = correct abstentions / ALL abstentions
- rate of correct abstention = non-answerable correctly abstained / ALL non-answerable
- FALSE VETO RATE          = answerable that were abstained / ALL ANSWERABLE

The last one is the one that used to be wrong. Dividing false vetoes by the
abstentions describes the COMPOSITION of the abstentions, not how often the
system vetoes something it could have answered. An arm that abstains twice and
gets one wrong would score 0.5 either way; an arm that abstains on half the
answerable corpus and gets them all wrong would also score 1.0 under the old
denominator, no matter how large the corpus. Only the answerable population
answers the question being asked.

WHAT IS PROVISIONAL. `I0`, `I1` and `I2` are working labels, not preregistered
protocol. `I0` is a MODELLED projection of the current linearized output, not a
measurement of the production pipeline; every result it produces is stamped
`simulado=True`.

[ES] Metricas de integridad para los brazos de trabajo I0 / I1 / I2.

CUAL ES LA UNIDAD. La AFIRMACION (`item_id`), y para agregar, el documento.
Nunca el hecho y nunca el segmento de tabla. Indexar por `table_segment_uid`
colapsa todas las filas de una tabla en una sola referencia, asi que dos
afirmaciones distintas se cuentan como una; y correr el ciclo por hecho permite
que un item con cinco hechos gaste cinco reintentos que nadie presupuesto.

QUE SON ESTOS NUMEROS. Completitud y localizabilidad de la evidencia, mas lo que
decidio el ciclo. Nada de esto mide si un valor es CORRECTO: un campo poblado
puede estar mal, y el extractor no puede ser su propia verdad de referencia.
`exactitud` queda en None en lugar de ser reemplazada en silencio por la
completitud.

QUE EXIGE REFERENCIA HUMANA. Toda cifra de calidad de la abstencion. Sus
denominadores son el punto:

- precision de abstencion    = abstenciones correctas / TODAS las abstenciones
- tasa de abstencion correcta = no respondibles correctamente abstenidos / TODOS los no respondibles
- TASA DE FALSO VETO         = respondibles abstenidos / TODOS LOS RESPONDIBLES

La ultima es la que estaba mal. Dividir los falsos vetos por las abstenciones
describe la COMPOSICION de las abstenciones, no cada cuanto el sistema veta algo
que podria haber respondido. Un brazo que se abstiene dos veces y erra una da
0,5 de cualquier modo; un brazo que se abstiene sobre la mitad del corpus
respondible y las erra todas tambien daria 1,0 con el denominador viejo, sin
importar el tamano del corpus. Solo la poblacion respondible responde la
pregunta que se esta haciendo.

QUE ES PROVISIONAL. `I0`, `I1` e `I2` son etiquetas de trabajo, no protocolo
preregistrado. `I0` es una proyeccion MODELADA de la salida linealizada actual,
no una medicion del pipeline productivo; todo resultado que produce queda
sellado con `simulado=True`.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field, replace
from typing import Optional, Sequence

from multirag.evidencia.ciclo import (
    ABSTENER,
    AdaptadorDeReintento,
    INDETERMINADO,
    PEDIR_ACLARACION,
    RESPONDER,
    ejecutar_ciclo,
)
from multirag.evidencia.contrato import Afirmacion, Evidencia, Localizacion
from multirag.evidencia.verificador import (
    COMPONENTES_SEMANTICOS,
    ENTIDAD,
    ESCALA,
    MONEDA,
    MONETARIO,
    PERIODO,
    RECETA_PREDETERMINADA,
    Receta,
    VALOR,
    Veredicto,
    presencia,
)


I0 = "I0"
I1 = "I1"
I2 = "I2"
BRAZOS = (I0, I1, I2)

ETIQUETAS_PROVISIONALES = True

DESCRIPCION_BRAZOS = {
    I0: "salida linealizada actual (proyeccion simulada, no medida)",
    I1: "table-aware + contrato + verificador + composicion",
    I2: "I1 + un reintento dirigido por afirmacion + abstencion",
}


# The exact fact integrity named in PRIORIDADES 7.1. `unidad` is the scale and
# `moneda` the currency, kept apart because a table can declare one without the
# other. It applies to monetary facts only: demanding a currency of a rate would
# report a defect that does not exist.
# [ES] La integridad exacta del hecho nombrada en PRIORIDADES 7.1. `unidad` es
# la escala y `moneda` la moneda, separadas porque una tabla puede declarar una
# sin la otra. Aplica solo a hechos monetarios: exigirle moneda a una tasa
# reportaria un defecto inexistente.
COMPONENTES_DEL_HECHO = (ENTIDAD, PERIODO, ESCALA, MONEDA, VALOR)


def proyectar_i0_simulado(evidencia: Evidencia) -> Evidencia:
    """Model the current linearized output: the text survives, the grid does not.

    Today a table reaches the index as flattened text inside a chunk. The number
    is still readable, but the cell coordinates, the table identity and the
    column header that carried scale, currency and period are gone. This
    projection reproduces that loss so the arms can be compared on the same
    claims.

    Dropping the table identity also disables composition, which is faithful:
    without a logical table there is no explicit link through which a header
    could donate its unit.

    IT IS A MODEL, NOT A MEASUREMENT. Any result derived from it is marked
    `simulado`. Replacing it with a real measurement of the linearized output is
    a precondition for reporting `I0` as a baseline outside development.

    [ES] Modela la salida linealizada actual: sobrevive el texto, no la grilla.

    Hoy una tabla llega al indice como texto aplanado dentro de un chunk. El
    numero sigue siendo legible, pero se pierden las coordenadas de celda, la
    identidad de la tabla y el encabezado de columna que llevaba escala, moneda
    y periodo. Esta proyeccion reproduce esa perdida para poder comparar los
    brazos sobre las mismas afirmaciones.

    Perder la identidad de tabla tambien inhabilita la composicion, y eso es
    fiel: sin tabla logica no hay vinculo explicito por el cual un encabezado
    pueda donar su unidad.

    ES UN MODELO, NO UNA MEDICION. Todo resultado derivado queda marcado
    `simulado`. Reemplazarla por una medicion real de la salida linealizada es
    condicion previa para reportar `I0` como baseline fuera de desarrollo.
    """
    return replace(
        evidencia,
        table_uid=None,
        table_segment_uid=None,
        continuation_of=None,
        escala=None,
        moneda=None,
        periodo=None,
        localizacion=Localizacion(
            paginas=evidencia.localizacion.paginas,
            hoja=evidencia.localizacion.hoja,
        ),
    )


@dataclass(frozen=True)
class Medicion:
    """Latency, tokens and cost - only when they were actually measured.

    Every field defaults to None, and None is reported as "not measured", never
    as zero. A zero would state that the arm was free.

    [ES] Latencia, tokens y costo - solo cuando se midieron de verdad.

    Todo campo arranca en None, y None se reporta como "no medido", nunca como
    cero. Un cero afirmaria que el brazo salio gratis.
    """

    latencia_ms: Optional[float] = None
    tokens_entrada: Optional[int] = None
    tokens_salida: Optional[int] = None
    costo_usd: Optional[float] = None

    def medida(self) -> bool:
        return any(
            v is not None
            for v in (
                self.latencia_ms,
                self.tokens_entrada,
                self.tokens_salida,
                self.costo_usd,
            )
        )


@dataclass(frozen=True)
class Observacion:
    """One CLAIM, under one arm, after the whole cycle has run.

    [ES] Una AFIRMACION, bajo un brazo, despues de correr el ciclo entero.
    """

    brazo: str
    item_id: str
    document_id: Optional[str]
    tipo: str

    presencia_evidencia: bool
    integridad_por_componente: dict
    integridad_exacta: bool
    integridad_exacta_del_hecho: Optional[bool]
    procedencia_exacta: bool
    soporte: str

    decision: str
    motivos: tuple[str, ...]
    reintentos_usados: int
    confianza_declarada: Optional[str]

    # Whether the retry actually brought something, and whether the governing
    # fact needed components from more than one piece.
    # [ES] Si el reintento trajo algo, y si el hecho gobernante necesito
    # componentes de mas de una pieza.
    evidencias_agregadas: int = 0
    compuesto: bool = False

    def abstuvo(self) -> bool:
        return self.decision in (ABSTENER, PEDIR_ACLARACION)

    def respondio(self) -> bool:
        return self.decision == RESPONDER

    def confianza_alta_con_integridad_incompleta(self) -> bool:
        return self.confianza_declarada == "alta" and not self.integridad_exacta


def _integridad_del_hecho(veredicto: Veredicto, presentes: dict) -> Optional[bool]:
    """The fixed 5-tuple of PRIORIDADES 7.1, for monetary facts only.

    [ES] La tupla fija de 5 de PRIORIDADES 7.1, solo para hechos monetarios.
    """
    if veredicto.tipo != MONETARIO:
        return None
    return all(presentes.get(c, False) for c in COMPONENTES_DEL_HECHO)


def observar(
    afirmaciones: Sequence[Afirmacion],
    brazo: str,
    adaptador: Optional[AdaptadorDeReintento] = None,
    receta: Receta = RECETA_PREDETERMINADA,
) -> list[Observacion]:
    """Run one arm over a set of CLAIMS: one cycle, one retry budget, each.

    The observation is built from the GOVERNING verdict after the cycle, not
    from the first piece of the initial set. After a retry the piece that
    repaired the claim is usually not the first one, and reading index zero
    would report the state of evidence that the retry already superseded.

    [ES] Corre un brazo sobre un conjunto de AFIRMACIONES: un ciclo y un
    presupuesto de reintento para cada una.

    La observacion se arma con el veredicto GOBERNANTE despues del ciclo, no con
    la primera pieza del conjunto inicial. Tras un reintento, la pieza que reparo
    la afirmacion normalmente no es la primera, y leer el indice cero reportaria
    el estado de una evidencia que el reintento ya superó.
    """
    if brazo not in BRAZOS:
        raise ValueError(f"brazo desconocido: {brazo!r}; se esperaba uno de {BRAZOS}")

    # Only I2 is allowed to spend the retry. Giving I1 an adapter would erase
    # the very difference the two arms exist to measure.
    # [ES] Solo I2 tiene permitido gastar el reintento. Darle un adaptador a I1
    # borraria justamente la diferencia que los dos brazos existen para medir.
    adaptador_efectivo = adaptador if brazo == I2 else None

    observaciones: list[Observacion] = []
    for afirmacion in afirmaciones:
        if brazo == I0:
            afirmacion = replace(
                afirmacion,
                evidencias=tuple(
                    proyectar_i0_simulado(e) for e in afirmacion.evidencias
                ),
            )

        resultado = ejecutar_ciclo(afirmacion, adaptador_efectivo, receta)

        veredicto = resultado.veredicto_gobernante()
        gobernante = resultado.evidencia_gobernante()
        presentes = presencia(gobernante) if gobernante is not None else {}

        compuesto = any(
            c.compuesto()
            for c in resultado.hechos_compuestos
            if gobernante is not None and c.efectiva is gobernante
        )

        observaciones.append(
            Observacion(
                brazo=brazo,
                item_id=afirmacion.item_id,
                document_id=afirmacion.documento_principal(),
                tipo=veredicto.tipo if veredicto else "sin_evidencia",
                presencia_evidencia=bool(veredicto and veredicto.procedencia_exacta),
                integridad_por_componente=(
                    dict(veredicto.integridad_por_componente) if veredicto else {}
                ),
                integridad_exacta=bool(veredicto and veredicto.integridad_exacta),
                integridad_exacta_del_hecho=(
                    _integridad_del_hecho(veredicto, presentes) if veredicto else None
                ),
                procedencia_exacta=bool(veredicto and veredicto.procedencia_exacta),
                soporte=veredicto.soporte if veredicto else "no_verificado",
                decision=resultado.decision,
                motivos=resultado.motivos,
                reintentos_usados=resultado.reintentos_usados,
                confianza_declarada=veredicto.confianza_declarada if veredicto else None,
                evidencias_agregadas=len(resultado.evidencias_finales)
                - len(afirmacion.evidencias),
                compuesto=compuesto,
            )
        )
    return observaciones


def _tasa(numerador: int, denominador: int) -> Optional[float]:
    return numerador / denominador if denominador else None


@dataclass(frozen=True)
class CalidadDeRespuesta:
    """Quality figures. All None unless a human reference was supplied.

    None means NOT COMPUTED. It is not zero, and it must never be printed as
    one: a zero would assert that the system never abstained correctly.

    [ES] Cifras de calidad. Todas None salvo que se aporte referencia humana.

    None significa NO CALCULADA. No es cero, y nunca debe imprimirse como tal:
    un cero afirmaria que el sistema jamas se abstuvo correctamente.
    """

    # abstenciones correctas / TODAS las abstenciones
    precision_de_abstencion: Optional[float] = None
    # no respondibles correctamente abstenidos / TODOS los no respondibles
    tasa_de_abstencion_correcta: Optional[float] = None
    # respondibles abstenidos / TODOS los respondibles
    tasa_de_falso_veto: Optional[float] = None
    # items respondidos / total de items con referencia
    cobertura: Optional[float] = None

    n_respondibles: int = 0
    n_no_respondibles: int = 0
    n_abstenciones_con_referencia: int = 0

    def calculada(self) -> bool:
        return self.tasa_de_falso_veto is not None or self.precision_de_abstencion is not None


def evaluar_calidad(
    observaciones: Sequence[Observacion], referencia: Optional[dict]
) -> CalidadDeRespuesta:
    """Compute the quality figures, each over its OWN denominator.

    `referencia` maps `item_id` to whether a human says the claim was answerable
    from the evidence. Items absent from it are simply not judged and take part
    in no denominator.

    [ES] Calcula las cifras de calidad, cada una sobre SU PROPIO denominador.

    `referencia` mapea `item_id` a si un humano dice que la afirmacion era
    respondible con la evidencia. Los items ausentes simplemente no fueron
    juzgados y no participan de ningun denominador.
    """
    if not referencia:
        return CalidadDeRespuesta()

    juzgadas = [o for o in observaciones if o.item_id in referencia]
    respondibles = [o for o in juzgadas if referencia[o.item_id]]
    no_respondibles = [o for o in juzgadas if not referencia[o.item_id]]
    abstenciones = [o for o in juzgadas if o.abstuvo()]

    abstenciones_correctas = [o for o in abstenciones if not referencia[o.item_id]]
    falsos_vetos = [o for o in abstenciones if referencia[o.item_id]]

    return CalidadDeRespuesta(
        precision_de_abstencion=_tasa(len(abstenciones_correctas), len(abstenciones)),
        tasa_de_abstencion_correcta=_tasa(
            len(abstenciones_correctas), len(no_respondibles)
        ),
        # The denominator is every ANSWERABLE item, not every abstention.
        # [ES] El denominador es todo item RESPONDIBLE, no toda abstencion.
        tasa_de_falso_veto=_tasa(len(falsos_vetos), len(respondibles)),
        cobertura=_tasa(sum(1 for o in juzgadas if o.respondio()), len(juzgadas)),
        n_respondibles=len(respondibles),
        n_no_respondibles=len(no_respondibles),
        n_abstenciones_con_referencia=len(abstenciones),
    )


@dataclass(frozen=True)
class ResumenDocumento:
    """One document's own numbers. This is the unit that can be averaged.

    [ES] Los numeros propios de un documento. Esta es la unidad promediable.
    """

    document_id: Optional[str]
    n: int
    presencia_evidencia: Optional[float]
    integridad_exacta: Optional[float]
    integridad_por_componente: dict
    abstenciones: int
    indeterminados: int


@dataclass(frozen=True)
class Resumen:
    """The report of one arm, with its caveats attached as data.

    [ES] El reporte de un brazo, con sus salvedades adjuntas como dato.
    """

    brazo: str
    simulado: bool
    receta: str
    tipologia_version: str
    etiquetas_provisionales: bool

    n_items: int
    n_documentos: int
    n_items_multidocumento: int

    # Pooled over every claim. Named so it cannot be mistaken for a rate that
    # supports inference. These describe BEHAVIOUR, not quality: they say what
    # the arm did, never whether it was right.
    # [ES] Agrupado sobre todas las afirmaciones. Nombrado para que no se
    # confunda con una tasa que soporte inferencia. Describen CONDUCTA, no
    # calidad: dicen lo que hizo el brazo, nunca si acerto.
    global_agrupado_no_inferencial: dict

    por_documento: tuple[ResumenDocumento, ...]
    mediana_entre_documentos: dict
    rango_entre_documentos: dict

    integridad_por_componente: dict
    integridad_exacta_del_hecho: Optional[float]
    distribucion_por_tipo: dict
    distribucion_por_soporte: dict

    confianza_alta_con_integridad_incompleta: int

    calidad: CalidadDeRespuesta = field(default_factory=CalidadDeRespuesta)

    # Accuracy is deliberately not computed here. See the module docstring.
    # [ES] La exactitud a proposito no se calcula aca. Ver el docstring del
    # modulo.
    exactitud: Optional[float] = None

    medicion: Medicion = field(default_factory=Medicion)

    def advertencias(self) -> tuple[str, ...]:
        """The caveats a reader must see before the numbers.

        [ES] Las salvedades que un lector tiene que ver antes que los numeros.
        """
        avisos = [
            "completitud no es exactitud: un campo poblado puede estar mal",
            "completitud estructural no es soporte: que un fragmento sea "
            "localizable no prueba que sostenga la afirmacion",
            f"unidad de analisis: documento (n={self.n_documentos}); "
            f"los {self.n_items} items no son independientes",
            f"tipologia sin ratificar: {self.tipologia_version}",
        ]
        if self.etiquetas_provisionales:
            avisos.append("I0/I1/I2 son etiquetas de trabajo, no protocolo preregistrado")
        if self.simulado:
            avisos.append("brazo simulado: proyeccion modelada, no medicion del pipeline")
        if not self.calidad.calculada():
            avisos.append(
                "sin referencia humana: precision de abstencion, tasa de abstencion "
                "correcta, falso veto y cobertura NO calculados"
            )
        if self.n_items_multidocumento:
            avisos.append(
                f"{self.n_items_multidocumento} items cruzan mas de un documento y "
                f"se agrupan bajo None en lugar de atribuirse a uno"
            )
        if not self.medicion.medida():
            avisos.append("latencia, tokens y costo no medidos en esta corrida")
        return tuple(avisos)


def resumir(
    observaciones: Sequence[Observacion],
    referencia: Optional[dict] = None,
    medicion: Optional[Medicion] = None,
    receta: Receta = RECETA_PREDETERMINADA,
) -> Resumen:
    """Aggregate observations of ONE arm, grouped by document.

    [ES] Agrega observaciones de UN brazo, agrupadas por documento.
    """
    if not observaciones:
        raise ValueError("no hay observaciones que resumir")

    brazos = {o.brazo for o in observaciones}
    if len(brazos) > 1:
        raise ValueError(f"un resumen describe un solo brazo; llegaron {sorted(brazos)}")
    brazo = observaciones[0].brazo

    items = {o.item_id for o in observaciones}
    if len(items) != len(observaciones):
        raise ValueError(
            "hay item_id repetidos: un resumen cuenta cada afirmacion una sola vez"
        )

    n = len(observaciones)

    por_doc: dict = {}
    for o in observaciones:
        por_doc.setdefault(o.document_id, []).append(o)

    componentes = tuple(COMPONENTES_SEMANTICOS)

    def _componentes(grupo: Sequence[Observacion]) -> dict:
        salida = {}
        for c in componentes:
            aplicables = [o for o in grupo if c in o.integridad_por_componente]
            poblados = sum(1 for o in aplicables if o.integridad_por_componente[c])
            salida[c] = _tasa(poblados, len(aplicables))
        return salida

    documentos = tuple(
        ResumenDocumento(
            document_id=doc,
            n=len(grupo),
            presencia_evidencia=_tasa(
                sum(1 for o in grupo if o.presencia_evidencia), len(grupo)
            ),
            integridad_exacta=_tasa(
                sum(1 for o in grupo if o.integridad_exacta), len(grupo)
            ),
            integridad_por_componente=_componentes(grupo),
            abstenciones=sum(1 for o in grupo if o.abstuvo()),
            indeterminados=sum(1 for o in grupo if o.decision == INDETERMINADO),
        )
        for doc, grupo in sorted(por_doc.items(), key=lambda kv: str(kv[0]))
    )

    def _entre_documentos(extraer):
        valores = [v for v in (extraer(d) for d in documentos) if v is not None]
        if not valores:
            return None, None
        return statistics.median(valores), (min(valores), max(valores))

    med_pres, rango_pres = _entre_documentos(lambda d: d.presencia_evidencia)
    med_int, rango_int = _entre_documentos(lambda d: d.integridad_exacta)

    monetarios = [o for o in observaciones if o.integridad_exacta_del_hecho is not None]
    integridad_hecho = _tasa(
        sum(1 for o in monetarios if o.integridad_exacta_del_hecho), len(monetarios)
    )

    tipos: dict = {}
    soportes: dict = {}
    for o in observaciones:
        tipos[o.tipo] = tipos.get(o.tipo, 0) + 1
        soportes[o.soporte] = soportes.get(o.soporte, 0) + 1

    return Resumen(
        brazo=brazo,
        simulado=(brazo == I0),
        receta=receta.nombre,
        tipologia_version=receta.tipologia_version,
        etiquetas_provisionales=ETIQUETAS_PROVISIONALES,
        n_items=n,
        n_documentos=len(por_doc),
        n_items_multidocumento=sum(1 for o in observaciones if o.document_id is None),
        global_agrupado_no_inferencial={
            "presencia_evidencia": _tasa(
                sum(1 for o in observaciones if o.presencia_evidencia), n
            ),
            "integridad_exacta": _tasa(
                sum(1 for o in observaciones if o.integridad_exacta), n
            ),
            # Behaviour, not quality: what the arm did, not whether it was right.
            # [ES] Conducta, no calidad: lo que hizo el brazo, no si acerto.
            "tasa_de_respuesta": _tasa(
                sum(1 for o in observaciones if o.respondio()), n
            ),
            "tasa_de_abstencion": _tasa(sum(1 for o in observaciones if o.abstuvo()), n),
            "tasa_de_indeterminado": _tasa(
                sum(1 for o in observaciones if o.decision == INDETERMINADO), n
            ),
            "items_compuestos": sum(1 for o in observaciones if o.compuesto),
            "reintentos_usados": sum(o.reintentos_usados for o in observaciones),
        },
        por_documento=documentos,
        mediana_entre_documentos={
            "presencia_evidencia": med_pres,
            "integridad_exacta": med_int,
        },
        rango_entre_documentos={
            "presencia_evidencia": rango_pres,
            "integridad_exacta": rango_int,
        },
        integridad_por_componente=_componentes(observaciones),
        integridad_exacta_del_hecho=integridad_hecho,
        distribucion_por_tipo=tipos,
        distribucion_por_soporte=soportes,
        confianza_alta_con_integridad_incompleta=sum(
            1 for o in observaciones if o.confianza_alta_con_integridad_incompleta()
        ),
        calidad=evaluar_calidad(observaciones, referencia),
        medicion=medicion or Medicion(),
    )
