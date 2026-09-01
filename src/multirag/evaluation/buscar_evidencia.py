"""Search the frozen corpus for the literal evidence of a Golden item.

Read-only. Accent- and case-insensitive matching happens in Python so the
database is never modified: the snapshot is frozen.

[ES] Busca en el corpus congelado la evidencia literal de un item del Golden.

Solo lectura. La comparacion sin tildes ni mayusculas se hace en Python para
no modificar la base: el snapshot esta congelado.
"""

import argparse
import unicodedata

from multirag.db import conectar


CARACTERES_CONTEXTO = 140


def normalizar(texto: str) -> str:
    """Lowercase, accent-free, and LENGTH-PRESERVING (one char in, one out).
    [ES] Minusculas y sin tildes, conservando la longitud."""
    return "".join(
        unicodedata.normalize("NFD", caracter)[0]
        for caracter in texto.lower()
    )


def compactar(texto: str) -> tuple[str, list[int]]:
    """Keep only letters and digits, plus a map back to the original offsets.

    The extraction spaces out punctuation ("$ 140 . 000 . 000"), so a literal
    search for "$140.000.000" would miss real evidence. Comparing only the
    alphanumeric skeleton removes that whole class of false negatives.

    [ES] Deja solo letras y numeros, con un mapa a las posiciones originales.

    La extraccion separa la puntuacion con espacios ("$ 140 . 000 . 000"), asi
    que buscar "$140.000.000" literal perderia evidencia real. Comparar solo el
    esqueleto alfanumerico elimina toda esa clase de falsos negativos.
    """
    caracteres: list[str] = []
    posiciones: list[int] = []

    for posicion, caracter in enumerate(normalizar(texto)):
        if caracter.isalnum():
            caracteres.append(caracter)
            posiciones.append(posicion)

    return "".join(caracteres), posiciones


def leer_chunks(fuente: str | None) -> list[tuple]:
    """Read the chunks, optionally restricted to one source.
    [ES] Lee los chunks, opcionalmente restringidos a una fuente."""
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            if fuente:
                cursor.execute(
                    """
                    SELECT chunk_uid, silo, fuente, titulo, contenido
                    FROM chunks
                    WHERE fuente ILIKE %s
                    ORDER BY chunk_uid
                    """,
                    (f"%{fuente}%",),
                )
            else:
                cursor.execute(
                    """
                    SELECT chunk_uid, silo, fuente, titulo, contenido
                    FROM chunks
                    ORDER BY chunk_uid
                    """
                )
            return cursor.fetchall()
    finally:
        conexion.close()


def buscar(texto: str, fuente: str | None) -> list[dict]:
    """Return every chunk containing the fragment, ignoring accents, case and
    punctuation, with an excerpt taken from the ORIGINAL text.
    [ES] Devuelve los chunks que contienen el fragmento, ignorando tildes,
    mayusculas y puntuacion, con un extracto tomado del texto ORIGINAL."""
    aguja, _ = compactar(texto)

    if not aguja:
        raise ValueError(
            "El texto a buscar no tiene ninguna letra ni numero."
        )

    hallazgos = []

    for chunk_uid, silo, fte, titulo, contenido in leer_chunks(fuente):
        pajar, posiciones = compactar(contenido)
        encontrado = pajar.find(aguja)

        if encontrado < 0:
            continue

        inicio = posiciones[encontrado]
        fin = posiciones[encontrado + len(aguja) - 1] + 1

        desde = max(0, inicio - CARACTERES_CONTEXTO)
        hasta = fin + CARACTERES_CONTEXTO

        hallazgos.append(
            {
                "chunk_uid": chunk_uid,
                "silo": silo,
                "fuente": fte,
                "titulo": titulo,
                "extracto": " ".join(contenido[desde:hasta].split()),
            }
        )

    return hallazgos


def mostrar_chunk(chunk_uid: str) -> None:
    """Print one chunk in full, to verify literal correspondence.
    [ES] Imprime un chunk completo, para verificar la correspondencia literal."""
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT chunk_uid, silo, fuente, document_id, titulo, contenido
                FROM chunks
                WHERE chunk_uid = %s
                """,
                (chunk_uid,),
            )
            fila = cursor.fetchone()
    finally:
        conexion.close()

    if fila is None:
        print(f"No existe el chunk {chunk_uid} en el snapshot.")
        return

    uid, silo, fuente, document_id, titulo, contenido = fila

    print(f"chunk_uid   : {uid}")
    print(f"silo        : {silo}")
    print(f"fuente      : {fuente}")
    print(f"document_id : {document_id}")
    print(f"titulo      : {titulo}")
    print("-" * 70)
    print(contenido)


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.
    [ES] Construye el analizador de argumentos de linea de comandos."""
    parser = argparse.ArgumentParser(
        description=(
            "Busca la evidencia literal de un item del Golden en el "
            "snapshot congelado. Solo lectura."
        )
    )
    parser.add_argument(
        "--texto",
        help="Fragmento literal a buscar. Corto y distintivo funciona mejor.",
    )
    parser.add_argument(
        "--fuente",
        help="Filtro parcial por fuente, por ejemplo Ley_24065.",
    )
    parser.add_argument(
        "--uid",
        help="Muestra un chunk completo por su chunk_uid.",
    )
    return parser


def main() -> None:
    """Run the search or show one chunk.
    [ES] Ejecuta la busqueda o muestra un chunk."""
    argumentos = construir_parser().parse_args()

    if argumentos.uid:
        mostrar_chunk(argumentos.uid)
        return

    if not argumentos.texto:
        print("Indique --texto para buscar, o --uid para ver un chunk.")
        return

    hallazgos = buscar(
        texto=argumentos.texto,
        fuente=argumentos.fuente,
    )

    print(f"coincidencias: {len(hallazgos)}")

    for hallazgo in hallazgos:
        print()
        print(f"chunk_uid : {hallazgo['chunk_uid']}")
        print(f"silo      : {hallazgo['silo']}")
        print(f"fuente    : {hallazgo['fuente']}")
        print(f"titulo    : {hallazgo['titulo']}")
        print(f"extracto  : ...{hallazgo['extracto']}...")


if __name__ == "__main__":
    main()
