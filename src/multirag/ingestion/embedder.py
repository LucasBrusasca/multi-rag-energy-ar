from typing import List, Dict
from sentence_transformers import SentenceTransformer

from multirag.config import EMBEDDING_MODEL

_model = None

def _get_model() -> SentenceTransformer:
    """ Carga el modelo UNA vez y lo reutiliza """
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def embed_chunks(chunks: List[Dict]) -> List[Dict]:
    """Agrega un vector de 1024 números a cada chunk."""
    model = _get_model()
    textos = [f"{c['title']}\n{c['content']}" for c in chunks]
    vectores = model.encode(textos, show_progress_bar = True)
    for chunk, vector in zip(chunks, vectores):
        chunk["embedding"] = vector.tolist()
    return chunks

def embed_query(texto: str) -> List[float]:
    """Convierte una sola pregunta en su vector de 1024."""
    return _get_model().encode(texto).tolist()


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from multirag.ingestion.chunker import chunk_by_structure

    if len(sys.argv) <2:
        print("Uso: python -m multirag.ingestion.embedder <ruta_al_documento>")
        sys.exit(1)

    ruta = Path(sys.argv[1])
    texto = ruta.read_text(encoding="utf-8")
    chunks = chunk_by_structure(texto, source=ruta.stem)
    chunks = embed_chunks(chunks)
    print(f"Total de chunks: {len(chunks)}")
    print(f"Dimensión del Embedding: {len(chunks[0]['embedding'])}")
    print(f"Primer chunk: {chunks[0]['title']}")
