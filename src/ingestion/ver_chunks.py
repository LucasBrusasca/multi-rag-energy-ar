import sys
from db import conectar

if len(sys.argv) < 2:
    print('Usage: python ver_chunks.py <silo> [fuente]')
    sys.exit(1)

silo = sys.argv[1]
fuente = sys.argv[2] if len(sys.argv) > 2 else None

sql = "SELECT id, fuente, titulo, contenido FROM chunks WHERE silo = %s"
params = [silo]
if fuente:
    sql += " AND fuente = %s"
    params.append(fuente)
sql += " ORDER BY id"

conexion = conectar()
try:
    with conexion.cursor() as cursor:
        cursor.execute(sql, params)
        for id_, fte, titulo, contenido in cursor.fetchall():
            print(f"\n--- id={id_} | fuente={fte} | titulo= {titulo!r} ---")
            print(contenido)
finally:
    conexion.close()