"""Tests for the calibration of the final `k`.

No PostgreSQL: retrieval is injected. What is under test is that the two curves
are read over the same ranking and that a confirmatory item cannot be used to
choose a hyperparameter.

[ES] Pruebas de la calibración del `k` final.

Sin PostgreSQL: la recuperación se inyecta. Lo que se prueba es que las dos
curvas se lean sobre el mismo ranking y que un ítem confirmatorio no pueda
usarse para elegir un hiperparámetro.
"""

import unittest


from multirag.evaluation.calibrar_k import (
    ErrorDeCalibracion,
    calibrar,
    medir_item,
    validar_items,
)


UID_EVIDENCIA = "e" * 64


def item(
    identificador: str = "G-P-001",
    uids=(UID_EVIDENCIA,),
    silos=("legal",),
    split: str = "desarrollo",
) -> dict:
    return {
        "id": identificador,
        "split": split,
        "pregunta": "¿Qué sanciones corresponden?",
        "silos_necesarios": list(silos),
        "evidencia": [
            {"chunk_uid_snapshot": uid}
            for uid in uids
        ],
    }


def chunk(uid: str, dominios=("legal",), contenido: str = "x" * 100) -> dict:
    return {
        "chunk_uid": uid,
        "silo": dominios[0] if dominios else None,
        "dominios_recuperacion": list(dominios),
        "contenido": contenido,
        "similitud": 0.9,
    }


class ValidacionTestCase(unittest.TestCase):
    """Development only, and evidence marked.

    [ES] Solo desarrollo, y con evidencia marcada.
    """

    def test_acepta_items_de_desarrollo(self) -> None:
        self.assertEqual(len(validar_items([item()])), 1)

    def test_rechaza_un_item_confirmatorio(self) -> None:
        """Using the test to choose a hyperparameter invalidates it.

        [ES] Usar el test para elegir un hiperparámetro lo invalida.
        """
        with self.assertRaises(ErrorDeCalibracion) as contexto:
            validar_items([item(split="test")])

        self.assertIn("desarrollo", str(contexto.exception))

    def test_rechaza_item_sin_evidencia(self) -> None:
        with self.assertRaises(ErrorDeCalibracion) as contexto:
            validar_items([item(uids=())])

        self.assertIn("evidencia", str(contexto.exception))

    def test_rechaza_conjunto_vacio(self) -> None:
        with self.assertRaises(ErrorDeCalibracion):
            validar_items([])


class MedirItemTestCase(unittest.TestCase):
    """Recall and contamination over the delivered prefix.

    [ES] Recall y contaminación sobre el prefijo entregado.
    """

    def test_evidencia_dentro_del_prefijo(self) -> None:
        resultados = [chunk("a" * 64), chunk(UID_EVIDENCIA)]

        self.assertFalse(medir_item(item(), resultados, 1)["acierto"])
        self.assertTrue(medir_item(item(), resultados, 2)["acierto"])

    def test_cuenta_la_contaminacion_por_dominio(self) -> None:
        resultados = [
            chunk(UID_EVIDENCIA, ("legal",)),
            chunk("b" * 64, ("contable",)),
            chunk("c" * 64, ("impositivo",)),
        ]

        medicion = medir_item(item(silos=("legal",)), resultados, 3)

        self.assertEqual(medicion["contaminados"], 2)

    def test_un_chunk_multidominio_no_contamina_si_toca_lo_necesario(
        self,
    ) -> None:
        """A0 and A1 are read with the same rule: intersection, not equality.

        [ES] A0 y A1 se leen con la misma regla: intersección, no igualdad.
        """
        resultados = [chunk("b" * 64, ("contable", "legal"))]

        medicion = medir_item(item(silos=("legal",)), resultados, 1)

        self.assertEqual(medicion["contaminados"], 0)

    def test_sin_silos_necesarios_no_se_puntua_contaminacion(self) -> None:
        medicion = medir_item(
            item(silos=()),
            [chunk("b" * 64, ("contable",))],
            1,
        )

        self.assertFalse(medicion["puntuable_contaminacion"])
        self.assertEqual(medicion["contaminados"], 0)

    def test_mide_el_presupuesto_de_contexto(self) -> None:
        """k is not only a count of fragments.

        [ES] k no es solo una cantidad de fragmentos.
        """
        resultados = [
            chunk("a" * 64, contenido="x" * 100),
            chunk("b" * 64, contenido="y" * 900),
        ]

        self.assertEqual(medir_item(item(), resultados, 1)["caracteres"], 100)
        self.assertEqual(medir_item(item(), resultados, 2)["caracteres"], 1000)

    def test_cae_al_silo_cuando_no_hay_dominios_de_recuperacion(self) -> None:
        registro = chunk("b" * 64)
        registro["dominios_recuperacion"] = []
        registro["silo"] = "contable"

        medicion = medir_item(item(silos=("legal",)), [registro], 1)

        self.assertEqual(medicion["contaminados"], 1)


class CalibrarTestCase(unittest.TestCase):
    """The grid comes from one ranking per question.

    [ES] La grilla sale de un solo ranking por pregunta.
    """

    def test_recupera_una_sola_vez_por_pregunta(self) -> None:
        """Two k values must not come from two separate runs.

        [ES] Dos valores de k no pueden salir de dos corridas distintas.
        """
        llamadas = []

        def buscar_falso(pregunta, k=3, **kwargs):
            llamadas.append((pregunta, k))
            return [chunk(f"{i:064x}") for i in range(k)]

        calibrar([item(), item("G-P-002")], buscar_falso, (1, 3, 5))

        self.assertEqual(len(llamadas), 2)
        self.assertEqual({k for _, k in llamadas}, {5})

    def test_el_recall_no_baja_al_crecer_k(self) -> None:
        """More context never removes an already delivered fragment.

        [ES] Más contexto nunca saca un fragmento ya entregado.
        """
        def buscar_falso(pregunta, k=3, **kwargs):
            return [
                chunk("a" * 64),
                chunk("b" * 64),
                chunk(UID_EVIDENCIA),
                chunk("d" * 64),
            ][:k]

        informe = calibrar([item()], buscar_falso, (1, 2, 3, 4))

        recalls = [fila["recall_item"] for fila in informe]

        self.assertEqual(recalls, sorted(recalls))
        self.assertEqual(informe[0]["recall_item"], 0.0)
        self.assertEqual(informe[-1]["recall_item"], 1.0)

    def test_la_contaminacion_sube_al_crecer_k(self) -> None:
        def buscar_falso(pregunta, k=3, **kwargs):
            return [
                chunk(UID_EVIDENCIA, ("legal",)),
                chunk("b" * 64, ("contable",)),
                chunk("c" * 64, ("financiero",)),
            ][:k]

        informe = calibrar([item()], buscar_falso, (1, 3))

        self.assertEqual(informe[0]["contaminacion"], 0.0)
        self.assertAlmostEqual(informe[1]["contaminacion"], 2 / 3)

    def test_distingue_recall_de_item_y_de_evidencia(self) -> None:
        """With two reference fragments, delivering one is not full recall.

        [ES] Con dos fragmentos de referencia, entregar uno no es recall pleno.
        """
        otro = "f" * 64

        def buscar_falso(pregunta, k=3, **kwargs):
            return [chunk(UID_EVIDENCIA)][:k]

        informe = calibrar(
            [item(uids=(UID_EVIDENCIA, otro))],
            buscar_falso,
            (1,),
        )

        self.assertEqual(informe[0]["recall_item"], 1.0)
        self.assertEqual(informe[0]["recall_evidencia"], 0.5)

    def test_rechaza_valores_de_k_invalidos(self) -> None:
        with self.assertRaises(ErrorDeCalibracion):
            calibrar([item()], lambda *a, **k: [], (0, 3))


if __name__ == "__main__":
    unittest.main()
