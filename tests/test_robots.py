"""Tests for RFC 9309 robots.txt evaluation.

The reason these exist is a real incident: the acquisition script trusted
`urllib.robotparser`, which implements the 1994 first-match rule, and downloaded
twenty documents whose publishers had disallowed automated access. The files were
deleted. Every case below is a way that mistake, or one like it, could come back.

[ES] Pruebas de la evaluacion de robots.txt segun RFC 9309.

El motivo por el que existen es un incidente real: el script de adquisicion
confio en `urllib.robotparser`, que implementa la regla de primera-coincidencia
de 1994, y descargo veinte documentos cuyos editores habian prohibido el acceso
automatico. Los archivos se borraron. Cada caso de abajo es una forma en que ese
error, o uno parecido, podria volver.
"""

import unittest
import urllib.robotparser

from multirag.acquisition.robots import (
    EMPATE_A_FAVOR_DE_ALLOW,
    PROHIBIDO_POR_REGLA,
    ROBOTS_AUSENTE,
    ROBOTS_ILEGIBLE,
    Robots,
    normalizar_ruta,
)


AGENTE = "multi-rag-energy-ar/0.1 (investigacion academica)"


def leer(texto: str) -> Robots:
    return Robots.desde_texto(texto)


class CoincidenciaMasLarga(unittest.TestCase):
    """[ES] La regla que causo el incidente."""

    EDENOR = """
User-Agent: *
Allow: /
Disallow: /files/
Disallow: /centro-ayuda/
"""

    def test_el_caso_exacto_de_edenor(self):
        # THE case. `Allow: /` is one character; `Disallow: /files/` is seven.
        # The longer pattern governs, and the investor PDFs are refused.
        # [ES] EL caso. `Allow: /` es un caracter; `Disallow: /files/` son siete.
        # Gana el patrón más largo, y los PDF para inversores se rechazan.
        robots = leer(self.EDENOR)
        d = robots.permite(
            "https://www.edenor.com/files/investors/2026-05/EEFF.pdf", AGENTE
        )
        self.assertFalse(d.permitido)
        self.assertEqual(d.motivo, PROHIBIDO_POR_REGLA)
        self.assertEqual(d.octetos_disallow, 7)
        self.assertEqual(d.octetos_allow, 1)

    def test_el_resto_del_sitio_de_edenor_sigue_permitido(self):
        # The rule forbids `/files/`, not the site. A matcher that over-blocks
        # is as wrong as one that under-blocks, just less dangerous.
        # [ES] La regla prohíbe `/files/`, no el sitio. Un comparador que bloquea
        # de más está tan mal como uno que bloquea de menos, solo que es menos
        # peligroso.
        robots = leer(self.EDENOR)
        self.assertTrue(robots.permite("https://www.edenor.com/inversores", AGENTE).permitido)

    def test_la_biblioteca_estandar_da_lo_contrario_en_este_caso(self):
        # Documented on purpose. This is not a test of our code: it pins WHY our
        # code exists, so nobody replaces it with the standard library again.
        # [ES] Documentado a propósito. No es una prueba de nuestro código: fija
        # POR QUÉ existe, para que nadie vuelva a reemplazarlo por la biblioteca
        # estándar.
        stdlib = urllib.robotparser.RobotFileParser()
        stdlib.parse(self.EDENOR.splitlines())
        url = "https://www.edenor.com/files/investors/2026-05/EEFF.pdf"
        self.assertTrue(stdlib.can_fetch(AGENTE, url), "la stdlib permite")
        self.assertFalse(leer(self.EDENOR).permite(url, AGENTE).permitido, "nosotros no")

    def test_gana_el_patron_mas_largo_aunque_este_escrito_al_final(self):
        # [ES] El orden en el archivo no decide nada. Solo la especificidad.
        robots = leer("User-agent: *\nDisallow: /a/\nAllow: /a/b/\n")
        self.assertTrue(robots.permite("/a/b/c.pdf", AGENTE).permitido)
        self.assertFalse(robots.permite("/a/z.pdf", AGENTE).permitido)

    def test_el_empate_se_resuelve_a_favor_de_allow(self):
        # [ES] La RFC resuelve el empate hacia la regla menos restrictiva.
        robots = leer("User-agent: *\nDisallow: /x/\nAllow: /x/\n")
        d = robots.permite("/x/documento.pdf", AGENTE)
        self.assertTrue(d.permitido)
        self.assertEqual(d.motivo, EMPATE_A_FAVOR_DE_ALLOW)
        self.assertEqual(d.octetos_allow, d.octetos_disallow)


class GruposDeAgentes(unittest.TestCase):
    """[ES] Cómo se arman los grupos, que es donde un parser ingenuo se pierde."""

    def test_varios_user_agent_consecutivos_comparten_las_reglas(self):
        # Consecutive agent lines form ONE group. A parser that attached the
        # rules only to the last agent would leave the first one unrestricted.
        # [ES] Las líneas de agente consecutivas forman UN grupo. Un parser que
        # colgara las reglas solo del último agente dejaría al primero sin
        # restricción.
        robots = leer(
            "User-agent: alfa\n"
            "User-agent: beta\n"
            "User-agent: gamma\n"
            "Disallow: /privado/\n"
        )
        for agente in ("alfa", "beta", "gamma"):
            self.assertFalse(
                robots.permite("/privado/x", agente).permitido, agente
            )

    def test_grupos_repetidos_del_mismo_agente_fusionan_sus_reglas(self):
        # Keeping only the last group would silently drop the first group's
        # restriction - the exact shape of an under-blocking bug.
        # [ES] Quedarse solo con el último grupo tiraría en silencio la
        # restricción del primero: la forma exacta de un bug que bloquea de menos.
        robots = leer(
            "User-agent: alfa\n"
            "Disallow: /uno/\n"
            "\n"
            "User-agent: beta\n"
            "Disallow: /otro/\n"
            "\n"
            "User-agent: alfa\n"
            "Disallow: /dos/\n"
        )
        self.assertFalse(robots.permite("/uno/x", "alfa").permitido)
        self.assertFalse(robots.permite("/dos/x", "alfa").permitido)
        self.assertTrue(robots.permite("/otro/x", "alfa").permitido)

    def test_sin_grupo_especifico_se_usa_el_comodin(self):
        robots = leer(
            "User-agent: googlebot\nDisallow: /solo-google/\n"
            "\nUser-agent: *\nDisallow: /para-todos/\n"
        )
        self.assertFalse(robots.permite("/para-todos/x", AGENTE).permitido)
        self.assertTrue(robots.permite("/solo-google/x", AGENTE).permitido)

    def test_un_grupo_especifico_desplaza_al_comodin(self):
        # [ES] Si hay grupo propio, el comodín no se aplica: no se suman.
        # El nombre del grupo es el TOKEN DE PRODUCTO completo. Esta prueba usaba
        # `multi-rag` y esperaba que nos capturara: eso era coincidencia por
        # prefijo, y estaba mal.
        robots = leer(
            "User-agent: multi-rag-energy-ar\nDisallow: /nuestro/\n"
            "\nUser-agent: *\nDisallow: /de-todos/\n"
        )
        self.assertFalse(robots.permite("/nuestro/x", AGENTE).permitido)
        self.assertTrue(robots.permite("/de-todos/x", AGENTE).permitido)

    def test_el_token_de_producto_ignora_mayusculas_pero_es_exacto(self):
        # This test asserted PREFIX matching, and it was wrong: RFC 9309 compares
        # the product token in full. `MULTI-RAG` is a prefix of our token, not
        # our token, and a prefix must not capture us.
        # [ES] Esta prueba afirmaba coincidencia por PREFIJO y estaba mal: la RFC
        # 9309 compara el token de producto completo. `MULTI-RAG` es un prefijo
        # de nuestro token, no nuestro token, y un prefijo no debe capturarnos.
        parcial = leer("User-agent: MULTI-RAG\nDisallow: /x/\n")
        self.assertTrue(parcial.permite("/x/a", "multi-rag-energy-ar/0.1").permitido)

        exacto = leer("User-agent: MULTI-RAG-ENERGY-AR\nDisallow: /x/\n")
        self.assertFalse(exacto.permite("/x/a", "multi-rag-energy-ar/0.1").permitido)

    def test_reglas_antes_de_cualquier_agente_no_pertenecen_a_nadie(self):
        # [ES] Un archivo mal formado no debe otorgar reglas huérfanas.
        robots = leer("Disallow: /huerfana/\nUser-agent: *\nDisallow: /valida/\n")
        self.assertTrue(robots.permite("/huerfana/x", AGENTE).permitido)
        self.assertFalse(robots.permite("/valida/x", AGENTE).permitido)


class Comodines(unittest.TestCase):
    """[ES] `*` y `$`, que son parte del estándar y no adorno."""

    def test_asterisco_es_cualquier_secuencia(self):
        robots = leer("User-agent: *\nDisallow: /*/privado/\n")
        self.assertFalse(robots.permite("/a/privado/x.pdf", AGENTE).permitido)
        self.assertFalse(robots.permite("/b/c/privado/x.pdf", AGENTE).permitido)
        self.assertTrue(robots.permite("/privado-no/x.pdf", AGENTE).permitido)

    def test_peso_ancla_el_final_de_la_ruta(self):
        robots = leer("User-agent: *\nDisallow: /*.pdf$\n")
        self.assertFalse(robots.permite("/docs/informe.pdf", AGENTE).permitido)
        self.assertTrue(robots.permite("/docs/informe.pdf.html", AGENTE).permitido)

    def test_un_disallow_vacio_permite_todo(self):
        # [ES] Es la forma que tiene la RFC de escribir "sin restricciones".
        robots = leer("User-agent: *\nDisallow:\n")
        self.assertTrue(robots.permite("/lo-que-sea/x", AGENTE).permitido)

    def test_disallow_barra_prohibe_el_sitio_entero(self):
        robots = leer("User-agent: *\nDisallow: /\n")
        self.assertFalse(robots.permite("/", AGENTE).permitido)
        self.assertFalse(robots.permite("/cualquier/cosa.pdf", AGENTE).permitido)


class PercentEncoding(unittest.TestCase):
    """[ES] Una URL codificada no puede colarse por delante de una regla."""

    def test_la_ruta_codificada_coincide_con_la_regla_sin_codificar(self):
        # `/fi%6Ces/` IS `/files/`. A matcher comparing raw bytes would let the
        # encoded form walk straight past the rule that names it.
        # [ES] `/fi%6Ces/` ES `/files/`. Un comparador de bytes crudos dejaría
        # pasar la forma codificada por delante de la regla que la nombra.
        robots = leer("User-agent: *\nAllow: /\nDisallow: /files/\n")
        self.assertFalse(robots.permite("/fi%6Ces/informe.pdf", AGENTE).permitido)

    def test_la_regla_codificada_coincide_con_la_ruta_sin_codificar(self):
        # [ES] Y al revés: la normalización tiene que ser simétrica.
        robots = leer("User-agent: *\nDisallow: /docu%6Dentos/\n")
        self.assertFalse(robots.permite("/documentos/x.pdf", AGENTE).permitido)

    def test_lo_no_ascii_se_codifica_en_lugar_de_decodificarse(self):
        # This test asserted DECODING, and it was wrong. RFC 9309 requires
        # non-ASCII and reserved octets to be percent-ENCODED before comparison;
        # decoding is the opposite operation and breaks on reserved characters,
        # turning `%3F` into a query separator.
        # [ES] Esta prueba afirmaba DECODIFICACIÓN y estaba mal. La RFC 9309
        # exige que lo no ASCII y lo reservado esté percent-CODIFICADO antes de
        # comparar; decodificar es la operación inversa y se rompe con los
        # caracteres reservados, convirtiendo `%3F` en un separador de query.
        robots = leer("User-agent: *\nDisallow: /informacion/\n")
        self.assertFalse(robots.permite("/informacion/x", AGENTE).permitido)
        self.assertEqual(normalizar_ruta("/informaci%C3%B3n/"), "/informaci%C3%B3n/")
        self.assertEqual(normalizar_ruta("/información/"), "/informaci%C3%B3n/")

    def test_barra_codificada_no_se_decodifica(self):
        # Decoding `%2F` would turn one path segment into two and change what
        # the path means, so it stays encoded on both sides.
        # [ES] Decodificar `%2F` convertiría un segmento en dos y cambiaría lo
        # que la ruta significa, así que queda codificado de los dos lados.
        self.assertEqual(normalizar_ruta("/a%2Fb/c"), "/a%2Fb/c")
        self.assertNotIn("/a/b/", normalizar_ruta("/a%2Fb/c"))


class PoliticaConservadora(unittest.TestCase):
    """[ES] Qué se hace cuando las reglas no se pueden leer."""

    def test_robots_ausente_404_permite_todo(self):
        # The RFC: no robots.txt means no rules. Refusing here would block every
        # site that simply never published one.
        # [ES] La RFC: sin robots.txt no hay reglas. Negarse acá bloquearía todo
        # sitio que simplemente nunca publicó uno.
        d = Robots.ausente().permite("/lo-que-sea", AGENTE)
        self.assertTrue(d.permitido)
        self.assertEqual(d.motivo, ROBOTS_AUSENTE)

    def test_robots_ilegible_prohibe_todo(self):
        # A server error, a timeout or an unparseable body leaves the rules
        # UNKNOWN. When the action is taking someone else's documents, "I could
        # not read your rules" is not permission.
        # [ES] Un error de servidor, un timeout o un cuerpo inparseable dejan las
        # reglas DESCONOCIDAS. Cuando la acción es tomar documentos ajenos, "no
        # pude leer tus reglas" no es un permiso.
        d = Robots.ilegible("http 503").permite("/lo-que-sea", AGENTE)
        self.assertFalse(d.permitido)
        self.assertEqual(d.motivo, ROBOTS_ILEGIBLE)
        self.assertEqual(d.regla, "http 503")

    def test_las_dos_politicas_son_distintas_a_proposito(self):
        # [ES] Ausente y no-legible NO son lo mismo, y confundirlos es o
        # bloquear medio internet o descargar lo que no corresponde.
        self.assertTrue(Robots.ausente().permite("/x", AGENTE).permitido)
        self.assertFalse(Robots.ilegible("timeout").permite("/x", AGENTE).permitido)


class ComportamientoGeneral(unittest.TestCase):
    """[ES] Lo que debe seguir funcionando."""

    def test_sin_reglas_aplicables_se_permite(self):
        robots = leer("User-agent: otro\nDisallow: /x/\n")
        self.assertTrue(robots.permite("/x/a", AGENTE).permitido)

    def test_los_comentarios_se_ignoran(self):
        robots = leer("# comentario\nUser-agent: *  # otro\nDisallow: /x/ # y otro\n")
        self.assertFalse(robots.permite("/x/a", AGENTE).permitido)

    def test_la_query_participa_de_la_comparacion(self):
        robots = leer("User-agent: *\nDisallow: /buscar?*\n")
        self.assertFalse(robots.permite("/buscar?q=algo", AGENTE).permitido)
        self.assertTrue(robots.permite("/buscar", AGENTE).permitido)

    def test_la_decision_explica_por_que(self):
        # [ES] Una negativa sin motivo es indistinguible de una falla.
        d = leer("User-agent: *\nAllow: /\nDisallow: /files/").permite("/files/x", AGENTE)
        self.assertEqual(d.regla, "/files/")
        self.assertGreater(d.octetos_disallow, d.octetos_allow)


if __name__ == "__main__":
    unittest.main()
