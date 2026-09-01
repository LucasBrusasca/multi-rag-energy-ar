"""Tests for the retrievable scope: A0/A1/A2 and E0/E1.

No PostgreSQL and no embedding model: the retrieval function is injected.

[ES] Pruebas del alcance recuperable: A0/A1/A2 y E0/E1.

Sin PostgreSQL y sin modelo de embeddings: la función de recuperación se
inyecta.
"""

import unittest


from multirag.orchestration.alcance import (
    COLUMNAS_RECUPERADAS,
    ORIGEN_AMBOS,
    ORIGEN_DOMINIO,
    ORIGEN_EXPANSION,
    ErrorDeAlcance,
    construir_consulta_vectorial,
    construir_filtro_asignacion,
    documentos_de,
    expandir_por_documento,
    fusionar_candidatos,
    ordenar_y_recortar,
    recuperar,
    recuperar_multidominio,
    validar_dominios,
    validar_variante_asignacion,
    validar_variante_expansion,
)


PREGUNTA = "¿Qué obligación establece la norma aplicable?"


def chunk(
    uid: str,
    similitud: float,
    document_id: str | None = None,
    silo: str = "legal",
) -> dict:
    """Build a retrieval record like the one buscar() returns.

    [ES] Construye un registro de recuperación como el que devuelve buscar().
    """
    return {
        "chunk_uid": uid,
        "silo": silo,
        "titulo": f"titulo-{uid}",
        "contenido": f"contenido-{uid}",
        "fuente": f"fuente-{uid}",
        "document_id": document_id,
        "instrument_id": None,
        "artifact_id": None,
        "similitud": similitud,
        "dominios_recuperacion": [],
        "origen_recuperacion": ORIGEN_DOMINIO,
    }


class BuscadorFalso:
    """Record the calls and answer with prepared results.

    [ES] Registra las llamadas y responde con resultados preparados.
    """

    def __init__(self, por_dominio=None, por_documento=None, monolitico=None):
        self.por_dominio = por_dominio or {}
        self.por_documento = por_documento or []
        self.monolitico = monolitico or []
        self.llamadas = []

    def __call__(self, pregunta, silo=None, k=3, documentos=None, **opciones):
        self.llamadas.append(
            {
                "pregunta": pregunta,
                "silo": silo,
                "k": k,
                "documentos": documentos,
                **opciones,
            }
        )

        if documentos:
            return [
                dict(registro)
                for registro in self.por_documento
                if registro.get("document_id") in documentos
            ][:k]

        if silo is None:
            return [
                dict(registro)
                for registro in self.monolitico
            ][:k]

        return [
            dict(registro)
            for registro in self.por_dominio.get(silo, [])
        ][:k]


class FiltroDeAsignacionTestCase(unittest.TestCase):
    """A0 keeps the current behaviour; A1/A2 demand explicit versions.

    [ES] A0 conserva el comportamiento actual; A1/A2 exigen versiones
    explícitas.
    """

    def test_a0_filtra_por_la_columna_heredada_silo(self) -> None:
        condiciones, parametros = construir_filtro_asignacion(
            variante_asignacion="A0",
            dominio="legal",
        )

        self.assertEqual(condiciones, ["silo = %s"])
        self.assertEqual(parametros, ["legal"])

    def test_a0_monolitico_no_agrega_condiciones(self) -> None:
        condiciones, parametros = construir_filtro_asignacion()

        self.assertEqual(condiciones, [])
        self.assertEqual(parametros, [])

    def test_a0_rechaza_versiones_de_membresias(self) -> None:
        with self.assertRaises(ErrorDeAlcance) as contexto:
            construir_filtro_asignacion(
                variante_asignacion="A0",
                dominio="legal",
                assignment_version="v1",
            )

        self.assertIn("A0", str(contexto.exception))
        self.assertIn("chunks.silo", str(contexto.exception))

    def test_a1_exige_version_explicita(self) -> None:
        with self.assertRaises(ErrorDeAlcance) as contexto:
            construir_filtro_asignacion(
                variante_asignacion="A1",
                dominio="legal",
            )

        mensaje = str(contexto.exception)

        self.assertIn("assignment_version", mensaje)
        self.assertIn("última versión", mensaje)

    def test_a1_rechaza_version_vacia(self) -> None:
        with self.assertRaises(ErrorDeAlcance):
            construir_filtro_asignacion(
                variante_asignacion="A1",
                dominio="legal",
                assignment_version="   ",
            )

    def test_a1_consulta_membresias_versionadas_sin_rechazadas(self) -> None:
        condiciones, parametros = construir_filtro_asignacion(
            variante_asignacion="A1",
            dominio="impositivo",
            assignment_version="asignacion-2026-08-22",
        )

        self.assertEqual(len(condiciones), 1)
        self.assertIn(
            "chunk_domain_membership",
            condiciones[0],
        )
        self.assertIn(
            "m.review_status <> %s",
            condiciones[0],
        )
        self.assertIn(
            "m.domain_id = %s",
            condiciones[0],
        )
        self.assertEqual(
            parametros,
            [
                "asignacion-2026-08-22",
                "rejected",
                "impositivo",
            ],
        )

    def test_a1_no_acepta_materialidad(self) -> None:
        with self.assertRaises(ErrorDeAlcance) as contexto:
            construir_filtro_asignacion(
                variante_asignacion="A1",
                assignment_version="v1",
                materiality_version="m1",
            )

        self.assertIn("A2", str(contexto.exception))

    def test_a2_exige_version_de_materialidad(self) -> None:
        with self.assertRaises(ErrorDeAlcance) as contexto:
            construir_filtro_asignacion(
                variante_asignacion="A2",
                assignment_version="v1",
            )

        self.assertIn(
            "materiality_version",
            str(contexto.exception),
        )

    def test_a2_agrega_compuerta_de_materialidad(self) -> None:
        condiciones, parametros = construir_filtro_asignacion(
            variante_asignacion="A2",
            dominio="contable",
            assignment_version="v1",
            materiality_version="m1",
        )

        self.assertEqual(len(condiciones), 2)
        self.assertIn(
            "chunk_materiality",
            condiciones[1],
        )
        self.assertIn(
            "administrativo_no_material",
            parametros[-1],
        )

    def test_a2_no_aplica_compuerta_en_consulta_procedimental(self) -> None:
        condiciones, _ = construir_filtro_asignacion(
            variante_asignacion="A2",
            dominio="contable",
            assignment_version="v1",
            materiality_version="m1",
            consulta_procedimental=True,
        )

        self.assertEqual(len(condiciones), 1)
        self.assertNotIn(
            "chunk_materiality",
            condiciones[0],
        )

    def test_a2_no_se_confunde_con_e1(self) -> None:
        """A2 is the materiality gate; documentary expansion is E1.

        [ES] A2 es la compuerta de materialidad; la expansión documental es E1.
        """
        with self.assertRaises(ErrorDeAlcance) as contexto:
            validar_variante_expansion("A2")

        self.assertIn(
            "A2",
            str(contexto.exception),
        )

        with self.assertRaises(ErrorDeAlcance):
            validar_variante_asignacion("E1")

        condiciones, _ = construir_filtro_asignacion(
            variante_asignacion="A2",
            assignment_version="v1",
            materiality_version="m1",
        )

        # The A2 gate says nothing about document_id: it is another dimension.
        # [ES] La compuerta A2 no dice nada de document_id: es otra dimensión.
        self.assertNotIn(
            "document_id",
            " ".join(condiciones),
        )


class ConsultaVectorialTestCase(unittest.TestCase):
    """The executed SQL and the planned SQL come from the same builder.

    [ES] El SQL ejecutado y el SQL planificado salen del mismo constructor.
    """

    def test_orden_de_parametros(self) -> None:
        condiciones, parametros = construir_filtro_asignacion(
            variante_asignacion="A1",
            dominio="legal",
            assignment_version="v1",
        )

        sql, params = construir_consulta_vectorial(
            vector_literal="[0.1,0.2]",
            k=5,
            condiciones=condiciones,
            parametros_filtro=parametros,
        )

        # Vector for the similarity column, filter parameters, vector for the
        # ordering, and k at the end.
        # [ES] Vector de la columna de similitud, parámetros del filtro, vector
        # del ordenamiento y k al final.
        self.assertEqual(
            params,
            [
                "[0.1,0.2]",
                "v1",
                "rejected",
                "legal",
                "[0.1,0.2]",
                5,
            ],
        )
        self.assertEqual(
            sql.count("%s"),
            len(params),
        )

    def test_devuelve_la_identidad_documental(self) -> None:
        sql, _ = construir_consulta_vectorial(
            vector_literal="[0.1]",
            k=1,
        )

        for columna in (
            "chunk_uid",
            "silo",
            "document_id",
            "instrument_id",
            "artifact_id",
        ):
            self.assertIn(columna, sql)

        self.assertIn(columna, COLUMNAS_RECUPERADAS)

    def test_sin_condiciones_no_emite_where(self) -> None:
        sql, params = construir_consulta_vectorial(
            vector_literal="[0.1]",
            k=2,
        )

        self.assertNotIn("WHERE", sql)
        self.assertEqual(params, ["[0.1]", "[0.1]", 2])

    def test_documentos_agrega_el_filtro_al_final(self) -> None:
        sql, params = construir_consulta_vectorial(
            vector_literal="[0.1]",
            k=2,
            condiciones=["silo = %s"],
            parametros_filtro=["legal"],
            documentos=["DOC-1", "DOC-2"],
        )

        self.assertIn(
            "WHERE silo = %s AND document_id = ANY(%s)",
            sql,
        )
        self.assertEqual(
            params,
            [
                "[0.1]",
                "legal",
                ["DOC-1", "DOC-2"],
                "[0.1]",
                2,
            ],
        )

    def test_k_invalido_en_la_consulta(self) -> None:
        with self.assertRaises(ErrorDeAlcance):
            construir_consulta_vectorial(
                vector_literal="[0.1]",
                k=0,
            )


class VariantesInvalidasTestCase(unittest.TestCase):
    """Invalid variants produce clear errors.

    [ES] Las variantes inválidas producen errores claros.
    """

    def test_variante_de_asignacion_desconocida(self) -> None:
        with self.assertRaises(ErrorDeAlcance) as contexto:
            validar_variante_asignacion("A3")

        mensaje = str(contexto.exception)

        self.assertIn("A3", mensaje)
        self.assertIn("A0, A1, A2", mensaje)

    def test_variante_de_expansion_desconocida(self) -> None:
        with self.assertRaises(ErrorDeAlcance) as contexto:
            validar_variante_expansion("E2")

        mensaje = str(contexto.exception)

        self.assertIn("E2", mensaje)
        self.assertIn("E0, E1", mensaje)

    def test_dominio_desconocido(self) -> None:
        with self.assertRaises(ErrorDeAlcance) as contexto:
            validar_dominios(["legal", "energetico"])

        self.assertIn(
            "energetico",
            str(contexto.exception),
        )

    def test_conjunto_de_dominios_vacio(self) -> None:
        with self.assertRaises(ErrorDeAlcance):
            validar_dominios([])

    def test_dominios_como_cadena(self) -> None:
        with self.assertRaises(ErrorDeAlcance):
            validar_dominios("legal")

    def test_dominios_repetidos_se_consultan_una_vez(self) -> None:
        self.assertEqual(
            validar_dominios(["legal", "legal", "impositivo"]),
            ("legal", "impositivo"),
        )

    def test_k_invalido(self) -> None:
        with self.assertRaises(ErrorDeAlcance):
            ordenar_y_recortar([], 0)


class RecuperacionMultidominioTestCase(unittest.TestCase):
    """Union, deduplication and constant final budget.

    [ES] Unión, deduplicación y presupuesto final constante.
    """

    def test_chunk_de_dos_dominios_aparece_una_sola_vez(self) -> None:
        compartido_legal = chunk("uid-compartido", 0.71)
        compartido_impositivo = chunk(
            "uid-compartido",
            0.88,
            silo="legal",
        )
        buscador = BuscadorFalso(
            por_dominio={
                "legal": [compartido_legal, chunk("uid-legal", 0.60)],
                "impositivo": [compartido_impositivo],
            }
        )

        resultados = recuperar_multidominio(
            pregunta=PREGUNTA,
            dominios=["legal", "impositivo"],
            buscar_fn=buscador,
            k=3,
        )

        uids = [registro["chunk_uid"] for registro in resultados]

        self.assertEqual(
            uids.count("uid-compartido"),
            1,
        )

        compartido = resultados[0]

        self.assertEqual(
            compartido["chunk_uid"],
            "uid-compartido",
        )
        self.assertEqual(
            compartido["dominios_recuperacion"],
            ["legal", "impositivo"],
        )
        self.assertEqual(
            compartido["similitud"],
            0.88,
        )

    def test_respeta_el_k_final(self) -> None:
        buscador = BuscadorFalso(
            por_dominio={
                "legal": [
                    chunk("uid-1", 0.9),
                    chunk("uid-2", 0.8),
                    chunk("uid-3", 0.7),
                ],
                "impositivo": [
                    chunk("uid-4", 0.85),
                    chunk("uid-5", 0.75),
                ],
            }
        )

        resultados = recuperar_multidominio(
            pregunta=PREGUNTA,
            dominios=["legal", "impositivo"],
            buscar_fn=buscador,
            k=2,
        )

        self.assertEqual(len(resultados), 2)
        self.assertEqual(
            [registro["chunk_uid"] for registro in resultados],
            ["uid-1", "uid-4"],
        )

        # Each domain is queried with the same k as A0: no extra budget.
        # [ES] Cada dominio se consulta con el mismo k que A0: sin presupuesto
        # adicional.
        self.assertEqual(
            [llamada["k"] for llamada in buscador.llamadas],
            [2, 2],
        )

    def test_propaga_la_variante_declarada(self) -> None:
        buscador = BuscadorFalso(
            por_dominio={"legal": [chunk("uid-1", 0.9)]}
        )

        recuperar_multidominio(
            pregunta=PREGUNTA,
            dominios=["legal"],
            buscar_fn=buscador,
            k=1,
            variante_asignacion="A1",
            assignment_version="v1",
        )

        self.assertEqual(
            buscador.llamadas[0]["variante_asignacion"],
            "A1",
        )
        self.assertEqual(
            buscador.llamadas[0]["assignment_version"],
            "v1",
        )

    def test_a1_sin_version_falla_antes_de_consultar(self) -> None:
        buscador = BuscadorFalso(
            por_dominio={"legal": [chunk("uid-1", 0.9)]}
        )

        with self.assertRaises(ErrorDeAlcance):
            recuperar(
                pregunta=PREGUNTA,
                buscar_fn=lambda *a, **kw: (_ for _ in ()).throw(
                    AssertionError(
                        "No debe consultarse la base sin versión explícita."
                    )
                ),
                dominios=["legal"],
                k=2,
                variante_asignacion="A1",
            )

        self.assertEqual(buscador.llamadas, [])


class FusionTestCase(unittest.TestCase):
    """Deduplication rules of the merge.

    [ES] Reglas de deduplicación de la fusión.
    """

    def test_conserva_la_similitud_mayor(self) -> None:
        fusionados = fusionar_candidatos(
            [
                chunk("uid-1", 0.40),
                chunk("uid-1", 0.95),
                chunk("uid-1", 0.10),
            ]
        )

        self.assertEqual(len(fusionados), 1)
        self.assertEqual(
            fusionados[0]["similitud"],
            0.95,
        )

    def test_combina_los_origenes(self) -> None:
        semilla = chunk("uid-1", 0.9)
        semilla["origen_recuperacion"] = ORIGEN_DOMINIO

        hermano = chunk("uid-1", 0.9)
        hermano["origen_recuperacion"] = ORIGEN_EXPANSION

        fusionados = fusionar_candidatos([semilla, hermano])

        self.assertEqual(
            fusionados[0]["origen_recuperacion"],
            ORIGEN_AMBOS,
        )

    def test_completa_campos_ausentes(self) -> None:
        parcial = chunk("uid-1", 0.9)
        parcial["document_id"] = None

        completo = chunk("uid-1", 0.5, document_id="DOC-1")

        fusionados = fusionar_candidatos([parcial, completo])

        self.assertEqual(
            fusionados[0]["document_id"],
            "DOC-1",
        )

    def test_registro_sin_chunk_uid_no_se_fusiona_con_otro(self) -> None:
        sin_uid = chunk("", 0.9)
        otro_sin_uid = chunk("", 0.8)

        fusionados = fusionar_candidatos([sin_uid, otro_sin_uid])

        self.assertEqual(len(fusionados), 2)


class ExpansionDocumentalTestCase(unittest.TestCase):
    """E1 works independently of A0/A1/A2.

    [ES] E1 funciona con independencia de A0/A1/A2.
    """

    def test_incorpora_un_hermano_relevante_del_mismo_documento(self) -> None:
        semilla = chunk("uid-semilla", 0.90, document_id="DOC-1")
        hermano = chunk("uid-hermano", 0.80, document_id="DOC-1")

        buscador = BuscadorFalso(
            por_documento=[semilla, hermano]
        )

        resultados = expandir_por_documento(
            pregunta=PREGUNTA,
            semillas=[semilla],
            buscar_fn=buscador,
            k=3,
        )

        uids = [registro["chunk_uid"] for registro in resultados]

        self.assertIn("uid-hermano", uids)

        recuperado = next(
            registro
            for registro in resultados
            if registro["chunk_uid"] == "uid-hermano"
        )

        self.assertEqual(
            recuperado["origen_recuperacion"],
            ORIGEN_EXPANSION,
        )

        # The sibling query is bounded and asks only for the seeds' documents.
        # [ES] La consulta de hermanos está acotada y pide solo los documentos
        # de las semillas.
        self.assertEqual(
            buscador.llamadas[0]["documentos"],
            ["DOC-1"],
        )
        self.assertEqual(
            buscador.llamadas[0]["k"],
            3,
        )

    def test_no_introduce_el_documento_completo(self) -> None:
        semilla = chunk("uid-semilla", 0.90, document_id="DOC-1")
        documento = [semilla] + [
            chunk(f"uid-hermano-{indice}", 0.10 * indice, document_id="DOC-1")
            for indice in range(1, 6)
        ]

        buscador = BuscadorFalso(por_documento=documento)

        resultados = expandir_por_documento(
            pregunta=PREGUNTA,
            semillas=[semilla],
            buscar_fn=buscador,
            k=2,
            k_hermanos=3,
        )

        self.assertEqual(len(resultados), 2)
        self.assertLess(
            len(resultados),
            len(documento),
        )
        self.assertEqual(
            buscador.llamadas[0]["k"],
            3,
        )

    def test_deduplica_semillas_y_hermanos(self) -> None:
        semilla = chunk("uid-semilla", 0.90, document_id="DOC-1")
        hermano = chunk("uid-hermano", 0.50, document_id="DOC-1")

        # The sibling query returns the seed as well: that is the natural case.
        # [ES] La consulta de hermanos devuelve también la semilla: es el caso
        # natural.
        buscador = BuscadorFalso(
            por_documento=[semilla, hermano]
        )

        resultados = expandir_por_documento(
            pregunta=PREGUNTA,
            semillas=[semilla],
            buscar_fn=buscador,
            k=5,
        )

        uids = [registro["chunk_uid"] for registro in resultados]

        self.assertEqual(len(uids), len(set(uids)))
        self.assertEqual(len(resultados), 2)

        recuperada = next(
            registro
            for registro in resultados
            if registro["chunk_uid"] == "uid-semilla"
        )

        self.assertEqual(
            recuperada["origen_recuperacion"],
            ORIGEN_AMBOS,
        )

    def test_chunk_sin_document_id_no_rompe(self) -> None:
        sin_documento = chunk("uid-sin-doc", 0.90)
        con_documento = chunk("uid-con-doc", 0.80, document_id="DOC-1")
        hermano = chunk("uid-hermano", 0.70, document_id="DOC-1")

        buscador = BuscadorFalso(
            por_documento=[con_documento, hermano]
        )

        resultados = expandir_por_documento(
            pregunta=PREGUNTA,
            semillas=[sin_documento, con_documento],
            buscar_fn=buscador,
            k=3,
        )

        uids = [registro["chunk_uid"] for registro in resultados]

        self.assertIn("uid-sin-doc", uids)
        self.assertIn("uid-hermano", uids)
        self.assertEqual(
            buscador.llamadas[0]["documentos"],
            ["DOC-1"],
        )

    def test_sin_ningun_document_id_no_consulta_hermanos(self) -> None:
        semilla = chunk("uid-sin-doc", 0.90)
        buscador = BuscadorFalso()

        resultados = expandir_por_documento(
            pregunta=PREGUNTA,
            semillas=[semilla],
            buscar_fn=buscador,
            k=3,
        )

        self.assertEqual(buscador.llamadas, [])
        self.assertEqual(len(resultados), 1)

    def test_documentos_de_ignora_valores_vacios(self) -> None:
        self.assertEqual(
            documentos_de(
                [
                    chunk("a", 0.1),
                    chunk("b", 0.1, document_id="DOC-1"),
                    chunk("c", 0.1, document_id="DOC-1"),
                    chunk("d", 0.1, document_id="DOC-2"),
                ]
            ),
            ["DOC-1", "DOC-2"],
        )


class RecuperarTestCase(unittest.TestCase):
    """The two dimensions combine without confusing each other.

    [ES] Las dos dimensiones se combinan sin confundirse entre sí.
    """

    def test_e0_no_expande(self) -> None:
        semilla = chunk("uid-semilla", 0.90, document_id="DOC-1")
        hermano = chunk("uid-hermano", 0.80, document_id="DOC-1")

        buscador = BuscadorFalso(
            por_dominio={"legal": [semilla]},
            por_documento=[semilla, hermano],
        )

        resultados = recuperar(
            pregunta=PREGUNTA,
            buscar_fn=buscador,
            dominios=["legal"],
            k=3,
            variante_expansion="E0",
        )

        self.assertEqual(
            [registro["chunk_uid"] for registro in resultados],
            ["uid-semilla"],
        )
        self.assertEqual(
            [
                llamada["documentos"]
                for llamada in buscador.llamadas
            ],
            [None],
        )

    def test_e1_mantiene_el_mismo_k_final_que_e0(self) -> None:
        semillas = [
            chunk("uid-1", 0.90, document_id="DOC-1"),
            chunk("uid-2", 0.85, document_id="DOC-1"),
        ]
        hermanos = [
            chunk("uid-3", 0.84, document_id="DOC-1"),
            chunk("uid-4", 0.83, document_id="DOC-1"),
        ]

        buscador = BuscadorFalso(
            por_dominio={"legal": semillas},
            por_documento=semillas + hermanos,
        )

        con_expansion = recuperar(
            pregunta=PREGUNTA,
            buscar_fn=buscador,
            dominios=["legal"],
            k=2,
            variante_expansion="E1",
        )

        self.assertEqual(len(con_expansion), 2)

    def test_e1_es_independiente_de_la_variante_de_asignacion(self) -> None:
        semilla = chunk("uid-semilla", 0.90, document_id="DOC-1")
        hermano = chunk("uid-hermano", 0.80, document_id="DOC-1")

        buscador = BuscadorFalso(
            por_dominio={"legal": [semilla]},
            por_documento=[semilla, hermano],
        )

        resultados = recuperar(
            pregunta=PREGUNTA,
            buscar_fn=buscador,
            dominios=["legal"],
            k=3,
            variante_asignacion="A1",
            variante_expansion="E1",
            assignment_version="v1",
        )

        self.assertIn(
            "uid-hermano",
            [registro["chunk_uid"] for registro in resultados],
        )

        # The sibling query keeps the eligibility filter, but drops the domain
        # restriction: that is precisely what documentary expansion relaxes.
        # [ES] La consulta de hermanos conserva el filtro de elegibilidad, pero
        # suelta la restricción de dominio: es justamente lo que la expansión
        # documental relaja.
        llamada_hermanos = buscador.llamadas[-1]

        self.assertIsNone(llamada_hermanos["silo"])
        self.assertEqual(
            llamada_hermanos["variante_asignacion"],
            "A1",
        )
        self.assertEqual(
            llamada_hermanos["assignment_version"],
            "v1",
        )

    def test_variante_de_expansion_invalida(self) -> None:
        with self.assertRaises(ErrorDeAlcance):
            recuperar(
                pregunta=PREGUNTA,
                buscar_fn=BuscadorFalso(),
                dominios=["legal"],
                k=1,
                variante_expansion="A2",
            )


if __name__ == "__main__":
    unittest.main()
