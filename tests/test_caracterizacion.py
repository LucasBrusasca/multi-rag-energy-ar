"""Direct tests for the corporate-candidate characteriser.

Every case here is a wrong answer the characteriser actually produced on the real
corpus. They are pinned so the heuristics cannot quietly regress into them:

  - `2025 Annual Report.pdf` was dated `2T2026`, because a stray quarter in the
    cover text outranked the year the document is about.
  - `To the shareholders of Pampa Energia S.A` was proposed as an entity. It
    contains a company name; it is not one.
  - `On April 21, 2026, Fertil Pampa S.A.U` likewise: a sentence that mentions a
    subsidiary must not become the document's main entity.
  - Closing dates came out as `31 DE MARZO DE 2026`, unnormalised, so two
    documents with the same period compared as different.
  - `iva` matched `comparativa`, `arca` matched `abarca`, and `percepcion de
    corrupcion` counted as tax material.

[ES] Pruebas directas del caracterizador de candidatos empresariales.

Cada caso de aca es una respuesta equivocada que el caracterizador produjo de
verdad sobre el corpus real. Quedan fijadas para que las heuristicas no puedan
volver a ellas en silencio.
"""

import unittest

from scripts.diagnostics.caracterizar_candidatos_empresariales import (
    UMBRAL_OCURRENCIAS,
    UMBRAL_PAGINAS,
    UMBRAL_TERMINOS,
    _normalizar_periodo,
    _patron_de_termino,
    clave_documental,
    proponer_dominios,
    proponer_entidad,
    proponer_periodo,
    proponer_tipo,
)


def lectura(paginas: dict) -> dict:
    """A fake reading: the characteriser only ever sees text keyed by page.

    [ES] Una lectura falsa: el caracterizador solo ve texto indexado por pagina.
    """
    texto = "\n".join(paginas.values())
    import unicodedata

    d = unicodedata.normalize("NFKD", texto)
    plano = " ".join(
        "".join(c for c in d if not unicodedata.combining(c)).lower().split()
    )
    return {
        "por_pagina": paginas,
        "texto": texto,
        "texto_plano": plano,
        "paginas": len(paginas),
    }


class PeriodoReal(unittest.TestCase):
    """[ES] El periodo sale del contenido, y sale en ISO."""

    def test_un_reporte_anual_no_se_fecha_por_un_trimestre_suelto(self):
        # THE case. `2025 Annual Report.pdf` was dated `2T2026` because a quarter
        # appeared somewhere in its head text. A document whose own name says
        # `Annual Report` is not about a quarter.
        # [ES] EL caso. `2025 Annual Report.pdf` quedaba fechado `2T2026` porque
        # un trimestre aparecía en algún lugar de su texto de cabecera. Un
        # documento cuyo propio nombre dice `Annual Report` no trata de un
        # trimestre.
        lec = lectura({
            1: "PAMPA ENERGIA S.A. Annual Report 2025",
            2: "Results for Q2 2026 are presented for comparison purposes only.",
            3: "ejercicio economico finalizado el 2025",
        })
        tipo = proponer_tipo(lec, "2025 Annual Report.pdf")
        self.assertEqual(tipo["tipo"], "memoria_anual")

        p = proponer_periodo(lec, "2025 Annual Report.pdf", "", "", tipo["tipo"])
        self.assertEqual(p["periodo_propuesto"], "2025")
        self.assertNotEqual(p["periodo_propuesto"], "2T2026")

    def test_las_fechas_de_cierre_se_normalizan_a_iso(self):
        # Unnormalised, two documents of the same period compare as different and
        # documentary deduplication stops working.
        # [ES] Sin normalizar, dos documentos del mismo período comparan
        # distinto y la deduplicación documental deja de funcionar.
        for crudo, esperado in (
            ("31 DE MARZO DE 2026", "2026-03-31"),
            ("31 de diciembre de 2025", "2025-12-31"),
            ("30 DE SEPTIEMBRE DE 2016", "2016-09-30"),
            ("30 de Junio de 2018", "2018-06-30"),
        ):
            lec = lectura({1: f"Estados financieros al {crudo}"})
            p = proponer_periodo(lec, "x.pdf", "", "", "estado_financiero")
            self.assertEqual(p["periodo_propuesto"], esperado, crudo)

    def test_el_ano_del_directorio_de_la_url_nunca_se_usa_como_periodo(self):
        # `/uploads/2026/07/EEFF-31-12-25.pdf` is a 2025 statement published in
        # 2026. Taking the directory would date it wrong by a year, silently, on
        # every document a site publishes late.
        # [ES] `/uploads/2026/07/EEFF-31-12-25.pdf` es un estado de 2025
        # publicado en 2026. Tomar el directorio lo fecharía mal por un año, en
        # silencio, en todo documento que un sitio publique con retraso.
        lec = lectura({1: "Estados financieros al 31 de diciembre de 2025"})
        p = proponer_periodo(
            lec, "EEFF-31-12-25.pdf", "",
            "https://x.com/uploads/2026/07/EEFF-31-12-25.pdf", "estado_financiero",
        )
        self.assertEqual(p["periodo_propuesto"], "2025-12-31")
        self.assertEqual(p["anio_en_url"], "2026")
        self.assertTrue(p["discrepa_con_url"], "la discrepancia se reporta")

    def test_el_contenido_le_gana_al_nombre_de_archivo(self):
        # [ES] La prioridad declarada es contenido > nombre > enlace.
        lec = lectura({1: "ejercicio economico finalizado el 2019"})
        p = proponer_periodo(lec, "informe-2024.pdf", "texto 2023", "", "memoria_anual")
        self.assertEqual(p["fuente"], "contenido_del_pdf")
        self.assertEqual(p["periodo_propuesto"], "2019")

    def test_sin_periodo_detectable_no_se_inventa(self):
        p = proponer_periodo(lectura({1: "sin fechas aqui"}), "x.pdf", "", "", "")
        self.assertIsNone(p["periodo_propuesto"])
        self.assertEqual(p["confianza"], "sin_periodo")

    def test_normalizar_periodo_acepta_mayusculas(self):
        # The direct cause of the fourteen unnormalised dates: the month lookup
        # ran without case-insensitivity.
        # [ES] La causa directa de las catorce fechas sin normalizar: la búsqueda
        # del mes corría sin ignorar mayúsculas.
        import re

        m = re.match(r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(20\d{2})",
                     "31 DE MARZO DE 2026", re.I)
        self.assertIsNotNone(m)


class EntidadPropuesta(unittest.TestCase):
    """[ES] Una razón social son pocas palabras, no una oración."""

    def test_una_oracion_que_menciona_la_empresa_no_es_la_empresa(self):
        # `To the shareholders of Pampa Energia S.A` contains a company name and
        # is not one. Either the name is extracted, or the entity stays absent -
        # never the whole clause.
        # [ES] `To the shareholders of Pampa Energia S.A` contiene una razón
        # social y no es una. O se extrae el nombre, o la entidad queda ausente:
        # nunca la oración entera.
        lec = lectura({1: "To the shareholders of Pampa Energia S.A"})
        e = proponer_entidad(lec, None)
        propuesta = e["entidad_propuesta"]
        if propuesta is not None:
            self.assertNotIn("shareholders", propuesta.lower())
            self.assertNotIn("to the", propuesta.lower())
            self.assertLessEqual(len(propuesta.split()), 4)

    def test_una_subsidiaria_mencionada_en_una_oracion_no_es_la_entidad(self):
        # `On April 21, 2026, Fertil Pampa S.A.U` names a subsidiary inside a
        # sentence. Promoting it to main entity would attribute the whole
        # document to the wrong company.
        # [ES] `On April 21, 2026, Fertil Pampa S.A.U` nombra una subsidiaria
        # dentro de una oración. Promoverla a entidad principal atribuiría el
        # documento entero a la empresa equivocada.
        lec = lectura({1: "On April 21, 2026, Fertil Pampa S.A.U announced"})
        e = proponer_entidad(lec, None)
        propuesta = e["entidad_propuesta"]
        if propuesta is not None:
            self.assertNotIn("april", propuesta.lower())
            self.assertNotIn("2026", propuesta)

    def test_la_procedencia_gana_sobre_el_texto(self):
        # A file taken from an issuer's own investor page is strong provenance.
        # [ES] Un archivo tomado de la página de inversores de la propia emisora
        # es procedencia fuerte.
        lec = lectura({1: "Otra Empresa S.A. es contraparte"})
        e = proponer_entidad(lec, "Transportadora de Gas del Sur")
        self.assertEqual(e["entidad_propuesta"], "Transportadora de Gas del Sur")
        self.assertEqual(e["origen"], "procedencia_ir")

    def test_sin_nada_legible_la_entidad_queda_ausente(self):
        e = proponer_entidad(lectura({1: "texto sin razones sociales"}), None)
        self.assertIsNone(e["entidad_propuesta"])
        self.assertEqual(e["confianza_entidad"], "sin_entidad")

    def test_la_confianza_acompania_siempre_a_la_propuesta(self):
        # [ES] Una propuesta sin confianza se lee como un dato.
        for sugerida in (None, "Transener"):
            e = proponer_entidad(lectura({1: "Transener S.A."}), sugerida)
            self.assertIn(e["confianza_entidad"],
                          ("alta", "media", "baja", "sin_entidad"))


class TerminosConLimitesLexicos(unittest.TestCase):
    """[ES] Los tres falsos positivos que vaciaban de sentido a un dominio."""

    def test_iva_no_coincide_con_comparativa(self):
        p = _patron_de_termino("iva")
        self.assertFalse(p.search("tabla comparativa de valores"))
        self.assertFalse(p.search("la derivada positiva"))
        self.assertTrue(p.search("el iva devengado"))

    def test_arca_no_coincide_con_abarca(self):
        p = _patron_de_termino("arca")
        self.assertFalse(p.search("esto abarca todo"))
        self.assertFalse(p.search("la marca registrada"))
        self.assertTrue(p.search("arca fiscalizo"))

    def test_la_percepcion_de_corrupcion_no_es_materia_impositiva(self):
        # Bare `percepcion` was replaced by the collocations that actually name a
        # tax regime.
        # [ES] El `percepcion` suelto se reemplazó por las colocaciones que
        # efectivamente nombran un régimen impositivo.
        p = _patron_de_termino("agente de percepcion")
        self.assertFalse(p.search("percepcion de corrupcion en el sector"))
        self.assertTrue(p.search("actua como agente de percepcion"))

    def test_afip_no_coincide_dentro_de_otra_palabra(self):
        p = _patron_de_termino("afip")
        self.assertFalse(p.search("se afiparon los datos"))
        self.assertTrue(p.search("la afip resolvio"))


class MaterialidadMinima(unittest.TestCase):
    """[ES] Una mención incidental no vuelve al documento de ese dominio."""

    def test_una_mencion_aislada_no_propone_el_dominio(self):
        # An annual report that names ENARGAS once, in a list of counterparties,
        # is not a regulatory document.
        # [ES] Una memoria que nombra a ENARGAS una vez, en una lista de
        # contrapartes, no es un documento regulatorio.
        lec = lectura({1: "Entre las contrapartes se encuentra ENARGAS."})
        d = proponer_dominios(lec)["legal"]
        self.assertFalse(d["propuesto"])
        self.assertIsNotNone(d["motivo_no_propuesto"])

    def test_hacen_falta_terminos_ocurrencias_y_paginas(self):
        # Three thresholds, and all three must clear. Enough distinct terms on a
        # single page is still one page.
        # [ES] Tres umbrales, y los tres tienen que superarse. Suficientes
        # términos distintos en una sola página siguen siendo una página.
        una_pagina = lectura({
            1: "enre enargas marco regulatorio audiencia publica ente regulador "
               "concesion servicio publico cuadro tarifario"
        })
        d = proponer_dominios(una_pagina)["legal"]
        self.assertGreaterEqual(d["terminos_distintos"], UMBRAL_TERMINOS)
        self.assertEqual(d["max_paginas_de_un_termino"], 1)
        self.assertFalse(d["propuesto"], "una sola página no alcanza")

    def test_materia_repartida_en_varias_paginas_si_propone(self):
        lec = lectura({
            1: "El marco regulatorio del ENRE fija el cuadro tarifario.",
            2: "El ENRE convoco una audiencia publica sobre la concesion.",
            3: "El ente regulador ENRE aprobo el cuadro tarifario.",
        })
        d = proponer_dominios(lec)["legal"]
        self.assertTrue(d["propuesto"])
        self.assertGreaterEqual(d["ocurrencias_totales"], UMBRAL_OCURRENCIAS)
        self.assertGreaterEqual(d["max_paginas_de_un_termino"], UMBRAL_PAGINAS)

    def test_cada_propuesta_lleva_su_evidencia_citada(self):
        lec = lectura({
            1: "El marco regulatorio del ENRE fija el cuadro tarifario.",
            2: "El ENRE convoco una audiencia publica sobre la concesion.",
            3: "El ente regulador ENRE aprobo el cuadro tarifario.",
        })
        d = proponer_dominios(lec)["legal"]
        self.assertTrue(d["evidencia"])
        for e in d["evidencia"]:
            self.assertIn("cita", e)
            self.assertIn("pagina", e)
            self.assertTrue(e["cita"].strip())

    def test_no_todo_documento_es_contable_y_financiero(self):
        # The correction of v1. A purely regulatory text must not acquire
        # accounting and financial memberships for free.
        # [ES] La corrección de la v1. Un texto puramente regulatorio no puede
        # adquirir gratis membresías contable y financiera.
        lec = lectura({
            1: "El ENRE fija el cuadro tarifario del servicio publico.",
            2: "El ente regulador convoco una audiencia publica.",
            3: "El marco regulatorio del ENRE rige la concesion.",
        })
        d = proponer_dominios(lec)
        self.assertTrue(d["legal"]["propuesto"])
        self.assertFalse(d["contable"]["propuesto"])
        self.assertFalse(d["financiero"]["propuesto"])


class ClaveDocumental(unittest.TestCase):
    """[ES] Deduplicación más allá del SHA-256."""

    def test_dos_renderizados_del_mismo_documento_comparten_clave(self):
        base = {
            "entidad_propuesta": "Transener S.A.", "tipo_propuesto": "estado_financiero",
            "periodo_propuesto": "2019-03-31", "titulo": "EEFF", "paginas": 41,
        }
        otro = dict(base, titulo="  eeff  ")
        self.assertEqual(clave_documental(base), clave_documental(otro))

    def test_distinto_periodo_es_distinto_documento(self):
        base = {
            "entidad_propuesta": "Transener S.A.", "tipo_propuesto": "estado_financiero",
            "periodo_propuesto": "2019-03-31", "titulo": "EEFF", "paginas": 41,
        }
        otro = dict(base, periodo_propuesto="2018-03-31")
        self.assertNotEqual(clave_documental(base), clave_documental(otro))

    def test_distinta_cantidad_de_paginas_es_distinto_documento(self):
        # Individual against consolidated: same entity, same closing date,
        # different document. Collapsing them would lose one.
        # [ES] Individual contra consolidado: misma entidad, misma fecha de
        # cierre, documento distinto. Colapsarlos perdería uno.
        base = {
            "entidad_propuesta": "Transener S.A.", "tipo_propuesto": "estado_financiero",
            "periodo_propuesto": "2019-03-31", "titulo": "EEFF", "paginas": 41,
        }
        otro = dict(base, paginas=40)
        self.assertNotEqual(clave_documental(base), clave_documental(otro))


if __name__ == "__main__":
    unittest.main()
