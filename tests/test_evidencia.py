"""Tests for the evidence-aware layer: contract, verifier and bounded cycle.

The guarantees under test are the ones that decide whether this can be trusted:

1. what is absent is reported absent, and a sentinel is never a value;
2. the obligation depends on the TYPE, and the type is never inferred from the
   field whose absence is being counted;
3. completeness and confidence stay separate: a fact can be high-confidence and
   unusable at the same time, and the verifier has to say both;
4. zero is a value, and a row or column 0 is a real cell;
5. the cycle spends exactly one retry, and a second one is impossible, not
   merely discouraged;
6. an abstention always carries its reason;
7. nothing here produces, needs or rewrites a `chunk_uid`.

[ES] Pruebas de la capa evidence-aware: contrato, verificador y ciclo acotado.

Las garantias que se prueban son las que deciden si esto es confiable:

1. lo ausente se reporta ausente, y un centinela nunca es un valor;
2. la obligatoriedad depende del TIPO, y el tipo nunca se infiere del campo cuya
   ausencia se esta contando;
3. completitud y confianza quedan separadas: un hecho puede ser de confianza
   alta e inutilizable a la vez, y el verificador tiene que decir las dos cosas;
4. el cero es un valor, y la fila o columna 0 es una celda real;
5. el ciclo gasta exactamente un reintento, y un segundo es imposible, no
   simplemente desaconsejado;
6. una abstencion siempre lleva su motivo;
7. nada de esto produce, necesita ni reescribe un `chunk_uid`.
"""

import dataclasses
import inspect
import unittest

from multirag.evidencia.ciclo import (
    ABSTENER,
    ACCION_PEDIR_ACLARACION,
    CONSULTAR_HECHOS_TABULARES,
    EXPANDIR_DOCUMENTO,
    ErrorDeCiclo,
    INDETERMINADO,
    MAX_REINTENTOS,
    PEDIR_ACLARACION,
    Plan,
    RESPONDER,
    _AdaptadorDeUnSoloUso,
    adaptador_de_prueba,
    ejecutar_ciclo,
    planificar_reintento,
)
from multirag.evidencia.composicion import (
    CONTINUIDAD_DECLARADA,
    MISMA_COLUMNA_DE_LA_MISMA_TABLA,
    MISMA_TABLA_LOGICA,
    MISMO_DOCUMENTO,
    NO_COMPONIBLES,
    componer,
    componer_una,
    vinculo_explicito,
)
from multirag.evidencia.contrato import (
    Afirmacion,
    Especificacion,
    Evidencia,
    Localizacion,
    ENTIDAD_AUSENTE,
    ENTIDAD_CURADA,
    MODALIDAD_TABLA,
    MODALIDAD_TEXTO,
    evidencia_de_chunk,
    evidencia_de_hecho_tabular,
)
from multirag.evidencia.metricas import (
    I0,
    I1,
    I2,
    Medicion,
    evaluar_calidad,
    observar,
    proyectar_i0_simulado,
    resumir,
)
from multirag.evidencia.verificador import (
    ALINEACION_NO_VERIFICADA,
    APORTE_AMBIGUO,
    COLUMNA,
    COMPARABILIDAD_INDETERMINADA,
    CONTEO,
    ENTIDAD,
    ENTIDAD_AUSENTE as MOTIVO_ENTIDAD_AUSENTE,
    ESCALA,
    ESCALA_AUSENTE,
    EVIDENCIA_NO_LOCALIZADA,
    FILA,
    FUENTES_EN_CONFLICTO,
    MONEDA,
    MONEDA_AMBIGUA,
    MONETARIO,
    NO_INTERPRETABLE,
    NO_VERIFICADO,
    PERIODO,
    PERIODO_AUSENTE,
    PORCENTAJE_RATIO,
    RECETA_REPORTE_V0,
    RECETA_TESIS,
    SOPORTE_NO_VERIFICADO,
    SOSTIENE,
    UNIDAD_AUSENTE,
    VALOR,
    VALOR_AUSENTE,
    alineada,
    clasificar_tipo,
    detectar_conflicto,
    determinar_soporte,
    verificar,
    verificar_conjunto,
)


def espec(*conceptos, **extra):
    """The claim specification a fact must align with before it may answer.

    Defaults to the concept of `hecho()`, so a test that only cares about
    integrity does not have to spell it out.

    [ES] La especificacion de la afirmacion con la que un hecho tiene que
    alinearse antes de poder responder. Por defecto, el concepto de `hecho()`,
    para que una prueba que solo mira integridad no tenga que deletrearla.
    """
    return Especificacion(conceptos=conceptos or ("Ingresos por servicios",), **extra)


def afirmacion_de(item_id, evidencias, conceptos=None, **extra):
    """[ES] Una afirmacion con especificacion declarada, que es la unica que
    puede llegar a `responder`."""
    return Afirmacion(
        item_id=item_id,
        evidencias=tuple(evidencias),
        especificacion=espec(*(conceptos or ())),
        **extra,
    )


def hecho(**sobrescribe):
    """A serialized fact, complete by default; each test breaks one thing.

    [ES] Un hecho serializado, completo por defecto; cada prueba rompe una sola
    cosa.
    """
    base = {
        "document_id": "DOC-0001",
        "artifact_id": "ART-SHA256-AAAA",
        "fuente": "TGS_EEFF_2025_09",
        "entidad": "Transportadora de Gas del Sur S.A.",
        "table_uid": "TBL-1111111111111111",
        "table_segment_uid": "TSEG-1111111111111111",
        "continuation_of": None,
        "source_pages": [7],
        "hoja": None,
        "ancla": "#/tables/3",
        "table_title": "Estado de situacion patrimonial",
        "row_label": "Ingresos por servicios",
        "row_section": None,
        "column_path": ["Ejercicio finalizado", "2025"],
        "period": {
            "crudo": "30-09-2025",
            "anio": 2025,
            "mes": 9,
            "fecha_fin": "2025-09-30",
            "granularidad": "9 meses",
            "origen": "celda_encabezado",
            "reglas": [],
        },
        "unit": {
            "escala": "miles",
            "moneda": "ARS",
            "base": None,
            "es_porcentaje": False,
            "origen": "celda_encabezado",
            "evidencia_texto": "en miles de pesos",
            "evidencia_ref": "r0c0",
            "reglas": [],
        },
        "value_raw": "1.234.567",
        "value": 1234567.0,
        "cell_coordinates": {
            "fila": 4,
            "col": 2,
            "fila_span": 1,
            "col_span": 1,
            "coordenada": None,
            "pagina": 7,
            "bbox": {"l": 1.0, "t": 2.0, "r": 3.0, "b": 4.0},
            "segmento": "#/tables/3",
        },
        "parser": "docling",
        "parser_version": "docling 2.96.1",
        "extraccion_version": "tablas-v0.1",
        "extraction_warnings": [],
        "reglas": [],
        "confianza": "alta",
    }
    base.update(sobrescribe)
    return base


class ContratoDeEvidencia(unittest.TestCase):
    """[ES] Lo ausente se representa ausente; las identidades se preservan."""

    def test_1_hecho_monetario_completo(self):
        # 1. A complete monetary fact: everything its type requires is there,
        # so it is exact and answerable in one pass.
        # [ES] 1. Hecho monetario completo: esta todo lo que su tipo exige, asi
        # que es exacto y respondible en una sola pasada.
        evidencia = evidencia_de_hecho_tabular(hecho())
        veredicto = verificar(evidencia, especificacion=espec())

        self.assertEqual(veredicto.tipo, MONETARIO)
        self.assertEqual(veredicto.componentes_faltantes, ())
        self.assertTrue(veredicto.integridad_exacta)
        self.assertTrue(veredicto.procedencia_exacta)
        self.assertEqual(veredicto.motivos, ())
        self.assertTrue(veredicto.suficiente())

        resultado = ejecutar_ciclo(afirmacion_de("item-1", [evidencia]))
        self.assertEqual(resultado.decision, RESPONDER)
        self.assertEqual(resultado.reintentos_usados, 0)

    def test_6_entidad_ausente_y_el_nombre_de_archivo_no_la_reemplaza(self):
        # 6. The extractor falls back to the file name. A file name is not an
        # entity, and the contract has to refuse it rather than record a 100 %
        # entity completeness that means nothing.
        # [ES] 6. El extractor cae al nombre de archivo. Un nombre de archivo no
        # es una entidad, y el contrato tiene que rechazarlo en lugar de anotar
        # una completitud de entidad del 100 % que no significa nada.
        evidencia = evidencia_de_hecho_tabular(
            hecho(entidad="TGS_EEFF_2025_09", fuente="TGS_EEFF_2025_09")
        )
        self.assertIsNone(evidencia.entidad)
        self.assertEqual(evidencia.entidad_origen, ENTIDAD_AUSENTE)

        veredicto = verificar(evidencia)
        self.assertIn(ENTIDAD, veredicto.componentes_faltantes)
        self.assertIn(MOTIVO_ENTIDAD_AUSENTE, veredicto.motivos)
        self.assertFalse(veredicto.integridad_exacta)

    def test_la_entidad_solo_se_puebla_a_proposito_desde_metadato_curado(self):
        # Enrichment is allowed, silence is not: the origin has to stay
        # readable, so a curated entity is never mistaken for a declared one.
        # [ES] El enriquecimiento se permite, el silencio no: el origen tiene
        # que quedar legible, para que una entidad curada nunca se confunda con
        # una declarada.
        evidencia = evidencia_de_hecho_tabular(hecho(entidad=None))
        self.assertIsNone(evidencia.entidad)

        enriquecida = evidencia.con_entidad("Transener S.A.")
        self.assertEqual(enriquecida.entidad, "Transener S.A.")
        self.assertEqual(enriquecida.entidad_origen, ENTIDAD_CURADA)
        # The original is untouched: the contract is frozen.
        # [ES] El original queda intacto: el contrato es inmutable.
        self.assertIsNone(evidencia.entidad)

    def test_7_procedencia_de_celda_completa(self):
        # 7. Cell provenance is what lets a human reopen the exact number:
        # document, page, table, row and column, plus the bbox when it exists.
        # [ES] 7. La procedencia de celda es lo que permite a un humano reabrir
        # el numero exacto: documento, pagina, tabla, fila y columna, mas el
        # bbox cuando existe.
        evidencia = evidencia_de_hecho_tabular(hecho())

        self.assertEqual(evidencia.modalidad, MODALIDAD_TABLA)
        self.assertEqual(evidencia.localizacion.paginas, (7,))
        self.assertEqual(evidencia.localizacion.fila, 4)
        self.assertEqual(evidencia.localizacion.columna, 2)
        self.assertIsNotNone(evidencia.localizacion.bbox)
        self.assertTrue(evidencia.localizacion.celda_localizada())
        # The uids are copied verbatim, never recomputed.
        # [ES] Los uid se copian tal cual, nunca se recalculan.
        self.assertEqual(evidencia.table_uid, "TBL-1111111111111111")
        self.assertEqual(evidencia.table_segment_uid, "TSEG-1111111111111111")

        veredicto = verificar(evidencia)
        self.assertEqual(veredicto.procedencia_faltante, ())
        self.assertTrue(veredicto.procedencia_exacta)

    def test_la_celda_cero_cero_existe_y_no_es_ausencia(self):
        # The grid is 0-indexed: (0,0) is the top-left cell, not a missing one.
        # [ES] La grilla es 0-indexada: (0,0) es la celda de arriba a la
        # izquierda, no una faltante.
        coords = dict(hecho()["cell_coordinates"])
        coords.update({"fila": 0, "col": 0})
        veredicto = verificar(evidencia_de_hecho_tabular(hecho(cell_coordinates=coords)))
        self.assertNotIn(FILA, veredicto.procedencia_faltante)
        self.assertNotIn(COLUMNA, veredicto.procedencia_faltante)

    def test_8_evidencia_textual(self):
        # 8. Text evidence: chunk_uid, page and offset. It is NOT asked for a
        # row or a column, because it does not have them and demanding them
        # would report a defect that does not exist.
        # [ES] 8. Evidencia textual: chunk_uid, pagina y offset. NO se le piden
        # fila ni columna, porque no las tiene y exigirselas reportaria un
        # defecto inexistente.
        evidencia = evidencia_de_chunk(
            {
                "chunk_uid": "CHK-abc123",
                "document_id": "DOC-0002",
                "artifact_id": "ART-SHA256-BBBB",
                "fuente": "Ley_24065_Energia_Electrica_TO",
                "titulo": "Articulo 40",
                "contenido": "Los transportistas y distribuidores...",
                "paginas": [12],
                "offset_desde": 5120,
                "offset_hasta": 5890,
            }
        )
        self.assertEqual(evidencia.modalidad, MODALIDAD_TEXTO)
        # Copied exactly: this layer never changes a chunk_uid.
        # [ES] Copiado exacto: esta capa nunca cambia un chunk_uid.
        self.assertEqual(evidencia.chunk_uid, "CHK-abc123")
        self.assertEqual(evidencia.localizacion.offset_desde, 5120)
        self.assertTrue(evidencia.localizacion.localizable())

        veredicto = verificar(evidencia)
        self.assertNotIn(FILA, veredicto.procedencia_requerida)
        self.assertNotIn(COLUMNA, veredicto.procedencia_requerida)
        self.assertTrue(veredicto.procedencia_exacta)

    def test_evidencia_sin_ubicacion_no_es_localizable(self):
        # [ES] Sin pagina, hoja ni offset no hay donde ir a comprobarlo.
        evidencia = evidencia_de_hecho_tabular(hecho(source_pages=[], hoja=None))
        veredicto = verificar(evidencia)
        self.assertIn(EVIDENCIA_NO_LOCALIZADA, veredicto.motivos)
        self.assertFalse(veredicto.procedencia_exacta)


class TipoYObligatoriedad(unittest.TestCase):
    """[ES] La obligatoriedad depende del tipo, y el tipo no mira lo medido."""

    def test_el_clasificador_no_puede_ver_los_campos_que_se_miden(self):
        # The non-circularity guarantee is the SIGNATURE. If someone ever adds
        # `escala`, `moneda`, `periodo` or `entidad` as a parameter, this fails
        # before any number is produced.
        # [ES] La garantia de no circularidad es la FIRMA. Si alguien alguna vez
        # agrega `escala`, `moneda`, `periodo` o `entidad` como parametro, esto
        # falla antes de que se produzca ningun numero.
        parametros = set(inspect.signature(clasificar_tipo).parameters)
        self.assertEqual(parametros, {"valor", "valor_crudo", "lexico"})
        for prohibido in ("escala", "moneda", "periodo", "entidad", "unidad"):
            self.assertNotIn(prohibido, parametros)

    def test_2_importe_sin_escala(self):
        # 2. The currency is known and the scale is not: the number can be a
        # thousand times wrong. Monetary, and incomplete.
        # [ES] 2. Se sabe la moneda y no la escala: el numero puede estar mil
        # veces mal. Monetario, e incompleto.
        unidad = dict(hecho()["unit"])
        unidad["escala"] = None
        veredicto = verificar(evidencia_de_hecho_tabular(hecho(unit=unidad)))

        self.assertEqual(veredicto.tipo, MONETARIO)
        self.assertEqual(veredicto.componentes_faltantes, (ESCALA,))
        self.assertIn(ESCALA_AUSENTE, veredicto.motivos)
        self.assertFalse(veredicto.integridad_exacta)
        # The scale is missing; the provenance is not. They are different
        # failures and must not be reported as one.
        # [ES] Falta la escala; la procedencia no. Son fallas distintas y no
        # deben reportarse como una sola.
        self.assertTrue(veredicto.procedencia_exacta)

    def test_3_porcentaje_no_requiere_moneda(self):
        # 3. Demanding a currency of a rate would count as incomplete something
        # the document never had to declare.
        # [ES] 3. Exigirle moneda a una tasa contaria como incompleto algo que
        # el documento nunca tuvo que declarar.
        unidad = {
            "escala": None,
            "moneda": None,
            "base": None,
            "es_porcentaje": True,
            "origen": "celda_encabezado",
            "evidencia_texto": "%",
            "evidencia_ref": "r0c2",
            "reglas": [],
        }
        evidencia = evidencia_de_hecho_tabular(
            hecho(
                row_label="Tasa de interes nominal anual",
                column_path=["%"],
                unit=unidad,
                value_raw="7,25",
                value=7.25,
            )
        )
        veredicto = verificar(evidencia)

        self.assertEqual(veredicto.tipo, PORCENTAJE_RATIO)
        self.assertNotIn(MONEDA, veredicto.componentes_requeridos)
        self.assertNotIn(ESCALA, veredicto.componentes_requeridos)
        self.assertEqual(veredicto.componentes_faltantes, ())
        self.assertTrue(veredicto.integridad_exacta)

    def test_4_valor_cero_es_valido(self):
        # 4. A balance sheet line can legitimately be zero. Treating it as
        # missing would invent an incomplete fact out of a complete one.
        # [ES] 4. Una linea de balance puede valer cero legitimamente. Tratarla
        # como faltante inventaria un hecho incompleto a partir de uno completo.
        veredicto = verificar(
            evidencia_de_hecho_tabular(hecho(value=0.0, value_raw="0"))
        )
        self.assertNotIn(VALOR, veredicto.componentes_faltantes)
        self.assertTrue(veredicto.integridad_por_componente[VALOR])
        self.assertTrue(veredicto.integridad_exacta)

    def test_5_periodo_ausente(self):
        # 5. An amount without a period does not say WHEN. Same fact, different
        # quarter, different answer.
        # [ES] 5. Un importe sin periodo no dice CUANDO. Mismo hecho, otro
        # trimestre, otra respuesta.
        veredicto = verificar(evidencia_de_hecho_tabular(hecho(period=None)))
        self.assertIn(PERIODO, veredicto.componentes_faltantes)
        self.assertIn(PERIODO_AUSENTE, veredicto.motivos)

    def test_periodo_con_todos_sus_campos_nulos_es_una_cascara_vacia(self):
        # [ES] Un Periodo presente pero sin ningun campo poblado no es periodo.
        vacio = {"crudo": None, "anio": None, "mes": None, "fecha_fin": None,
                 "granularidad": None, "origen": "ausente", "reglas": []}
        veredicto = verificar(evidencia_de_hecho_tabular(hecho(period=vacio)))
        self.assertIn(PERIODO, veredicto.componentes_faltantes)

    def test_valor_ausente_da_hecho_no_interpretable(self):
        # [ES] Sin valor no hay hecho que sostener; el tipo lo dice.
        veredicto = verificar(
            evidencia_de_hecho_tabular(hecho(value=None, value_raw="-"))
        )
        self.assertEqual(veredicto.tipo, NO_INTERPRETABLE)
        self.assertNotIn(VALOR_AUSENTE, veredicto.motivos)  # el tipo no lo exige

    def test_conteo_no_requiere_moneda_ni_escala(self):
        # [ES] Una cantidad de acciones no tiene moneda.
        unidad = {"escala": None, "moneda": None, "base": None, "es_porcentaje": False,
                  "origen": "ausente", "evidencia_texto": None, "evidencia_ref": None,
                  "reglas": []}
        veredicto = verificar(
            evidencia_de_hecho_tabular(
                hecho(
                    row_label="Cantidad de acciones en circulacion",
                    column_path=["2025"],
                    unit=unidad,
                    value=1000.0,
                    value_raw="1.000",
                )
            )
        )
        self.assertEqual(veredicto.tipo, CONTEO)
        self.assertNotIn(MONEDA, veredicto.componentes_requeridos)
        self.assertTrue(veredicto.integridad_exacta)

    def test_moneda_ambigua_se_reporta_aunque_la_moneda_este_presente(self):
        # In Argentina "$" is read as pesos by default and also used for
        # dollars. Ambiguity is not absence: the component IS there, and it is
        # still not safe to answer with it.
        # [ES] En Argentina "$" se lee pesos por defecto y tambien se usa para
        # dolares. La ambiguedad no es ausencia: el componente ESTA, y aun asi
        # no es seguro responder con el.
        veredicto = verificar(
            evidencia_de_hecho_tabular(
                hecho(extraction_warnings=["moneda_inferida_de_simbolo_pesos"])
            )
        )
        self.assertTrue(veredicto.integridad_por_componente[MONEDA])
        self.assertEqual(veredicto.componentes_faltantes, ())
        self.assertIn(MONEDA_AMBIGUA, veredicto.motivos)
        # Complete, and still not sufficient.
        # [ES] Completo, y aun asi insuficiente.
        self.assertTrue(veredicto.integridad_exacta)
        self.assertFalse(veredicto.suficiente())

    def test_las_dos_recetas_difieren_solo_en_la_entidad(self):
        # [ES] La receta del reporte no exige entidad; la de la tesis si. Se
        # reportan las dos para que el hueco de entidad quede visible.
        evidencia = evidencia_de_hecho_tabular(hecho(entidad=None))
        tesis = verificar(evidencia, RECETA_TESIS)
        reporte = verificar(evidencia, RECETA_REPORTE_V0)

        self.assertIn(ENTIDAD, tesis.componentes_requeridos)
        self.assertNotIn(ENTIDAD, reporte.componentes_requeridos)
        self.assertFalse(tesis.integridad_exacta)
        self.assertTrue(reporte.integridad_exacta)


class ConfianzaContraIntegridad(unittest.TestCase):
    """[ES] El caso testigo: seguro para el extractor, inutilizable para el lector."""

    def test_12_confianza_alta_con_integridad_incompleta(self):
        # 12. The 53 witness facts of reports/completitud_hechos.md: the
        # extractor's rule never looks at the missing scale, so it reports high
        # confidence over a number that can be a thousand times wrong.
        #
        # The verifier does NOT lower the confidence. Doing that would hide the
        # finding: the point is precisely that the two disagree.
        #
        # [ES] 12. Los 53 hechos testigo de reports/completitud_hechos.md: la
        # regla del extractor nunca mira la escala faltante, asi que informa
        # confianza alta sobre un numero que puede estar mil veces mal.
        #
        # El verificador NO baja la confianza. Hacerlo ocultaria el hallazgo: el
        # punto es justamente que las dos cosas se contradicen.
        unidad = dict(hecho()["unit"])
        unidad["escala"] = None
        evidencia = evidencia_de_hecho_tabular(
            hecho(unit=unidad, confianza="alta", extraction_warnings=["escala_ausente"])
        )
        veredicto = verificar(evidencia)

        self.assertEqual(veredicto.confianza_declarada, "alta")
        self.assertFalse(veredicto.integridad_exacta)
        self.assertIn(ESCALA_AUSENTE, veredicto.motivos)
        self.assertTrue(veredicto.confianza_alta_con_integridad_incompleta())

    def test_la_confianza_del_extractor_se_copia_intacta(self):
        # [ES] Se copia, no se recalcula: es la etiqueta del extractor.
        for declarada in ("alta", "media", "baja"):
            evidencia = evidencia_de_hecho_tabular(hecho(confianza=declarada))
            self.assertEqual(verificar(evidencia).confianza_declarada, declarada)


class ConflictoEntreFuentes(unittest.TestCase):
    """[ES] Misma afirmacion, numero distinto: se reporta, no se elige ganador.

    Pero primero hay que probar que son la MISMA afirmacion. Pesos contra
    dolares, o consolidado contra individual, no es un desacuerdo: son cosas
    distintas, y llamarlas conflicto fabricaria un hallazgo con datos correctos.
    """

    def _unidad(self, **cambios):
        unidad = dict(hecho()["unit"])
        # Direct assignment: the key exists with value None, so setdefault would
        # leave it undeclared and the comparison would come back undetermined.
        # [ES] Asignacion directa: la clave existe con valor None, asi que
        # setdefault la dejaria sin declarar y la comparacion volveria
        # indeterminada.
        unidad["base"] = "nominal"
        unidad.update(cambios)
        return unidad

    def test_dos_valores_distintos_de_la_misma_afirmacion_comparable(self):
        # EVERY comparability dimension declared and equal - currency, scope,
        # accounting basis and scenario - and the values still differ. Only then
        # is it a contradiction. Leaving any of the four undeclared is enough to
        # make it undetermined instead, which is what the next test shows.
        # [ES] TODAS las dimensiones de comparabilidad declaradas e iguales
        # -moneda, alcance, base contable y escenario- y aun asi los valores
        # difieren. Recien ahi es una contradiccion. Dejar cualquiera de las
        # cuatro sin declarar alcanza para volverla indeterminada, que es lo que
        # muestra la prueba siguiente.
        uno = evidencia_de_hecho_tabular(
            hecho(alcance="consolidado", escenario="real", unit=self._unidad())
        )
        dos = evidencia_de_hecho_tabular(
            hecho(
                alcance="consolidado",
                escenario="real",
                unit=self._unidad(),
                value=9999999.0,
                value_raw="9.999.999",
            )
        )
        motivos = detectar_conflicto([uno, dos])
        self.assertEqual(set(motivos.values()), {FUENTES_EN_CONFLICTO})

        for v in verificar_conjunto([uno, dos]):
            self.assertIn(FUENTES_EN_CONFLICTO, v.motivos)
            self.assertFalse(v.suficiente())

    def test_sin_alcance_declarado_la_comparabilidad_queda_indeterminada(self):
        # The extractor does not produce `alcance`, so this is the NORMAL
        # outcome over real facts today. Saying "indeterminate" instead of
        # "conflict" is the finding, not a failure to detect one.
        # [ES] El extractor no produce `alcance`, asi que este es el resultado
        # NORMAL sobre hechos reales hoy. Decir "indeterminada" en lugar de
        # "conflicto" es el hallazgo, no una falla de deteccion.
        uno = evidencia_de_hecho_tabular(hecho())
        dos = evidencia_de_hecho_tabular(hecho(value=9999999.0, value_raw="9.999.999"))
        motivos = detectar_conflicto([uno, dos])
        self.assertEqual(set(motivos.values()), {COMPARABILIDAD_INDETERMINADA})

    def test_sin_escala_no_se_declara_conflicto_sino_incompletitud(self):
        # Two figures whose scale is unknown are not in conflict; they are
        # incomparable. Calling that a conflict would manufacture a finding.
        # [ES] Dos cifras de escala desconocida no estan en conflicto; son
        # incomparables. Llamarlo conflicto fabricaria un hallazgo.
        sin_escala = dict(hecho()["unit"])
        sin_escala["escala"] = None
        uno = evidencia_de_hecho_tabular(hecho(unit=sin_escala))
        dos = evidencia_de_hecho_tabular(
            hecho(unit=sin_escala, value=9999.0, value_raw="9.999")
        )
        self.assertEqual(detectar_conflicto([uno, dos]), {})

    def test_el_conflicto_pide_aclaracion_en_lugar_de_abstenerse(self):
        # [ES] El sistema si encontro la evidencia; lo que falta es una decision
        # humana sobre que fuente manda.
        uno = evidencia_de_hecho_tabular(
            hecho(alcance="consolidado", escenario="real", unit=self._unidad())
        )
        dos = evidencia_de_hecho_tabular(
            hecho(
                alcance="consolidado",
                escenario="real",
                unit=self._unidad(),
                value=42.0,
                value_raw="42",
            )
        )
        resultado = ejecutar_ciclo([uno, dos])
        self.assertEqual(resultado.decision, PEDIR_ACLARACION)
        self.assertIn(FUENTES_EN_CONFLICTO, resultado.motivos)
        self.assertEqual(resultado.reintentos_usados, 0)


class CicloReflexivoAcotado(unittest.TestCase):
    """[ES] Un reintento. Exactamente uno. Y la abstencion siempre con motivo."""

    def _sin_escala(self):
        unidad = dict(hecho()["unit"])
        unidad["escala"] = None
        return evidencia_de_hecho_tabular(
            hecho(unit=unidad, extraction_warnings=["escala_ausente"])
        )

    def test_el_plan_elige_la_accion_que_puede_aportar_lo_que_falta(self):
        # [ES] La escala vive en el encabezado del segmento: hechos tabulares.
        veredictos = verificar_conjunto([self._sin_escala()])
        plan = planificar_reintento(veredictos, [self._sin_escala()])
        self.assertIsNotNone(plan)
        self.assertEqual(plan.accion, CONSULTAR_HECHOS_TABULARES)
        self.assertEqual(plan.motivo, ESCALA_AUSENTE)
        self.assertEqual(plan.document_ids, ("DOC-0001",))

    def test_la_entidad_faltante_manda_a_expandir_el_documento(self):
        # [ES] La entidad se declara en la caratula, nunca en la celda.
        evidencia = evidencia_de_hecho_tabular(hecho(entidad=None))
        plan = planificar_reintento(verificar_conjunto([evidencia]), [evidencia])
        self.assertEqual(plan.accion, EXPANDIR_DOCUMENTO)

    def _comparable(self, **cambios):
        """[ES] Un hecho con TODAS las dimensiones de comparabilidad declaradas."""
        unidad = dict(hecho()["unit"])
        unidad["base"] = "nominal"
        return evidencia_de_hecho_tabular(
            hecho(alcance="consolidado", escenario="real", unit=unidad, **cambios)
        )

    def test_el_conflicto_planifica_pedir_aclaracion_y_no_recupera_mas(self):
        # [ES] Recuperar mas no resuelve que dos fuentes se contradigan.
        uno = self._comparable()
        dos = self._comparable(value=42.0, value_raw="42")
        plan = planificar_reintento(verificar_conjunto([uno, dos]), [uno, dos])
        self.assertEqual(plan.accion, ACCION_PEDIR_ACLARACION)

    def test_la_comparabilidad_indeterminada_manda_a_expandir_el_documento(self):
        # [ES] Lo que volveria comparables dos cifras -el alcance ante todo- se
        # declara en la caratula y las notas, no en la celda.
        uno = evidencia_de_hecho_tabular(hecho())
        dos = evidencia_de_hecho_tabular(hecho(value=42.0, value_raw="42"))
        veredictos = verificar_conjunto([uno, dos])
        self.assertIn(COMPARABILIDAD_INDETERMINADA, veredictos[0].motivos)
        plan = planificar_reintento(veredictos, [uno, dos])
        self.assertEqual(plan.accion, EXPANDIR_DOCUMENTO)

    def test_evidencia_completa_no_planifica_reintento(self):
        # [ES] Gastar presupuesto para no cambiar nada no es reflexion.
        completa = evidencia_de_hecho_tabular(hecho())
        veredictos = verificar_conjunto([completa], especificacion=espec())
        self.assertIsNone(planificar_reintento(veredictos, [completa]))

    def test_9_un_reintento_exitoso(self):
        # 9. The scale was missing; the retry brought the header segment that
        # declares it, and the answer becomes possible. Exactly one retry.
        # [ES] 9. Faltaba la escala; el reintento trajo el segmento de
        # encabezado que la declara, y la respuesta se vuelve posible. Un solo
        # reintento.
        completa = evidencia_de_hecho_tabular(hecho())
        adaptador = adaptador_de_prueba(lambda plan: [completa])

        resultado = ejecutar_ciclo(
            afirmacion_de("item-9", [self._sin_escala()]), adaptador
        )

        self.assertEqual(resultado.decision, RESPONDER)
        self.assertEqual(resultado.reintentos_usados, 1)
        self.assertEqual(resultado.plan.accion, CONSULTAR_HECHOS_TABULARES)
        # The retry ADDS evidence; it does not replace the initial set.
        # [ES] El reintento AGREGA evidencia; no reemplaza el conjunto inicial.
        self.assertEqual(len(resultado.evidencias_finales), 2)
        self.assertFalse(resultado.veredictos_iniciales[0].integridad_exacta)

    def test_10_reintento_fallido_con_abstencion_explicada(self):
        # 10. The scale is not in the document. No amount of retrieval will
        # produce it, so the honest outcome is to abstain - saying why.
        # [ES] 10. La escala no esta en el documento. Ninguna recuperacion la va
        # a producir, asi que el resultado honesto es abstenerse - diciendo por
        # que.
        adaptador = adaptador_de_prueba(lambda plan: [])
        resultado = ejecutar_ciclo([self._sin_escala()], adaptador)

        self.assertEqual(resultado.decision, ABSTENER)
        self.assertTrue(resultado.abstuvo())
        self.assertIn(ESCALA_AUSENTE, resultado.motivos)
        self.assertEqual(resultado.reintentos_usados, 1)

    def test_sin_adaptador_no_hay_reintento_y_se_abstiene(self):
        # [ES] Es la diferencia entre I1 e I2, no un plan B.
        resultado = ejecutar_ciclo([self._sin_escala()])
        self.assertEqual(resultado.decision, ABSTENER)
        self.assertEqual(resultado.reintentos_usados, 0)
        self.assertIn(ESCALA_AUSENTE, resultado.motivos)

    def test_11_el_segundo_reintento_es_imposible(self):
        # 11. The limit is not a convention. An adapter that tries to be called
        # twice raises, so code that loops fails loudly instead of quietly
        # costing more.
        # [ES] 11. El limite no es una convencion. Un adaptador que intente ser
        # llamado dos veces levanta excepcion, asi que el codigo que itere falla
        # a gritos en lugar de costar mas en silencio.
        self.assertEqual(MAX_REINTENTOS, 1)

        interno = adaptador_de_prueba(lambda plan: [])
        una_vez = _AdaptadorDeUnSoloUso(interno)
        plan = Plan(accion=CONSULTAR_HECHOS_TABULARES, motivo=ESCALA_AUSENTE)

        una_vez.ejecutar(plan)
        with self.assertRaises(ErrorDeCiclo):
            una_vez.ejecutar(plan)

    def test_11b_el_ciclo_nunca_gasta_mas_de_un_reintento(self):
        # [ES] Aunque el reintento no arregle nada, el ciclo no vuelve a
        # intentar: cuenta los usos del adaptador, no las promesas.
        #
        # El donante viene de OTRO documento, asi que no hay vinculo explicito y
        # no puede aportar la escala. Si viniera de la misma tabla logica la
        # compondria y repararia la afirmacion, que es otra prueba.
        llamadas = []

        def responder(plan):
            llamadas.append(plan)
            return [
                evidencia_de_hecho_tabular(
                    hecho(document_id="DOC-AJENO", table_uid="TBL-ajena")
                )
            ]

        resultado = ejecutar_ciclo(
            afirmacion_de("item-11b", [self._sin_escala()]),
            adaptador_de_prueba(responder),
        )
        self.assertEqual(len(llamadas), 1)
        self.assertEqual(resultado.reintentos_usados, 1)
        self.assertLessEqual(resultado.reintentos_usados, MAX_REINTENTOS)
        self.assertEqual(resultado.decision, ABSTENER)


class MetricasDeIntegridad(unittest.TestCase):
    """[ES] Agrupadas por documento, con las salvedades adjuntas como dato."""

    def _corpus(self):
        """Three CLAIMS, not three facts. The item is the unit.

        [ES] Tres AFIRMACIONES, no tres hechos. El item es la unidad.
        """
        unidad_sin_escala = dict(hecho()["unit"])
        unidad_sin_escala["escala"] = None
        return [
            afirmacion_de("item-completo", (evidencia_de_hecho_tabular(hecho()),)),
            afirmacion_de(
                "item-sin-escala",
                (
                    evidencia_de_hecho_tabular(
                        hecho(
                            table_uid="TBL-otra",
                            table_segment_uid="TSEG-otra",
                            unit=unidad_sin_escala,
                            extraction_warnings=["escala_ausente"],
                        )
                    ),
                ),
            ),
            afirmacion_de(
                "item-sin-periodo",
                (
                    evidencia_de_hecho_tabular(
                        hecho(document_id="DOC-0002", period=None, confianza="alta")
                    ),
                ),
            ),
        ]

    def test_un_resumen_cuenta_cada_afirmacion_una_sola_vez(self):
        # [ES] Un item_id repetido inflaria todos los denominadores.
        observaciones = observar(self._corpus(), I1)
        with self.assertRaises(ValueError):
            resumir(observaciones + observaciones[:1])

    def test_la_proyeccion_i0_pierde_la_grilla_y_queda_marcada_simulada(self):
        # [ES] I0 modela lo que la linealizacion destruye. Es un modelo, y el
        # resumen tiene que decirlo.
        proyectada = proyectar_i0_simulado(evidencia_de_hecho_tabular(hecho()))
        self.assertIsNone(proyectada.table_uid)
        self.assertIsNone(proyectada.escala)
        self.assertIsNone(proyectada.periodo)
        self.assertIsNone(proyectada.localizacion.fila)

        resumen = resumir(observar(self._corpus(), I0))
        self.assertTrue(resumen.simulado)
        self.assertIn(
            "brazo simulado: proyeccion modelada, no medicion del pipeline",
            resumen.advertencias(),
        )

    def test_i1_no_reintenta_aunque_reciba_un_adaptador(self):
        # [ES] Darle el reintento a I1 borraria la diferencia que los dos brazos
        # existen para medir.
        adaptador = adaptador_de_prueba(lambda plan: [evidencia_de_hecho_tabular(hecho())])
        i1 = observar(self._corpus(), I1, adaptador)
        i2 = observar(self._corpus(), I2, adaptador)
        self.assertEqual(sum(o.reintentos_usados for o in i1), 0)
        self.assertGreater(sum(o.reintentos_usados for o in i2), 0)

    def test_el_resumen_agrupa_por_documento_y_no_pooleado(self):
        # [ES] 3 items de 2 documentos no son 3 observaciones independientes.
        resumen = resumir(observar(self._corpus(), I1))
        self.assertEqual(resumen.n_items, 3)
        self.assertEqual(resumen.n_documentos, 2)
        self.assertEqual(len(resumen.por_documento), 2)
        self.assertIn("global_agrupado_no_inferencial", resumen.__dict__)
        self.assertIn(
            "unidad de analisis: documento (n=2); los 3 items no son independientes",
            resumen.advertencias(),
        )

    def test_sin_referencia_la_calidad_no_se_evalua_y_no_se_inventa_un_cero(self):
        # [ES] None significa "no se aporto referencia"; un cero afirmaria que
        # nunca acerto.
        resumen = resumir(observar(self._corpus(), I1))
        self.assertIsNone(resumen.calidad.precision_de_abstencion)
        self.assertIsNone(resumen.calidad.tasa_de_abstencion_correcta)
        self.assertIsNone(resumen.calidad.tasa_de_falso_veto)
        self.assertIsNone(resumen.calidad.cobertura)
        self.assertIsNone(resumen.exactitud)
        self.assertFalse(resumen.calidad.calculada())

    def test_cada_metrica_de_calidad_usa_su_propio_denominador(self):
        # Three judged items: two answerable, one not. The system abstains on
        # `item-sin-escala` (answerable, so a false veto) and on
        # `item-sin-periodo` (not answerable, so a correct abstention), and
        # answers `item-completo`.
        #
        # Each figure has a DIFFERENT denominator, and that is the whole point:
        #   precision de abstencion    = 1 correcta / 2 abstenciones      = 0,50
        #   tasa de abstencion correcta = 1 correcta / 1 no respondible   = 1,00
        #   tasa de falso veto          = 1 falso   / 2 respondibles      = 0,50
        # Under the old denominator the false veto rate would have been 1/2 of
        # the abstentions by coincidence; here the three numbers separate.
        #
        # [ES] Tres items juzgados: dos respondibles, uno no. El sistema se
        # abstiene en `item-sin-escala` (respondible, o sea falso veto) y en
        # `item-sin-periodo` (no respondible, o sea abstencion correcta), y
        # responde `item-completo`.
        #
        # Cada cifra tiene un denominador DISTINTO, y ese es todo el punto.
        observaciones = observar(self._corpus(), I1)
        referencia = {
            "item-completo": True,
            "item-sin-escala": True,
            "item-sin-periodo": False,
        }
        calidad = resumir(observaciones, referencia=referencia).calidad

        self.assertEqual(calidad.n_respondibles, 2)
        self.assertEqual(calidad.n_no_respondibles, 1)
        self.assertEqual(calidad.n_abstenciones_con_referencia, 2)

        self.assertEqual(calidad.precision_de_abstencion, 0.5)
        self.assertEqual(calidad.tasa_de_abstencion_correcta, 1.0)
        self.assertEqual(calidad.tasa_de_falso_veto, 0.5)
        self.assertAlmostEqual(calidad.cobertura, 1 / 3)

    def test_la_latencia_no_medida_se_reporta_como_no_medida(self):
        # [ES] Un cero afirmaria que el brazo salio gratis.
        resumen = resumir(observar(self._corpus(), I1))
        self.assertFalse(resumen.medicion.medida())
        self.assertIn(
            "latencia, tokens y costo no medidos en esta corrida", resumen.advertencias()
        )

        con_medicion = resumir(
            observar(self._corpus(), I1), medicion=Medicion(latencia_ms=12.5)
        )
        self.assertTrue(con_medicion.medicion.medida())

    def test_el_resumen_lleva_siempre_la_salvedad_de_completitud_y_exactitud(self):
        # [ES] Completitud no es exactitud, y el numero no debe viajar sin eso.
        resumen = resumir(observar(self._corpus(), I1))
        self.assertIn(
            "completitud no es exactitud: un campo poblado puede estar mal",
            resumen.advertencias(),
        )
        self.assertIn("tipologia sin ratificar", " ".join(resumen.advertencias()))

    def test_los_casos_de_confianza_alta_incompleta_se_cuentan(self):
        # [ES] El caso testigo tiene que ser detectable en el agregado, no solo
        # hecho por hecho.
        resumen = resumir(observar(self._corpus(), I1))
        self.assertGreaterEqual(resumen.confianza_alta_con_integridad_incompleta, 1)

    def test_un_resumen_describe_un_solo_brazo(self):
        # [ES] Mezclar brazos en un resumen invalida la comparacion.
        mezclado = observar(self._corpus(), I1) + observar(self._corpus(), I2)
        with self.assertRaises(ValueError):
            resumir(mezclado)


class RegresionDeCorreccion(unittest.TestCase):
    """The ten failures an independent review reproduced, each pinned by a test.

    Every one of these passed the previous suite. They are here so that no
    refactor can quietly restore any of them.

    [ES] Los diez fallos que una revision independiente reprodujo, cada uno
    fijado por una prueba.

    Todos pasaban la suite anterior. Estan aca para que ningun refactor pueda
    restaurarlos en silencio.
    """

    # --- helpers ---

    def _chunk(self, **cambios):
        base = {
            "chunk_uid": "CHK-irrelevante",
            "document_id": "DOC-0009",
            "artifact_id": "ART-SHA256-CCCC",
            "fuente": "Ley_24076_Gas_Natural_TO",
            "titulo": "Articulo 2",
            "contenido": "El transporte y la distribucion de gas natural...",
            "paginas": [3],
            "offset_desde": 900,
            "offset_hasta": 1400,
        }
        base.update(cambios)
        return evidencia_de_chunk(base)

    def _fila_sin_unidad(self):
        """[ES] La fila trae concepto, periodo y valor; la unidad no esta en ella."""
        unidad = {
            "escala": None, "moneda": None, "base": None, "es_porcentaje": False,
            "origen": "ausente", "evidencia_texto": None, "evidencia_ref": None,
            "reglas": [],
        }
        coords = dict(hecho()["cell_coordinates"])
        coords.update({"fila": 9, "col": 2})
        return evidencia_de_hecho_tabular(
            hecho(
                entidad="Transener S.A.",
                row_label="Ingresos por servicios",
                unit=unidad,
                table_segment_uid="TSEG-cuerpo",
                cell_coordinates=coords,
                extraction_warnings=["escala_ausente", "unidad_ausente"],
            )
        )

    def _encabezado_con_unidad(self, **cambios):
        """[ES] El encabezado de la MISMA tabla logica declara escala y moneda."""
        coords = dict(hecho()["cell_coordinates"])
        coords.update({"fila": 0, "col": 2})
        datos = dict(
            entidad="Transener S.A.",
            row_label="Cifras expresadas",
            table_segment_uid="TSEG-encabezado",
            cell_coordinates=coords,
        )
        datos.update(cambios)
        return evidencia_de_hecho_tabular(hecho(**datos))

    # --- 1 y 2: localizable no es soporte ---

    def test_r1_texto_irrelevante_localizable_no_habilita_respuesta(self):
        # A chunk with a heading and a page number is perfectly locatable. It
        # has no value, so its type demanded nothing, so it used to come out
        # "exactly complete" and sufficient - and the system answered with a
        # fragment that may be about anything at all.
        # [ES] Un chunk con titulo y numero de pagina es perfectamente
        # localizable. No tiene valor, asi que su tipo no exigia nada, asi que
        # salia "exactamente completo" y suficiente - y el sistema respondia con
        # un fragmento que puede hablar de cualquier cosa.
        veredicto = verificar(self._chunk())

        self.assertTrue(veredicto.procedencia_exacta)   # si, localizable
        self.assertTrue(veredicto.integridad_exacta)    # si, sin componentes faltantes
        self.assertEqual(veredicto.soporte, NO_VERIFICADO)
        self.assertFalse(veredicto.suficiente())        # y aun asi NO alcanza
        self.assertIn(SOPORTE_NO_VERIFICADO, veredicto.motivos)

    def test_r2_texto_con_soporte_no_verificado_queda_indeterminado(self):
        # Undetermined is NOT an abstention. Abstaining claims "the evidence
        # does not support this"; here nothing was established either way, and
        # scoring it as a correct abstention would credit a judgement never made.
        # [ES] Indeterminado NO es una abstencion. Abstenerse afirma "la
        # evidencia no sostiene esto"; aca no se establecio nada en ningun
        # sentido, y puntuarlo como abstencion correcta acreditaria un juicio que
        # nunca se hizo.
        resultado = ejecutar_ciclo(afirmacion_de("item-texto", (self._chunk(),)))

        self.assertEqual(resultado.decision, INDETERMINADO)
        self.assertNotEqual(resultado.decision, RESPONDER)
        self.assertFalse(resultado.abstuvo())
        self.assertIn(SOPORTE_NO_VERIFICADO, resultado.motivos)

    def test_la_referencia_humana_no_existe_en_el_camino_de_inferencia(self):
        # The previous version of this test asserted the opposite, and it was
        # wrong: it celebrated the leak. `Afirmacion` used to carry
        # `referencia_humana`, it reached `determinar_soporte`, and the Gold
        # label flipped the decision from `indeterminado` to `responder`. The
        # system read the answer key and was then scored against it.
        #
        # The field is gone. Not deprecated, not ignored - absent, so the leak
        # is a TypeError instead of a silent inflation.
        #
        # [ES] La version anterior de esta prueba afirmaba lo contrario, y estaba
        # mal: festejaba la fuga. `Afirmacion` llevaba `referencia_humana`,
        # llegaba a `determinar_soporte`, y la etiqueta del Golden cambiaba la
        # decision de `indeterminado` a `responder`. El sistema leia la hoja de
        # respuestas y despues se puntuaba contra ella.
        #
        # El campo ya no existe. No esta deprecado ni ignorado: esta ausente,
        # asi que la fuga es un TypeError en lugar de una inflacion silenciosa.
        with self.assertRaises(TypeError):
            Afirmacion("item-x", (self._chunk(),), referencia_humana=True)

        self.assertNotIn(
            "referencia_humana",
            inspect.signature(verificar).parameters,
        )
        self.assertNotIn(
            "referencia_humana",
            inspect.signature(determinar_soporte).parameters,
        )

    # --- 3 y 4: composicion solo con vinculo explicito ---

    def test_r3_valor_y_unidad_repartidos_se_componen_con_vinculo_explicito(self):
        # The realistic case: the row carries concept, period and amount; the
        # header of the SAME logical table carries scale and currency. Composing
        # is what turns "the amount has no scale" into a complete, traceable
        # fact - and refusing to compose would report as incomplete something
        # the document states perfectly well.
        # [ES] El caso realista: la fila lleva concepto, periodo e importe; el
        # encabezado de la MISMA tabla logica lleva escala y moneda. Componer es
        # lo que convierte "el importe no tiene escala" en un hecho completo y
        # trazable - y negarse a componer reportaria como incompleto algo que el
        # documento declara perfectamente.
        fila = self._fila_sin_unidad()
        encabezado = self._encabezado_con_unidad()

        self.assertFalse(verificar(fila, especificacion=espec()).integridad_exacta)

        compuesto = componer_una(fila, [fila, encabezado])
        self.assertTrue(compuesto.compuesto())
        self.assertEqual(compuesto.efectiva.escala, "miles")
        self.assertEqual(compuesto.efectiva.moneda, "ARS")
        self.assertTrue(
            verificar(compuesto.efectiva, especificacion=espec()).integridad_exacta
        )

        # The value and the concept stayed put. Only the missing unit travelled.
        # [ES] El valor y el concepto no se movieron. Solo viajo la unidad que
        # faltaba.
        self.assertEqual(compuesto.efectiva.valor, fila.valor)
        self.assertEqual(compuesto.efectiva.concepto, fila.concepto)
        for prohibido in NO_COMPONIBLES:
            self.assertNotIn(prohibido, [a.componente for a in compuesto.aportes])

        # Every borrowed component can be reopened at its own source.
        # [ES] Cada componente prestado se puede reabrir en su propia fuente.
        procedencia = compuesto.procedencia()
        self.assertEqual(procedencia[0]["rol"], "base")
        self.assertEqual(procedencia[0]["table_segment_uid"], "TSEG-cuerpo")
        prestados = {p["rol"]: p for p in procedencia[1:]}
        self.assertIn("aporta:escala", prestados)
        self.assertEqual(prestados["aporta:escala"]["table_segment_uid"], "TSEG-encabezado")
        self.assertEqual(prestados["aporta:escala"]["vinculo"], MISMA_TABLA_LOGICA)

        # And the cycle answers, once, with the composed fact.
        # [ES] Y el ciclo responde, una sola vez, con el hecho compuesto.
        resultado = ejecutar_ciclo(
            afirmacion_de("item-compuesto", (fila, encabezado))
        )
        self.assertEqual(resultado.decision, RESPONDER)
        self.assertEqual(resultado.reintentos_usados, 0)

    def test_r4_fragmentos_no_relacionados_nunca_se_fusionan(self):
        # No link, no donation - however similar the pieces look. This is the
        # rule that stops a plausible number from being assembled out of two
        # unrelated documents.
        # [ES] Sin vinculo no hay donacion, por parecidas que se vean las piezas.
        # Es la regla que impide armar una cifra verosimil con dos documentos sin
        # relacion.
        fila = self._fila_sin_unidad()
        ajeno = self._encabezado_con_unidad(
            document_id="DOC-AJENO", table_uid="TBL-ajena"
        )

        self.assertIsNone(vinculo_explicito(fila, ajeno, "escala"))
        self.assertIsNone(vinculo_explicito(fila, ajeno, "moneda"))

        compuesto = componer_una(fila, [fila, ajeno])
        self.assertFalse(compuesto.compuesto())
        self.assertIsNone(compuesto.efectiva.escala)
        self.assertFalse(
            verificar(compuesto.efectiva, especificacion=espec()).integridad_exacta
        )

    def test_un_periodo_solo_viaja_dentro_de_la_misma_columna(self):
        # The period is declared per COLUMN. Taking it from a neighbouring
        # column would move the figure to another quarter and read as
        # impeccable.
        # [ES] El periodo se declara por COLUMNA. Tomarlo de una columna vecina
        # moveria la cifra a otro trimestre y se leeria impecable.
        coords_receptor = dict(hecho()["cell_coordinates"])
        coords_receptor.update({"fila": 9, "col": 2})
        receptor = evidencia_de_hecho_tabular(
            hecho(period=None, cell_coordinates=coords_receptor,
                  table_segment_uid="TSEG-r")
        )

        coords_vecina = dict(hecho()["cell_coordinates"])
        coords_vecina.update({"fila": 9, "col": 3})
        otra_columna = evidencia_de_hecho_tabular(
            hecho(cell_coordinates=coords_vecina, table_segment_uid="TSEG-v")
        )
        self.assertIsNone(vinculo_explicito(receptor, otra_columna, "periodo"))

        coords_misma = dict(hecho()["cell_coordinates"])
        coords_misma.update({"fila": 0, "col": 2})
        misma_columna = evidencia_de_hecho_tabular(
            hecho(cell_coordinates=coords_misma, table_segment_uid="TSEG-m")
        )
        self.assertEqual(
            vinculo_explicito(receptor, misma_columna, "periodo"),
            MISMA_COLUMNA_DE_LA_MISMA_TABLA,
        )

    # --- 5 y 6: el presupuesto es del item, y el reintento se refleja ---

    def test_r5_dos_hechos_de_un_mismo_item_consumen_un_solo_reintento(self):
        # Two incomplete facts in ONE claim. Running the cycle per fact spent
        # two retries that nobody budgeted; the bound belongs to the question.
        # [ES] Dos hechos incompletos en UNA afirmacion. Correr el ciclo por
        # hecho gastaba dos reintentos que nadie presupuesto; la cota pertenece a
        # la pregunta.
        # Neither can repair the other: both lack the unit, so there is nothing
        # to donate between them and the retry is the only move left.
        # [ES] Ninguno puede reparar al otro: a los dos les falta la unidad, asi
        # que no hay nada que donarse y el reintento es la unica jugada.
        sin_unidad = {
            "escala": None, "moneda": None, "base": None, "es_porcentaje": False,
            "origen": "ausente", "evidencia_texto": None, "evidencia_ref": None,
            "reglas": [],
        }
        primero = self._fila_sin_unidad()
        segundo = evidencia_de_hecho_tabular(
            hecho(
                entidad="Transener S.A.",
                row_label="Costos de explotacion",
                unit=sin_unidad,
                table_segment_uid="TSEG-otro-cuerpo",
            )
        )
        self.assertFalse(verificar(primero, especificacion=espec()).integridad_exacta)
        self.assertFalse(verificar(segundo, especificacion=espec()).integridad_exacta)
        llamadas = []

        def responder(plan):
            llamadas.append(plan)
            return []

        afirmacion = afirmacion_de("item-con-dos-hechos", (primero, segundo))
        resultado = ejecutar_ciclo(afirmacion, adaptador_de_prueba(responder))

        self.assertEqual(len(llamadas), 1)
        self.assertEqual(resultado.reintentos_usados, MAX_REINTENTOS)

        # And through the metrics path, which is where the leak used to happen.
        # [ES] Y por el camino de las metricas, que es donde estaba la fuga.
        observaciones = observar([afirmacion], I2, adaptador_de_prueba(responder))
        self.assertEqual(len(observaciones), 1)
        self.assertEqual(observaciones[0].reintentos_usados, 1)
        self.assertEqual(observaciones[0].item_id, "item-con-dos-hechos")

    def test_r6_la_evidencia_del_reintento_se_refleja_en_la_observacion(self):
        # The retry brings the header that completes the fact. Reading index
        # zero of the initial set reported the state the retry had already
        # superseded, so a successful repair looked like a failure.
        # [ES] El reintento trae el encabezado que completa el hecho. Leer el
        # indice cero del conjunto inicial reportaba el estado que el reintento
        # ya habia superado, asi que una reparacion exitosa parecia una falla.
        fila = self._fila_sin_unidad()
        encabezado = self._encabezado_con_unidad()

        afirmacion = afirmacion_de("item-reparado", (fila,))
        observaciones = observar(
            [afirmacion], I2, adaptador_de_prueba(lambda plan: [encabezado])
        )
        observacion = observaciones[0]

        self.assertEqual(observacion.reintentos_usados, 1)
        self.assertEqual(observacion.evidencias_agregadas, 1)
        # The observation describes the REPAIRED claim, not the initial fragment.
        # [ES] La observacion describe la afirmacion REPARADA, no el fragmento
        # inicial.
        self.assertTrue(observacion.integridad_exacta)
        self.assertTrue(observacion.compuesto)
        self.assertEqual(observacion.decision, RESPONDER)

        # I1, with no retry, still sees it incomplete: that is the difference
        # the two arms exist to measure.
        # [ES] I1, sin reintento, la sigue viendo incompleta: esa es la
        # diferencia que los dos brazos existen para medir.
        sin_reintento = observar([afirmacion], I1)[0]
        self.assertFalse(sin_reintento.integridad_exacta)
        self.assertEqual(sin_reintento.reintentos_usados, 0)

    def test_una_pieza_no_anclada_del_reintento_no_puede_responder(self):
        # A complete, correct fact from another document answers a question
        # nobody asked. It may donate; it may not answer.
        # [ES] Un hecho completo y correcto de otro documento responde una
        # pregunta que nadie hizo. Puede donar; no puede responder.
        fila = self._fila_sin_unidad()
        ajeno = evidencia_de_hecho_tabular(
            hecho(document_id="DOC-AJENO", table_uid="TBL-ajena")
        )
        resultado = ejecutar_ciclo(
            afirmacion_de("item-no-anclado", (fila,)),
            adaptador_de_prueba(lambda plan: [ajeno]),
        )
        self.assertNotEqual(resultado.decision, RESPONDER)
        self.assertEqual(resultado.reintentos_usados, 1)

    # --- 7 y 8: comparabilidad antes que conflicto ---

    def test_r7_ars_y_usd_no_producen_conflicto_numerico(self):
        # Pesos against dollars is not a disagreement, and no conversion is
        # invented to force one. Reporting it as a conflict would manufacture a
        # finding out of two correct figures.
        # [ES] Pesos contra dolares no es un desacuerdo, y no se inventa ninguna
        # conversion para forzarlo. Reportarlo como conflicto fabricaria un
        # hallazgo con dos cifras correctas.
        pesos = dict(hecho()["unit"])
        pesos.update({"moneda": "ARS", "base": "nominal"})
        dolares = dict(hecho()["unit"])
        dolares.update({"moneda": "USD", "base": "nominal"})

        uno = evidencia_de_hecho_tabular(
            hecho(unit=pesos, alcance="consolidado", escenario="real")
        )
        dos = evidencia_de_hecho_tabular(
            hecho(
                unit=dolares, alcance="consolidado", escenario="real",
                value=1234.0, value_raw="1.234",
            )
        )
        self.assertEqual(detectar_conflicto([uno, dos]), {})
        for v in verificar_conjunto([uno, dos]):
            self.assertNotIn(FUENTES_EN_CONFLICTO, v.motivos)

    def test_r8_consolidado_e_individual_no_son_la_misma_afirmacion(self):
        # [ES] Una cifra consolidada y una individual no se contradicen: dicen
        # cosas distintas sobre perimetros distintos.
        unidad = dict(hecho()["unit"])
        unidad["base"] = "nominal"
        consolidado = evidencia_de_hecho_tabular(
            hecho(unit=unidad, alcance="consolidado", escenario="real")
        )
        individual = evidencia_de_hecho_tabular(
            hecho(
                unit=unidad, alcance="individual", escenario="real",
                value=555.0, value_raw="555",
            )
        )
        self.assertEqual(detectar_conflicto([consolidado, individual]), {})

    def test_la_comparacion_de_valores_es_exacta_y_no_de_punto_flotante(self):
        # An accounting identity is exact or it is nothing. Under float
        # arithmetic `0.1 + 0.2` decides whether two figures agree.
        # [ES] Una identidad contable es exacta o no es nada. Con aritmetica de
        # punto flotante, `0.1 + 0.2` decide si dos cifras coinciden.
        unidad = dict(hecho()["unit"])
        unidad.update({"escala": "unidades", "base": "nominal"})
        uno = evidencia_de_hecho_tabular(
            hecho(unit=unidad, alcance="consolidado", escenario="real",
                  value=0.1 + 0.2, value_raw="0,30000000000000004")
        )
        dos = evidencia_de_hecho_tabular(
            hecho(unit=unidad, alcance="consolidado", escenario="real",
                  value=0.3, value_raw="0,3")
        )
        # They really are different numbers, and the exact comparison says so
        # instead of hiding it behind a rounding tolerance.
        # [ES] Realmente son numeros distintos, y la comparacion exacta lo dice
        # en lugar de esconderlo tras una tolerancia de redondeo.
        self.assertEqual(
            set(detectar_conflicto([uno, dos]).values()), {FUENTES_EN_CONFLICTO}
        )

    # --- 9 y 10: la unidad de las metricas ---

    def test_r9_dos_items_del_mismo_segmento_conservan_referencias_distintas(self):
        # Many facts share a `table_segment_uid`. Indexing by it collapsed
        # different claims into one, so a reference given about one of them was
        # applied to the other.
        # [ES] Muchos hechos comparten `table_segment_uid`. Indexar por el
        # colapsaba afirmaciones distintas en una sola, asi que una referencia
        # dada sobre una se aplicaba a la otra.
        uno = evidencia_de_hecho_tabular(hecho(row_label="Ingresos por servicios"))
        dos = evidencia_de_hecho_tabular(hecho(row_label="Costos de explotacion"))
        self.assertEqual(uno.table_segment_uid, dos.table_segment_uid)

        observaciones = observar(
            [
                afirmacion_de("item-A", (uno,), conceptos=("Ingresos por servicios",)),
                afirmacion_de("item-B", (dos,), conceptos=("Costos de explotacion",)),
            ],
            I1,
        )
        self.assertEqual({o.item_id for o in observaciones}, {"item-A", "item-B"})
        self.assertEqual(resumir(observaciones).n_items, 2)

    def test_r10_el_falso_veto_se_divide_por_todos_los_items_respondibles(self):
        # Three answerable items, one of them abstained. The false veto rate is
        # 1/3 - one veto over the answerable population.
        #
        # The old denominator was the ABSTENTIONS: 1/1 = 1.0, which says the
        # system vetoes everything it could answer. It does not; it vetoes one
        # in three. That figure described the composition of the abstentions,
        # not the rate of false vetoes, and it stayed 1.0 however large the
        # corpus grew.
        #
        # [ES] Tres items respondibles, uno abstenido. La tasa de falso veto es
        # 1/3 - un veto sobre la poblacion respondible.
        #
        # El denominador viejo eran las ABSTENCIONES: 1/1 = 1,0, que dice que el
        # sistema veta todo lo que podria responder. No lo hace; veta uno de cada
        # tres. Esa cifra describia la composicion de las abstenciones, no la
        # tasa de falsos vetos, y se quedaba en 1,0 por grande que fuera el
        # corpus.
        unidad_rota = dict(hecho()["unit"])
        unidad_rota["escala"] = None

        afirmaciones = [
            afirmacion_de("resp-1", (evidencia_de_hecho_tabular(hecho()),)),
            afirmacion_de("resp-2", (evidencia_de_hecho_tabular(hecho()),)),
            afirmacion_de(
                "resp-3-vetada",
                (evidencia_de_hecho_tabular(hecho(unit=unidad_rota)),),
            ),
        ]
        referencia = {"resp-1": True, "resp-2": True, "resp-3-vetada": True}
        observaciones = observar(afirmaciones, I1)

        abstenidas = [o for o in observaciones if o.abstuvo()]
        self.assertEqual(len(abstenidas), 1)

        calidad = evaluar_calidad(observaciones, referencia)
        self.assertEqual(calidad.n_respondibles, 3)
        self.assertAlmostEqual(calidad.tasa_de_falso_veto, 1 / 3)
        # The old figure, kept visible for contrast: it is a different question.
        # [ES] La cifra vieja, visible para contrastar: es otra pregunta.
        self.assertEqual(calidad.precision_de_abstencion, 0.0)
        self.assertNotEqual(calidad.tasa_de_falso_veto, 1.0)


class AlineacionAfirmacionEvidencia(unittest.TestCase):
    """Structural completeness is not aboutness. A complete, correct, perfectly
    located row about COSTS does not answer a question about SALES.

    [ES] La completitud estructural no es pertinencia. Una fila completa,
    correcta y perfectamente localizada sobre COSTOS no responde una pregunta
    sobre VENTAS.
    """

    def _ventas(self, **cambios):
        datos = dict(row_label="Ventas", table_segment_uid="TSEG-ventas")
        datos.update(cambios)
        return evidencia_de_hecho_tabular(hecho(**datos))

    def _costos(self, **cambios):
        datos = dict(row_label="Costos de explotacion", table_segment_uid="TSEG-costos")
        datos.update(cambios)
        return evidencia_de_hecho_tabular(hecho(**datos))

    def _pregunta_ventas(self, item_id, evidencias):
        return Afirmacion(
            item_id=item_id,
            evidencias=tuple(evidencias),
            pregunta="Cuales fueron las ventas?",
            especificacion=Especificacion(conceptos=("Ventas",)),
        )

    def test_a1_ventas_con_evidencia_de_costos_no_responde(self):
        # The reproduction: question about sales, evidence about costs. Complete,
        # located, traceable, high confidence - and about something else.
        # [ES] La reproduccion: pregunta por ventas, evidencia de costos.
        # Completa, localizada, trazable, de confianza alta - y sobre otra cosa.
        costos = self._costos()
        veredicto = verificar(costos, especificacion=Especificacion(conceptos=("Ventas",)))

        self.assertTrue(veredicto.integridad_exacta)
        self.assertTrue(veredicto.procedencia_exacta)
        self.assertEqual(veredicto.soporte, NO_VERIFICADO)
        self.assertIn(ALINEACION_NO_VERIFICADA, veredicto.motivos)

        resultado = ejecutar_ciclo(self._pregunta_ventas("item-a1", [costos]))
        self.assertNotEqual(resultado.decision, RESPONDER)
        self.assertEqual(resultado.decision, INDETERMINADO)

    def test_a2_el_reintento_no_responde_ventas_con_ebitda_de_la_misma_tabla(self):
        # Same logical table authorises DONATING a component. It does not make
        # EBITDA an answer about sales. This is the case where the previous
        # anchoring rule was not enough: the piece was anchored, and still about
        # something else.
        # [ES] La misma tabla logica autoriza a DONAR un componente. No convierte
        # al EBITDA en una respuesta sobre ventas. Este es el caso donde la regla
        # de anclaje anterior no alcanzaba: la pieza estaba anclada, y aun asi
        # hablaba de otra cosa.
        ventas_sin_valor = self._ventas(value=None, value_raw="-")
        ebitda = evidencia_de_hecho_tabular(
            hecho(row_label="EBITDA", table_segment_uid="TSEG-ebitda")
        )

        resultado = ejecutar_ciclo(
            self._pregunta_ventas("item-a2", [ventas_sin_valor]),
            adaptador_de_prueba(lambda plan: [ebitda]),
        )
        self.assertEqual(resultado.reintentos_usados, 1)
        self.assertNotEqual(resultado.decision, RESPONDER)

    def test_a3_evidencia_alineada_con_ventas_si_responde(self):
        # [ES] El caso positivo: si la evidencia habla de lo que se pregunto, se
        # responde. La regla no es "nunca responder": es "responder lo que se
        # pregunto".
        resultado = ejecutar_ciclo(self._pregunta_ventas("item-a3", [self._ventas()]))
        self.assertEqual(resultado.decision, RESPONDER)
        gobernante = resultado.evidencia_gobernante()
        self.assertEqual(gobernante.concepto, "Ventas")

    def test_la_alineacion_conceptual_es_igualdad_exacta_y_nada_mas(self):
        # An extended label is NOT the declared concept. "Resultado financiero"
        # is a different line of the same statement than "Resultado", and
        # "Ventas netas" is a different figure than "Ventas". A prefix rule
        # would have the system inventing the synonymy itself, which is a domain
        # judgement this layer has no standing to make.
        #
        # The claim declares what it accepts. That is one line of the Golden, it
        # is auditable, and a reviewer can see exactly which labels were
        # admitted.
        #
        # [ES] Una etiqueta extendida NO es el concepto declarado. "Resultado
        # financiero" es otra linea del mismo estado que "Resultado", y "Ventas
        # netas" es otra cifra que "Ventas". Una regla de prefijo pondria al
        # sistema a inventar la sinonimia por su cuenta, que es un juicio de
        # dominio para el que esta capa no tiene autoridad.
        #
        # La afirmacion declara lo que acepta. Es una linea del Golden, es
        # auditable, y un revisor ve exactamente que etiquetas se admitieron.
        self.assertFalse(
            alineada(
                self._ventas(row_label="Resultado financiero"),
                Especificacion(conceptos=("Resultado",)),
            )
        )
        self.assertFalse(
            alineada(
                self._ventas(row_label="Ventas netas"),
                Especificacion(conceptos=("Ventas",)),
            )
        )
        self.assertTrue(
            alineada(
                self._ventas(row_label="Ventas netas"),
                Especificacion(conceptos=("Ventas", "Ventas netas")),
            )
        )
        # Neither substring nor suffix, in any direction.
        # [ES] Ni subcadena ni sufijo, en ninguna direccion.
        self.assertFalse(
            alineada(
                self._ventas(row_label="Costo de ventas"),
                Especificacion(conceptos=("Ventas",)),
            )
        )
        self.assertFalse(
            alineada(
                self._ventas(row_label="Ventas"),
                Especificacion(conceptos=("Ventas netas",)),
            )
        )

    def test_solo_se_normalizan_mayusculas_acentos_y_espacios(self):
        # The one liberty taken with a label: the same string typed differently
        # is the same concept. Nothing beyond that.
        # [ES] La unica libertad que se toma con una etiqueta: la misma cadena
        # escrita distinto es el mismo concepto. Nada mas alla de eso.
        pedido = Especificacion(conceptos=("Resultado del periodo",))
        for variante in ("resultado del periodo", "RESULTADO DEL PERÍODO",
                         "  Resultado   del  período  "):
            self.assertTrue(
                alineada(self._ventas(row_label=variante), pedido), variante
            )

    def test_sin_especificacion_ningun_hecho_puede_gobernar(self):
        # Without knowing what was asked, "this fact answers it" is an
        # assumption, not a finding.
        # [ES] Sin saber que se pregunto, "este hecho lo responde" es un
        # supuesto, no un hallazgo.
        resultado = ejecutar_ciclo(Afirmacion("item-sin-espec", (self._ventas(),)))
        self.assertEqual(resultado.decision, INDETERMINADO)
        self.assertIn(SOPORTE_NO_VERIFICADO, resultado.motivos)

    def test_la_pregunta_en_texto_libre_no_interviene_en_ninguna_decision(self):
        # Two claims, the same evidence and specification, opposite questions.
        # If the prose mattered, these would differ - and matching prose to a
        # fact would need a model, which this layer must not contain.
        # [ES] Dos afirmaciones, la misma evidencia y especificacion, preguntas
        # opuestas. Si la prosa influyera, darian distinto - y aparear prosa con
        # un hecho exigiria un modelo, que esta capa no debe contener.
        evidencia = self._ventas()
        espec_ventas = Especificacion(conceptos=("Ventas",))
        una = Afirmacion("q1", (evidencia,), pregunta="Cuales fueron las ventas?",
                         especificacion=espec_ventas)
        otra = Afirmacion("q2", (evidencia,), pregunta="Cual fue el precio de la luna?",
                          especificacion=espec_ventas)
        self.assertEqual(
            ejecutar_ciclo(una).decision, ejecutar_ciclo(otra).decision
        )

    def test_ningun_string_externo_habilita_responder_una_afirmacion_incompatible(self):
        # This test asserted the OPPOSITE and it was wrong. A piece used to
        # carry a `soporte_declarado` string naming the claim it supported, and
        # that string alone granted `sostiene` - so a complete row reading
        # "Costos de explotacion" answered a question about sales, because a
        # field in a file said so.
        #
        # The field had no producer, no method, no version and no verifiable
        # provenance: an unaudited bypass shaped like an audit trail. It is
        # removed from the contract, so setting it is a TypeError, and it is no
        # longer read from `hechos.jsonl` either.
        #
        # PENDING WORK: a real external support link would need `item_id`,
        # producer, method, version and traceable provenance, plus an aligner
        # frozen and evaluated independently - and it could never come from the
        # evaluation Gold. Not implemented here.
        #
        # [ES] Esta prueba afirmaba lo CONTRARIO y estaba mal. Una pieza llevaba
        # un string `soporte_declarado` con el nombre de la afirmacion que
        # sostenia, y ese string solo otorgaba `sostiene` - asi que una fila
        # completa que decia "Costos de explotacion" respondia una pregunta sobre
        # ventas, porque un campo de un archivo lo afirmaba.
        #
        # El campo no tenia productor, ni metodo, ni version, ni procedencia
        # verificable: una valvula sin auditar con forma de pista de auditoria.
        # Se elimino del contrato, asi que asignarlo es un TypeError, y tampoco
        # se lee ya desde `hechos.jsonl`.
        self.assertNotIn(
            "soporte_declarado", {f.name for f in dataclasses.fields(Evidencia)}
        )
        with self.assertRaises(TypeError):
            Evidencia(
                modalidad=MODALIDAD_TABLA,
                document_id="DOC-0001",
                artifact_id="ART-X",
                fuente="x",
                localizacion=Localizacion(),
                soporte_declarado="item-a7",
            )

        # Even smuggled in through the serialized record, it grants nothing:
        # the contract does not read the key at all.
        # [ES] Ni siquiera colandolo por el registro serializado otorga nada: el
        # contrato directamente no lee la clave.
        contrabando = evidencia_de_hecho_tabular(
            hecho(row_label="Costos de explotacion", soporte_declarado="item-a7")
        )
        resultado = ejecutar_ciclo(
            Afirmacion(
                "item-a7", (contrabando,),
                especificacion=Especificacion(conceptos=("Ventas",)),
            )
        )
        self.assertNotEqual(resultado.decision, RESPONDER)
        self.assertEqual(resultado.decision, INDETERMINADO)
        self.assertIn(ALINEACION_NO_VERIFICADA, resultado.motivos)

    def test_el_texto_nunca_alcanza_soporte_por_esta_capa(self):
        # Declared scope: this deterministic layer validates integrity and
        # alignment of STRUCTURED TABULAR facts. Text remains a retrievable
        # representation of the RAG, and its semantic support stays
        # `no_verificado` until an independent mechanism exists. That mechanism
        # is not being implemented here.
        # [ES] Alcance declarado: esta capa deterministica valida integridad y
        # alineacion de HECHOS TABULARES ESTRUCTURADOS. El texto sigue siendo una
        # representacion recuperable del RAG, y su soporte semantico queda
        # `no_verificado` hasta que exista un mecanismo independiente. Ese
        # mecanismo no se implementa aca.
        chunk = evidencia_de_chunk(
            {
                "chunk_uid": "CHK-ventas",
                "document_id": "DOC-0009",
                "artifact_id": "ART-SHA256-CCCC",
                "fuente": "TGS_EEFF_2025_09",
                "titulo": "Ventas",
                "contenido": "Las ventas del ejercicio ascendieron a...",
                "paginas": [4],
                "offset_desde": 10,
                "offset_hasta": 90,
            }
        )
        # Its title is EXACTLY the declared concept, and it still does not
        # sustain: alignment of prose is not something a rule can settle.
        # [ES] Su titulo es EXACTAMENTE el concepto declarado, y aun asi no
        # sostiene: la alineacion de prosa no es algo que una regla resuelva.
        resultado = ejecutar_ciclo(
            Afirmacion(
                "item-texto-ventas", (chunk,),
                especificacion=Especificacion(conceptos=("Ventas",)),
            )
        )
        self.assertEqual(resultado.decision, INDETERMINADO)
        self.assertEqual(resultado.veredicto_gobernante().soporte, NO_VERIFICADO)

    def test_a4_la_etiqueta_gold_no_cambia_la_prediccion(self):
        # THE LEAK TEST. Same evidence, same claim, and the two possible Gold
        # labels. The decision, the reasons, the support and the retry count must
        # be byte-identical: the reference evaluates the prediction, it does not
        # participate in it.
        #
        # [ES] LA PRUEBA DE LA FUGA. La misma evidencia, la misma afirmacion, y
        # las dos etiquetas Gold posibles. La decision, los motivos, el soporte y
        # el conteo de reintentos tienen que ser identicos: la referencia evalua
        # la prediccion, no participa de ella.
        afirmacion = self._pregunta_ventas("item-gold", [self._ventas()])
        prediccion = observar([afirmacion], I1)[0]

        con_gold_true = resumir([prediccion], referencia={"item-gold": True})
        con_gold_false = resumir([prediccion], referencia={"item-gold": False})

        # The prediction is one object, produced before either label existed.
        # [ES] La prediccion es un solo objeto, producido antes de que existiera
        # ninguna de las dos etiquetas.
        for resumen in (con_gold_true, con_gold_false):
            self.assertEqual(resumen.por_documento[0].n, 1)
        self.assertEqual(
            con_gold_true.global_agrupado_no_inferencial,
            con_gold_false.global_agrupado_no_inferencial,
        )

        # And running the whole cycle again under each label yields the same
        # decision, because no label can reach it.
        # [ES] Y volver a correr el ciclo entero bajo cada etiqueta da la misma
        # decision, porque ninguna etiqueta puede llegar hasta ahi.
        repetida = observar([afirmacion], I1)[0]
        self.assertEqual(prediccion.decision, repetida.decision)
        self.assertEqual(prediccion.soporte, repetida.soporte)
        self.assertEqual(prediccion.motivos, repetida.motivos)
        self.assertEqual(prediccion.reintentos_usados, repetida.reintentos_usados)

        # Only the QUALITY figures move with the label, and only they may.
        # [ES] Solo las cifras de CALIDAD se mueven con la etiqueta, y solo ellas
        # pueden hacerlo.
        self.assertNotEqual(
            con_gold_true.calidad.tasa_de_falso_veto,
            con_gold_false.calidad.tasa_de_falso_veto,
        )


class ComposicionInvarianteAlOrden(unittest.TestCase):
    """Two incompatible headers must not resolve into whichever arrived first.

    [ES] Dos encabezados incompatibles no deben resolverse en el que haya
    llegado primero.
    """

    def _receptor(self):
        sin_unidad = {
            "escala": None, "moneda": None, "base": None, "es_porcentaje": False,
            "origen": "ausente", "evidencia_texto": None, "evidencia_ref": None,
            "reglas": [],
        }
        return evidencia_de_hecho_tabular(
            hecho(unit=sin_unidad, table_segment_uid="TSEG-cuerpo")
        )

    def _encabezado(self, escala, moneda, segmento):
        unidad = dict(hecho()["unit"])
        unidad.update({"escala": escala, "moneda": moneda})
        return evidencia_de_hecho_tabular(
            hecho(unit=unidad, table_segment_uid=segmento)
        )

    def test_a5_dos_unidades_incompatibles_no_se_componen(self):
        # miles/ARS against millones/USD. Completing from either one would
        # produce a figure a thousand times off, in the wrong currency, looking
        # entirely ordinary. The component stays missing and says why.
        # [ES] miles/ARS contra millones/USD. Completar con cualquiera de los dos
        # daria una cifra mil veces corrida, en la moneda equivocada, con aspecto
        # del todo normal. El componente queda faltante y dice por que.
        receptor = self._receptor()
        uno = self._encabezado("miles", "ARS", "TSEG-h1")
        otro = self._encabezado("millones", "USD", "TSEG-h2")

        compuesto = componer_una(receptor, [receptor, uno, otro])

        self.assertFalse(compuesto.compuesto())
        self.assertTrue(compuesto.ambiguo())
        self.assertIn("unidad", compuesto.ambiguedades)
        self.assertIsNone(compuesto.efectiva.escala)
        self.assertIsNone(compuesto.efectiva.moneda)

        veredicto = verificar(compuesto.efectiva, especificacion=espec())
        self.assertIn(APORTE_AMBIGUO, veredicto.motivos)
        self.assertFalse(veredicto.integridad_exacta)

    def test_a6_invertir_el_orden_de_los_donantes_no_cambia_el_resultado(self):
        # The bug in one line: first-valid-donor made the answer depend on the
        # order the pieces happened to arrive in.
        # [ES] El fallo en una linea: el primer-donante-valido hacia que la
        # respuesta dependiera del orden en que llegaron las piezas.
        receptor = self._receptor()
        uno = self._encabezado("miles", "ARS", "TSEG-h1")
        otro = self._encabezado("millones", "USD", "TSEG-h2")

        directo = componer_una(receptor, [receptor, uno, otro])
        inverso = componer_una(receptor, [receptor, otro, uno])

        self.assertEqual(directo.efectiva.escala, inverso.efectiva.escala)
        self.assertEqual(directo.efectiva.moneda, inverso.efectiva.moneda)
        self.assertEqual(directo.ambiguedades, inverso.ambiguedades)
        self.assertEqual(directo.compuesto(), inverso.compuesto())

    def test_a7_donantes_duplicados_y_consistentes_si_componen(self):
        # Ambiguity is disagreement, not multiplicity. Three headers saying the
        # same thing are one offer, and refusing to compose there would report as
        # incomplete a fact the document states three times over.
        # [ES] La ambiguedad es discrepancia, no multiplicidad. Tres encabezados
        # que dicen lo mismo son una sola oferta, y negarse a componer ahi
        # reportaria como incompleto un hecho que el documento declara tres veces.
        receptor = self._receptor()
        donantes = [
            self._encabezado("miles", "ARS", "TSEG-h1"),
            self._encabezado("miles", "ARS", "TSEG-h2"),
            self._encabezado("miles", "ARS", "TSEG-h3"),
        ]
        compuesto = componer_una(receptor, [receptor] + donantes)

        self.assertTrue(compuesto.compuesto())
        self.assertFalse(compuesto.ambiguo())
        self.assertEqual(compuesto.efectiva.escala, "miles")
        self.assertEqual(compuesto.efectiva.moneda, "ARS")
        self.assertTrue(
            verificar(compuesto.efectiva, especificacion=espec()).integridad_exacta
        )

        # And the order of three identical donors is equally irrelevant.
        # [ES] Y el orden de tres donantes identicos es igual de irrelevante.
        inverso = componer_una(receptor, [receptor] + list(reversed(donantes)))
        self.assertEqual(compuesto.efectiva.escala, inverso.efectiva.escala)
        self.assertEqual(compuesto.efectiva.moneda, inverso.efectiva.moneda)

    def test_la_escala_y_la_moneda_no_se_toman_de_donantes_distintos(self):
        # One header declares only the scale, another only the currency. Taking
        # one from each would assemble a unit that never appeared together
        # anywhere in the document.
        # [ES] Un encabezado declara solo la escala, otro solo la moneda. Tomar
        # uno de cada uno armaria una unidad que nunca aparecio junta en ningun
        # lugar del documento.
        receptor = self._receptor()
        solo_escala = self._encabezado("millones", None, "TSEG-h1")
        solo_moneda = self._encabezado(None, "USD", "TSEG-h2")

        compuesto = componer_una(receptor, [receptor, solo_escala, solo_moneda])

        self.assertTrue(compuesto.ambiguo())
        self.assertFalse(
            compuesto.efectiva.escala is not None
            and compuesto.efectiva.moneda is not None
        )

    def test_un_donante_que_contradice_la_unidad_presente_no_completa_la_otra_mitad(self):
        # The row already says "miles". A header saying "millones" is not
        # completing it, it is disagreeing - so its currency is not borrowed
        # either.
        # [ES] La fila ya dice "miles". Un encabezado que dice "millones" no la
        # esta completando, esta discrepando - asi que tampoco se le toma la
        # moneda.
        unidad = dict(hecho()["unit"])
        unidad.update({"escala": "miles", "moneda": None})
        receptor = evidencia_de_hecho_tabular(
            hecho(unit=unidad, table_segment_uid="TSEG-cuerpo")
        )
        incompatible = self._encabezado("millones", "USD", "TSEG-h1")

        compuesto = componer_una(receptor, [receptor, incompatible])
        self.assertIsNone(compuesto.efectiva.moneda)
        self.assertEqual(compuesto.efectiva.escala, "miles")


if __name__ == "__main__":
    unittest.main()
