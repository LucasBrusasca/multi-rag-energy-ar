"""Tests for the blinded semantic review evidence policy.

[ES] Pruebas de la política de evidencia de la revisión ciega.
"""

import csv
import json
import unittest
from pathlib import Path


from multirag.evaluation.revisar_semantica_ciega import (
    normalizar_para_evidencia,
    renderizar_enlaces_markdown,
    validar_revision,
)


OBJETIVO_CON_ENLACE = (
    "correspondan. (Párrafo incorporado por art. 1° del\n"
    "[Decreto N° 752/2019]"
    "(\\\\servicios.infoleg.gob.ar\\verNorma.do?id=331094)\n"
    "B.O. 1/11/2019)"
)

VECINO_ANTERIOR = (
    "La ADMINISTRACIÓN FEDERAL DE INGRESOS PÚBLICOS informará "
    "los montos definitivos que al respecto"
)


def revision_valida(evidencias: list[str]) -> dict:
    """Build a minimal non-material review.

    [ES] Construye una revisión no material mínima.
    """
    return {
        "estado_revision": "sin_dominio_por_no_materialidad",
        "dominios_revision": [],
        "materialidad_revision": "administrativo_no_material",
        "evidencias_textuales": evidencias,
        "justificacion_breve": "Fórmula administrativa.",
        "confianza_autodeclarada": 0.9,
        "requiere_revision_experta": False,
        "motivo_revision": "",
    }


class RenderizarEnlacesTestCase(unittest.TestCase):
    """Verify the markdown rendering is narrow and deterministic.

    [ES] Verifica que el render markdown sea estrecho y determinista.
    """

    def test_renderiza_enlace_inline(self) -> None:
        self.assertEqual(
            renderizar_enlaces_markdown("ver [Ley 27.430](http://x)"),
            "ver Ley 27.430",
        )

    def test_no_toca_parentesis_ni_corchetes_sueltos(self) -> None:
        for texto in (
            "(Párrafo incorporado por art. 1°)",
            "[sin destino]",
            "(solo paréntesis)",
            "un [corchete] y un (paréntesis) sueltos",
        ):
            self.assertEqual(
                renderizar_enlaces_markdown(texto),
                texto,
            )

    def test_destino_con_parentesis_no_se_transforma(self) -> None:
        texto = "[Ley](http://x/a(b))"
        self.assertEqual(
            renderizar_enlaces_markdown(texto),
            texto,
        )

    def test_conserva_parentesis_en_texto_visible(self) -> None:
        self.assertEqual(
            renderizar_enlaces_markdown("[Ley 20.628 (t.o. 1997)](u)"),
            "Ley 20.628 (t.o. 1997)",
        )

    def test_es_determinista(self) -> None:
        self.assertEqual(
            normalizar_para_evidencia(OBJETIVO_CON_ENLACE),
            normalizar_para_evidencia(OBJETIVO_CON_ENLACE),
        )


class PoliticaEvidenciaTestCase(unittest.TestCase):
    """Verify what counts as literal evidence under policy v2.

    [ES] Verifica qué cuenta como evidencia literal bajo la v2.
    """

    def _validar(self, evidencias: list[str]) -> dict:
        return validar_revision(
            revision=revision_valida(evidencias),
            contenido_objetivo=OBJETIVO_CON_ENLACE,
        )

    def test_acepta_texto_visible_del_enlace(self) -> None:
        self._validar(["Decreto N° 752/2019"])

    def test_acepta_enlace_crudo_completo(self) -> None:
        self._validar(
            [
                "[Decreto N° 752/2019]"
                "(\\\\servicios.infoleg.gob.ar\\verNorma.do?id=331094)"
            ]
        )

    def test_acepta_cita_que_atraviesa_el_enlace(self) -> None:
        self._validar(
            [
                "(Párrafo incorporado por art. 1° del "
                "Decreto N° 752/2019 B.O. 1/11/2019)"
            ]
        )

    def test_rechaza_url_sola(self) -> None:
        with self.assertRaises(ValueError):
            self._validar(
                ["\\\\servicios.infoleg.gob.ar\\verNorma.do?id=331094"]
            )

    def test_rechaza_evidencia_del_vecino(self) -> None:
        for cita in (
            "ADMINISTRACIÓN FEDERAL DE INGRESOS PÚBLICOS",
            "los montos definitivos que al respecto",
        ):
            with self.assertRaises(ValueError):
                self._validar([cita])

    def test_rechaza_elipsis(self) -> None:
        with self.assertRaises(ValueError):
            self._validar(["correspondan. ... B.O. 1/11/2019)"])

    def test_rechaza_parafraseo(self) -> None:
        with self.assertRaises(ValueError):
            self._validar(["párrafo agregado por el decreto 752"])

    def test_no_modifica_la_evidencia_almacenada(self) -> None:
        cruda = (
            "[Decreto N° 752/2019]"
            "(\\\\servicios.infoleg.gob.ar\\verNorma.do?id=331094)"
        )
        resultado = self._validar([cruda])
        self.assertEqual(
            resultado["evidencias_textuales"],
            [cruda],
        )


class RevalidacionResultadosExistentesTestCase(unittest.TestCase):
    """Re-check stored evidence without invoking any model.

    [ES] Revalida evidencia almacenada sin invocar ningún modelo.
    """

    BASE = (
        Path(__file__).resolve().parents[1]
        / "experimentos"
        / "contexto_semantico_piloto_v1"
    )

    def test_los_jsonl_existentes_siguen_validando(self) -> None:
        planilla = self.BASE / "revision_ciega_v1.csv"

        if not planilla.is_file():
            self.skipTest("Artefactos del piloto no disponibles.")

        with planilla.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as archivo:
            filas = {
                int(fila["orden_revision"]): fila["contenido_objetivo"]
                for fila in csv.DictReader(archivo)
            }

        for nombre in (
            "revision_gemini_3_5_flash_v1.jsonl",
            "revision_gemini_3_5_flash_smoke_v1.jsonl",
            "revision_qwen_3_5_27b_smoke_v2.jsonl",
        ):
            ruta = self.BASE / nombre

            if not ruta.is_file():
                continue

            for linea in ruta.read_text(
                encoding="utf-8"
            ).splitlines():
                registro = json.loads(linea)
                objetivo = normalizar_para_evidencia(
                    filas[registro["orden_revision"]]
                )

                for evidencia in registro["evidencias_textuales"]:
                    self.assertIn(
                        normalizar_para_evidencia(evidencia),
                        objetivo,
                        f"{nombre}: {evidencia!r}",
                    )


if __name__ == "__main__":
    unittest.main()