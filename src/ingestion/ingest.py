import sys
from pathlib import Path

def parse_pdf(path:Path) -> str:
    from docling.document_converter import DocumentConverter
    result = DocumentConverter().convert(str(path))
    return result.document.export_to_markdown()

def parse_excel(path:Path)-> str:
    import openpyxl
    wb = openpyxl.load_workbook(str(path),read_only=True, data_only=True)
    lineas = []
    for ws in wb.worksheets:
        lineas.append(f"## Hoja: {ws.title}")
        for row in ws.iter_rows(values_only=True):
            celdas = [str(c) for c in row if c is not None]
            if celdas:
                lineas.append(" | ".join(celdas))
    wb.close()
    return "\n".join(lineas)

def parse_csv(path:Path)->str:
    import csv
    lineas = []
    with path.open(encoding="utf-8", errors="ignore", newline="") as f:
        for fila in csv.reader(f):
            if any(c.strip() for c in fila):
                lineas.append(" | ".join(fila))
    return "\n".join(lineas)

def _office_xml(path:Path, partes: list[str])-> str:
    import zipfile, re
    texto = []
    with zipfile.ZipFile(path) as z:
        nombres= []
        for patron in partes:
            if patron.endswith("/"):
                nombres += sorted(n for n in z.namelist() if n.startswith(patron) and n.endswith(".xml"))
            elif patron in z.namelist():
                nombres.append(patron)
        for nombre in nombres:
            xml = z.read(nombre).decode("utf-8", errors="ignore")
            for frag in re.findall(r"<(?:w|a):t[^>]*>(.*?)</(?:w|a):t>", xml, re.DOTALL):
                texto.append(re.sub(r"<[^>]+>", "",frag))
            texto.append("")
    return "\n".join(texto).strip()

def parse_word(path: Path)-> str:
    return _office_xml(path, ["word/document.xml"])

def parse_pptx(path:Path)-> str:
    return _office_xml(path,["ppt/slides/"])

def parse_html(path: Path)-> str:
    import re
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"),"html.parser")
    for tag in soup(["script","style","nav","header","footer","aside"]):
        tag.decompose()
    return re.sub(r"\s+", " ",soup.get_text(separator=" ")).strip()

def parse_texto(path: Path)-> str:
    return path.read_text(encoding="utf-8",errors="ignore")

READERS = {
    ".pdf": parse_pdf,
    ".xlsx": parse_excel,
    ".xls": parse_excel,
    ".csv": parse_csv,
    ".docx": parse_word,
    ".pptx": parse_pptx,
    ".html": parse_html,
    ".htm": parse_html,
    ".txt": parse_texto,
    ".md": parse_texto    
    }

def parse_document(path: Path) -> str:
    """Despacha al lector correcto según la extensión."""
    reader = READERS.get(path.suffix.lower())
    if reader is None:
        raise ValueError(f"Formato no soportado: {path.suffix}, Soportados: {list(READERS)}")
    return reader(path)

def save_processed(text: str, output_path: Path) -> None:
    """Guarda el texto procesado como .md (crea la carpeta si no existe)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    print(f"Guardado en: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/ingestion/ingest.py <ruta_al_archivo")
        sys.exit(1)

    src = Path(sys.argv[1])
    print(f"Parseando: {src.name} ({src.suffix})")
    text=parse_document(src)
    out = Path("data/processed") / (src.stem +".md")
    save_processed(text, out)
    print(f"OK_ {len(text)} caracteres.")