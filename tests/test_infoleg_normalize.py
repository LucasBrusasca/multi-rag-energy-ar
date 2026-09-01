"""Tests for the provider-specific InfoLEG HTML normalization stage."""

import csv
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from multirag.acquisition.providers.infoleg.normalize import (
    normalizar_lote,
    promover_encabezados_articulos,
)


class InfolegNormalizeTestCase(unittest.TestCase):
    """Verify batch selection, provenance and raw-source preservation."""

    def test_preserva_dos_puntos_contiguos_al_encabezado(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            entrada = raiz / "fuente.htm"
            salida = raiz / "normalizada.html"
            texto_visible = "ARTÍCULO 1º-: Texto dispositivo."
            entrada.write_text(
                (
                    '<html><head><meta charset="utf-8"></head>'
                    f"<body><div>{texto_visible}</div></body></html>"
                ),
                encoding="utf-8",
            )

            procedencia = promover_encabezados_articulos(entrada, salida)
            documento = BeautifulSoup(
                salida.read_text(encoding="utf-8"),
                "lxml",
            )

            self.assertEqual(procedencia["cantidad_promovida"], 1)
            self.assertEqual(
                documento.body.get_text(" ", strip=True),
                texto_visible,
            )
            self.assertEqual(documento.h2.get_text(strip=True), "ARTÍCULO 1º-:")

    def test_registra_equivalencia_cuando_solo_normaliza_espaciado(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            entrada = raiz / "fuente.htm"
            salida = raiz / "normalizada.html"
            entrada.write_text(
                "<html><body><div>ARTÍCULO 21.-Sin reglamentar.</div></body></html>",
                encoding="utf-8",
            )

            procedencia = promover_encabezados_articulos(entrada, salida)

            self.assertTrue(procedencia["contenido_visible_equivalente"])
            self.assertEqual(
                procedencia["tipo_equivalencia"],
                "solo_espaciado",
            )

    def test_normaliza_disponibles_y_reporta_faltantes(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            seleccion = raiz / "seleccion.csv"
            entrada = raiz / "crudos"
            salida = raiz / "normalizados"
            entrada.mkdir()
            campos = ("dominio", "criterio", "id_norma")
            filas = [
                {
                    "dominio": "energia",
                    "criterio": "materia",
                    "id_norma": "1",
                },
                {
                    "dominio": "impositivo",
                    "criterio": "organismo",
                    "id_norma": "2",
                },
            ]

            with seleccion.open("w", encoding="utf-8", newline="") as archivo:
                escritor = csv.DictWriter(archivo, fieldnames=campos)
                escritor.writeheader()
                escritor.writerows(filas)

            crudo = entrada / "energia_materia_1.htm"
            contenido_crudo = (
                b"<html><body><div>ARTICULO 1.- Texto.</div></body></html>"
            )
            crudo.write_bytes(contenido_crudo)

            informe = normalizar_lote(seleccion, entrada, salida)

            self.assertEqual(informe["seleccionados"], 2)
            self.assertEqual(informe["normalizados"], 1)
            self.assertEqual(
                informe["faltantes"],
                ["impositivo_organismo_2.htm"],
            )
            self.assertEqual(crudo.read_bytes(), contenido_crudo)
            self.assertTrue((salida / "energia_materia_1.html").is_file())
            self.assertTrue(
                informe["resultados"][0]["contenido_visible_equivalente"]
            )


if __name__ == "__main__":
    unittest.main()
