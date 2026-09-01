"""Tests for the read-only classifier pilot ablation."""

import unittest

from scripts.diagnostics.clasificador_pilot_ablation import (
    combinar_cosenos,
    describir_distribucion,
    resumir,
    validar_pesos,
)


class ClasificadorPilotAblationTestCase(unittest.TestCase):
    """Verify the mathematical, database-independent diagnostic core."""

    def test_valida_y_ordena_pesos(self) -> None:
        self.assertEqual(validar_pesos([0.75, 0.25, 0.5]), [0.25, 0.5, 0.75])

        with self.assertRaisesRegex(ValueError, "entre 0 y 1"):
            validar_pesos([1.1])

    def test_combina_senales_con_peso_explicito(self) -> None:
        resultado = combinar_cosenos(
            {"legal": 0.8, "impositivo": 0.2},
            {"legal": 0.4, "impositivo": 0.6},
            peso_centroide=0.25,
        )

        self.assertAlmostEqual(resultado["legal"], 0.5)
        self.assertAlmostEqual(resultado["impositivo"], 0.5)

    def test_describe_distribucion_sin_umbral_oculto(self) -> None:
        resultado = describir_distribucion(
            {"legal": 0.6, "impositivo": 0.4}
        )

        self.assertEqual(resultado["silo"], "legal")
        self.assertAlmostEqual(resultado["margen_top1_top2"], 0.2)
        self.assertIn("entropia_normalizada", resultado)
        self.assertNotIn("ambiguo", resultado)

    def test_resumen_reporta_acuerdo_no_exactitud(self) -> None:
        resultados = [
            {
                "silo_ingesta": "legal",
                "politicas": {
                    "descripciones": {
                        "silo": "impositivo",
                        "margen_top1_top2": 0.1,
                        "entropia_normalizada": 0.8,
                    }
                },
            }
        ]

        resumen = resumir(resultados, ["descripciones"])

        self.assertEqual(
            resumen["descripciones"]["desacuerdos_con_silo_ingesta"],
            1,
        )
        self.assertNotIn("exactitud", resumen["descripciones"])


if __name__ == "__main__":
    unittest.main()
