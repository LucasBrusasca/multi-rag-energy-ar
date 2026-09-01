"""Tests for the B0, B1 and B2 retrieval comparison.

[ES] Pruebas de la comparación de recuperación B0, B1 y B2.
"""

import unittest


from multirag.evaluation.comparar import comparar_recuperacion
from multirag.orchestration.alcance import ErrorDeAlcance


class CompararRecuperacionTestCase(unittest.TestCase):
    """Verify that the retrieval arms are compared fairly.

    [ES] Verifica que los brazos de recuperación se comparen justamente.
    """

    def test_compara_brazos_con_misma_pregunta_y_k(self) -> None:
        pregunta = "¿Qué establece la normativa aplicable?"
        k = 2
        silos_oraculo = ("legal", "impositivo")

        resultados_b0 = [
            {"silo": "legal", "similitud": 0.90},
            {"silo": "contable", "similitud": 0.70},
        ]
        chunk_uid_legal = "a" * 64
        resultados_legal = [
            {
                "chunk_uid": chunk_uid_legal,
                "silo": "legal",
                "similitud": 0.95,
            },
        ]
        resultados_impositivo = [
            {"silo": "impositivo", "similitud": 0.85},
        ]
        resultados_b2 = [
            {"silo": "legal", "similitud": 0.92},
            {"silo": "impositivo", "similitud": 0.82},
        ]

        llamadas_buscar = []
        llamadas_ruteado = []

        def buscar_falso(
            pregunta_recibida: str,
            silo: str | None = None,
            k: int = 3,
        ) -> list[dict]:
            llamadas_buscar.append(
                (pregunta_recibida, silo, k)
            )

            if silo is None:
                return resultados_b0

            if silo == "legal":
                return resultados_legal

            if silo == "impositivo":
                return resultados_impositivo

            return []

        def buscar_ruteado_falso(
            pregunta_recibida: str,
            k: int = 3,
        ) -> list[dict]:
            llamadas_ruteado.append(
                (pregunta_recibida, k)
            )
            return resultados_b2

        resultado = comparar_recuperacion(
            pregunta=pregunta,
            silos_oraculo=silos_oraculo,
            k=k,
            buscar_fn=buscar_falso,
            buscar_ruteado_fn=buscar_ruteado_falso,
        )

        self.assertEqual(
            llamadas_buscar,
            [
                (pregunta, None, k),
                (pregunta, "legal", k),
                (pregunta, "impositivo", k),
            ],
        )
        self.assertEqual(
            llamadas_ruteado,
            [
                (pregunta, k),
            ],
        )
        self.assertEqual(
            resultado["B0"],
            resultados_b0,
        )
        self.assertEqual(
            resultado["B1"],
            [
                resultados_legal[0],
                resultados_impositivo[0],
            ],
        )
        self.assertEqual(
            resultado["B1"][0]["chunk_uid"],
            chunk_uid_legal,
        )
        self.assertEqual(
            resultado["B2"],
            resultados_b2,
        )
        self.assertEqual(
            resultado["variante_asignacion"],
            "A0",
        )
        self.assertEqual(
            resultado["variante_expansion"],
            "E0",
        )
        self.assertIsNone(
            resultado["assignment_version"]
        )


class VariantesDeclaradasTestCase(unittest.TestCase):
    """The comparison can declare A0/A1/A2 and E0/E1 without renaming B0/B1/B2.

    [ES] La comparación puede declarar A0/A1/A2 y E0/E1 sin renombrar
    B0/B1/B2.
    """

    def registro(
        self,
        uid: str,
        similitud: float,
        silo: str = "legal",
        document_id: str | None = None,
    ) -> dict:
        return {
            "chunk_uid": uid,
            "silo": silo,
            "titulo": "",
            "contenido": "",
            "fuente": "",
            "document_id": document_id,
            "instrument_id": None,
            "artifact_id": None,
            "similitud": similitud,
            "dominios_recuperacion": [],
            "origen_recuperacion": "dominio",
        }

    def test_a0_explicita_conserva_el_camino_historico(self) -> None:
        llamadas = []

        def buscar_falso(pregunta, silo=None, k=3):
            llamadas.append((pregunta, silo, k))
            return [self.registro("uid-1", 0.9, silo or "legal")]

        resultado = comparar_recuperacion(
            pregunta="¿Qué dice la norma?",
            silos_oraculo=("legal",),
            k=1,
            buscar_fn=buscar_falso,
            buscar_ruteado_fn=lambda pregunta, k=3: [],
            variante_asignacion="A0",
            variante_expansion="E0",
        )

        # The historical signature is preserved: no extra arguments reach a
        # retrieval function that does not expect them.
        # [ES] Se conserva la firma histórica: ningún argumento extra llega a
        # una función de recuperación que no lo espera.
        self.assertEqual(
            llamadas,
            [
                ("¿Qué dice la norma?", None, 1),
                ("¿Qué dice la norma?", "legal", 1),
            ],
        )
        self.assertEqual(len(resultado["B1"]), 1)

    def test_a1_exige_version_explicita(self) -> None:
        with self.assertRaises(ErrorDeAlcance) as contexto:
            comparar_recuperacion(
                pregunta="¿Qué dice la norma?",
                silos_oraculo=("legal",),
                k=1,
                buscar_fn=lambda *a, **kw: [],
                buscar_ruteado_fn=lambda pregunta, k=3: [],
                variante_asignacion="A1",
            )

        self.assertIn(
            "assignment_version",
            str(contexto.exception),
        )

    def test_a1_declarada_deduplica_y_respeta_k(self) -> None:
        compartido_legal = self.registro("uid-compartido", 0.70)
        compartido_impositivo = self.registro(
            "uid-compartido",
            0.95,
            silo="legal",
        )

        def buscar_falso(pregunta, silo=None, k=3, documentos=None, **opciones):
            self.assertEqual(
                opciones["variante_asignacion"],
                "A1",
            )
            self.assertEqual(
                opciones["assignment_version"],
                "asignacion-piloto-1",
            )

            if silo == "legal":
                return [compartido_legal]

            if silo == "impositivo":
                return [compartido_impositivo]

            return [self.registro("uid-monolitico", 0.5)]

        resultado = comparar_recuperacion(
            pregunta="¿Qué dice la norma?",
            silos_oraculo=("legal", "impositivo"),
            k=2,
            buscar_fn=buscar_falso,
            buscar_ruteado_fn=lambda pregunta, k=3: [],
            variante_asignacion="A1",
            assignment_version="asignacion-piloto-1",
        )

        self.assertEqual(len(resultado["B1"]), 1)
        self.assertEqual(
            resultado["B1"][0]["dominios_recuperacion"],
            ["legal", "impositivo"],
        )
        self.assertEqual(
            resultado["B1"][0]["similitud"],
            0.95,
        )
        self.assertEqual(
            resultado["assignment_version"],
            "asignacion-piloto-1",
        )

    def test_variante_de_expansion_invalida(self) -> None:
        with self.assertRaises(ErrorDeAlcance):
            comparar_recuperacion(
                pregunta="¿Qué dice la norma?",
                silos_oraculo=("legal",),
                k=1,
                buscar_fn=lambda *a, **kw: [],
                buscar_ruteado_fn=lambda pregunta, k=3: [],
                variante_expansion="A2",
            )


if __name__ == "__main__":
    unittest.main()
