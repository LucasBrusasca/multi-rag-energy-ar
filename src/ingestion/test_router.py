import sys
from retriever import buscar_ruteado

pregunta = " ".join(sys.argv[1:])
if not pregunta:
    print('Uso: python src/ingestion/test_router.py "<pregunta>'); sys.exit(1)

for r in buscar_ruteado(pregunta):
    print(f" [sim {r['similitud']:.3f}] ({r['silo']}) {r['titulo'][:55]} - {r['fuente']}")