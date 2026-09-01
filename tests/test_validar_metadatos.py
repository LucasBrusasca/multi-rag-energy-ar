"""Tests for the metadata validation configuration.

[ES] Pruebas de la configuración utilizada para validar metadatos.
"""

import copy
import json
import tempfile
import unittest
from importlib.resources import files
from pathlib import Path
from typing import cast


from multirag.ingestion.validar_metadatos import (
    cargar_configuracion_catalogo,
    validar_estructura_configuracion,
    validar_registro_metadatos,
)


RUTA_CONFIGURACION_REAL = Path(
    str(files("multirag.ingestion").joinpath("catalogo_vocabularios.json"))
)


class ValidarMetadatosTestCase(unittest.TestCase):
    """Verify loading of the metadata validation configuration.

    [ES] Verifica la carga de la configuración de validación de metadatos.
    """

    def test_carga_configuracion_catalogo_valida(self) -> None:
        configuracion_esperada = {
            "schema_version": "1.0",
            "politica_clasificacion": {
                "modo": "conjunto_abierto",
            },
            "vocabularios": {
                "dominios_documentales": [
                    "legal",
                    "impositivo",
                ],
            },
        }

        with tempfile.TemporaryDirectory() as temporal:
            ruta_configuracion = (
                Path(temporal)
                / "catalogo_vocabularios.json"
            )
            ruta_configuracion.write_text(
                json.dumps(
                    configuracion_esperada,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            configuracion_obtenida = (
                cargar_configuracion_catalogo(
                    ruta_configuracion
                )
            )

        self.assertEqual(
            configuracion_obtenida,
            configuracion_esperada,
        )



    def test_rechaza_configuracion_inexistente(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_inexistente = (
                Path(temporal)
                / "configuracion_inexistente.json"
            )

            with self.assertRaisesRegex(
                    FileNotFoundError,
                    "No existe la configuración"
            ):
                cargar_configuracion_catalogo(
                    ruta_inexistente
                )


    def test_rechaza_configuracion_con_json_invalido(
            self
    ) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_configuracion = (
                Path(temporal)
                / "configuracion_invalida.json"
            )
            ruta_configuracion.write_text(
                '{"schema_version": "1.0"',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                    ValueError,
                    "JSON inválido"
            ):
                cargar_configuracion_catalogo(
                    ruta_configuracion
                )

    def test_rechaza_configuracion_cuya_raiz_no_es_objeto(
            self
    ) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_configuracion = (
                Path(temporal)
                / "configuracion_lista.json"
            )
            ruta_configuracion.write_text(
                json.dumps(
                    [
                        "legal",
                        "impositivo",
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                    ValueError,
                    "raíz.*objeto JSON"
            ):
                cargar_configuracion_catalogo(
                    ruta_configuracion
                )

    def test_valida_estructura_configuracion_real(self) -> None:
        configuracion = cargar_configuracion_catalogo(
            RUTA_CONFIGURACION_REAL
        )

        resultado = validar_estructura_configuracion(
            configuracion
        )

        self.assertIsNone(resultado)

    def test_rechaza_clave_raiz_obligatoria_ausente(self) -> None:
        configuracion = {
            "schema_version": "1.0",
        }

        with self.assertRaisesRegex(
            ValueError,
            "taxonomia_version"
        ):
            validar_estructura_configuracion(
                configuracion
            )

    def test_rechaza_silos_experimentales_duplicados(self) -> None:
        configuracion_original = (
            cargar_configuracion_catalogo(
                RUTA_CONFIGURACION_REAL
            )
        )
        configuracion = copy.deepcopy(
            configuracion_original
        )
        alcance = cast(
            dict[str, object],
            configuracion["alcance_experimental"],
        )
        silos = cast(
            list[str],
            alcance["silos_evaluados_en_la_tesis"],
        )
        silos.append(silos[0])

        with self.assertRaisesRegex(
            ValueError,
            "silos_evaluados_en_la_tesis.*duplicados"
        ):
            validar_estructura_configuracion(
                configuracion
            )

    def test_rechaza_vocabulario_con_valores_duplicados(self) -> None:
        configuracion_original = (
            cargar_configuracion_catalogo(
                RUTA_CONFIGURACION_REAL
            )
        )
        configuracion = copy.deepcopy(
            configuracion_original
        )
        vocabularios = cast(
            dict[str, object],
            configuracion["vocabularios"],
        )
        dominios = cast(
            list[str],
            vocabularios["dominios_documentales"],
        )
        dominios.append(dominios[0])

        with self.assertRaisesRegex(
            ValueError,
            "dominios_documentales.*duplicados"
        ):
            validar_estructura_configuracion(
                configuracion
            )

    def test_rechaza_silo_fuera_del_vocabulario_de_dominios(self) -> None:
        configuracion_original = (
            cargar_configuracion_catalogo(
                RUTA_CONFIGURACION_REAL
            )
        )
        configuracion = copy.deepcopy(
            configuracion_original
        )
        alcance = cast(
            dict[str, object],
            configuracion["alcance_experimental"],
        )
        silos = cast(
            list[str],
            alcance["silos_evaluados_en_la_tesis"],
        )
        silos.append(
            "dominio_experimental_inexistente"
        )

        with self.assertRaisesRegex(
            ValueError,
            "dominio_experimental_inexistente"
        ):
            validar_estructura_configuracion(
                configuracion
            )

    def _construir_configuracion_validacion_minima(
            self
    ) -> dict[str, object]:
        return {
            "separador_multivalor": "|",
            "patrones_identidad": {},
            "formatos_fecha_permitidos": [
                "AAAA",
                "AAAA-MM",
                "AAAA-MM-DD",
            ],
            "campos_multivalor": [
                "dominios_documentales",
                "modalidades_esperadas",
            ],
            "tipos_documento_por_familia": {},
            "vocabularios": {},
            "campos_objetivos_requeridos": [
                "artifact_id",
                "archivo_referencia",
                "fuente",
                "sha256",
            ],
            "campos_canonicos_requeridos_si_incluido": [
                "titulo_oficial",
                "estado_inclusion",
            ],
            "reglas_condicionales": {
                "motivo_exclusion_requerido_si_estado": (
                    "excluido"
                ),
            },
        }

    def _construir_registro_borrador(self) -> dict[str, str]:
        huella_sha256 = "a" * 64

        return {
            "artifact_id": (
                f"ART-SHA256-{huella_sha256.upper()}"
            ),
            "archivo_referencia": "documento.pdf",
            "fuente": "documento",
            "sha256": huella_sha256,
            "titulo_oficial": "",
            "estado_inclusion": "",
            "motivo_exclusion": "",
        }

    def test_borrador_con_trazabilidad_no_tiene_errores(
            self
    ) -> None:
        configuracion = (
            self._construir_configuracion_validacion_minima()
        )
        registro = self._construir_registro_borrador()

        resultado = validar_registro_metadatos(
            registro,
            configuracion,
        )

        self.assertEqual(resultado["errores"], [])
        self.assertTrue(
            any(
                "estado_inclusion" in advertencia
                for advertencia in resultado["advertencias"]
            )
        )

    def test_rechaza_campo_objetivo_vacio(self) -> None:
        configuracion = (
            self._construir_configuracion_validacion_minima()
        )
        registro = self._construir_registro_borrador()
        registro["artifact_id"] = ""

        resultado = validar_registro_metadatos(
            registro,
            configuracion,
        )

        self.assertTrue(
            any(
                "artifact_id" in error
                for error in resultado["errores"]
            )
        )

    def test_rechaza_registro_incluido_incompleto(
            self
    ) -> None:
        configuracion = (
            self._construir_configuracion_validacion_minima()
        )
        registro = self._construir_registro_borrador()
        registro["estado_inclusion"] = "incluido"

        resultado = validar_registro_metadatos(
            registro,
            configuracion,
        )

        self.assertTrue(
            any(
                "titulo_oficial" in error
                for error in resultado["errores"]
            )
        )

    def test_rechaza_registro_incluido_con_espacio_final(
            self
    ) -> None:
        configuracion = (
            self._construir_configuracion_validacion_minima()
        )
        registro = self._construir_registro_borrador()
        registro["estado_inclusion"] = "incluido "

        resultado = validar_registro_metadatos(
            registro,
            configuracion,
        )

        self.assertTrue(
            any(
                "titulo_oficial" in error
                for error in resultado["errores"]
            )
        )

    def test_rechaza_registro_excluido_sin_motivo(
            self
    ) -> None:
        configuracion = (
            self._construir_configuracion_validacion_minima()
        )
        registro = self._construir_registro_borrador()
        registro["estado_inclusion"] = "excluido"

        resultado = validar_registro_metadatos(
            registro,
            configuracion,
        )

        self.assertTrue(
            any(
                "motivo_exclusion" in error
                for error in resultado["errores"]
            )
        )

    def _cargar_configuracion_real(
        self
    ) -> dict[str, object]:
        return cargar_configuracion_catalogo(
            RUTA_CONFIGURACION_REAL
        )

    def _construir_registro_incluido_valido(
            self
    ) -> dict[str, str]:
        huella_sha256 = "a" * 64

        return {
            "instrument_id": "INS-0001",
            "document_id": "DOC-0001",
            "artifact_id": (
                f"ART-SHA256-{huella_sha256.upper()}"
            ),
            "archivo_referencia": "resolucion.pdf",
            "fuente": "resolucion",
            "sha256": huella_sha256,
            "titulo_oficial": "Resolucion de prueba",
            "emisor_id": "EMI-0001",
            "emisor_nombre": "Secretaría de Energía",
            "tipo_documento": "resolucion",
            "fecha_documento": "2026-08-02",
            "jurisdiccion": "argentina_nacional",
            "dominios_documentales": "legal|regulatorio",
            "origen_fuente": "publica",
            "url_origen": "",
            "modalidades_esperadas": "texto|tabla",
            "estado_inclusion": "incluido",
            "motivo_exclusion": "",
            "observaciones": "",
        }

    def test_acepta_registro_incluido_valido(
            self
    ) -> None:
        configuracion = self._cargar_configuracion_real()
        registro = (
            self._construir_registro_incluido_valido()
        )

        resultado = validar_registro_metadatos(
            registro,
            configuracion,
        )

        self.assertEqual(resultado["errores"], [])
        self.assertEqual(resultado["advertencias"], [])

    def test_rechaza_identificador_con_formato_invalido(
            self
    ) -> None:
        configuracion = self._cargar_configuracion_real()
        registro = (
            self._construir_registro_incluido_valido()
        )
        registro["instrument_id"] = "INS-1"

        resultado = validar_registro_metadatos(
            registro,
            configuracion,
        )

        self.assertTrue(
            any(
                "instrument_id" in error
                for error in resultado["errores"]
            )
        )

    def test_rechaza_fecha_documento_invalida(
            self
    ) -> None:
        configuracion = self._cargar_configuracion_real()
        registro = (
            self._construir_registro_incluido_valido()
        )
        registro["fecha_documento"] = "2026-99-99"

        resultado = validar_registro_metadatos(
            registro,
            configuracion,
        )

        self.assertTrue(
            any(
                "fecha_documento" in error
                for error in resultado["errores"]
            )
        )

    def test_rechaza_dominio_no_registrado_en_incluido(
            self
    ) -> None:
        configuracion = self._cargar_configuracion_real()
        registro = (
            self._construir_registro_incluido_valido()
        )
        registro["dominios_documentales"] = (
            "legal|dominio_nuevo"
        )

        resultado = validar_registro_metadatos(
            registro,
            configuracion,
        )

        self.assertTrue(
            any(
                "dominio_nuevo" in error
                for error in resultado["errores"]
            )
        )

    def test_rechaza_valor_multivariable_duplicado(
            self
    ) -> None:
        configuracion = self._cargar_configuracion_real()
        registro = (
            self._construir_registro_incluido_valido()
        )
        registro["dominios_documentales"] = "legal|legal"

        resultado = validar_registro_metadatos(
            registro,
            configuracion,
        )

        self.assertTrue(
            any(
                "duplicado" in error
                for error in resultado["errores"]
            )
        )
