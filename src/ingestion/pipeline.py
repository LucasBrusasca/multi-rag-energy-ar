import sys
from pathlib import Path
from psycopg2.extras import execute_values
from db import conectar
from chunker import chunk_by_structure
from embedder import embed_chunks
import json
from clasificador import clasificar


def guardar_chunks(chunks: list[dict], conexion, fuente: str, silo: str, silo_scores: dict) -> int:
    """Inserta los chunks en un batch. Idempotente: borra los de esa fuente antes."""
    scores_json = json.dumps(silo_scores)
    filas = [
       (
          silo,
          scores_json,
          c["title"],
          c["content"],
          "[" + ",".join(map(str,c["embedding"])) + "]",
          fuente, 
       )
        for c in chunks
    ]
    with conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM chunks WHERE fuente = %s", (fuente,))
            execute_values(
                cursor,
                "INSERT INTO chunks (silo, silo_scores, titulo, contenido, embedding,fuente) VALUES %s",
                filas,
                template="(%s,%s::jsonb, %s, %s, %s::vector, %s)"
            )
    return len(filas)


def cargar_documento(ruta_md: str, fuente: str) -> None:
    """Pipeline completo: lee el .md -> clasifica -> chunk -> embed -> persiste."""
    texto = Path(ruta_md).read_text(encoding="utf-8")
    
    clasif = clasificar(texto)
    silo = clasif["silo"]
    silo_scores = clasif["silo_scores"]
    print(f"Clasificado como '{silo}' -> {silo_scores}")
    
    chunks = chunk_by_structure(texto, source=fuente)
    chunks = embed_chunks(chunks)

    conexion = conectar()
    try:
        n= guardar_chunks(chunks, conexion, fuente, silo, silo_scores)
        print(f"OK: {n} chunks de '{fuente}' (silo: {silo}) guardados.")
    finally:
        conexion.close()
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/ingestion/pipeline.py <ruta_al_md>")
        sys.exit(1)
    ruta = Path(sys.argv[1])
    cargar_documento(ruta_md=str(ruta),fuente=ruta.stem)