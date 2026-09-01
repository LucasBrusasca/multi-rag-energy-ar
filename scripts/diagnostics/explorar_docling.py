import sys
from multirag.ingestion.chunker import chunk_with_docling

if len(sys.argv) < 2:
    print("Uso: python -m scripts.diagnostics.explorar_docling <ruta_documento>")
    sys.exit(1)

chunks = chunk_with_docling(sys.argv[1], source="test")
print(f"\n Total chunks: {len(chunks)}\n")
for i, c in enumerate(chunks):
    print(f"[{i}] hierarchy={c['hierarchy']} title= {c['title']!r} (content: {len(c['content'])} chars)")
