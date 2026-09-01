"""From grid to facts: concept + period + unit + value + provenance.

One fact per data cell. The fact is what can be quoted, and it carries
everything needed to go back to the exact cell that produced it.

[ES] De la grilla al hecho: concepto + periodo + unidad + valor + procedencia.

Un hecho por celda de dato. El hecho es lo que se puede citar, y lleva todo lo
necesario para volver a la celda exacta que lo produjo.
"""

from __future__ import annotations

from typing import Optional

from multirag.ingestion.tablas.continuidad import encabezado_efectivo
from multirag.ingestion.tablas.grilla import (
    VACIO,
    a_numero,
    clasificar,
    columnas_de_valor,
    column_path,
    es_fila_seccion,
    expandir,
    normalizar,
)
from multirag.ingestion.tablas.modelo import (
    EXTRACCION_VERSION,
    HechoTabular,
    SegmentoTabla,
    Unidad,
)
from multirag.ingestion.tablas.semantica import detectar_periodo, detectar_unidad


# Cells that could not be parsed but are still worth reporting: they were meant
# to be a number, and the loss has to be visible.
# [ES] Celdas que no se pudieron interpretar pero igual se informan: iban a ser
# un numero, y la perdida tiene que verse.
IRRECUPERABLES_QUE_IMPORTAN = frozenset({"celdas_colapsadas"})


def _confianza(
    tiene_camino: bool,
    heredado: bool,
    unidad: Unidad,
    periodo_declarado: bool,
    avisos: tuple[str, ...],
    valor: Optional[float],
) -> str:
    """Confidence is a label with a reason, not a number that looks like one.

    [ES] La confianza es una etiqueta con motivo, no un numero que aparenta
    serlo.
    """
    if valor is None or not tiene_camino:
        return "baja"
    # `nota:` entries record what the parser said; they do not limit the datum.
    # [ES] Las entradas `nota:` registran lo que dijo el parser; no limitan el
    # dato.
    if [a for a in avisos if not a.startswith("nota:")]:
        return "media"
    if not heredado and unidad.origen in ("celda_encabezado", "caption") and periodo_declarado:
        return "alta"
    return "media"


def _unidad_de_columna(
    base: Unidad, camino: tuple[str, ...]
) -> tuple[Unidad, list[str]]:
    """A column can declare its own unit ('%', 'USD') over the table's.

    [ES] Una columna puede declarar su propia unidad ('%', 'USD') por encima de
    la de la tabla.
    """
    candidatos = [(texto, "celda_encabezado", None) for texto in camino]
    propia, avisos = detectar_unidad(candidatos)
    if not propia.declarada():
        return base, []
    return (
        Unidad(
            escala=propia.escala or base.escala,
            moneda=propia.moneda or base.moneda,
            base=propia.base or base.base,
            es_porcentaje=propia.es_porcentaje or base.es_porcentaje,
            origen=propia.origen if propia.escala else base.origen,
            evidencia_texto=propia.evidencia_texto or base.evidencia_texto,
            evidencia_ref=propia.evidencia_ref or base.evidencia_ref,
            reglas=tuple(dict.fromkeys(propia.reglas + base.reglas)),
        ),
        [a for a in avisos if a != "unidad_ausente"],
    )


def hechos_de_segmento(
    segmento: SegmentoTabla, por_uid: dict[str, SegmentoTabla]
) -> list[HechoTabular]:
    """Emit the facts of one segment, using the header that governs it.

    If the segment is a continuation, the header comes from its head and the
    provenance keeps BOTH pages, because the reader needs both to verify it.

    [ES] Emite los hechos de un segmento, usando el encabezado que lo gobierna.

    Si el segmento es una continuacion, el encabezado sale de su cabecera y la
    procedencia conserva LAS DOS paginas, porque el lector necesita las dos para
    verificarlo.
    """
    # A table with no amounts produces no facts: it is served by its text
    # chunk, and emitting empty facts would only pollute retrieval.
    # [ES] Una tabla sin importes no produce hechos: la sirve su chunk de texto,
    # y emitir hechos vacios solo ensuciaria la recuperacion.
    if "tabla_sin_valores_numericos" in segmento.extraction_warnings:
        return []

    grilla = expandir(segmento)
    cabecera = encabezado_efectivo(segmento, por_uid)
    heredado = cabecera is not None and cabecera.table_segment_uid != segmento.table_segment_uid

    if cabecera is None:
        segmento.avisar("sin_encabezado_recuperable")
        banda: tuple[int, ...] = ()
        grilla_encabezado = grilla
    else:
        banda = cabecera.banda_encabezado
        grilla_encabezado = expandir(cabecera) if heredado else grilla

    unidad_base = cabecera.unidad if (heredado and cabecera) else segmento.unidad
    if heredado and cabecera and not segmento.unidad.declarada() and unidad_base.declarada():
        unidad_base = Unidad(
            escala=unidad_base.escala,
            moneda=unidad_base.moneda,
            base=unidad_base.base,
            es_porcentaje=unidad_base.es_porcentaje,
            origen="heredada_de_continuacion",
            evidencia_texto=unidad_base.evidencia_texto,
            evidencia_ref=unidad_base.evidencia_ref,
            reglas=unidad_base.reglas + ("unidad_heredada_de_cabecera",),
        )

    paginas = tuple(
        sorted(set(segmento.source_pages) | set(cabecera.source_pages if heredado and cabecera else ()))
    )

    # Warnings the link actually resolved must not travel with the fact: saying
    # "unidad_ausente" next to a stated unit would misreport the extraction.
    # They are replaced by the warning that says where it was inherited from.
    # [ES] Los avisos que el vinculo efectivamente resolvio no pueden viajar con
    # el hecho: decir "unidad_ausente" al lado de una unidad declarada informa
    # mal la extraccion. Se reemplazan por el aviso que dice de donde se heredo.
    RESUELTOS_POR_HERENCIA = ("sin_encabezado_propio", "unidad_ausente", "escala_ausente")
    avisos_segmento = tuple(segmento.extraction_warnings)
    if heredado and cabecera:
        avisos_segmento = tuple(
            a for a in avisos_segmento if a not in RESUELTOS_POR_HERENCIA
        ) + (f"encabezado_heredado_de:{cabecera.ancla}",)
        if not unidad_base.declarada():
            avisos_segmento += ("unidad_ausente",)

    columnas = columnas_de_valor(
        grilla_encabezado if heredado else grilla,
        (cabecera.num_rows if heredado and cabecera else segmento.num_rows),
        segmento.num_cols,
        segmento.columna_etiqueta,
        banda,
    )
    if heredado:
        # The continuation has no header of its own; its value columns are the
        # head's, which is precisely what the link is for. Any column that only
        # carries data in the continuation is added, so nothing is dropped.
        # [ES] La continuacion no tiene encabezado propio; sus columnas de valor
        # son las de la cabecera, que es justamente para lo que sirve el vinculo.
        # Se agrega la columna que solo trae datos en la continuacion, para no
        # perder nada.
        propias = columnas_de_valor(
            grilla, segmento.num_rows, segmento.num_cols, segmento.columna_etiqueta, ()
        )
        columnas = tuple(
            c for c in sorted(set(columnas) | set(propias)) if c < segmento.num_cols
        )

    caminos = {c: column_path(grilla_encabezado, banda, c) for c in columnas}
    periodos = {c: detectar_periodo(caminos[c], "column_path") for c in columnas}
    unidades = {c: _unidad_de_columna(unidad_base, caminos[c]) for c in columnas}

    titulo = segmento.titulo_inferido or (
        cabecera.titulo_inferido if (heredado and cabecera) else None
    )

    hechos: list[HechoTabular] = []
    seccion: Optional[str] = None
    filas_datos = [f for f in range(segmento.num_rows) if f not in (banda if not heredado else ())]

    for fila in filas_datos:
        if es_fila_seccion(grilla, fila, segmento.num_cols, segmento.columna_etiqueta):
            seccion = normalizar(grilla[(fila, segmento.columna_etiqueta)].texto)
            continue

        etiqueta_celda = grilla.get((fila, segmento.columna_etiqueta))
        row_label = normalizar(etiqueta_celda.texto) if etiqueta_celda else ""

        for col in columnas:
            celda = grilla.get((fila, col))
            if celda is None:
                continue
            crudo = normalizar(celda.texto)
            if clasificar(crudo) == VACIO and celda.valor_nativo is None:
                continue

            valor, avisos_valor = a_numero(crudo, celda.valor_nativo)
            # A fact needs a figure. A cell of plain text is not a fact; a cell
            # that WAS meant to be a number and could not be read is one,
            # because reporting it is what makes the loss visible.
            # [ES] Un hecho necesita una cifra. Una celda de texto llano no es
            # un hecho; una celda que IBA a ser un numero y no se pudo leer si
            # lo es, porque informarla es lo que vuelve visible la perdida.
            if valor is None and not set(avisos_valor) & IRRECUPERABLES_QUE_IMPORTAN:
                continue
            if not row_label:
                avisos_valor = tuple(avisos_valor) + ("fila_sin_etiqueta",)

            periodo, avisos_periodo = periodos[col]
            unidad, avisos_unidad = unidades[col]
            avisos = tuple(
                dict.fromkeys(
                    tuple(avisos_valor) + tuple(avisos_periodo) + tuple(avisos_unidad)
                )
            )

            hechos.append(
                HechoTabular(
                    document_id=segmento.document_id,
                    artifact_id=segmento.artifact_id,
                    fuente=segmento.fuente,
                    entidad=segmento.entidad,
                    table_uid=segmento.table_uid,
                    table_segment_uid=segmento.table_segment_uid,
                    continuation_of=segmento.continuation_of,
                    source_pages=paginas,
                    hoja=segmento.hoja,
                    ancla=segmento.ancla,
                    table_title=titulo,
                    row_label=row_label,
                    row_section=seccion,
                    column_path=caminos[col],
                    period=periodo,
                    unit=unidad if unidad.declarada() else None,
                    value_raw=crudo if crudo else str(celda.valor_nativo),
                    value=valor,
                    cell_coordinates={
                        "fila": fila,
                        "col": col,
                        "fila_span": celda.fila_span,
                        "col_span": celda.col_span,
                        "coordenada": celda.coordenada,
                        "pagina": celda.pagina,
                        "bbox": celda.bbox,
                        "segmento": segmento.ancla,
                    },
                    parser=segmento.parser,
                    parser_version=segmento.parser_version,
                    extraccion_version=EXTRACCION_VERSION,
                    extraction_warnings=tuple(
                        dict.fromkeys(avisos_segmento + avisos)
                    ),
                    reglas=tuple(segmento.reglas),
                    confianza=_confianza(
                        bool(caminos[col]),
                        heredado,
                        unidad,
                        periodo is not None,
                        avisos,
                        valor,
                    ),
                )
            )
    return hechos


def hechos_de_documento(segmentos: list[SegmentoTabla]) -> list[HechoTabular]:
    por_uid = {s.table_segment_uid: s for s in segmentos}
    return [h for s in segmentos for h in hechos_de_segmento(s, por_uid)]
