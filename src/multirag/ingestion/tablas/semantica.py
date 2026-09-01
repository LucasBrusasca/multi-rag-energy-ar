"""Unit and period: what turns 136.110 into an interpretable figure.

Two rules govern this module.

1. Nothing is invented. Every attribute comes from a cell, a caption or an
   identified text, and the identifier of that evidence travels with it.
2. Where it was read from is part of the datum. A unit taken from the table
   header and a unit taken from a nearby paragraph are not the same claim.

[ES] Unidad y periodo: lo que convierte 136.110 en una cifra interpretable.

Este modulo se gobierna por dos reglas.

1. No se inventa nada. Cada atributo sale de una celda, de un caption o de un
   texto identificado, y el identificador de esa evidencia viaja con el.
2. De donde se leyo es parte del dato. Una unidad tomada del encabezado de la
   tabla y una tomada de un parrafo cercano no son la misma afirmacion.
"""

from __future__ import annotations

import calendar
import re
from typing import Iterable, Optional

from multirag.ingestion.tablas.grilla import MESES, normalizar
from multirag.ingestion.tablas.modelo import Periodo, Unidad


# Ordered from strongest to weakest evidence. The order is the policy.
# [ES] Ordenado de evidencia mas fuerte a mas debil. El orden es la politica.
PRIORIDAD_ORIGEN = (
    "celda_encabezado",
    "caption",
    "texto_adyacente",
    "heredada_de_continuacion",
)

_RE_MILES_DE_MILLONES = re.compile(r"miles\s+de\s+millones|billion|bn\b", re.IGNORECASE)
_RE_MILLONES = re.compile(r"millones|million|mill[oó]n|\bmm\b", re.IGNORECASE)
_RE_MILES = re.compile(r"\bmiles\b|thousand|\bmiles\s+de\b", re.IGNORECASE)

_RE_USD = re.compile(r"US\s*\$|\bUSD\b|d[oó]lar|u\$s|\bdollar", re.IGNORECASE)
_RE_ARS = re.compile(r"\bARS\b|\bpesos?\b", re.IGNORECASE)
_RE_SIMBOLO_PESOS = re.compile(r"\$")

_RE_CONSTANTE = re.compile(r"moneda\s+constante", re.IGNORECASE)
_RE_HOMOGENEA = re.compile(r"moneda\s+homog[eé]nea|homogene", re.IGNORECASE)
_RE_NOMINAL = re.compile(r"moneda\s+nominal|valores\s+nominales", re.IGNORECASE)

_RE_PORCENTAJE = re.compile(r"%|porcentaje|percent", re.IGNORECASE)

# Something must look like a unit declaration before it is read as one.
# [ES] Algo tiene que parecer una declaracion de unidad antes de leerse como tal.
_RE_HUELE_A_UNIDAD = re.compile(
    r"millones|million|mill[oó]n|miles|thousand|billion|"
    r"US\s*\$|USD|d[oó]lar|u\$s|\bARS\b|\bpesos?\b|\$|"
    r"moneda\s+(constante|homog[eé]nea|nominal)|expresad|\bin\s+US",
    re.IGNORECASE,
)


def huele_a_unidad(texto: object) -> bool:
    return bool(_RE_HUELE_A_UNIDAD.search(normalizar(texto)))


def _escala(texto: str) -> tuple[Optional[str], Optional[str]]:
    if _RE_MILES_DE_MILLONES.search(texto):
        return "miles_de_millones", "escala_miles_de_millones"
    if _RE_MILLONES.search(texto):
        return "millones", "escala_millones"
    if _RE_MILES.search(texto):
        return "miles", "escala_miles"
    return None, None


def _moneda(texto: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Returns (currency, rule, warning). A bare '$' is declared, not assumed silently.

    [ES] Devuelve (moneda, regla, aviso). Un '$' pelado se declara, no se asume
    en silencio.
    """
    if _RE_USD.search(texto):
        return "USD", "moneda_USD_explicita", None
    if _RE_ARS.search(texto):
        return "ARS", "moneda_ARS_explicita", None
    if _RE_SIMBOLO_PESOS.search(texto):
        return "ARS", "moneda_ARS_por_simbolo", "moneda_inferida_de_simbolo_pesos"
    return None, None, None


def _base(texto: str) -> tuple[Optional[str], Optional[str]]:
    if _RE_CONSTANTE.search(texto):
        return "moneda_constante", "base_moneda_constante"
    if _RE_HOMOGENEA.search(texto):
        return "moneda_homogenea", "base_moneda_homogenea"
    if _RE_NOMINAL.search(texto):
        return "nominal", "base_nominal"
    return None, None


def detectar_unidad(
    candidatos: Iterable[tuple[str, str, Optional[str]]],
) -> tuple[Unidad, list[str]]:
    """Compose the unit from candidates `(text, origin, reference)`.

    Each attribute is taken from the strongest candidate that declares it, and
    every attribute records which origin produced it. `Unidad.origen` reports
    the origin of the SCALE, because that is the one that decides how the
    number is read.

    [ES] Compone la unidad a partir de candidatos `(texto, origen, referencia)`.

    Cada atributo se toma del candidato mas fuerte que lo declara, y cada
    atributo deja registrado que origen lo produjo. `Unidad.origen` informa el
    origen de la ESCALA, porque es el que decide como se lee el numero.
    """
    ordenados = sorted(
        candidatos,
        key=lambda c: PRIORIDAD_ORIGEN.index(c[1]) if c[1] in PRIORIDAD_ORIGEN else 99,
    )

    escala = moneda = base = None
    origen_escala = None
    origen_primario = None
    evidencia_texto = evidencia_ref = None
    es_porcentaje = False
    reglas: list[str] = []
    avisos: list[str] = []

    for texto_crudo, origen, referencia in ordenados:
        texto = normalizar(texto_crudo)
        if not texto:
            continue

        if escala is None:
            valor, regla = _escala(texto)
            if valor:
                escala, origen_escala = valor, origen
                origen_primario = origen_primario or origen
                evidencia_texto, evidencia_ref = texto, referencia
                reglas.append(f"{regla}:{origen}")

        if moneda is None:
            valor, regla, aviso = _moneda(texto)
            if valor:
                moneda = valor
                origen_primario = origen_primario or origen
                reglas.append(f"{regla}:{origen}")
                if aviso:
                    avisos.append(aviso)
                if evidencia_texto is None:
                    evidencia_texto, evidencia_ref = texto, referencia

        if base is None:
            valor, regla = _base(texto)
            if valor:
                base = valor
                origen_primario = origen_primario or origen
                reglas.append(f"{regla}:{origen}")

        # A '%' inside a free paragraph is not a declaration that the table
        # is in percentages. Only a header cell or a caption can say that.
        # [ES] Un '%' dentro de un parrafo suelto no declara que la tabla este
        # en porcentaje. Solo puede decirlo una celda de encabezado o un caption.
        if (
            not es_porcentaje
            and origen in ("celda_encabezado", "caption")
            and _RE_PORCENTAJE.search(texto)
        ):
            es_porcentaje = True
            origen_primario = origen_primario or origen
            reglas.append(f"porcentaje:{origen}")

    unidad = Unidad(
        escala=escala,
        moneda=moneda,
        base=base,
        es_porcentaje=es_porcentaje,
        origen=origen_escala or origen_primario or "ausente",
        evidencia_texto=evidencia_texto,
        evidencia_ref=evidencia_ref,
        reglas=tuple(reglas),
    )
    if not unidad.declarada():
        avisos.append("unidad_ausente")
    if unidad.escala is None and unidad.moneda is not None:
        avisos.append("escala_ausente")
    return unidad, avisos


_RE_FECHA_SUELTA = re.compile(r"(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})")
_RE_MES_ANIO = re.compile(
    r"\b(ene|feb|mar|abr|may|jun|jul|ago|sep|sept|oct|nov|dic)[a-z]*[\-/ ]?(\d{2,4})\b",
    re.IGNORECASE,
)
_RE_ANIO = re.compile(r"\b(19\d{2}|20\d{2})\b")
_RE_DURACION = re.compile(r"\b(\d{1,2})\s*meses\b", re.IGNORECASE)
_RE_ANIO_MOVIL = re.compile(r"a[nñ]o\s+m[oó]vil|\bLTM\b|trailing", re.IGNORECASE)
_RE_TRIMESTRE = re.compile(
    r"first\s+quarter|primer\s+trimestre|\bQ1\b|1Q|segundo\s+trimestre|second\s+quarter|"
    r"\bQ2\b|2Q|tercer\s+trimestre|third\s+quarter|\bQ3\b|3Q|cuarto\s+trimestre|"
    r"fourth\s+quarter|\bQ4\b|4Q|trimestre|quarter",
    re.IGNORECASE,
)
_RE_SALDO = re.compile(r"\bas\s+of\b|\bal\s+\d|\bcierre\b", re.IGNORECASE)


def _fin_de_mes(anio: int, mes: int) -> str:
    return f"{anio:04d}-{mes:02d}-{calendar.monthrange(anio, mes)[1]:02d}"


def _normalizar_anio(bruto: str) -> int:
    valor = int(bruto)
    return 2000 + valor if valor < 100 else valor


def detectar_periodo(fragmentos: Iterable[str], origen: str) -> tuple[Optional[Periodo], list[str]]:
    """Compose the period from header fragments. Composes; never completes.

    An unresolvable date is left as `crudo` with a warning: a period read wrong
    attributes a figure to the wrong quarter, which is worse than admitting the
    document did not say.

    [ES] Compone el periodo a partir de fragmentos del encabezado. Compone;
    nunca completa.

    Una fecha que no se puede resolver queda como `crudo` con un aviso: un
    periodo mal leido atribuye una cifra al trimestre equivocado, que es peor
    que admitir que el documento no lo dijo.
    """
    piezas = [normalizar(f) for f in fragmentos if normalizar(f)]
    if not piezas:
        return None, []

    unido = " ".join(piezas)
    anio = mes = None
    fecha_fin = None
    granularidad = None
    reglas: list[str] = []
    avisos: list[str] = []

    m = _RE_FECHA_SUELTA.search(unido)
    if m:
        a, b, c = m.groups()
        primero, segundo = int(a), int(b)
        anio_fecha = _normalizar_anio(c)
        if primero > 12 >= segundo:
            dia, mes_fecha = primero, segundo
            reglas.append("fecha_dd_mm_aaaa")
        elif segundo > 12 >= primero:
            mes_fecha, dia = primero, segundo
            reglas.append("fecha_mm_dd_aaaa")
        else:
            dia = mes_fecha = None
            avisos.append(f"fecha_ambigua:{m.group(0)}")
        if dia and mes_fecha:
            fecha_fin = f"{anio_fecha:04d}-{mes_fecha:02d}-{dia:02d}"
            anio, mes = anio_fecha, mes_fecha

    if fecha_fin is None:
        m = _RE_MES_ANIO.search(unido)
        if m:
            clave = m.group(1).lower()
            mes = MESES.get(clave) or MESES[clave[:3]]
            anio = _normalizar_anio(m.group(2))
            fecha_fin = _fin_de_mes(anio, mes)
            reglas.append("mes_anio_a_fin_de_mes")

    if anio is None:
        m = _RE_ANIO.search(unido)
        if m:
            anio = int(m.group(1))
            reglas.append("anio_suelto")

    m = _RE_DURACION.search(unido)
    if m:
        granularidad = f"{int(m.group(1))} meses"
        reglas.append("duracion_declarada")
    elif _RE_ANIO_MOVIL.search(unido):
        granularidad = "12 meses"
        reglas.append("anio_movil_a_12_meses")
    elif _RE_TRIMESTRE.search(unido):
        granularidad = "3 meses"
        reglas.append("trimestre_a_3_meses")
    elif _RE_SALDO.search(unido):
        granularidad = "saldo"
        reglas.append("saldo_a_una_fecha")

    if anio is None and fecha_fin is None and granularidad is None:
        return None, []

    return (
        Periodo(
            crudo=" / ".join(piezas),
            anio=anio,
            mes=mes,
            fecha_fin=fecha_fin,
            granularidad=granularidad,
            origen=origen,
            reglas=tuple(reglas),
        ),
        avisos,
    )
