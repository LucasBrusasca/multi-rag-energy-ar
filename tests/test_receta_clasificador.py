"""Tests for freezing the classifier recipe.

The guarantee under test is narrow and important: a silent change to the prompt,
the silo descriptions, the model or the temperature must be detected.

[ES] Pruebas del congelamiento de la receta del clasificador.

La garantía que se prueba es angosta e importante: un cambio silencioso del
prompt, de las descripciones de silo, del modelo o de la temperatura tiene que
detectarse.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


from multirag.research import receta_clasificador as receta_mod
from multirag.research.receta_clasificador import (
    RecetaAlterada,
    congelar,
    huella,
    plantilla,
    receta,
    verificar,
)


class HuellaTestCase(unittest.TestCase):
    """The fingerprint covers everything that changes the answer.

    [ES] La huella cubre todo lo que cambia la respuesta.
    """

    def test_es_determinista(self) -> None:
        self.assertEqual(huella(), huella())

    def test_la_plantilla_contiene_las_descripciones_de_silo(self) -> None:
        texto = plantilla()

        for silo in ("legal", "impositivo", "contable", "financiero"):
            self.assertIn(silo, texto)

    def test_la_plantilla_no_contiene_el_texto_de_un_chunk(self) -> None:
        """The fingerprint must describe the template, not one fragment.

        [ES] La huella tiene que describir la plantilla, no un fragmento.
        """
        self.assertIn("<<FRAGMENTO>>", plantilla())

    def test_cambiar_el_modelo_cambia_la_huella(self) -> None:
        original = receta()
        alterada = dict(original)
        alterada["modelo"] = "otro/modelo"

        self.assertNotEqual(huella(original), huella(alterada))

    def test_cambiar_una_descripcion_de_silo_cambia_la_huella(self) -> None:
        original = receta()
        alterada = json.loads(json.dumps(original))
        alterada["silos"]["legal"] += " y algo más"

        self.assertNotEqual(huella(original), huella(alterada))

    def test_cambiar_la_temperatura_cambia_la_huella(self) -> None:
        original = receta()
        alterada = dict(original)
        alterada["temperatura"] = 0.7

        self.assertNotEqual(huella(original), huella(alterada))


class CongelarTestCase(unittest.TestCase):
    """Freezing is a one-time act with an explicit date.

    [ES] Congelar es un acto único y con fecha explícita.
    """

    def setUp(self) -> None:
        self.directorio = tempfile.mkdtemp()
        self.ruta = Path(self.directorio) / "receta.json"

    def test_escribe_el_manifiesto(self) -> None:
        manifiesto = congelar(
            self.ruta,
            version="receta-llm-v1",
            fecha="2026-08-23",
            motivo="antes de clasificar el corpus",
        )

        self.assertTrue(self.ruta.is_file())
        self.assertEqual(manifiesto["version"], "receta-llm-v1")
        self.assertEqual(
            manifiesto["huella_sha256"],
            huella(),
        )

        guardado = json.loads(self.ruta.read_text(encoding="utf-8"))

        self.assertEqual(guardado["fecha_congelamiento"], "2026-08-23")
        self.assertIn("plantilla_prompt", guardado["receta"])

    def test_no_pisa_una_receta_existente(self) -> None:
        congelar(self.ruta, version="v1", fecha="2026-08-23")

        with self.assertRaises(RecetaAlterada) as contexto:
            congelar(self.ruta, version="v2", fecha="2026-08-24")

        self.assertIn("Ya existe", str(contexto.exception))


class VerificarTestCase(unittest.TestCase):
    """Verification is what turns freezing into a guarantee.

    [ES] La verificación es lo que convierte el congelamiento en garantía.
    """

    def setUp(self) -> None:
        self.directorio = tempfile.mkdtemp()
        self.ruta = Path(self.directorio) / "receta.json"
        congelar(
            self.ruta,
            version="receta-llm-v1",
            fecha="2026-08-23",
        )

    def test_sin_cambios_verifica(self) -> None:
        manifiesto = verificar(self.ruta)

        self.assertEqual(manifiesto["version"], "receta-llm-v1")

    def test_detecta_un_cambio_de_modelo(self) -> None:
        alterada = receta()
        alterada["modelo"] = "otro/modelo"

        with mock.patch.object(
            receta_mod,
            "receta",
            return_value=alterada,
        ):
            with self.assertRaises(RecetaAlterada) as contexto:
                verificar(self.ruta)

        self.assertIn("modelo", str(contexto.exception))

    def test_detecta_un_cambio_del_prompt(self) -> None:
        alterada = receta()
        alterada["plantilla_prompt"] += "\nRegla nueva agregada a mano."

        with mock.patch.object(
            receta_mod,
            "receta",
            return_value=alterada,
        ):
            with self.assertRaises(RecetaAlterada) as contexto:
                verificar(self.ruta)

        self.assertIn("plantilla del prompt", str(contexto.exception))

    def test_detecta_un_cambio_de_descripcion_de_silo(self) -> None:
        alterada = json.loads(json.dumps(receta()))
        alterada["silos"]["contable"] = "otra descripción"

        with mock.patch.object(
            receta_mod,
            "receta",
            return_value=alterada,
        ):
            with self.assertRaises(RecetaAlterada) as contexto:
                verificar(self.ruta)

        self.assertIn("contable", str(contexto.exception))

    def test_sin_receta_congelada_falla_con_mensaje_util(self) -> None:
        with self.assertRaises(RecetaAlterada) as contexto:
            verificar(Path(self.directorio) / "no_existe.json")

        self.assertIn("ANTES", str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
