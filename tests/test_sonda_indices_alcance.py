"""Tests for the plan classifier of the scope index probe.

The plan texts are the real ones produced by the snapshot on 23-ago-2026,
abbreviated in the vector literal only. They exist so that the classifier
cannot regress to the substring heuristic that first misread them.

[ES] Pruebas del clasificador de planes de la sonda de índices del alcance.

Los textos de plan son los reales producidos por el snapshot el 23-ago-2026,
abreviados solamente en el literal del vector. Existen para que el clasificador
no pueda volver a la heurística de subcadena que los leyó mal al principio.
"""

import unittest


from scripts.diagnostics.sonda_indices_alcance import (
    caminos_de_acceso,
    clasificar_plan,
    ordena_por_distancia,
    usa_indice_vectorial,
)


INDICES_VECTORIALES = (
    "chunk_contable_hnsw",
    "chunk_financiero_hnsw",
    "chunks_impositivo_hnsw",
    "chunks_legal_hnsw",
)


# A0 filtered by silo: btree on silo, then an explicit sort by distance.
# [ES] A0 filtrada por silo: btree sobre silo y luego orden explícito por
# distancia.
PLAN_A0_POR_SILO = """Limit  (cost=1215.56..1215.57 rows=3 width=1119)
  ->  Sort  (cost=1215.56..1217.63 rows=828 width=1119)
        Sort Key: ((embedding <=> '[0,0,0]'::vector))
        ->  Bitmap Heap Scan on chunks  (cost=18.70..1204.86 rows=828 width=1119)
              Recheck Cond: (silo = 'legal'::text)
              ->  Bitmap Index Scan on chunks_silo_idx  (cost=0.00..18.49 rows=828 width=0)
                    Index Cond: (silo = 'legal'::text)"""


PLAN_A0_MONOLITICA = """Limit  (cost=1379.05..1379.06 rows=3 width=1119)
  ->  Sort  (cost=1379.05..1389.98 rows=4373 width=1119)
        Sort Key: ((embedding <=> '[0,0,0]'::vector))
        ->  Seq Scan on chunks  (cost=0.00..1322.53 rows=4373 width=1119)"""


PLAN_E1_HERMANOS = """Limit  (cost=8.24..8.24 rows=1 width=1119)
  ->  Sort  (cost=8.24..8.24 rows=1 width=1119)
        Sort Key: ((embedding <=> '[0,0,0]'::vector))
        ->  Index Scan using chunks_document_id_idx on chunks  (cost=0.28..8.23 rows=1 width=1119)
              Index Cond: (document_id = ANY ('{DOC-EJEMPLO}'::text[]))"""


# What an approximate search actually looks like: the vector index serves the
# ordering and there is no Sort node.
# [ES] Cómo se ve realmente una búsqueda aproximada: el índice vectorial sirve
# el ordenamiento y no hay nodo Sort.
PLAN_APROXIMADO = """Limit  (cost=0.42..12.10 rows=3 width=1119)
  ->  Index Scan using chunks_legal_hnsw on chunks  (cost=0.42..3245.11 rows=828 width=1119)
        Order By: (embedding <=> '[0,0,0]'::vector)"""


class ClasificarPlanTestCase(unittest.TestCase):
    """An explicit Sort by distance means exact search.

    [ES] Un Sort explícito por distancia significa búsqueda exacta.
    """

    def test_a0_por_silo_es_exacta(self) -> None:
        clasificacion = clasificar_plan(
            PLAN_A0_POR_SILO,
            INDICES_VECTORIALES,
        )

        self.assertTrue(
            clasificacion.startswith("EXACTA"),
            clasificacion,
        )

    def test_bitmap_index_scan_no_es_busqueda_vectorial(self) -> None:
        """`Bitmap Index Scan on chunks_silo_idx` contains "Index Scan" and has
        nothing to do with HNSW.

        [ES] `Bitmap Index Scan on chunks_silo_idx` contiene "Index Scan" y no
        tiene nada que ver con HNSW.
        """
        self.assertFalse(
            usa_indice_vectorial(
                PLAN_A0_POR_SILO,
                INDICES_VECTORIALES,
            )
        )

    def test_a0_monolitica_es_exacta(self) -> None:
        clasificacion = clasificar_plan(
            PLAN_A0_MONOLITICA,
            INDICES_VECTORIALES,
        )

        self.assertTrue(
            clasificacion.startswith("EXACTA"),
            clasificacion,
        )

    def test_hermanos_de_e1_es_exacta(self) -> None:
        clasificacion = clasificar_plan(
            PLAN_E1_HERMANOS,
            INDICES_VECTORIALES,
        )

        self.assertTrue(
            clasificacion.startswith("EXACTA"),
            clasificacion,
        )

    def test_las_tres_formas_del_snapshot_coinciden(self) -> None:
        """No asymmetry between arms on this snapshot.

        [ES] Sin asimetría entre brazos sobre este snapshot.
        """
        metodos = {
            clasificar_plan(plan, INDICES_VECTORIALES).split(" —")[0]
            for plan in (
                PLAN_A0_POR_SILO,
                PLAN_A0_MONOLITICA,
                PLAN_E1_HERMANOS,
            )
        }

        self.assertEqual(len(metodos), 1)

    def test_reconoce_una_busqueda_aproximada(self) -> None:
        clasificacion = clasificar_plan(
            PLAN_APROXIMADO,
            INDICES_VECTORIALES,
        )

        self.assertTrue(
            clasificacion.startswith("APROXIMADA"),
            clasificacion,
        )
        self.assertFalse(
            ordena_por_distancia(PLAN_APROXIMADO)
        )

    def test_sin_indices_vectoriales_declarados_no_inventa_aproximacion(
        self,
    ) -> None:
        clasificacion = clasificar_plan(PLAN_APROXIMADO, ())

        self.assertFalse(clasificacion.startswith("APROXIMADA"))

    def test_nombra_el_camino_de_acceso(self) -> None:
        self.assertIn(
            "Seq Scan on chunks",
            clasificar_plan(
                PLAN_A0_MONOLITICA,
                INDICES_VECTORIALES,
            ),
        )
        self.assertIn(
            "Bitmap Index Scan on chunks_silo_idx",
            caminos_de_acceso(PLAN_A0_POR_SILO),
        )


if __name__ == "__main__":
    unittest.main()
