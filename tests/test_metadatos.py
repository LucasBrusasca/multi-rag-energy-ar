"""Tests for the human-curated document metadata catalog.

[ES] Pruebas del catálogo de metadatos documentales curados humanamente.
"""

import csv
import io
import json
import tempfile
import unittest
from pathlib import Path


from multirag.ingestion.metadatos import (
    cargar_catalogo_objetivo_jsonl,
    construir_plantilla_metadatos,
    construir_registro_metadatos,
    generar_plantilla_metadatos,
    guardar_plantilla_csv,
    serializar_plantilla_csv,
)


class MetadatosTestCase(unittest.TestCase):
    """Verify the Bronze-to-Silver metadata record construction.

    [ES] Verifica la construcción del registro de metadatos Bronze-to-Silver.
    """

    def test_construye_registro_curado_vacio(self) -> None:
        huella_sha256 = "a" * 64
        artifact_id = f"ART-SHA256-{huella_sha256.upper()}"
        archivo_relativo = "subdirectorio/documento_prueba.pdf"
        fuente = "documento_prueba"

        registro_objetivo = {
            "artifact_id": artifact_id,
            "archivo_relativo": archivo_relativo,
            "fuente": fuente,
            "sha256": huella_sha256,
            "mime_firma": "application/pdf",
            "tamano_bytes": 123,
            }

        registro_metadatos = construir_registro_metadatos(
            registro_objetivo
            )

        self.assertEqual(
                registro_metadatos,
                {
                "instrument_id": "",
                "document_id": "",
                "artifact_id": artifact_id,
                "archivo_referencia": archivo_relativo,
                "fuente": fuente,
                "sha256": huella_sha256,
                "titulo_oficial": "",
                "emisor_id": "",
                "emisor_nombre": "",
                "tipo_documento": "",
                "fecha_documento": "",
                "jurisdiccion": "",
                "dominios_documentales": "",
                "origen_fuente": "",
                "url_origen": "",
                "modalidades_esperadas": "",
                "estado_inclusion": "",
                "motivo_exclusion": "",
                "observaciones": "",
                },
        )

    def test_transfiere_trazabilidad_objetiva(self) -> None:
        huella_sha256 = "a" * 64
        artifact_id = f"ART-SHA256-{huella_sha256.upper()}"
        fuente = "Decreto_1398_1992_Reglamentario_Electrico"

        registro_objetivo = {
            "artifact_id": artifact_id,
            "archivo_relativo": (
                "normativa/"
                "Decreto_1398_1992_Reglamentario_Electrico.pdf"
            ),
            "fuente": fuente,
            "sha256": huella_sha256,
        }

        registro_metadatos = construir_registro_metadatos(
            registro_objetivo
        )

        self.assertEqual(
            registro_metadatos["artifact_id"],
            artifact_id,
        )
        self.assertEqual(
            registro_metadatos["archivo_referencia"],
            registro_objetivo["archivo_relativo"],
        )
        self.assertEqual(
            registro_metadatos["fuente"],
            fuente,
        )
        self.assertEqual(
            registro_metadatos["sha256"],
            huella_sha256,
        )



    def test_rechaza_registro_sin_artifact_id(self) -> None:
        registro_objetivo = {
            "archivo_relativo": "subdirectorio/documento_prueba.pdf",
        }

        with self.assertRaisesRegex(ValueError, "artifact_id"):
            construir_registro_metadatos(registro_objetivo)

    def test_rechaza_registro_sin_archivo_relativo(self) -> None:
        artifact_id = f"ART-SHA256-{'A' * 64}"
        registro_objetivo = {
            "artifact_id": artifact_id,
        }

        with self.assertRaisesRegex(ValueError, "archivo_relativo"):
            construir_registro_metadatos(registro_objetivo)


    def test_construye_una_fila_por_artifact_id(self) -> None:
        primera_huella = "a" * 64
        segunda_huella = "b" * 64

        primer_artifact_id = (
            f"ART-SHA256-{primera_huella.upper()}"
        )
        segundo_artifact_id = (
            f"ART-SHA256-{segunda_huella.upper()}"
        )

        registros_objetivos = [
            {
                "artifact_id": primer_artifact_id,
                "archivo_relativo": "original/documento.pdf",
                "fuente":"documento",
                "sha256": primera_huella,
            },
            {
                "artifact_id": primer_artifact_id,
                "archivo_relativo": "copias/documento_copiado.pdf",
                "fuente": "documento_copiado",
                "sha256": primera_huella
            },
            {
                "artifact_id": segundo_artifact_id,
                "archivo_relativo": "otro/documento.pdf",
                "fuente": "otro_documento",
                "sha256": segunda_huella,
            },
        ]

        plantilla = construir_plantilla_metadatos(
            registros_objetivos
        )

        self.assertEqual(len(plantilla), 2)
        self.assertEqual(
            [
                registro["artifact_id"]
                for registro in plantilla
            ],
            [
                primer_artifact_id,
                segundo_artifact_id,
            ]
        )
        self.assertEqual(
            plantilla[0]["archivo_referencia"],
            "original/documento.pdf",
        )


    def test_serializa_plantilla_csv_sin_perder_contenido(self) -> None:
        huella_sha256 = "a" * 64
        artifact_id = f"ART-SHA256-{huella_sha256.upper()}"


        registro_objetivo = {
            "artifact_id": artifact_id,
            "archivo_relativo": "documentos/resolucion.pdf",
            "fuente": "resolucion",
            "sha256": huella_sha256
        }
        registro_metadatos = construir_registro_metadatos(
            registro_objetivo
        )
        registro_metadatos["titulo_oficial"] = (
            "Resolución de energía, transporte y distribución"
        )
        registro_metadatos["emisor_nombre"] = (
            "Secretaría de Energía"
        )

        texto_csv = serializar_plantilla_csv(
            [registro_metadatos]
        )

        lector = csv.DictReader(io.StringIO(texto_csv))
        filas = list(lector)

        self.assertEqual(len(filas), 1)
        self.assertEqual(
            filas[0]["titulo_oficial"],
            "Resolución de energía, transporte y distribución",
        )
        self.assertEqual(
            filas[0]["emisor_nombre"],
            "Secretaría de Energía",
        )

    def test_guarda_plantilla_csv_atomicamente(self) -> None:
        huella_sha256 = "a" * 64
        artifact_id = f"ART-SHA256-{huella_sha256.upper()}"
        archivo_relativo = "documentos/resolucion.pdf"
        titulo_oficial = "Resolución de energía"

        with tempfile.TemporaryDirectory() as temporal:
            directorio_temporal = Path(temporal)
            ruta_salida = (
                directorio_temporal
                / "catalogos"
                / "metadatos_curados.csv"
            )

            registro_objetivo = {
                "artifact_id": artifact_id,
                "archivo_relativo": archivo_relativo,
                "fuente": "resolucion",
                "sha256": huella_sha256
            }
            registro_metadatos = construir_registro_metadatos(
                registro_objetivo
            )
            registro_metadatos["titulo_oficial"] = titulo_oficial
            registros = [registro_metadatos]

            ruta_guardada = guardar_plantilla_csv(
                registros_metadatos=registros,
                ruta_salida=ruta_salida,
            )

            ruta_temporal = ruta_salida.resolve().with_name(
                f".{ruta_salida.name}.tmp"
            )
            contenido_esperado = serializar_plantilla_csv(
                registros
            )
            contenido_guardado = ruta_salida.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                ruta_guardada,
                ruta_salida.resolve(),
            )
            self.assertTrue(ruta_salida.is_file())
            self.assertEqual(
                contenido_guardado,
                contenido_esperado,
            )
            self.assertFalse(ruta_temporal.exists())

    def test_no_sobrescribe_plantilla_csv_existente(self) -> None:
        contenido_curado = "contenido curado por una persona\n"
        huella_sha256= "a" * 64
        artifact_id = f"ART-SHA256-{huella_sha256.upper()}"

        with tempfile.TemporaryDirectory() as temporal:
            ruta_salida = (
                Path(temporal)
                / "metadatos_curados.csv"
            )
            ruta_salida.write_text(
                contenido_curado,
                encoding="utf-8",
                newline="\n",
            )

            registro_objetivo = {
                "artifact_id": artifact_id,
                "archivo_relativo": "documentos/resolucion.pdf",
                "fuente": "resolucion",
                "sha256": huella_sha256,
            }
            registro_metadatos = construir_registro_metadatos(
                registro_objetivo
            )

            with self.assertRaises(FileExistsError):
                guardar_plantilla_csv(
                    registros_metadatos=[registro_metadatos],
                    ruta_salida=ruta_salida
                )

            self.assertEqual(
                ruta_salida.read_text(encoding="utf-8"),
                contenido_curado,
            )


    def test_genera_plantilla_desde_catalogo_objetivo(self) -> None:
        primera_huella = "a" * 64
        segunda_huella = "b" * 64

        primer_artifact_id = (
            f"ART-SHA256-{primera_huella.upper()}"
        )
        segundo_artifact_id = (
            f"ART-SHA256-{segunda_huella.upper()}"
        )


        registros_objetivos = [
            {
                "artifact_id": primer_artifact_id,
                "archivo_relativo": "original/documento.pdf",
                "fuente": "documento",
                "sha256": primera_huella,
            },
            {
                "artifact_id": segundo_artifact_id,
                "archivo_relativo": "otro/documento.pdf",
                "fuente": "otro_documento",
                "sha256": segunda_huella,
            }
        ]
        contenido_catalogo = "".join(
            json.dumps(
                registro,
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n"
            for registro in registros_objetivos
        )

        with tempfile.TemporaryDirectory() as temporal:
            directorio = Path(temporal)
            ruta_catalogo = directorio / "inventario.jsonl"
            ruta_salida = directorio / "metadatos.csv"

            ruta_catalogo.write_text(
                contenido_catalogo,
                encoding="utf-8",
                newline="\n",
            )

            ruta_generada = generar_plantilla_metadatos(
                ruta_catalogo=ruta_catalogo,
                ruta_salida=ruta_salida,
            )

            with ruta_generada.open(
                "r",
                encoding="utf-8",
                newline="",
            ) as archivo:
                filas = list(csv.DictReader(archivo))

            self.assertEqual(
                ruta_generada,
                ruta_salida.resolve(),
            )
            self.assertEqual(len(filas), 2)
            self.assertEqual(
                filas[0]["artifact_id"],
                primer_artifact_id,
            )
            self.assertEqual(
                filas[1]["artifact_id"],
                segundo_artifact_id,
            )
            self.assertEqual(filas[0]["document_id"], "")
            self.assertEqual(filas[1]["document_id"], "")


    def test_carga_catalogo_objetivo_jsonl_utf8_con_bom(self) -> None:
        huella_sha256 = "a" * 64

        registro_esperado = {
            "artifact_id": (
                f"ART-SHA256-{huella_sha256.upper()}"
            ),
            "archivo_relativo": (
                "normativa/resolución_energía.pdf"
            ),
            "fuente": "resolución_energía",
            "sha256": huella_sha256,
            "mime_firma": "application/pdf",
        }
        contenido_jsonl = (
            json.dumps(
                registro_esperado,
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n"
        )

        with tempfile.TemporaryDirectory() as temporal:
            ruta_catalogo = (
                Path(temporal)
                / "inventario_objetivo.jsonl"
            )
            ruta_catalogo.write_text(
                contenido_jsonl,
                encoding="utf-8-sig",
                newline="\n",
            )

            registros_cargados = cargar_catalogo_objetivo_jsonl(
                ruta_catalogo
            )

            self.assertEqual(
                registros_cargados,
                [registro_esperado],
            )


    def test_rechaza_catalogo_objetivo_inexistente(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_inexistente = (
                Path(temporal)
                / "inventario_inexistente.jsonl"
            )

            with self.assertRaisesRegex(
                FileNotFoundError,
                "No existe el catálogo objetivo",
            ):
                cargar_catalogo_objetivo_jsonl(
                    ruta_inexistente
                )


    def test_rechaza_json_invalido_indicando_linea(self) -> None:
        huella_sha256 = "a" * 64

        registro_valido = {
            "artifact_id": (
                f"ART-SHA256-{huella_sha256.upper()}"
            ),
            "archivo_relativo": "documentos/valido.pdf",
            "fuente": "valido",
            "sha256": huella_sha256,
        }
        primera_linea = json.dumps(
            registro_valido,
            sort_keys=True,
        )
        segunda_linea_invalida = (
            '{"artifact_id": "registro sin cierre"'
        )
        contenido_jsonl = (
            primera_linea
            + "\n"
            + segunda_linea_invalida
            + "\n"
        )

        with tempfile.TemporaryDirectory() as temporal:
            ruta_catalogo = (
                Path(temporal)
                / "inventario_con_error.jsonl"
            )
            ruta_catalogo.write_text(
                contenido_jsonl,
                encoding="utf-8",
                newline="\n",
            )

            with self.assertRaisesRegex(
                ValueError,
                "línea 2",
            ):
                cargar_catalogo_objetivo_jsonl(
                    ruta_catalogo
                )

    def test_rechaza_linea_json_que_no_sea_objeto(self) -> None:
        contenido_jsonl = json.dumps(
            ["esto", "es", "una", "lista"]
        )

        with tempfile.TemporaryDirectory() as temporal:
            ruta_catalogo = (
                Path(temporal)
                / "inventario_con_lista.jsonl"
            )
            ruta_catalogo.write_text(
                contenido_jsonl + "\n",
                encoding="utf-8",
                newline="\n",
            )

            with self.assertRaisesRegex(
                ValueError,
                "Línea: 1",
            ):
                cargar_catalogo_objetivo_jsonl(
                    ruta_catalogo
                )


if __name__ == "__main__":
    unittest.main()
