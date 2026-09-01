"""Tests for the contrast against the catalog's human domains.

The point of these tests is the null hypothesis: an agreement figure produced
against very broad human labels can be high and mean nothing, and the report
must be able to say so.

[ES] Pruebas del contraste contra los dominios humanos del catálogo.

El punto de estas pruebas es la hipótesis nula: una cifra de acuerdo producida
contra etiquetas humanas muy amplias puede ser alta y no significar nada, y el
informe tiene que poder decirlo.
"""

import unittest


from multirag.config import SILOS
from scripts.diagnostics.contrastar_con_catalogo import contrastar


TODOS_LOS_SILOS = set(SILOS)


CATALOGO = {
    # A document whose human label covers every silo: the test cannot fail.
    # [ES] Un documento cuya etiqueta humana cubre todos los silos: el test no
    # puede fallar.
    "DOC-AMPLIO": {
        "humanos": TODOS_LOS_SILOS | {"regulatorio"},
        "silos": TODOS_LOS_SILOS,
    },
    # A document with a single silo: the test discriminates.
    # [ES] Un documento con un solo silo: el test discrimina.
    "DOC-ESTRECHO": {
        "humanos": {"legal", "regulatorio"},
        "silos": {"legal"},
    },
}


def chunk(uid: str, documento: str, silo: str, scores=None) -> dict:
    return {
        "chunk_uid": uid,
        "document_id": documento,
        "silo": silo,
        "scores": scores or {},
    }


class PoderDelTestCase(unittest.TestCase):
    """A broad human label inflates the agreement without adding evidence.

    [ES] Una etiqueta humana amplia infla el acuerdo sin aportar evidencia.
    """

    def test_documento_amplio_no_discrimina(self) -> None:
        resultado = contrastar(
            [chunk("a" * 64, "DOC-AMPLIO", "contable")],
            CATALOGO,
        )

        self.assertEqual(resultado["a0_dentro"], 1)
        self.assertEqual(resultado["discriminantes"], 0)
        self.assertAlmostEqual(
            resultado["esperado_al_azar"],
            1.0,
        )

    def test_documento_estrecho_discrimina(self) -> None:
        resultado = contrastar(
            [chunk("a" * 64, "DOC-ESTRECHO", "contable")],
            CATALOGO,
        )

        self.assertEqual(resultado["a0_dentro"], 0)
        self.assertEqual(resultado["discriminantes"], 1)
        self.assertAlmostEqual(
            resultado["esperado_al_azar"],
            1 / len(SILOS),
        )

    def test_el_acuerdo_restringido_separa_lo_informativo(self) -> None:
        """Nine chunks in the broad document and one wrong in the narrow one
        give 90 % overall, and 0 % where the test can actually fail.

        [ES] Nueve chunks en el documento amplio y uno equivocado en el
        estrecho dan 90 % global, y 0 % donde el test puede fallar de verdad.
        """
        chunks = [
            chunk(f"{indice:064x}", "DOC-AMPLIO", "contable")
            for indice in range(9)
        ] + [chunk("f" * 64, "DOC-ESTRECHO", "contable")]

        resultado = contrastar(chunks, CATALOGO)

        self.assertEqual(resultado["evaluables"], 10)
        self.assertEqual(resultado["a0_dentro"], 9)
        self.assertEqual(resultado["discriminantes"], 1)
        self.assertEqual(
            resultado["a0_dentro_discriminantes"],
            0,
        )
        self.assertAlmostEqual(
            resultado["esperado_al_azar"] / 10,
            (9 * 1.0 + 1 * (1 / len(SILOS))) / 10,
        )


class CoberturaTestCase(unittest.TestCase):
    """Chunks that cannot be contrasted are reported, never silently dropped.

    [ES] Los chunks que no se pueden contrastar se informan, nunca se
    descartan en silencio.
    """

    def test_chunk_sin_document_id(self) -> None:
        resultado = contrastar(
            [chunk("a" * 64, None, "legal")],
            CATALOGO,
        )

        self.assertEqual(resultado["sin_documento"], 1)
        self.assertEqual(resultado["evaluables"], 0)

    def test_documento_no_catalogado(self) -> None:
        resultado = contrastar(
            [chunk("a" * 64, "DOC-FANTASMA", "legal")],
            CATALOGO,
        )

        self.assertEqual(
            resultado["documento_no_catalogado"],
            1,
        )
        self.assertEqual(resultado["evaluables"], 0)

    def test_registra_los_casos_sospechosos(self) -> None:
        resultado = contrastar(
            [chunk("a" * 64, "DOC-ESTRECHO", "contable")],
            CATALOGO,
        )

        self.assertEqual(len(resultado["casos_fuera"]), 1)
        self.assertEqual(
            resultado["casos_fuera"][0]["silo"],
            "contable",
        )
        self.assertEqual(
            resultado["casos_fuera"][0]["dominios_humanos"],
            ["legal"],
        )


class ConjuntoA1TestCase(unittest.TestCase):
    """A1 is contrasted as containment, not as equality.

    [ES] A1 se contrasta como contención, no como igualdad.
    """

    def test_conjunto_contenido(self) -> None:
        resultado = contrastar(
            [
                chunk(
                    "a" * 64,
                    "DOC-ESTRECHO",
                    "legal",
                    {
                        "legal": 0.90,
                        "impositivo": 0.05,
                        "contable": 0.03,
                        "financiero": 0.02,
                    },
                )
            ],
            CATALOGO,
            margen=0.05,
        )

        self.assertEqual(resultado["a1_contenido"], 1)
        self.assertEqual(resultado["a1_agrega_fuera"], 0)

    def test_conjunto_que_agrega_un_dominio_ajeno(self) -> None:
        resultado = contrastar(
            [
                chunk(
                    "a" * 64,
                    "DOC-ESTRECHO",
                    "legal",
                    {
                        "legal": 0.46,
                        "impositivo": 0.44,
                        "contable": 0.05,
                        "financiero": 0.05,
                    },
                )
            ],
            CATALOGO,
            margen=0.05,
        )

        self.assertEqual(resultado["a1_agrega_fuera"], 1)
        self.assertEqual(
            dict(resultado["a1_dominios_fuera"]),
            {"impositivo": 1},
        )


if __name__ == "__main__":
    unittest.main()
