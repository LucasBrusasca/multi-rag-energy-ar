import sys
from pathlib import Path
from psycopg2.extras import execute_values
from db import conectar
from chunker import chunk_by_structure
from embedder import embed_chunks


def guardar_chunks(chunks: list[dict], conexion, fuente: str, silo: str) -> int:
    """Inserta los chunks en un batch. Idempotente: borra los de esa fuente antes."""
    filas = [
       (
          silo,
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
                "INSERT INTO chunks (silo, titulo,contenido,embedding,fuente) VALUES %s",
                filas,
                template="(%s,%s,%s,%s::vector, %s)"
            )
    return len(filas)


def cargar_documento(ruta_md: str, fuente: str, silo: str) -> None:
    """Pipeline completo: lee el .md -> chunk -> embed -> persiste en Postgres."""
    texto = Path(ruta_md).read_text(encoding="utf-8")
    chunks = chunk_by_structure(texto, source=fuente)
    chunks = embed_chunks(chunks)

    conexion = conectar()
    try:
        n= guardar_chunks(chunks, conexion, fuente, silo)
        print(f"OK: {n} chunks de '{fuente}' (silo: {silo}) guardados.")
    finally:
        conexion.close()
    

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python src/ingestion/pipeline.py <ruta_al_md> <silo>")
        sys.exit(1)
    ruta = Path(sys.argv[1])
    silo = sys.argv[2]
    cargar_documento(ruta_md=str(ruta),fuente=ruta.stem,silo=silo)