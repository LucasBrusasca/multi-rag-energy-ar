"""Compare silo-prototype policies on an already ingested pilot.

This diagnostic is read-only over PostgreSQL. Reference centroids exclude the
pilot documents, preventing each evaluated chunk from influencing its own
prototype. The report measures sensitivity and uncertainty; without curated
labels it must not be interpreted as classification accuracy.

[ES] Compara politicas de prototipos sobre un piloto ya ingerido.

El diagnostico solo lee PostgreSQL. Los centroides de referencia excluyen los
documentos piloto para impedir que cada chunk evaluado influya en su propio
prototipo. El informe mide sensibilidad e incertidumbre; sin etiquetas curadas
no debe interpretarse como exactitud de clasificacion.
"""

import argparse
import json
import math
import statistics
from pathlib import Path

from multirag.config import CLASIFICADOR_TEMP, EMBEDDING_MODEL, SILOS
from multirag.db import conectar
from multirag.ingestion.embedder import embed_query
from multirag.orchestration.clasificador import (
    _centroide_l2,
    _coseno,
    _softmax,
)


def validar_pesos(pesos: list[float]) -> list[float]:
    """Validate unique centroid weights in the closed interval [0, 1].

    [ES] Valida pesos unicos del centroide en el intervalo cerrado [0, 1].
    """
    if not pesos:
        raise ValueError("Debe indicarse al menos un peso de centroide.")

    if any(not math.isfinite(peso) or not 0.0 <= peso <= 1.0 for peso in pesos):
        raise ValueError("Cada peso de centroide debe estar entre 0 y 1.")

    if len(pesos) != len(set(pesos)):
        raise ValueError("Los pesos de centroide no pueden repetirse.")

    return sorted(pesos)


def combinar_cosenos(
    cosenos_centroides: dict[str, float],
    cosenos_descripciones: dict[str, float],
    peso_centroide: float,
) -> dict[str, float]:
    """Combine both semantic signals using an explicit convex weight.

    [ES] Combina ambas senales semanticas con un peso convexo explicito.
    """
    if set(cosenos_centroides) != set(cosenos_descripciones):
        raise ValueError("Las senales no contienen los mismos dominios.")

    validar_pesos([peso_centroide])

    return {
        silo: (
            peso_centroide * cosenos_centroides[silo]
            + (1.0 - peso_centroide) * cosenos_descripciones[silo]
        )
        for silo in cosenos_centroides
    }


def describir_distribucion(distribucion: dict[str, float]) -> dict[str, object]:
    """Return label, probabilities, normalized entropy and top-two margin.

    [ES] Devuelve etiqueta, probabilidades, entropia normalizada y margen.
    """
    orden = sorted(distribucion.items(), key=lambda item: -item[1])
    mejor, segundo = orden[:2]
    probabilidades = [probabilidad for _, probabilidad in orden]
    entropia = -sum(
        probabilidad * math.log(probabilidad)
        for probabilidad in probabilidades
        if probabilidad > 0
    ) / math.log(len(probabilidades))

    return {
        "silo": mejor[0],
        "scores": distribucion,
        "entropia_normalizada": entropia,
        "margen_top1_top2": mejor[1] - segundo[1],
    }


def clasificar_con_prototipos(
    vector: list[float],
    prototipos: dict[str, list[float]],
) -> tuple[dict[str, float], dict[str, object]]:
    """Classify one existing embedding against supplied prototypes.

    [ES] Clasifica un embedding existente contra los prototipos recibidos.
    """
    cosenos = {
        silo: _coseno(vector, prototipo)
        for silo, prototipo in prototipos.items()
    }
    distribucion = _softmax(cosenos, CLASIFICADOR_TEMP)
    return cosenos, describir_distribucion(distribucion)


def cargar_referencia(
    conexion,
    documentos_excluidos: list[str],
) -> tuple[dict[str, list[list[float]]], dict[str, int]]:
    """Load reference embeddings by silo, excluding pilot documents.

    [ES] Carga embeddings de referencia por silo, excluyendo el piloto.
    """
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT silo, embedding::text
            FROM chunks
            WHERE document_id IS NOT NULL
              AND document_id <> ALL(%s)
            ORDER BY silo, id
            """,
            (documentos_excluidos,),
        )
        filas = cursor.fetchall()

    por_silo: dict[str, list[list[float]]] = {silo: [] for silo in SILOS}

    for silo, vector_texto in filas:
        if silo in por_silo:
            por_silo[silo].append(json.loads(vector_texto))

    vacios = [silo for silo, vectores in por_silo.items() if not vectores]

    if vacios:
        raise ValueError(f"No hay referencia para estos silos: {vacios}")

    conteos = {silo: len(vectores) for silo, vectores in por_silo.items()}
    return por_silo, conteos


def cargar_piloto(
    conexion,
    documentos: list[str],
) -> list[dict[str, object]]:
    """Load pilot chunks and their stored ingestion assignments.

    [ES] Carga chunks piloto y sus asignaciones guardadas durante la ingesta.
    """
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                chunk_uid,
                document_id,
                fuente,
                titulo,
                contenido,
                silo,
                embedding::text
            FROM chunks
            WHERE document_id = ANY(%s)
            ORDER BY document_id, id
            """,
            (documentos,),
        )
        filas = cursor.fetchall()

    encontrados = {fila[2] for fila in filas}
    faltantes = [documento for documento in documentos if documento not in encontrados]

    if faltantes:
        raise ValueError(f"No se encontraron documentos piloto: {faltantes}")

    return [
        {
            "id_db": fila[0],
            "chunk_uid": fila[1],
            "document_id": fila[2],
            "fuente": fila[3],
            "titulo": fila[4],
            "contenido": fila[5],
            "silo_ingesta": fila[6],
            "embedding": json.loads(fila[7]),
        }
        for fila in filas
    ]


def resumir(resultados: list[dict[str, object]], politicas: list[str]) -> dict:
    """Summarize agreement and score dispersion without claiming accuracy.

    [ES] Resume acuerdo y dispersion sin afirmar exactitud.
    """
    resumen = {}

    for politica in politicas:
        margenes = [
            float(resultado["politicas"][politica]["margen_top1_top2"])
            for resultado in resultados
        ]
        entropias = [
            float(resultado["politicas"][politica]["entropia_normalizada"])
            for resultado in resultados
        ]
        coincidencias = sum(
            resultado["politicas"][politica]["silo"]
            == resultado["silo_ingesta"]
            for resultado in resultados
        )
        resumen[politica] = {
            "coincidencias_con_silo_ingesta": coincidencias,
            "desacuerdos_con_silo_ingesta": len(resultados) - coincidencias,
            "margen_mediano": statistics.median(margenes),
            "entropia_mediana": statistics.median(entropias),
        }

    return resumen


def construir_informe(
    documentos: list[str],
    pesos: list[float],
) -> dict[str, object]:
    """Build the complete read-only ablation report.

    [ES] Construye el informe completo de ablacion de solo lectura.
    """
    pesos = validar_pesos(pesos)
    conexion = conectar()

    try:
        referencia, conteos_referencia = cargar_referencia(conexion, documentos)
        piloto = cargar_piloto(conexion, documentos)
    finally:
        conexion.close()

    prototipos_centroides = {
        silo: _centroide_l2(vectores)
        for silo, vectores in referencia.items()
    }
    prototipos_descripciones = {
        silo: embed_query(descripcion)
        for silo, descripcion in SILOS.items()
    }
    politicas = ["centroides", "descripciones"] + [
        f"hibrido_peso_centroide_{peso:g}"
        for peso in pesos
    ]
    resultados = []

    for chunk in piloto:
        vector = chunk.pop("embedding")
        cosenos_centroides, resultado_centroides = clasificar_con_prototipos(
            vector,
            prototipos_centroides,
        )
        cosenos_descripciones, resultado_descripciones = clasificar_con_prototipos(
            vector,
            prototipos_descripciones,
        )
        resultados_politicas = {
            "centroides": resultado_centroides,
            "descripciones": resultado_descripciones,
        }

        for peso in pesos:
            nombre = f"hibrido_peso_centroide_{peso:g}"
            cosenos_hibridos = combinar_cosenos(
                cosenos_centroides,
                cosenos_descripciones,
                peso,
            )
            resultados_politicas[nombre] = describir_distribucion(
                _softmax(cosenos_hibridos, CLASIFICADOR_TEMP)
            )

        resultados.append({**chunk, "politicas": resultados_politicas})

    return {
        "estado": "exploratorio_sin_verdad_curada",
        "restriccion_interpretativa": (
            "Los acuerdos y desacuerdos miden sensibilidad a la politica de "
            "prototipos; no miden exactitud."
        ),
        "documentos_piloto": documentos,
        "documentos_excluidos_de_centroides": documentos,
        "modelo_embedding": EMBEDDING_MODEL,
        "temperatura": CLASIFICADOR_TEMP,
        "pesos_hibridos": pesos,
        "conteos_referencia_por_silo": conteos_referencia,
        "cantidad_chunks_piloto": len(resultados),
        "resumen": resumir(resultados, politicas),
        "chunks": resultados,
    }


def guardar_informe(informe: dict[str, object], ruta_salida: Path) -> Path:
    """Persist the report atomically without overwriting an existing run.

    [ES] Persiste el informe atomicamente sin sobrescribir una corrida previa.
    """
    ruta_salida = ruta_salida.resolve()

    if ruta_salida.exists():
        raise FileExistsError(f"El informe ya existe: {ruta_salida}")

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_temporal = ruta_salida.with_name(f".{ruta_salida.name}.tmp")

    try:
        ruta_temporal.write_text(
            json.dumps(informe, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        ruta_temporal.replace(ruta_salida)
    finally:
        if ruta_temporal.exists():
            ruta_temporal.unlink()

    return ruta_salida


def construir_parser() -> argparse.ArgumentParser:
    """Build the explicit command-line contract.

    [ES] Construye el contrato explicito de linea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Compara prototipos sobre chunks piloto sin modificar PostgreSQL."
        )
    )
    parser.add_argument(
        "--document-id",
        action="append",
        required=True,
        help="Documento piloto; se puede repetir.",
    )
    parser.add_argument(
        "--peso-centroide",
        action="append",
        type=float,
        required=True,
        help=(
            "Peso experimental del centroide en la mezcla convexa; "
            "se puede repetir."
        ),
    )
    parser.add_argument("--salida", type=Path, required=True)
    return parser


def main() -> None:
    """Run and persist the requested pilot ablation.

    [ES] Ejecuta y persiste la ablacion piloto solicitada.
    """
    parser = construir_parser()
    argumentos = parser.parse_args()

    if len(argumentos.document_id) != len(set(argumentos.document_id)):
        parser.error("Los document_id no pueden repetirse.")

    try:
        informe = construir_informe(
            documentos=argumentos.document_id,
            pesos=argumentos.peso_centroide,
        )
        salida = guardar_informe(informe, argumentos.salida)
    except (FileExistsError, FileNotFoundError, ValueError) as error:
        parser.error(str(error))

    print(f"chunks evaluados : {informe['cantidad_chunks_piloto']}")
    print("referencia        : centroides sin documentos piloto")
    print("verdad curada     : no disponible")
    print()

    for politica, resumen in informe["resumen"].items():
        print(
            f"{politica}: "
            f"desacuerdos={resumen['desacuerdos_con_silo_ingesta']} "
            f"margen_mediano={resumen['margen_mediano']:.3f} "
            f"entropia_mediana={resumen['entropia_mediana']:.3f}"
        )

    print()
    print(f"informe           : {salida}")
    print("PostgreSQL        : no modificado")


if __name__ == "__main__":
    main()
