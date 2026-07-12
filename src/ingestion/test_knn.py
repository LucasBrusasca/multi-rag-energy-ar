import sys
from embedder import embed_query
from clasificador import clasificar_knn

if len(sys.argv) < 2:
    print('Usage: python test_knn.py "<text>"')
    sys.exit(1)


r = clasificar_knn(embed_query(" ".join(sys.argv[1:])))
print(f"silo: {r['silo']}")
print(f"scores: {r['silo_scores']}")
