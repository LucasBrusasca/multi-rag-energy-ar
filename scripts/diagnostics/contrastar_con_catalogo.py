"""Contrast the automatic assignment against the human domains of the catalog.

The curated catalog already carries a human, document-level, multi-domain
label. It is the only human multilabel signal that exists today, and nothing
uses it beyond intersecting it with the four silos.

What this can and cannot conclude:

- A document label does NOT transfer to every one of its chunks: rule 3 of
  `DECISION_ARQUITECTURA_MULTILABEL.md` forbids inheriting it. So a chunk whose
  domain IS among its document's domains proves nothing.
- The converse does carry information: a chunk assigned a domain that its
  document does NOT have anywhere is either a classifier error or a human
  omission. At scale, the rate of those is a weak but human-grounded error
  signal over the WHOLE corpus, without labelling a single chunk by hand.
- It is an upper bound on agreement, never an accuracy: the human label is
  coarser than the unit being judged.

STRICTLY READ-ONLY. It opens a read-only transaction and writes nothing.

[ES] Contrasta la asignación automática contra los dominios humanos del
catálogo.

El catálogo curado ya trae una etiqueta humana, a nivel de documento y
multidominio. Es la única señal humana multietiqueta que existe hoy, y nada la
usa más allá de intersecarla con los cuatro silos.

Qué puede y qué no puede concluir:

- La etiqueta de un documento NO se traslada a cada uno de sus chunks: la regla
  3 de `DECISION_ARQUITECTURA_MULTILABEL.md` prohíbe heredarla. Así que un
  chunk cuyo dominio SÍ está entre los del documento no prueba nada.
- La recíproca sí informa: un chunk al que se le asigna un dominio que su
  documento NO tiene en ninguna parte es o un error del clasificador o una
  omisión humana. A escala, la tasa de esos casos es una señal de error débil
  pero anclada en humanos sobre TODO el corpus, sin etiquetar un solo chunk a
  mano.
- Es una cota superior del acuerdo, nunca una exactitud: la etiqueta humana es
  más gruesa que la unidad que se juzga.

ESTRICTAMENTE DE SOLO LECTURA. Abre una transacción de solo lectura y no
escribe nada.
"""

import argparse
import collections
import csv
import json
from pathlib import Path

from multirag.config import SILOS
from multirag.db import conectar
from multirag.ingestion.membresias import conjunto_por_margen
from multirag.paths import DATA_DIR


CATALOGO_PREDETERMINADO = DATA_DIR / "catalog" / "metadatos_curados.csv"


def leer_catalogo(ruta: Path) -> tuple[dict, collections.Counter]:
    """Read document -> human domains, and count what falls outside the silos.

    Both are returned: silently dropping the human labels that are not one of
    the four silos is precisely what hides how much of the catalog the current
    taxonomy cannot express.

    [ES] Lee documento -> dominios humanos, y cuenta lo que cae fuera de los
    silos.

    Se devuelven ambos: descartar en silencio las etiquetas humanas que no son
    uno de los cuatro silos es justamente lo que oculta cuánto del catálogo no
    puede expresar la taxonomía vigente.
    """
    por_documento: dict[str, dict] = {}
    fuera = collections.Counter()

    with Path(ruta).open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            crudos = {
                valor.strip()
                for valor in (
                    fila.get("dominios_documentales") or ""
                ).split("|")
                if valor.strip()
            }

            for dominio in crudos - set(SILOS):
                fuera[dominio] += 1

            documento = (fila.get("document_id") or "").strip()

            if not documento:
                continue

            por_documento[documento] = {
                "humanos": crudos,
                "silos": crudos & set(SILOS),
            }

    return por_documento, fuera


def leer_chunks(cursor, limite=None) -> list[dict]:
    """Read every chunk with its document, silo and score distribution.

    [ES] Lee cada chunk con su documento, silo y distribución de scores.
    """
    cursor.execute(
        """
        SELECT chunk_uid, document_id, silo, silo_scores
        FROM chunks
        WHERE chunk_uid IS NOT NULL
        ORDER BY chunk_uid
        """
        + ("LIMIT %s" if limite else ""),
        (limite,) if limite else (),
    )

    chunks = []

    for chunk_uid, document_id, silo, scores in cursor.fetchall():
        if isinstance(scores, str):
            scores = json.loads(scores)

        chunks.append(
            {
                "chunk_uid": chunk_uid,
                "document_id": document_id,
                "silo": silo,
                "scores": scores if isinstance(scores, dict) else {},
            }
        )

    return chunks


def contrastar(
    chunks: list[dict],
    catalogo: dict,
    *,
    margen: float | None = None,
) -> dict:
    """Compare each chunk's assignment with its document's human domains.

    [ES] Compara la asignación de cada chunk con los dominios humanos de su
    documento.
    """
    resultado = {
        "chunks": len(chunks),
        "sin_documento": 0,
        "documento_no_catalogado": 0,
        "documento_sin_silos": 0,
        "evaluables": 0,
        "a0_dentro": 0,
        "a0_fuera": collections.Counter(),
        "a1_evaluables": 0,
        "a1_contenido": 0,
        "a1_agrega_fuera": 0,
        "a1_dominios_fuera": collections.Counter(),
        # How many silos the human label of each chunk's document covers. When
        # it covers all of them the test CANNOT fail, so those chunks inflate
        # the agreement without contributing any evidence.
        # [ES] Cuántos silos cubre la etiqueta humana del documento de cada
        # chunk. Cuando los cubre todos, el test NO PUEDE fallar, así que esos
        # chunks inflan el acuerdo sin aportar evidencia.
        "amplitud_del_documento": collections.Counter(),
        "esperado_al_azar": 0.0,
        # Same contrast restricted to the chunks whose document leaves at
        # least one silo out: only there can the test discriminate.
        # [ES] El mismo contraste restringido a los chunks cuyo documento deja
        # afuera al menos un silo: solo ahí el test puede discriminar.
        "discriminantes": 0,
        "a0_dentro_discriminantes": 0,
        "casos_fuera": [],
        # Agreement broken down by the document's human silo set. Without this
        # the aggregate hides WHICH documents the strict test actually covers:
        # if the blind ones are exactly those where the classifier is known to
        # fail, a high overall figure is measuring the easy half.
        # [ES] Acuerdo desagregado por el conjunto de silos humanos del
        # documento. Sin esto, el agregado oculta QUÉ documentos cubre de
        # verdad el test estricto: si los ciegos son justo aquellos donde el
        # clasificador falla, una cifra global alta está midiendo la mitad
        # fácil.
        "por_conjunto": collections.defaultdict(
            lambda: {"chunks": 0, "dentro": 0}
        ),
    }

    for chunk in chunks:
        documento = chunk["document_id"]

        if not documento:
            resultado["sin_documento"] += 1
            continue

        entrada = catalogo.get(documento)

        if entrada is None:
            resultado["documento_no_catalogado"] += 1
            continue

        humanos = entrada["silos"]

        if not humanos:
            resultado["documento_sin_silos"] += 1
            continue

        resultado["evaluables"] += 1
        resultado["amplitud_del_documento"][len(humanos)] += 1

        # Probability that a silo drawn at random would land inside this
        # document's human label. Averaged over chunks it is the null the
        # observed agreement has to beat to mean anything.
        # [ES] Probabilidad de que un silo sorteado al azar cayera dentro de la
        # etiqueta humana de este documento. Promediada sobre los chunks es la
        # hipótesis nula que el acuerdo observado tiene que superar para
        # significar algo.
        resultado["esperado_al_azar"] += len(humanos) / len(SILOS)

        discrimina = len(humanos) < len(SILOS)

        if discrimina:
            resultado["discriminantes"] += 1

        clave = "|".join(sorted(humanos))
        resultado["por_conjunto"][clave]["chunks"] += 1

        if chunk["silo"] in humanos:
            resultado["a0_dentro"] += 1
            resultado["por_conjunto"][clave]["dentro"] += 1

            if discrimina:
                resultado["a0_dentro_discriminantes"] += 1
        else:
            resultado["a0_fuera"][
                f"{chunk['silo']} en documento {'|'.join(sorted(humanos))}"
            ] += 1
            resultado["casos_fuera"].append(
                {
                    "chunk_uid": chunk["chunk_uid"],
                    "document_id": documento,
                    "silo": chunk["silo"],
                    "dominios_humanos": sorted(humanos),
                }
            )

        if margen is None or not chunk["scores"]:
            continue

        conjunto = set(conjunto_por_margen(chunk["scores"], margen))

        resultado["a1_evaluables"] += 1

        if conjunto <= humanos:
            resultado["a1_contenido"] += 1
        else:
            resultado["a1_agrega_fuera"] += 1

            for dominio in conjunto - humanos:
                resultado["a1_dominios_fuera"][dominio] += 1

    return resultado


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.

    [ES] Construye la interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Contrasta la asignación automática contra los dominios humanos "
            "del catálogo. Solo lectura."
        )
    )
    parser.add_argument(
        "--catalogo",
        type=Path,
        default=CATALOGO_PREDETERMINADO,
        help="CSV de metadatos curados.",
    )
    parser.add_argument(
        "--margen",
        type=float,
        default=0.05,
        help=(
            "Margen de la regla A1 a contrastar. Por defecto 0.05."
        ),
    )
    parser.add_argument(
        "--exportar-sospechosos",
        type=Path,
        default=None,
        help=(
            "Guarda en JSONL los chunks cuyo silo no figura en su "
            "documento. Son candidatos de error señalados por juicio "
            "humano, sin etiquetar ningún chunk a mano."
        ),
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Procesar solo los primeros N chunks.",
    )
    return parser


def main() -> None:
    """Run the contrast.

    [ES] Ejecuta el contraste.
    """
    argumentos = construir_parser().parse_args()

    catalogo, fuera = leer_catalogo(argumentos.catalogo)

    print("=== Vocabulario humano del catálogo ===")
    print(f"documentos catalogados: {len(catalogo)}")

    if fuera:
        total_fuera = sum(fuera.values())
        print(
            f"\nEtiquetas humanas que la taxonomía de 4 silos NO puede "
            f"expresar, y que el código vigente descarta en silencio "
            f"({total_fuera} menciones):"
        )

        for dominio, cantidad in fuera.most_common():
            print(f"  {dominio:<14} en {cantidad} documento(s)")

        print(
            "\nSon candidatas a 'fuera_de_ontologia' (regla 4 de la decisión) "
            "o a un silo nuevo. Hoy no son ninguna de las dos: desaparecen."
        )

    conexion = conectar()

    try:
        with conexion.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            chunks = leer_chunks(cursor, argumentos.limite)

        conexion.rollback()
    finally:
        conexion.close()

    resultado = contrastar(
        chunks,
        catalogo,
        margen=argumentos.margen,
    )

    print("\n=== Cobertura del contraste ===")
    print(f"chunks leídos: {resultado['chunks']}")
    print(f"  sin document_id: {resultado['sin_documento']}")
    print(
        f"  documento no catalogado: "
        f"{resultado['documento_no_catalogado']}"
    )
    print(
        f"  documento sin ningún silo humano: "
        f"{resultado['documento_sin_silos']}"
    )
    print(f"  evaluables: {resultado['evaluables']}")

    evaluables = resultado["evaluables"] or 1

    print("\n=== A0: el silo del chunk contra los dominios del documento ===")
    print(
        "Un chunk cuyo silo NO figura en ninguna parte de su documento es un "
        "error del clasificador o una omisión humana. No al revés: coincidir "
        "no prueba nada, porque la etiqueta documental no se hereda."
    )
    print("\n--- Poder del test ---")
    print(
        "Cuántos silos cubre la etiqueta humana del documento de cada chunk. "
        f"Si los cubre los {len(SILOS)}, el test NO PUEDE fallar para ese "
        "chunk: cuenta como acuerdo sin aportar evidencia."
    )

    for amplitud, cantidad in sorted(
        resultado["amplitud_del_documento"].items()
    ):
        marca = (
            "  <<< el test no discrimina"
            if amplitud >= len(SILOS)
            else ""
        )
        print(
            f"  documento con {amplitud} silo(s) humano(s): {cantidad} "
            f"chunks ({100 * cantidad / evaluables:.1f}%){marca}"
        )

    esperado = resultado["esperado_al_azar"] / evaluables

    print(
        f"\nAcuerdo esperado si el silo se sorteara AL AZAR: "
        f"{100 * esperado:.1f}%"
    )

    print(
        f"\ndentro de los dominios del documento: {resultado['a0_dentro']} "
        f"({100 * resultado['a0_dentro'] / evaluables:.1f}%)"
    )

    fuera_a0 = sum(resultado["a0_fuera"].values())

    print(
        f"FUERA de los dominios del documento: {fuera_a0} "
        f"({100 * fuera_a0 / evaluables:.1f}%)"
    )

    observado = resultado["a0_dentro"] / evaluables

    print(
        f"\nEl acuerdo observado ({100 * observado:.1f}%) contra el azar "
        f"({100 * esperado:.1f}%): "
        + (
            "supera al azar, así que el contraste dice algo."
            if observado > esperado + 0.05
            else "NO lo supera con claridad. El acuerdo es en buena parte un "
            "artefacto de lo amplias que son las etiquetas humanas, no "
            "evidencia de que el clasificador acierte."
        )
    )

    if resultado["discriminantes"]:
        discriminantes = resultado["discriminantes"]

        print(
            f"\nRestringido a los {discriminantes} chunks cuyo documento deja "
            f"afuera al menos un silo ({100 * discriminantes / evaluables:.1f}"
            "% del total), que son los únicos donde el test puede fallar:"
        )
        print(
            f"  dentro: {resultado['a0_dentro_discriminantes']} "
            f"({100 * resultado['a0_dentro_discriminantes'] / discriminantes:.1f}%)"
        )
        print(
            f"  FUERA:  {discriminantes - resultado['a0_dentro_discriminantes']} "
            f"({100 * (discriminantes - resultado['a0_dentro_discriminantes']) / discriminantes:.1f}%)"
        )

    if resultado["a0_fuera"]:
        print("\n  casos más frecuentes:")

        for caso, cantidad in resultado["a0_fuera"].most_common(10):
            print(f"    {cantidad:>5}  {caso}")

    if resultado["por_conjunto"]:
        print(
            "\n--- Dónde cubre el test, desagregado por documento ---"
        )
        print(
            "Un conjunto humano de "
            f"{len(SILOS)} silos acepta cualquier asignación. Si esos "
            "documentos son justamente donde el clasificador ya estaba medido "
            "como malo, la cifra global está midiendo la mitad fácil."
        )
        print(
            f"\n{'silos humanos del documento':<44} {'chunks':>7} "
            f"{'dentro':>8} {'azar':>7}"
        )

        for clave, datos in sorted(
            resultado["por_conjunto"].items(),
            key=lambda par: -par[1]["chunks"],
        ):
            cantidad = datos["chunks"]
            amplitud = len(clave.split("|"))
            azar = amplitud / len(SILOS)
            marca = "  <<< ciego" if amplitud >= len(SILOS) else ""

            print(
                f"{clave:<44} {cantidad:>7} "
                f"{100 * datos['dentro'] / cantidad:>7.1f}% "
                f"{100 * azar:>6.0f}%{marca}"
            )

    if resultado["a1_evaluables"]:
        a1 = resultado["a1_evaluables"]

        print(
            f"\n=== A1 (margen {argumentos.margen}): el conjunto contra el "
            "documento ==="
        )
        print(
            f"conjunto contenido en el documento: "
            f"{resultado['a1_contenido']} "
            f"({100 * resultado['a1_contenido'] / a1:.1f}%)"
        )
        print(
            f"agrega al menos un dominio ajeno al documento: "
            f"{resultado['a1_agrega_fuera']} "
            f"({100 * resultado['a1_agrega_fuera'] / a1:.1f}%)"
        )

        if resultado["a1_dominios_fuera"]:
            print("\n  dominios agregados que el documento no tiene:")

            for dominio, cantidad in resultado[
                "a1_dominios_fuera"
            ].most_common():
                print(f"    {dominio:<14} {cantidad}")

    if argumentos.exportar_sospechosos and resultado["casos_fuera"]:
        ruta = Path(argumentos.exportar_sospechosos).resolve()

        if ruta.exists():
            raise FileExistsError(
                f"La salida ya existe y no será sobrescrita: {ruta}"
            )

        ruta.parent.mkdir(parents=True, exist_ok=True)

        temporal = ruta.with_name(f".{ruta.name}.tmp")
        temporal.write_text(
            "".join(
                json.dumps(caso, ensure_ascii=False, sort_keys=True) + "\n"
                for caso in resultado["casos_fuera"]
            ),
            encoding="utf-8",
            newline="\n",
        )
        temporal.replace(ruta)

        print(
            f"\n{len(resultado['casos_fuera'])} chunks sospechosos "
            f"exportados a {ruta}."
        )
        print(
            "Son candidatos naturales para el bloque incierto de la muestra "
            "Gold: los señala el juicio humano ya existente, no el propio "
            "clasificador. NO son errores confirmados: hay que leerlos."
        )

    print(
        "\nEsto es una COTA SUPERIOR del acuerdo, no una exactitud: la "
        "etiqueta humana es del documento y la decisión es del chunk."
    )


if __name__ == "__main__":
    main()
