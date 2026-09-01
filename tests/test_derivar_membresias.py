"""Tests for the statistics reported by the A1 parameter sweep.

They guard numbers that would end up in the thesis, so they must not be
sensitive to outliers in ways the reader cannot see.

[ES] Pruebas de los estadísticos que informa el barrido del parámetro de A1.

Resguardan números que terminarían en la tesis, así que no deben ser sensibles
a valores atípicos de un modo que el lector no pueda ver.
"""

import unittest


from scripts.admin.derivar_membresias_desde_scores import (
    _mediana,
    barrer_parametro,
)


UID_DECIDIDO = "a" * 64
UID_BIDOMINIO = "b" * 64
UID_INDECISO = "c" * 64


FILAS = [
    (
        UID_DECIDIDO,
        {
            "legal": 0.90,
            "impositivo": 0.05,
            "contable": 0.03,
            "financiero": 0.02,
        },
    ),
    (
        UID_BIDOMINIO,
        {
            "legal": 0.46,
            "impositivo": 0.44,
            "contable": 0.05,
            "financiero": 0.05,
        },
    ),
    (
        UID_INDECISO,
        {
            "legal": 0.26,
            "impositivo": 0.25,
            "contable": 0.25,
            "financiero": 0.24,
        },
    ),
]

SILOS_A0 = {
    UID_DECIDIDO: "legal",
    UID_BIDOMINIO: "legal",
    UID_INDECISO: "legal",
}


class MedianaTestCase(unittest.TestCase):
    """The median is not dragged by the chunks that open every domain.

    [ES] La mediana no la arrastran los chunks que abren todos los dominios.
    """

    def test_mitad_en_uno_y_mitad_en_cuatro(self) -> None:
        self.assertEqual(_mediana({1: 5, 4: 5}), 1.0)

    def test_mayoria_en_dos(self) -> None:
        self.assertEqual(_mediana({1: 1, 2: 8, 4: 1}), 2.0)

    def test_histograma_vacio(self) -> None:
        self.assertEqual(_mediana({}), 0.0)

    def test_un_solo_valor_atipico_no_mueve_la_mediana(self) -> None:
        """The mean would move; the median does not.

        [ES] El promedio se movería; la mediana no.
        """
        sin_atipico = _mediana({1: 99})
        con_atipico = _mediana({1: 99, 4: 1})

        self.assertEqual(sin_atipico, con_atipico)


class EstadisticosDelBarridoTestCase(unittest.TestCase):
    """Counts, not averages: the size of the experimental difference.

    [ES] Conteos, no promedios: el tamaño de la diferencia experimental.
    """

    def barrer(self, valor: float) -> dict:
        return barrer_parametro(
            FILAS,
            regla="margen",
            valores=(valor,),
            silos_a0=SILOS_A0,
        )[0]

    def test_difieren_de_a0_cuenta_los_chunks_con_mas_de_un_dominio(
        self,
    ) -> None:
        linea = self.barrer(0.05)

        self.assertEqual(linea["difieren_de_a0"], 2)
        self.assertAlmostEqual(
            linea["proporcion_difieren"],
            2 / 3,
        )

    def test_sin_discriminar_cuenta_aparte_los_que_abren_todo(self) -> None:
        linea = self.barrer(0.05)

        self.assertEqual(linea["sin_discriminar"], 1)

    def test_un_margen_minimo_no_difiere_de_a0(self) -> None:
        linea = self.barrer(0.001)

        self.assertEqual(linea["difieren_de_a0"], 0)
        self.assertEqual(linea["sin_discriminar"], 0)

    def test_la_inflacion_es_un_cociente_de_conteos(self) -> None:
        """Scope inflation per domain: eligible under A1 over labelled under A0.

        [ES] Inflación del alcance por dominio: elegibles bajo A1 sobre
        etiquetados bajo A0.
        """
        linea = self.barrer(0.05)

        # The three chunks carry silo='legal' under A0, and all three keep
        # 'legal' under A1, so its scope does not inflate.
        # [ES] Los tres chunks tienen silo='legal' bajo A0 y los tres conservan
        # 'legal' bajo A1, así que su alcance no se infla.
        self.assertAlmostEqual(linea["inflacion"]["legal"], 1.0)

        # 'impositivo' has no A0 chunk here, so it cannot be a ratio and is
        # omitted instead of dividing by zero.
        # [ES] 'impositivo' no tiene ningún chunk A0 acá, así que no puede ser
        # un cociente y se omite en lugar de dividir por cero.
        self.assertNotIn("impositivo", linea["inflacion"])

    def test_conserva_a0_siempre_con_la_regla_de_margen(self) -> None:
        for valor in (0.001, 0.05, 0.3, 0.9):
            linea = self.barrer(valor)

            self.assertEqual(
                linea["conserva_a0"],
                linea["chunks"],
            )


if __name__ == "__main__":
    unittest.main()
