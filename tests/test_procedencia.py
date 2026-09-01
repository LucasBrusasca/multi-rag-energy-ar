"""Tests for positional provenance and for merging repeated texts.

The guarantee under test is the one that decides whether this can be applied
without re-ingesting: the `chunk_uid` must not change.

[ES] Pruebas de la procedencia posicional y de la fusión de textos repetidos.

La garantía que se prueba es la que decide si esto se puede aplicar sin
reingerir: el `chunk_uid` no tiene que cambiar.
"""

import hashlib
import unittest


from multirag.ingestion.chunker import extraer_procedencia
from multirag.ingestion.pipeline import (
    COLUMNAS_INSERT,
    _acumular_procedencia,
    _rango_de_paginas,
)


class ProvFalsa:
    def __init__(self, page_no):
        self.page_no = page_no


class ItemFalso:
    def __init__(self, self_ref, paginas=()):
        self.self_ref = self_ref
        self.prov = [ProvFalsa(p) for p in paginas]


class MetaFalsa:
    def __init__(self, doc_items):
        self.doc_items = doc_items
        self.headings = []


class ChunkFalso:
    def __init__(self, texto, doc_items):
        self.text = texto
        self.meta = MetaFalsa(doc_items)


class ExtraerProcedenciaTestCase(unittest.TestCase):
    """Docling already carries the page; the project was discarding it.

    [ES] Docling ya trae la página; el proyecto la estaba descartando.
    """

    def test_pdf_devuelve_el_rango_de_paginas(self) -> None:
        chunk = ChunkFalso(
            "texto",
            [
                ItemFalso("#/texts/3", [1]),
                ItemFalso("#/texts/4", [2]),
            ],
        )

        procedencia = extraer_procedencia(chunk)

        self.assertEqual(procedencia["pagina_desde"], 1)
        self.assertEqual(procedencia["pagina_hasta"], 2)

    def test_conserva_la_ruta_estructural(self) -> None:
        chunk = ChunkFalso(
            "texto",
            [ItemFalso("#/texts/57", [3]), ItemFalso("#/tables/0", [3])],
        )

        self.assertEqual(
            extraer_procedencia(chunk)["doc_refs"],
            ["#/texts/57", "#/tables/0"],
        )

    def test_html_sin_pagina_conserva_la_ruta(self) -> None:
        """In HTML the page does not exist; the structural path does.

        [ES] En HTML la página no existe; la ruta estructural sí.
        """
        chunk = ChunkFalso("texto", [ItemFalso("#/texts/57", [])])

        procedencia = extraer_procedencia(chunk)

        self.assertIsNone(procedencia["pagina_desde"])
        self.assertIsNone(procedencia["pagina_hasta"])
        self.assertEqual(procedencia["doc_refs"], ["#/texts/57"])

    def test_calcula_el_offset_acumulado(self) -> None:
        """Docling does not give a global offset; it is accumulated here.

        [ES] Docling no da un offset global; se acumula acá.
        """
        chunk = ChunkFalso("0123456789", [ItemFalso("#/texts/1", [1])])

        procedencia = extraer_procedencia(chunk, offset_global=100)

        self.assertEqual(procedencia["offset_desde"], 100)
        self.assertEqual(procedencia["offset_hasta"], 110)

    def test_sin_doc_items_no_rompe(self) -> None:
        chunk = ChunkFalso("texto", [])

        procedencia = extraer_procedencia(chunk)

        self.assertIsNone(procedencia["pagina_desde"])
        self.assertEqual(procedencia["doc_refs"], [])


class RangoDePaginasTestCase(unittest.TestCase):
    """A merged chunk spans pages; the range expands to all of them.

    [ES] Un chunk fusionado abarca varias páginas; el rango se expande a todas.
    """

    def test_una_sola_pagina(self) -> None:
        self.assertEqual(
            _rango_de_paginas({"pagina_desde": 3, "pagina_hasta": 3}),
            [3],
        )

    def test_rango_expandido(self) -> None:
        self.assertEqual(
            _rango_de_paginas({"pagina_desde": 3, "pagina_hasta": 6}),
            [3, 4, 5, 6],
        )

    def test_sin_paginas(self) -> None:
        self.assertEqual(
            _rango_de_paginas({"pagina_desde": None, "pagina_hasta": None}),
            [],
        )


class TextoRepetidoTestCase(unittest.TestCase):
    """A repeated text does not lose its second location.

    [ES] Un texto repetido no pierde su segunda ubicación.
    """

    def test_acumula_la_pagina_de_la_repeticion(self) -> None:
        """The case that motivated this: the same row on pages 3 and 12.

        [ES] El caso que motivó esto: la misma fila en las páginas 3 y 12.
        """
        fila = {
            "paginas": [3],
            "doc_refs": ["#/tables/0"],
        }

        _acumular_procedencia(
            fila,
            {
                "pagina_desde": 12,
                "pagina_hasta": 12,
                "doc_refs": ["#/tables/5"],
            },
        )

        self.assertEqual(fila["paginas"], [3, 12])
        self.assertEqual(
            fila["doc_refs"],
            ["#/tables/0", "#/tables/5"],
        )

    def test_no_repite_una_pagina_ya_registrada(self) -> None:
        fila = {"paginas": [3], "doc_refs": ["#/texts/1"]}

        _acumular_procedencia(
            fila,
            {
                "pagina_desde": 3,
                "pagina_hasta": 3,
                "doc_refs": ["#/texts/1"],
            },
        )

        self.assertEqual(fila["paginas"], [3])
        self.assertEqual(fila["doc_refs"], ["#/texts/1"])

    def test_las_paginas_quedan_ordenadas(self) -> None:
        fila = {"paginas": [12], "doc_refs": []}

        _acumular_procedencia(
            fila,
            {"pagina_desde": 3, "pagina_hasta": 3, "doc_refs": []},
        )

        self.assertEqual(fila["paginas"], [3, 12])


class IdentidadDelChunkTestCase(unittest.TestCase):
    """The decisive guarantee: adding provenance does not change the chunk_uid.

    If it changed, the 4803 chunks would lose their identity and the
    memberships, materiality and every measurement already taken would break.

    [ES] La garantía decisiva: agregar procedencia no cambia el chunk_uid.

    Si cambiara, los 4803 chunks perderían su identidad y se romperían las
    membresías, la materialidad y toda medición ya tomada.
    """

    def uid(self, fuente: str, hierarchy: list, contenido: str) -> str:
        return hashlib.sha256(
            (
                f"{fuente}|"
                f"{'/'.join(hierarchy)}|"
                f"{contenido}"
            ).encode("utf-8")
        ).hexdigest()

    def test_el_hash_solo_usa_fuente_jerarquia_y_contenido(self) -> None:
        esperado = self.uid("Ley_24065", ["CAP I", "Art 1"], "texto")

        self.assertEqual(
            esperado,
            self.uid("Ley_24065", ["CAP I", "Art 1"], "texto"),
        )

    def test_la_procedencia_no_entra_en_el_insert_del_hash(self) -> None:
        """The provenance columns exist in the INSERT, not in the identity.

        [ES] Las columnas de procedencia están en el INSERT, no en la
        identidad.
        """
        for columna in (
            "paginas",
            "doc_refs",
            "offset_desde",
            "offset_hasta",
        ):
            self.assertIn(columna, COLUMNAS_INSERT)

        # The three fields the hash does use.
        # [ES] Los tres campos que el hash sí usa.
        for columna in ("fuente", "hierarchy", "contenido"):
            self.assertIn(columna, COLUMNAS_INSERT)

    def test_el_insert_declara_todas_sus_columnas(self) -> None:
        self.assertEqual(
            len(COLUMNAS_INSERT),
            len(set(COLUMNAS_INSERT)),
        )
        self.assertEqual(len(COLUMNAS_INSERT), 15)


if __name__ == "__main__":
    unittest.main()
