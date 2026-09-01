"""robots.txt evaluation per RFC 9309, because the standard library is not.

WHY THIS EXISTS. `urllib.robotparser` implements the 1994 draft, where the FIRST
matching rule wins. RFC 9309 - the standard robots.txt files are actually
written against - says the MOST SPECIFIC match wins. `edenor.com` publishes:

    User-Agent: *
    Allow: /
    Disallow: /files/

Under first-match, `Allow: /` matches first and everything is permitted, which
is what the standard library answers and it is wrong. Trusting it downloaded
twenty documents whose publishers had asked automated clients not to take them.
They were deleted; this module is why it cannot happen again.

FOUR THINGS A NAIVE IMPLEMENTATION GETS WRONG, and this one does not:

  PRODUCT TOKEN, MATCHED EXACTLY. The group name is compared against the product
  token of the user-agent - the part before `/` or the first space - case
  -insensitively and in full. Prefix matching would let a group for `multi`
  capture `multi-rag-energy-ar`, and would fail to capture it from a group named
  `multi-rag-energy-ar-2`. Both are wrong in opposite directions.

  CANONICAL PERCENT-ENCODING. The RFC requires reserved and non-ASCII octets to
  be percent-encoded before comparison. Decoding everything is the opposite
  operation: it turns `%3F` into a literal `?` and a path segment into a query
  separator. Only the unreserved set is decoded here.

  SPECIFICITY IN MATCHED OCTETS, not pattern length. `/*.htm` is six characters
  and constrains all nine octets of `/page.htm`, because it pins both ends.
  Pattern length would call `/page` more specific and get the verdict backwards.

  AN EMPTY GROUP IS NOT A MISSING GROUP. `User-agent: quxbot` with no rules means
  quxbot has a group that forbids nothing. Falling back to `*` there would apply
  restrictions the file deliberately did not give it.

CONSERVATIVE POLICY WHERE THE RFC LEAVES ROOM. A missing robots.txt (404/410)
means no rules, so everything is allowed - that is the RFC, and refusing there
would block every site that never published one. But a server error, a timeout
or an unparseable body leaves the rules UNKNOWN, and this module refuses. When
the action is downloading someone else's documents, "I could not read your
rules" is not permission.

[ES] Evaluacion de robots.txt segun RFC 9309, porque la biblioteca estandar no
lo hace.

POR QUE EXISTE. `urllib.robotparser` implementa el borrador de 1994, donde gana
la PRIMERA regla que coincide. La RFC 9309 -contra la que realmente se escriben
los robots.txt- dice que gana la coincidencia MAS ESPECIFICA. `edenor.com`
publica:

    User-Agent: *
    Allow: /
    Disallow: /files/

Con primera-coincidencia, `Allow: /` matchea primero y todo queda permitido, que
es lo que responde la biblioteca estandar y esta mal. Confiar en ella descargo
veinte documentos que sus editores habian pedido que los clientes automaticos no
tomaran. Se borraron; este modulo es la razon por la que no puede volver a pasar.

CUATRO COSAS QUE UNA IMPLEMENTACION INGENUA HACE MAL, y esta no:

  TOKEN DE PRODUCTO, COMPARADO EXACTO. El nombre del grupo se compara contra el
  token de producto del user-agent -la parte antes de `/` o del primer espacio-
  sin distinguir mayusculas y completo. Comparar por prefijo dejaria que un grupo
  para `multi` capturara a `multi-rag-energy-ar`, y no lo capturaria desde un
  grupo llamado `multi-rag-energy-ar-2`. Las dos cosas estan mal, en direcciones
  opuestas.

  PERCENT-ENCODING CANONICO. La RFC exige que los octetos reservados y no ASCII
  esten percent-encoded antes de comparar. Decodificar todo es la operacion
  inversa: convierte `%3F` en un `?` literal y un segmento de ruta en un
  separador de query. Aca solo se decodifica el conjunto no reservado.

  ESPECIFICIDAD EN OCTETOS COINCIDENTES, no en largo del patron. `/*.htm` mide
  seis caracteres y restringe los nueve octetos de `/page.htm`, porque fija los
  dos extremos. El largo del patron llamaria mas especifico a `/page` y daria el
  veredicto al reves.

  UN GRUPO VACIO NO ES UN GRUPO AUSENTE. `User-agent: quxbot` sin reglas
  significa que quxbot tiene un grupo que no le prohibe nada. Caer al `*` ahi le
  aplicaria restricciones que el archivo deliberadamente no le dio.

POLITICA CONSERVADORA DONDE LA RFC DEJA MARGEN. Un robots.txt ausente (404/410)
significa que no hay reglas, asi que todo esta permitido: eso dice la RFC, y
negarse ahi bloquearia todo sitio que nunca publico uno. Pero un error de
servidor, un timeout o un cuerpo inparseable dejan las reglas DESCONOCIDAS, y
este modulo se niega. Cuando la accion es descargar documentos ajenos, "no pude
leer tus reglas" no es un permiso.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlsplit


PERMITIR = "allow"
PROHIBIR = "disallow"

# Why a decision came out the way it did, kept as data so the acquisition log
# can record the reason next to every URL it did not fetch.
# [ES] Por que una decision salio como salio, guardado como dato para que el
# registro de adquisicion anote el motivo al lado de cada URL que no bajo.
SIN_REGLAS = "sin_reglas_aplicables"
GRUPO_VACIO = "grupo_propio_sin_reglas"
PERMITIDO_POR_REGLA = "allow_mas_especifico"
PROHIBIDO_POR_REGLA = "disallow_mas_especifico"
EMPATE_A_FAVOR_DE_ALLOW = "empate_resuelto_a_favor_de_allow"
ROBOTS_AUSENTE = "robots_ausente_404_todo_permitido"
ROBOTS_ILEGIBLE = "robots_ilegible_o_error_se_asume_prohibido"

# RFC 3986 unreserved set: these and only these may appear decoded in the
# canonical form. Everything else stays percent-encoded on both sides.
# [ES] Conjunto no reservado de RFC 3986: estos y solo estos pueden aparecer
# decodificados en la forma canonica. Todo lo demas queda percent-encoded de los
# dos lados.
NO_RESERVADOS = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
)

# Structural and reserved characters that stay literal rather than being
# re-encoded: they already are in their canonical form.
# [ES] Caracteres estructurales y reservados que quedan literales en lugar de
# recodificarse: ya estan en su forma canonica.
LITERALES = frozenset("/*$?&=:@!+,;'()[]#%")

ESCAPE = re.compile(r"%([0-9A-Fa-f]{2})")


def token_de_producto(agente: str) -> str:
    """The product token of a user-agent string, lowercased.

    `multi-rag-energy-ar/0.1 (research; corpus)` becomes `multi-rag-energy-ar`.

    [ES] El token de producto de un user-agent, en minusculas.
    """
    return re.split(r"[/\s]", (agente or "").strip(), maxsplit=1)[0].lower()


def normalizar_ruta(ruta: str) -> str:
    """Canonical percent-encoding, so both sides of the comparison agree.

    Only the unreserved set is decoded. `%6C` becomes `l` because `l` is
    unreserved, so `/fi%6Ces/` and `/files/` compare equal. `%2F` and `%3F` stay
    encoded because `/` and `?` are reserved and decoding them would change what
    the path means. Non-ASCII is encoded, uppercase hex throughout.

    [ES] Percent-encoding canonico, para que los dos lados de la comparacion
    coincidan.

    Solo se decodifica el conjunto no reservado. `%6C` pasa a `l` porque `l` no
    es reservado, asi que `/fi%6Ces/` y `/files/` comparan iguales. `%2F` y `%3F`
    quedan codificados porque `/` y `?` son reservados y decodificarlos cambiaria
    lo que la ruta significa. Lo no ASCII se codifica, con hexadecimal en
    mayuscula siempre.
    """
    if not ruta:
        return "/"

    salida, i, largo = [], 0, len(ruta)
    while i < largo:
        c = ruta[i]
        m = ESCAPE.match(ruta, i)
        if m:
            caracter = chr(int(m.group(1), 16))
            salida.append(caracter if caracter in NO_RESERVADOS
                          else "%" + m.group(1).upper())
            i += 3
            continue
        if c in NO_RESERVADOS or c in LITERALES:
            salida.append(c)
        else:
            salida.extend(f"%{b:02X}" for b in c.encode("utf-8"))
        i += 1
    return "".join(salida)


def _a_expresion(patron: str) -> Optional[re.Pattern]:
    """Compile an RFC 9309 path pattern into a regular expression.

    The wildcard is NON-greedy on purpose. A greedy `.*` would make every rule
    ending in `*` match the whole path, so `/fish*` and `/f*` would score
    identically and specificity would stop discriminating. Non-greedy makes
    `/fish*` constrain five octets, which is what it actually constrains.

    [ES] Compila un patron de ruta de la RFC 9309 a expresion regular.

    El comodin es NO codicioso a proposito. Un `.*` codicioso haria que toda
    regla terminada en `*` matcheara la ruta entera, asi que `/fish*` y `/f*`
    puntuarian igual y la especificidad dejaria de discriminar. No codicioso hace
    que `/fish*` restrinja cinco octetos, que es lo que restringe de verdad.
    """
    if patron == "":
        return None
    ancla = patron.endswith("$")
    cuerpo = patron[:-1] if ancla else patron
    partes = [re.escape(t) for t in cuerpo.split("*")]
    return re.compile("^" + ".*?".join(partes) + ("$" if ancla else ""))


@dataclass
class Regla:
    tipo: str
    patron: str
    expresion: Optional[re.Pattern] = None

    def __post_init__(self):
        self.expresion = _a_expresion(
            normalizar_ruta(self.patron) if self.patron else ""
        )

    def coincide(self, ruta: str) -> int:
        """Octets of the PATH this rule constrains, or -1 if it does not match.

        RFC 9309 says the most specific match is "the match that has the most
        octets", so the span of the match is measured, not the length of the
        pattern.

        [ES] Octetos de la RUTA que esta regla restringe, o -1 si no coincide.

        La RFC 9309 dice que la coincidencia mas especifica es "la que tiene mas
        octetos", asi que se mide el tramo coincidente, no el largo del patron.
        """
        if self.expresion is None:
            return -1
        m = self.expresion.match(ruta)
        return m.end() if m else -1


@dataclass
class Decision:
    permitido: bool
    motivo: str
    regla: Optional[str] = None
    octetos_allow: int = -1
    octetos_disallow: int = -1


@dataclass
class Robots:
    """Parsed rules of one host, ready to answer about any of its paths.

    [ES] Reglas parseadas de un host, listas para responder sobre cualquiera de
    sus rutas.
    """

    grupos: dict = field(default_factory=dict)
    legible: bool = True
    motivo_ilegible: Optional[str] = None
    permitir_todo: bool = False

    @classmethod
    def ilegible(cls, motivo: str) -> "Robots":
        return cls(legible=False, motivo_ilegible=motivo)

    @classmethod
    def ausente(cls) -> "Robots":
        return cls(permitir_todo=True)

    @classmethod
    def desde_texto(cls, texto: str) -> "Robots":
        """Parse groups, honouring consecutive agents and merging repeats.

        A group is one or more consecutive `User-agent` lines followed by rules;
        all those agents share them. If the same agent heads another group later
        in the file, the rules MERGE rather than replace: a crawler that kept
        only the last group would silently ignore the first one's restrictions.

        [ES] Parsea grupos, respetando agentes consecutivos y fusionando
        repetidos.

        Un grupo es una o mas lineas `User-agent` consecutivas seguidas de
        reglas; todos esos agentes las comparten. Si el mismo agente encabeza
        otro grupo mas adelante, las reglas se FUSIONAN en lugar de reemplazarse:
        un rastreador que se quedara solo con el ultimo grupo ignoraria en
        silencio las restricciones del primero.
        """
        grupos: dict = {}
        agentes: list = []
        esperando = True

        for linea_cruda in texto.splitlines():
            linea = linea_cruda.split("#", 1)[0].strip()
            if not linea or ":" not in linea:
                continue
            campo, _, valor = linea.partition(":")
            campo, valor = campo.strip().lower(), valor.strip()

            if campo == "user-agent":
                if not esperando:
                    agentes = []
                    esperando = True
                agentes.append(valor.lower())
                grupos.setdefault(valor.lower(), [])
            elif campo in (PERMITIR, PROHIBIR):
                if not agentes:
                    continue  # rules before any agent belong to nobody
                esperando = False
                for agente in agentes:
                    grupos.setdefault(agente, []).append(Regla(campo, valor))

        return cls(grupos=grupos)

    def _reglas_para(self, agente: str) -> Optional[list]:
        """The group whose product token equals ours, or the wildcard, or None.

        [ES] El grupo cuyo token de producto es igual al nuestro, o el comodin, o
        None.
        """
        token = token_de_producto(agente)
        if token in self.grupos:
            return self.grupos[token]
        return self.grupos.get("*")

    def permite(self, url_o_ruta: str, agente: str) -> Decision:
        """Decide, with the reason and the two competing match lengths.

        [ES] Decide, con el motivo y los dos largos de coincidencia que
        compitieron.
        """
        if self.permitir_todo:
            return Decision(True, ROBOTS_AUSENTE)
        if not self.legible:
            return Decision(False, ROBOTS_ILEGIBLE, regla=self.motivo_ilegible)

        partes = urlsplit(url_o_ruta)
        ruta = partes.path or "/"
        if partes.query:
            ruta += "?" + partes.query
        ruta = normalizar_ruta(ruta)

        reglas = self._reglas_para(agente)
        if reglas is None:
            return Decision(True, SIN_REGLAS)
        if not reglas:
            return Decision(True, GRUPO_VACIO)

        mejor_allow, mejor_disallow = -1, -1
        patron_allow, patron_disallow = None, None
        for regla in reglas:
            # An empty `Disallow:` forbids nothing: it is the RFC's way of
            # writing "allow everything" and must not be treated as a rule.
            # [ES] Un `Disallow:` vacio no prohibe nada: es la forma que tiene la
            # RFC de escribir "permitir todo" y no debe tratarse como regla.
            if regla.tipo == PROHIBIR and regla.patron == "":
                continue
            octetos = regla.coincide(ruta)
            if octetos < 0:
                continue
            if regla.tipo == PERMITIR and octetos > mejor_allow:
                mejor_allow, patron_allow = octetos, regla.patron
            elif regla.tipo == PROHIBIR and octetos > mejor_disallow:
                mejor_disallow, patron_disallow = octetos, regla.patron

        if mejor_disallow < 0:
            return Decision(True, SIN_REGLAS, octetos_allow=mejor_allow)
        if mejor_allow > mejor_disallow:
            return Decision(True, PERMITIDO_POR_REGLA, patron_allow,
                            mejor_allow, mejor_disallow)
        if mejor_allow == mejor_disallow:
            # The RFC resolves a tie toward the least restrictive rule.
            # [ES] La RFC resuelve el empate hacia la regla menos restrictiva.
            return Decision(True, EMPATE_A_FAVOR_DE_ALLOW, patron_allow,
                            mejor_allow, mejor_disallow)
        return Decision(False, PROHIBIDO_POR_REGLA, patron_disallow,
                        mejor_allow, mejor_disallow)


def obtener(host: str, sesion, agente: str, tiempo_limite: int = 45) -> Robots:
    """Fetch and parse a host's robots.txt, applying the conservative policy.

    [ES] Trae y parsea el robots.txt de un host, aplicando la politica
    conservadora.
    """
    try:
        respuesta = sesion.get(
            f"{host}/robots.txt", headers={"User-Agent": agente}, timeout=tiempo_limite
        )
    except Exception as error:
        return Robots.ilegible(f"error de red: {type(error).__name__}")

    if respuesta.status_code in (404, 410):
        return Robots.ausente()
    if respuesta.status_code != 200:
        return Robots.ilegible(f"http {respuesta.status_code}")
    try:
        return Robots.desde_texto(respuesta.text)
    except Exception as error:
        return Robots.ilegible(f"cuerpo inparseable: {type(error).__name__}")
