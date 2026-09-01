"""Tests for the two-stage blind review interface.

The behavioural half runs the interface's own validation and export functions
under node. Asserting that a file "contains a blind stage" proves nothing about
whether the proposal is actually withheld.

[ES] Pruebas de la interfaz de revision ciega en dos etapas.

La mitad de comportamiento corre las propias funciones de validacion y
exportacion de la interfaz con node. Afirmar que un archivo "tiene una etapa
ciega" no prueba nada sobre si la propuesta se oculta de verdad.
"""

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from multirag.paths import EXPERIMENTS_DIR

HTML = EXPERIMENTS_DIR / "revision_corpus" / "revision_corpus_v2.html"
INICIO = "/* === INICIO LOGICA PURA === */"
FIN = "/* === FIN LOGICA PURA === */"
NODE = shutil.which("node")


def html_generado() -> str:
    if not HTML.exists():
        raise unittest.SkipTest(f"no existe {HTML}")
    return HTML.read_text(encoding="utf-8")


def datos(html: str) -> dict:
    m = re.search(r'<script type="application/json" id="datos">(.*?)</script>', html, re.S)
    assert m
    return json.loads(m.group(1).replace("\\u003c", "<"))


def en_node(html: str, cuerpo: str) -> dict:
    if NODE is None:
        raise unittest.SkipTest("node no disponible")
    i, f = html.index(INICIO), html.index(FIN) + len(FIN)
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = Path(carpeta) / "p.mjs"
        ruta.write_text(html[i:f] + "\n" + cuerpo, encoding="utf-8")
        p = subprocess.run([NODE, str(ruta)], capture_output=True, text=True,
                           encoding="utf-8")
        if p.returncode != 0:
            raise AssertionError(f"node fallo:\n{p.stderr}")
        return json.loads(p.stdout)


class RevisionCiega(unittest.TestCase):
    """[ES] Lo que hace que la revision valga: la propuesta se oculta primero."""

    def setUp(self):
        self.html = html_generado()
        self.d = datos(self.html)

    def test_la_etapa_dos_arranca_oculta_en_el_marcado(self):
        # If the proposal were rendered and merely hidden by CSS, a reviewer
        # could read it. It is rendered only after the blind stage is recorded.
        # [ES] Si la propuesta se renderizara y solo se ocultara por CSS, un
        # revisor podría leerla. Se renderiza recién tras registrar la etapa
        # ciega.
        # Attribute order is not fixed, so both orders are accepted. The claim
        # under test is that the element starts hidden, not how it is written.
        # [ES] El orden de los atributos no es fijo, así que se aceptan los dos.
        # Lo que se prueba es que el elemento arranca oculto, no cómo se escribe.
        self.assertRegex(
            self.html,
            r'(id="etapa2"[^>]*class="etapa oculto"'
            r'|class="etapa oculto"[^>]*id="etapa2")',
        )
        self.assertIn('if(mostrar){', self.html)
        self.assertIn("pintarPropuesta(d);", self.html)

    def test_el_boton_de_revelar_exige_la_etapa_ciega_valida(self):
        self.assertIn("refrescarRevelar", self.html)
        self.assertIn("if(!validarEtapa(d,E(d).ciega,VT,VD).ok)return;", self.html)

    def test_se_registran_las_dos_etapas_y_si_hubo_cambio(self):
        # Without `cambio_tras_revelar`, a corpus that simply copied the
        # classifier is indistinguishable from one that agreed with it.
        # [ES] Sin `cambio_tras_revelar`, un corpus que copió al clasificador es
        # indistinguible de uno que coincidió con él.
        r = self._js(
            'const docs=[{id:"a",cohorte:"x",archivo:"a.pdf",ruta:"r",paginas:1,'
            'propuesta:{emisor:"E",tipo:"t",periodo:"2025",dominios:["legal"]}}];\n'
            'const est={a:{ciega:{decision:"confirmar"},'
            'adjudicada:{decision:"corregir",tipo:"memoria_anual"},observaciones:""}};\n'
            "console.log(JSON.stringify(armarJson({receta:'r',alcance:{},"
            "huella_fuentes:'h',fecha_exportacion:'x',salvedades:[]},"
            "docs,est,VT,VD)));"
        )
        d0 = r["decisiones"][0]
        self.assertEqual(d0["ciega"]["decision"], "confirmar")
        self.assertEqual(d0["adjudicada"]["decision"], "corregir")
        self.assertTrue(d0["cambio_tras_revelar"])
        self.assertEqual(r["conteos"]["cambio_tras_revelar"], 1)

    def test_una_decision_solo_ciega_no_cuenta_como_completa(self):
        # [ES] La adjudicación es obligatoria: sin ella el documento queda a
        # medias, no terminado.
        r = self._js(
            'const docs=[{id:"a",cohorte:"x",archivo:"a",ruta:"r",paginas:1,'
            'propuesta:{}}];\n'
            'const est={a:{ciega:{decision:"confirmar"},adjudicada:{}}};\n'
            "console.log(JSON.stringify(contar(docs,est,VT,VD)));"
        )
        self.assertEqual(r["ciega"], 1)
        self.assertEqual(r["adjudicada"], 0)

    def _js(self, cuerpo):
        return en_node(self.html, (
            f"const VT={json.dumps(self.d['vocabulario_tipo'])};\n"
            f"const VD={json.dumps(self.d['dominios'])};\n" + cuerpo
        ))


class VocabularioYValidacion(unittest.TestCase):
    """[ES] El formulario no acepta cualquier cosa."""

    def setUp(self):
        self.html = html_generado()
        self.d = datos(self.html)

    def _periodos(self, valores):
        return en_node(self.html, (
            f"const V={json.dumps(valores)};\n"
            "console.log(JSON.stringify(V.map(periodoValido)));"
        ))

    def test_el_periodo_acepta_solo_las_tres_formas(self):
        # Free text produced `31 DE MARZO DE 2026` and `2T2026` for the same kind
        # of thing. A catalogue where one period is written three ways cannot be
        # deduplicated or grouped.
        # [ES] El texto libre producía `31 DE MARZO DE 2026` y `2T2026` para la
        # misma clase de cosa. Un catálogo donde un período se escribe de tres
        # formas no se puede deduplicar ni agrupar.
        buenos = ["2025", "1T2026", "2026-03-31", ""]
        malos = ["31 DE MARZO DE 2026", "marzo 2026", "2026-13-01", "2026-03-32",
                 "5T2026", "25", "2026/03/31"]
        self.assertEqual(self._periodos(buenos), [True] * len(buenos))
        self.assertEqual(self._periodos(malos), [False] * len(malos))

    def test_el_tipo_sale_del_vocabulario_controlado(self):
        r = en_node(self.html, (
            f"const VT={json.dumps(self.d['vocabulario_tipo'])};\n"
            'console.log(JSON.stringify(["estado_financiero","EEFF","",'
            '"estdo_financiero"].map(function(t){return tipoValido(t,VT);})));'
        ))
        self.assertEqual(r, [True, False, True, False])

    def test_ninguno_es_una_respuesta_valida_y_excluyente(self):
        # `ninguno` must be expressible: a document that contributes to no domain
        # is a real answer, and leaving every box unticked is indistinguishable
        # from not having answered.
        # [ES] `ninguno` tiene que poder expresarse: un documento que no aporta a
        # ningún dominio es una respuesta real, y dejar todas las casillas sin
        # marcar es indistinguible de no haber contestado.
        r = en_node(self.html, (
            f"const VD={json.dumps(self.d['dominios'])};\n"
            'console.log(JSON.stringify([["ninguno"],["ninguno","legal"],'
            '["legal","contable"],["inventado"]].map(function(s){'
            'return dominiosValidos(s,VD);})));'
        ))
        self.assertEqual(r, [True, False, True, False])

    def test_corregir_exige_completar_algo(self):
        r = en_node(self.html, (
            f"const VT={json.dumps(self.d['vocabulario_tipo'])};\n"
            f"const VD={json.dumps(self.d['dominios'])};\n"
            'const doc={id:"a"};\n'
            'console.log(JSON.stringify([{decision:"corregir"},'
            '{decision:"corregir",periodo:"2025"},'
            '{decision:"corregir",periodo:"marzo"},'
            '{decision:"dudoso"},{decision:"dudoso",observaciones:"x"}]'
            '.map(function(e){return validarEtapa(doc,e,VT,VD);})));'
        ))
        self.assertEqual([x["ok"] for x in r], [False, True, False, False, True])
        self.assertIn("período debe ser", r[2]["motivo"])


class AlcanceDeclarado(unittest.TestCase):
    """[ES] Los 59 no incluyen las 150 de InfoLEG, y hay que decirlo."""

    def setUp(self):
        self.html = html_generado()
        self.d = datos(self.html)

    def test_cubre_59_y_declara_que_faltan_las_150(self):
        self.assertEqual(len(self.d["documentos"]), 59)
        self.assertEqual(self.d["alcance"]["infoleg_no_incluidos"], 150)
        self.assertIn("NO incluyen las 150", self.d["alcance"]["texto"])

    def test_dice_que_terminar_los_59_no_cierra_las_brechas(self):
        # The claim v2 made implicitly and should not have.
        # [ES] La afirmación que la v2 hacía implícitamente y no debía.
        self.assertIn("NO vuelve conocidas las brechas", self.d["alcance"]["texto"])

    def test_hay_un_boton_para_abrir_el_documento_con_ruta_local(self):
        self.assertIn('id="abrir"', self.html)
        self.assertIn('window.open("file:///"+D.raiz+"/"+d.ruta', self.html)
        self.assertTrue(self.d["raiz"].endswith("multi-rag-energy-ar"))

    def test_no_usa_innerhtml_ni_sale_a_internet(self):
        for prohibido in ("innerHTML", "document.write", "eval(", "fetch(",
                          "XMLHttpRequest"):
            self.assertNotIn(prohibido, self.html, prohibido)
        self.assertNotRegex(self.html, r"<script[^>]+\bsrc\s*=")


class ExportacionDeDosEtapas(unittest.TestCase):
    """[ES] El CSV lleva las dos decisiones y la propuesta, para poder auditar."""

    def setUp(self):
        self.html = html_generado()
        self.d = datos(self.html)

    def test_el_csv_lleva_ciega_final_propuesta_y_el_cambio(self):
        import csv as _csv
        import io

        estados = {
            x["id"]: {
                "ciega": {"decision": "confirmar"},
                "adjudicada": {"decision": "confirmar"},
                "observaciones": "",
            }
            for x in self.d["documentos"]
        }
        primero = self.d["documentos"][0]["id"]
        estados[primero]["adjudicada"] = {"decision": "corregir", "periodo": "2020"}

        r = en_node(self.html, (
            f"const D={json.dumps(self.d)};\n"
            f"const est={json.dumps(estados)};\n"
            "console.log(JSON.stringify({csv:armarCsv(D.documentos,est,"
            "D.vocabulario_tipo,D.dominios)}));"
        ))
        filas = list(_csv.DictReader(io.StringIO(r["csv"])))
        self.assertEqual(len(filas), 59)
        for columna in ("decision_ciega", "decision_final", "cambio_tras_revelar",
                        "propuesta_emisor", "propuesta_dominios"):
            self.assertIn(columna, filas[0])
        cambiados = [f for f in filas if f["cambio_tras_revelar"] == "si"]
        self.assertEqual(len(cambiados), 1)
        self.assertEqual(cambiados[0]["id"], primero)


if __name__ == "__main__":
    unittest.main()
