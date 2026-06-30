import sys
from db import conectar
from embedder import embed_query
from config import RETRIEVAL_TOP_K


def buscar(pregunta: str, silo: str = None, k: int = RETRIEVAL_TOP_K) -> list[dict]:
    """Retrieve the top-k chunks most similar to the question (cosine similarity).
        If 'silo' is given, search only within that domain (segregated retrieval);
        If 'silo' is None, search across all silos (monolithic baseline)"""
    vector = embed_query(pregunta)
    vector_literal = "[" + ",".join(map(str,vector)) + "]"

    filtro = "WHERE silo = %s" if silo else ""

    params = [vector_literal] + ([silo] if silo else []) + [vector_literal, k]

    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                   f"""
                    SELECT silo, titulo, contenido, fuente,
                        1 - (embedding <=> %s::vector) AS similitud
                    FROM chunks
                    {filtro}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    params
            )
            filas = cursor.fetchall()
    finally:
            conexion.close()

    return [
            {"silo": si, "titulo": t, "contenido": c, "fuente": f, "similitud": s}
            for (si, t,c,f,s) in filas
    ]


if __name__ == "__main__":
    from config import SILOS
    args = sys.argv[1:]
    if not args:
         print('Uso: python src/ingestion/retriever.py [<silo>] "<pregunta>"')
         sys.exit(1)
    if args[0] in SILOS:
         silo, pregunta = args[0], " ".join(args[1:])
    else:
         silo, pregunta = None, " ".join(args)
    modo = f"silo: {silo}" if silo else "MONOLÍTICO (todos los silos)"
    print(f"[{modo}] Pregunta: {pregunta}\n")
    for r in buscar(pregunta, silo):
         print(f"[sim {r['similitud']:.3f}] ({r['silo']}) {r['titulo']} ({r['fuente']})")
         print(r["contenido"][:200]); print("-" * 40)