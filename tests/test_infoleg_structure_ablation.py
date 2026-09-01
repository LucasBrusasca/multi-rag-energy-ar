"""Tests for the temporary InfoLEG structure ablation."""

import tempfile
import unittest
from pathlib import Path

from multirag.acquisition.providers.infoleg.normalize import (
    promover_encabezados_articulos,
)
from scripts.diagnostics.infoleg_structure_ablation import resumir_chunks


class InfolegStructureAblationTestCase(unittest.TestCase):
    """Verify safe article promotion and comparable metrics."""

    def test_promueve_inicios_y_no_referencias_internas(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            entrada = raiz / "entrada.htm"
            salida = raiz / "salida.htm"
            entrada.write_text(
                """
                <html><head></head><body>
                <div>Artículo 14 del Título I regula una referencia.</div>
                <div>ARTÍCULO 1º.- Primera disposición.</div>
                <div>Art. 2º — Segunda disposición.</div>
                <table><tr><td>Dato</td></tr></table>
                </body></html>
                """,
                encoding="utf-8",
            )

            resultado = promover_encabezados_articulos(entrada, salida)
            html = salida.read_text(encoding="utf-8")

            self.assertEqual(resultado["cantidad_promovida"], 2)
            self.assertTrue(resultado["contenido_visible_equivalente"])
            self.assertEqual(html.count("<h2>"), 2)
            self.assertIn("Artículo 14 del Título I", html)
            self.assertIn("<table>", html)

    def test_resumen_cuenta_estructura_y_cortes(self) -> None:
        chunks = [
            {
                "title": "ARTÍCULO 1º.-",
                "hierarchy": ["ARTÍCULO 1º.-"],
                "content": "Una frase incompleta",
            },
            {
                "title": "",
                "hierarchy": [],
                "content": "continúa aquí.",
            },
        ]

        resumen = resumir_chunks(chunks)

        self.assertEqual(resumen["chunks"], 2)
        self.assertEqual(resumen["chunks_con_titulo"], 1)
        self.assertEqual(resumen["chunks_con_jerarquia"], 1)
        self.assertEqual(resumen["cantidad_cortes_probables"], 1)


if __name__ == "__main__":
    unittest.main()
