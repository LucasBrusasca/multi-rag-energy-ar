"""Genera una revisión por documento sin modificar catálogo, corpus ni la v2.

Usa el inventario embebido en la interfaz v2 como snapshot; no reinterpreta
documentos ni vuelve a ejecutar las heurísticas de clasificación.
"""

import argparse
import json
import re
from pathlib import Path

from multirag.paths import EXPERIMENTS_DIR

ASSETS = Path(__file__).parent / "revision_documental"


def generar(origen: Path, salida: Path, demo: bool = False) -> dict:
    contenido = origen.read_text(encoding="utf-8")
    match = re.search(r'<script type="application/json" id="datos">(.*?)</script>', contenido, re.S)
    if not match:
        raise ValueError("La interfaz fuente no contiene un inventario reconocible.")
    datos = json.loads(match.group(1))
    ids = [d["id"] for d in datos["documentos"]]
    if len(ids) != len(set(ids)):
        raise ValueError("El inventario tiene identificadores repetidos.")
    datos["receta_origen"] = datos["receta"]
    datos["receta"] = "revision-documental-v3-por-documento"
    if demo:
        datos["huella_fuentes"] = "prueba-ui-v3-ficticia"
        datos["documentos"] = [{
            "id": f"PRUEBA-{i}", "archivo": f"Documento ficticio {i}.pdf",
            "ruta": "NO_EXISTE_DOCUMENTO_FICTICIO.pdf", "cohorte": "activo",
            "propuesta": {"emisor": "Emisor ficticio", "tipo": "estado_financiero",
                          "periodo": "2025", "dominios": ["contable"], "evidencia": [], "avisos": []},
        } for i in (1, 2)]
        datos["alcance"] = {"texto": "PRUEBA DE INTERFAZ. Dos documentos ficticios; estas decisiones no pertenecen al corpus."}
        datos["etiquetas_cohorte"] = {"activo": "PRUEBA FICTICIA"}
    html = (ASSETS / "interfaz.html").read_text(encoding="utf-8")
    js = (ASSETS / "interfaz.js").read_text(encoding="utf-8")
    html = html.replace("__CODIGO__", js).replace(
        "__DATOS__", json.dumps(datos, ensure_ascii=False).replace("<", "\\u003c")
    )
    if salida.resolve() == origen.resolve():
        raise ValueError("La salida debe ser distinta de la v2.")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(html, encoding="utf-8")
    return datos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origen", type=Path, default=EXPERIMENTS_DIR / "revision_corpus/revision_corpus_v2.html")
    parser.add_argument("--salida", type=Path, default=EXPERIMENTS_DIR / "revision_corpus/revision_documental_v3.html")
    parser.add_argument("--demo", action="store_true", help="Dos documentos ficticios para probar la UI sin decisiones reales.")
    args = parser.parse_args()
    if args.demo and args.salida.name == "revision_documental_v3.html":
        parser.error("La demo necesita --salida con otro nombre para no reemplazar la entrega.")
    datos = generar(args.origen, args.salida, args.demo)
    print(f"{len(datos['documentos'])} documentos. Interfaz: {args.salida}")
    print("Sin cambios en decisiones previas, catálogo o base de datos.")


if __name__ == "__main__":
    main()
