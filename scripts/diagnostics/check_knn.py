import sys
from multirag.ingestion.embedder import embed_query
from multirag.orchestration.clasificador import clasificar_knn

if len(sys.argv) < 2:
    print('Uso: python -m scripts.diagnostics.check_knn "<texto>"')
    sys.exit(1)


r = clasificar_knn(embed_query(" ".join(sys.argv[1:])))
print(f"silo: {r['silo']}")
print(f"scores: {r['silo_scores']}")
