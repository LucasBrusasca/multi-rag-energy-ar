"""The deterministic core: read the grid, infer the header, build column_path.

No model and no LLM take part here. Everything is decided by the shape of the
cell contents, because that is reconstructible and auditable. The parser's own
header flags are read but never trusted: they were wrong in 10 of the 15 tables
audited (`experimentos/auditoria_tablas/DIAGNOSTICO.md`, section 2.2).

[ES] El nucleo deterministico: leer la grilla, inferir el encabezado, construir
el column_path.

Aca no interviene ningun modelo ni ningun LLM. Todo se decide por la forma del
contenido de las celdas, porque eso es reconstruible y auditable. Las marcas de
encabezado del parser se leen pero nunca se creen: se equivocaron en 10 de las
15 tablas auditadas (`experimentos/auditoria_tablas/DIAGNOSTICO.md`, seccion 2.2).
"""

from __future__ import annotations

import re
from typing import Optional

from multirag.ingestion.tablas.modelo import Celda, SegmentoTabla


# A header band deeper than this is not a header: it is a table whose first
# rows happen to be textual. Bounding it keeps a pathological table from
# swallowing its own data.
# [ES] Una banda de encabezado mas profunda que esto no es un encabezado: es
# una tabla cuyas primeras filas resultan ser textuales. Acotarla evita que una
# tabla patologica se coma sus propios datos.
MAX_FILAS_ENCABEZADO = 6


VACIO, NUMERO, ANIO, PERIODO, TEXTO = "VACIO", "NUMERO", "ANIO", "PERIODO", "TEXTO"


# es-AR thousands separator is '.', decimal separator is ','. Parentheses mean
# a negative amount, as in every financial statement in the corpus.
# [ES] En es-AR el separador de miles es '.' y el decimal es ','. El parentesis
# significa importe negativo, como en todos los estados contables del corpus.
_RE_MILES = re.compile(r"^-?\d{1,3}(\.\d{3})+(,\d+)?$")
_RE_DECIMAL_COMA = re.compile(r"^-?\d+,\d+$")
_RE_ENTERO = re.compile(r"^-?\d+$")
_RE_DECIMAL_PUNTO = re.compile(r"^-?\d+\.\d+$")
_RE_PORCENTAJE = re.compile(r"^-?[\d.,]+\s*%$")
# Both separators present: whichever comes last is the decimal one. That is
# decidable from the string, unlike a lone group of three digits.
# [ES] Los dos separadores presentes: el que va ultimo es el decimal. Eso se
# decide desde la cadena, a diferencia de un unico grupo de tres digitos.
_RE_MIXTO_ES_AR = re.compile(r"^-?\d{1,3}(\.\d{3})+,\d+$")
_RE_MIXTO_EN_US = re.compile(r"^-?\d{1,3}(,\d{3})+\.\d+$")
# A single group of three digits reads as thousands under es-AR and as a
# decimal under en-US. The corpus convention is es-AR, and the assumption is
# declared alongside the value instead of being made silently.
# [ES] Un unico grupo de tres digitos se lee como miles en es-AR y como decimal
# en en-US. La convencion del corpus es es-AR, y el supuesto se declara junto al
# valor en vez de asumirse en silencio.
_RE_UN_SOLO_GRUPO = re.compile(r"^-?\d{1,3}\.\d{3}$")

# Two amounts glued into one cell: two columns collapsed into one by the
# parser. It is not a number and must not be read as one.
# [ES] Dos importes pegados en una celda: dos columnas colapsadas en una por el
# parser. No es un numero y no se puede leer como tal.
_RE_VALORES_PEGADOS = re.compile(r"^\(?-?[\d.,]+\)?(\s+\(?-?[\d.,]+\)?)+$")

_RE_FECHA = re.compile(r"^\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}$")
_RE_MES_ANIO = re.compile(
    r"^(ene|feb|mar|abr|may|jun|jul|ago|sep|sept|oct|nov|dic)[a-z]*[\-/ ]?(\d{2,4})$",
    re.IGNORECASE,
)
_RE_DURACION = re.compile(r"^\d{1,2}\s*meses$", re.IGNORECASE)
_RE_PERIODO_PALABRA = re.compile(
    r"trimestre|quarter|semestre|ejercicio|per[ií]odo|a[nñ]o\s+m[oó]vil|"
    r"meses|as\s+of|al\s+\d|year",
    re.IGNORECASE,
)

MESES = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dic": 12,
}


def normalizar(texto: object) -> str:
    """[ES] Colapsa espacios y saltos: la grilla no depende del maquetado."""
    if texto is None:
        return ""
    return re.sub(r"\s+", " ", str(texto)).strip()


def clasificar(texto: object) -> str:
    """Classify a cell by SHAPE, which is what the header inference needs.

    ANIO is separated from NUMERO on purpose: a header row of financial years
    (`2024 2023 2022`) is numeric in shape and a header in meaning, and
    collapsing the two is exactly the mistake that produced
    "Flujo de Caja Operativo (FCO), (30.716) = 204.545".

    [ES] Clasifica una celda por su FORMA, que es lo que necesita la inferencia
    de encabezado.

    ANIO se separa de NUMERO a proposito: una fila de encabezado con ejercicios
    (`2024 2023 2022`) es numerica en forma y encabezado en sentido, y
    confundirlas es exactamente el error que produjo
    "Flujo de Caja Operativo (FCO), (30.716) = 204.545".
    """
    limpio = normalizar(texto)
    if not limpio:
        return VACIO

    if _RE_PORCENTAJE.match(limpio):
        return NUMERO

    desnudo = limpio.replace("(", "").replace(")", "").replace("$", "").strip()

    if _RE_ENTERO.match(desnudo) and 1900 <= abs(int(desnudo)) <= 2100:
        return ANIO
    if _RE_FECHA.match(desnudo) or _RE_MES_ANIO.match(desnudo):
        return PERIODO
    if _RE_DURACION.match(limpio):
        return PERIODO

    if _RE_VALORES_PEGADOS.match(limpio):
        return NUMERO
    if any(p.match(desnudo) for p in (_RE_MILES, _RE_DECIMAL_COMA, _RE_ENTERO, _RE_DECIMAL_PUNTO)):
        return NUMERO

    if _RE_PERIODO_PALABRA.search(limpio):
        return PERIODO
    return TEXTO


def a_numero(texto: object, valor_nativo=None) -> tuple[Optional[float], tuple[str, ...]]:
    """Parse an amount, or refuse to. Refusing is a result, not a failure.

    Returns (value, warnings). An ambiguous or collapsed cell returns None plus
    the warning that says why, because a wrong number is worse than no number.

    [ES] Interpreta un importe, o se niega. Negarse es un resultado, no una
    falla.

    Devuelve (valor, avisos). Una celda ambigua o colapsada devuelve None mas el
    aviso que dice por que, porque un numero equivocado es peor que ningun
    numero.
    """
    if isinstance(valor_nativo, bool):
        return None, ("valor_booleano",)
    if isinstance(valor_nativo, (int, float)):
        return float(valor_nativo), ()

    limpio = normalizar(texto)
    if not limpio:
        return None, ()

    if _RE_VALORES_PEGADOS.match(limpio) and " " in limpio:
        return None, ("celdas_colapsadas",)

    negativo = limpio.startswith("(") and limpio.endswith(")")
    desnudo = limpio.strip("()").replace("$", "").replace("%", "").strip()
    if desnudo.startswith("-"):
        negativo, desnudo = True, desnudo[1:]

    avisos: tuple[str, ...] = ()

    if _RE_MIXTO_EN_US.match(desnudo):
        valor = float(desnudo.replace(",", ""))
    elif _RE_MIXTO_ES_AR.match(desnudo) or _RE_MILES.match(desnudo):
        if _RE_UN_SOLO_GRUPO.match(desnudo):
            avisos = ("separador_de_miles_asumido_es_ar",)
        valor = float(desnudo.replace(".", "").replace(",", "."))
    elif _RE_DECIMAL_COMA.match(desnudo):
        valor = float(desnudo.replace(",", "."))
    elif _RE_ENTERO.match(desnudo):
        valor = float(desnudo)
    elif _RE_DECIMAL_PUNTO.match(desnudo):
        valor = float(desnudo)
    else:
        return None, ("valor_no_numerico",)

    return (-valor if negativo else valor), avisos


def expandir(segmento: SegmentoTabla) -> dict[tuple[int, int], Celda]:
    """Project spans onto every position they cover.

    A cell merged across three columns must answer for the three, otherwise a
    header that spans a group is lost for two of its columns.

    [ES] Proyecta los spans sobre todas las posiciones que cubren.

    Una celda combinada sobre tres columnas tiene que responder por las tres; si
    no, un encabezado que abarca un grupo se pierde para dos de sus columnas.
    """
    grilla: dict[tuple[int, int], Celda] = {}
    for celda in segmento.celdas:
        for f in range(celda.fila, celda.fila + max(1, celda.fila_span)):
            for c in range(celda.col, celda.col + max(1, celda.col_span)):
                grilla.setdefault((f, c), celda)
    return grilla


def inferir_columna_etiqueta(
    grilla: dict[tuple[int, int], Celda], num_rows: int, num_cols: int
) -> int:
    """The column holding the concepts, which is the row label.

    It is the leftmost column with at least one text cell and no amounts.
    Falling back to 0 is honest: it is what every audited table used.

    [ES] La columna que lleva los conceptos, que es la etiqueta de la fila.

    Es la columna mas a la izquierda con al menos una celda de texto y sin
    importes. Caer en 0 es honesto: es la que usaron todas las tablas auditadas.
    """
    for c in range(num_cols):
        clases = [clasificar(grilla[(f, c)].texto) for f in range(num_rows) if (f, c) in grilla]
        if not clases:
            continue
        if any(k == TEXTO for k in clases) and not any(k == NUMERO for k in clases):
            return c
    return 0


def _clases_de_fila(
    grilla: dict[tuple[int, int], Celda], fila: int, num_cols: int, columna_etiqueta: int
) -> list[str]:
    return [
        clasificar(grilla[(fila, c)].texto)
        for c in range(num_cols)
        if c != columna_etiqueta and (fila, c) in grilla
    ]


def _fila_es_encabezado(clases: list[str]) -> bool:
    """A header row states WHAT the columns are; it never states an amount.

    A row of bare years counts as a header: its numerics are all years.

    [ES] Una fila de encabezado dice QUE son las columnas; nunca dice un
    importe. Una fila de anios sueltos cuenta como encabezado: todos sus
    numericos son anios.
    """
    utiles = [k for k in clases if k != VACIO]
    if not utiles:
        return False
    return NUMERO not in utiles


def inferir_banda_encabezado(
    grilla: dict[tuple[int, int], Celda],
    num_rows: int,
    num_cols: int,
    columna_etiqueta: int,
) -> tuple[int, ...]:
    """The header band is the leading PREFIX of header rows. It can be empty.

    Empty is the important case: it is what a table continued from the previous
    page looks like, and it is what stops a data row from being read as a
    header.

    [ES] La banda de encabezado es el PREFIJO inicial de filas de encabezado.
    Puede ser vacia.

    Vacia es el caso importante: es lo que parece una tabla continuada de la
    pagina anterior, y es lo que evita que una fila de datos se lea como
    encabezado.
    """
    banda: list[int] = []
    for fila in range(min(num_rows, MAX_FILAS_ENCABEZADO)):
        clases = _clases_de_fila(grilla, fila, num_cols, columna_etiqueta)
        utiles = [k for k in clases if k != VACIO]
        if not utiles:
            # A row with only a label is a section title, not a header: it
            # closes the band instead of extending it.
            # [ES] Una fila con solo etiqueta es un titulo de seccion, no un
            # encabezado: cierra la banda en vez de extenderla.
            break
        if not _fila_es_encabezado(clases):
            break
        banda.append(fila)
    return tuple(banda)


def es_fila_seccion(
    grilla: dict[tuple[int, int], Celda], fila: int, num_cols: int, columna_etiqueta: int
) -> bool:
    """A row with a label and no values: 'Rentabilidad', 'ASSETS'.

    [ES] Una fila con etiqueta y sin valores: 'Rentabilidad', 'ASSETS'.
    """
    if (fila, columna_etiqueta) not in grilla:
        return False
    if not normalizar(grilla[(fila, columna_etiqueta)].texto):
        return False
    clases = _clases_de_fila(grilla, fila, num_cols, columna_etiqueta)
    return all(k == VACIO for k in clases)


def columnas_de_valor(
    grilla: dict[tuple[int, int], Celda],
    num_rows: int,
    num_cols: int,
    columna_etiqueta: int,
    banda: tuple[int, ...],
) -> tuple[int, ...]:
    """Columns that actually carry data. Empty visual separators are dropped.

    This is what makes the audited spreadsheet readable: 9 of its 12 columns
    are blank separators (`DIAGNOSTICO.md`, section 2.4).

    [ES] Columnas que efectivamente llevan datos. Los separadores visuales
    vacios se descartan.

    Esto es lo que vuelve legible la planilla auditada: 9 de sus 12 columnas son
    separadores en blanco (`DIAGNOSTICO.md`, seccion 2.4).
    """
    utiles = []
    for c in range(num_cols):
        if c == columna_etiqueta:
            continue
        tiene_dato = any(
            (f, c) in grilla and clasificar(grilla[(f, c)].texto) != VACIO
            for f in range(num_rows)
            if f not in banda
        )
        tiene_encabezado = any(
            (f, c) in grilla and clasificar(grilla[(f, c)].texto) != VACIO for f in banda
        )
        if tiene_dato or tiene_encabezado:
            utiles.append(c)
    return tuple(utiles)


def column_path(
    grilla: dict[tuple[int, int], Celda], banda: tuple[int, ...], col: int
) -> tuple[str, ...]:
    """The hierarchical header of one column, outermost level first.

    Consecutive repetitions are collapsed, which is what a merged cell spanning
    several rows produces. Nothing is added that is not in a cell.

    [ES] El encabezado jerarquico de una columna, del nivel mas externo al mas
    interno. Se colapsan las repeticiones consecutivas, que es lo que produce
    una celda combinada sobre varias filas. No se agrega nada que no este en
    una celda.
    """
    camino: list[str] = []
    for fila in banda:
        if (fila, col) not in grilla:
            continue
        texto = normalizar(grilla[(fila, col)].texto)
        if not texto:
            continue
        if camino and camino[-1] == texto:
            continue
        camino.append(texto)
    return tuple(camino)


def contrastar_con_parser(
    segmento: SegmentoTabla, grilla: dict[tuple[int, int], Celda]
) -> None:
    """Record where our inference and the parser disagree. Do not overwrite it.

    Being able to count this disagreement is a finding of the thesis, so it is
    stored, not resolved.

    [ES] Registra donde discrepan nuestra inferencia y el parser. No la pisa.

    Poder contar esa discrepancia es un hallazgo de la tesis, asi que se guarda,
    no se resuelve.
    """
    if not segmento.parser_marca_encabezados:
        return

    del_parser = {
        celda.fila
        for celda in segmento.celdas
        if celda.es_encabezado_col_parser and normalizar(celda.texto)
    }
    nuestra = set(segmento.banda_encabezado)
    if del_parser == nuestra:
        return
    # Prefixed `nota:` because it does not limit the datum: it measures how
    # often the parser disagrees with us, which is a finding, not a defect of
    # the fact. The summary counts limiting warnings separately.
    # [ES] Prefijado `nota:` porque no limita el dato: mide cada cuanto el
    # parser discrepa con nosotros, que es un hallazgo, no un defecto del hecho.
    # El resumen cuenta aparte las advertencias que si limitan.
    segmento.avisar(
        "nota:encabezado_discrepa_con_parser:"
        f"parser={sorted(del_parser)},inferido={sorted(nuestra)}"
    )
