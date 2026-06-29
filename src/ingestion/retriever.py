import sys
from db import conectar
from embedder import embed_query
from config import RETRIEVAL_TOP_K


def buscar(pregunta: str, silo: str ,k: int = RETRIEVAL_TOP_K) -> list[dict]:
    """Busca los k chunks más parecidos a la pregunta DENTRO de un silo."""
    vector = embed_query(pregunta)
    vector_literal = "[" + ",".join(map(str,vector)) + "]"

    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                    """
                    SELECT titulo, contenido, fuente,
                        1 - (embedding <=> %s::vector) AS similitud
                    FROM chunks
                    WHERE silo = %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (vector_literal,silo, vector_literal, k)
            )
            filas = cursor.fetchall()
    finally:
            conexion.close()

    return [
            {"titulo": t, "contenido": c, "fuente": f, "similitud": s}
            for (t,c,f,s) in filas
    ]


if __name__ == "__main__":
    if len(sys.argv) < 3:
         print('Uso: python src/ingestion/retriever.py <silo> "<tu pregunta>"')
         sys.exit(1)
    silo = sys.argv[1]
    
    pregunta = " ".join(sys.argv[2:])
    print(f"[silo: {silo}] Pregunta: {pregunta}\n")
    for r in buscar(pregunta, silo):
         print(f"[sim {r['similitud']:.3f}] {r['titulo']} ({r['fuente']})")
         print(r["contenido"][:200])
         print("-" * 40)