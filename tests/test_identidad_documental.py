"""Tests for documentary identity linkage.

[ES] Pruebas de la vinculación de identidad documental.
"""

import hashlib
import tempfile
import unittest
from pathlib import Path

from multirag.ingestion.pipeline import (
    construir_parser,
    resolver_identidad_documental,
)
from multirag.ingestion.vincular_identidad import (
    construir_plan_vinculacion,
)


class IdentidadDocumentalTestCase(unittest.TestCase):
    """Verify documentary identity resolution and linkage planning.

    [ES] Verifica la resolución y planificación de identidad documental.
    """

    def construir_identidad(
        self,
        fuente: str,
        contenido: bytes,
        instrument_id: str,
        document_id: str,
    ) -> dict[str, str]:
        """Build a valid identity fixture from binary content.

        [ES] Construye una identidad de prueba desde contenido binario.
        """

        huella_sha256 = hashlib.sha256(contenido).hexdigest()

        return {
            "fuente": fuente,
            "instrument_id": instrument_id,
            "document_id": document_id,
            "artifact_id": (
                f"ART-SHA256-{huella_sha256.upper()}"
            ),
        }

    def test_resuelve_identidad_por_contenido(self) -> None:
        contenido = b"contenido documental verificable"

        identidad = self.construir_identidad(
            fuente="documento_catalogado",
            contenido=contenido,
            instrument_id="INS-0001",
            document_id="DOC-0001",
        )

        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "archivo_renombrado.pdf"
            ruta.write_bytes(contenido)

            resultado = resolver_identidad_documental(
                ruta=ruta,
                identidades_por_fuente={
                    identidad["fuente"]: identidad,
                },
            )

        self.assertEqual(resultado, identidad)

    def test_parser_acepta_catalogo_de_identidad_explicito(self) -> None:
        argumentos = construir_parser().parse_args(
            [
                "--metadatos",
                "catalogo_piloto.csv",
                "documento_a.html",
                "documento_b.html",
            ]
        )

        self.assertEqual(argumentos.metadatos, Path("catalogo_piloto.csv"))
        self.assertEqual(
            argumentos.documentos,
            [Path("documento_a.html"), Path("documento_b.html")],
        )

    def test_rechaza_artefacto_no_catalogado(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "desconocido.pdf"
            ruta.write_bytes(b"contenido no catalogado")

            with self.assertRaisesRegex(
                ValueError,
                "no tiene identidad documental curada",
            ):
                resolver_identidad_documental(
                    ruta=ruta,
                    identidades_por_fuente={},
                )

    def test_construye_plan_y_reporta_fuentes_no_ingeridas(
        self,
    ) -> None:
        identidad_ingerida = self.construir_identidad(
            fuente="fuente_ingerida",
            contenido=b"contenido ingerido",
            instrument_id="INS-0001",
            document_id="DOC-0001",
        )
        identidad_pendiente = self.construir_identidad(
            fuente="fuente_pendiente",
            contenido=b"contenido pendiente",
            instrument_id="INS-0002",
            document_id="DOC-0002",
        )

        plan, fuentes_no_ingeridas = construir_plan_vinculacion(
            chunks_por_fuente={
                "fuente_ingerida": 10,
            },
            identidades_por_fuente={
                "fuente_ingerida": identidad_ingerida,
                "fuente_pendiente": identidad_pendiente,
            },
        )

        self.assertEqual(
            plan,
            [
                (
                    "fuente_ingerida",
                    "INS-0001",
                    "DOC-0001",
                    identidad_ingerida["artifact_id"],
                )
            ],
        )
        self.assertEqual(
            fuentes_no_ingeridas,
            ["fuente_pendiente"],
        )

    def test_rechaza_fuente_persistida_sin_identidad(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "sin identidad curada",
        ):
            construir_plan_vinculacion(
                chunks_por_fuente={
                    "fuente_sin_catalogar": 5,
                },
                identidades_por_fuente={},
            )


if __name__ == "__main__":
    unittest.main()
