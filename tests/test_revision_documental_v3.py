"""Validación y conservación del avance en la interfaz por documento."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "scripts/diagnostics/revision_documental"


class RevisionDocumentalV3(unittest.TestCase):
    def js(self, code):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node no disponible")
        fuente = (ASSETS / "interfaz.js").read_text(encoding="utf-8").split("/* === FIN LOGICA PURA === */")[0]
        pre = '''
const D={receta:'revision-documental-v3-por-documento',huella_fuentes:'h',
  vocabulario_tipo:['estado_financiero','no_determinado'],dominios:['legal','contable','impositivo','financiero'],
  documentos:[{id:'a',archivo:'a.pdf'},{id:'b',archivo:'b.xlsx'}],alcance:{}};
const tipos=D.vocabulario_tipo, dominios=D.dominios;
function ficha(){return {...nuevaFicha(),decision:'incluir',emisor:'Ejemplo',tipo:'estado_financiero',periodo:'2025',dominios:['contable'],consultado:true};}
function registro(){return {borrador:ficha(),historial:[]};}
function errorDe(fn){try{fn();return false;}catch(e){return e.message;}}
'''
        proceso = subprocess.run([node, "-e", fuente + pre + code], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        return json.loads(proceso.stdout)

    def test_incluir_exige_datos_y_original(self):
        r = self.js("console.log(JSON.stringify([{}, {emisor:''},{tipo:''},{periodo:''},{dominios:[]},{consultado:false}].map(x=>validarFicha({...ficha(),...x},tipos,dominios))));")
        self.assertEqual(r[0], "")
        self.assertTrue(all(r[1:]))

    def test_duda_y_exclusion_usan_el_comentario_visible(self):
        r = self.js("console.log(JSON.stringify(['dudoso','excluir'].map(decision=>[validarFicha({...nuevaFicha(),decision,consultado:true},tipos,dominios),validarFicha({...nuevaFicha(),decision,consultado:true,comentarios:'No identifico al emisor'},tipos,dominios)]))); ")
        for vacio, comentado in r:
            self.assertTrue(vacio)
            self.assertEqual(comentado, "")

    def test_fechas_reales_y_trimestres(self):
        r = self.js("console.log(JSON.stringify(['2025','1T2026','2024-02-29','2025-02-29','2026-04-31','5T2026',''].map(periodoValido))); ")
        self.assertEqual(r, [True, True, True, False, False, False, False])

    def test_periodo_desconocido_es_explicito(self):
        r = self.js("console.log(JSON.stringify([validarFicha({...ficha(),periodo:'',periodo_desconocido:true},tipos,dominios),validarFicha({...ficha(),periodo_desconocido:true},tipos,dominios)]));")
        self.assertEqual(r[0], "")
        self.assertTrue(r[1])

    def test_ninguno_es_excluyente(self):
        r = self.js("console.log(JSON.stringify([cambiarDominio(['legal'],'ninguno',true),cambiarDominio(['ninguno'],'contable',true),validarFicha({...ficha(),dominios:['ninguno','legal']},tipos,dominios)]));")
        self.assertEqual(r[:2], [["ninguno"], ["contable"]])
        self.assertTrue(r[2])

    def test_primera_opinion_se_conserva_y_no_se_sobrescribe(self):
        r = self.js("const e=registro();guardarLectura(e,'t1',tipos,dominios);e.borrador.emisor='Otro';guardarLectura(e,'t2',tipos,dominios);console.log(JSON.stringify([e.inicial.emisor,e.revelada_en,cambioDeCriterio(e)]));")
        self.assertEqual(r, ["Ejemplo", "t1", True])

    def test_comentarios_no_se_confunden_con_cambio_de_etiqueta(self):
        r = self.js("const e=registro();guardarLectura(e,'t',tipos,dominios);e.borrador.comentarios='Agrego una página';console.log(JSON.stringify(cambioDeCriterio(e))); ")
        self.assertFalse(r)

    def test_no_finaliza_sin_primera_lectura(self):
        self.assertTrue(self.js("console.log(JSON.stringify(errorDe(()=>finalizar(registro(),'t',tipos,dominios))));"))

    def test_dudoso_termina_ficha_pero_no_valida_documento(self):
        r = self.js("const e=registro();e.borrador.decision='dudoso';e.borrador.comentarios='Duda';guardarLectura(e,'t1',tipos,dominios);finalizar(e,'t2',tipos,dominios);console.log(JSON.stringify([estadoRegistro(e),e.historial.length]));")
        self.assertEqual(r, ["dudoso", 1])

    def test_roundtrip_respaldo_conserva_comentarios_y_ficha(self):
        r = self.js("const e=registro();e.borrador.comentarios='Línea 1\\nLínea 2, á';guardarLectura(e,'t1',tipos,dominios);finalizar(e,'t2',tipos,dominios);const p=exportarEstado(D,{a:e},'t3');const restaurado=importarEstado(D,p,{});console.log(JSON.stringify([restaurado.a,e,Object.keys(restaurado)]));")
        self.assertEqual(r[0], r[1])
        self.assertEqual(r[2], ["a"])

    def test_importacion_no_pisa_revision_local(self):
        r = self.js("const e=registro();e.borrador.comentarios='Local';const p=exportarEstado(D,{a:registro()},'t');console.log(JSON.stringify(importarEstado(D,p,{a:e}).a.borrador.comentarios));")
        self.assertEqual(r, "Local")

    def test_importacion_rechaza_inventario_distinto_y_duplicados(self):
        r = self.js("const p=exportarEstado(D,{a:registro()},'t');const copia=copiar(p);copia.decisiones.push(copia.decisiones[0]);console.log(JSON.stringify([errorDe(()=>importarEstado(D,{...p,huella_fuentes:'otra'},{})),errorDe(()=>importarEstado(D,copia,{}))]));")
        self.assertTrue(all(r))

    def test_antecedentes_v2_no_inventan_lectura_ciega_ni_datos(self):
        r = self.js("const p={receta:'interfaz-corpus-v2-ciega',huella_fuentes:'h',decisiones:[{id:'a',ciega:{decision:'confirmar'},adjudicada:{decision:'confirmar'},observaciones:'Nota previa',propuesta:{emisor:'NO COPIAR'}}]};const e=importarEstado(D,p,{}).a;const antes=copiar(e);e.borrador=ficha();guardarLectura(e,'t',tipos,dominios);console.log(JSON.stringify([antes.borrador.emisor,antes.borrador.comentarios,estadoRegistro(antes),e.origen_lectura,e.antecedente_v2.propuesta.emisor]));")
        self.assertEqual(r, ["", "Nota previa", "pendiente", "revision_con_antecedentes_v2", "NO COPIAR"])

    def test_importacion_rechaza_completado_sin_datos(self):
        r = self.js("const e=registro();e.finalizado_en='t';const p=exportarEstado(D,{a:e},'t');console.log(JSON.stringify(errorDe(()=>importarEstado(D,p,{}))));")
        self.assertTrue(r)

    def test_plantilla_generada_coincide_y_conserva_inventario(self):
        html = (ROOT / "experimentos/revision_corpus/revision_documental_v3.html").read_text(encoding="utf-8")
        v2 = (ROOT / "experimentos/revision_corpus/revision_corpus_v2.html").read_text(encoding="utf-8")
        def datos(texto):
            return json.loads(re.search(r'<script type="application/json" id="datos">(.*?)</script>', texto, re.S)[1])
        self.assertEqual(datos(html)["documentos"], datos(v2)["documentos"])
        self.assertEqual(datos(html)["huella_fuentes"], datos(v2)["huella_fuentes"])
        self.assertEqual(len(datos(html)["documentos"]), 59)
        self.assertIn((ASSETS / "interfaz.js").read_text(encoding="utf-8"), html)
        for prohibido in ["innerHTML", "fetch(", "XMLHttpRequest", "document.write"]:
            self.assertNotIn(prohibido, html)


if __name__ == "__main__":
    unittest.main()
