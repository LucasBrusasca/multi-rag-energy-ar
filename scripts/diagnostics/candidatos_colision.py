"""Find candidate collision pairs for writing Golden questions.

The hardest part of writing a `colision` item is not the question: it is finding
a PLAUSIBLE DISTRACTOR — a fragment that shares terminology with the evidence
but belongs to a domain that is not needed to answer. `PROTOCOLO_GOLDEN.md`
requires exactly that, and requires the distractor's domain to be established by
human review, never by the automatic `silo`, `silo_scores` or the router output.

This script proposes pairs and nothing else:

- the ANCHOR comes from a document whose human label names a single silo, so its
  domain is unambiguous;
- the DISTRACTOR is a fragment that the embedding places very close to the
  anchor, taken from a document whose human domains do NOT intersect the
  anchor's.

Both domains come from the curated catalog, that is, from human judgement. The
proximity comes from the embedding, which is a search aid, not evidence.

WHAT IT DOES NOT DO: it does not write the question, does not decide the
stratum, and does not confirm that the pair is a real collision. That is human
reading, as the protocol demands. A close pair may simply be the same matter
said twice.

STRICTLY READ-ONLY over the database.

[ES] Encuentra pares candidatos de colisión para escribir preguntas del Golden.

Lo difícil de escribir un ítem `colision` no es la pregunta: es encontrar un
DISTRACTOR PLAUSIBLE — un fragmento que comparte terminología con la evidencia
pero pertenece a un dominio que no hace falta para responder.
`PROTOCOLO_GOLDEN.md` exige justamente eso, y exige que el dominio del distractor
se establezca por revisión humana, nunca por el `silo` automático, los
`silo_scores` ni la salida del router.

Este script propone pares y nada más:

- el ANCLA sale de un documento cuya etiqueta humana nombra un solo silo, así su
  dominio no es ambiguo;
- el DISTRACTOR es un fragmento que el embedding ubica muy cerca del ancla,
  tomado de un documento cuyos dominios humanos NO intersectan los del ancla.

Los dos dominios vienen del catálogo curado, es decir, de juicio humano. La
cercanía viene del embedding, que es una ayuda de búsqueda, no evidencia.

LO QUE NO HACE: no escribe la pregunta, no decide el estrato y no confirma que
el par sea una colisión real. Eso es lectura humana, como exige el protocolo. Un
par cercano puede ser simplemente la misma materia dicha dos veces.

ESTRICTAMENTE DE SOLO LECTURA sobre la base.
"""

import argparse
import csv
import random
import re
from pathlib import Path

from multirag.config import SILOS
from multirag.db import conectar
from multirag.paths import DATA_DIR, EXPERIMENTS_DIR


CATALOGO = DATA_DIR / "catalog" / "metadatos_curados.csv"

SALIDA_PREDETERMINADA = EXPERIMENTS_DIR / "candidatos_colision.md"

# Below this length a fragment rarely carries substantive matter on its own.
# [ES] Por debajo de este largo un fragmento rara vez tiene materia sustantiva
# propia.
LARGO_MINIMO = 400

# Administrative closing formulas: they have no substantive matter, so they make
# neither anchors nor informative distractors.
# [ES] Fórmulas administrativas de cierre: no tienen materia sustantiva, así que
# no sirven ni de ancla ni de distractor informativo.
PATRON_ADMINISTRATIVO = re.compile(
    r"arch[ií]vese|comun[ií]quese|publ[ií]quese|reg[ií]strese"
    r"|d[ée]se a la direcci[óo]n nacional del registro oficial",
    re.IGNORECASE,
)

SEMILLA = 11


def cargar_dominios_por_documento() -> dict:
    """document_id -> set of human silos, from the curated catalog.

    [ES] document_id -> conjunto de silos humanos, del catálogo curado.
    """
    dominios = {}

    with CATALOGO.open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            silos = {
                valor.strip()
                for valor in (
                    fila.get("dominios_documentales") or ""
                ).split("|")
                if valor.strip()
            } & set(SILOS)

            documento = (fila.get("document_id") or "").strip()

            if documento and silos:
                dominios[documento] = silos

    return dominios


def es_sustantivo(titulo: str, contenido: str) -> bool:
    """Rough filter for fragments with matter of their own.

    It is a heuristic to shorten the reading list, not a materiality judgement.

    [ES] Filtro grueso de fragmentos con materia propia.

    Es una heurística para acortar la lista de lectura, no un juicio de
    materialidad.
    """
    if not contenido or len(contenido) < LARGO_MINIMO:
        return False

    return not PATRON_ADMINISTRATIVO.search(contenido[:400])


def leer_chunks(cursor) -> list[dict]:
    """Read every chunk with its document. Read-only.

    [ES] Lee cada chunk con su documento. Solo lectura.
    """
    cursor.execute(
        """
        SELECT chunk_uid, document_id, fuente, titulo, contenido, hierarchy
        FROM chunks
        WHERE chunk_uid IS NOT NULL AND document_id IS NOT NULL
        ORDER BY chunk_uid
        """
    )

    return [
        {
            "chunk_uid": uid,
            "document_id": documento,
            "fuente": fuente,
            "titulo": titulo or "",
            "contenido": contenido or "",
            "hierarchy": hierarchy or [],
        }
        for uid, documento, fuente, titulo, contenido, hierarchy in cursor.fetchall()
    ]


def vecinos_de_otro_dominio(
    cursor,
    chunk_uid: str,
    documentos_ajenos: list[str],
    cantidad: int,
) -> list[tuple]:
    """Nearest fragments to the anchor among documents of other domains.

    The comparison uses the anchor's own embedding, read inside the query, so no
    vector travels through Python.

    [ES] Fragmentos más cercanos al ancla entre documentos de otros dominios.

    La comparación usa el embedding del propio ancla, leído dentro de la
    consulta, así que ningún vector viaja por Python.
    """
    cursor.execute(
        """
        SELECT c.chunk_uid, c.document_id, c.fuente, c.titulo, c.contenido,
               1 - (c.embedding <=> a.embedding) AS similitud
        FROM chunks AS c
        CROSS JOIN (
            SELECT embedding FROM chunks WHERE chunk_uid = %s
        ) AS a
        WHERE c.document_id = ANY(%s)
          AND c.chunk_uid <> %s
          AND length(c.contenido) >= %s
        ORDER BY c.embedding <=> a.embedding
        LIMIT %s
        """,
        (chunk_uid, documentos_ajenos, chunk_uid, LARGO_MINIMO, cantidad),
    )

    return cursor.fetchall()


def recortar(texto: str, largo: int = 320) -> str:
    """Collapse whitespace and cut, for a readable listing.

    [ES] Colapsa espacios y recorta, para un listado legible.
    """
    limpio = " ".join((texto or "").split())

    return limpio[:largo] + ("..." if len(limpio) > largo else "")


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.

    [ES] Construye la interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Propone pares ancla/distractor para escribir preguntas del "
            "estrato colision. Solo lectura."
        )
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=SALIDA_PREDETERMINADA,
        help="Archivo markdown a generar. No sobrescribe.",
    )
    parser.add_argument(
        "--anclas",
        type=int,
        default=40,
        help="Cuántas anclas proponer. Por defecto 40.",
    )
    parser.add_argument(
        "--distractores",
        type=int,
        default=3,
        help="Distractores por ancla. Por defecto 3.",
    )
    parser.add_argument(
        "--similitud-minima",
        type=float,
        default=0.60,
        help=(
            "Un distractor por debajo de esta similitud no es plausible. "
            "Por defecto 0.60."
        ),
    )
    return parser


def main() -> None:
    """Generate the candidate listing.

    [ES] Genera el listado de candidatos.
    """
    argumentos = construir_parser().parse_args()
    salida = Path(argumentos.salida).resolve()

    if salida.exists():
        raise SystemExit(
            f"La salida ya existe y no será sobrescrita: {salida}"
        )

    dominios = cargar_dominios_por_documento()

    # Only documents with a single human silo make unambiguous anchors.
    # [ES] Solo los documentos con un único silo humano dan anclas sin
    # ambigüedad.
    documentos_claros = {
        documento: next(iter(silos))
        for documento, silos in dominios.items()
        if len(silos) == 1
    }

    conexion = conectar()

    try:
        with conexion.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            chunks = leer_chunks(cursor)

            candidatos = [
                chunk
                for chunk in chunks
                if chunk["document_id"] in documentos_claros
                and es_sustantivo(chunk["titulo"], chunk["contenido"])
            ]

            print(f"chunks leídos: {len(chunks)}")
            print(
                f"documentos de dominio humano único: "
                f"{len(documentos_claros)}"
            )
            print(f"anclas posibles: {len(candidatos)}")

            if not candidatos:
                raise SystemExit(
                    "Ningún chunk cumple las condiciones de ancla."
                )

            # Balance the anchors across domains so one big document does not
            # take over the listing.
            # [ES] Se equilibran las anclas entre dominios para que un
            # documento grande no acapare el listado.
            sorteador = random.Random(SEMILLA)
            por_dominio: dict[str, list] = {}

            for chunk in candidatos:
                dominio = documentos_claros[chunk["document_id"]]
                por_dominio.setdefault(dominio, []).append(chunk)

            elegidas = []
            cupo = max(1, argumentos.anclas // max(1, len(por_dominio)))

            for dominio in sorted(por_dominio):
                grupo = por_dominio[dominio]
                elegidas += sorteador.sample(
                    grupo,
                    min(cupo, len(grupo)),
                )

            print(
                "anclas elegidas por dominio: "
                + ", ".join(
                    f"{d}={min(cupo, len(por_dominio[d]))}"
                    for d in sorted(por_dominio)
                )
            )

            lineas = [
                "# Candidatos para preguntas de colisión\n",
                "Cada bloque es un **ancla** (evidencia posible) con sus "
                "**distractores** más cercanos,",
                "tomados de documentos cuyo dominio humano NO se cruza con el "
                "del ancla.\n",
                "**Cómo usarlo:** leé el ancla y preguntate qué consulta real "
                "se respondería con eso.",
                "Después mirá el distractor: si un buscador podría traerlo por "
                "parecido de vocabulario",
                "pero NO sirve para responder, tenés un ítem de colisión. Si el "
                "distractor en realidad",
                "también responde, no es colisión — descartalo y pasá al "
                "siguiente.\n",
                "⚠️ La cercanía la calcula el embedding y es solo una ayuda "
                "para buscar. El dominio",
                "de cada fragmento sale de la etiqueta humana de su documento. "
                "Que un par esté acá",
                "**no** significa que sea una colisión: eso lo decidís leyendo, "
                "como pide el protocolo.\n",
                "---\n",
            ]

            pares = 0

            for numero, ancla in enumerate(sorted(elegidas, key=lambda c: c["chunk_uid"]), 1):
                dominio_ancla = documentos_claros[ancla["document_id"]]

                ajenos = [
                    documento
                    for documento, silos in dominios.items()
                    if dominio_ancla not in silos
                ]

                if not ajenos:
                    continue

                vecinos = vecinos_de_otro_dominio(
                    cursor,
                    ancla["chunk_uid"],
                    ajenos,
                    argumentos.distractores,
                )

                vecinos = [
                    v for v in vecinos
                    if float(v[5]) >= argumentos.similitud_minima
                ]

                if not vecinos:
                    continue

                ruta = " > ".join(
                    p for p in (ancla["hierarchy"] or []) if p
                )

                lineas.append(f"## {numero}. Ancla — dominio `{dominio_ancla}`\n")
                lineas.append(f"- **fuente:** {ancla['fuente']}")
                lineas.append(f"- **document_id:** `{ancla['document_id']}`")
                lineas.append(f"- **chunk_uid:** `{ancla['chunk_uid']}`")

                if ruta:
                    lineas.append(f"- **ubicación:** {ruta}")

                if ancla["titulo"]:
                    lineas.append(f"- **título:** {recortar(ancla['titulo'], 120)}")

                lineas.append("")
                lineas.append(f"> {recortar(ancla['contenido'], 600)}")
                lineas.append("")
                lineas.append("**Distractores candidatos:**\n")

                for uid, documento, fuente, titulo, contenido, similitud in vecinos:
                    dominios_distractor = "|".join(
                        sorted(dominios.get(documento, set()))
                    )
                    lineas.append(
                        f"- `{similitud:.3f}` · **{fuente}** · dominios "
                        f"`{dominios_distractor}` · chunk `{uid[:16]}...`"
                    )
                    lineas.append(f"  > {recortar(contenido, 300)}")
                    lineas.append("")
                    pares += 1

                lineas.append("---\n")

        conexion.rollback()
    finally:
        conexion.close()

    salida.parent.mkdir(parents=True, exist_ok=True)
    temporal = salida.with_name(f".{salida.name}.tmp")
    temporal.write_text("\n".join(lineas), encoding="utf-8", newline="\n")
    temporal.replace(salida)

    print(f"\npares propuestos: {pares}")
    print(f"listado: {salida}")


if __name__ == "__main__":
    main()
