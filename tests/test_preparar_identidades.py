"""Tests for explicit pilot identity preparation.

[ES] Pruebas de preparacion explicita de identidades piloto.
"""

import tempfile
import unittest
from pathlib import Path

from multirag.ingestion.preparar_identidades import (
    construir_identidades_piloto,
    guardar_identidades,
)
from multirag.ingestion.vincular_identidad import (
    cargar_identidades_por_fuente,
)


class PrepararIdentidadesTestCase(unittest.TestCase):
    """Verify allocation, selection and persistence of pilot identities."""

    def test_asigna_ids_despues_de_los_maximos_y_respeta_orden(self) -> None:
        candidatos = [
            {"fuente": "fuente_b", "artifact_id": "ART-B"},
            {"fuente": "fuente_a", "artifact_id": "ART-A"},
        ]
        existentes = [
            {
                "instrument_id": "INS-0007",
                "document_id": "DOC-0009",
                "artifact_id": "ART-EXISTENTE",
                "fuente": "existente",
            }
        ]

        identidades = construir_identidades_piloto(
            candidatos=candidatos,
            existentes=existentes,
            fuentes=["fuente_a", "fuente_b"],
        )

        self.assertEqual(
            identidades,
            [
                {
                    "instrument_id": "INS-0008",
                    "document_id": "DOC-0010",
                    "artifact_id": "ART-A",
                    "fuente": "fuente_a",
                },
                {
                    "instrument_id": "INS-0009",
                    "document_id": "DOC-0011",
                    "artifact_id": "ART-B",
                    "fuente": "fuente_b",
                },
            ],
        )

    def test_rechaza_fuente_ausente(self) -> None:
        with self.assertRaisesRegex(ValueError, "no existen"):
            construir_identidades_piloto(
                candidatos=[{"fuente": "presente", "artifact_id": "ART-A"}],
                existentes=[],
                fuentes=["ausente"],
            )

    def test_rechaza_artefacto_ya_canonico(self) -> None:
        with self.assertRaisesRegex(ValueError, "ya existe"):
            construir_identidades_piloto(
                candidatos=[{"fuente": "nueva", "artifact_id": "ART-A"}],
                existentes=[
                    {
                        "instrument_id": "INS-0001",
                        "document_id": "DOC-0001",
                        "artifact_id": "ART-A",
                        "fuente": "existente",
                    }
                ],
                fuentes=["nueva"],
            )

    def test_salida_es_compatible_con_el_pipeline(self) -> None:
        identidades = [
            {
                "instrument_id": "INS-0001",
                "document_id": "DOC-0001",
                "artifact_id": "ART-A",
                "fuente": "fuente_a",
            }
        ]

        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / "identidades.csv"
            guardar_identidades(identidades, salida)
            cargadas = cargar_identidades_por_fuente(salida)

        self.assertEqual(cargadas, {"fuente_a": identidades[0]})


if __name__ == "__main__":
    unittest.main()
