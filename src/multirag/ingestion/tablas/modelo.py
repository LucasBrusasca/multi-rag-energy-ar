"""Table-aware representation: identities, units, periods, facts.

Nothing here touches `chunks`. A table segment is a NEW object that lives
beside the chunk and references it by value, exactly as the ledger does.

[ES] Representacion table-aware: identidades, unidades, periodos, hechos.

Nada de esto toca `chunks`. Un segmento de tabla es un objeto NUEVO que vive al
lado del chunk y lo referencia por valor, igual que el ledger.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any, Optional


# Version of the extraction recipe. It enters every uid, so two different
# recipes coexist in the same database without colliding and without rewriting
# a single chunk_uid.
# [ES] Version de la receta de extraccion. Entra en cada uid, asi dos recetas
# distintas conviven en la misma base sin colisionar y sin reescribir un solo
# chunk_uid.
EXTRACCION_VERSION = "tablas-v0.1"


def _uid(prefijo: str, *partes: object) -> str:
    """Deterministic identifier: same input, same uid, on any machine.

    [ES] Identificador deterministico: misma entrada, mismo uid, en cualquier
    maquina.
    """
    semilla = "|".join(str(p) for p in partes)
    return f"{prefijo}-{hashlib.sha256(semilla.encode('utf-8')).hexdigest()[:16]}"


def uid_segmento(artifact_id: str, ancla: str) -> str:
    """[ES] Identidad de UNA tabla fisica (una tabla de Docling, un bloque de hoja)."""
    return _uid("TSEG", artifact_id, ancla, EXTRACCION_VERSION)


def uid_tabla(artifact_id: str, ancla_cabecera: str) -> str:
    """Identity of the LOGICAL table: head segment plus its continuations.

    The physical segment keeps its own uid; this one only groups. That is what
    lets one table be linked to another without either losing its identity.

    [ES] Identidad de la tabla LOGICA: el segmento cabecera mas sus
    continuaciones. El segmento fisico conserva su propio uid; este solo
    agrupa. Eso es lo que permite vincular una tabla con otra sin que ninguna
    de las dos pierda su identidad.
    """
    return _uid("TBL", artifact_id, ancla_cabecera, EXTRACCION_VERSION)


@dataclass(frozen=True)
class Unidad:
    """How a number must be read. `origen` is part of the datum, not decoration.

    "millones" read inside the table header and "millones" read in a nearby
    paragraph do not carry the same evidentiary weight. A field that does not
    distinguish them turns an inference into a fact.

    [ES] Como hay que leer un numero. `origen` es parte del dato, no adorno.

    "millones" leido dentro del encabezado de la tabla y "millones" leido en un
    parrafo cercano no tienen la misma fuerza probatoria. Un campo que no los
    distingue convierte una inferencia en un dato.
    """

    escala: Optional[str] = None      # 'unidades' | 'miles' | 'millones' | 'miles_de_millones'
    moneda: Optional[str] = None      # 'ARS' | 'USD' | None
    base: Optional[str] = None        # 'moneda_constante' | 'moneda_homogenea' | 'nominal'
    es_porcentaje: bool = False
    origen: str = "ausente"           # celda_encabezado | caption | texto_adyacente |
                                      # heredada_de_continuacion | ausente
    evidencia_texto: Optional[str] = None
    evidencia_ref: Optional[str] = None
    reglas: tuple[str, ...] = ()

    def declarada(self) -> bool:
        return bool(self.escala or self.moneda or self.base or self.es_porcentaje)

    def legible(self) -> Optional[str]:
        if self.es_porcentaje:
            return "porcentaje"
        partes = [p for p in (self.escala, self.moneda) if p]
        if not partes:
            return self.base.replace("_", " ") if self.base else None
        texto = " de ".join(partes) if len(partes) == 2 else partes[0]
        if self.base:
            texto = f"{texto} ({self.base.replace('_', ' ')})"
        return texto


@dataclass(frozen=True)
class Periodo:
    """The period a column refers to. Never invented: only composed from cells.

    [ES] El periodo al que se refiere una columna. Nunca inventado: solo
    compuesto a partir de celdas.
    """

    crudo: Optional[str] = None         # exactly what the header cells said
    anio: Optional[int] = None
    mes: Optional[int] = None
    fecha_fin: Optional[str] = None     # ISO, only when the header states it or a
                                        # month-year makes it unambiguous
    granularidad: Optional[str] = None  # '3 meses' | '9 meses' | '12 meses' | 'saldo'
    origen: str = "ausente"             # column_path | celda_encabezado | ausente
    reglas: tuple[str, ...] = ()

    def legible(self) -> Optional[str]:
        if self.crudo is None:
            return None
        if self.fecha_fin and self.granularidad and self.granularidad != "saldo":
            return f"periodo de {self.granularidad} terminado el {self.fecha_fin}"
        if self.fecha_fin and self.granularidad == "saldo":
            return f"saldo al {self.fecha_fin}"
        if self.fecha_fin:
            return f"al {self.fecha_fin}"
        return self.crudo


@dataclass
class Celda:
    """One grid cell, with everything the parser said about it.

    The parser's header flags are stored VERBATIM. Our own inference lives in
    the segment, separately, so the disagreement between the two can be
    measured instead of silently overwritten.

    [ES] Una celda de la grilla, con todo lo que el parser dijo de ella.

    Las marcas de encabezado del parser se guardan TAL CUAL. Nuestra inferencia
    vive en el segmento, aparte, para poder medir el desacuerdo entre las dos
    en lugar de pisarlo en silencio.
    """

    fila: int
    col: int
    texto: str
    fila_span: int = 1
    col_span: int = 1
    valor_nativo: Any = None                  # only spreadsheets carry a typed value
    es_encabezado_col_parser: bool = False
    es_encabezado_fila_parser: bool = False
    es_seccion_parser: bool = False
    bbox: Optional[dict] = None
    coordenada: Optional[str] = None          # 'D4' in a spreadsheet, None in a PDF
    pagina: Optional[int] = None


@dataclass
class SegmentoTabla:
    """One PHYSICAL table: a Docling table, or one header block of a sheet.

    [ES] Una tabla FISICA: una tabla de Docling, o un bloque de encabezado de
    una hoja.
    """

    table_segment_uid: str
    table_uid: str
    continuation_of: Optional[str]
    document_id: Optional[str]
    artifact_id: Optional[str]
    fuente: Optional[str]
    entidad: Optional[str]
    parser: str
    parser_version: str
    ancla: str                                # '#/tables/4' | "'EERR-C ing'!B40:F52"
    # Whether this parser emits header flags at all. openpyxl does not, and
    # counting "the parser marked nothing" as a disagreement would inflate the
    # measurement of how often Docling is wrong.
    # [ES] Si este parser emite marcas de encabezado. openpyxl no lo hace, y
    # contar "el parser no marco nada" como discrepancia inflaria la medicion
    # de cada cuanto se equivoca Docling.
    parser_marca_encabezados: bool = False
    source_pages: tuple[int, ...] = ()
    hoja: Optional[str] = None
    caption: Optional[str] = None
    # The label-column cell of the first header row. It is a CELL, not a
    # guess: it is what tells five 'Reporting EBITDA' rows apart.
    # [ES] La celda de la columna de etiqueta en la primera fila de
    # encabezado. Es una CELDA, no una suposicion: es lo que distingue
    # cinco filas 'Reporting EBITDA' entre si.
    titulo_inferido: Optional[str] = None
    num_rows: int = 0
    num_cols: int = 0
    celdas: list[Celda] = field(default_factory=list)
    # Our own inference, never the parser's.
    # [ES] Nuestra inferencia, nunca la del parser.
    banda_encabezado: tuple[int, ...] = ()
    columna_etiqueta: int = 0
    unidad: Unidad = field(default_factory=Unidad)
    extraction_warnings: list[str] = field(default_factory=list)
    reglas: list[str] = field(default_factory=list)

    def avisar(self, aviso: str) -> None:
        if aviso not in self.extraction_warnings:
            self.extraction_warnings.append(aviso)

    def anotar(self, regla: str) -> None:
        if regla not in self.reglas:
            self.reglas.append(regla)


@dataclass(frozen=True)
class HechoTabular:
    """concept + period + unit + value, with the provenance that justifies it.

    [ES] concepto + periodo + unidad + valor, con la procedencia que lo
    justifica.
    """

    document_id: Optional[str]
    artifact_id: Optional[str]
    fuente: Optional[str]
    entidad: Optional[str]

    table_uid: str
    table_segment_uid: str
    continuation_of: Optional[str]
    source_pages: tuple[int, ...]
    hoja: Optional[str]
    ancla: str
    table_title: Optional[str]

    row_label: str
    row_section: Optional[str]
    column_path: tuple[str, ...]
    period: Optional[Periodo]
    unit: Optional[Unidad]

    value_raw: str
    value: Optional[float]
    cell_coordinates: dict

    parser: str
    parser_version: str
    extraccion_version: str
    extraction_warnings: tuple[str, ...]
    reglas: tuple[str, ...]
    confianza: str                            # 'alta' | 'media' | 'baja'

    def afirmacion(self) -> str:
        """One human-readable line. What is missing says so; it is not filled in.

        [ES] Una linea legible por humanos. Lo que falta se dice; no se rellena.
        """
        partes = [self.entidad or self.fuente or "(entidad no declarada)"]
        if self.table_title and self.table_title != self.row_label:
            partes.append(self.table_title)
        partes.append(
            f"{self.row_section} / {self.row_label}" if self.row_section else self.row_label
        )

        periodo = self.period.legible() if self.period else None
        partes.append(periodo or "(periodo no declarado)")

        unidad = self.unit.legible() if self.unit and self.unit.declarada() else None
        partes.append(unidad or "(unidad no declarada)")

        partes.append(f"valor {self.value_raw}")

        if self.source_pages:
            etiqueta = "pagina" if len(self.source_pages) == 1 else "paginas"
            partes.append(f"{etiqueta} {' y '.join(str(p) for p in self.source_pages)}")
        elif self.hoja:
            partes.append(
                f"hoja {self.hoja!r} celda {self.cell_coordinates.get('coordenada')}"
            )

        return " - ".join(partes)

    def como_dict(self) -> dict:
        d = asdict(self)
        d["period"] = asdict(self.period) if self.period else None
        d["unit"] = asdict(self.unit) if self.unit else None
        return d
