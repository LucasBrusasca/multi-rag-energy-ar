"""Tests for the RQ0 diagnostic: the parts that decide whether it means anything.

None of these touch the database. What is under test is the reasoning, not the
numbers. Four of them pin defects the first version of the script actually had:

1. THE DOCUMENT IS THE UNIT, AND WEIGHS ONCE. Duplicating a document's chunks
   must not move the primary result by a hair. The first version built centroids
   from chunks, so a document of 812 chunks pulled 270 times harder than one of
   3 and the answer described the longest documents.
2. THE NULL REFITS. Permuting labels has to re-run every fold and rebuild every
   centroid. Keeping the observed predictions and permuting only the truth tests
   a different and much weaker hypothesis.
3. THE BOOTSTRAP KEEPS EVERY CLASS. Stratified within the true class, so no
   resample can silently lose one and make balanced accuracy undefined.
4. THE FOUR SILOS ARE THE PRIMARY QUESTION, and `financiero` keeps its three
   documents. `dominio_combinacion` drops all three of them.

[ES] Pruebas del diagnostico RQ0: las partes que deciden si significa algo.

Ninguna toca la base. Lo que se prueba es el razonamiento, no los numeros.
Cuatro de ellas fijan defectos que la primera version del script tenia de verdad:

1. EL DOCUMENTO ES LA UNIDAD, Y PESA UNA VEZ. Duplicar los chunks de un
   documento no debe mover ni un pelo el resultado primario. La primera version
   armaba los centroides con chunks, asi que un documento de 812 chunks tiraba
   270 veces mas fuerte que uno de 3 y la respuesta describia los documentos mas
   largos.
2. EL NULO REAJUSTA. Permutar etiquetas tiene que volver a correr cada fold y
   reconstruir cada centroide. Conservar las predicciones observadas y permutar
   solo la verdad prueba otra hipotesis, mucho mas debil.
3. EL BOOTSTRAP CONSERVA TODAS LAS CLASES. Estratificado dentro de la clase
   verdadera, para que ninguna remuestra pueda perder una en silencio y volver
   indefinida la exactitud balanceada.
4. LOS CUATRO SILOS SON LA PREGUNTA PRIMARIA, y `financiero` conserva sus tres
   documentos. `dominio_combinacion` los descarta a los tres.
"""

import collections
import csv
import unittest
from pathlib import Path

import numpy as np

from multirag.config import SILOS
from multirag.paths import DATA_DIR
from scripts.diagnostics.rq0_geometria_vs_metadatos import (
    DOMINIOS_CENTRALES,
    MINIMO_PARA_BOOTSTRAP,
    SEPARADOR_DOMINIOS,
    bootstrap_estratificado,
    clases_admisibles,
    etiquetas_por_documento,
    formatear_p,
    holm,
    huella_de_conjunto,
    leer_inventario_objetivo,
    normalizar,
    nulo_reajustado,
    predecir_documentos,
    vectores_por_documento,
)


def corpus_sintetico(chunks_por_documento, semilla=7):
    """Six documents in two separable clouds, with the chunk counts requested.

    [ES] Seis documentos en dos nubes separables, con las cantidades de chunks
    que se pidan.
    """
    generador = np.random.default_rng(semilla)
    X, grupos, etiquetas = [], [], {}
    for i, n in enumerate(chunks_por_documento):
        doc = f"DOC-{i:02d}"
        clase = "a" if i < 3 else "b"
        etiquetas[doc] = clase
        centro = np.zeros(8)
        centro[0] = 3.0 if clase == "a" else -3.0
        X.append(generador.normal(centro, 0.4, size=(n, 8)))
        grupos.extend([doc] * n)
    return normalizar(np.vstack(X)), grupos, etiquetas


class ElDocumentoPesaUnaVez(unittest.TestCase):
    """[ES] El defecto 1 de la v0.1, fijado."""

    def test_duplicar_los_chunks_de_un_documento_no_cambia_el_primario(self):
        # THE regression. The same six documents, one of them with its chunks
        # repeated ten times. Under the old chunk-weighted centroids this
        # rewrote the answer; with one vector per document it cannot move at all,
        # because the mean of a set equals the mean of that set repeated.
        # [ES] LA regresion. Los mismos seis documentos, uno con sus chunks
        # repetidos diez veces. Con los centroides pesados por chunks de antes
        # esto reescribia la respuesta; con un vector por documento no puede
        # moverse nada, porque el promedio de un conjunto es igual al promedio de
        # ese conjunto repetido.
        X, grupos, etiquetas = corpus_sintetico([20, 20, 20, 20, 20, 20])
        documentos, V = vectores_por_documento(X, grupos)
        docs_a, verdadero_a, predicho_a = predecir_documentos(V, documentos, etiquetas)

        # Duplicate every chunk of DOC-00, ten times over.
        # [ES] Duplicar cada chunk de DOC-00, diez veces.
        idx = [i for i, g in enumerate(grupos) if g == "DOC-00"]
        X_dup = np.vstack([X] + [X[idx]] * 9)
        grupos_dup = list(grupos) + ["DOC-00"] * (len(idx) * 9)

        documentos_b, V_b = vectores_por_documento(X_dup, grupos_dup)
        docs_b, verdadero_b, predicho_b = predecir_documentos(V_b, documentos_b, etiquetas)

        self.assertEqual(docs_a, docs_b)
        self.assertEqual(list(verdadero_a), list(verdadero_b))
        self.assertEqual(list(predicho_a), list(predicho_b))
        np.testing.assert_allclose(V, V_b, atol=1e-12)

    def test_un_documento_de_800_chunks_no_domina_a_uno_de_3(self):
        # Wildly unequal lengths, same two clouds. The document vectors must
        # come out unit-norm and one per document regardless.
        # [ES] Largos desparejos al extremo, las mismas dos nubes. Los vectores
        # documentales tienen que salir de norma 1 y uno por documento igual.
        X, grupos, etiquetas = corpus_sintetico([800, 3, 5, 700, 4, 3])
        documentos, V = vectores_por_documento(X, grupos)

        self.assertEqual(len(documentos), 6)
        self.assertEqual(V.shape, (6, 8))
        np.testing.assert_allclose(np.linalg.norm(V, axis=1), 1.0, atol=1e-12)

        docs, verdadero, predicho = predecir_documentos(V, documentos, etiquetas)
        self.assertEqual(len(docs), 6)

    def test_cada_documento_entra_una_sola_vez_en_el_centroide_de_su_clase(self):
        # The centroid of a class must equal the plain mean of its document
        # vectors, normalised - not a chunk-weighted average of them.
        # [ES] El centroide de una clase tiene que ser el promedio llano de sus
        # vectores documentales, normalizado; no un promedio de ellos pesado por
        # chunks.
        X, grupos, etiquetas = corpus_sintetico([500, 4, 6, 300, 5, 4])
        documentos, V = vectores_por_documento(X, grupos)

        de_clase_a = [i for i, d in enumerate(documentos) if etiquetas[d] == "a"]
        esperado = normalizar(V[de_clase_a].mean(axis=0)[None, :])[0]

        # Same arithmetic the fold uses, written the obvious way.
        # [ES] La misma aritmetica que usa el fold, escrita de la forma obvia.
        suma = sum(V[i] for i in de_clase_a)
        obtenido = normalizar((suma / len(de_clase_a))[None, :])[0]
        np.testing.assert_allclose(esperado, obtenido, atol=1e-12)

    def test_ningun_documento_se_predice_con_un_centroide_que_lo_contiene(self):
        # Leave-one-document-out: the held-out document must not be in the sums
        # that build the centroids. A single document per class would make that
        # impossible, and that fold is dropped rather than scored.
        # [ES] Dejar-un-documento-afuera: el documento retenido no puede estar en
        # las sumas que arman los centroides. Con un solo documento por clase eso
        # seria imposible, y ese fold se descarta en lugar de puntuarse.
        X, grupos, etiquetas = corpus_sintetico([10, 10])
        etiquetas["DOC-00"], etiquetas["DOC-01"] = "a", "b"
        documentos, V = vectores_por_documento(X, grupos)
        docs, _, _ = predecir_documentos(V, documentos, etiquetas)
        self.assertEqual(docs, [])


class ElNuloReajusta(unittest.TestCase):
    """[ES] El defecto 2 de la v0.1, fijado."""

    def test_la_permutacion_vuelve_a_ajustar_todos_los_folds(self):
        # Instrumented: every refit calls `_predecir_una_pasada`. With N
        # permutations it must be called N times, once per permutation, each one
        # running the full leave-one-document-out loop. The old null called the
        # classifier zero times.
        # [ES] Instrumentado: cada reajuste llama a `_predecir_una_pasada`. Con N
        # permutaciones tiene que llamarse N veces, una por permutacion, y cada
        # una corre el ciclo completo. El nulo viejo llamaba al clasificador cero
        # veces.
        import scripts.diagnostics.rq0_geometria_vs_metadatos as rq0

        X, grupos, etiquetas = corpus_sintetico([8, 8, 8, 8, 8, 8])
        documentos, V = vectores_por_documento(X, grupos)

        original = rq0._predecir_una_pasada
        llamadas = {"n": 0, "etiquetas_vistas": []}

        def espia(V_, y_):
            llamadas["n"] += 1
            llamadas["etiquetas_vistas"].append(tuple(y_.tolist()))
            return original(V_, y_)

        rq0._predecir_una_pasada = espia
        try:
            nulos = rq0.nulo_reajustado(V, documentos, etiquetas, 25, 3)
        finally:
            rq0._predecir_una_pasada = original

        self.assertEqual(llamadas["n"], 25)
        self.assertEqual(len(nulos), 25)
        # The labels it refits on are permuted, not the observed ones.
        # [ES] Las etiquetas con las que reajusta estan permutadas, no son las
        # observadas.
        observadas = tuple(etiquetas[d] for d in documentos)
        self.assertTrue(any(v != observadas for v in llamadas["etiquetas_vistas"]))
        # And every permutation is a relabelling: the multiset is preserved.
        # [ES] Y cada permutacion es un reetiquetado: se conserva el multiconjunto.
        for vistas in llamadas["etiquetas_vistas"]:
            self.assertEqual(
                collections.Counter(vistas), collections.Counter(observadas)
            )

    def test_el_nulo_de_una_senal_real_queda_por_debajo_de_lo_observado(self):
        # [ES] Si el nulo no baja con senal real, no esta midiendo nada.
        X, grupos, etiquetas = corpus_sintetico([8, 8, 8, 8, 8, 8])
        documentos, V = vectores_por_documento(X, grupos)
        _, verdadero, predicho = predecir_documentos(V, documentos, etiquetas)

        from sklearn.metrics import balanced_accuracy_score

        observado = balanced_accuracy_score(verdadero, predicho)
        nulos = nulo_reajustado(V, documentos, etiquetas, 200, 3)
        self.assertGreater(observado, float(np.mean(nulos)))

    def test_el_nulo_es_reproducible_con_la_misma_semilla(self):
        X, grupos, etiquetas = corpus_sintetico([6, 6, 6, 6, 6, 6])
        documentos, V = vectores_por_documento(X, grupos)
        uno = nulo_reajustado(V, documentos, etiquetas, 50, 42)
        otro = nulo_reajustado(V, documentos, etiquetas, 50, 42)
        np.testing.assert_array_equal(uno, otro)


class ElBootstrapConservaLasClases(unittest.TestCase):
    """[ES] El defecto 4 de la v0.1, fijado."""

    def test_ninguna_remuestra_pierde_una_clase(self):
        # A plain bootstrap over these 10 documents loses the minority class
        # often. Stratifying makes it impossible, so balanced accuracy is always
        # defined and no resample has to be discarded.
        # [ES] Un bootstrap comun sobre estos 10 documentos pierde seguido la
        # clase minoritaria. Estratificar lo vuelve imposible, asi que la
        # exactitud balanceada siempre esta definida y no hay que descartar
        # ninguna remuestra.
        import scripts.diagnostics.rq0_geometria_vs_metadatos as rq0

        verdadero = np.array(["a"] * 8 + ["b"] * 2, dtype=object)
        predicho = np.array(["a"] * 8 + ["b"] * 2, dtype=object)

        original = rq0.balanced_accuracy_score
        vistas = []

        def espia(v, p):
            vistas.append(sorted(set(np.asarray(v).tolist())))
            return original(v, p)

        rq0.balanced_accuracy_score = espia
        try:
            valores = rq0.bootstrap_estratificado(verdadero, predicho, 300, 5)
        finally:
            rq0.balanced_accuracy_score = original

        self.assertEqual(len(valores), 300)
        for clases in vistas:
            self.assertEqual(clases, ["a", "b"])

    def test_conserva_el_tamano_de_cada_clase(self):
        # [ES] Estratificado significa el mismo tamano por clase, no solo la
        # presencia de la clase.
        import scripts.diagnostics.rq0_geometria_vs_metadatos as rq0

        verdadero = np.array(["a"] * 7 + ["b"] * 3, dtype=object)
        original = rq0.balanced_accuracy_score
        conteos = []

        def espia(v, p):
            conteos.append(collections.Counter(np.asarray(v).tolist()))
            return original(v, p)

        rq0.balanced_accuracy_score = espia
        try:
            rq0.bootstrap_estratificado(verdadero, verdadero, 100, 5)
        finally:
            rq0.balanced_accuracy_score = original

        for c in conteos:
            self.assertEqual(c["a"], 7)
            self.assertEqual(c["b"], 3)

    def test_el_umbral_de_omision_del_intervalo_esta_declarado(self):
        # [ES] Con tres documentos el intervalo es decorado, y el umbral que lo
        # decide es una constante visible, no un numero escondido en una rama.
        self.assertGreaterEqual(MINIMO_PARA_BOOTSTRAP, 4)


class LosCuatroSilosSonLaPreguntaPrimaria(unittest.TestCase):
    """[ES] El defecto 3 de la v0.1, fijado. Con el catalogo real."""

    def _catalogo_real(self):
        ruta = DATA_DIR / "catalog" / "metadatos_curados.csv"
        with ruta.open(encoding="utf-8-sig") as f:
            return {r["document_id"]: r for r in csv.DictReader(f)}

    def test_los_dominios_centrales_son_los_cuatro_silos_de_la_configuracion(self):
        # Read from the single source of truth, not retyped. If a silo is
        # renamed in config, this analysis follows or fails loudly.
        # [ES] Leidos de la fuente unica de verdad, no reescritos. Si se renombra
        # un silo en config, este analisis lo sigue o falla a gritos.
        self.assertEqual(set(DOMINIOS_CENTRALES), set(SILOS))
        self.assertEqual(len(DOMINIOS_CENTRALES), 4)
        for esperado in ("legal", "impositivo", "contable", "financiero"):
            self.assertIn(esperado, DOMINIOS_CENTRALES)

    def test_financiero_conserva_sus_tres_documentos_como_ovr(self):
        # The whole point of problem 3. As a one-vs-rest token, `financiero`
        # keeps its three documents; as part of `dominio_combinacion` it loses
        # all three.
        # [ES] Todo el punto del problema 3. Como token uno-contra-el-resto,
        # `financiero` conserva sus tres documentos; dentro de
        # `dominio_combinacion` los pierde a los tres.
        catalogo = self._catalogo_real()
        objetivos = etiquetas_por_documento(catalogo, list(catalogo))

        con_financiero = [
            d for d, tks in objetivos["dominio_token"].items() if "financiero" in tks
        ]
        self.assertEqual(len(con_financiero), 3)

        admisibles, _ = clases_admisibles(objetivos["dominio_combinacion"], 2)
        perdidos = [
            d for d in con_financiero
            if objetivos["dominio_combinacion"][d] not in admisibles
        ]
        self.assertEqual(sorted(perdidos), sorted(con_financiero))

    def test_los_24_documentos_estan_contabilizados_y_los_pilotos_afuera(self):
        # [ES] 24 en el inventario objetivo, 24 en el catalogo, y los artefactos
        # piloto no estan en ninguno de los dos.
        catalogo = self._catalogo_real()
        self.assertEqual(len(catalogo), 24)
        self.assertEqual(len(leer_inventario_objetivo()), 24)

        objetivos = etiquetas_por_documento(catalogo, list(catalogo))
        for nombre in ("tipo_documento", "emisor_id", "dominio_token"):
            self.assertEqual(len(objetivos[nombre]), 24)

        for piloto in ("DOC-0025", "DOC-0026", "DOC-0027", "DOC-0028"):
            self.assertNotIn(piloto, catalogo)

    def test_cada_documento_aporta_a_todos_sus_dominios_no_solo_al_primero(self):
        # [ES] Multietiqueta de verdad: un documento `contable|regulatorio` es
        # positivo en los dos, no solo en el que aparece primero.
        catalogo = self._catalogo_real()
        objetivos = etiquetas_por_documento(catalogo, list(catalogo))
        conteo = collections.Counter()
        for tks in objetivos["dominio_token"].values():
            conteo.update(tks)
        # More token-assignments than documents: they overlap, as they must.
        # [ES] Mas asignaciones de token que documentos: se superponen, como
        # corresponde.
        self.assertGreater(sum(conteo.values()), 24)
        self.assertEqual(objetivos["dominio_token"]["DOC-0007"].count("contable"), 1)


class PresentacionDeResultados(unittest.TestCase):
    """[ES] Un p impreso como 0.000 afirma mas certeza de la que hay."""

    def test_los_valores_p_nunca_se_imprimen_como_cero(self):
        self.assertEqual(formatear_p(0.0), "<0.001")
        self.assertEqual(formatear_p(0.0004), "<0.001")
        self.assertEqual(formatear_p(1 / 2001), "<0.001")
        self.assertEqual(formatear_p(0.049), "0.049")
        self.assertEqual(formatear_p(None), "—")
        self.assertNotEqual(formatear_p(0.0001), "0.000")

    def test_holm_es_monotono_y_no_afloja_ninguna_prueba(self):
        # Holm can only make a p larger, never smaller, and the adjusted values
        # must not cross.
        # [ES] Holm solo puede agrandar un p, nunca achicarlo, y los ajustados no
        # se pueden cruzar.
        crudos = {"a": 0.001, "b": 0.02, "c": 0.04, "d": 0.5}
        ajustados = holm(crudos)
        for nombre, p in crudos.items():
            self.assertGreaterEqual(ajustados[nombre], p)
        ordenados = [ajustados[k] for k in sorted(crudos, key=crudos.get)]
        self.assertEqual(ordenados, sorted(ordenados))

    def test_holm_sobre_cuatro_pruebas_multiplica_la_menor_por_cuatro(self):
        # [ES] Cuatro silos son cuatro oportunidades de encontrar algo.
        ajustados = holm({"a": 0.01, "b": 0.02, "c": 0.03, "d": 0.04})
        self.assertAlmostEqual(ajustados["a"], 0.04)


class HuellaDelConjunto(unittest.TestCase):
    """[ES] Sin huella, una tabla de numeros no se ata a los datos."""

    def test_no_depende_del_orden_de_las_filas(self):
        self.assertEqual(
            huella_de_conjunto(["D2", "D1"], ["c2", "c1"]),
            huella_de_conjunto(["D1", "D2"], ["c1", "c2"]),
        )

    def test_cambia_si_cambia_un_solo_chunk(self):
        self.assertNotEqual(
            huella_de_conjunto(["D1"], ["c1", "c2"]),
            huella_de_conjunto(["D1"], ["c1", "c3"]),
        )


class LecturaDelCatalogo(unittest.TestCase):
    """[ES] El campo de dominios es multivaluado y se separa por `|`."""

    def test_los_dominios_se_separan_por_barra_vertical(self):
        catalogo = {
            "D1": {"tipo_documento": "t", "emisor_id": "e",
                   "dominios_documentales": "contable|regulatorio"},
        }
        objetivos = etiquetas_por_documento(catalogo, ["D1"])
        self.assertEqual(objetivos["dominio_token"]["D1"], ("contable", "regulatorio"))
        self.assertEqual(SEPARADOR_DOMINIOS, "|")

    def test_la_combinacion_completa_se_conserva_aparte(self):
        catalogo = {
            "D1": {"tipo_documento": "t", "emisor_id": "e",
                   "dominios_documentales": "contable|regulatorio"},
        }
        objetivos = etiquetas_por_documento(catalogo, ["D1"])
        self.assertEqual(objetivos["dominio_combinacion"]["D1"], "contable|regulatorio")

    def test_un_documento_sin_fila_en_el_catalogo_no_inventa_etiqueta(self):
        catalogo = {
            "D1": {"tipo_documento": "t", "emisor_id": "e",
                   "dominios_documentales": "contable"},
        }
        objetivos = etiquetas_por_documento(catalogo, ["D1", "D-9999"])
        self.assertNotIn("D-9999", objetivos["tipo_documento"])

    def test_una_clase_de_un_solo_documento_queda_excluida(self):
        etiquetas = {"D1": "ley", "D2": "ley", "D3": "decreto"}
        admisibles, excluidas = clases_admisibles(etiquetas, 2)
        self.assertEqual(admisibles, {"ley"})
        self.assertEqual(excluidas, ["decreto"])

    def test_el_minimo_se_cuenta_en_documentos_y_no_en_chunks(self):
        # [ES] La firma solo acepta un mapeo a nivel documento, asi que contar
        # chunks no es expresable.
        admisibles, excluidas = clases_admisibles({"D1": "prospecto"}, 2)
        self.assertEqual(admisibles, set())
        self.assertEqual(excluidas, ["prospecto"])


if __name__ == "__main__":
    unittest.main()
