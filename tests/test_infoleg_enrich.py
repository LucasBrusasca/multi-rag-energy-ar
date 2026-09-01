"""Tests for source-backed InfoLEG metadata enrichment."""

import unittest

from multirag.acquisition.providers.infoleg.enrich import (
    enriquecer_plantilla,
    normalizar_valor_taxonomico,
)


class InfolegEnrichTestCase(unittest.TestCase):
    """Verify deterministic joins without creating semantic ground truth."""

    def test_normaliza_tipo_sin_mapa_de_casos(self) -> None:
        self.assertEqual(
            normalizar_valor_taxonomico("Resolución General"),
            "resolucion_general",
        )

    def test_enriquece_hechos_y_no_asigna_dominios(self) -> None:
        registro = {
            "instrument_id": "",
            "document_id": "",
            "artifact_id": "ART-SHA256-" + "A" * 64,
            "archivo_referencia": "energia_materia_1.html",
            "fuente": "energia_materia_1",
            "sha256": "a" * 64,
            "titulo_oficial": "",
            "emisor_id": "",
            "emisor_nombre": "",
            "tipo_documento": "",
            "fecha_documento": "",
            "jurisdiccion": "",
            "dominios_documentales": "",
            "origen_fuente": "",
            "url_origen": "",
            "modalidades_esperadas": "",
            "estado_inclusion": "",
            "motivo_exclusion": "",
            "observaciones": "",
        }
        seleccion = {
            "dominio": "energia",
            "criterio": "materia",
            "id_norma": "1",
            "tipo_norma": "Decreto",
            "numero_norma": "10/2024",
            "organismo_origen": "PODER EJECUTIVO NACIONAL",
            "fecha_sancion": "2024-01-02",
            "titulo_resumido": "REGLAMENTACION",
            "url": "https://example.test/1",
        }

        enriquecidos, resumen = enriquecer_plantilla(
            [registro],
            [seleccion],
            {"decreto"},
        )
        resultado = enriquecidos[0]

        self.assertEqual(resultado["tipo_documento"], "decreto")
        self.assertEqual(resultado["fecha_documento"], "2024-01-02")
        self.assertEqual(resultado["dominios_documentales"], "")
        self.assertEqual(resultado["instrument_id"], "")
        self.assertEqual(resultado["document_id"], "")
        self.assertEqual(resultado["emisor_id"], "")
        self.assertEqual(resultado["estado_inclusion"], "pendiente_revision")
        self.assertIn(
            "estrato_adquisicion=energia/materia",
            resultado["observaciones"],
        )
        self.assertEqual(resumen["enriquecidos"], 1)

    def test_tipo_nuevo_permanece_no_identificado(self) -> None:
        registro = {
            "fuente": "impositivo_organismo_2",
        }
        seleccion = {
            "dominio": "impositivo",
            "criterio": "organismo",
            "id_norma": "2",
            "tipo_norma": "Acordada",
            "numero_norma": "1",
            "organismo_origen": "TRIBUNAL",
            "fecha_sancion": "2024-01-02",
            "titulo_resumido": "TITULO",
            "url": "https://example.test/2",
        }

        enriquecidos, resumen = enriquecer_plantilla(
            [registro],
            [seleccion],
            {"decreto"},
        )

        self.assertEqual(
            enriquecidos[0]["tipo_documento"],
            "no_identificado",
        )
        self.assertIn("Acordada", enriquecidos[0]["observaciones"])
        self.assertEqual(resumen["tipos_pendientes"], ["Acordada"])


if __name__ == "__main__":
    unittest.main()
