"""Evidence contract: what has to be on the table before an answer is allowed.

The contract is a REPRESENTATION, not an enrichment. It reads what the
extractor and the chunk already produced, marks explicitly what is absent, and
invents nothing. Three rules govern every field:

1. a sentinel is not a value. `entidad == fuente` means the extractor fell back
   to the file name; the contract records that as ABSENT, not as an entity;
2. identities are preserved verbatim. `chunk_uid`, `table_uid` and
   `table_segment_uid` are copied, never recomputed and never rewritten;
3. no LLM participates. Every field here comes from a deterministic read.

[ES] Contrato de evidencia: que tiene que estar sobre la mesa antes de
permitir una respuesta.

El contrato es una REPRESENTACION, no un enriquecimiento. Lee lo que el
extractor y el chunk ya produjeron, marca explicitamente lo ausente, y no
inventa nada. Tres reglas gobiernan cada campo:

1. un centinela no es un valor. `entidad == fuente` significa que el extractor
   cayo al nombre de archivo; el contrato lo registra como AUSENTE, no como
   entidad;
2. las identidades se preservan tal cual. `chunk_uid`, `table_uid` y
   `table_segment_uid` se copian, nunca se recalculan ni se reescriben;
3. no interviene ningun LLM. Todo campo sale de una lectura deterministica.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Optional


# Version of the contract. It travels with every verdict so a number can always
# be traced back to the rules that produced it.
# [ES] Version del contrato. Viaja con cada veredicto para que un numero
# siempre se pueda rastrear hasta las reglas que lo produjeron.
CONTRATO_VERSION = "evidencia-v0.1"


MODALIDAD_TEXTO = "texto"
MODALIDAD_TABLA = "tabla"


# Text that is present but means "could not be determined". Counting it as
# populated would inflate completeness over fields that are empty of content.
# Same list as reports/completitud_hechos.md, section 0.
# [ES] Texto presente que significa "no se pudo determinar". Contarlo como
# poblado inflaria la completitud sobre campos vacios de contenido. Misma lista
# que reports/completitud_hechos.md, seccion 0.
NULOS_TEXTUALES = frozenset(
    {"-", "--", "desconocido", "n/a", "na", "no disponible", "none", "null", "s/d", "sd"}
)


# How the entity got there. `ausente` is a first-class outcome, not a failure to
# report: the plan allows enriching it later from curated metadata, and that
# enrichment must stay distinguishable from something the document declared.
# [ES] Como llego la entidad. `ausente` es un resultado de primera clase, no una
# falla de reporte: el plan permite enriquecerla despues desde metadatos
# curados, y ese enriquecimiento tiene que seguir siendo distinguible de algo
# que el documento haya declarado.
ENTIDAD_AUSENTE = "ausente"
ENTIDAD_DECLARADA = "declarada_en_documento"
ENTIDAD_CURADA = "metadato_curado"


def texto_util(valor: Any) -> Optional[str]:
    """Return the text only if it carries content; otherwise None.

    Strings of dots are the table-of-contents leader Docling leaves behind
    ("Informacion Legal ......"): present, and empty of meaning.

    [ES] Devuelve el texto solo si lleva contenido; si no, None.

    Las cadenas de puntos son el relleno de indice que deja Docling
    ("Informacion Legal ......"): presente, y vacio de significado.
    """
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    if texto.lower() in NULOS_TEXTUALES:
        return None
    if not texto.strip(". "):
        return None
    return texto


@dataclass(frozen=True)
class Localizacion:
    """Where a human can reopen the evidence, in the source document.

    Every field is optional because documents differ: a PDF has pages and a
    bbox, a spreadsheet has a sheet and a coordinate, a text chunk has an
    offset. What a representation does not have stays None instead of being
    filled with a plausible substitute.

    [ES] Donde un humano puede reabrir la evidencia, en el documento fuente.

    Todo campo es opcional porque los documentos difieren: un PDF tiene paginas
    y bbox, una planilla tiene hoja y coordenada, un chunk de texto tiene
    offset. Lo que una representacion no tiene queda en None en lugar de
    rellenarse con un sustituto verosimil.
    """

    paginas: tuple[int, ...] = ()
    hoja: Optional[str] = None
    fila: Optional[int] = None
    columna: Optional[int] = None
    coordenada: Optional[str] = None
    bbox: Optional[Mapping[str, Any]] = None
    offset_desde: Optional[int] = None
    offset_hasta: Optional[int] = None

    def localizable(self) -> bool:
        """Whether a reader could physically go and check this.

        Page 0 is a sentinel: Docling numbers from 1. Row and column 0 are NOT
        absent: the grid is 0-indexed and (0,0) is a real cell.

        [ES] Si un lector podria ir fisicamente a comprobarlo.

        La pagina 0 es un centinela: Docling numera desde 1. La fila y la
        columna 0 NO estan ausentes: la grilla es 0-indexada y (0,0) es una
        celda real.
        """
        if any(p for p in self.paginas):
            return True
        if self.hoja is not None:
            return True
        return self.offset_desde is not None

    def celda_localizada(self) -> bool:
        """Cell-level provenance: the location plus the exact coordinates.

        [ES] Procedencia a nivel de celda: la ubicacion mas las coordenadas
        exactas.
        """
        return self.localizable() and self.fila is not None and self.columna is not None


@dataclass(frozen=True)
class Evidencia:
    """One piece of evidence, in whichever representation produced it.

    The shared head (document, artifact, location) is what makes text and table
    comparable. The semantic components below only apply to a fact; for text
    they stay None and the verifier is told so by `modalidad`.

    [ES] Una pieza de evidencia, en la representacion que la haya producido.

    La cabecera comun (documento, artefacto, ubicacion) es lo que vuelve
    comparables texto y tabla. Los componentes semanticos de abajo solo aplican
    a un hecho; para texto quedan en None y el verificador se entera por
    `modalidad`.
    """

    modalidad: str

    document_id: Optional[str]
    artifact_id: Optional[str]
    fuente: Optional[str]
    localizacion: Localizacion

    # --- text identity / identidad de texto ---
    chunk_uid: Optional[str] = None
    texto: Optional[str] = None

    # --- table identity / identidad de tabla ---
    table_uid: Optional[str] = None
    table_segment_uid: Optional[str] = None
    continuation_of: Optional[str] = None
    ancla: Optional[str] = None

    # --- semantic components of the fact / componentes semanticos del hecho ---
    entidad: Optional[str] = None
    entidad_origen: str = ENTIDAD_AUSENTE
    concepto: Optional[str] = None
    periodo: Optional[str] = None
    escala: Optional[str] = None
    moneda: Optional[str] = None
    es_porcentaje: bool = False
    valor: Optional[float] = None
    valor_crudo: Optional[str] = None

    # --- what makes two figures comparable / lo que vuelve comparables dos cifras ---
    # `alcance` is NOT extracted today: the table-aware prototype has no such
    # field, so it stays None for every fact read from `hechos.jsonl`. That is
    # reported as OUT OF SCOPE of extraction, not as a missing datum - and it is
    # exactly why two figures cannot be declared in conflict yet: nothing says
    # whether one is consolidated and the other individual.
    # [ES] `alcance` NO se extrae hoy: el prototipo table-aware no tiene ese
    # campo, asi que queda en None para todo hecho leido de `hechos.jsonl`. Eso
    # se reporta como FUERA DEL ALCANCE de extraccion, no como dato faltante - y
    # es justamente por lo que todavia no se pueden declarar en conflicto dos
    # cifras: nada dice si una es consolidada y la otra individual.
    alcance: Optional[str] = None        # 'consolidado' | 'individual' | None
    base_contable: Optional[str] = None  # 'moneda_constante' | 'nominal' | ...
    escenario: Optional[str] = None      # 'real' | 'proyectado' | 'reexpresado' | None

    # NOTE: there is deliberately NO external support-link field here.
    #
    # One existed: a `soporte_declarado` string naming the claim a piece
    # supported, which by itself granted `sostiene`. It let a complete row
    # reading "Costos de explotacion" answer a question about sales, because a
    # field said so. The field had no producer, no method, no version and no
    # verifiable provenance - an unaudited bypass shaped like an audit trail.
    # A dormant field is not safer than a live one: it invites being wired back.
    #
    # PENDING WORK, not implemented here. A real external support link would
    # need, at minimum: `item_id`, producer, method, version and traceable
    # provenance, plus an aligner frozen and evaluated independently. It could
    # never be derived from the evaluation Gold, which would be the same leak
    # this layer already removed once.
    #
    # [ES] OJO: a proposito NO hay campo de vinculo de soporte externo.
    #
    # Existio uno: un string `soporte_declarado` que nombraba la afirmacion que
    # una pieza sostenia, y que por si solo otorgaba `sostiene`. Permitia que una
    # fila completa que decia "Costos de explotacion" respondiera una pregunta
    # sobre ventas, porque un campo lo afirmaba. El campo no tenia productor, ni
    # metodo, ni version, ni procedencia verificable: una valvula sin auditar con
    # forma de pista de auditoria. Un campo dormido no es mas seguro que uno
    # vivo: invita a volver a conectarlo.
    #
    # TRABAJO PENDIENTE, no implementado aca. Un vinculo externo de soporte real
    # necesitaria, como minimo: `item_id`, productor, metodo, version y
    # procedencia trazable, mas un alineador congelado y evaluado de forma
    # independiente. Nunca podria derivarse del Gold de evaluacion, que seria la
    # misma fuga que esta capa ya elimino una vez.

    # --- what the extractor said about itself / lo que el extractor dijo de si ---
    # Confidence is COPIED, never recomputed here. It is the extractor's own
    # deterministic label, and the point of the verifier is to show that it is
    # not a completeness measure.
    # [ES] La confianza se COPIA, nunca se recalcula aca. Es la etiqueta
    # deterministica del propio extractor, y el objetivo del verificador es
    # mostrar que no es una medida de completitud.
    confianza: Optional[str] = None
    advertencias_extraccion: tuple[str, ...] = ()
    parser: Optional[str] = None
    parser_version: Optional[str] = None
    extraccion_version: Optional[str] = None
    contrato_version: str = CONTRATO_VERSION

    # Lexical context used ONLY to classify the fact type. Kept apart from the
    # measured components on purpose: see verificador.clasificar_tipo.
    # [ES] Contexto lexico usado SOLO para clasificar el tipo de hecho. Se
    # mantiene aparte de los componentes medidos a proposito: ver
    # verificador.clasificar_tipo.
    lexico: tuple[str, ...] = ()

    def con_entidad(self, nombre: str, origen: str = ENTIDAD_CURADA) -> "Evidencia":
        """Attach a curated entity, keeping the record of where it came from.

        This is the ONLY sanctioned way to fill `entidad`, and it never happens
        by itself: someone has to link the curated metadata on purpose.

        [ES] Adjunta una entidad curada, conservando el registro de su origen.

        Es la UNICA via autorizada para poblar `entidad`, y nunca ocurre sola:
        alguien tiene que vincular el metadato curado a proposito.
        """
        util = texto_util(nombre)
        if util is None:
            return self
        return replace(self, entidad=util, entidad_origen=origen)


@dataclass(frozen=True)
class Especificacion:
    """What the claim is ABOUT, structured so a rule can check alignment.

    A free-text question cannot be matched against a fact without a language
    model, and a language model inside this layer would make the system its own
    judge of whether it answered. So the claim is declared structurally, upstream
    of retrieval, by whoever wrote the question.

    Without this, "how much were sales?" was answered by a complete, correct,
    perfectly located row reading "Costos de explotacion". Every structural check
    passed; the answer was about something else.

    `conceptos` holds the accepted forms of the concept, declared explicitly
    rather than guessed. Declaring the synonyms upstream is what keeps the
    matching deterministic and auditable: a reviewer can see exactly which labels
    were accepted for this claim.

    [ES] De que trata la afirmacion, estructurado para que una regla pueda
    comprobar la alineacion.

    Una pregunta en texto libre no se puede aparear con un hecho sin un modelo de
    lenguaje, y un modelo de lenguaje dentro de esta capa volveria al sistema
    juez de si se respondio a si mismo. Por eso la afirmacion se declara
    estructuralmente, aguas arriba de la recuperacion, por quien escribio la
    pregunta.

    Sin esto, "cuanto fueron las ventas?" se respondia con una fila completa,
    correcta y perfectamente localizada que decia "Costos de explotacion". Todos
    los controles estructurales pasaban; la respuesta era sobre otra cosa.

    `conceptos` guarda las formas aceptadas del concepto, declaradas
    explicitamente en lugar de adivinadas. Declarar los sinonimos aguas arriba es
    lo que mantiene el apareo deterministico y auditable: un revisor puede ver
    exactamente que etiquetas se aceptaron para esta afirmacion.
    """

    conceptos: tuple[str, ...] = ()
    entidad: Optional[str] = None
    periodo: Optional[str] = None

    # Filled from the claim, so an upstream-produced support link can be checked
    # against the claim it declares to support.
    # [ES] Se completa desde la afirmacion, para poder contrastar un vinculo de
    # soporte producido aguas arriba contra la afirmacion que dice sostener.
    item_id: Optional[str] = None

    def declarada(self) -> bool:
        """Without an expected concept there is nothing to align against.

        [ES] Sin concepto esperado no hay contra que alinear.
        """
        return bool(self.conceptos)


@dataclass(frozen=True)
class Afirmacion:
    """One claim to be sustained: THE unit of budget, of metrics and of memory.

    Everything that used to be counted per fact is counted here instead, and the
    reason is not tidiness:

    - a retry budget spent per FACT means an item holding five facts quietly
      spends five retries. The bound has to belong to the question, not to how
      many rows happened to be retrieved;
    - an abstention indexed by `table_segment_uid` collapses every row of one
      table into a single reference, so two different claims read as one. The
      identity has to be the claim's own;
    - a human reference is given about a QUESTION ("does this evidence sustain
      the answer?"), never about a cell.

    `componentes_requeridos` is what the QUESTION demands on top of what the
    fact type demands. A question about a period requires a period even if the
    type would not.

    [ES] Una afirmacion a sostener: LA unidad de presupuesto, de metricas y de
    registro.

    Todo lo que antes se contaba por hecho se cuenta aca, y el motivo no es
    prolijidad:

    - un presupuesto de reintento gastado por HECHO significa que un item con
      cinco hechos gasta en silencio cinco reintentos. La cota tiene que
      pertenecer a la pregunta, no a cuantas filas se hayan recuperado;
    - una abstencion indexada por `table_segment_uid` colapsa todas las filas de
      una tabla en una sola referencia, asi que dos afirmaciones distintas se
      leen como una. La identidad tiene que ser la de la afirmacion;
    - una referencia humana se da sobre una PREGUNTA ("esta evidencia sostiene
      la respuesta?"), nunca sobre una celda.

    `componentes_requeridos` es lo que exige la PREGUNTA por encima de lo que
    exige el tipo del hecho. Una pregunta por un periodo exige periodo aunque el
    tipo no lo exigiera.
    """

    item_id: str
    evidencias: tuple[Evidencia, ...]

    # Free text, for a human to read. It is NOT used by any decision, and it
    # must never be: matching prose against a fact needs a language model, and a
    # model inside this layer would judge whether the system answered itself.
    # What the decisions use is `especificacion`.
    # [ES] Texto libre, para que lo lea un humano. NO lo usa ninguna decision, y
    # no debe usarlo nunca: aparear prosa contra un hecho exige un modelo de
    # lenguaje, y un modelo dentro de esta capa juzgaria si el sistema se
    # respondio a si mismo. Lo que usan las decisiones es `especificacion`.
    pregunta: Optional[str] = None

    especificacion: Optional[Especificacion] = None
    componentes_requeridos: tuple[str, ...] = ()

    # NOTE: there is deliberately NO human reference field here.
    #
    # It used to exist, and it leaked: the Gold label reached `determinar_soporte`
    # and flipped the decision from `indeterminado` to `responder`. The system
    # was reading the answer key and then being scored against it. A reference
    # that can change the prediction cannot evaluate the prediction.
    #
    # The reference now lives only in `metricas.resumir(referencia=...)`, applied
    # AFTER the prediction exists. Keeping it out of this dataclass is what makes
    # the leak structurally impossible rather than merely discouraged.
    #
    # [ES] OJO: a proposito NO hay campo de referencia humana aca.
    #
    # Existia, y se filtraba: la etiqueta del Golden llegaba a
    # `determinar_soporte` y cambiaba la decision de `indeterminado` a
    # `responder`. El sistema leia la hoja de respuestas y despues se puntuaba
    # contra ella. Una referencia que puede cambiar la prediccion no puede
    # evaluar la prediccion.
    #
    # La referencia vive ahora solo en `metricas.resumir(referencia=...)`,
    # aplicada DESPUES de que la prediccion existe. Dejarla fuera de esta
    # dataclass es lo que vuelve la fuga estructuralmente imposible en lugar de
    # simplemente desaconsejada.

    @classmethod
    def de_evidencias(cls, item_id: str, evidencias, **extra) -> "Afirmacion":
        return cls(item_id=item_id, evidencias=tuple(evidencias), **extra)

    def especificacion_efectiva(self) -> Optional[Especificacion]:
        """The specification carrying this claim's own id, or None if undeclared.

        [ES] La especificacion con el id de esta afirmacion, o None si no se
        declaro.
        """
        if self.especificacion is None:
            return None
        return replace(self.especificacion, item_id=self.item_id)

    def documento_principal(self) -> Optional[str]:
        """The document to group by, or None when the claim spans several.

        Grouping a cross-document claim under one of its documents would
        misattribute it, so it groups under None and the summary says so.

        [ES] El documento por el que agrupar, o None si la afirmacion cruza
        varios. Agrupar una afirmacion multidocumento bajo uno de sus documentos
        la atribuiria mal, asi que agrupa bajo None y el resumen lo dice.
        """
        documentos = {e.document_id for e in self.evidencias if e.document_id}
        return documentos.pop() if len(documentos) == 1 else None


def evidencia_de_hecho_tabular(hecho: Mapping[str, Any]) -> Evidencia:
    """Build the contract from one fact of the isolated table-aware extractor.

    Accepts the serialized `hechos.jsonl` record. It reads, it does not rewrite:
    the file is never touched and no uid is recomputed.

    [ES] Construye el contrato desde un hecho del extractor table-aware aislado.

    Acepta el registro serializado de `hechos.jsonl`. Lee, no reescribe: el
    archivo nunca se toca y ningun uid se recalcula.
    """
    fuente = hecho.get("fuente")
    entidad_cruda = texto_util(hecho.get("entidad"))

    # The extractor falls back to the file name when the document declares no
    # entity. A file name is not an entity.
    # [ES] El extractor cae al nombre de archivo cuando el documento no declara
    # entidad. Un nombre de archivo no es una entidad.
    if entidad_cruda is not None and fuente is not None:
        if entidad_cruda == str(fuente).strip():
            entidad_cruda = None

    unidad = hecho.get("unit") or {}
    periodo_dict = hecho.get("period") or {}
    coords = hecho.get("cell_coordinates") or {}

    # The period counts as present only if it says something. A Periodo whose
    # fields are all null is an empty shell.
    # [ES] El periodo cuenta como presente solo si dice algo. Un Periodo con
    # todos los campos nulos es una cascara vacia.
    periodo = None
    campos_periodo = ("crudo", "anio", "mes", "fecha_fin", "granularidad")
    if any(periodo_dict.get(k) for k in campos_periodo):
        periodo = texto_util(periodo_dict.get("crudo"))
        if periodo is None:
            alterno = periodo_dict.get("fecha_fin") or periodo_dict.get("anio")
            periodo = str(alterno) if alterno else None

    localizacion = Localizacion(
        paginas=tuple(int(p) for p in (hecho.get("source_pages") or ())),
        hoja=hecho.get("hoja"),
        fila=coords.get("fila"),
        columna=coords.get("col"),
        coordenada=coords.get("coordenada"),
        bbox=coords.get("bbox"),
    )

    lexico = tuple(
        str(t)
        for t in (
            hecho.get("row_label"),
            hecho.get("row_section"),
            hecho.get("table_title"),
            *(hecho.get("column_path") or ()),
        )
        if t
    )

    return Evidencia(
        modalidad=MODALIDAD_TABLA,
        document_id=hecho.get("document_id"),
        artifact_id=hecho.get("artifact_id"),
        fuente=fuente,
        localizacion=localizacion,
        table_uid=hecho.get("table_uid"),
        table_segment_uid=hecho.get("table_segment_uid"),
        continuation_of=hecho.get("continuation_of"),
        ancla=hecho.get("ancla"),
        entidad=entidad_cruda,
        entidad_origen=ENTIDAD_DECLARADA if entidad_cruda else ENTIDAD_AUSENTE,
        concepto=texto_util(hecho.get("row_label")),
        periodo=periodo,
        escala=unidad.get("escala"),
        moneda=unidad.get("moneda"),
        es_porcentaje=bool(unidad.get("es_porcentaje")),
        valor=hecho.get("value"),
        valor_crudo=hecho.get("value_raw"),
        # `alcance` and `escenario` have no source in the extractor. They are
        # left absent on purpose instead of being guessed from the file name or
        # the table title.
        # [ES] `alcance` y `escenario` no tienen origen en el extractor. Se
        # dejan ausentes a proposito en lugar de adivinarlos del nombre de
        # archivo o del titulo de la tabla.
        alcance=hecho.get("alcance"),
        base_contable=unidad.get("base"),
        escenario=hecho.get("escenario"),
        # `soporte_declarado` is NOT read from the record. Reading a support
        # assertion blindly out of a jsonl is exactly the unaudited bypass that
        # was removed: any field in any file could have granted `sostiene`.
        # [ES] `soporte_declarado` NO se lee del registro. Leer a ciegas una
        # afirmacion de soporte de un jsonl es exactamente la valvula sin
        # auditar que se elimino: cualquier campo de cualquier archivo podria
        # haber otorgado `sostiene`.
        confianza=hecho.get("confianza"),
        advertencias_extraccion=tuple(hecho.get("extraction_warnings") or ()),
        parser=hecho.get("parser"),
        parser_version=hecho.get("parser_version"),
        extraccion_version=hecho.get("extraccion_version"),
        lexico=lexico,
    )


def evidencia_de_chunk(chunk: Mapping[str, Any]) -> Evidencia:
    """Build the contract from one retrieved text chunk.

    `chunk_uid` is copied as delivered. This function must never derive, hash or
    normalise it: the identity of the snapshot is not ours to change.

    [ES] Construye el contrato desde un chunk de texto recuperado.

    `chunk_uid` se copia tal como llega. Esta funcion nunca debe derivarlo,
    hashearlo ni normalizarlo: la identidad del snapshot no nos pertenece.
    """
    paginas = chunk.get("paginas") or ()
    if isinstance(paginas, (int, str)):
        paginas = (paginas,)
    paginas = tuple(int(p) for p in paginas if str(p).strip().lstrip("-").isdigit())

    return Evidencia(
        modalidad=MODALIDAD_TEXTO,
        document_id=chunk.get("document_id"),
        artifact_id=chunk.get("artifact_id"),
        fuente=chunk.get("fuente"),
        localizacion=Localizacion(
            paginas=paginas,
            offset_desde=chunk.get("offset_desde"),
            offset_hasta=chunk.get("offset_hasta"),
        ),
        chunk_uid=chunk.get("chunk_uid"),
        texto=chunk.get("contenido"),
        concepto=texto_util(chunk.get("titulo")),
    )
