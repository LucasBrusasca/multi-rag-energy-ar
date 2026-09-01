"""Linking a table split across pages, conservatively and reversibly.

The rule is deliberately hard to satisfy. A wrong link attributes figures to
the wrong concepts, which is worse than the orphan continuation it was meant to
repair. So EVERY condition must hold, each one is recorded, and the first that
fails is recorded too, with its reason.

What linking does NOT do:

- it does not merge the segments: each keeps its `table_segment_uid`, its own
  pages and its own cells;
- it does not rewrite any cell;
- it is undone by clearing `continuation_of`, with nothing else to revert.

[ES] Vinculo de una tabla partida entre paginas, conservador y reversible.

La regla es deliberadamente dificil de satisfacer. Un vinculo equivocado
atribuye cifras a conceptos que no son, que es peor que la continuacion huerfana
que venia a reparar. Por eso tienen que cumplirse TODAS las condiciones, cada
una queda registrada, y la primera que falla queda registrada tambien, con su
motivo.

Lo que el vinculo NO hace:

- no fusiona los segmentos: cada uno conserva su `table_segment_uid`, sus
  paginas y sus celdas;
- no reescribe ninguna celda;
- se deshace borrando `continuation_of`, sin nada mas que revertir.
"""

from __future__ import annotations

from typing import Optional

from multirag.ingestion.tablas.grilla import (
    NUMERO,
    VACIO,
    clasificar,
    expandir,
)
from multirag.ingestion.tablas.modelo import SegmentoTabla


# A continuation must be mostly amounts. Below this it is another table that
# happens to lack a header.
# [ES] Una continuacion tiene que ser mayormente importes. Por debajo de esto es
# otra tabla que casualmente no tiene encabezado.
PROPORCION_MINIMA_NUMERICA = 0.6


def _proporcion_numerica(segmento: SegmentoTabla) -> float:
    grilla = expandir(segmento)
    clases = [
        clasificar(grilla[(f, c)].texto)
        for f in range(segmento.num_rows)
        for c in range(segmento.num_cols)
        if c != segmento.columna_etiqueta and (f, c) in grilla
    ]
    utiles = [k for k in clases if k != VACIO]
    if not utiles:
        return 0.0
    return sum(1 for k in utiles if k == NUMERO) / len(utiles)


def evaluar_continuidad(
    anterior: SegmentoTabla, actual: SegmentoTabla
) -> tuple[bool, list[str], Optional[str]]:
    """Decide whether `actual` continues `anterior`. Returns (yes, rules, reason).

    [ES] Decide si `actual` continua a `anterior`. Devuelve (si, reglas, motivo).
    """
    reglas: list[str] = []

    if anterior.artifact_id != actual.artifact_id:
        return False, reglas, "otro_artefacto"
    reglas.append("mismo_artefacto")

    if not anterior.source_pages or not actual.source_pages:
        return False, reglas, "sin_pagina_declarada"

    pagina_anterior = max(anterior.source_pages)
    pagina_actual = min(actual.source_pages)
    if pagina_actual != pagina_anterior + 1:
        return False, reglas, f"paginas_no_consecutivas:{pagina_anterior}->{pagina_actual}"
    reglas.append("paginas_consecutivas")

    if anterior.num_cols != actual.num_cols:
        return False, reglas, f"ancho_distinto:{anterior.num_cols}!={actual.num_cols}"
    reglas.append("mismo_ancho")

    if not anterior.banda_encabezado:
        return False, reglas, "el_anterior_tampoco_tiene_encabezado"
    reglas.append("el_anterior_tiene_encabezado")

    if actual.banda_encabezado:
        return False, reglas, f"tiene_encabezado_propio:{list(actual.banda_encabezado)}"
    reglas.append("sin_encabezado_propio")

    proporcion = _proporcion_numerica(actual)
    if proporcion < PROPORCION_MINIMA_NUMERICA:
        return False, reglas, f"poco_numerica:{proporcion:.2f}"
    reglas.append(f"mayormente_numerica:{proporcion:.2f}")

    if anterior.columna_etiqueta != actual.columna_etiqueta:
        return False, reglas, "columna_de_etiqueta_distinta"
    reglas.append("misma_columna_de_etiqueta")

    return True, reglas, None


def enlazar_continuaciones(segmentos: list[SegmentoTabla]) -> None:
    """Link, in reading order, every segment that continues the previous one.

    Only IMMEDIATELY consecutive segments are compared: if another table sits in
    between, the reading order says they are not the same table.

    A chain is allowed (A <- B <- C) because a table can span three pages, and
    all of them share the `table_uid` of the head.

    [ES] Vincula, en orden de lectura, cada segmento que continua al anterior.

    Solo se comparan segmentos INMEDIATAMENTE consecutivos: si hay otra tabla en
    el medio, el orden de lectura dice que no son la misma tabla.

    Se admite cadena (A <- B <- C) porque una tabla puede abarcar tres paginas, y
    todas comparten el `table_uid` de la cabecera.
    """
    for indice in range(1, len(segmentos)):
        anterior, actual = segmentos[indice - 1], segmentos[indice]
        continua, reglas, motivo = evaluar_continuidad(anterior, actual)
        for regla in reglas:
            actual.anotar(f"continuidad:{regla}")
        if continua:
            actual.continuation_of = anterior.table_segment_uid
            actual.table_uid = anterior.table_uid
            actual.anotar("continuidad:enlazada")
        else:
            actual.anotar(f"continuidad:no_enlazada:{motivo}")
            # A table with no amounts is out of scope: it is not an orphan
            # continuation, it is simply not this module's business.
            # [ES] Una tabla sin importes esta fuera de alcance: no es una
            # continuacion huerfana, sencillamente no es asunto de este modulo.
            if not actual.banda_encabezado and (
                "tabla_sin_valores_numericos" not in actual.extraction_warnings
            ):
                actual.avisar(f"continuacion_huerfana:{motivo}")


def encabezado_efectivo(
    segmento: SegmentoTabla, por_uid: dict[str, SegmentoTabla]
) -> Optional[SegmentoTabla]:
    """The segment whose header governs this one: itself, or its head.

    [ES] El segmento cuyo encabezado gobierna a este: el mismo, o su cabecera.
    """
    visto: set[str] = set()
    actual = segmento
    while not actual.banda_encabezado and actual.continuation_of:
        if actual.continuation_of in visto:
            return None
        visto.add(actual.continuation_of)
        siguiente = por_uid.get(actual.continuation_of)
        if siguiente is None:
            return None
        actual = siguiente
    return actual if actual.banda_encabezado else None
