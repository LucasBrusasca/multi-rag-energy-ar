import re
from pathlib import Path
from typing import List, Dict, Tuple
from config import CHUNK_MIN_CHARS, CHUNK_MAX_CHARS, CHUNK_SENALES

_RE_HEADING = re.compile(r"^#{1,6}\s")
_RE_MAYUS = re.compile(r"^[A-ZÁÉÍÓÚÑÜ]{3,}")
_RE_ENUMERADOR = re.compile(r"^\(?(\d+(\.\d+)*|[a-zA-Z]|[ivxlcdmIVXLCDM]+)[\.\)]\s")
_RE_TABLA = re.compile(r"^\|.*\|\s*$")


def _es_inicio_seccion(linea: str, senales: Tuple[str, ...]) -> bool:
    if "heading" in senales and _RE_HEADING.match(linea): return True
    if "mayus" in senales and _RE_MAYUS.match(linea): return True
    if "enumerador" in senales and _RE_ENUMERADOR.match(linea): return True
    return False

def _titulo_corto(linea: str) -> str:
    """Rótulo corto: '## Resolución' -> 'Resolución'; 'ARTÍCULO 5.- Reempl...' -> 'ARTÍCULO 5'."""
    base = linea.lstrip("#").strip()
    m = re.match(r"^(.{1,40}?)\s*[\.\-:-]",base)
    return (m.group(1).strip() if m else base[:40]).strip()

def chunk_by_structure (
        text: str,
        source: str,
        senales: Tuple[str, ...] = CHUNK_SENALES,
        min_chars: int=CHUNK_MIN_CHARS,
        max_chars: int=CHUNK_MAX_CHARS
) -> List[Dict]:
    """Parte el texto por su ESTRUCTURA combinando señales por forma.
    - Tablas Markdown: bloque atómico (no se parten).
    - Sección > max_chars: se sub-divide por párrafos.
    - Fragmentos < min_chars: se  descartan.
    """
    secciones: List[Tuple[str, List[str]]] = []
    titulo, buffer = "Inicio", []
    
    for line in text.split("\n"):
        limpia = line.strip()

        # Una tabla nunca abre/cierra sección: se mantiene pegada
        if _RE_TABLA.match(limpia):
            buffer.append(line)
            continue

        if limpia and _es_inicio_seccion(limpia,senales):
            secciones.append((titulo,buffer))
            titulo = _titulo_corto(limpia)
            buffer = [] if _RE_HEADING.match(limpia) else [line]
        else:
            buffer.append(line)
    secciones.append((titulo,buffer))

    chunks = []
    for tit, lineas in secciones:
        contenido = "\n".join(lineas).strip()
        if len(contenido) < min_chars:
            continue
        for sub in _sub_dividir(contenido, max_chars):
            chunks.append({"title": tit,"content": sub, "source": source})
    return chunks

def _sub_dividir(texto: str, max_chars: int) -> List[str]:
    """Si el texto excede max_chars, lo corta por párrafos sin pasarse"""
    if len(texto) <= max_chars:
        return [texto]
    partes, actual = [], ""
    for parrafo in texto.split("\n\n"):
        if actual and len(actual) + len(parrafo) > max_chars:
            partes.append(actual.strip())
            actual = parrafo
        else:
            actual = f"{actual}\n\n{parrafo}" if actual else parrafo
    if actual.strip():
        partes.append(actual.strip())
    return partes


if __name__ == "__main__":
    import sys
    if len(sys.argv) <2:
        print("Uso: python src/ingestion/chunker.py <ruta_al_md>")
        sys.exit(1)
    ruta = Path(sys.argv[1])
    text = ruta.read_text(encoding="utf-8")
    chunks = chunk_by_structure(text, source=ruta.stem)
    print(f"Total de chunks: {len(chunks)}\n")
    for c in chunks:
        print(f"--- {c['title']} ---")
        print(c["content"][:200])
        print()


def chunk_with_docling(path, source):
    """Chunk a document with Docling's nativa structure-aware chunker.
        Returns the project's chunks dicts + the section hierarchy.
        [ES] Trocea un documento con el chunker nativo de Docling.
        Devuelve los dicts del proyecto + la jerarquía de sección."""
    from docling.document_converter import DocumentConverter
    from docling.chunking import HybridChunker
    document = DocumentConverter().convert(path).document
    chunks = []
    for ch in HybridChunker().chunk(dl_doc=document):
        headings = ch.meta.headings or []
        chunks.append({
            "title": headings[-1] if headings else "",
            "content": ch.text,
            "source": source,
            "hierarchy":headings
        })
    return chunks
