"""Derive an A1 proposal artifact from the `silo_scores` already persisted.

Its only purpose is to make the multilabel circuit executable without spending
anything: the distribution per chunk is already in the database, so a declared
rule turns it into a domain set of one, several or zero domains.

⚠️ THE UNDERLYING CLASSIFIER IS KNOWN TO BE BAD. `DECISIONES_VIGENTES.md` §6
measured it on 4-ago-2026: `92 %` on normative documents and `11 %` on
non-normative ones, and it changed a document's silo on its own when the corpus
grew. What comes out of here exercises the MECHANISM; it is not evidence about
the corpus and it is not a candidate for promotion.

STRICTLY READ-ONLY over `chunks`: it opens a read-only transaction and writes
nothing. Its output is a JSONL artifact, which `multirag.ingestion.membresias`
then turns into SQL. `chunks.silo` and `chunks.silo_scores` are not touched, as
`DECISIONES_VIGENTES.md` §13 requires.

[ES] Deriva un artefacto de propuestas A1 desde los `silo_scores` ya
persistidos.

Su único propósito es volver ejecutable el circuito multietiqueta sin gastar
nada: la distribución por chunk ya está en la base, así que una regla declarada
la convierte en un conjunto de uno, varios o cero dominios.

⚠️ EL CLASIFICADOR SUBYACENTE ES MALO Y ESTÁ MEDIDO. `DECISIONES_VIGENTES.md`
§6 lo midió el 4-ago-2026: `92 %` en documentos normativos y `11 %` en no
normativos, y cambió por sí solo el silo de un documento al crecer el corpus.
Lo que sale de acá ejercita el MECANISMO; no es evidencia sobre el corpus ni un
candidato a promoción.

ESTRICTAMENTE DE SOLO LECTURA sobre `chunks`: abre una transacción de solo
lectura y no escribe nada. Su salida es un artefacto JSONL, que después
`multirag.ingestion.membresias` convierte en SQL. No toca `chunks.silo` ni
`chunks.silo_scores`, como exige `DECISIONES_VIGENTES.md` §13.
"""

import argparse
import collections
import json
from pathlib import Path

from multirag.config import ROUTER_COBERTURA, SILOS
from multirag.db import conectar
from multirag.ingestion.membresias import (
    ErrorDeMembresias,
    conjunto_por_cobertura,
    conjunto_por_margen,
    conjunto_por_umbral,
)


# What the score means. It is a softmax over cosine similarities to the silo
# centroid: it is NOT a calibrated probability, and the name says so.
#
# [ES] Qué significa el score. Es un softmax sobre similitudes coseno al
# centroide del silo: NO es una probabilidad calibrada, y el nombre lo dice.
SCORE_KIND = "softmax_coseno_a_centroide_no_calibrado"

METODO = "coseno_a_centroide"


# Sweep values per rule. They only describe the snapshot; none is preferred.
# [ES] Valores del barrido por regla. Solo describen el snapshot; ninguno es
# preferido.
BARRIDO_PREDETERMINADO = {
    "cobertura": (0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90),
    "umbral": (0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60),
    "margen": (0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30),
}


def leer_scores(cursor, limite=None) -> list[tuple[str, dict]]:
    """Read `chunk_uid` and its score distribution. Read-only.

    [ES] Lee `chunk_uid` y su distribución de scores. Solo lectura.
    """
    cursor.execute(
        """
        SELECT chunk_uid, silo_scores
        FROM chunks
        WHERE chunk_uid IS NOT NULL
          AND silo_scores IS NOT NULL
        ORDER BY chunk_uid
        """
        + ("LIMIT %s" if limite else ""),
        (limite,) if limite else (),
    )

    filas = []

    for chunk_uid, scores in cursor.fetchall():
        if isinstance(scores, str):
            scores = json.loads(scores)

        if not isinstance(scores, dict):
            continue

        filas.append((chunk_uid, scores))

    return filas


def aplicar_regla(scores: dict, regla: str, valor: float) -> list[str]:
    """Apply the declared A1 rule to one distribution.

    [ES] Aplica la regla A1 declarada a una distribución.
    """
    if regla == "margen":
        return conjunto_por_margen(scores, valor)

    if regla == "umbral":
        return conjunto_por_umbral(scores, valor)

    if regla == "cobertura":
        return conjunto_por_cobertura(scores, valor)

    raise ErrorDeMembresias(
        f"Regla desconocida: {regla!r}. Las reglas válidas son "
        + ", ".join(sorted(BARRIDO_PREDETERMINADO))
        + "."
    )


def construir_registros(
    filas: list[tuple[str, dict]],
    *,
    regla: str,
    valor: float,
) -> list[dict]:
    """Build the proposal artifact, one record per chunk.

    [ES] Construye el artefacto de propuestas, un registro por chunk.
    """
    registros = []

    for chunk_uid, scores in filas:
        dominios = aplicar_regla(scores, regla, valor)

        registros.append(
            {
                "chunk_uid": chunk_uid,
                "dominios_propuestos": dominios,
                "estado_asignacion": (
                    "asignado" if dominios else "incierto"
                ),
                "scores_por_dominio": {
                    dominio: float(scores[dominio])
                    for dominio in dominios
                },
                # The full distribution travels with the artifact so the rule
                # parameter can be swept later without querying again.
                # [ES] La distribución completa viaja con el artefacto para
                # poder barrer el parámetro de la regla sin volver a consultar.
                "distribucion": {
                    dominio: float(valor)
                    for dominio, valor in scores.items()
                    if dominio in SILOS
                },
                "modelo_resuelto": METODO,
                "regla": regla,
                "parametro_regla": valor,
            }
        )

    return registros


def resumir(registros: list[dict]) -> dict:
    """Count how many domains each chunk received.

    The distribution of set sizes is the first thing worth looking at: if every
    chunk gets exactly one domain, A1 collapses into A0 and there is nothing to
    compare.

    [ES] Cuenta cuántos dominios recibió cada chunk.

    La distribución de tamaños del conjunto es lo primero que vale mirar: si
    todo chunk recibe exactamente un dominio, A1 colapsa en A0 y no hay nada
    que comparar.
    """
    tamanos = collections.Counter(
        len(registro["dominios_propuestos"])
        for registro in registros
    )

    por_dominio = collections.Counter(
        dominio
        for registro in registros
        for dominio in registro["dominios_propuestos"]
    )

    return {
        "chunks": len(registros),
        "tamanos": dict(sorted(tamanos.items())),
        "por_dominio": dict(sorted(por_dominio.items())),
        "membresias": sum(
            tamano * cantidad
            for tamano, cantidad in tamanos.items()
        ),
    }


def barrer_parametro(
    filas: list[tuple[str, dict]],
    *,
    regla: str,
    valores,
    silos_a0: dict | None = None,
) -> list[dict]:
    """Report what each rule parameter would produce, in a single pass.

    It answers a question that must be settled before running the pilot: with
    which parameter does A1 stop being A0 without becoming the monolithic arm?
    A set that opens almost every domain makes the segregation collapse, and
    then B1 and B2 stop differing from B0 for a reason that has nothing to do
    with the architecture.

    This is DESCRIPTION of the snapshot, not calibration: no ground truth is
    involved, so no parameter can be declared better here.

    [ES] Informa qué produciría cada parámetro de la regla, en una sola pasada.

    Responde una pregunta que hay que zanjar antes de correr el piloto: ¿con
    qué parámetro A1 deja de ser A0 sin convertirse en el brazo monolítico? Un
    conjunto que abre casi todos los dominios hace colapsar la segregación, y
    entonces B1 y B2 dejan de diferenciarse de B0 por un motivo que nada tiene
    que ver con la arquitectura.

    Esto es DESCRIPCIÓN del snapshot, no calibración: no interviene ninguna
    verdad de referencia, así que acá no puede declararse mejor ningún
    parámetro.
    """
    informe = []

    for valor in valores:
        registros = construir_registros(
            filas,
            regla=regla,
            valor=valor,
        )
        resumen = resumir(registros)

        conserva_a0 = None
        inflacion = {}

        if silos_a0:
            conserva_a0 = sum(
                1
                for registro in registros
                if silos_a0.get(registro["chunk_uid"])
                in registro["dominios_propuestos"]
            )

            # How much the retrievable scope of each domain grows: chunks
            # eligible under A1 over chunks labelled with that domain under A0.
            # It is a ratio of counts, so no outlier can drag it the way a mean
            # over domains-per-chunk can.
            #
            # [ES] Cuánto crece el alcance recuperable de cada dominio: chunks
            # elegibles bajo A1 sobre chunks etiquetados con ese dominio bajo
            # A0. Es un cociente de conteos, así que ningún valor atípico lo
            # arrastra como sí puede hacerlo un promedio de dominios por chunk.
            conteo_a0 = collections.Counter(silos_a0.values())

            inflacion = {
                dominio: (
                    resumen["por_dominio"].get(dominio, 0)
                    / conteo_a0[dominio]
                )
                for dominio in sorted(SILOS)
                if conteo_a0.get(dominio)
            }

        total = resumen["chunks"] or 1

        informe.append(
            {
                "valor": valor,
                "membresias": resumen["membresias"],
                # Chunks where A1 actually says something different from A0.
                # This is the size of the experimental difference, and it is a
                # plain count: no mean, no outlier sensitivity.
                # [ES] Chunks donde A1 dice algo distinto de A0. Es el tamaño
                # de la diferencia experimental, y es un conteo llano: sin
                # promedio y sin sensibilidad a valores atípicos.
                "difieren_de_a0": sum(
                    cantidad
                    for tamano, cantidad in resumen["tamanos"].items()
                    if tamano != 1
                ),
                # Chunks where every domain entered: the classifier said
                # nothing. Counted apart instead of smeared into an average.
                # [ES] Chunks donde entraron todos los dominios: el
                # clasificador no dijo nada. Se cuentan aparte en lugar de
                # diluirse en un promedio.
                "sin_discriminar": resumen["tamanos"].get(len(SILOS), 0),
                "mediana": _mediana(resumen["tamanos"]),
                "inflacion": inflacion,
                "tamanos": resumen["tamanos"],
                "conserva_a0": conserva_a0,
                "chunks": resumen["chunks"],
                "proporcion_difieren": (
                    sum(
                        cantidad
                        for tamano, cantidad in resumen["tamanos"].items()
                        if tamano != 1
                    )
                    / total
                ),
            }
        )

    return informe


def _mediana(tamanos: dict) -> float:
    """Median number of domains per chunk, from the size histogram.

    Unlike the mean it is not dragged by the chunks that open every domain.

    [ES] Mediana de dominios por chunk, a partir del histograma de tamaños.

    A diferencia del promedio, no la arrastran los chunks que abren todos los
    dominios.
    """
    total = sum(tamanos.values())

    if not total:
        return 0.0

    objetivo = total / 2
    acumulado = 0

    for tamano in sorted(tamanos):
        acumulado += tamanos[tamano]

        if acumulado >= objetivo:
            return float(tamano)

    return float(max(tamanos))


def analizar_margenes(
    filas: list[tuple[str, dict]],
    *,
    banda=(0.50, 0.60, 0.70, 0.80),
) -> dict:
    """Distinguish genuine multi-domain content from classifier confusion.

    Two very different situations produce the same "2 domains per chunk":

    - genuine multi-domain matter: the two top scores are BOTH high and close,
      and the bottom ones clearly lower. Such a chunk stays at two domains
      across a wide band of coverage values.
    - undecided classifier: the four scores are all similar. The set of such a
      chunk grows smoothly with the parameter and never settles.

    The margin between the first and the second score separates them, and the
    stability across the band confirms it. No ground truth is involved: this
    describes the classifier's geometry, not the corpus's truth.

    [ES] Distingue contenido genuinamente multidominio de confusión del
    clasificador.

    Dos situaciones muy distintas producen el mismo «2 dominios por chunk»:

    - materia genuinamente multidominio: los dos scores mayores son AMBOS altos
      y cercanos, y los menores claramente más bajos. Un chunk así se mantiene
      en dos dominios a lo largo de una banda amplia de valores de cobertura.
    - clasificador indeciso: los cuatro scores son parecidos. El conjunto de un
      chunk así crece suavemente con el parámetro y nunca se asienta.

    El margen entre el primer y el segundo score los separa, y la estabilidad a
    lo largo de la banda lo confirma. No interviene ninguna verdad de
    referencia: esto describe la geometría del clasificador, no la verdad del
    corpus.
    """
    cortes = (0.01, 0.05, 0.10, 0.20, 0.40)
    margenes = collections.Counter()
    estables = collections.Counter()

    for _, scores in filas:
        ordenados = sorted(
            (
                float(valor)
                for dominio, valor in scores.items()
                if dominio in SILOS
            ),
            reverse=True,
        )

        if len(ordenados) < 2:
            continue

        margen = ordenados[0] - ordenados[1]

        etiqueta = f">={cortes[-1]}"

        for corte in cortes:
            if margen < corte:
                etiqueta = f"<{corte}"
                break

        margenes[etiqueta] += 1

        tamanos = {
            len(conjunto_por_cobertura(scores, valor))
            for valor in banda
        }

        estables[
            f"{tamanos.pop()} dominio(s)"
            if len(tamanos) == 1
            else "inestable"
        ] += 1

    return {
        "total": sum(margenes.values()),
        "margenes": dict(margenes),
        "estables": dict(estables),
        "banda": banda,
        "cortes": cortes,
    }


def leer_silos(cursor) -> dict:
    """Read the A0 label of every chunk. Read-only.

    [ES] Lee la etiqueta A0 de cada chunk. Solo lectura.
    """
    cursor.execute(
        """
        SELECT chunk_uid, silo
        FROM chunks
        WHERE chunk_uid IS NOT NULL
        """
    )

    return dict(cursor.fetchall())


def guardar_jsonl(registros: list[dict], ruta_salida: Path) -> Path:
    """Save the artifact atomically, without overwriting.

    [ES] Guarda el artefacto atómicamente, sin sobrescribir.
    """
    ruta = Path(ruta_salida).resolve()

    if ruta.exists():
        raise ErrorDeMembresias(
            f"La salida ya existe y no será sobrescrita: {ruta}"
        )

    ruta.parent.mkdir(parents=True, exist_ok=True)

    temporal = ruta.with_name(f".{ruta.name}.tmp")

    temporal.write_text(
        "".join(
            json.dumps(registro, ensure_ascii=False, sort_keys=True) + "\n"
            for registro in registros
        ),
        encoding="utf-8",
        newline="\n",
    )
    temporal.replace(ruta)

    return ruta


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.

    [ES] Construye la interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Deriva propuestas A1 desde los silo_scores ya persistidos. "
            "Solo lectura: no modifica la base."
        )
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=None,
        help=(
            "Artefacto JSONL a generar. No sobrescribe. "
            "Se omite si solo se pide --barrido."
        ),
    )
    parser.add_argument(
        "--barrido",
        nargs="*",
        type=float,
        default=None,
        help=(
            "Informa qué produciría cada valor de la regla, sin generar "
            "artefacto. Sin valores usa un barrido predeterminado."
        ),
    )
    parser.add_argument(
        "--regla",
        default="margen",
        choices=("margen", "cobertura", "umbral"),
        help=(
            "margen: el ganador más todo dominio a menos de esa distancia "
            "de él; nunca pierde la etiqueta A0. "
            "cobertura: el conjunto más chico que acumula la masa pedida. "
            "umbral: todo dominio que alcance el valor."
        ),
    )
    parser.add_argument(
        "--valor",
        type=float,
        default=None,
        help=(
            "Parámetro de la regla. Es un valor DECLARADO, no calibrado. "
            "Sin valor usa 0.05 para margen y "
            f"{ROUTER_COBERTURA} (ROUTER_COBERTURA) para cobertura."
        ),
    )
    parser.add_argument(
        "--margenes",
        action="store_true",
        help=(
            "Distingue contenido multidominio genuino de confusión del "
            "clasificador, mediante el margen entre los dos scores mayores "
            "y la estabilidad del conjunto a lo largo de una banda."
        ),
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Procesar solo los primeros N chunks (prueba rápida).",
    )
    return parser


def main() -> None:
    """Generate the artifact from the command line.

    [ES] Genera el artefacto desde la línea de comandos.
    """
    argumentos = construir_parser().parse_args()

    if (
        argumentos.salida is None
        and argumentos.barrido is None
        and not argumentos.margenes
    ):
        raise ErrorDeMembresias(
            "Indique --salida para generar el artefacto, --barrido para "
            "explorar el parámetro, --margenes para diagnosticar la señal, "
            "o una combinación."
        )

    if argumentos.valor is None:
        argumentos.valor = (
            0.05 if argumentos.regla == "margen" else ROUTER_COBERTURA
        )

    conexion = conectar()

    try:
        with conexion.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            filas = leer_scores(cursor, argumentos.limite)
            silos_a0 = leer_silos(cursor)

        conexion.rollback()
    finally:
        conexion.close()

    if not filas:
        raise ErrorDeMembresias(
            "Ningún chunk tiene silo_scores persistidos."
        )

    if argumentos.margenes:
        analisis = analizar_margenes(filas)
        total = analisis["total"]

        print(
            f"Diagnóstico de la señal sobre {total} chunks.\n"
            "Describe la geometría del clasificador, NO la verdad del corpus."
        )
        print(
            "\nMargen entre el primer y el segundo score. Un margen chico "
            "significa que el clasificador NO distingue entre esos dos "
            "dominios; no significa que el fragmento trate de ambos."
        )

        for etiqueta in (
            [f"<{corte}" for corte in analisis["cortes"]]
            + [f">={analisis['cortes'][-1]}"]
        ):
            cantidad = analisis["margenes"].get(etiqueta, 0)
            print(
                f"  margen {etiqueta:>7}: {cantidad:>6} "
                f"({100 * cantidad / total:.1f}%)"
            )

        print(
            "\nEstabilidad del conjunto en la banda de cobertura "
            f"{analisis['banda']}. Un chunk genuinamente multidominio "
            "conserva su cantidad de dominios en toda la banda; uno que solo "
            "confunde al clasificador crece con el parámetro."
        )

        for etiqueta, cantidad in sorted(
            analisis["estables"].items()
        ):
            print(
                f"  {etiqueta:>12}: {cantidad:>6} "
                f"({100 * cantidad / total:.1f}%)"
            )

        if argumentos.barrido is None and argumentos.salida is None:
            return

        print()

    if argumentos.barrido is not None:
        valores = argumentos.barrido or list(BARRIDO_PREDETERMINADO[
            argumentos.regla
        ])

        print(
            f"Barrido de la regla '{argumentos.regla}' sobre "
            f"{len(filas)} chunks. Descripción del snapshot, NO calibración: "
            "sin verdad de referencia no se puede declarar mejor ningún valor."
        )
        print(
            "\nA0 abre exactamente 1 dominio por chunk. Si A1 abre casi "
            f"{len(SILOS)}, la segregación colapsa y B1/B2 dejan de "
            "distinguirse de B0 por un motivo ajeno a la arquitectura.\n"
        )
        print(
            "'difieren de A0' es la cantidad de chunks donde A1 dice algo "
            "distinto de A0: es el tamaño real de la diferencia experimental. "
            "'sin discriminar' son los chunks que abren TODOS los dominios, o "
            "sea donde el clasificador no dijo nada. 'inflación' es cuánto "
            "crece el alcance recuperable de cada dominio (elegibles A1 sobre "
            "etiquetados A0), como cociente de conteos.\n"
        )
        print(
            f"{'valor':>7} {'difieren de A0':>16} {'sin discrim.':>13} "
            f"{'mediana':>8} {'inflación mín–máx':>19}  reparto"
        )

        informe = barrer_parametro(
            filas,
            regla=argumentos.regla,
            valores=valores,
            silos_a0=silos_a0,
        )

        for linea in informe:
            reparto = " ".join(
                f"{tamano}:{cantidad}"
                for tamano, cantidad in linea["tamanos"].items()
            )
            difieren = (
                f"{linea['difieren_de_a0']} "
                f"({100 * linea['proporcion_difieren']:.1f}%)"
            )
            sin_discriminar = (
                f"{linea['sin_discriminar']} "
                f"({100 * linea['sin_discriminar'] / linea['chunks']:.1f}%)"
            )
            inflacion = (
                f"{min(linea['inflacion'].values()):.2f}–"
                f"{max(linea['inflacion'].values()):.2f}x"
                if linea["inflacion"]
                else "-"
            )

            print(
                f"{linea['valor']:>7} {difieren:>16} {sin_discriminar:>13} "
                f"{linea['mediana']:>8.0f} {inflacion:>19}  {reparto}"
            )

        print(
            "\nTodas las configuraciones conservan la etiqueta A0 en el "
            "100 % de los chunks: el ganador siempre entra en el conjunto."
            if all(
                linea["conserva_a0"] == linea["chunks"]
                for linea in informe
            )
            else "\nATENCIÓN: alguna configuración pierde la etiqueta A0 de "
            "algunos chunks, que dejarían de ser recuperables bajo A1."
        )

        if argumentos.salida is None:
            return

        print()

    registros = construir_registros(
        filas,
        regla=argumentos.regla,
        valor=argumentos.valor,
    )

    ruta = guardar_jsonl(registros, argumentos.salida)
    resumen = resumir(registros)

    print(f"Regla: {argumentos.regla}={argumentos.valor} (DECLARADA, no calibrada)")
    print(f"Chunks procesados: {resumen['chunks']}")
    print(f"Membresías que se generarían: {resumen['membresias']}")
    print("Chunks por cantidad de dominios:")

    for tamano, cantidad in resumen["tamanos"].items():
        print(f"  {tamano} dominio(s): {cantidad}")

    print("Membresías por dominio:")

    for dominio, cantidad in resumen["por_dominio"].items():
        print(f"  {dominio}: {cantidad}")

    print(f"\nArtefacto: {ruta}")
    print(
        "\nADVERTENCIA: el clasificador por coseno está medido como malo "
        "(92 % normativo / 11 % no normativo, DECISIONES_VIGENTES.md §6). "
        "Esto sirve para ejercitar el mecanismo A1, NO como evidencia ni "
        "como candidato a promoción."
    )
    print(
        f"\nSiguiente paso (genera el SQL, sin aplicarlo):\n"
        f"  python -B -m multirag.ingestion.membresias \\\n"
        f"    --propuestas {ruta} \\\n"
        f"    --salida <archivo>.sql \\\n"
        f"    --assignment-version coseno-{argumentos.regla}-{argumentos.valor} \\\n"
        f"    --taxonomy-version <version> \\\n"
        f"    --score-kind {SCORE_KIND}"
    )


if __name__ == "__main__":
    main()
