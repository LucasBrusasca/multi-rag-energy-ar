"""Tests for the objective and format-neutral corpus catalog.


[ES] Pruebas del catálogo objetivo y neutral respecto del formato.
"""


import hashlib
import json
import tempfile
import unittest
from pathlib import Path


from multirag.ingestion.catalogo import (
    calcular_sha256,
    construir_catalogo_objetivo,
    construir_artifact_id,
    construir_registro_fuente,
    detectar_mime_por_firma,
    listar_fuentes_directorio,
    guardar_catalogo_jsonl,
    serializar_catalogo_jsonl
)


class CatalogoTestCase(unittest.TestCase):
    """Verify deterministic and format-neutral catalog behavior.

    [ES] verifica el comportamiento determinista y neutral del catálogo.
    """


    def test_list_fuentes_recursivamente_y_en_orden(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            directorio = Path(temporal)
            subdirectorio = directorio / "subdirectorio"
            subdirectorio.mkdir()

            (directorio / "B.txt").write_bytes(b"b")
            (directorio / "a.pdf").write_bytes(b"a")
            (directorio / "sin_extension").write_bytes(b"sin extension")
            (subdirectorio / "c.xlsx").write_bytes(b"c")
            (subdirectorio / "datos.zzz").write_bytes(b"desconocido")

            fuentes = listar_fuentes_directorio(directorio)
            rutas = [
                fuente.relative_to(directorio).as_posix()
                for fuente in fuentes
            ]


            self.assertEqual(
                rutas,
                [
                    "a.pdf",
                    "B.txt",
                    "sin_extension",
                    "subdirectorio/c.xlsx",
                    "subdirectorio/datos.zzz"
                ]
            )

    def test_catalogo_conserva_ocurrencias_del_mismo_contenido(
            self
    ) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            directorio = Path(temporal)
            contenido_compartido = b"documento repetido"

            primera_ruta = directorio / "documento_original.pdf"
            segunda_ruta = directorio / "copia_documento.txt"

            primera_ruta.write_bytes(contenido_compartido)
            segunda_ruta.write_bytes(contenido_compartido)

            registros = construir_catalogo_objetivo(directorio)

            self.assertEqual(len(registros),2)
            self.assertEqual(
                [
                    registro["archivo_relativo"]
                    for registro in registros
                ],
                [
                    "copia_documento.txt",
                    "documento_original.pdf"
                ]
            )
            self.assertEqual(
                registros[0]["artifact_id"],
                registros[1]["artifact_id"]
            )

    def test_serializa_catalogo_jsonl_deterministicamente(self) -> None:
        primer_registro = {
            "nombre_archivo": "regulación.pdf",
            "tamano_bytes": 123,
            "mime_firma": "application/pdf"
        }
        mismo_registro_con_otro_orden = {
            "mime_firma": "application/pdf",
            "nombre_archivo": "regulación.pdf",
            "tamano_bytes": 123
        }

        primera_serializacion = serializar_catalogo_jsonl(
            [primer_registro]
        )
        segunda_serializacion = serializar_catalogo_jsonl(
            [mismo_registro_con_otro_orden]
        )

        self.assertEqual(
            primera_serializacion,
            segunda_serializacion
        )
        self.assertTrue(primera_serializacion.endswith("\n"))
        self.assertIn("regulación.pdf", primera_serializacion)
        self.assertEqual(
            json.loads(primera_serializacion),
            primer_registro
        )
        self.assertEqual(serializar_catalogo_jsonl([]), "")


    def test_guarda_catalogo_jsonl_atomicamente(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            directorio = Path(temporal)
            ruta_salida = (
                directorio
                / "catalogos"
                / "inventario_objetivo.jsonl"
            )
            registros = [
                {
                    "nombre_archivo": "regulación.pdf",
                    "mime_firma": "application/pdf",
                    "tamano_bytes": 123
                }
            ]


            ruta_guardada = guardar_catalogo_jsonl(
                registros=registros,
                ruta_salida=ruta_salida
            )


            ruta_temporal = ruta_salida.resolve().with_name(
                f".{ruta_salida.name}.tmp"
            )

            self.assertEqual(
                ruta_guardada,
                ruta_salida.resolve()
            )
            self.assertTrue(ruta_salida.is_file())
            self.assertEqual(
                ruta_salida.read_text(encoding="utf-8"),
                serializar_catalogo_jsonl(registros)
            )
            self.assertFalse(ruta_temporal.exists())


    def test_calcula_sha256_deterministicamente(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "fuente.bin"
            contenido = b"contenido de prueba multimodal"
            ruta.write_bytes(contenido)


            huella_esperada = hashlib.sha256(contenido).hexdigest()
            primera_huella = calcular_sha256(ruta)
            segunda_huella = calcular_sha256(ruta)

            self.assertEqual(primera_huella, huella_esperada)
            self.assertEqual(segunda_huella, huella_esperada)
            self.assertEqual(primera_huella, segunda_huella)


    def test_construye_artifact_id_sin_truncar_hash(self) -> None:
        contenido = b"identidad documental"
        huella = hashlib.sha256(contenido).hexdigest()

        artifact_id = construir_artifact_id(huella)
        nombre_algoritmo = hashlib.sha256().name.upper()


        self.assertEqual(
            artifact_id,
            f"ART-{nombre_algoritmo}-{huella.upper()}"
        )

    def test_artifact_id_depende_del_contenido(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            directorio = Path(temporal)
            contenido_compartido = b"mismo contenido documento"

            primera_ruta = directorio / "primera_fuente.pdf"
            segunda_ruta = directorio / "otro_nombre.txt"
            tercera_ruta = directorio / "contenido_diferente.bin"

            primera_ruta.write_bytes(contenido_compartido)
            segunda_ruta.write_bytes(contenido_compartido)
            tercera_ruta.write_bytes(b"contenido documental diferente")

            primer_registro = construir_registro_fuente(
                ruta=primera_ruta,
                directorio_base=directorio
            )
            segundo_registro = construir_registro_fuente(
                ruta=segunda_ruta,
                directorio_base=directorio
            )
            tercer_registro = construir_registro_fuente(
                ruta=tercera_ruta,
                directorio_base=directorio
            )

            self.assertEqual(
                primer_registro["artifact_id"],
                segundo_registro["artifact_id"]
            )
            self.assertNotEqual(
                primer_registro["artifact_id"],
                tercer_registro["artifact_id"]
            )



    def test_rechaza_huellas_sha256_invalidas(self) -> None:
        huella_valida = hashlib.sha256(b"valido").hexdigest()


        casos_invalidos = {
            "longitud incorrecta": "abc",
            "caracter no hexadecimal": "g" * len(huella_valida),
            "espacio interno": (
                huella_valida[:10]
                + " "
                + huella_valida[11:]
            )
        }

        for descripcion, huella in casos_invalidos.items():
            with self.subTest(descripcion=descripcion):
                with self.assertRaises(ValueError):
                    construir_artifact_id(huella)


    def test_detecta_firma_aunque_extension_sea_incorrecta(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "documento.txt"
            ruta.write_bytes(b"%PDF-1.4\n%contenido de prueba\n")


            mime = detectar_mime_por_firma(ruta)


            self.assertEqual(mime, "application/pdf")


    def test_conserva_fuente_con_firma_desconocida(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            directorio = Path(temporal)
            ruta = directorio / "fuente_sin_extension"
            contenido = b"contenido sin firma binaria reconocible"
            ruta.write_bytes(contenido)

            registro = construir_registro_fuente(
                ruta=ruta,
                directorio_base=directorio
            )

            self.assertEqual(
                registro["archivo_relativo"],
                "fuente_sin_extension"
            )
            self.assertEqual(
                registro["nombre_archivo"],
                "fuente_sin_extension"
            )
            self.assertEqual(registro["extension"], "")
            self.assertIsNone(registro["mime_firma"])
            self.assertEqual(
                registro["tamano_bytes"],
                len(contenido)
            )


    def test_construye_registro_objetivo(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            directorio = Path(temporal)
            subdirectorio = directorio / "documentos"
            subdirectorio.mkdir()

            ruta = subdirectorio / "BALANCE.PDF"
            contenido = b"%PDF-1.4\n%balance de prueba\n"
            ruta.write_bytes(contenido)

            huella_esperada = hashlib.sha256(contenido).hexdigest()
            nombre_algoritmo = hashlib.sha256().name.upper()
            artifact_id_esperado = (
                f"ART-{nombre_algoritmo}-{huella_esperada.upper()}"
            )

            registro = construir_registro_fuente(
                ruta=ruta,
                directorio_base=directorio
            )

            self.assertEqual(
                registro["artifact_id"],
                artifact_id_esperado
            )

            self.assertEqual(registro["fuente"], "BALANCE")
            self.assertEqual(
                registro["nombre_archivo"],
                "BALANCE.PDF"
            )
            self.assertEqual(
                registro["archivo_relativo"],
                "documentos/BALANCE.PDF"
            )
            self.assertEqual(registro["extension"], ".pdf")
            self.assertEqual(
                registro["mime_firma"],
                "application/pdf"
            )
            self.assertEqual(
                registro["tamano_bytes"],
                len(contenido)
            )
            self.assertEqual(
                registro["sha256"],
                huella_esperada
            )


    def test_rechaza_archivo_fuera_del_directorio_base(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            directorio_base = raiz / "corpus"
            directorio_base.mkdir()


            ruta_externa = raiz / "externo.pdf"
            ruta_externa.write_bytes(b"%PDF-1.4\n")


            with self.assertRaises(ValueError):
                construir_registro_fuente(
                    ruta=ruta_externa,
                    directorio_base=directorio_base
                )


    def test_rechaza_ruta_con_retroceso_fuera_del_directorio(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            directorio_base = raiz / "corpus"
            directorio_base.mkdir()

            ruta_externa = raiz / "externo.pdf"
            ruta_externa.write_bytes(b"%PDF-1.4\n")

            ruta_con_retroceso = (
                directorio_base / ".." / "externo.pdf"
            )

            self.assertTrue(ruta_con_retroceso.is_file())

            with self.assertRaises(ValueError):
                construir_registro_fuente(
                    ruta=ruta_con_retroceso,
                    directorio_base=directorio_base
                )


if __name__ == "__main__":
    unittest.main()
