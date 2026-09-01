"""Select a stratified sample of chunks for independent human labelling.

Two blocks: a random draw for an unbiased accuracy estimate, and an
uncertainty draw to learn the decision boundary. The labelling sheet never
exposes the classifier's own prediction.

[ES] Selecciona una muestra estratificada de chunks para etiquetado humano
independiente.

Dos bloques: un sorteo aleatorio para estimar exactitud sin sesgo, y un bloque
por incertidumbre para aprender la frontera de decisión. La planilla de
etiquetado nunca expone la predicción del propio clasificador.
"""

import argparse
import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

from multirag.config import SILOS
from multirag.db import conectar


VERSION_MUESTRA = "muestra-etiquetado-v1"

COLUMNAS_ETIQUETADO = (
    "orden",
    "chunk_uid",
    "titulo",
    "contenido",
    "materialidad_humana",
    "dominios_humano",
    "observaciones",
)

COLUMNAS_METADATOS = (
    "chunk_uid",
    "bloque",
    "entropia",
    "margen",
    "document_id",
    "silo_persistido",
    "silo_scores",
)


def calcular_entropia(distribucion: dict[str, float]) -> float:
    """Return the Shannon entropy normalised to [0, 1].

    [ES] Devuelve la entropía de Shannon normalizada a [0, 1].
    """
    valores = [
        p for p in distribucion.values()
        if p > 0
    ]

    if len(valores) <= 1:
        return 0.0

    entropia = -sum(
        p * math.log(p) for p in valores
    )

    return entropia / math.log(len(SILOS))


def calcular_margen(distribucion: dict[str, float]) -> float:
    """Return the gap between the top two probabilities.

    [ES] Devuelve la diferencia entre las dos probabilidades mayores.
    """
    ordenados = sorted(
        distribucion.values(),
        reverse=True,
    )

    if len(ordenados) < 2:
        return 1.0

    return ordenados[0] - ordenados[1]


def normalizar_scores(crudo: Any) -> dict[str, float] | None:
    """Return silo_scores as a dict of floats, or None if unusable.

    [ES] Devuelve silo_scores como diccionario de flotantes, o None.
    """
    if crudo is None:
        return None

    distribucion = (
        json.loads(crudo)
        if isinstance(crudo, str)
        else crudo
    )

    if not isinstance(distribucion, dict) or not distribucion:
        return None

    return {
        silo: float(valor)
        for silo, valor in distribucion.items()
    }


def cargar_chunks() -> list[dict[str, Any]]:
    """Read every chunk with a usable score distribution.

    [ES] Lee todos los chunks con una distribución utilizable.
    """
    conexion = conectar()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT chunk_uid, titulo, contenido,
                       document_id, silo, silo_scores
                FROM chunks
                WHERE chunk_uid IS NOT NULL
                ORDER BY chunk_uid
                """
            )
            filas = cursor.fetchall()
    finally:
        conexion.close()

    chunks = []
    descartados = 0

    for (
        chunk_uid,
        titulo,
        contenido,
        document_id,
        silo,
        scores_crudo,
    ) in filas:
        distribucion = normalizar_scores(scores_crudo)

        if distribucion is None:
            descartados += 1
            continue

        chunks.append(
            {
                "chunk_uid": chunk_uid,
                "titulo": titulo or "",
                "contenido": contenido or "",
                "document_id": document_id,
                "silo_persistido": silo,
                "silo_scores": distribucion,
                "entropia": calcular_entropia(distribucion),
                "margen": calcular_margen(distribucion),
            }
        )

    if descartados:
        print(
            f"Advertencia: {descartados} chunks sin silo_scores "
            "utilizables quedaron fuera de la selección."
        )

    return chunks


def seleccionar(
    chunks: list[dict[str, Any]],
    n_aleatorio: int,
    n_incierto: int,
    semilla: int,
) -> list[dict[str, Any]]:
    """Draw the random block first, then the uncertainty block.

    [ES] Sortea primero el bloque aleatorio y después el incierto.
    """
    if len(chunks) < n_aleatorio + n_incierto:
        raise ValueError(
            "El corpus no alcanza para la muestra pedida: "
            f"{len(chunks)} chunks disponibles."
        )

    sorteador = random.Random(semilla)

    aleatorios = sorteador.sample(chunks, n_aleatorio)
    ya_elegidos = {c["chunk_uid"] for c in aleatorios}

    restantes = [
        c for c in chunks
        if c["chunk_uid"] not in ya_elegidos
    ]
    restantes.sort(
        key=lambda c: (-c["entropia"], c["chunk_uid"]),
    )

    inciertos = restantes[:n_incierto]

    for chunk in aleatorios:
        chunk["bloque"] = "aleatorio"

    for chunk in inciertos:
        chunk["bloque"] = "incierto"

    muestra = aleatorios + inciertos
    sorteador.shuffle(muestra)

    return muestra


def calcular_sha256(ruta: Path) -> str:
    """Return the SHA-256 digest of a file.

    [ES] Devuelve la huella SHA-256 de un archivo.
    """
    huella = hashlib.sha256()

    with ruta.open("rb") as archivo:
        for bloque in iter(
            lambda: archivo.read(1024 * 1024),
            b"",
        ):
            huella.update(bloque)

    return huella.hexdigest()


def guardar_csv(
    filas: list[dict[str, Any]],
    columnas: tuple[str, ...],
    ruta: Path,
) -> Path:
    """Write a CSV without overwriting an existing file.

    [ES] Escribe un CSV sin sobrescribir un archivo existente.
    """
    ruta_resuelta = ruta.resolve()

    if ruta_resuelta.exists():
        raise FileExistsError(
            "La salida ya existe y no será sobrescrita: "
            f"{ruta_resuelta}"
        )

    ruta_resuelta.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with ruta_resuelta.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=list(columnas),
        )
        escritor.writeheader()
        escritor.writerows(filas)

    return ruta_resuelta


def informar_distribucion(
    muestra: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
) -> None:
    """Print the diagnostics that make the sample interpretable.

    [ES] Imprime los diagnósticos que hacen interpretable la muestra.
    """
    entropias = sorted(c["entropia"] for c in chunks)
    n = len(entropias)

    def percentil(p: float) -> float:
        return entropias[min(int(n * p), n - 1)]

    print()
    print(f"Chunks evaluados      : {n}")
    print(
        "Entropía p25/p50/p75  : "
        f"{percentil(0.25):.3f} / "
        f"{percentil(0.50):.3f} / "
        f"{percentil(0.75):.3f}"
    )

    documentos: dict[str, int] = {}

    for chunk in muestra:
        clave = chunk["document_id"] or "SIN_DOCUMENT_ID"
        documentos[clave] = documentos.get(clave, 0) + 1

    print(f"Documentos en la muestra: {len(documentos)}")

    for documento, cuenta in sorted(
        documentos.items(),
        key=lambda par: -par[1],
    ):
        print(f"  {documento}: {cuenta}")


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.

    [ES] Construye la interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Selecciona una muestra estratificada de chunks para "
            "etiquetado humano independiente."
        )
    )
    parser.add_argument(
        "--salida",
        type=Path,
        required=True,
        help="Ruta del CSV de etiquetado (archivo nuevo).",
    )
    parser.add_argument(
        "--semilla",
        type=int,
        required=True,
        help="Semilla del sorteo. Queda registrada en el informe.",
    )
    parser.add_argument(
        "--aleatorios",
        type=int,
        default=50,
        help="Tamaño del bloque aleatorio. Por defecto: 50.",
    )
    parser.add_argument(
        "--inciertos",
        type=int,
        default=50,
        help="Tamaño del bloque incierto. Por defecto: 50.",
    )
    return parser


def main() -> None:
    """Select, report and persist the labelling sample.

    [ES] Selecciona, informa y guarda la muestra de etiquetado.
    """
    argumentos = construir_parser().parse_args()

    if argumentos.aleatorios < 1 or argumentos.inciertos < 1:
        raise SystemExit(
            "ERROR: ambos bloques deben tener al menos un elemento."
        )

    ruta_etiquetado = argumentos.salida
    ruta_metadatos = ruta_etiquetado.with_name(
        f"{ruta_etiquetado.stem}_metadatos.csv"
    )

    for ruta in (ruta_etiquetado, ruta_metadatos):
        if ruta.resolve().exists():
            raise SystemExit(
                f"ERROR: la salida ya existe: {ruta.resolve()}"
            )

    chunks = cargar_chunks()

    try:
        muestra = seleccionar(
            chunks=chunks,
            n_aleatorio=argumentos.aleatorios,
            n_incierto=argumentos.inciertos,
            semilla=argumentos.semilla,
        )
    except ValueError as error:
        raise SystemExit(f"ERROR: {error}") from error

    filas_etiquetado = [
        {
            "orden": numero,
            "chunk_uid": chunk["chunk_uid"],
            "titulo": chunk["titulo"],
            "contenido": chunk["contenido"],
            "materialidad_humana": "",
            "dominios_humano": "",
            "observaciones": "",
        }
        for numero, chunk in enumerate(muestra, start=1)
    ]

    filas_metadatos = [
        {
            "chunk_uid": chunk["chunk_uid"],
            "bloque": chunk["bloque"],
            "entropia": round(chunk["entropia"], 6),
            "margen": round(chunk["margen"], 6),
            "document_id": chunk["document_id"],
            "silo_persistido": chunk["silo_persistido"],
            "silo_scores": json.dumps(
                chunk["silo_scores"],
                ensure_ascii=False,
                sort_keys=True,
            ),
        }
        for chunk in muestra
    ]

    salida_etiquetado = guardar_csv(
        filas=filas_etiquetado,
        columnas=COLUMNAS_ETIQUETADO,
        ruta=ruta_etiquetado,
    )
    salida_metadatos = guardar_csv(
        filas=filas_metadatos,
        columnas=COLUMNAS_METADATOS,
        ruta=ruta_metadatos,
    )

    informar_distribucion(muestra, chunks)

    print()
    print(f"Versión             : {VERSION_MUESTRA}")
    print(f"Semilla             : {argumentos.semilla}")
    print(
        "Bloques             : "
        f"{argumentos.aleatorios} aleatorios + "
        f"{argumentos.inciertos} inciertos"
    )
    print(f"Planilla            : {salida_etiquetado}")
    print(f"SHA-256 planilla    : {calcular_sha256(salida_etiquetado)}")
    print(f"Metadatos (no mirar): {salida_metadatos}")
    print("PostgreSQL          : solo lectura")


if __name__ == "__main__":
    main()