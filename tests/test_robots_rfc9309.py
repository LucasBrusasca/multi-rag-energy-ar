"""Normative RFC 9309 examples, plus the four things v2 got wrong.

The examples in `EjemplosNormativosRFC9309` are taken from the RFC itself. If
they fail, the implementation is wrong - not the test.

The other classes pin the four defects an independent review found in the first
RFC-9309 attempt: prefix-matched agents instead of product tokens, decoding
reserved characters, specificity measured as pattern length, and an empty group
falling back to the wildcard.

[ES] Ejemplos normativos de la RFC 9309, mas las cuatro cosas que la v2 hizo mal.

Los ejemplos de `EjemplosNormativosRFC9309` estan tomados de la propia RFC. Si
fallan, esta mal la implementacion, no la prueba.

Las otras clases fijan los cuatro defectos que una revision independiente
encontro en el primer intento de RFC 9309: agentes comparados por prefijo en
lugar de por token de producto, decodificacion de caracteres reservados,
especificidad medida como largo del patron, y un grupo vacio cayendo al comodin.
"""

import unittest

from multirag.acquisition.robots import (
    GRUPO_VACIO,
    Robots,
    normalizar_ruta,
    token_de_producto,
)


AGENTE = "multi-rag-energy-ar/0.1 (investigacion academica)"


def leer(texto: str) -> Robots:
    return Robots.desde_texto(texto)


class EjemplosNormativosRFC9309(unittest.TestCase):
    """[ES] Tomados textualmente de la RFC 9309, seccion 5.1."""

    SIMPLE = """
User-Agent: *
Disallow: *.gif$
Disallow: /example/
Allow: /publications/

User-Agent: foobot
Disallow: /
Allow: /example/page.html
Allow: /example/allowed.gif

User-Agent: barbot
User-Agent: bazbot
Disallow: /example/page.html

User-Agent: quxbot
"""

    def test_el_grupo_comodin(self):
        r = leer(self.SIMPLE)
        self.assertTrue(r.permite("/publications/x.html", "otrobot").permitido)
        self.assertFalse(r.permite("/example/x.html", "otrobot").permitido)
        self.assertFalse(r.permite("/cualquiera/imagen.gif", "otrobot").permitido)

    def test_foobot_solo_puede_las_dos_rutas_permitidas(self):
        # The RFC states foobot is disallowed everything except those two paths.
        # [ES] La RFC dice que a foobot se le prohibe todo salvo esas dos rutas.
        r = leer(self.SIMPLE)
        self.assertTrue(r.permite("/example/page.html", "foobot").permitido)
        self.assertTrue(r.permite("/example/allowed.gif", "foobot").permitido)
        self.assertFalse(r.permite("/", "foobot").permitido)
        self.assertFalse(r.permite("/publications/x.html", "foobot").permitido)
        self.assertFalse(r.permite("/example/otra.html", "foobot").permitido)

    def test_barbot_y_bazbot_comparten_el_grupo(self):
        # Two consecutive User-agent lines, one set of rules.
        # [ES] Dos lineas User-agent consecutivas, un solo juego de reglas.
        r = leer(self.SIMPLE)
        for bot in ("barbot", "bazbot"):
            self.assertFalse(r.permite("/example/page.html", bot).permitido, bot)
            self.assertTrue(r.permite("/example/allowed.gif", bot).permitido, bot)
            self.assertTrue(r.permite("/", bot).permitido, bot)

    def test_quxbot_tiene_grupo_vacio_y_todo_permitido(self):
        # THE case an empty-group bug gets wrong. quxbot has its own group with
        # no rules; falling back to `*` would forbid `/example/` for it, which
        # the file deliberately did not do.
        # [ES] EL caso que arruina un bug de grupo vacio. quxbot tiene grupo
        # propio sin reglas; caer al `*` le prohibiria `/example/`, que el
        # archivo deliberadamente no hizo.
        r = leer(self.SIMPLE)
        d = r.permite("/example/x.html", "quxbot")
        self.assertTrue(d.permitido)
        self.assertEqual(d.motivo, GRUPO_VACIO)
        self.assertTrue(r.permite("/cualquiera/x.gif", "quxbot").permitido)

    FUSION = """
User-Agent: example-bot
Disallow: /foo
Disallow: /bar

User-Agent: example-bot
Disallow: /baz
"""

    def test_los_grupos_repetidos_fusionan(self):
        # RFC 9309 section 2.2.1.
        r = leer(self.FUSION)
        for ruta in ("/foo", "/bar", "/baz"):
            self.assertFalse(r.permite(ruta, "example-bot").permitido, ruta)


class TokenDeProducto(unittest.TestCase):
    """[ES] Se compara el token de producto, exacto, no un prefijo cualquiera."""

    def test_se_extrae_antes_de_la_barra_o_del_espacio(self):
        self.assertEqual(
            token_de_producto("multi-rag-energy-ar/0.1 (x)"), "multi-rag-energy-ar"
        )
        self.assertEqual(token_de_producto("foobot"), "foobot")
        self.assertEqual(token_de_producto("FooBot/1.0"), "foobot")

    def test_un_grupo_con_un_prefijo_del_token_no_nos_captura(self):
        # `startswith` would have let a group named `multi` capture us.
        # [ES] `startswith` habria dejado que un grupo llamado `multi` nos
        # capturara.
        r = leer("User-agent: multi\nDisallow: /x/\n")
        self.assertTrue(r.permite("/x/a", AGENTE).permitido)

    def test_un_grupo_mas_largo_que_el_token_tampoco(self):
        r = leer("User-agent: multi-rag-energy-ar-2\nDisallow: /x/\n")
        self.assertTrue(r.permite("/x/a", AGENTE).permitido)

    def test_el_token_exacto_si_nos_captura(self):
        r = leer("User-agent: multi-rag-energy-ar\nDisallow: /x/\n")
        self.assertFalse(r.permite("/x/a", AGENTE).permitido)


class EspecificidadPorOctetos(unittest.TestCase):
    """[ES] Octetos coincidentes, no largo del patron: cambian los veredictos."""

    def test_un_comodin_puede_ser_mas_especifico_que_un_literal_mas_largo(self):
        # `/*.htm` is six characters and `/page` is five, but `/*.htm`
        # constrains all nine octets of `/page.htm` because it pins both ends.
        # Pattern length would get this verdict backwards.
        # [ES] `/*.htm` mide seis caracteres y `/page` cinco, pero `/*.htm`
        # restringe los nueve octetos de `/page.htm` porque fija los dos
        # extremos. El largo del patron daria este veredicto al reves.
        r = leer("User-agent: *\nAllow: /page\nDisallow: /*.htm\n")
        d = r.permite("/page.htm", AGENTE)
        self.assertFalse(d.permitido)
        self.assertEqual(d.octetos_disallow, 9)
        self.assertEqual(d.octetos_allow, 5)

    def test_un_literal_mas_largo_gana_a_un_comodin_corto(self):
        # The reverse must hold too, or the measure is merely inverted. The
        # non-greedy wildcard makes `/fish*` constrain five octets, not twelve.
        # [ES] Lo inverso tambien tiene que valer, o la medida solo esta dada
        # vuelta. El comodin no codicioso hace que `/fish*` restrinja cinco
        # octetos, no doce.
        r = leer("User-agent: *\nDisallow: /fish*\nAllow: /fishheads\n")
        d = r.permite("/fishheads/x", AGENTE)
        self.assertTrue(d.permitido)
        self.assertEqual(d.octetos_allow, 10)
        self.assertEqual(d.octetos_disallow, 5)

    def test_el_caso_de_edenor_sigue_dando_prohibido(self):
        r = leer("User-Agent: *\nAllow: /\nDisallow: /files/\n")
        d = r.permite("https://www.edenor.com/files/investors/x.pdf", AGENTE)
        self.assertFalse(d.permitido)
        self.assertEqual(d.octetos_disallow, 7)
        self.assertEqual(d.octetos_allow, 1)


class NormalizacionDeReservados(unittest.TestCase):
    """[ES] Percent-encoding canonico: se decodifica solo lo no reservado."""

    def test_los_no_reservados_se_decodifican(self):
        self.assertEqual(normalizar_ruta("/fi%6Ces/"), "/files/")
        self.assertEqual(normalizar_ruta("/a%2Db"), "/a-b")

    def test_los_reservados_quedan_codificados(self):
        # Decoding `%3F` would turn a path segment into a query separator, and
        # decoding `%2F` would turn one segment into two.
        # [ES] Decodificar `%3F` convertiria un segmento de ruta en un separador
        # de query, y decodificar `%2F` convertiria un segmento en dos.
        self.assertEqual(normalizar_ruta("/a%3Fb"), "/a%3Fb")
        self.assertEqual(normalizar_ruta("/a%2Fb"), "/a%2Fb")
        self.assertEqual(normalizar_ruta("/a%23b"), "/a%23b")

    def test_el_hexadecimal_se_normaliza_a_mayuscula(self):
        self.assertEqual(normalizar_ruta("/a%2fb"), "/a%2Fb")

    def test_lo_no_ascii_se_codifica(self):
        self.assertEqual(normalizar_ruta("/información/"), "/informaci%C3%B3n/")

    def test_la_regla_y_la_ruta_se_normalizan_igual(self):
        # Both sides go through the same function, so an encoded URL cannot walk
        # past a rule that names it, in either direction.
        # [ES] Los dos lados pasan por la misma funcion, asi que una URL
        # codificada no puede pasar por delante de una regla que la nombra, en
        # ninguna de las dos direcciones.
        r = leer("User-agent: *\nDisallow: /informaci%C3%B3n/\n")
        self.assertFalse(r.permite("/información/x", AGENTE).permitido)
        self.assertFalse(r.permite("/informaci%C3%B3n/x", AGENTE).permitido)


if __name__ == "__main__":
    unittest.main()
