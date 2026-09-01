"""Tests for the table-aware representation.

The guarantees under test are the ones that decide whether this can be adopted:

1. the header is inferred from the SHAPE of the grid, not from the parser's
   flags, which were wrong in 10 of 15 audited tables;
2. a data row is never promoted to header ("Variacion del Capital de Trabajo");
3. a continuation is linked only when EVERY condition holds, and both pages
   survive as provenance;
4. no unit, header or period is invented: what is missing stays null and warns;
5. the spreadsheet is read natively, with hierarchical headers resolved;
6. nothing here produces or requires a `chunk_uid`.

[ES] Pruebas de la representacion table-aware.

Las garantias que se prueban son las que deciden si esto se puede adoptar:

1. el encabezado se infiere de la FORMA de la grilla, no de las marcas del
   parser, que se equivocaron en 10 de 15 tablas auditadas;
2. una fila de datos nunca se promueve a encabezado ("Variacion del Capital de
   Trabajo");
3. una continuacion se vincula solo si se cumplen TODAS las condiciones, y las
   dos paginas sobreviven como procedencia;
4. no se inventa unidad, encabezado ni periodo: lo que falta queda en null y
   avisa;
5. la planilla se lee nativamente, con encabezados jerarquicos resueltos;
6. nada de esto produce ni necesita un `chunk_uid`.
"""

import json
import tempfile
import unittest
from pathlib import Path

from multirag.ingestion.tablas.adaptadores import (
    preparar_segmento,
    segmentos_desde_docling,
    segmentos_desde_excel,
)
from multirag.ingestion.tablas.continuidad import (
    enlazar_continuaciones,
    evaluar_continuidad,
)
from multirag.ingestion.tablas.grilla import (
    ANIO,
    NUMERO,
    TEXTO,
    VACIO,
    a_numero,
    clasificar,
    column_path,
    expandir,
)
from multirag.ingestion.tablas.hechos import hechos_de_documento
from multirag.ingestion.tablas.modelo import (
    Celda,
    SegmentoTabla,
    uid_segmento,
    uid_tabla,
)
from multirag.ingestion.tablas.semantica import detectar_periodo, detectar_unidad

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TRANSENER = FIXTURES / "transener_tablas_3_4.json"


def segmento_de_filas(filas, ancla="#/tables/0", paginas=(1,), artifact_id="ART-X", **extra):
    """[ES] Arma un segmento desde una matriz de textos, sin parser de por medio."""
    celdas = [
        Celda(fila=f, col=c, texto=texto)
        for f, fila in enumerate(filas)
        for c, texto in enumerate(fila)
    ]
    segmento = SegmentoTabla(
        table_segment_uid=uid_segmento(artifact_id, ancla),
        table_uid=uid_tabla(artifact_id, ancla),
        continuation_of=None,
        document_id="DOC-X",
        artifact_id=artifact_id,
        fuente="fuente_x",
        entidad="Entidad X",
        parser="prueba",
        parser_version="0",
        ancla=ancla,
        source_pages=paginas,
        num_rows=len(filas),
        num_cols=max(len(f) for f in filas),
        celdas=celdas,
        **extra,
    )
    return preparar_segmento(segmento)


class ClasificacionDeCeldas(unittest.TestCase):
    def test_un_anio_no_es_un_importe(self):
        # Collapsing the two is the mistake that turned an amount into a column
        # name in the audited report.
        # [ES] Confundirlos es el error que convirtio un importe en nombre de
        # columna en el informe auditado.
        self.assertEqual(clasificar("2024"), ANIO)
        self.assertEqual(clasificar("204.545"), NUMERO)
        self.assertEqual(clasificar("(30.716)"), NUMERO)
        self.assertEqual(clasificar("NIIF"), TEXTO)
        self.assertEqual(clasificar(""), VACIO)

    def test_importes_es_ar(self):
        self.assertEqual(a_numero("204.545")[0], 204545.0)
        self.assertEqual(a_numero("(30.716)")[0], -30716.0)
        self.assertEqual(a_numero("12,5")[0], 12.5)
        self.assertEqual(a_numero("-26")[0], -26.0)

    def test_valor_nativo_de_planilla_no_pasa_por_locale(self):
        self.assertEqual(a_numero("143.51411701499998", 143.51411701499998)[0], 143.51411701499998)

    def test_el_supuesto_de_locale_viaja_con_el_dato(self):
        # '1.029' is 1029 under es-AR and 1.029 under en-US. The corpus
        # convention is es-AR; what matters is that the assumption travels.
        # [ES] '1.029' es 1029 en es-AR y 1,029 en en-US. La convencion del
        # corpus es es-AR; lo que importa es que el supuesto viaje con el dato.
        valor, avisos = a_numero("1.029")
        self.assertEqual(valor, 1029.0)
        self.assertIn("separador_de_miles_asumido_es_ar", avisos)

    def test_con_los_dos_separadores_no_hay_ambiguedad(self):
        self.assertEqual(a_numero("1.029.320,50")[0], 1029320.5)
        self.assertEqual(a_numero("1,029,320.50")[0], 1029320.5)

    def test_dos_importes_pegados_no_son_un_numero(self):
        valor, avisos = a_numero("1.029.320 1.030.565")
        self.assertIsNone(valor)
        self.assertIn("celdas_colapsadas", avisos)


class BandaDeEncabezado(unittest.TestCase):
    def test_banda_multinivel(self):
        segmento = segmento_de_filas(
            [
                ["Cifras", "Moneda Constante", "Moneda Constante"],
                ["Año", "sept-25", "2024"],
                ["Período", "9 meses", "12 meses"],
                ["EBITDA", "219.587", "184.548"],
            ]
        )
        self.assertEqual(segmento.banda_encabezado, (0, 1, 2))

    def test_una_fila_de_importes_nunca_es_encabezado(self):
        # Case A of the acceptance criteria, in isolation.
        # [ES] Caso A de los criterios de aceptacion, aislado.
        segmento = segmento_de_filas(
            [
                ["Variación del Capital de Trabajo", "(30.716)", "(32.572)"],
                ["Flujo de Caja Operativo (FCO)", "204.545", "139.724"],
            ]
        )
        self.assertEqual(segmento.banda_encabezado, ())
        self.assertIn("sin_encabezado_propio", segmento.extraction_warnings)

    def test_la_discrepancia_con_el_parser_se_registra_no_se_pisa(self):
        celdas = [
            Celda(fila=0, col=0, texto="Concepto"),
            Celda(fila=0, col=1, texto="2024"),
            Celda(fila=1, col=0, texto="Ventas"),
            Celda(fila=1, col=1, texto="100", es_encabezado_col_parser=True),
        ]
        segmento = SegmentoTabla(
            table_segment_uid="TSEG-x", table_uid="TBL-x", continuation_of=None,
            document_id=None, artifact_id="ART", fuente=None, entidad=None,
            parser="prueba", parser_version="0", parser_marca_encabezados=True,
            ancla="#/tables/0",
            source_pages=(1,), num_rows=2, num_cols=2, celdas=celdas,
        )
        preparar_segmento(segmento)
        self.assertEqual(segmento.banda_encabezado, (0,))
        self.assertEqual(
            [celda.es_encabezado_col_parser for celda in segmento.celdas],
            [False, False, False, True],
        )
        self.assertTrue(
            any(
                a.startswith("nota:encabezado_discrepa_con_parser")
                for a in segmento.extraction_warnings
            )
        )

    def test_una_tabla_sin_importes_queda_fuera_de_alcance(self):
        segmento = segmento_de_filas(
            [["Resolución", "Fecha", "Implicancias"], ["21/2025", "28 de enero", "Flexibilizó"]]
        )
        self.assertIn("tabla_sin_valores_numericos", segmento.extraction_warnings)
        self.assertEqual(hechos_de_documento([segmento]), [])


class CaminoDeColumna(unittest.TestCase):
    def test_celda_combinada_encabeza_todas_sus_columnas(self):
        celdas = [
            Celda(fila=0, col=1, texto="First quarter", col_span=2),
            Celda(fila=1, col=1, texto="2026"),
            Celda(fila=1, col=2, texto="2025"),
        ]
        segmento = SegmentoTabla(
            table_segment_uid="TSEG-x", table_uid="TBL-x", continuation_of=None,
            document_id=None, artifact_id="ART", fuente=None, entidad=None,
            parser="prueba", parser_version="0", ancla="a", source_pages=(),
            num_rows=2, num_cols=3, celdas=celdas,
        )
        grilla = expandir(segmento)
        self.assertEqual(column_path(grilla, (0, 1), 1), ("First quarter", "2026"))
        self.assertEqual(column_path(grilla, (0, 1), 2), ("First quarter", "2025"))


class ReglaDeContinuidad(unittest.TestCase):
    def _cabecera(self, paginas=(10,)):
        return segmento_de_filas(
            [["Concepto", "sept-25", "2024"], ["EBITDA", "219.587", "184.548"]],
            ancla="#/tables/3",
            paginas=paginas,
        )

    def _continuacion(self, paginas=(11,)):
        return segmento_de_filas(
            [["Variación del Capital de Trabajo", "(30.716)", "(32.572)"]],
            ancla="#/tables/4",
            paginas=paginas,
        )

    def test_enlaza_cuando_se_cumplen_todas(self):
        cabecera, continuacion = self._cabecera(), self._continuacion()
        enlaza, reglas, motivo = evaluar_continuidad(cabecera, continuacion)
        self.assertTrue(enlaza, motivo)
        self.assertIn("paginas_consecutivas", reglas)
        self.assertIn("sin_encabezado_propio", reglas)

    def test_no_enlaza_si_las_paginas_no_son_consecutivas(self):
        enlaza, _, motivo = evaluar_continuidad(self._cabecera(), self._continuacion((13,)))
        self.assertFalse(enlaza)
        self.assertTrue(motivo.startswith("paginas_no_consecutivas"))

    def test_no_enlaza_si_tiene_encabezado_propio(self):
        propia = segmento_de_filas(
            [["Concepto", "2023", "2022"], ["EBITDA", "1.000", "900"]],
            ancla="#/tables/4",
            paginas=(11,),
        )
        enlaza, _, motivo = evaluar_continuidad(self._cabecera(), propia)
        self.assertFalse(enlaza)
        self.assertTrue(motivo.startswith("tiene_encabezado_propio"))

    def test_no_enlaza_entre_artefactos_distintos(self):
        otro = segmento_de_filas(
            [["Variación", "(1)", "(2)"]], ancla="#/tables/4", paginas=(11,), artifact_id="ART-OTRO"
        )
        enlaza, _, motivo = evaluar_continuidad(self._cabecera(), otro)
        self.assertFalse(enlaza)
        self.assertEqual(motivo, "otro_artefacto")

    def test_el_vinculo_no_fusiona_ni_borra_identidades(self):
        cabecera, continuacion = self._cabecera(), self._continuacion()
        uid_previo = continuacion.table_segment_uid
        enlazar_continuaciones([cabecera, continuacion])
        self.assertEqual(continuacion.table_segment_uid, uid_previo)
        self.assertEqual(continuacion.continuation_of, cabecera.table_segment_uid)
        self.assertEqual(continuacion.table_uid, cabecera.table_uid)
        self.assertEqual(continuacion.source_pages, (11,))
        self.assertEqual(cabecera.source_pages, (10,))

    def test_el_vinculo_es_reversible(self):
        # Undoing it is clearing one field: the facts go back to what they were
        # without the link, and nothing else changes.
        # [ES] Deshacerlo es borrar un campo: los hechos vuelven a ser lo que
        # eran sin el vinculo, y no cambia nada mas.
        cabecera, continuacion = self._cabecera(), self._continuacion()
        enlazar_continuaciones([cabecera, continuacion])
        con_vinculo = hechos_de_documento([cabecera, continuacion])[-1]
        self.assertEqual(con_vinculo.column_path, ("2024",))
        self.assertEqual(con_vinculo.source_pages, (10, 11))

        continuacion.continuation_of = None
        continuacion.table_uid = uid_tabla(continuacion.artifact_id, continuacion.ancla)
        sin_vinculo = hechos_de_documento([continuacion])[-1]
        self.assertEqual(sin_vinculo.column_path, ())
        self.assertEqual(sin_vinculo.source_pages, (11,))
        self.assertEqual(sin_vinculo.confianza, "baja")
        self.assertIn("sin_encabezado_recuperable", sin_vinculo.extraction_warnings)
        self.assertEqual(sin_vinculo.value, con_vinculo.value)


class UnidadYPeriodo(unittest.TestCase):
    def test_el_encabezado_le_gana_al_texto_adyacente(self):
        unidad, _ = detectar_unidad(
            [
                ("(miles de pesos)", "texto_adyacente", "#/texts/9"),
                ("$ Millones", "celda_encabezado", "r1c0"),
            ]
        )
        self.assertEqual(unidad.escala, "millones")
        self.assertEqual(unidad.origen, "celda_encabezado")

    def test_el_origen_viaja_con_la_unidad(self):
        unidad, _ = detectar_unidad(
            [("(millones de ARS, año fiscal finalizado en diciembre)", "texto_adyacente", "#/texts/376")]
        )
        self.assertEqual((unidad.escala, unidad.moneda), ("millones", "ARS"))
        self.assertEqual(unidad.origen, "texto_adyacente")
        self.assertEqual(unidad.evidencia_ref, "#/texts/376")

    def test_sin_declaracion_no_hay_unidad_inventada(self):
        unidad, avisos = detectar_unidad([("Cifras Consolidadas", "celda_encabezado", "r0c0")])
        self.assertFalse(unidad.declarada())
        self.assertIn("unidad_ausente", avisos)

    def test_el_simbolo_pesos_se_declara_como_inferencia(self):
        unidad, avisos = detectar_unidad([("$ Millones", "celda_encabezado", "r1c0")])
        self.assertEqual(unidad.moneda, "ARS")
        self.assertIn("moneda_inferida_de_simbolo_pesos", avisos)

    def test_periodo_compuesto_de_mes_y_duracion(self):
        periodo, _ = detectar_periodo(("sept-25", "9 meses"), "column_path")
        self.assertEqual(periodo.fecha_fin, "2025-09-30")
        self.assertEqual(periodo.granularidad, "9 meses")

    def test_periodo_de_trimestre_y_anio(self):
        periodo, _ = detectar_periodo(("First quarter", "2026"), "column_path")
        self.assertEqual((periodo.anio, periodo.granularidad), (2026, "3 meses"))

    def test_saldo_a_una_fecha(self):
        periodo, _ = detectar_periodo(("As of 03.31.2026",), "column_path")
        self.assertEqual(periodo.fecha_fin, "2026-03-31")
        self.assertEqual(periodo.granularidad, "saldo")

    def test_una_fecha_ambigua_no_se_resuelve(self):
        periodo, avisos = detectar_periodo(("Al 03/04/2026",), "column_path")
        self.assertIsNone(periodo.fecha_fin)
        self.assertTrue(any(a.startswith("fecha_ambigua") for a in avisos))

    def test_sin_periodo_declarado_devuelve_none(self):
        periodo, _ = detectar_periodo(("Importe",), "column_path")
        self.assertIsNone(periodo)


@unittest.skipUnless(TRANSENER.is_file(), f"falta el fixture {TRANSENER}")
class AceptacionTransener(unittest.TestCase):
    """Case A: a table continued between pages, with an orphan continuation.

    [ES] Caso A: tabla continuada entre paginas, con la continuacion huerfana.
    """

    @classmethod
    def setUpClass(cls):
        documento = json.loads(TRANSENER.read_text(encoding="utf-8"))
        cls.segmentos = segmentos_desde_docling(
            documento,
            parser_version="docling-fixture",
            identidad={
                "document_id": "DOC-0024",
                "artifact_id": "ART-SHA256-D883",
                "fuente": "Transener_Calificacion_FIX",
                "entidad": "Transener",
            },
        )
        cls.por_ancla = {s.ancla: s for s in cls.segmentos}
        cls.hechos = hechos_de_documento(cls.segmentos)

    def test_a1_reconoce_que_la_tabla_continua_entre_paginas(self):
        cabecera = self.por_ancla["#/tables/3"]
        continuacion = self.por_ancla["#/tables/4"]
        self.assertEqual(continuacion.continuation_of, cabecera.table_segment_uid)
        self.assertEqual(continuacion.table_uid, cabecera.table_uid)

    def test_a2_recupera_el_encabezado_de_la_pagina_anterior(self):
        hecho = self._hecho("Flujo de Caja Operativo (FCO)", "139.724")
        self.assertEqual(
            hecho.column_path, ("Moneda Constante(*)", "NIIF", "sept-25", "9 meses")
        )
        self.assertEqual(hecho.period.fecha_fin, "2025-09-30")
        self.assertEqual(hecho.period.granularidad, "9 meses")

    def test_a3_variacion_del_capital_de_trabajo_no_es_encabezado(self):
        self.assertEqual(self.por_ancla["#/tables/4"].banda_encabezado, ())
        hecho = self._hecho("Variación del Capital de Trabajo", "(30.716)")
        self.assertEqual(hecho.value, -30716.0)
        self.assertNotIn(
            "Variación del Capital de Trabajo",
            [pieza for h in self.hechos for pieza in h.column_path],
        )

    def test_a4_conserva_ambas_paginas_como_procedencia(self):
        hecho = self._hecho("Flujo de Caja Operativo (FCO)", "139.724")
        self.assertEqual(hecho.source_pages, (10, 11))
        self.assertEqual(hecho.cell_coordinates["segmento"], "#/tables/4")
        self.assertIsNotNone(hecho.cell_coordinates["bbox"])

    def test_la_unidad_viene_del_texto_adyacente_y_lo_declara(self):
        hecho = self._hecho("Flujo de Caja Operativo (FCO)", "139.724")
        self.assertEqual((hecho.unit.escala, hecho.unit.moneda), ("millones", "ARS"))
        self.assertEqual(hecho.unit.base, "moneda_constante")
        self.assertEqual(hecho.unit.origen, "heredada_de_continuacion")
        self.assertEqual(hecho.unit.evidencia_ref, "#/texts/376")

    def test_la_afirmacion_es_legible_y_completa(self):
        afirmacion = self._hecho("Flujo de Caja Operativo (FCO)", "139.724").afirmacion()
        for pieza in (
            "Transener",
            "Flujo de Caja Operativo (FCO)",
            "9 meses",
            "2025-09-30",
            "millones de ARS",
            "139.724",
            "paginas 10 y 11",
        ):
            self.assertIn(pieza, afirmacion)

    def _hecho(self, etiqueta, crudo):
        for hecho in self.hechos:
            if hecho.row_label == etiqueta and hecho.value_raw == crudo:
                return hecho
        self.fail(f"no se emitio el hecho {etiqueta!r}={crudo!r}")


class AceptacionExcel(unittest.TestCase):
    """Case B: hierarchical and merged headers, native reading, no OCR.

    The workbook is built here so the test does not depend on a quarantined
    file, and reproduces the structure the audit found: unit in the label
    column, a merged period over the year columns, and a blank separator column.

    [ES] Caso B: encabezados jerarquicos y combinados, lectura nativa, sin OCR.

    El libro se arma aca para que la prueba no dependa de un archivo en
    cuarentena, y reproduce la estructura que encontro la auditoria: unidad en
    la columna de etiqueta, periodo combinado sobre las columnas de anio, y una
    columna separadora en blanco.
    """

    @classmethod
    def setUpClass(cls):
        openpyxl = __import__("openpyxl")
        cls.directorio = tempfile.TemporaryDirectory()
        cls.ruta = Path(cls.directorio.name) / "planilla.xlsx"
        libro = openpyxl.Workbook()
        hoja = libro.active
        hoja.title = "EERR"
        hoja["B2"] = "In US$ million"
        hoja["D2"] = "First quarter"
        hoja.merge_cells("D2:F2")
        hoja.merge_cells("B2:B3")
        hoja["D3"] = 2026
        hoja["F3"] = 2025
        hoja["B4"], hoja["D4"], hoja["F4"] = "Sales revenue", 573, 414
        hoja["B5"], hoja["D5"], hoja["F5"] = "Selling expenses", -26, -21
        libro.save(cls.ruta)
        libro.close()

        cls.segmentos = segmentos_desde_excel(
            cls.ruta,
            parser_version="openpyxl-prueba",
            identidad={"artifact_id": "ART-XLSX", "fuente": "planilla.xlsx"},
        )
        cls.hechos = hechos_de_documento(cls.segmentos)

    @classmethod
    def tearDownClass(cls):
        cls.directorio.cleanup()

    def test_b1_se_lee_nativamente_sin_ocr(self):
        self.assertEqual([s.parser for s in self.segmentos], ["openpyxl"])

    def test_b2_resuelve_encabezado_combinado_y_jerarquico(self):
        hecho = self._hecho("Sales revenue", 573)
        self.assertEqual(hecho.column_path, ("First quarter", "2026"))

    def test_b3_asocia_concepto_periodo_unidad_y_valor(self):
        hecho = self._hecho("Selling expenses", -26)
        self.assertEqual(hecho.row_label, "Selling expenses")
        self.assertEqual(hecho.period.anio, 2026)
        self.assertEqual(hecho.period.granularidad, "3 meses")
        self.assertEqual((hecho.unit.escala, hecho.unit.moneda), ("millones", "USD"))
        self.assertEqual(hecho.value, -26.0)

    def test_b4_la_columna_separadora_vacia_no_genera_hechos(self):
        self.assertEqual({h.cell_coordinates["coordenada"][0] for h in self.hechos}, {"D", "F"})

    def test_la_procedencia_llega_a_la_celda(self):
        hecho = self._hecho("Sales revenue", 414)
        self.assertEqual(hecho.cell_coordinates["coordenada"], "F4")
        self.assertEqual(hecho.hoja, "EERR")
        self.assertIn("EERR", hecho.ancla)

    def _hecho(self, etiqueta, valor):
        for hecho in self.hechos:
            if hecho.row_label == etiqueta and hecho.value == valor:
                return hecho
        self.fail(f"no se emitio el hecho {etiqueta!r}={valor!r}")


class Advertencias(unittest.TestCase):
    def test_no_se_contrasta_contra_un_parser_que_no_marca_encabezados(self):
        # openpyxl emits no header flags; counting that as a disagreement would
        # inflate the measurement of how often Docling gets it wrong.
        # [ES] openpyxl no emite marcas de encabezado; contarlo como
        # discrepancia inflaria la medicion de cuanto se equivoca Docling.
        segmento = segmento_de_filas([["Concepto", "2024"], ["Ventas", "100"]])
        self.assertFalse(
            [a for a in segmento.extraction_warnings if a.startswith("nota:")]
        )

    def test_una_nota_no_es_una_limitacion_del_dato(self):
        # The parser disagreement is a measurement of the parser, not a defect
        # of the figure; mixing the two would make every fact look degraded.
        # [ES] La discrepancia con el parser mide al parser, no degrada la
        # cifra; mezclarlas haria que todos los hechos parezcan deficientes.
        segmento = segmento_de_filas(
            [["Concepto (millones de pesos)", "2024"], ["Ventas", "100"]]
        )
        hecho = hechos_de_documento([segmento])[0]
        limitantes = [
            a for a in hecho.extraction_warnings if not a.startswith("nota:")
        ]
        self.assertEqual(limitantes, [])
        self.assertEqual(hecho.confianza, "alta")


class IdentidadesYAislamiento(unittest.TestCase):
    def test_los_uid_son_deterministicos(self):
        self.assertEqual(uid_segmento("ART", "#/tables/4"), uid_segmento("ART", "#/tables/4"))
        self.assertNotEqual(uid_segmento("ART", "#/tables/4"), uid_segmento("ART", "#/tables/3"))

    def test_ningun_campo_del_hecho_es_un_chunk_uid(self):
        # This representation lives beside `chunks`; it neither reads nor
        # rewrites a single chunk_uid.
        # [ES] Esta representacion vive al lado de `chunks`; no lee ni reescribe
        # ningun chunk_uid.
        segmento = segmento_de_filas(
            [["Concepto", "2024"], ["Ventas", "100"]]
        )
        hecho = hechos_de_documento([segmento])[0]
        self.assertNotIn("chunk_uid", hecho.como_dict())

    def test_el_hecho_se_serializa_a_json(self):
        segmento = segmento_de_filas([["Concepto", "2024"], ["Ventas", "100"]])
        hecho = hechos_de_documento([segmento])[0]
        json.dumps(hecho.como_dict(), ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
