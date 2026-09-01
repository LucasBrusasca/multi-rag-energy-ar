"""Conservative composition: assemble one fact from components spread across pieces.

A real table splits the fact. The row carries the concept and the amount; the
column header carries the period; the caption or a sibling segment carries the
scale and the currency. Refusing to compose would report as incomplete a fact
the document states perfectly well.

Composing carelessly is worse than not composing. Two rows of the same table
have the same unit and different amounts; taking the amount from one and the
scale from the other is correct, but taking the AMOUNT from the other is a
fabricated figure that looks impeccable. So three rules hold, and none of them
is negotiable:

1. ONLY MISSING COMPONENTS ARE FILLED. A component already present is never
   overwritten. A donor cannot contradict, only complete.
2. THE VALUE AND THE CONCEPT NEVER TRAVEL. They are what makes the claim THIS
   claim; importing them from another piece would not complete a fact, it would
   invent one.
3. NO MERGING BY SIMILARITY. A donor is only accepted through an EXPLICIT link
   that the documents themselves declare: the same logical table, a declared
   continuity, the same column of the same table, the same document. Textual
   resemblance, closeness in the ranking or a shared embedding are not links.

The provenance of every donor is preserved, so a composed fact can be reopened
component by component. A composed fact that cannot be traced back to each of
its sources is not evidence, it is a guess with citations.

[ES] Composicion conservadora: armar un hecho con componentes repartidos entre
piezas.

Una tabla real parte el hecho. La fila lleva el concepto y el importe; el
encabezado de columna lleva el periodo; el caption o un segmento hermano llevan
la escala y la moneda. Negarse a componer reportaria como incompleto un hecho
que el documento declara perfectamente.

Componer sin cuidado es peor que no componer. Dos filas de la misma tabla tienen
la misma unidad y distinto importe; tomar el importe de una y la escala de la
otra es correcto, pero tomar el IMPORTE de la otra es una cifra fabricada con
aspecto impecable. Por eso rigen tres reglas, y ninguna es negociable:

1. SOLO SE COMPLETAN COMPONENTES FALTANTES. Un componente ya presente nunca se
   pisa. Un donante no puede contradecir, solo completar.
2. EL VALOR Y EL CONCEPTO NUNCA VIAJAN. Son lo que vuelve a esta afirmacion ESTA
   afirmacion; importarlos de otra pieza no completaria un hecho, inventaria
   uno.
3. NO SE FUSIONA POR PARECIDO. Un donante se acepta solo por un vinculo
   EXPLICITO que los documentos mismos declaran: la misma tabla logica, una
   continuidad declarada, la misma columna de la misma tabla, el mismo
   documento. El parecido textual, la cercania en el ranking o un embedding
   compartido no son vinculos.

Se preserva la procedencia de cada donante, para que un hecho compuesto se pueda
reabrir componente por componente. Un hecho compuesto que no se puede rastrear
hasta cada una de sus fuentes no es evidencia, es una suposicion con citas.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field, replace
from typing import Optional, Sequence

from multirag.evidencia.contrato import Evidencia, MODALIDAD_TABLA
from multirag.evidencia.verificador import APORTE_AMBIGUO


# Components a donor may supply. `valor` and `concepto` are deliberately absent:
# see rule 2 above.
# [ES] Componentes que un donante puede aportar. `valor` y `concepto` estan
# deliberadamente ausentes: ver la regla 2 de arriba.
COMPONIBLES = ("entidad", "escala", "moneda", "periodo")

# Scale and currency are ONE component, not two. "miles" from one header and
# "USD" from another is a combination that never appeared together in the
# document, and the resulting amount would look entirely ordinary.
# [ES] La escala y la moneda son UN componente, no dos. "miles" de un encabezado
# y "USD" de otro es una combinacion que nunca aparecio junta en el documento, y
# el importe resultante se veria del todo normal.
COMPONENTES_DE_UNIDAD = ("escala", "moneda")

COMPONIBLES_INDEPENDIENTES = tuple(
    c for c in COMPONIBLES if c not in COMPONENTES_DE_UNIDAD
)

# Never composable, at any distance. Kept as an explicit list so that adding one
# is a visible decision and not an accident.
# [ES] Nunca componibles, a ninguna distancia. Se guarda como lista explicita
# para que agregar uno sea una decision visible y no un accidente.
NO_COMPONIBLES = ("valor", "concepto", "valor_crudo")


# --- Link names, kept for provenance / Nombres de vinculo, para procedencia ---
MISMO_DOCUMENTO = "mismo_documento"
MISMA_TABLA_LOGICA = "misma_tabla_logica"
CONTINUIDAD_DECLARADA = "continuidad_declarada"
MISMA_COLUMNA_DE_LA_MISMA_TABLA = "misma_columna_de_la_misma_tabla"


def _misma_tabla_logica(receptor: Evidencia, donante: Evidencia) -> bool:
    return (
        receptor.table_uid is not None
        and receptor.table_uid == donante.table_uid
    )


def continuidad_declarada(receptor: Evidencia, donante: Evidencia) -> bool:
    """A split table linked by the extractor, not by us guessing adjacency.

    [ES] Una tabla partida vinculada por el extractor, no por nosotros
    adivinando adyacencia.
    """
    if receptor.continuation_of and receptor.continuation_of == donante.table_segment_uid:
        return True
    if donante.continuation_of and donante.continuation_of == receptor.table_segment_uid:
        return True
    return False


def vinculo_explicito(
    receptor: Evidencia, donante: Evidencia, componente: str
) -> Optional[str]:
    """The link that authorises this donor to supply THIS component, or None.

    The requirement tightens with how local the component is:

    - `entidad` is a property of the DOCUMENT: the same document is enough;
    - `escala` and `moneda` are declared per table: the same logical table, or a
      continuity the extractor declared;
    - `periodo` is declared per COLUMN: the same column of the same table.
      Taking the period of a neighbouring column would move the figure to
      another quarter and read as impeccable.

    [ES] El vinculo que autoriza a este donante a aportar ESTE componente, o
    None.

    La exigencia se ajusta segun que tan local sea el componente:

    - `entidad` es propiedad del DOCUMENTO: alcanza el mismo documento;
    - `escala` y `moneda` se declaran por tabla: la misma tabla logica, o una
      continuidad que el extractor haya declarado;
    - `periodo` se declara por COLUMNA: la misma columna de la misma tabla.
      Tomar el periodo de una columna vecina moveria la cifra a otro trimestre y
      se leeria impecable.
    """
    if componente not in COMPONIBLES:
        return None
    if receptor is donante:
        return None
    # Composition is a structural operation over grids. A text chunk declares no
    # table identity, so nothing authorises it to donate a component.
    # [ES] La composicion es una operacion estructural sobre grillas. Un chunk
    # de texto no declara identidad de tabla, asi que nada lo autoriza a donar.
    if receptor.modalidad != MODALIDAD_TABLA or donante.modalidad != MODALIDAD_TABLA:
        return None
    if not receptor.document_id or receptor.document_id != donante.document_id:
        return None

    if componente == "entidad":
        return MISMO_DOCUMENTO

    if componente in ("escala", "moneda"):
        if _misma_tabla_logica(receptor, donante):
            return MISMA_TABLA_LOGICA
        if continuidad_declarada(receptor, donante):
            return CONTINUIDAD_DECLARADA
        return None

    if componente == "periodo":
        if not (_misma_tabla_logica(receptor, donante) or continuidad_declarada(receptor, donante)):
            return None
        columna = receptor.localizacion.columna
        if columna is None or columna != donante.localizacion.columna:
            return None
        return MISMA_COLUMNA_DE_LA_MISMA_TABLA

    return None


@dataclass(frozen=True)
class Aporte:
    """One component borrowed from one donor, with the link that allowed it.

    [ES] Un componente prestado por un donante, con el vinculo que lo permitio.
    """

    componente: str
    valor: str
    vinculo: str
    document_id: Optional[str]
    table_uid: Optional[str]
    table_segment_uid: Optional[str]
    paginas: tuple[int, ...]
    fila: Optional[int]
    columna: Optional[int]

    @classmethod
    def de(cls, componente: str, donante: Evidencia, vinculo: str) -> "Aporte":
        return cls(
            componente=componente,
            valor=str(getattr(donante, componente)),
            vinculo=vinculo,
            document_id=donante.document_id,
            table_uid=donante.table_uid,
            table_segment_uid=donante.table_segment_uid,
            paginas=donante.localizacion.paginas,
            fila=donante.localizacion.fila,
            columna=donante.localizacion.columna,
        )


@dataclass(frozen=True)
class HechoCompuesto:
    """A claim plus the borrowed components that completed it, fully traceable.

    [ES] Una afirmacion mas los componentes prestados que la completaron,
    enteramente trazable.
    """

    base: Evidencia
    efectiva: Evidencia
    aportes: tuple[Aporte, ...] = ()

    # Components that were NOT completed because linked donors disagreed. They
    # stay missing on purpose; the alternative was to let input order decide.
    # [ES] Componentes que NO se completaron porque donantes vinculados
    # discreparon. Quedan faltantes a proposito; la alternativa era dejar que
    # decidiera el orden de entrada.
    ambiguedades: tuple[str, ...] = ()

    def compuesto(self) -> bool:
        return bool(self.aportes)

    def ambiguo(self) -> bool:
        return bool(self.ambiguedades)

    def procedencia(self) -> tuple[dict, ...]:
        """Every piece that contributed, so each one can be reopened.

        [ES] Cada pieza que aporto, para poder reabrirlas una por una.
        """
        cabeza = {
            "rol": "base",
            "document_id": self.base.document_id,
            "table_uid": self.base.table_uid,
            "table_segment_uid": self.base.table_segment_uid,
            "paginas": self.base.localizacion.paginas,
            "fila": self.base.localizacion.fila,
            "columna": self.base.localizacion.columna,
        }
        prestados = tuple(
            {
                "rol": f"aporta:{a.componente}",
                "vinculo": a.vinculo,
                "document_id": a.document_id,
                "table_uid": a.table_uid,
                "table_segment_uid": a.table_segment_uid,
                "paginas": a.paginas,
                "fila": a.fila,
                "columna": a.columna,
            }
            for a in self.aportes
        )
        return (cabeza,) + prestados


def _normalizar(valor) -> str:
    """Compare donated values without case or accents deciding the outcome.

    [ES] Comparar valores donados sin que mayusculas ni acentos decidan el
    resultado.
    """
    descompuesto = unicodedata.normalize("NFKD", str(valor))
    return "".join(c for c in descompuesto if not unicodedata.combining(c)).strip().lower()


def _unidad_compatible(receptor: Evidencia, donante: Evidencia) -> bool:
    """A donor may complete the unit only if it does not contradict what is there.

    If the row already says "miles" and the donor says "millones", the donor is
    not completing anything - it is disagreeing, and its currency must not be
    borrowed either.

    [ES] Un donante puede completar la unidad solo si no contradice lo que ya
    esta. Si la fila ya dice "miles" y el donante dice "millones", el donante no
    esta completando nada: esta discrepando, y tampoco se le puede tomar la
    moneda.
    """
    for componente in COMPONENTES_DE_UNIDAD:
        propio = getattr(receptor, componente)
        ajeno = getattr(donante, componente)
        if propio is not None and ajeno is not None:
            if _normalizar(propio) != _normalizar(ajeno):
                return False
    return True


def _donantes_validos(
    receptor: Evidencia, candidatos: Sequence[Evidencia], componente: str
) -> list[tuple[Evidencia, str]]:
    """Every donor explicitly linked for this component. All of them, not the first.

    [ES] Todo donante explicitamente vinculado para este componente. Todos, no el
    primero.
    """
    validos = []
    for donante in candidatos:
        if getattr(donante, componente, None) is None:
            continue
        vinculo = vinculo_explicito(receptor, donante, componente)
        if vinculo is not None:
            validos.append((donante, vinculo))
    return validos


def componer_una(
    receptor: Evidencia, candidatos: Sequence[Evidencia]
) -> HechoCompuesto:
    """Complete one piece of evidence from the others, only through explicit links.

    THE RESULT DOES NOT DEPEND ON THE ORDER OF THE INPUT. Taking the first valid
    donor made it depend: with two incompatible headers in the same table, one
    ordering produced "miles / ARS" and the reverse produced "millones / USD" -
    the same evidence, two different amounts, and nothing in the output saying
    so. Instead every valid donor is gathered:

    - all donors agree -> compose, and record the provenance;
    - donors disagree  -> do NOT compose. The component stays missing and an
      `aporte_ambiguo` warning is raised, so the ambiguity is reported rather
      than resolved by accident.

    SCALE AND CURRENCY TRAVEL TOGETHER. They are one unit, not two fields: taking
    "miles" from one header and "USD" from another manufactures a combination
    that never appeared anywhere in the document, and it would look entirely
    ordinary. A donor also has to be compatible with what the row already
    declares, or it is disagreeing rather than completing.

    [ES] Completa una evidencia con las demas, solo por vinculos explicitos.

    EL RESULTADO NO DEPENDE DEL ORDEN DE ENTRADA. Tomar el primer donante valido
    hacia que dependiera: con dos encabezados incompatibles en la misma tabla, un
    orden producia "miles / ARS" y el inverso "millones / USD" - la misma
    evidencia, dos importes distintos, y nada en la salida que lo dijera. En
    cambio se juntan todos los donantes validos:

    - todos coinciden -> se compone, y se registra la procedencia;
    - discrepan       -> NO se compone. El componente queda faltante y se levanta
      una advertencia `aporte_ambiguo`, para que la ambiguedad se reporte en
      lugar de resolverse por accidente.

    LA ESCALA Y LA MONEDA VIAJAN JUNTAS. Son una unidad, no dos campos: tomar
    "miles" de un encabezado y "USD" de otro fabrica una combinacion que nunca
    aparecio junta en el documento, y se veria del todo normal. Ademas el donante
    tiene que ser compatible con lo que la fila ya declara, o esta discrepando en
    lugar de completar.
    """
    aportes: list[Aporte] = []
    cambios: dict = {}
    ambiguos: list[str] = []

    # --- the unit, as ONE linked component / la unidad, como UN componente ---
    faltantes_de_unidad = [
        c for c in COMPONENTES_DE_UNIDAD if getattr(receptor, c) is None
    ]
    if faltantes_de_unidad:
        # A donor qualifies if it declares ANY part of the unit. Collecting only
        # the ones that declare the scale would silently ignore a header that
        # declares just the currency - and, worse, would let a scale-only donor
        # and a currency-only donor be combined into a unit that never appeared
        # together anywhere.
        # [ES] Un donante califica si declara CUALQUIER parte de la unidad. Juntar
        # solo los que declaran la escala ignoraria en silencio un encabezado que
        # declara solo la moneda - y, peor, permitiria que un donante de solo
        # escala y uno de solo moneda se combinaran en una unidad que nunca
        # aparecio junta en ningun lado.
        candidatos_de_unidad = []
        vistos = set()
        for componente in COMPONENTES_DE_UNIDAD:
            for donante, vinculo in _donantes_validos(receptor, candidatos, componente):
                if id(donante) in vistos:
                    continue
                vistos.add(id(donante))
                candidatos_de_unidad.append((donante, vinculo))

        ofertas: dict = {}
        for donante, vinculo in candidatos_de_unidad:
            if not _unidad_compatible(receptor, donante):
                continue
            # The pair as the donor declares it. Two donors offering the same
            # pair are the same offer, however many of them there are.
            # [ES] El par tal como lo declara el donante. Dos donantes que
            # ofrecen el mismo par son la misma oferta, sean los que sean.
            clave = tuple(
                None if getattr(donante, c) is None else _normalizar(getattr(donante, c))
                for c in COMPONENTES_DE_UNIDAD
            )
            ofertas.setdefault(clave, (donante, vinculo))

        if len(ofertas) > 1:
            ambiguos.append("unidad")
        elif len(ofertas) == 1:
            donante, vinculo = next(iter(ofertas.values()))
            for componente in faltantes_de_unidad:
                aportado = getattr(donante, componente)
                if aportado is None:
                    continue
                cambios[componente] = aportado
                aportes.append(Aporte.de(componente, donante, vinculo))

    # --- the independent components / los componentes independientes ---
    for componente in COMPONIBLES_INDEPENDIENTES:
        if getattr(receptor, componente) is not None:
            continue  # regla 1: nunca se pisa lo presente
        validos = _donantes_validos(receptor, candidatos, componente)
        if not validos:
            continue
        distintos = {_normalizar(getattr(d, componente)) for d, _ in validos}
        if len(distintos) > 1:
            ambiguos.append(componente)
            continue
        donante, vinculo = validos[0]
        cambios[componente] = getattr(donante, componente)
        aportes.append(Aporte.de(componente, donante, vinculo))

    if not cambios and not ambiguos:
        return HechoCompuesto(base=receptor, efectiva=receptor, aportes=())

    advertencias = receptor.advertencias_extraccion + tuple(
        f"{APORTE_AMBIGUO}:{c}" for c in ambiguos
    )
    efectiva = replace(receptor, advertencias_extraccion=advertencias, **cambios)

    return HechoCompuesto(
        base=receptor,
        efectiva=efectiva,
        aportes=tuple(aportes),
        ambiguedades=tuple(ambiguos),
    )


def anclada(evidencia: Evidencia, ancla: Sequence[Evidencia]) -> bool:
    """May this piece be the ANSWER to the claim, or only a donor to it?

    A retry brings evidence. Some of it completes the claim; some of it is a
    perfectly valid fact about something else entirely. Without this
    distinction, a retry that fetched an unrelated complete row from another
    document would turn an abstention into an answer - a correct fact, answering
    a question nobody asked, and impossible to tell apart from a real repair.

    Anchored means: it was in the initial set, or it is explicitly linked to
    something that was, through the same logical table or a declared continuity.
    The same document is deliberately NOT enough: a document holds many
    unrelated tables.

    THIS IS CONSERVATIVE AND IT HAS A COST. A retry that legitimately finds the
    answering fact in a DIFFERENT table of the same document will not be allowed
    to answer with it, and the claim will abstain instead. That is the intended
    trade: abstaining on a real answer is visible and measurable as a false veto;
    answering with an unanchored fact is invisible.

    [ES] Puede esta pieza ser la RESPUESTA a la afirmacion, o solo donarle algo?

    Un reintento trae evidencia. Parte completa la afirmacion; parte es un hecho
    perfectamente valido sobre otra cosa. Sin esta distincion, un reintento que
    trajera una fila completa e inconexa de otro documento convertiria una
    abstencion en respuesta: un hecho correcto, respondiendo una pregunta que
    nadie hizo, e imposible de distinguir de una reparacion real.

    Anclada significa: estaba en el conjunto inicial, o esta explicitamente
    vinculada a algo que si estaba, por la misma tabla logica o una continuidad
    declarada. El mismo documento a proposito NO alcanza: un documento tiene
    muchas tablas sin relacion entre si.

    ESTO ES CONSERVADOR Y TIENE UN COSTO. Un reintento que legitimamente
    encuentre el hecho que responde en OTRA tabla del mismo documento no va a
    poder responder con el, y la afirmacion se abstendra. Ese es el intercambio
    buscado: abstenerse sobre una respuesta real es visible y medible como falso
    veto; responder con un hecho no anclado es invisible.
    """
    for pieza in ancla:
        if evidencia is pieza:
            return True
    for pieza in ancla:
        if not evidencia.document_id or evidencia.document_id != pieza.document_id:
            continue
        if evidencia.table_uid is not None and evidencia.table_uid == pieza.table_uid:
            return True
        if continuidad_declarada(evidencia, pieza):
            return True
    return False


def componer(evidencias: Sequence[Evidencia]) -> tuple[HechoCompuesto, ...]:
    """Compose every piece against every other. Order of the input is preserved.

    [ES] Compone cada pieza contra las demas. Se preserva el orden de entrada.
    """
    evidencias = tuple(evidencias)
    return tuple(componer_una(e, evidencias) for e in evidencias)
