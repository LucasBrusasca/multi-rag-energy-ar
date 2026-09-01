"""Two-stage retrieval: find the DOCUMENT semantically, then search inside it.

B1d showed that restricting to the evidence's document is the only filter that
helps, but it is an oracle. This measures how much of that gain a deployable
document-level index recovers, scoring documents two ways:

  centroide -> L2 centroid of the document's chunk embeddings (its "average
               meaning"; expected to blur on multi-domain documents)
  maximo    -> the document scores as high as its single best chunk

Read-only over the frozen snapshot.

[ES] Recuperacion en dos niveles: primero el DOCUMENTO, despues adentro.

B1d mostro que restringir al documento de la evidencia es el unico filtro que
ayuda, pero es un oraculo. Esto mide cuanto de esa ganancia recupera un indice
de documentos desplegable, puntuando documentos de dos formas:

  centroide -> centroide L2 de los embeddings del documento (su "significado
               promedio"; se espera que se desdibuje en documentos multidominio)
  maximo    -> el documento vale lo que su mejor chunk
"""

import json

import numpy as np

from multirag.db import conectar
from multirag.evaluation.sonda_b0_b1 import (
        ESTRATO_PREDETERMINADO,
        RUTA_BORRADOR,
        RUTA_YAML,
        cargar_items_borrador,
        cargar_items_yaml,
        posiciones_de_anclas,
        ranking_b0,
        ubicacion_de_anclas,
        unir_items,
)
from multirag.ingestion.embedder import embed_query
from multirag.orchestration.clasificador import _centroide_l2, _coseno
from multirag.orchestration.retriever import buscar

VALORES_N = (1, 2, 3)
VALORES_K = (1, 3, 10)
K_MAXIMO = max(VALORES_K)


def cargar_embeddings_por_documento(conexion) -> dict:
    """Read every chunk embedding, grouped by its document.
    [ES] Lee todos los embeddings de chunks, agrupados por documento."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT document_id, embedding::text FROM chunks "
            "WHERE document_id IS NOT NULL"
        )
        filas = cursor.fetchall()

    por_documento = {}

    for document_id, vector in filas:
        por_documento.setdefault(document_id, []).append(json.loads(vector))

    return por_documento


def ranking_documentos(vector_consulta, embeddings: dict, modo: str) -> list:
    """Rank documents for a query. modo = 'centroide' | 'maximo'.
    [ES] Ordena documentos para una consulta. modo = 'centroide' | 'maximo'."""
    puntajes = []

    for document_id, vectores in embeddings.items():
        if modo == "centroide":
            puntaje = _coseno(vector_consulta, _centroide_l2(vectores))
        else:
            puntaje = max(_coseno(vector_consulta, v) for v in vectores)

        puntajes.append((puntaje, document_id))

    puntajes.sort(reverse=True)

    return [document_id for _, document_id in puntajes]


def main() -> None:
    """Measure document routing and the retrieval it enables.
    [ES] Mide el ruteo de documentos y la recuperacion que habilita."""
    items = unir_items(
        cargar_items_borrador(RUTA_BORRADOR, ESTRATO_PREDETERMINADO),
        cargar_items_yaml(RUTA_YAML, ESTRATO_PREDETERMINADO),
    )

    conexion = conectar()

    try:
        embeddings = cargar_embeddings_por_documento(conexion)
        print(f"documentos indexados: {len(embeddings)}")

        # Los centroides se calculan una sola vez, no por consulta.
        centroides = {
            document_id: _centroide_l2(vectores)
            for document_id, vectores in embeddings.items()
        }

        resultados = []

        for identificador, datos in items.items():
            if not datos["anclas"] or not datos["pregunta"]:
                continue

            _, documentos, ausentes = ubicacion_de_anclas(
                conexion, datos["anclas"]
            )

            if ausentes:
                continue

            vector = embed_query(datos["pregunta"])

            orden = {
                "centroide": [
                    d for _, d in sorted(
                        ((_coseno(vector, c), d) for d, c in centroides.items()),
                        reverse=True,
                    )
                ],
                "maximo": ranking_documentos(vector, embeddings, "maximo"),
            }

            fila = {
                "id": identificador,
                "docs_evidencia": documentos,
                "B0": posiciones_de_anclas(
                    ranking_b0(datos["pregunta"], K_MAXIMO), datos["anclas"]
                ),
            }

            for modo in ("centroide", "maximo"):
                fila[f"rango_doc_{modo}"] = min(
                    (orden[modo].index(d) + 1 for d in documentos
                     if d in orden[modo]),
                    default=None,
                )

                for n in VALORES_N:
                    recuperados = [
                        registro["chunk_uid"]
                        for registro in buscar(
                            datos["pregunta"],
                            k=K_MAXIMO,
                            documentos=orden[modo][:n],
                        )
                    ]
                    fila[f"{modo}_N{n}"] = posiciones_de_anclas(
                        recuperados, datos["anclas"]
                    )

            resultados.append(fila)
            print(
                f"[OK] {identificador}  doc correcto en puesto: "
                f"centroide={fila['rango_doc_centroide']} "
                f"maximo={fila['rango_doc_maximo']}"
            )
    finally:
        conexion.close()

    total = len(resultados)

    if not total:
        print("No hay items evaluables.")
        return

    print()
    print("--- ruteo de documentos: el documento de la evidencia esta en el top-N ---")

    for modo in ("centroide", "maximo"):
        linea = []

        for n in VALORES_N:
            aciertos = sum(
                1 for f in resultados
                if f[f"rango_doc_{modo}"] and f[f"rango_doc_{modo}"] <= n
            )
            linea.append(f"top-{n}: {aciertos}/{total}")

        print(f"   {modo:10} " + "   ".join(linea))

    print()
    print("--- Hit@k de la recuperacion resultante ---")
    print("  k   B0      centroide N1  N2    N3      maximo N1  N2    N3")
    print("-" * 66)

    for k in VALORES_K:
        celdas = [
            f"{sum(1 for f in resultados if any(p <= k for p in f['B0'])):>2}/{total:<4}"
        ]

        for modo in ("centroide", "maximo"):
            for n in VALORES_N:
                aciertos = sum(
                    1 for f in resultados
                    if any(p <= k for p in f[f"{modo}_N{n}"])
                )
                celdas.append(f"{aciertos:>2}/{total:<4}")

        print(f"{k:>3}   " + "  ".join(celdas))

    print()
    print("Referencia del oraculo B1d medido antes: 10/14 en Hit@1, 12/14 en Hit@3.")
    print("EXPLORATORIO. 24 documentos: elegir 1 entre 24 es mucho mas facil que")
    print("entre 15.000, asi que estos numeros son optimistas.")


if __name__ == "__main__":
    main()
