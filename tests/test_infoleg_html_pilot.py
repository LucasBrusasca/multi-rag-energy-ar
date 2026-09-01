"""Tests for the reproducible InfoLEG HTML-conversion pilot."""

import tempfile
import unittest
from pathlib import Path

from scripts.diagnostics.infoleg_html_pilot import (
    _es_corte_probable,
    diagnosticar_archivo,
    seleccionar_muestra,
)


class InfolegHtmlPilotTestCase(unittest.TestCase):
    """Verify sampling and derived conversion diagnostics."""

    def test_selecciona_mediana_por_grupo_y_maximo_global(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            textos = Path(temporal)
            filas = []

            for dominio, criterio, tamanos in (
                ("energia", "materia", (10, 20, 30)),
                ("energia", "organismo", (40, 50, 60)),
                ("impositivo", "materia", (70, 80, 500)),
                ("impositivo", "organismo", (90, 100, 110)),
            ):
                for indice, tamano in enumerate(tamanos, start=1):
                    identificador = f"{dominio}-{criterio}-{indice}"
                    fila = {
                        "dominio": dominio,
                        "criterio": criterio,
                        "id_norma": identificador,
                    }
                    filas.append(fila)
                    nombre = f"{dominio}_{criterio}_{identificador}.htm"
                    (textos / nombre).write_bytes(b"x" * tamano)

            muestra = seleccionar_muestra(filas, textos)

            self.assertEqual(len(muestra), 5)
            self.assertEqual(
                sorted(registro["tamano_bytes"] for registro in muestra),
                [20, 50, 80, 100, 500],
            )

    def test_diagnostica_estructura_articulos_y_corte_probable(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "energia_materia_1.htm"
            ruta.write_text(
                """
                <html><body>
                <h1>Norma</h1>
                <div>ARTÍCULO 1.- Primera disposición.</div>
                <div>ARTÍCULO 2.- Segunda disposición.</div>
                </body></html>
                """,
                encoding="utf-8",
            )
            registro = {
                "fila": {
                    "dominio": "energia",
                    "criterio": "materia",
                    "id_norma": "1",
                    "tipo_norma": "Ley",
                    "numero_norma": "1",
                },
                "ruta": ruta,
                "tamano_bytes": ruta.stat().st_size,
            }

            def convertidor(_ruta: Path, source: str) -> list[dict]:
                self.assertEqual(source, ruta.stem)
                return [
                    {
                        "title": "Norma",
                        "hierarchy": ["Norma"],
                        "content": "ARTÍCULO 1.- Primera disposición incompleta",
                    },
                    {
                        "title": "",
                        "hierarchy": [],
                        "content": "continúa. ARTÍCULO 2.- Segunda disposición.",
                    },
                ]

            resultado = diagnosticar_archivo(registro, convertidor=convertidor)

            self.assertEqual(resultado["fuente_html"]["encabezados_semanticos"], 1)
            self.assertEqual(resultado["conversion"]["chunks"], 2)
            self.assertEqual(
                resultado["conversion"]["articulos_fuente_recuperados"],
                2,
            )
            self.assertEqual(
                resultado["conversion"]["limites_con_corte_probable"],
                [1],
            )

    def test_heuristica_no_marca_limite_despues_de_punto(self) -> None:
        self.assertFalse(_es_corte_probable("Fin de oración.", "otra oración"))
        self.assertTrue(_es_corte_probable("frase incompleta", "continúa"))


if __name__ == "__main__":
    unittest.main()
