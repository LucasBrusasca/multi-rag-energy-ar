"""Tests for the domain instruction, help and criterion versioning of v3.

Two kinds: structure read off the generated file, and behaviour executed under
node. The behavioural half matters most for versioning - a criterion stamp that
is written retroactively over old records would look identical in the source and
be wrong in the data.

[ES] Pruebas de la consigna de dominios, la ayuda y el versionado de criterio de
la v3.

Dos tipos: estructura leida del archivo generado, y comportamiento ejecutado con
node. La mitad de comportamiento es la que mas importa para el versionado: un
sello de criterio escrito retroactivamente sobre registros viejos se veria igual
en el fuente y estaria mal en los datos.
"""

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from multirag.config import SILOS
from multirag.paths import EXPERIMENTS_DIR

HTML = EXPERIMENTS_DIR / "revision_corpus" / "revision_documental_v3.html"
INICIO = "/* === INICIO LOGICA PURA === */"
FIN = "/* === FIN LOGICA PURA === */"
NODE = shutil.which("node")


def html_generado() -> str:
    if not HTML.exists():
        raise unittest.SkipTest(f"no existe {HTML}")
    return HTML.read_text(encoding="utf-8")


def en_node(html: str, cuerpo: str):
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


class ConsignaDeDominios(unittest.TestCase):
    """[ES] Lo que el revisor lee antes de marcar una casilla."""

    def setUp(self):
        self.html = html_generado()

    def test_el_titulo_del_campo_es_dominios_de_conocimiento(self):
        self.assertIn("<legend>Dominios de conocimiento</legend>", self.html)

    def test_la_consigna_pide_senalar_un_pasaje_y_no_un_umbral(self):
        # The criterion is "can you point at it", not "does it appear N times".
        # A count threshold would make a one-article tax provision invisible and
        # a passing mention decisive.
        # [ES] El criterio es «podés señalarlo», no «aparece N veces». Un umbral
        # de conteo volvería invisible una disposición impositiva de un artículo
        # y decisiva una mención al pasar.
        for frase in (
            "Marcá un tema si podés señalar un pasaje o tabla",
            "una regla, explicación o dato concreto",
            "No hace falta que sea el tema principal",
            "No alcanza con nombrarlo o remitir a otro documento sin desarrollarlo",
            "Indicá dónde lo encontraste",
        ):
            self.assertIn(frase, self.html, frase)

    def test_aclara_que_no_se_asignan_los_fragmentos(self):
        # The distinction the project documents as rule 3: the document label is
        # not inherited by its chunks.
        # [ES] La distinción que el proyecto documenta como regla 3: la etiqueta
        # documental no la heredan sus fragmentos.
        self.assertIn(
            "no estás asignando todos sus fragmentos a esos silos", self.html
        )

    def test_no_hay_umbrales_de_cantidad_en_la_consigna(self):
        # No article count, page count or mention count as a universal threshold.
        # [ES] Ni cantidad de artículos, ni de páginas, ni de menciones como
        # umbral universal.
        legend = self.html.index("<legend>Dominios de conocimiento</legend>")
        bloque = self.html[legend:legend + 4000]
        for prohibido in ("al menos 3", "al menos tres", "más de una página",
                          "al menos dos páginas", "menciones", "capítulo entero"):
            self.assertNotIn(prohibido, bloque, prohibido)


class AyudaPorDominio(unittest.TestCase):
    """[ES] Descripción visible + desplegable, para los cuatro dominios."""

    def setUp(self):
        self.html = html_generado()
        m = re.search(r"const temas=\{.*?\n\};", self.html, re.S)
        assert m, "no se encontró el bloque temas"
        self.bloque = m.group(0)

    def test_los_cuatro_dominios_tienen_las_tres_secciones(self):
        for dominio in ("legal", "impositivo", "contable", "financiero"):
            trozo = self.bloque[self.bloque.index(dominio + ":"):]
            trozo = trozo[:trozo.index("]],") + 3] if "]]," in trozo else trozo
            for clave in ("incluye:", "no_alcanza:", "ejemplo:"):
                self.assertIn(clave, trozo, f"{dominio} sin {clave}")

    def test_hay_un_desplegable_por_dominio(self):
        self.assertIn("Qué incluye / Qué no alcanza / Ejemplo", self.html)
        self.assertIn('elemento("details")', self.html)

    def test_los_ejemplos_cubren_normas_informes_y_planillas(self):
        # A reviewer works on all three shapes; examples that only mention
        # reports would not help on a norm or a spreadsheet.
        # [ES] Un revisor trabaja con las tres formas; ejemplos que solo hablen
        # de informes no ayudan ante una norma o una planilla.
        for dominio in ("legal", "impositivo", "contable"):
            trozo = self.bloque[self.bloque.index(dominio + ":"):][:2600]
            for forma in ("Norma:", "Informe:", "Planilla:"):
                self.assertIn(forma, trozo, f"{dominio} sin ejemplo de {forma}")

    def test_hay_una_explicacion_para_distinguir_contable_de_financiero(self):
        self.assertIn("Contable o financiero: cómo distinguirlos", self.html)
        self.assertIn("Un juego de estados financieros es contable", self.html)

    def test_hay_ejemplos_de_superposicion(self):
        self.assertIn("Legal + impositivo", self.html)
        self.assertIn("Contable + financiero", self.html)

    def test_los_ejemplos_se_declaran_como_ejemplos_y_no_como_reglas(self):
        # Otherwise a reviewer reads "annual report -> contable + financiero" as
        # a rule and stops reading the document.
        # [ES] Si no, un revisor lee «memoria → contable + financiero» como regla
        # y deja de leer el documento.
        self.assertIn("Los ejemplos son ejemplos, no reglas", self.html)
        self.assertIn("Ningún tipo de archivo determina por sí solo un tema", self.html)

    def test_la_ayuda_sigue_las_definiciones_del_proyecto(self):
        # Anchored to `config.SILOS`, not invented for the interface. Spot-check
        # terms each documented definition names explicitly.
        # [ES] Anclada en `config.SILOS`, no inventada para la interfaz. Se
        # verifican términos que cada definición documentada nombra explícitamente.
        self.assertEqual(set(SILOS), {"legal", "impositivo", "contable", "financiero"})
        for termino in ("audiencias públicas", "ENARGAS", "concesiones"):
            self.assertIn(termino.split()[0][:6].lower(),
                          self.bloque.lower(), termino)
        for termino in ("alícuotas", "base imponible", "retenciones"):
            self.assertIn(termino.lower(), self.bloque.lower(), termino)
        for termino in ("flujo de efectivo", "NIIF", "notas"):
            self.assertIn(termino.lower(), self.bloque.lower(), termino)
        for termino in ("obligaciones negociables", "apalancamiento", "calificaci"):
            self.assertIn(termino.lower(), self.bloque.lower(), termino)

    def test_ninguno_no_es_lo_mismo_que_no_estoy_seguro(self):
        # Conflating them would turn every doubt into a negative label.
        # [ES] Confundirlos convertiría cada duda en una etiqueta negativa.
        self.assertIn("No es «no estoy seguro»", self.html)


class CorrespondenciaRegulatorio(unittest.TestCase):
    """[ES] Cuatro silos: `regulatorio` energético vive dentro de `legal`."""

    def setUp(self):
        self.html = html_generado()

    def test_el_nombre_visible_incluye_regulatorio_energetico(self):
        self.assertIn("Legal / regulatorio energético", self.html)

    def test_el_identificador_sigue_siendo_legal(self):
        # The visible name changed; the id must not. A renamed id would break
        # every stored record and the persisted classification.
        # [ES] Cambió el nombre visible; el identificador no puede cambiar. Un id
        # renombrado rompería cada registro guardado y la clasificación persistida.
        self.assertIn('legal:["Legal / regulatorio energético"', self.html)

    def test_no_hay_un_quinto_silo(self):
        # `temas` sits outside the pure-logic block, so this is read off the
        # source rather than executed.
        # [ES] `temas` está fuera del bloque de lógica pura, así que esto se lee
        # del fuente en vez de ejecutarse.
        bloque = re.search(r"const temas=\{.*?\n\};", self.html, re.S).group(0)
        claves = re.findall(r"^\s(\w+):\[", bloque, re.M)
        self.assertEqual(claves, ["legal", "impositivo", "contable",
                                  "financiero", "ninguno"])
        self.assertEqual(set(claves) - {"ninguno"}, set(SILOS))

    def test_se_asigna_por_materia_y_no_por_forma_juridica(self):
        # The trap this closes: "it is a law, therefore legal". A tax law is a
        # law and is still `impositivo`.
        # [ES] La trampa que cierra: «es una ley, entonces legal». Una ley
        # tributaria es una ley y sigue siendo `impositivo`.
        self.assertIn("Se marca por materia, no por forma jurídica", self.html)
        self.assertIn("una ley tributaria sigue siendo una ley", self.html.lower())

    def test_advierte_los_dos_sentidos_de_regulatorio(self):
        # The empirical finding: 10 of the 17 historical `regulatorio` labels
        # sit on company documents and mean "operates in a regulated sector".
        # [ES] El hallazgo empírico: 10 de las 17 etiquetas históricas
        # `regulatorio` están en documentos de empresas y significan «opera en un
        # sector regulado».
        self.assertIn("No es un quinto tema", self.html)
        self.assertIn("esta empresa opera en un sector regulado", self.html)

    def test_la_lectura_del_regulatorio_viejo_se_declara_no_verificada(self):
        # What is observed is the label distribution. What that label MEANT is a
        # hypothesis: nobody recorded the original criterion and none of those
        # documents has been read. Stating it as fact would launder a guess into
        # the instrument the reviewer trusts.
        # [ES] Lo observado es la distribución de etiquetas. Lo que esa etiqueta
        # SIGNIFICABA es hipótesis: nadie registró el criterio original y ninguno
        # de esos documentos se leyó. Afirmarlo como hecho metería una conjetura
        # dentro del instrumento del que el revisor se fía.
        self.assertIn("eso no está verificado", self.html.lower())
        self.assertIn("todavía no se leyeron", self.html)


class AvisoDeNoPersistencia(unittest.TestCase):
    """[ES] Sin guardado automático se puede trabajar, pero hay que avisarlo."""

    def setUp(self):
        self.html = html_generado()

    def test_terminar_no_dice_guardado_cuando_no_hay_persistencia(self):
        # Saying "quedaron guardados" with localStorage blocked is false: the
        # work is in memory and dies with the tab.
        # [ES] Decir «quedaron guardados» con localStorage bloqueado es falso: el
        # trabajo está en memoria y muere con la pestaña.
        i = self.html.index("Ficha terminada: ")
        bloque = self.html[i:i + 500]
        self.assertIn("persistencia", bloque, "el mensaje debe depender del estado")
        self.assertIn("solo en memoria y se pierde al cerrar", bloque)
        self.assertIn("Descargá el avance", bloque)

    def test_el_bloqueo_no_impide_trabajar_en_memoria(self):
        # `guardar()` must swallow the blocked write and carry on; if it threw,
        # `editar()` would die and the whole form would stop responding.
        # [ES] `guardar()` tiene que tragarse la escritura bloqueada y seguir; si
        # lanzara, `editar()` moriría y el formulario entero dejaría de responder.
        i = self.html.index("function guardar()")
        bloque = self.html[i:i + 420]
        self.assertIn("if(!bloqueoAlmacen)", bloque)
        self.assertIn("catch(e){persistencia=false;}", bloque)
        self.assertIn("No hay guardado automático disponible", bloque)


class ConteosFueraDeLaVistaPrincipal(unittest.TestCase):
    """[ES] Los umbrales de la máquina no encabezan la lectura humana."""

    def setUp(self):
        self.html = html_generado()

    def test_la_vista_principal_muestra_pasaje_pagina_y_explicacion(self):
        self.assertIn('"página "+(ev.pagina||"no indicada")', self.html)
        self.assertIn('se encontró «"+ev.termino+"»', self.html)

    def test_los_conteos_bajan_a_un_registro_tecnico(self):
        # `motivo` carries "terminos=2/3 ocurrencias=6/6". It stays available -
        # it is technical evidence - but behind a <details>, not on the first
        # line the reviewer reads.
        # [ES] `motivo` trae «terminos=2/3 ocurrencias=6/6». Sigue disponible
        # —es evidencia técnica— pero detrás de un <details>, no en la primera
        # línea que lee el revisor.
        principal = re.search(r'fund\.append\(elemento\("p",\(ev\.dominio.*?"help"\)\);',
                              self.html, re.S).group(0)
        for contador in ("motivo", "ocurrencias", "terminos", "paginas_termino"):
            self.assertNotIn(contador, principal,
                             f"{contador} no va en la línea que se lee primero")
        self.assertIn("ev.motivo", self.html, "pero el motivo se conserva")
        self.assertIn("Registro técnico: cómo contó la máquina", self.html)

    def test_declara_que_ocultarlos_no_vuelve_ciega_la_revision(self):
        # The honest limit. Hiding the counts reduces anchoring; it does not
        # turn an assisted review into a blind reading.
        # [ES] El límite honesto. Ocultar los conteos reduce el anclaje; no
        # convierte una revisión asistida en una lectura ciega.
        self.assertIn("revisión asistida, no una lectura ciega", self.html)
        self.assertIn("Tu criterio no usa umbrales", self.html)


class CriterioVersionado(unittest.TestCase):
    """[ES] Qué criterio se usó, y que no se aplique hacia atrás."""

    def setUp(self):
        self.html = html_generado()

    def _js(self, cuerpo):
        return en_node(self.html, cuerpo)

    def test_una_ficha_nueva_queda_sellada_con_el_criterio_vigente(self):
        r = self._js(
            "const e={borrador:nuevaFicha()};\n"
            "e.borrador.decision='incluir';e.borrador.emisor='X';"
            "e.borrador.tipo='ley';e.borrador.periodo='2025';"
            "e.borrador.dominios=['legal'];e.borrador.consultado=true;\n"
            "guardarLectura(e,'2026-08-30T00:00:00Z',['ley'],['legal']);\n"
            "console.log(JSON.stringify({v:e.criterio_version,o:e.origen_lectura}));"
        )
        self.assertEqual(r["v"], "criterio-dominios-2026-08-30")
        self.assertEqual(r["o"], "manual_pre_revelado")

    def test_un_registro_anterior_no_recibe_el_criterio_nuevo(self):
        # THE point. Regenerating the file must not rewrite the history of a
        # decision taken under the previous instruction.
        # [ES] EL punto. Regenerar el archivo no puede reescribir la historia de
        # una decisión tomada con la consigna anterior.
        r = self._js(
            "const e={borrador:nuevaFicha(),inicial:nuevaFicha(),"
            "revelada_en:'2026-08-29T00:00:00Z',origen_lectura:'manual_pre_revelado'};\n"
            "e.borrador.decision='incluir';e.borrador.emisor='X';"
            "e.borrador.tipo='ley';e.borrador.periodo='2025';"
            "e.borrador.dominios=['legal'];e.borrador.consultado=true;\n"
            "guardarLectura(e,'2026-08-30T00:00:00Z',['ley'],['legal']);\n"
            "console.log(JSON.stringify({v:e.criterio_version===undefined?null:e.criterio_version}));"
        )
        self.assertIsNone(r["v"], "una ficha ya iniciada no se resella")

    def test_el_historial_guarda_el_criterio_de_cada_cierre(self):
        r = self._js(
            "const e={borrador:nuevaFicha()};\n"
            "e.borrador.decision='incluir';e.borrador.emisor='X';"
            "e.borrador.tipo='ley';e.borrador.periodo='2025';"
            "e.borrador.dominios=['legal'];e.borrador.consultado=true;\n"
            "guardarLectura(e,'2026-08-30T00:00:00Z',['ley'],['legal']);\n"
            "finalizar(e,'2026-08-30T01:00:00Z',['ley'],['legal']);\n"
            "console.log(JSON.stringify(e.historial));"
        )
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["criterio_version"], "criterio-dominios-2026-08-30")

    def test_la_exportacion_declara_el_criterio_usado(self):
        r = self._js(
            "const D={receta:'r',huella_fuentes:'h',alcance:{},documentos:["
            "{id:'a',archivo:'a.pdf',ruta:'r',cohorte:'activo'}]};\n"
            "console.log(JSON.stringify(exportarEstado(D,{},'2026-08-30')));"
        )
        self.assertEqual(r["criterio_version"], "criterio-dominios-2026-08-30")
        self.assertIn("contenido sustantivo", r["criterio_resumen"])


class AntecedenteDeclarado(unittest.TestCase):
    """[ES] Lo que el sistema no puede saber, se declara; no se inventa."""

    def setUp(self):
        self.html = html_generado()

    def test_existe_la_casilla_para_declararlo(self):
        self.assertIn('id="antecedente-declarado"', self.html)
        self.assertIn("El sistema no puede saberlo por su cuenta", self.html)

    def test_declararlo_cambia_el_origen_de_la_lectura(self):
        # A reading taken after seeing the proposal must not be recorded as
        # independent. The system cannot detect it, so the person declares it.
        # [ES] Una lectura tomada después de ver la propuesta no puede quedar
        # registrada como independiente. El sistema no puede detectarlo, así que
        # lo declara la persona.
        r = en_node(self.html, (
            "function ficha(dec){const e={borrador:nuevaFicha()};"
            "e.borrador.decision='incluir';e.borrador.emisor='X';"
            "e.borrador.tipo='ley';e.borrador.periodo='2025';"
            "e.borrador.dominios=['legal'];e.borrador.consultado=true;"
            "e.borrador.antecedente_declarado=dec;"
            "guardarLectura(e,'2026-08-30T00:00:00Z',['ley'],['legal']);return e;}\n"
            "console.log(JSON.stringify({sin:ficha(false).origen_lectura,"
            "con:ficha(true).origen_lectura}));"
        ))
        self.assertEqual(r["sin"], "manual_pre_revelado")
        self.assertEqual(r["con"], "revision_con_antecedente_declarado")

    def test_un_antecedente_v2_importado_sigue_teniendo_prioridad(self):
        # An imported v2 record is an antecedent the system DOES know about, and
        # it must not be downgraded by an unticked box.
        # [ES] Un registro v2 importado es un antecedente que el sistema SÍ
        # conoce, y no puede degradarse porque una casilla esté sin marcar.
        r = en_node(self.html, (
            "const e={borrador:nuevaFicha(),antecedente_v2:{algo:1}};\n"
            "e.borrador.decision='incluir';e.borrador.emisor='X';"
            "e.borrador.tipo='ley';e.borrador.periodo='2025';"
            "e.borrador.dominios=['legal'];e.borrador.consultado=true;\n"
            "guardarLectura(e,'2026-08-30T00:00:00Z',['ley'],['legal']);\n"
            "console.log(JSON.stringify({o:e.origen_lectura}));"
        ))
        self.assertEqual(r["o"], "revision_con_antecedentes_v2")


class ConservacionDeRegistros(unittest.TestCase):
    """[ES] Nada de lo ya cargado se pierde ni se reetiqueta."""

    def setUp(self):
        self.html = html_generado()

    def test_recuperar_un_respaldo_conserva_comentarios_y_evidencia(self):
        r = en_node(self.html, (
            "const e={borrador:nuevaFicha()};\n"
            "e.borrador.decision='dudoso';e.borrador.emisor='Emisor';"
            "e.borrador.tipo='ley';e.borrador.periodo='2025';"
            "e.borrador.dominios=['legal'];e.borrador.consultado=true;"
            "e.borrador.evidencia='página 3, tabla 2';"
            "e.borrador.comentarios='la tabla sigue en la página siguiente';\n"
            "guardarLectura(e,'2026-08-30T00:00:00Z',['ley'],['legal']);\n"
            "const D={receta:'r',huella_fuentes:'h',alcance:{},documentos:["
            "{id:'a',archivo:'a.pdf',ruta:'r',cohorte:'activo'}]};\n"
            "const paq=exportarEstado(D,{a:e},'2026-08-30');\n"
            "console.log(JSON.stringify(paq.decisiones[0].registro));"
        ))
        self.assertEqual(r["borrador"]["evidencia"], "página 3, tabla 2")
        self.assertEqual(r["borrador"]["comentarios"],
                         "la tabla sigue en la página siguiente")
        self.assertEqual(r["inicial"]["dominios"], ["legal"])
        self.assertEqual(r["criterio_version"], "criterio-dominios-2026-08-30")

    def test_un_respaldo_anterior_se_recupera_entero_y_sin_resellar(self):
        # The whole point of the recovery requirement: a backup written before
        # this change must come back with every decision and comment intact, and
        # must NOT be stamped with the new criterion it was not taken under.
        # [ES] El punto del requisito de recuperación: un respaldo escrito antes
        # de este cambio tiene que volver con cada decisión y comentario
        # intactos, y NO puede quedar sellado con el criterio nuevo, bajo el que
        # no fue tomado.
        r = en_node(self.html, (
            "const D={receta:'r',huella_fuentes:'h',alcance:{},documentos:["
            "{id:'a',archivo:'a.pdf',ruta:'r',cohorte:'activo'}]};\n"
            "const vieja={borrador:{decision:'dudoso',emisor:'E',tipo:'ley',"
            "periodo:'2025',periodo_desconocido:false,dominios:['legal','contable'],"
            "evidencia:'pág. 3, celda B7',comentarios:'la tabla sigue en la hoja 2',"
            "consultado:true},inicial:{decision:'dudoso',emisor:'E',tipo:'ley',"
            "periodo:'2025',periodo_desconocido:false,dominios:['legal'],"
            "evidencia:'pág. 3',comentarios:'nota inicial',consultado:true},"
            "revelada_en:'2026-08-20T00:00:00Z',origen_lectura:'manual_pre_revelado'};\n"
            "const paq={receta:D.receta,huella_fuentes:'h',fecha_exportacion:'2026-08-20',"
            "decisiones:[{id:'a',registro:vieja}]};\n"
            "const e=importarEstado(D,paq,{}).a;\n"
            "console.log(JSON.stringify({com:e.borrador.comentarios,"
            "ev:e.borrador.evidencia,dom:e.borrador.dominios,"
            "comIni:e.inicial.comentarios,domIni:e.inicial.dominios,"
            "origen:e.origen_lectura,ant:e.borrador.antecedente_declarado,"
            "sellado:'criterio_version' in e}));"
        ))
        self.assertEqual(r["com"], "la tabla sigue en la hoja 2")
        self.assertEqual(r["ev"], "pág. 3, celda B7")
        self.assertEqual(r["dom"], ["legal", "contable"])
        self.assertEqual(r["comIni"], "nota inicial")
        self.assertEqual(r["domIni"], ["legal"], "la primera lectura no se pisa")
        self.assertEqual(r["origen"], "manual_pre_revelado")
        self.assertFalse(r["ant"], "el campo ausente se completa en false")
        self.assertFalse(r["sellado"], "no se le atribuye el criterio nuevo")

    def test_el_campo_nuevo_no_rompe_una_ficha_vieja_sin_el(self):
        # A backup written before the field existed must still load, with the
        # field defaulting to false rather than the import failing.
        # [ES] Un respaldo escrito antes de que el campo existiera tiene que
        # seguir cargando, con el campo en false en vez de fallar la importación.
        r = en_node(self.html, (
            "const f=nuevaFicha();delete f.antecedente_declarado;\n"
            "console.log(JSON.stringify({tiene:'antecedente_declarado' in f,"
            "nueva:nuevaFicha().antecedente_declarado}));"
        ))
        self.assertFalse(r["tiene"])
        self.assertFalse(r["nueva"])


if __name__ == "__main__":
    unittest.main()
