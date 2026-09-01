"""FASE 3 - Controlled acquisition of corporate documents into incoming/candidates.

WHAT IT IS. A crawler that discovers PDF links on the investor-relations pages of
Argentine energy issuers, records everything needed to audit each download, and
saves the files to a staging zone that is NOT part of the corpus.

ROBOTS.TXT IS ENFORCED, NOT CONSULTED. Every candidate URL is checked against the
site's own rules before any request, and a disallowed URL is never fetched - it
is reported as `bloqueado_por_robots` so a human can decide whether to obtain it
another way. This is not a formality: `edenor.com` disallows `/files/`, and every
Edenor investor PDF lives under `/files/investors/`. An acquisition script that
ignored that would quietly build a corpus on documents the publisher asked
automated clients not to take.

URLS ARE DISCOVERED, NEVER INVENTED. The seed pages are probed and the ones that
do not answer are reported as unreachable. No URL in the output was written from
memory; every one of them came back from a real request whose status code is
recorded.

WHAT IT DOES NOT DO. It does not ingest, does not touch PostgreSQL, does not
write to `data/raw`, and does not assign a domain to anything. Every record
leaves as `pendiente_revision`, and the document type it proposes is a proposal.

[ES] FASE 3 - Adquisicion controlada de documentos empresariales hacia
incoming/candidates.

QUE ES. Un rastreador que descubre enlaces a PDF en las paginas de relaciones con
inversores de emisoras energeticas argentinas, registra todo lo necesario para
auditar cada descarga, y guarda los archivos en una zona de preparacion que NO es
parte del corpus.

ROBOTS.TXT SE CUMPLE, NO SE CONSULTA. Cada URL candidata se contrasta con las
reglas del propio sitio antes de cualquier pedido, y una URL no permitida no se
descarga nunca: se reporta como `bloqueado_por_robots` para que un humano decida
si conseguirla por otra via. Esto no es una formalidad: `edenor.com` prohibe
`/files/`, y todos los PDF para inversores de Edenor viven bajo
`/files/investors/`. Un script de adquisicion que ignorara eso armaria en
silencio un corpus sobre documentos que el editor pidio que los clientes
automaticos no tomaran.

LAS URL SE DESCUBREN, NUNCA SE INVENTAN. Las paginas semilla se sondean y las que
no responden se reportan como inalcanzables. Ninguna URL de la salida se escribio
de memoria; todas volvieron de un pedido real cuyo codigo de estado queda
registrado.

QUE NO HACE. No ingiere, no toca PostgreSQL, no escribe en `data/raw`, y no le
asigna dominio a nada. Todo registro sale como `pendiente_revision`, y el tipo
documental que propone es una propuesta.
"""

import argparse
import collections
import hashlib
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path

import requests

from multirag.acquisition import robots as robots_rfc
from multirag.paths import DATA_DIR, PROJECT_ROOT


RECETA_VERSION = "adquisicion-fase3-v1"

DESTINO = DATA_DIR / "incoming" / "candidates"
INVENTARIO = DATA_DIR / "catalog" / "candidates" / "inventario_fase1.jsonl"

AGENTE = "multi-rag-energy-ar/0.1 (investigacion academica; corpus de tesis)"
PAUSA_SEGUNDOS = 1.5
TIEMPO_LIMITE = 45
TAMANO_MAXIMO = 60 * 1024 * 1024

# Issuers and the paths where an investor-relations section usually lives. The
# paths are CANDIDATES to probe: whichever answers 200 is used, the rest are
# reported. Nothing here is asserted to exist.
# [ES] Emisoras y las rutas donde suele vivir una seccion de relaciones con
# inversores. Las rutas son CANDIDATAS a sondear: se usa la que responda 200 y el
# resto se reporta. Aca no se afirma que ninguna exista.
EMISORAS = [
    ("TGS", "Transportadora de Gas del Sur", "transporte_gas", "www.tgs.com.ar",
     ["/inversores", "/es/inversores", "/investors"]),
    ("TRANSENER", "Transener", "transporte_electrico", "www.transener.com.ar",
     ["/inversores", "/informacion-financiera", "/es/inversores"]),
    ("EDENOR", "Edenor", "distribucion_electrica", "www.edenor.com",
     ["/inversores", "/es/inversores", "/investors"]),
    ("PAMPA", "Pampa Energia", "generacion_integrada", "www.pampaenergia.com",
     ["/inversores", "/es/inversores", "/investors", "/relacion-con-inversores"]),
    ("CEPU", "Central Puerto", "generacion", "www.centralpuerto.com",
     ["/inversores", "/es/inversores", "/investors"]),
    ("YPF", "YPF", "integrada", "www.ypf.com",
     ["/inversores", "/inversoresaccionistas", "/investors"]),
    ("VIST", "Vista Energy", "upstream", "www.vistaenergy.com",
     ["/investors", "/inversores", "/en/investors"]),
    ("METROGAS", "Metrogas", "distribucion_gas", "www.metrogas.com.ar",
     ["/inversores", "/institucional/inversores"]),
    ("CAMUZZI", "Camuzzi Gas Pampeana", "distribucion_gas", "www.camuzzigas.com.ar",
     ["/inversores", "/institucional"]),
    ("GENNEIA", "Genneia", "renovables", "www.genneia.com.ar",
     ["/inversores", "/es/inversores", "/investors"]),
    ("CAPEX", "Capex", "generacion", "www.capex.com.ar",
     ["/inversores", "/es/inversores"]),
    ("CGC", "Compania General de Combustibles", "upstream", "www.cgc.com.ar",
     ["/inversores", "/es/inversores"]),
    ("ALBANESI", "Albanesi", "generacion", "www.albanesi.com.ar",
     ["/inversores", "/es/inversores"]),
    ("MSU", "MSU Energy", "generacion", "www.msuenergy.com",
     ["/investors", "/inversores"]),
]

# Document type proposed from the link text and file name. A PROPOSAL: the human
# review decides. Order matters - the first match wins, so the specific patterns
# come before the general ones.
# [ES] Tipo documental propuesto a partir del texto del enlace y del nombre de
# archivo. Una PROPUESTA: decide la revision humana. El orden importa: gana la
# primera coincidencia, asi que los patrones especificos van antes que los
# generales.
TIPOS = [
    ("estado_financiero", r"estados?[\s_-]*(financieros?|contables?)|financial[\s_-]*statements?|eeff|balance"),
    ("reporte_resultados", r"earnings|resultados|reporte[\s_-]*de[\s_-]*resultados|results[\s_-]*release"),
    ("presentacion_inversores", r"investor[\s_-]*present|presentaci[oó]n|conference[\s_-]*call|corporate[\s_-]*present"),
    ("memoria_anual", r"memoria|annual[\s_-]*report|reporte[\s_-]*anual|20-f|integrated[\s_-]*report"),
    ("prospecto", r"prospect|suplemento[\s_-]*de[\s_-]*precio|offering|pricing[\s_-]*supplement"),
    ("obligacion_negociable", r"obligaci[oó]n(es)?[\s_-]*negociable|\bon\b[\s_-]*clase|notes"),
    ("informe_calificacion", r"calificaci[oó]n|rating"),
    ("reporte_sostenibilidad", r"sustentabilidad|sostenibilidad|asg|esg|sustainab"),
]

PERIODO = re.compile(
    r"(?:^|[^0-9])((?:1|2|3|4)[QT]\s?(?:20)?\d{2}|(?:20)?\d{2}\s?[QT](?:1|2|3|4)|20\d{2})"
)


def _plano(t: str) -> str:
    d = unicodedata.normalize("NFKD", t or "")
    s = "".join(c for c in d if not unicodedata.combining(c))
    return " ".join(s.lower().split())


def sesion() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": AGENTE})
    return s


class Robots:
    """Thin cache over `multirag.acquisition.robots`, one fetch per host.

    The evaluation itself lives in the module, where it is tested. This only
    remembers what was already fetched.

    [ES] Cache delgado sobre `multirag.acquisition.robots`, un pedido por host.

    La evaluacion vive en el modulo, donde esta probada. Esto solo recuerda lo
    que ya se trajo.
    """

    def __init__(self, ses):
        self._ses = ses
        self._cache = {}

    def permite(self, url: str) -> tuple:
        partes = urllib.parse.urlsplit(url)
        host = f"{partes.scheme}://{partes.netloc}"
        if host not in self._cache:
            self._cache[host] = robots_rfc.obtener(host, self._ses, AGENTE, TIEMPO_LIMITE)
        decision = self._cache[host].permite(url, AGENTE)
        detalle = decision.motivo
        if decision.regla:
            detalle += f" ({decision.regla})"
        return decision.permitido, detalle


def descubrir_semillas(ses, robots) -> list:
    """Probe the candidate IR paths of each issuer. Report what answers.

    [ES] Sondea las rutas candidatas de RI de cada emisora. Reporta lo que
    responde.
    """
    semillas = []
    for sigla, nombre, segmento, host, rutas in EMISORAS:
        encontrada = None
        intentos = []
        for ruta in rutas:
            url = f"https://{host}{ruta}"
            permitido, motivo = robots.permite(url)
            if not permitido:
                intentos.append({"url": url, "estado": "bloqueado_por_robots",
                                 "detalle": motivo})
                continue
            try:
                r = ses.get(url, timeout=TIEMPO_LIMITE, allow_redirects=True)
                # A site can answer 200 with an error page. YPF redirects to
                # `/error.html?errorCode=404`, and taking that as a valid seed
                # would put a "not found" page into the corpus provenance.
                # [ES] Un sitio puede responder 200 con una pagina de error. YPF
                # redirige a `/error.html?errorCode=404`, y tomar eso como
                # semilla valida metería una pagina de "no encontrado" en la
                # procedencia del corpus.
                es_error = bool(
                    re.search(r"/error|errorcode=|404", r.url, re.I)
                    or re.search(r"<title>[^<]*(404|no disponible|not found)", r.text[:4000], re.I)
                )
                intentos.append({
                    "url": url, "estado": str(r.status_code),
                    "url_final": r.url,
                    "detalle": "pagina de error disfrazada de 200" if es_error else None,
                })
                if r.status_code == 200 and len(r.text) > 500 and not es_error:
                    encontrada = {"url": r.url, "html": r.text}
                    break
            except Exception as e:
                intentos.append({"url": url, "estado": f"error: {type(e).__name__}"})
            time.sleep(PAUSA_SEGUNDOS)
        semillas.append(
            {
                "sigla": sigla, "emisor_nombre": nombre, "segmento": segmento,
                "host": host, "intentos": intentos,
                "semilla": encontrada["url"] if encontrada else None,
                "html": encontrada["html"] if encontrada else None,
            }
        )
        print(f"  {sigla:10} {'OK ' + encontrada['url'] if encontrada else 'sin pagina de RI alcanzable'}",
              flush=True)
    return semillas


def enlaces_pdf(html: str, base: str) -> list:
    """Every PDF link on the page, with the text of its anchor.

    The anchor text is what a human reads to know what the file is; the file
    name alone often says `1Q26.pdf` and nothing else.

    [ES] Todo enlace a PDF de la pagina, con el texto de su ancla.

    El texto del ancla es lo que un humano lee para saber que es el archivo; el
    nombre solo suele decir `1Q26.pdf` y nada mas.
    """
    from bs4 import BeautifulSoup

    sopa = BeautifulSoup(html, "lxml")
    vistos, salida = set(), []
    for a in sopa.find_all("a", href=True):
        href = a["href"].strip()
        if ".pdf" not in href.lower():
            continue
        absoluta = urllib.parse.urljoin(base, href)
        absoluta = urllib.parse.urldefrag(absoluta).url
        if absoluta in vistos:
            continue
        vistos.add(absoluta)
        salida.append({"url": absoluta, "texto_enlace": " ".join(a.get_text().split())[:200]})
    return salida


def proponer_tipo(texto: str) -> str:
    plano = _plano(texto)
    for tipo, patron in TIPOS:
        if re.search(patron, plano):
            return tipo
    return "no_determinado"


def proponer_periodo(texto: str):
    m = PERIODO.search(texto or "")
    return m.group(1).strip() if m else None


def sha256_de_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def hashes_existentes() -> set:
    if not INVENTARIO.exists():
        return set()
    return {
        json.loads(l)["sha256"] for l in INVENTARIO.open(encoding="utf-8")
    }


def nombre_seguro(url: str, sigla: str) -> str:
    base = urllib.parse.unquote(Path(urllib.parse.urlsplit(url).path).name)
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base)[:120] or "documento.pdf"
    if not base.lower().endswith(".pdf"):
        base += ".pdf"
    return f"{sigla}__{base}"


def ordenar_por_diversidad(candidatos) -> list:
    """Interleave document types within each issuer before repeating any.

    A cap of eight taken in page order would take eight quarterly statements of
    the same series from the issuer that lists them first. Rotating over the
    proposed types first spends the cap on variety, which is what the corpus
    needs: `evitar que un unico emisor aporte mas de cinco documentos muy
    semejantes`.

    [ES] Intercala tipos documentales dentro de cada emisora antes de repetir
    ninguno.

    Un tope de ocho tomado en orden de pagina se llevaria ocho estados trimestrales
    de la misma serie de la emisora que los liste primero. Rotar primero sobre los
    tipos propuestos gasta el cupo en variedad, que es lo que el corpus necesita.
    """
    por_emisor = collections.defaultdict(lambda: collections.defaultdict(list))
    for c in candidatos:
        por_emisor[c["sigla"]][c["tipo_documental_propuesto"]].append(c)

    salida = []
    for sigla in sorted(por_emisor):
        tipos = por_emisor[sigla]
        # `no_determinado` last: a link whose type could not be proposed is the
        # least informative use of the cap.
        # [ES] `no_determinado` al final: un enlace cuyo tipo no se pudo proponer
        # es el uso menos informativo del cupo.
        orden = sorted(tipos, key=lambda t: (t == "no_determinado", t))
        rondas = max(len(v) for v in tipos.values())
        for i in range(rondas):
            for tipo in orden:
                if i < len(tipos[tipo]):
                    salida.append(tipos[tipo][i])
    return salida


def descargar(ses, robots, candidatos, limite_por_emisor, ya_conocidos) -> list:
    """Download what robots allows, register everything, decide nothing.

    [ES] Descarga lo que robots permite, registra todo, no decide nada.
    """
    DESTINO.mkdir(parents=True, exist_ok=True)
    registros = []
    por_emisor = collections.Counter()
    vistos_hash = set(ya_conocidos)

    for c in candidatos:
        sigla = c["sigla"]
        registro = dict(c)
        registro["fecha_acceso"] = datetime.now(timezone.utc).isoformat()
        registro["estado"] = "pendiente_revision"
        registro["fase"] = "fase3_empresarial"

        if por_emisor[sigla] >= limite_por_emisor:
            registro["resultado"] = "omitido_por_tope_de_emisor"
            registros.append(registro)
            continue

        permitido, motivo = robots.permite(c["url"])
        if not permitido:
            registro["resultado"] = "bloqueado_por_robots"
            registro["detalle"] = motivo
            registros.append(registro)
            continue

        try:
            r = ses.get(c["url"], timeout=TIEMPO_LIMITE, stream=True)
            registro["http_status"] = r.status_code
            if r.status_code != 200:
                registro["resultado"] = f"http_{r.status_code}"
                registros.append(registro)
                time.sleep(PAUSA_SEGUNDOS)
                continue
            contenido = b""
            for trozo in r.iter_content(1 << 16):
                contenido += trozo
                if len(contenido) > TAMANO_MAXIMO:
                    break
            if len(contenido) > TAMANO_MAXIMO:
                registro["resultado"] = "excede_tamano_maximo"
                registros.append(registro)
                time.sleep(PAUSA_SEGUNDOS)
                continue
            if not contenido.startswith(b"%PDF"):
                registro["resultado"] = "no_es_pdf"
                registros.append(registro)
                time.sleep(PAUSA_SEGUNDOS)
                continue
        except Exception as e:
            registro["resultado"] = f"error: {type(e).__name__}"
            registros.append(registro)
            continue

        huella = sha256_de_bytes(contenido)
        registro["sha256"] = huella
        registro["bytes"] = len(contenido)
        registro["formato"] = "pdf"
        registro["content_type"] = r.headers.get("Content-Type")

        if huella in vistos_hash:
            registro["resultado"] = "duplicado_de_material_ya_disponible"
            registros.append(registro)
            time.sleep(PAUSA_SEGUNDOS)
            continue

        destino = DESTINO / nombre_seguro(c["url"], sigla)
        destino.write_bytes(contenido)
        vistos_hash.add(huella)
        por_emisor[sigla] += 1
        registro["resultado"] = "descargado"
        registro["ruta"] = str(destino.relative_to(PROJECT_ROOT)).replace("\\", "/")
        registros.append(registro)
        print(f"    + {sigla:10} {destino.name[:70]}  {len(contenido)/1e6:.1f} MB", flush=True)
        time.sleep(PAUSA_SEGUNDOS)

    return registros


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tope-por-emisor", type=int, default=6)
    parser.add_argument("--solo-descubrir", action="store_true")
    parser.add_argument(
        "--salida", type=Path,
        default=DATA_DIR / "catalog" / "candidates" / "adquisicion_fase3.json",
    )
    args = parser.parse_args()

    ses = sesion()
    robots = Robots(ses)

    print("descubriendo paginas de relaciones con inversores ...", flush=True)
    semillas = descubrir_semillas(ses, robots)

    candidatos = []
    for s in semillas:
        if not s["html"]:
            continue
        for enlace in enlaces_pdf(s["html"], s["semilla"]):
            contexto = f"{enlace['texto_enlace']} {enlace['url']}"
            candidatos.append(
                {
                    "sigla": s["sigla"],
                    "emisor_nombre": s["emisor_nombre"],
                    "segmento": s["segmento"],
                    "pagina_origen": s["semilla"],
                    "url": enlace["url"],
                    "titulo_propuesto": enlace["texto_enlace"] or Path(
                        urllib.parse.urlsplit(enlace["url"]).path
                    ).name,
                    "tipo_documental_propuesto": proponer_tipo(contexto),
                    "periodo_propuesto": proponer_periodo(contexto),
                    "criterio_inclusion": (
                        "enlace publico en la pagina de relaciones con inversores "
                        "de la propia emisora"
                    ),
                }
            )

    print(f"\ncandidatos descubiertos: {len(candidatos)}", flush=True)
    for sigla, n in collections.Counter(c["sigla"] for c in candidatos).most_common():
        print(f"  {sigla:10} {n}")

    registros = []
    if not args.solo_descubrir:
        print("\ndescargando lo que robots permite ...", flush=True)
        registros = descargar(
            ses, robots, ordenar_por_diversidad(candidatos),
            args.tope_por_emisor, hashes_existentes(),
        )

    salida = {
        "receta": RECETA_VERSION,
        "fecha": datetime.now(timezone.utc).isoformat(),
        "agente": AGENTE,
        "destino": str(DESTINO.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "tope_por_emisor": args.tope_por_emisor,
        "semillas": [
            {k: v for k, v in s.items() if k != "html"} for s in semillas
        ],
        "candidatos": len(candidatos),
        "registros": registros,
        "salvedades": [
            "robots.txt se CUMPLE: una URL prohibida no se descarga y se reporta.",
            "Las URL fueron DESCUBIERTAS con pedidos reales; ninguna se escribio de "
            "memoria.",
            "Nada se ingirio, nada se movio a data/raw y no se toco PostgreSQL.",
            "El tipo documental y el periodo son PROPUESTAS derivadas del texto del "
            "enlace; los decide la revision humana.",
            "Ningun documento tiene dominio asignado. Todo sale pendiente_revision.",
        ],
    }
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(
        json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if registros:
        print()
        for resultado, n in collections.Counter(
            r["resultado"] for r in registros
        ).most_common():
            print(f"  {resultado:38} {n}")
    print(f"\nregistro  {args.salida}")


if __name__ == "__main__":
    main()
