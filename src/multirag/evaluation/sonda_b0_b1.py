"""Exploratory probe: does knowing where the evidence physically lives help?

B0 searches the whole corpus. B1 searches only the silo(s) where the anchored
evidence is stored in the frozen snapshot (location oracle: diagnostic, not
deployable). Both arms share embedder, retrieval function and final k.

Read-only. EXPLORATORY: not confirmatory evidence.

[ES] Sonda exploratoria: saber donde vive fisicamente la evidencia, ayuda?

B0 busca en todo el corpus. B1 busca solo en el o los silos donde la evidencia
anclada esta guardada en el snapshot congelado (oraculo de ubicacion: es
diagnostico, no desplegable). Los dos brazos comparten embedder, funcion de
recuperacion y k final.

Solo lectura. EXPLORATORIO: no es evidencia confirmatoria.
"""

import argparse
import re
from pathlib import Path

import yaml

from multirag.db import conectar
from multirag.orchestration.retriever import buscar
from multirag.paths import EXPERIMENTS_DIR, PROJECT_ROOT


RAIZ_PROYECTO = PROJECT_ROOT
RUTA_BORRADOR = EXPERIMENTS_DIR / "golden_piloto_borrador.md"
RUTA_YAML = EXPERIMENTS_DIR / "golden_piloto_v0.yaml"

SEPARADOR_CABECERA = "\u00b7"
PATRON_UID = re.compile(r"\b[0-9a-f]{64}\b")
PATRON_PREGUNTA = re.compile(r"\*\*Pregunta:\*\*\s*(.+)")
PATRON_ANCLAS = re.compile(r"\*\*Chunks? candidatos?:\*\*\s*(.+)")

ESTRATO_PREDETERMINADO = "colision"
K_PREDETERMINADOS = (1, 3, 5, 10)


def huella_particion(conexion) -> str:
    """Same fingerprint recorded in the snapshot manifest. Print it to prove
    the probe ran against the frozen partition.
    [ES] La misma huella que quedo en el manifest del snapshot. Se imprime para
    probar que la sonda corrio sobre la particion congelada."""
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT encode(
                sha256(
                    convert_to(
                        string_agg(chunk_uid || '|' || silo, chr(10)
                                   ORDER BY chunk_uid),
                        'UTF8'
                    )
                ),
                'hex'
            )
            FROM chunks
            """
        )
        return cursor.fetchone()[0]


def cargar_items_borrador(ruta: Path, estrato: str) -> dict[str, dict]:
    """Read the markdown draft: id, question and anchored chunk_uids.
    [ES] Lee el borrador markdown: id, pregunta y chunk_uid anclados."""
    items: dict[str, dict] = {}

    for bloque in re.split(r"^## ", ruta.read_text(encoding="utf-8"), flags=re.M)[1:]:
        cabecera = bloque.split("\n")[0]
        partes = [p.strip() for p in cabecera.split(SEPARADOR_CABECERA)]

        if len(partes) < 2 or partes[1] != estrato:
            continue

        pregunta = PATRON_PREGUNTA.search(bloque)
        anclas = PATRON_ANCLAS.search(bloque)

        items[partes[0]] = {
            "pregunta": pregunta.group(1).strip() if pregunta else "",
            "anclas": PATRON_UID.findall(anclas.group(1)) if anclas else [],
        }

    return items


def cargar_items_yaml(ruta: Path, estrato: str) -> dict[str, dict]:
    """Read the formalized YAML items of the same stratum.
    [ES] Lee los items ya formalizados en YAML del mismo estrato."""
    items: dict[str, dict] = {}

    if not ruta.is_file():
        return items

    for item in yaml.safe_load(ruta.read_text(encoding="utf-8")) or []:
        if item.get("estrato") != estrato:
            continue

        items[item["id"]] = {
            "pregunta": item.get("pregunta", ""),
            "anclas": [
                evidencia["chunk_uid_snapshot"]
                for evidencia in item.get("evidencia", [])
                if evidencia.get("chunk_uid_snapshot")
            ],
        }

    return items


def unir_items(borrador: dict, yaml_items: dict) -> dict[str, dict]:
    """Merge both sources: the question from whichever has it, anchors unioned.
    [ES] Une las dos fuentes: la pregunta de la que la tenga, anclas unidas."""
    unidos: dict[str, dict] = {}

    for origen in (yaml_items, borrador):
        for identificador, datos in origen.items():
            destino = unidos.setdefault(
                identificador,
                {"pregunta": "", "anclas": []},
            )
            destino["pregunta"] = destino["pregunta"] or datos["pregunta"]

            for ancla in datos["anclas"]:
                if ancla not in destino["anclas"]:
                    destino["anclas"].append(ancla)

    return dict(sorted(unidos.items()))


def ubicacion_de_anclas(conexion, anclas: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Where the anchors physically live: silos, document_ids, missing uids.
    This is B1's oracle. It is derived from the snapshot, never guessed.
    [ES] Donde viven fisicamente las anclas: silos, document_id y uid ausentes.
    Este es el oraculo de B1. Sale del snapshot, nunca se adivina."""
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT chunk_uid, silo, document_id
            FROM chunks
            WHERE chunk_uid = ANY(%s)
            """,
            (anclas,),
        )
        filas = cursor.fetchall()

    encontrados = {uid for uid, _, _ in filas}

    return (
        sorted({silo for _, silo, _ in filas}),
        sorted({documento for _, _, documento in filas if documento}),
        [ancla for ancla in anclas if ancla not in encontrados],
    )


def ranking_b0(pregunta: str, k_maximo: int) -> list[str]:
    """Monolithic ranking: the whole corpus, no silo filter.
    [ES] Ranking monolitico: todo el corpus, sin filtro de silo."""
    return [
        resultado["chunk_uid"]
        for resultado in buscar(pregunta, silo=None, k=k_maximo)
    ]


def ranking_b1(pregunta: str, silos: list[str], k_maximo: int) -> list[str]:
    """Oracle ranking: only the silos holding the evidence, merged by similarity
    and TRUNCATED to k_maximo so both arms are compared over the same depth.
    [ES] Ranking del oraculo: solo los silos que contienen la evidencia, unidos
    por similitud y RECORTADO a k_maximo, para que los dos brazos se comparen
    sobre la misma profundidad."""
    candidatos = []

    for silo in silos:
        candidatos.extend(buscar(pregunta, silo=silo, k=k_maximo))

    candidatos.sort(key=lambda r: float(r["similitud"]), reverse=True)

    return [resultado["chunk_uid"] for resultado in candidatos][:k_maximo]


def ranking_b1d(pregunta: str, documentos: list[str], k_maximo: int) -> list[str]:
    """Document oracle: restrict to the document(s) holding the evidence.
    Upper bound of ANY content-based partition. Diagnostic only: nobody could
    deploy a retriever that already knows the answer's document.
    [ES] Oraculo de documento: restringe al documento o documentos que contienen
    la evidencia. Cota superior de CUALQUIER particion por contenido. Solo
    diagnostico: nadie puede desplegar un buscador que ya sabe el documento."""
    return [
        resultado["chunk_uid"]
        for resultado in buscar(pregunta, k=k_maximo, documentos=documentos)
    ][:k_maximo]


def posiciones_de_anclas(ranking: list[str], anclas: list[str]) -> list[int]:
    """1-based positions of EVERY anchored chunk found in the ranking.

    Hit@k needs only the first one; Recall@k needs all of them. Returning the
    full list keeps both metrics derivable from one pass.

    [ES] Posiciones (base 1) de TODAS las anclas halladas en el ranking.

    Hit@k solo necesita la primera; Recall@k necesita todas. Devolver la lista
    completa permite derivar las dos metricas de una sola pasada.
    """
    return [
        posicion
        for posicion, chunk_uid in enumerate(ranking, start=1)
        if chunk_uid in anclas
    ]


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.
    [ES] Construye el analizador de argumentos de linea de comandos."""
    parser = argparse.ArgumentParser(
        description=(
            "Sonda exploratoria B0 vs B1 sobre el snapshot congelado. "
            "Solo lectura."
        )
    )
    parser.add_argument(
        "--estrato",
        default=ESTRATO_PREDETERMINADO,
        help=f"Estrato a evaluar. Predeterminado: {ESTRATO_PREDETERMINADO}.",
    )
    parser.add_argument(
        "--k",
        type=int,
        nargs="+",
        default=list(K_PREDETERMINADOS),
        help=(
            "Valores de k a reportar. Predeterminados: "
            f"{' '.join(str(k) for k in K_PREDETERMINADOS)}."
        ),
    )
    return parser


NOMBRES_BRAZOS = ("B0", "B1", "B1d")


def main() -> None:
    """Run the probe over every arm and print Hit@k, Recall@k and MRR.
    [ES] Ejecuta la sonda sobre cada brazo e imprime Hit@k, Recall@k y MRR."""
    argumentos = construir_parser().parse_args()

    valores_k = sorted(set(argumentos.k))
    k_maximo = max(valores_k)

    items = unir_items(
        cargar_items_borrador(RUTA_BORRADOR, argumentos.estrato),
        cargar_items_yaml(RUTA_YAML, argumentos.estrato),
    )

    conexion = conectar()

    try:
        print(f"huella_particion: {huella_particion(conexion)}")
        print(f"estrato         : {argumentos.estrato}")
        print(f"items hallados  : {len(items)}")
        print(f"k evaluados     : {valores_k}")
        print()

        evaluables = []
        documentos_vistos = set()

        for identificador, datos in items.items():
            if not datos["anclas"] or not datos["pregunta"]:
                print(f"[SALTEADO] {identificador}: sin ancla o sin pregunta")
                continue

            silos, docs, ausentes = ubicacion_de_anclas(
                conexion,
                datos["anclas"],
            )

            if ausentes:
                print(
                    f"[SALTEADO] {identificador}: "
                    f"{len(ausentes)} ancla(s) no existen en el snapshot"
                )
                continue

            rankings = {
                "B0": ranking_b0(datos["pregunta"], k_maximo),
                "B1": ranking_b1(datos["pregunta"], silos, k_maximo),
                "B1d": ranking_b1d(datos["pregunta"], docs, k_maximo),
            }

            evaluables.append(
                {
                    "id": identificador,
                    "n_anclas": len(datos["anclas"]),
                    "silos": silos,
                    "docs": docs,
                    "pos": {
                        nombre: posiciones_de_anclas(ranking, datos["anclas"])
                        for nombre, ranking in rankings.items()
                    },
                }
            )
            documentos_vistos.update(docs)

            print(
                f"[OK] {identificador}  anclas={len(datos['anclas'])}  "
                f"silos={','.join(silos)}  docs={','.join(docs)}"
            )
    finally:
        conexion.close()

    if not evaluables:
        print("\nNo hay items evaluables.")
        return

    def primero(posiciones):
        return min(posiciones) if posiciones else None

    total = len(evaluables)

    print()
    encabezado = "item      anclas  " + "".join(
        f"rango_{nombre:<6}" for nombre in NOMBRES_BRAZOS
    )
    print(encabezado)
    print("-" * len(encabezado))

    for fila in evaluables:
        rangos = "".join(
            f"{str(primero(fila['pos'][nombre]) or '-'):<12}"
            for nombre in NOMBRES_BRAZOS
        )
        print(f"{fila['id']:9} {fila['n_anclas']:^6}  {rangos}")

    print()
    print(f"items evaluados      : {total}")
    print(f"documentos distintos : {len(documentos_vistos)}")

    print()
    print("  k   " + "".join(f"Hit@k {nombre:<7}" for nombre in NOMBRES_BRAZOS))
    print("-" * 50)

    for k in valores_k:
        celdas = ""
        for nombre in NOMBRES_BRAZOS:
            hits = sum(
                1 for f in evaluables if any(p <= k for p in f["pos"][nombre])
            )
            celdas += f"{hits:>3}/{total:<9}"
        print(f"{k:>3}   {celdas}")

    print()
    print("  k   " + "".join(f"Recall@k {nombre:<4}" for nombre in NOMBRES_BRAZOS))
    print("-" * 50)

    for k in valores_k:
        celdas = ""
        for nombre in NOMBRES_BRAZOS:
            recall = sum(
                len([p for p in f["pos"][nombre] if p <= k]) / f["n_anclas"]
                for f in evaluables
            ) / total
            celdas += f"{recall:>8.3f}     "
        print(f"{k:>3}   {celdas}")

    print()
    for nombre in NOMBRES_BRAZOS:
        mrr = sum(
            1 / primero(f["pos"][nombre]) if f["pos"][nombre] else 0.0
            for f in evaluables
        ) / total
        print(f"MRR (hasta k={k_maximo})   {nombre:<4} = {mrr:.3f}")

    print()
    print(
        "EXPLORATORIO. B1d es una cota diagnostica, no un sistema desplegable. "
        "Los items del estrato NO tienen distractores de colision verificados, "
        "asi que esto no juzga la hipotesis."
    )


if __name__ == "__main__":
    main()
