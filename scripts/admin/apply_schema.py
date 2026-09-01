"""Aplica el esquema SQL canónico del paquete Multi-RAG."""

from importlib.resources import files

from multirag.db import conectar


def main() -> None:
    """Lee el esquema empaquetado y lo aplica en una transacción."""
    sql = (
        files("multirag.ingestion")
        .joinpath("schema.sql")
        .read_text(encoding="utf-8")
    )

    conexion = conectar()
    try:
        with conexion, conexion.cursor() as cursor:
            cursor.execute(sql)
    finally:
        conexion.close()

    print("Schema aplicado.")


if __name__ == "__main__":
    main()
