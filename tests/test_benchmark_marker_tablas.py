"""Pruebas del benchmark estructural de parsers tabulares."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.diagnostics.benchmark_marker_tablas import (
    cargar_marker_archivo,
    evaluar_caso,
    tablas_desde_html,
    validar_manifest,
)


class BenchmarkMarkerTablasTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.html = """
        <table>
          <tr><th rowspan="2">Concepto</th><th colspan="2">Nueve meses</th></tr>
          <tr><th>2025</th><th>2024</th></tr>
          <tr><td>Ingresos</td><td>100</td><td>80</td></tr>
        </table>
        """

    def test_rowspan_colspan_conservan_alineacion(self) -> None:
        celdas = tablas_desde_html(self.html)[0]
        encabezado = next(c for c in celdas if c.texto == "Nueve meses")
        valor = next(c for c in celdas if c.texto == "100")

        self.assertEqual((encabezado.columna, encabezado.columna_fin), (1, 3))
        self.assertTrue(encabezado.comparte_columna(valor))

    def test_detecta_asociacion_correcta_y_columna_incorrecta(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "ejemplo.json"
            ruta.write_text(
                json.dumps(
                    {
                        "blocks": [
                            {
                                "id": "/page/4/Table/0",
                                "block_type": "Table",
                                "page": 999,
                                "html": self.html,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            tablas = cargar_marker_archivo(
                ruta, "ejemplo.pdf", "marker:test", page_base=0
            )

        base = {
            "case_id": "correcto",
            "documento": "ejemplo.pdf",
            "concepto": ["Ingresos"],
            "valor": ["100"],
            "encabezados": [["Nueve meses"], ["2025"]],
            "paginas": [5],
        }
        correcto = evaluar_caso(base, tablas)
        incorrecto = evaluar_caso(
            {**base, "case_id": "incorrecto", "valor": ["80"]}, tablas
        )

        self.assertTrue(correcto["respondible"])
        self.assertEqual(correcto["paginas_observadas"], [5])
        self.assertTrue(incorrecto["componentes"])
        self.assertTrue(incorrecto["misma_tabla"])
        self.assertFalse(incorrecto["asociacion"])

    def test_exige_todas_las_paginas_para_tabla_partida(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "ejemplo.json"
            ruta.write_text(
                json.dumps(
                    {
                        "blocks": [
                            {
                                "id": "/page/9/Table/0",
                                "block_type": "Table",
                                "page": 9,
                                "html": self.html,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            tablas = cargar_marker_archivo(
                ruta, "ejemplo.pdf", "marker:test", page_base=0
            )

        caso = {
            "case_id": "partida",
            "documento": "ejemplo.pdf",
            "concepto": ["Ingresos"],
            "valor": ["100"],
            "encabezados": [["2025"]],
            "paginas": [10, 11],
        }
        resultado = evaluar_caso(caso, tablas)

        self.assertTrue(resultado["asociacion"])
        self.assertFalse(resultado["procedencia"])
        self.assertFalse(resultado["respondible"])

    def test_manifest_rechaza_excel(self) -> None:
        manifest = {
            "cases": [
                {
                    "case_id": "excel",
                    "documento": "ventas.xlsx",
                    "concepto": ["Ventas"],
                    "valor": ["10"],
                    "paginas": [1],
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "auditar_excel"):
            validar_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
