import sys
from retriever import buscar, buscar_ruteado


pregunta = " ".join(sys.argv[1:])
if not pregunta:
    print('Uso: python src/ingestion/comparar.py' "<pregunta>"); sys.exit(1)

print("\n===== B0 MONOLITICO (searches all silos) =====")
for r in buscar(pregunta):
    print(f" [sim {r['similitud']:.3f}] ({r['silo']}) {r['titulo'][:48]} - {r['fuente']}")

print("\n===== B1 SEGREGATED (routed, scoped search) =====")
for r in buscar_ruteado(pregunta):
    print(f" [sim {r['similitud']:.3f}] ({r['silo']}) {r['titulo'][:48]} - {r['fuente']}")
    