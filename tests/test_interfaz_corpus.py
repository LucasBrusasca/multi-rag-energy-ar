"""Tests for the corpus review interface (59 documents, three cohorts).

Same two kinds of check as the catalogue interface: structure read off the file,
and behaviour actually executed under node. The behavioural half is the one that
matters - asserting that a file "contains a validation function" says nothing
about what it does.

[ES] Pruebas de la interfaz de revision del corpus (59 documentos, tres
cohortes).

Los mismos dos tipos de comprobacion que la interfaz del catalogo: estructura
leida del archivo, y comportamiento efectivamente ejecutado con node. La mitad de
comportamiento es la que importa: afirmar que un archivo "contiene una funcion de
validacion" no dice nada sobre lo que hace.
"""

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from multirag.paths import EXPERIMENTS_DIR

HTML = EXPERIMENTS_DIR / "revision_corpus" / "revision_corpus.html"
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


class Estructura(unittest.TestCase):
    def setUp(self):
        self.html = html_generado()
        self.d = datos(self.html)

    def test_cubre_las_tres_cohortes_completas(self):
        # 24 + 24 + 11 = 59. Reviewing them in three instruments would make the
        # one comparison that matters - is this new document the active one? -
        # the hardest to make.
        # [ES] 24 + 24 + 11 = 59. Revisarlos en tres instrumentos volvería la
        # única comparación que importa la más difícil de hacer.
        import collections

        c = collections.Counter(x["cohorte"] for x in self.d["documentos"])
        self.assertEqual(c["activo"], 24)
        self.assertEqual(c["empresarial_nuevo"], 24)
        self.assertEqual(c["cuarentena"], 11)
        self.assertEqual(len(self.d["documentos"]), 59)

    def test_los_cuatro_dominios_son_independientes(self):
        # [ES] Cuatro campos separados, no una caja de texto para los cuatro.
        self.assertEqual(list(self.d["dominios"]),
                         ["legal", "impositivo", "contable", "financiero"])
        self.assertEqual(len(self.d["campos"]), 4)
        for campo in ("emisor_corregido", "tipo_corregido", "periodo_corregido",
                      "dominios_corregidos"):
            self.assertIn(campo, self.d["campos"])

    def test_no_todo_empresarial_es_contable_y_financiero(self):
        # THE correction of v1. If every corporate document were assigned both
        # domains, there would be exactly one combination.
        # [ES] LA corrección de la v1. Si a todo documento empresarial se le
        # asignaran los dos dominios, habría una sola combinación.
        nuevos = [x for x in self.d["documentos"] if x["cohorte"] == "empresarial_nuevo"]
        combos = {tuple(sorted(x["dominios_propuestos"])) for x in nuevos}
        self.assertGreater(len(combos), 1, "la v1 producía una sola combinación")
        con_ambos = [x for x in nuevos
                     if set(x["dominios_propuestos"]) >= {"contable", "financiero"}]
        self.assertLess(len(con_ambos), len(nuevos),
                        "no todos pueden tener contable Y financiero")

    def test_cada_propuesta_lleva_confianza(self):
        # [ES] Una propuesta sin confianza se lee como un dato.
        for x in self.d["documentos"]:
            self.assertIn("confianza_entidad", x)
            self.assertIn("confianza_periodo", x)

    def test_los_empresariales_llevan_evidencia_citada(self):
        # [ES] La propuesta de dominio tiene que poder reabrirse.
        nuevos = [x for x in self.d["documentos"] if x["cohorte"] == "empresarial_nuevo"]
        con_evidencia = [x for x in nuevos if x["evidencia_dominios"]]
        self.assertGreater(len(con_evidencia), len(nuevos) // 2)
        muestra = con_evidencia[0]["evidencia_dominios"][0]
        for clave in ("dominio", "termino", "pagina", "cita"):
            self.assertIn(clave, muestra)

    def test_las_columnas_humanas_no_vienen_precargadas(self):
        for x in self.d["documentos"]:
            for columna in self.d["columnas_humanas"]:
                self.assertNotIn(columna, x, f"{x['id']}/{columna}")

    def test_es_autocontenido_y_no_usa_innerhtml(self):
        for prohibido in ("innerHTML", "document.write", "eval(", "fetch(",
                          "XMLHttpRequest"):
            self.assertNotIn(prohibido, self.html, prohibido)
        self.assertNotRegex(self.html, r"<script[^>]+\bsrc\s*=")

    def test_avisa_cuando_el_periodo_discrepa_con_la_url(self):
        # The URL directory is the PUBLICATION date, not the period. The
        # interface must say so where they diverge instead of silently picking.
        # [ES] El directorio de la URL es la fecha de PUBLICACIÓN, no el período.
        # La interfaz tiene que decirlo donde divergen, en vez de elegir en
        # silencio.
        avisos = " ".join(
            a for x in self.d["documentos"] for a in x.get("avisos", [])
        )
        self.assertIn("directorio de la URL", avisos)

    def test_declara_los_archivos_de_cuarentena_no_leidos(self):
        # [ES] No se inventa una caracterización a partir de un nombre.
        sin_leer = [
            x for x in self.d["documentos"]
            if any("no se leyó su contenido" in a for a in x.get("avisos", []))
        ]
        self.assertEqual(len(sin_leer), 2, "las dos planillas de cuarentena")


class Comportamiento(unittest.TestCase):
    def setUp(self):
        self.html = html_generado()
        self.d = datos(self.html)

    def _js(self, cuerpo):
        return en_node(self.html, (
            f"const D={json.dumps(self.d)};\n"
            "const CAMPOS=D.campos, ORIGEN=D.origen_de_correccion;\n"
            "const HUMANAS=D.columnas_humanas;\n" + cuerpo
        ))

    def test_las_reglas_de_decision_se_cumplen(self):
        r = self._js(
            'const doc={id:"x",emisor_propuesto:"Ente S.A.",tipo_propuesto:"eeff",'
            'periodo_propuesto:"2025",dominios_propuestos:["contable"]};\n'
            "const casos=[{decision:'confirmar'},"
            "{decision:'confirmar',tipo_corregido:'x'},"
            "{decision:'corregir'},"
            "{decision:'corregir',tipo_corregido:'eeff'},"
            "{decision:'corregir',tipo_corregido:'memoria'},"
            "{decision:'dudoso'},{decision:'dudoso',observaciones:'no sé'},"
            "{decision:'excluir'},{decision:'excluir',observaciones:'motivo'}];\n"
            "console.log(JSON.stringify(casos.map(c=>validar(doc,c,CAMPOS,ORIGEN))));"
        )
        self.assertEqual([x["ok"] for x in r],
                         [True, False, False, False, True, False, True, False, True])
        self.assertIn("no admite correcciones", r[1]["motivo"])
        self.assertIn("distinto del actual", r[3]["motivo"])

    def test_el_csv_conserva_las_59_filas_y_las_columnas(self):
        import csv as _csv
        import io

        estados = {
            x["id"]: {"decision": "confirmar"} for x in self.d["documentos"]
        }
        r = self._js(
            f"const E={json.dumps(estados)};\n"
            "console.log(JSON.stringify({csv:armarCsv(D.documentos,E,D.columnas,HUMANAS)}));"
        )
        filas = list(_csv.reader(io.StringIO(r["csv"])))
        self.assertEqual(filas[0], list(self.d["columnas"]))
        self.assertEqual(len(filas), 60, "encabezado + 59")
        for f in filas:
            self.assertEqual(len(f), len(self.d["columnas"]))

    def test_los_dominios_se_exportan_con_barra_vertical(self):
        # [ES] Mismo formato que el catálogo, para que la corrección se pueda
        # aplicar después sin traducir.
        import csv as _csv
        import io

        estados = {x["id"]: {"decision": "confirmar"} for x in self.d["documentos"]}
        r = self._js(
            f"const E={json.dumps(estados)};\n"
            "console.log(JSON.stringify({csv:armarCsv(D.documentos,E,D.columnas,HUMANAS)}));"
        )
        filas = list(_csv.DictReader(io.StringIO(r["csv"])))
        con_varios = [f for f in filas if "|" in f["dominios_propuestos"]]
        self.assertTrue(con_varios, "algún documento tiene más de un dominio")

    def test_una_decision_invalida_cuenta_como_pendiente(self):
        # [ES] Si no, exportar se habilitaría con reglas incumplidas.
        estados = {x["id"]: {"decision": "confirmar"} for x in self.d["documentos"]}
        primero = self.d["documentos"][0]["id"]
        estados[primero] = {"decision": "dudoso"}
        r = self._js(
            f"const E={json.dumps(estados)};\n"
            "console.log(JSON.stringify(contar(D.documentos,E,D.opciones,CAMPOS,ORIGEN)));"
        )
        self.assertEqual(r["pendientes"], 1)
        self.assertEqual(r["confirmar"], 58)

    def test_el_json_marca_las_decisiones_invalidas(self):
        estados = {x["id"]: {"decision": "confirmar"} for x in self.d["documentos"]}
        estados[self.d["documentos"][0]["id"]] = {"decision": "excluir"}
        r = self._js(
            f"const E={json.dumps(estados)};\n"
            "console.log(JSON.stringify(armarJson({receta:'r',huella_fuentes:'h',"
            "fecha_exportacion:'2026-08-29',salvedades:[]},D.documentos,E,"
            "D.opciones,CAMPOS,ORIGEN,HUMANAS)));"
        )
        self.assertEqual(len(r["decisiones"]), 59)
        self.assertEqual(r["conteos"]["pendientes"], 1)
        invalidas = [d for d in r["decisiones"] if not d["valida"]]
        self.assertEqual(len(invalidas), 1)


if __name__ == "__main__":
    unittest.main()
