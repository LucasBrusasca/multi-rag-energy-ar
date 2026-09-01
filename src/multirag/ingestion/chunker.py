import re
from pathlib import Path
from typing import List, Dict, Tuple

from multirag.config import (
    CHUNK_MAX_CHARS,
    CHUNK_MAX_TOKENS,
    CHUNK_MIN_CHARS,
    CHUNK_SENALES,
    EMBEDDING_MODEL,
)


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
        print("Uso: python -m multirag.ingestion.chunker <ruta_al_documento>")
        sys.exit(1)
    ruta = Path(sys.argv[1])
    text = ruta.read_text(encoding="utf-8")
    chunks = chunk_by_structure(text, source=ruta.stem)
    print(f"Total de chunks: {len(chunks)}\n")
    for c in chunks:
        print(f"--- {c['title']} ---")
        print(c["content"][:200])
        print()


def _necesita_ocr(ruta: str) -> bool:
    """True if the document is a scan: the MAJORITY of its pages have no extractable text.
    OCR is a PDF question — text-native formats (docx/html/...) never need it.
    [ES] True si el documento es un escaneo: la MAYORÍA de sus páginas no tiene texto extraíble.
    El OCR es una pregunta de PDFs — los formatos de texto nativo (docx/html/...) nunca lo necesitan."""
    if Path(ruta).suffix.lower() != ".pdf":
        return False
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(ruta)
    try:
        total = len(pdf)
        if total == 0:
            return True
        con_texto = 0
        for i in range(total):
            pagina = pdf[i]
            texto = pagina.get_textpage()
            if (texto.get_text_bounded() or "").strip():
                con_texto += 1
            texto.close()
            pagina.close()
        return (total - con_texto) > con_texto
    finally:
        pdf.close()


def _imagenes_sin_texto(chunks: List[Dict]) -> int:
    """Count image placeholders Docling left behind: images it could NOT read.
    Non-zero means content was lost and the document must be re-processed with OCR.
    [ES] Cuenta los placeholders de imagen que dejó Docling: imágenes que NO pudo leer.
    Distinto de cero significa que se perdió contenido y el documento debe re-procesarse con OCR."""
    return sum(c["content"].count("<!-- image -->") for c in chunks)

def extraer_procedencia(ch, offset_global: int = 0) -> Dict:
    """Extract where in the document each chunk comes from.

    Docling already carries this in `ch.meta.doc_items[].prov[]` and the project
    was discarding it. It is what the plan needs to cite "the exact source, page
    and paragraph" (p. 8).

    What each field is, and what it is NOT:

    - `pagina_desde` / `pagina_hasta`: a RANGE, because a merged chunk can span
      pages. Empty for HTML, where the page does not exist as a concept.
    - `doc_refs`: the structural path of the nodes (`#/texts/57`, `#/tables/0`).
      Always present, including HTML. For HTML it IS the equivalent of the
      paragraph number, and it is honest: a rendered page would be an artifact
      of the browser, not a property of the document.
    - `offset_desde`: character position accumulated in reading order. Docling
      does NOT provide a global offset — its `charspan` restarts at 0 on each
      item — so it is computed here by accumulating lengths. It is exact for the
      order in which the chunker emits, and it is the honest reading of the
      plan's "character offset".

    [ES] Extrae de dónde viene cada chunk dentro del documento.

    Docling ya trae esto en `ch.meta.doc_items[].prov[]` y el proyecto lo estaba
    descartando. Es lo que el plan necesita para citar "la fuente exacta, página
    y párrafo" (p. 8).

    Qué es cada campo, y qué NO es:

    - `pagina_desde` / `pagina_hasta`: un RANGO, porque un chunk fusionado puede
      abarcar varias páginas. Vacío en HTML, donde la página no existe como
      concepto.
    - `doc_refs`: la ruta estructural de los nodos (`#/texts/57`, `#/tables/0`).
      Siempre presente, HTML incluido. Para HTML ES el equivalente del número de
      párrafo, y es honesto: una página renderizada sería un artefacto del
      navegador, no una propiedad del documento.
    - `offset_desde`: posición de carácter acumulada en orden de lectura.
      Docling NO da un offset global —su `charspan` reinicia en 0 en cada
      ítem—, así que se calcula acá acumulando longitudes. Es exacto para el
      orden en que el chunker emite, y es la lectura honesta del "offset de
      caracteres" del plan.
    """
    items = list(getattr(ch.meta, "doc_items", None) or [])

    paginas = [
        prov.page_no
        for item in items
        for prov in (getattr(item, "prov", None) or [])
        if getattr(prov, "page_no", None) is not None
    ]

    refs = [
        ref
        for ref in (getattr(item, "self_ref", None) for item in items)
        if ref
    ]

    return {
        "pagina_desde": min(paginas) if paginas else None,
        "pagina_hasta": max(paginas) if paginas else None,
        "doc_refs": refs,
        "offset_desde": offset_global,
        "offset_hasta": offset_global + len(ch.text),
    }


_convertidores = {}
_troceador = None

def chunk_with_docling(path, source):
    """Chunk a document with Docling's nativa structure-aware chunker.
        Returns the project's chunk dicts + the section hierarchy.
        OCR is decided PER DOCUMENT (_necesita_ocr).
        Chunk size follows the PROJECT's embedder, not Docling's default tokenizer.
        Refuses partial conversions: a document ingests COMPLETE or fails loudly.
        [ES] Trocea un documento con el chunker nativo de Docling.
        Devuelve los dicts del proyecto + la jerarquía de sección.
        El OCR se decide POR DOCUMENTO (_necesita_ocr).
        El tamaño de chunk sigue al embedder DEL PROYECTO, no al tokenizer default de Docling.
        Rechaza conversiones parciales: un documento entra COMPLETO o falla avisando."""
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
    from docling.chunking import HybridChunker
    from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

    global _troceador
    ocr = _necesita_ocr(path)
    if ocr not in _convertidores:
        opciones = PdfPipelineOptions()
        opciones.do_ocr = ocr
        opciones.do_table_structure = True
        _convertidores[ocr] = DocumentConverter(
            format_options = {InputFormat.PDF:
        PdfFormatOption(pipeline_options=opciones, backend=PyPdfiumDocumentBackend)}
        )
    resultado = _convertidores[ocr].convert(path,raises_on_error=False)

    if resultado.status.name != "SUCCESS":
        detalles = "\n".join(f"  - {e}" for e in resultado.errors)
        raise RuntimeError(
            f"Conversión INCOMPLETA de '{path}' ({resultado.status.name}, {len(resultado.errors)} errores: {detalles}). "
            f"NO se ingiere un documento parcial."
        )

    document = resultado.document

    if _troceador is None:
        _troceador = HybridChunker(
            tokenizer=HuggingFaceTokenizer.from_pretrained(
                model_name=EMBEDDING_MODEL, max_tokens=CHUNK_MAX_TOKENS
            )
        )
    troceador = _troceador

    chunks = []
    offset_global = 0
    for ch in troceador.chunk(dl_doc=document):
        if len(ch.text.strip()) < CHUNK_MIN_CHARS:
            offset_global += len(ch.text)
            continue
        headings = ch.meta.headings or []
        procedencia = extraer_procedencia(ch, offset_global)
        offset_global += len(ch.text)
        chunks.append({
            "title": headings[-1] if headings else "",
            "content": ch.text,
            "source": source,
            "hierarchy":headings,
            **procedencia,
        })

    perdidas = _imagenes_sin_texto(chunks)
    if perdidas:
        print(f"[chunker] AVISO: {perdidas} imagen(es) sin texto extraido en '{source}' -> re-procesar con OCR")
    return chunks
