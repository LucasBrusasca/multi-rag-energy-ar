"""Throwaway: rank a silo's chunks by the old classifier's confidence (max silo_score).
Highest-confidence first = best seed candidates; garbage/ambiguous sink to the bottom.
[ES] Descartable: ordena los chunks de un silo por la confianza del clasificador viejo
(score máximo). Los más confiables primero = mejores candidatos a semilla."""
import sys, json

from multirag.db import conectar


def as_dict(s):
    if isinstance(s, str):
        return json.loads(s)
    return s or {}


if len(sys.argv) < 2:
    print('Uso: python -m multirag.research.candidatos_semilla <silo>')
    sys.exit(1)

silo = sys.argv[1]

conexion = conectar()
try:
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT id, fuente, silo_scores, contenido FROM chunks WHERE silo = %s",
            (silo,),
        )
        filas = cursor.fetchall()
finally:
    conexion.close()

filas.sort(key=lambda f: max(as_dict(f[2]).values(), default=0.0), reverse=True)
for id_, fuente, scores, contenido in filas:
    conf = max(as_dict(scores).values(), default=0.0)
    snippet = " ".join(contenido.split())[:110]
    print(f"{conf:.2f} | id={id_:<5} | {fuente:24s} | {snippet}")
