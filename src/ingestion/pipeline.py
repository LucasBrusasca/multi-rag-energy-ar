import sys
from pathlib import Path
from psycopg2.extras import execute_values
from db import conectar
from chunker import chunk_with_docling
from embedder import embed_chunks
import json
from clasificador import clasificar_vector


def guardar_chunks(chunks: list[dict], conexion, fuente: str) -> int:
    """Batch-insert chunks, each with ITS OWN silo. Idempotent: deletes that source first.
    [ES] Inserta los chunks en batch, cada uno con SU PROPIO silo. Idempotente: borra los de esa fuente antes."""
    filas = [
       (
          c["silo"],
          json.dumps(c["silo_scores"]),
          c["title"],
          c["content"],
          "[" + ",".join(map(str,c["embedding"])) + "]",
          fuente,
          c["hierarchy"],
       )
        for c in chunks
    ]
    with conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM chunks WHERE fuente = %s", (fuente,))
            execute_values(
                cursor,
                "INSERT INTO chunks (silo, silo_scores, titulo, contenido, embedding, fuente, hierarchy) VALUES %s",
                filas,
                template="(%s,%s::jsonb, %s, %s, %s::vector, %s,%s::text[])"
            )
    return len(filas)


def cargar_documento(ruta: str, fuente: str) -> None:
    """Full pipeline: file -> Docling chunk -> embed -> classify -> persist.
    [ES] Pipeline completo: archivo -> chunk con Docling -> embed -> clasifica cada chunk -> persiste."""
    from collections import Counter
    
    chunks = chunk_with_docling(ruta, source=fuente)
    chunks = embed_chunks(chunks)

    for c in chunks:
        clasif = clasificar_vector(c["embedding"])
        c["silo"] = clasif["silo"]
        c["silo_scores"] = clasif["silo_scores"]

    reparto = Counter(c["silo"] for c in chunks)
    print(f"Reparto por silo: {dict(reparto)}")

    conexion = conectar()
    try:
        n = guardar_chunks(chunks, conexion, fuente)
        print(f"OK: {n} chunks de '{fuente}' guardados.")
    finally:
        conexion.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/ingestion/pipeline.py <ruta_al_md>")
        sys.exit(1)
    ruta = Path(sys.argv[1])
    cargar_documento(ruta=str(ruta),fuente=ruta.stem)