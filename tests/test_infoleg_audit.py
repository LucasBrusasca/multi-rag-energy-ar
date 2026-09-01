"""Tests for the non-destructive InfoLEG acquisition audit.

[ES] Pruebas de la auditoría no destructiva de adquisición InfoLEG.
"""

import csv
import json
import tempfile
import unittest
from pathlib import Path

from multirag.acquisition.providers.infoleg.audit import (
    auditar_lote,
    guardar_informe,
)


class InfolegAuditTestCase(unittest.TestCase):
    """Verify selection reconciliation and deterministic reporting.
    [ES] Verifica la conciliación y el informe determinista."""

    def _guardar_seleccion(self, ruta: Path, filas: list[dict]) -> None:
        campos = ("dominio", "criterio", "id_norma", "url")

        with ruta.open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(filas)

    def test_detecta_faltantes_extras_y_copias_exactas(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            seleccion = raiz / "seleccion.csv"
            textos = raiz / "textos"
            textos.mkdir()
            self._guardar_seleccion(
                seleccion,
                [
                    {
                        "dominio": "energia",
                        "criterio": "materia",
                        "id_norma": "1",
                        "url": "https://ejemplo/1",
                    },
                    {
                        "dominio": "impositivo",
                        "criterio": "organismo",
                        "id_norma": "2",
                        "url": "https://ejemplo/2",
                    },
                ],
            )
            contenido = b"<!doctype html><html><body>norma</body></html>"
            (textos / "energia_materia_1.htm").write_bytes(contenido)
            (textos / "nombre_historico_1.htm").write_bytes(contenido)

            informe = auditar_lote(seleccion, textos)

            self.assertEqual(informe["resumen"]["archivos_faltantes"], 1)
            self.assertEqual(informe["resumen"]["archivos_extras"], 1)
            self.assertEqual(
                informe["faltantes"],
                ["impositivo_organismo_2.htm"],
            )
            self.assertEqual(informe["extras"], ["nombre_historico_1.htm"])
            self.assertEqual(len(informe["grupos_duplicados"]), 1)

    def test_detecta_firma_no_html_y_pagina_de_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            seleccion = raiz / "seleccion.csv"
            textos = raiz / "textos"
            textos.mkdir()
            self._guardar_seleccion(
                seleccion,
                [
                    {
                        "dominio": "energia",
                        "criterio": "materia",
                        "id_norma": "1",
                        "url": "https://ejemplo/1",
                    },
                    {
                        "dominio": "energia",
                        "criterio": "materia",
                        "id_norma": "2",
                        "url": "https://ejemplo/2",
                    },
                ],
            )
            (textos / "energia_materia_1.htm").write_bytes(b"no es html")
            (textos / "energia_materia_2.htm").write_bytes(
                b"<html><body>403 Forbidden</body></html>"
            )

            informe = auditar_lote(seleccion, textos)

            self.assertEqual(
                informe["firma_no_html"],
                ["energia_materia_1.htm"],
            )
            self.assertEqual(
                informe["posibles_paginas_error_http"],
                ["energia_materia_2.htm"],
            )

    def test_guarda_json_determinista_y_sin_temporal_residual(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            destino = raiz / "informes" / "auditoria.json"
            informe = {"resumen": {"presentes": 2}, "faltantes": []}

            primera = guardar_informe(informe, destino)
            primer_contenido = primera.read_bytes()
            segunda = guardar_informe(informe, destino)

            self.assertEqual(primera, segunda)
            self.assertEqual(primer_contenido, segunda.read_bytes())
            self.assertEqual(
                json.loads(segunda.read_text(encoding="utf-8")),
                informe,
            )
            self.assertFalse((destino.parent / ".auditoria.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
