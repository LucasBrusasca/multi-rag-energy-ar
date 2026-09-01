"""Tests for the Silver membership producer.

It never connects to PostgreSQL: it only reads a JSONL artifact and writes SQL.

[ES] Pruebas del productor de membresías Silver.

Nunca se conecta a PostgreSQL: solo lee un artefacto JSONL y escribe SQL.
"""

import json
import tempfile
import unittest
from pathlib import Path


from multirag.ingestion.membresias import (
    ErrorDeMembresias,
    cargar_propuestas,
    conjunto_por_cobertura,
    conjunto_por_margen,
    conjunto_por_umbral,
    filas_de_materialidad,
    filas_de_membresia,
    metodo_de_asignacion,
    sentencias_sql,
)


UID_A = "a" * 64
UID_B = "b" * 64
UID_C = "c" * 64


VERSIONES = {
    "assignment_version": "silver-2026-08-23",
    "taxonomy_version": "taxonomia-v1",
    "assignment_method": "qwen3:8b",
}


def propuesta(
    uid: str,
    dominios,
    materialidad: str = "sustantivo",
    estado: str = "asignado",
    confianza=0.8,
) -> dict:
    return {
        "chunk_uid": uid,
        "dominios_propuestos": dominios,
        "materialidad_propuesta": materialidad,
        "estado_asignacion": estado,
        "confianza_autodeclarada": confianza,
        "modelo_resuelto": "qwen3:8b",
    }


class CargarPropuestasTestCase(unittest.TestCase):
    """The artifact is validated before producing anything.

    [ES] El artefacto se valida antes de producir nada.
    """

    def escribir(self, lineas) -> Path:
        directorio = tempfile.mkdtemp()
        ruta = Path(directorio) / "propuestas.jsonl"
        ruta.write_text(
            "".join(
                json.dumps(linea, ensure_ascii=False) + "\n"
                for linea in lineas
            ),
            encoding="utf-8",
            newline="\n",
        )
        return ruta

    def test_carga_registros_validos(self) -> None:
        ruta = self.escribir(
            [
                propuesta(UID_A, ["legal"]),
                propuesta(UID_B, []),
            ]
        )

        registros = cargar_propuestas(ruta)

        self.assertEqual(len(registros), 2)

    def test_rechaza_chunk_uid_invalido(self) -> None:
        ruta = self.escribir([propuesta("no-es-un-uid", ["legal"])])

        with self.assertRaises(ErrorDeMembresias) as contexto:
            cargar_propuestas(ruta)

        self.assertIn("chunk_uid", str(contexto.exception))

    def test_rechaza_chunk_uid_repetido(self) -> None:
        ruta = self.escribir(
            [
                propuesta(UID_A, ["legal"]),
                propuesta(UID_A, ["impositivo"]),
            ]
        )

        with self.assertRaises(ErrorDeMembresias) as contexto:
            cargar_propuestas(ruta)

        self.assertIn("repetido", str(contexto.exception))

    def test_rechaza_artefacto_vacio(self) -> None:
        ruta = self.escribir([])

        with self.assertRaises(ErrorDeMembresias):
            cargar_propuestas(ruta)

    def test_rechaza_artefacto_inexistente(self) -> None:
        with self.assertRaises(ErrorDeMembresias):
            cargar_propuestas(Path("no_existe.jsonl"))


class FilasDeMembresiaTestCase(unittest.TestCase):
    """Zero, one or several domains per chunk, without duplicating the chunk.

    [ES] Cero, uno o varios dominios por chunk, sin duplicar el chunk.
    """

    def test_un_chunk_multidominio_produce_una_fila_por_dominio(self) -> None:
        filas = filas_de_membresia(
            [propuesta(UID_A, ["legal", "impositivo"])],
            **VERSIONES,
        )

        self.assertEqual(len(filas), 2)
        self.assertEqual(
            {fila["chunk_uid"] for fila in filas},
            {UID_A},
        )
        self.assertEqual(
            [fila["domain_id"] for fila in filas],
            ["legal", "impositivo"],
        )

    def test_chunk_sin_dominios_no_produce_filas(self) -> None:
        filas = filas_de_membresia(
            [
                propuesta(
                    UID_A,
                    [],
                    materialidad="administrativo_no_material",
                    estado="sin_dominio_por_no_materialidad",
                )
            ],
            **VERSIONES,
        )

        self.assertEqual(filas, [])

    def test_las_filas_son_silver(self) -> None:
        filas = filas_de_membresia(
            [propuesta(UID_A, ["legal"])],
            **VERSIONES,
        )

        self.assertEqual(
            filas[0]["review_status"],
            "automatic",
        )
        self.assertEqual(
            filas[0]["score_kind"],
            "confianza_autodeclarada_llm",
        )
        self.assertEqual(filas[0]["score"], 0.8)

    def test_score_ausente_deja_score_kind_nulo(self) -> None:
        registro = propuesta(UID_A, ["legal"])
        del registro["confianza_autodeclarada"]

        filas = filas_de_membresia([registro], **VERSIONES)

        self.assertIsNone(filas[0]["score"])
        self.assertIsNone(filas[0]["score_kind"])

    def test_rechaza_dominio_desconocido(self) -> None:
        with self.assertRaises(ErrorDeMembresias) as contexto:
            filas_de_membresia(
                [propuesta(UID_A, ["energetico"])],
                **VERSIONES,
            )

        self.assertIn("energetico", str(contexto.exception))

    def test_rechaza_estado_incoherente_con_los_dominios(self) -> None:
        with self.assertRaises(ErrorDeMembresias) as contexto:
            filas_de_membresia(
                [
                    propuesta(
                        UID_A,
                        ["legal"],
                        estado="sin_dominio_por_no_materialidad",
                    )
                ],
                **VERSIONES,
            )

        self.assertIn("estado", str(contexto.exception))

    def test_exige_version_explicita(self) -> None:
        argumentos = dict(VERSIONES)
        argumentos["assignment_version"] = ""

        with self.assertRaises(ErrorDeMembresias) as contexto:
            filas_de_membresia(
                [propuesta(UID_A, ["legal"])],
                **argumentos,
            )

        self.assertIn(
            "assignment_version",
            str(contexto.exception),
        )

    def test_rechaza_version_con_caracteres_peligrosos(self) -> None:
        argumentos = dict(VERSIONES)
        argumentos["assignment_version"] = "v1'); DROP TABLE chunks; --"

        with self.assertRaises(ErrorDeMembresias):
            filas_de_membresia(
                [propuesta(UID_A, ["legal"])],
                **argumentos,
            )

    def test_lee_el_artefacto_de_revision_ciega(self) -> None:
        registro = {
            "chunk_uid": UID_A,
            "dominios_revision": ["contable"],
            "materialidad_revision": "sustantivo",
            "estado_revision": "asignado",
            "confianza_autodeclarada": 1.0,
            "modelo_resuelto": "gemini-3.5-flash",
        }

        filas = filas_de_membresia(
            [registro],
            assignment_version="silver-1",
            taxonomy_version="taxonomia-v1",
            assignment_method=metodo_de_asignacion([registro]),
        )

        self.assertEqual(filas[0]["domain_id"], "contable")
        self.assertEqual(
            filas[0]["assignment_method"],
            "gemini-3.5-flash",
        )


class FilasDeMaterialidadTestCase(unittest.TestCase):
    """One row per chunk and version: materiality is not per domain.

    [ES] Una fila por chunk y versión: la materialidad no es por dominio.
    """

    def test_una_fila_por_chunk_aunque_tenga_dos_dominios(self) -> None:
        filas = filas_de_materialidad(
            [propuesta(UID_A, ["legal", "impositivo"])],
            materiality_version="materialidad-v1",
            assignment_method="qwen3:8b",
        )

        self.assertEqual(len(filas), 1)
        self.assertEqual(
            filas[0]["materiality"],
            "sustantivo",
        )

    def test_rechaza_materialidad_fuera_del_vocabulario(self) -> None:
        with self.assertRaises(ErrorDeMembresias) as contexto:
            filas_de_materialidad(
                [propuesta(UID_A, ["legal"], materialidad="dudoso")],
                materiality_version="materialidad-v1",
                assignment_method="qwen3:8b",
            )

        self.assertIn("dudoso", str(contexto.exception))

    def test_chunk_sin_materialidad_se_omite(self) -> None:
        registro = propuesta(UID_A, ["legal"])
        del registro["materialidad_propuesta"]

        filas = filas_de_materialidad(
            [registro],
            materiality_version="materialidad-v1",
            assignment_method="qwen3:8b",
        )

        self.assertEqual(filas, [])


class ReglaDelConjuntoTestCase(unittest.TestCase):
    """A1 produces one, several or zero domains, never a fixed top-2.

    [ES] A1 produce uno, varios o cero dominios, nunca un top-2 fijo.
    """

    # A sharp distribution: the classifier is sure.
    # [ES] Distribución puntiaguda: el clasificador está seguro.
    PUNTIAGUDA = {
        "legal": 0.90,
        "impositivo": 0.05,
        "contable": 0.03,
        "financiero": 0.02,
    }

    # A flat one: the chunk sits between domains.
    # [ES] Plana: el chunk está entre dominios.
    PLANA = {
        "legal": 0.30,
        "impositivo": 0.28,
        "contable": 0.22,
        "financiero": 0.20,
    }

    def test_cobertura_devuelve_uno_si_la_distribucion_es_puntiaguda(
        self,
    ) -> None:
        self.assertEqual(
            conjunto_por_cobertura(self.PUNTIAGUDA, 0.70),
            ["legal"],
        )

    def test_cobertura_abre_mas_dominios_si_la_distribucion_es_plana(
        self,
    ) -> None:
        conjunto = conjunto_por_cobertura(self.PLANA, 0.70)

        self.assertEqual(
            conjunto,
            ["legal", "impositivo", "contable"],
        )

    def test_cobertura_ordena_por_score_descendente(self) -> None:
        self.assertEqual(
            conjunto_por_cobertura(self.PLANA, 0.99)[0],
            "legal",
        )

    def test_umbral_puede_devolver_cero_dominios(self) -> None:
        self.assertEqual(
            conjunto_por_umbral(self.PLANA, 0.50),
            [],
        )

    def test_umbral_puede_devolver_varios(self) -> None:
        self.assertEqual(
            conjunto_por_umbral(self.PLANA, 0.25),
            ["legal", "impositivo"],
        )

    def test_ignora_claves_que_no_son_dominios(self) -> None:
        scores = dict(self.PUNTIAGUDA)
        scores["fuera_de_ontologia"] = 0.99

        self.assertEqual(
            conjunto_por_umbral(scores, 0.5),
            ["legal"],
        )

    def test_rechaza_parametros_fuera_de_rango(self) -> None:
        for valor in (0.0, -0.1, 1.5):
            with self.assertRaises(ErrorDeMembresias):
                conjunto_por_umbral(self.PLANA, valor)

            with self.assertRaises(ErrorDeMembresias):
                conjunto_por_cobertura(self.PLANA, valor)

    # Two top scores that are both high and close, and two clearly lower: the
    # shape of genuinely two-domain content.
    # [ES] Dos scores altos y cercanos, y dos claramente menores: la forma del
    # contenido genuinamente bidominio.
    BIDOMINIO = {
        "legal": 0.46,
        "impositivo": 0.44,
        "contable": 0.05,
        "financiero": 0.05,
    }

    def test_margen_da_un_dominio_si_el_ganador_esta_adelante(self) -> None:
        self.assertEqual(
            conjunto_por_margen(self.PUNTIAGUDA, 0.05),
            ["legal"],
        )

    def test_margen_abre_solo_los_indistinguibles_del_ganador(self) -> None:
        self.assertEqual(
            conjunto_por_margen(self.BIDOMINIO, 0.05),
            ["legal", "impositivo"],
        )

    def test_margen_nunca_pierde_la_etiqueta_a0(self) -> None:
        """The winner is always in the set, for any margin.

        [ES] El ganador siempre está en el conjunto, con cualquier margen.
        """
        for scores in (
            self.PUNTIAGUDA,
            self.PLANA,
            self.BIDOMINIO,
        ):
            ganador = max(scores, key=scores.get)

            for margen in (0.0, 0.01, 0.05, 0.2, 0.9):
                self.assertIn(
                    ganador,
                    conjunto_por_margen(scores, margen),
                )

    def test_margen_no_se_corre_con_el_parametro(self) -> None:
        """Unlike coverage, the result stops moving once the margin exceeds the
        real gap. That stability is why the rule fits this classifier.

        [ES] A diferencia de la cobertura, el resultado deja de moverse cuando
        el margen supera la brecha real. Esa estabilidad es la razón por la que
        la regla le sirve a este clasificador.
        """
        resultados = {
            tuple(conjunto_por_margen(self.PUNTIAGUDA, margen))
            for margen in (0.05, 0.10, 0.20, 0.30)
        }

        self.assertEqual(len(resultados), 1)

    def test_margen_cero_solo_admite_empates_exactos(self) -> None:
        self.assertEqual(
            conjunto_por_margen(self.BIDOMINIO, 0.0),
            ["legal"],
        )

        empate = {
            "legal": 0.40,
            "impositivo": 0.40,
            "contable": 0.10,
            "financiero": 0.10,
        }

        self.assertEqual(
            conjunto_por_margen(empate, 0.0),
            ["impositivo", "legal"],
        )

    def test_margen_rechaza_parametros_fuera_de_rango(self) -> None:
        for valor in (-0.1, 1.0, 1.5):
            with self.assertRaises(ErrorDeMembresias):
                conjunto_por_margen(self.PLANA, valor)

    def test_el_score_por_dominio_llega_a_la_fila(self) -> None:
        registro = {
            "chunk_uid": UID_A,
            "dominios_propuestos": ["legal", "impositivo"],
            "estado_asignacion": "asignado",
            "scores_por_dominio": {
                "legal": 0.6,
                "impositivo": 0.3,
            },
            "modelo_resuelto": "coseno_a_centroide",
        }

        filas = filas_de_membresia(
            [registro],
            assignment_version="coseno-1",
            taxonomy_version="taxonomia-v1",
            assignment_method="coseno_a_centroide",
            score_kind="softmax_coseno_a_centroide_no_calibrado",
        )

        self.assertEqual(
            {
                fila["domain_id"]: fila["score"]
                for fila in filas
            },
            {"legal": 0.6, "impositivo": 0.3},
        )
        self.assertEqual(
            filas[0]["score_kind"],
            "softmax_coseno_a_centroide_no_calibrado",
        )


class SentenciasSqlTestCase(unittest.TestCase):
    """The emitted SQL is idempotent and never overwrites a human review.

    [ES] El SQL emitido es idempotente y nunca pisa una revisión humana.
    """

    def sql_de(self, registros) -> str:
        return sentencias_sql(
            filas_de_membresia(registros, **VERSIONES),
            filas_de_materialidad(
                registros,
                materiality_version="materialidad-v1",
                assignment_method="qwen3:8b",
            ),
            origen="artefacto.jsonl",
            huella="0" * 64,
        )

    def test_no_pisa_una_revision_humana(self) -> None:
        sql = self.sql_de([propuesta(UID_A, ["legal"])])

        self.assertIn(
            "ON CONFLICT (chunk_uid, domain_id, assignment_version) "
            "DO NOTHING;",
            sql,
        )
        self.assertIn(
            "ON CONFLICT (chunk_uid, materiality_version) DO NOTHING;",
            sql,
        )
        self.assertNotIn("DO UPDATE", sql)

    def test_declara_que_son_silver(self) -> None:
        sql = self.sql_de([propuesta(UID_A, ["legal"])])

        self.assertIn("Silver", sql)
        self.assertIn("'automatic'", sql)

    def test_es_trazable_al_artefacto(self) -> None:
        sql = self.sql_de([propuesta(UID_A, ["legal"])])

        self.assertIn("artefacto.jsonl", sql)
        self.assertIn("0" * 64, sql)

    def test_transaccion_completa(self) -> None:
        sql = self.sql_de([propuesta(UID_A, ["legal"])])

        self.assertTrue(sql.count("BEGIN;") == 1)
        self.assertTrue(sql.rstrip().endswith("COMMIT;"))

    def test_sin_filas_no_emite_insert_vacio(self) -> None:
        sql = sentencias_sql(
            [],
            [],
            origen="artefacto.jsonl",
            huella="0" * 64,
        )

        self.assertNotIn("INSERT INTO", sql)
        self.assertIn("Sin filas para chunk_domain_membership", sql)

    def test_no_duplica_el_chunk_entre_dominios(self) -> None:
        sql = self.sql_de(
            [propuesta(UID_A, ["legal", "impositivo"])]
        )

        # The chunk_uid appears once per membership and once for materiality,
        # but no chunk content is copied anywhere.
        # [ES] El chunk_uid aparece una vez por membresía y una por
        # materialidad, pero no se copia contenido del chunk en ningún lado.
        self.assertEqual(sql.count(UID_A), 3)
        self.assertNotIn("contenido", sql)


if __name__ == "__main__":
    unittest.main()
