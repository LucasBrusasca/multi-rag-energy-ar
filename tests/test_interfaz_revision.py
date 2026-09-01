"""Tests for the offline HTML review interface.

Two kinds of check, and the second is the one that matters:

1. STRUCTURE, read off the generated file: it is self-contained, it never uses
   `innerHTML`, it embeds the 24 documents and the 22 columns, it flags the
   ingestion defect, and it does not show the automatic classification up front.

2. BEHAVIOUR, actually executed. The validation and export functions are
   extracted VERBATIM from the generated HTML and run under node. Asserting that
   a file "contains a validation function" proves nothing about what it does;
   these tests run it and check the answers. If node is unavailable the
   behavioural tests are skipped and say so, rather than passing quietly.

[ES] Pruebas de la interfaz HTML de revision, offline.

Dos tipos de comprobacion, y la segunda es la que importa:

1. ESTRUCTURA, leida del archivo generado: es autocontenido, nunca usa
   `innerHTML`, embebe los 24 documentos y las 22 columnas, marca el defecto de
   ingesta, y no muestra la clasificacion automatica de entrada.

2. COMPORTAMIENTO, efectivamente ejecutado. Las funciones de validacion y
   exportacion se extraen TAL CUAL del HTML generado y se corren con node.
   Afirmar que un archivo "contiene una funcion de validacion" no prueba nada
   sobre lo que hace; estas pruebas la corren y comprueban las respuestas. Si
   node no esta disponible, las pruebas de comportamiento se saltean y lo dicen,
   en lugar de pasar en silencio.
"""

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from multirag.paths import EXPERIMENTS_DIR
from scripts.diagnostics.generar_interfaz_revision import (
    CAMPOS_CORREGIBLES,
    ORIGEN_DE_CORRECCION,
    OPCIONES_DECISION,
    incrustar_json,
)


HTML = EXPERIMENTS_DIR / "revision_catalogo_24" / "revision_catalogo_24.html"

INICIO = "/* === INICIO LOGICA PURA === */"
FIN = "/* === FIN LOGICA PURA === */"

NODE = shutil.which("node")


def html_generado() -> str:
    if not HTML.exists():
        raise unittest.SkipTest(
            f"no existe {HTML}; generar con "
            f"python -m scripts.diagnostics.generar_interfaz_revision"
        )
    return HTML.read_text(encoding="utf-8")


def datos_embebidos(html: str) -> dict:
    bloque = re.search(
        r'<script type="application/json" id="datos">(.*?)</script>', html, re.S
    )
    assert bloque, "no se encontró el bloque de datos embebidos"
    return json.loads(bloque.group(1).replace("\\u003c", "<"))


def logica_pura(html: str) -> str:
    inicio = html.index(INICIO)
    fin = html.index(FIN) + len(FIN)
    return html[inicio:fin]


def correr_en_node(html: str, cuerpo: str) -> dict:
    """Run the interface's OWN functions under node and return what they said.

    [ES] Corre las PROPIAS funciones de la interfaz con node y devuelve lo que
    dijeron.
    """
    if NODE is None:
        raise unittest.SkipTest("node no está disponible; se saltean las pruebas de comportamiento")
    guion = logica_pura(html) + "\n" + cuerpo
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = Path(carpeta) / "prueba.mjs"
        ruta.write_text(guion, encoding="utf-8")
        proceso = subprocess.run(
            [NODE, str(ruta)], capture_output=True, text=True, encoding="utf-8"
        )
        if proceso.returncode != 0:
            raise AssertionError(f"node falló:\n{proceso.stderr}")
        return json.loads(proceso.stdout)


CONSTANTES_JS = (
    f"const CAMPOS = {json.dumps(list(CAMPOS_CORREGIBLES))};\n"
    f"const ORIGEN = {json.dumps(dict(ORIGEN_DE_CORRECCION))};\n"
    f"const OPCIONES = {json.dumps(list(OPCIONES_DECISION))};\n"
    'const HUMANAS = ["decision_humana"].concat(CAMPOS).concat(["observaciones"]);\n'
    'const DOC = {document_id:"DOC-0001", fuente:"f", emisor_id:"EMI-0001",\n'
    '  emisor_nombre:"Ente X", tipo_documento:"resolucion",\n'
    '  dominios_documentales:"legal|regulatorio"};\n'
)


class EstructuraDelArchivo(unittest.TestCase):
    """[ES] Lo que se puede leer del archivo generado."""

    def setUp(self):
        self.html = html_generado()

    def test_es_autocontenido_y_no_sale_a_internet(self):
        # No external script, stylesheet or font, and no network call. The file
        # has to work by double-clicking it with the wifi off.
        # [ES] Ningún script, hoja de estilo ni fuente externa, y ninguna llamada
        # de red. El archivo tiene que funcionar con doble clic y el wifi
        # apagado.
        self.assertNotRegex(self.html, r"<script[^>]+\bsrc\s*=")
        self.assertNotRegex(self.html, r"<link[^>]+stylesheet")
        for prohibido in ("fetch(", "XMLHttpRequest", "navigator.sendBeacon",
                          "WebSocket", "import(", "@import"):
            self.assertNotIn(prohibido, self.html, prohibido)

    def test_nunca_usa_innerhtml(self):
        # Titles and excerpts come from real documents, and a document is
        # untrusted input. One innerHTML is all it takes.
        # [ES] Los títulos y extractos vienen de documentos reales, y un
        # documento es entrada no confiable. Con un solo innerHTML alcanza.
        for prohibido in ("innerHTML", "outerHTML", "insertAdjacentHTML",
                          "document.write", "eval("):
            self.assertNotIn(prohibido, self.html, prohibido)

    def test_los_enlaces_solo_se_crean_para_http_y_https(self):
        # A `javascript:` value in a catalogue field must not become clickable.
        # [ES] Un valor `javascript:` en un campo del catálogo no puede volverse
        # clickeable.
        self.assertIn(r"/^https?:\/\//i.test(url)", self.html)

    def test_embebe_los_24_documentos_con_las_22_columnas(self):
        datos = datos_embebidos(self.html)
        self.assertEqual(len(datos["documentos"]), 24)
        self.assertEqual(len(datos["columnas"]), 22)
        for doc in datos["documentos"]:
            self.assertEqual(set(doc), set(datos["columnas"]))

    def test_las_seis_columnas_humanas_vienen_vacias(self):
        # [ES] La interfaz no precarga ninguna decisión.
        datos = datos_embebidos(self.html)
        for doc in datos["documentos"]:
            for columna in datos["columnas_humanas"]:
                self.assertEqual(doc[columna], "", f"{doc['document_id']}/{columna}")

    def test_marca_el_defecto_de_ingesta_de_doc_0017(self):
        # [ES] Advertencia no bloqueante, y el texto dice que no se corrige acá.
        datos = datos_embebidos(self.html)
        self.assertIn("DOC-0017", datos["defectos"])
        self.assertGreater(datos["defectos"]["DOC-0017"]["ocurrencias"], 0)
        self.assertIn("no debe corregirse desde", self.html)

    def test_la_clasificacion_automatica_no_se_muestra_de_entrada(self):
        # It is embedded, because the reviewer may want it afterwards - but the
        # container starts hidden and the button carries the anchoring warning.
        # [ES] Está embebida, porque el revisor puede quererla después, pero el
        # contenedor arranca oculto y el botón lleva la advertencia de anclaje.
        datos = datos_embebidos(self.html)
        self.assertTrue(datos["contexto_automatico"])
        self.assertIn('id="auto-contenido"', self.html)
        self.assertRegex(
            self.html, r'class="contenido oculto"\s+id="auto-contenido"'
        )
        self.assertIn("Mostrar clasificación automática", self.html)
        self.assertIn("puede anclar tu juicio", self.html)

    def test_declara_que_nada_se_aplica_al_catalogo(self):
        # The two statements the reviewer has to be able to read on screen:
        # nothing leaves the machine, and nothing is applied to the catalogue.
        # [ES] Las dos afirmaciones que el revisor tiene que poder leer en
        # pantalla: nada sale de la máquina, y nada se aplica al catálogo.
        texto = self.html.lower()
        self.assertIn("nada se envía a internet", texto)
        self.assertIn("nada se aplica\n    al catálogo", texto)
        self.assertIn("nada se aplicó al catálogo", texto)

    def test_el_json_embebido_no_puede_cerrar_la_etiqueta_script(self):
        # [ES] Un `</script>` dentro de un extracto rompería la página entera.
        peligroso = incrustar_json({"x": "</script><script>alert(1)</script>"})
        self.assertNotIn("</script>", peligroso)
        self.assertIn("\\u003c", peligroso)


class ValidacionEjecutada(unittest.TestCase):
    """[ES] Las reglas de llenado, corridas de verdad con node."""

    def setUp(self):
        self.html = html_generado()

    def _validar(self, casos):
        cuerpo = CONSTANTES_JS + (
            f"const CASOS = {json.dumps(casos)};\n"
            "const salida = CASOS.map(function(c){\n"
            "  const doc = Object.assign({}, DOC, c.doc || {});\n"
            "  return validarDecision(doc, c.estado, CAMPOS, ORIGEN);\n"
            "});\n"
            "console.log(JSON.stringify(salida));\n"
        )
        return correr_en_node(self.html, cuerpo)

    def test_confirmar_sin_correcciones_es_valido(self):
        r = self._validar([{"estado": {"decision_humana": "confirmar"}}])
        self.assertTrue(r[0]["ok"])

    def test_confirmar_con_una_correccion_cargada_es_invalido(self):
        # [ES] «Confirmar» no admite correcciones cargadas.
        r = self._validar([
            {"estado": {"decision_humana": "confirmar",
                        "tipo_documento_corregido": "ley"}}
        ])
        self.assertFalse(r[0]["ok"])
        self.assertIn("no admite correcciones", r[0]["motivo"])

    def test_corregir_sin_ningun_campo_es_invalido(self):
        r = self._validar([{"estado": {"decision_humana": "corregir"}}])
        self.assertFalse(r[0]["ok"])

    def test_corregir_repitiendo_el_valor_actual_es_invalido(self):
        # THE case worth testing. Retyping what is already on file is not a
        # correction, and accepting it would record a change that changes
        # nothing.
        # [ES] EL caso que vale la pena probar. Reescribir lo que ya está no es
        # una corrección, y aceptarlo registraría un cambio que no cambia nada.
        r = self._validar([
            {"estado": {"decision_humana": "corregir",
                        "tipo_documento_corregido": "resolucion"}}
        ])
        self.assertFalse(r[0]["ok"])
        self.assertIn("distinto del actual", r[0]["motivo"])

    def test_corregir_con_un_valor_distinto_es_valido(self):
        r = self._validar([
            {"estado": {"decision_humana": "corregir",
                        "tipo_documento_corregido": "resolucion_general"}}
        ])
        self.assertTrue(r[0]["ok"])

    def test_corregir_ignora_diferencias_de_espacios(self):
        # [ES] " resolucion " no es una corrección; es el mismo valor.
        r = self._validar([
            {"estado": {"decision_humana": "corregir",
                        "tipo_documento_corregido": "  resolucion  "}}
        ])
        self.assertFalse(r[0]["ok"])

    def test_dudoso_exige_observacion(self):
        r = self._validar([
            {"estado": {"decision_humana": "dudoso"}},
            {"estado": {"decision_humana": "dudoso", "observaciones": "   "}},
            {"estado": {"decision_humana": "dudoso", "observaciones": "no sé si es legal"}},
        ])
        self.assertFalse(r[0]["ok"])
        self.assertFalse(r[1]["ok"], "espacios en blanco no son una observación")
        self.assertTrue(r[2]["ok"])

    def test_excluir_exige_justificacion(self):
        r = self._validar([
            {"estado": {"decision_humana": "excluir_del_corpus"}},
            {"estado": {"decision_humana": "excluir_del_corpus",
                        "observaciones": "duplicado binario de DOC-0004"}},
        ])
        self.assertFalse(r[0]["ok"])
        self.assertTrue(r[1]["ok"])

    def test_sin_decision_es_invalido(self):
        r = self._validar([{"estado": {}}])
        self.assertFalse(r[0]["ok"])

    def test_los_conteos_separan_validos_de_pendientes(self):
        # [ES] Una decisión inválida cuenta como PENDIENTE, no como decidida: si
        # no, «Finalizar» se habilitaría con reglas incumplidas.
        cuerpo = CONSTANTES_JS + (
            'const DOCS = [{document_id:"A",tipo_documento:"t"},'
            '{document_id:"B",tipo_documento:"t"},{document_id:"C",tipo_documento:"t"}];\n'
            # B queda sin observación a propósito: es la decisión inválida.
            'const E = {A:{decision_humana:"confirmar"},'
            'B:{decision_humana:"dudoso"},'
            'C:{decision_humana:"excluir_del_corpus",observaciones:"motivo"}};\n'
            "console.log(JSON.stringify("
            "contarDecisiones(DOCS, E, OPCIONES, CAMPOS, ORIGEN)));\n"
        )
        c = correr_en_node(self.html, cuerpo)
        self.assertEqual(c["confirmar"], 1)
        self.assertEqual(c["excluir_del_corpus"], 1)
        self.assertEqual(c["dudoso"], 0)
        self.assertEqual(c["pendientes"], 1)


class ExportacionEjecutada(unittest.TestCase):
    """[ES] El CSV y el JSON que salen, generados por el propio archivo."""

    def setUp(self):
        self.html = html_generado()
        self.datos = datos_embebidos(self.html)

    def _estados_completos(self):
        """[ES] Una decisión válida para los 24, con variedad de tipos."""
        estados = {}
        for i, doc in enumerate(self.datos["documentos"]):
            uid = doc["document_id"]
            if i % 4 == 0:
                estados[uid] = {"decision_humana": "confirmar"}
            elif i % 4 == 1:
                estados[uid] = {"decision_humana": "corregir",
                                "tipo_documento_corregido": "TIPO_NUEVO"}
            elif i % 4 == 2:
                estados[uid] = {"decision_humana": "dudoso",
                                "observaciones": "duda " + uid}
            else:
                estados[uid] = {"decision_humana": "excluir_del_corpus",
                                "observaciones": "motivo " + uid}
        return estados

    def _exportar(self, estados):
        cuerpo = (
            f"const D = {json.dumps(self.datos)};\n"
            f"const E = {json.dumps(estados)};\n"
            "const CAMPOS = D.campos_corregibles, ORIGEN = D.origen_de_correccion;\n"
            "const HUMANAS = D.columnas_humanas;\n"
            "const csv = armarCsv(D.documentos, E, D.columnas, HUMANAS);\n"
            "const js = armarJson({receta:'r', huella_catalogo:'h', huella_csv_v2:'c',"
            " fecha_exportacion:'2026-08-29T00:00:00Z', salvedades:['s']},"
            " D.documentos, E, D.opciones_decision, CAMPOS, ORIGEN, HUMANAS);\n"
            "console.log(JSON.stringify({csv: csv, json: js}));\n"
        )
        return correr_en_node(self.html, cuerpo)

    def test_el_csv_conserva_las_22_columnas_y_las_24_filas(self):
        # Parsed, not split on newlines. The evidence columns legitimately
        # contain newlines, so counting raw lines counts wrong - and a CSV that
        # only parses correctly when read as CSV is exactly what is wanted.
        # [ES] Parseado, no partido por saltos de línea. Las columnas de
        # evidencia contienen saltos legítimamente, así que contar líneas crudas
        # cuenta mal - y un CSV que solo parsea bien leído como CSV es
        # exactamente lo que se busca.
        import csv as _csv
        import io

        salida = self._exportar(self._estados_completos())
        filas = list(_csv.reader(io.StringIO(salida["csv"])))
        self.assertEqual(filas[0], list(self.datos["columnas"]))
        self.assertEqual(len(filas), 25, "encabezado + 24 filas")
        for fila in filas:
            self.assertEqual(len(fila), 22)

    def test_el_csv_completa_las_seis_columnas_humanas(self):
        estados = self._estados_completos()
        salida = self._exportar(estados)
        import csv as _csv
        import io

        filas = list(_csv.DictReader(io.StringIO(salida["csv"])))
        self.assertEqual(len(filas), 24)
        for fila in filas:
            uid = fila["document_id"]
            self.assertEqual(fila["decision_humana"], estados[uid]["decision_humana"])
            self.assertEqual(
                fila["observaciones"], estados[uid].get("observaciones", "")
            )
            self.assertEqual(
                fila["tipo_documento_corregido"],
                estados[uid].get("tipo_documento_corregido", ""),
            )

    def test_el_csv_conserva_los_valores_originales_de_las_16_columnas(self):
        # [ES] La exportación no debe alterar ningún dato del catálogo.
        salida = self._exportar(self._estados_completos())
        import csv as _csv
        import io

        filas = {f["document_id"]: f for f in _csv.DictReader(io.StringIO(salida["csv"]))}
        originales = {d["document_id"]: d for d in self.datos["documentos"]}
        no_humanas = [c for c in self.datos["columnas"]
                      if c not in self.datos["columnas_humanas"]]
        for uid, fila in filas.items():
            for columna in no_humanas:
                self.assertEqual(fila[columna], originales[uid][columna],
                                 f"{uid}/{columna}")

    def test_el_csv_escapa_comillas_y_saltos_de_linea(self):
        # The evidence columns contain newlines and quotation marks by
        # construction. An unescaped one silently shifts every later column.
        # [ES] Las columnas de evidencia contienen saltos de línea y comillas por
        # construcción. Uno sin escapar corre en silencio todas las columnas
        # siguientes.
        estados = self._estados_completos()
        primero = self.datos["documentos"][0]["document_id"]
        estados[primero] = {"decision_humana": "dudoso",
                            "observaciones": 'tiene "comillas", coma y\nsalto'}
        salida = self._exportar(estados)
        import csv as _csv
        import io

        filas = {f["document_id"]: f for f in _csv.DictReader(io.StringIO(salida["csv"]))}
        self.assertEqual(len(filas), 24)
        self.assertEqual(filas[primero]["observaciones"],
                         'tiene "comillas", coma y\nsalto')

    def test_el_json_lleva_receta_huella_fecha_decisiones_y_conteos(self):
        salida = self._exportar(self._estados_completos())
        js = salida["json"]
        for clave in ("receta", "huella_catalogo", "fecha_exportacion",
                      "decisiones", "conteos"):
            self.assertIn(clave, js)
        self.assertEqual(len(js["decisiones"]), 24)
        self.assertEqual(js["conteos"]["pendientes"], 0)
        self.assertEqual(
            sum(js["conteos"][o] for o in self.datos["opciones_decision"]), 24
        )
        self.assertTrue(all(d["valida"] for d in js["decisiones"]))

    def test_el_json_marca_como_invalida_una_decision_incompleta(self):
        # [ES] Exportar no blanquea una regla incumplida: la marca.
        estados = self._estados_completos()
        primero = self.datos["documentos"][0]["document_id"]
        estados[primero] = {"decision_humana": "dudoso"}  # sin observación
        salida = self._exportar(estados)
        js = salida["json"]
        self.assertEqual(js["conteos"]["pendientes"], 1)
        invalidas = [d for d in js["decisiones"] if not d["valida"]]
        self.assertEqual([d["document_id"] for d in invalidas], [primero])

    def test_sin_decisiones_el_csv_sigue_teniendo_las_24_filas_vacias(self):
        # [ES] Exportar sin cargar nada no pierde documentos; los deja vacíos.
        salida = self._exportar({})
        import csv as _csv
        import io

        filas = list(_csv.DictReader(io.StringIO(salida["csv"])))
        self.assertEqual(len(filas), 24)
        self.assertTrue(all(f["decision_humana"] == "" for f in filas))


if __name__ == "__main__":
    unittest.main()
