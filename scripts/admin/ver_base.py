from multirag.db import conectar

conexion = conectar()
try:
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT fuente, silo, Count(*)"
            "FROM chunks GROUP BY fuente, silo ORDER BY fuente, silo"
        )
        for fuente, silo, n in cursor.fetchall():
            print(f"{fuente:40s} | {silo:12s} | {n}")
finally:
    conexion.close()
