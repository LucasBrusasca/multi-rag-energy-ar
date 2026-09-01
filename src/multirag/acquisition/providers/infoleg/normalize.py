"""Normalize acquired InfoLEG HTML while preserving the immutable raw source.

InfoLEG pages use visually separated ``div``/``br`` blocks but almost no
semantic headings. This adapter promotes only dispositive article starts to
``h2`` elements in a derived UTF-8 copy so Docling can preserve legal
structure. The transformation is provider-specific; the generic chunker stays
format- and provider-neutral.

[ES] Normaliza HTML adquirido de InfoLEG sin modificar la fuente cruda.

Las páginas usan bloques visuales pero casi ningún encabezado semántico. Este
adaptador promueve solamente comienzos dispositivos de artículos a ``h2`` en
una copia derivada UTF-8 para que Docling preserve la estructura normativa.
"""

import argparse
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

from multirag.acquisition.providers.infoleg.audit import (
    calcular_sha256,
    cargar_seleccion,
    guardar_informe,
)
from multirag.acquisition.providers.infoleg.download import nombre_archivo
from multirag.paths import DATA_DIR


DIRECTORIO = DATA_DIR / "incoming" / "infoleg"
SELECCION = DIRECTORIO / "seleccion.csv"
TEXTOS_CRUDOS = DIRECTORIO / "textos"
DIRECTORIO_DERIVADO = DATA_DIR / "staged" / "infoleg"
TEXTOS_NORMALIZADOS = DIRECTORIO_DERIVADO / "textos"
MANIFEST = DIRECTORIO_DERIVADO / "normalizacion_manifest.json"

VERSION_TRANSFORMACION = "infoleg-semantic-html-v1"
PATRON_ENCABEZADO_ARTICULO = re.compile(
    r"^(?P<encabezado>"
    r"(?:ART[ÍI]CULO|Art(?:ículo|\.))"
    r"\s+\d+\s*[°º]?\s*(?:\.-|\.|—|–|-)(?:\s*:)?"
    r")(?P<resto>.*)$",
    re.IGNORECASE,
)


def normalizar_espacios(texto: str) -> str:
    """Collapse whitespace for content-equivalence checks.
    [ES] Colapsa espacios para comprobar equivalencia de contenido."""
    return " ".join(texto.split())


def quitar_espacios(texto: str) -> str:
    """Remove whitespace without changing any content character.
    [ES] Quita blancos sin alterar ningun caracter de contenido."""
    return "".join(texto.split())


def promover_encabezados_articulos(
    ruta_entrada: Path,
    ruta_salida: Path,
) -> dict:
    """Create one normalized UTF-8 HTML copy and return its provenance.

    Only article starts with a number and a dispositive delimiter are promoted.
    Internal references such as ``Artículo 14 del Título I`` remain ordinary
    text. The function aborts if normalized visible text differs from the raw
    visible text after whitespace normalization.

    [ES] Crea una copia HTML UTF-8 normalizada y devuelve su procedencia.
    """
    if not ruta_entrada.is_file():
        raise FileNotFoundError(f"No existe la fuente cruda: {ruta_entrada}")

    soup = BeautifulSoup(ruta_entrada.read_bytes(), "lxml")

    for etiqueta in soup(("script", "noscript", "style")):
        etiqueta.decompose()

    cuerpo = soup.body or soup
    texto_antes = normalizar_espacios(cuerpo.get_text(" ", strip=True))
    promovidos = []

    for nodo in list(cuerpo.find_all(string=True)):
        if not isinstance(nodo, NavigableString):
            continue

        texto = normalizar_espacios(str(nodo))

        if not texto:
            continue

        coincidencia = PATRON_ENCABEZADO_ARTICULO.match(texto)

        if coincidencia is None:
            continue

        encabezado = coincidencia.group("encabezado").strip()
        resto = coincidencia.group("resto").strip()
        etiqueta_h2 = soup.new_tag("h2")
        etiqueta_h2.string = encabezado
        reemplazos = [etiqueta_h2]

        if resto:
            reemplazos.append(NavigableString(f" {resto}"))

        nodo.replace_with(*reemplazos)
        promovidos.append(encabezado)

    texto_despues = normalizar_espacios(cuerpo.get_text(" ", strip=True))

    equivalencia_exacta = texto_antes == texto_despues
    equivalencia_sin_espacios = (
        quitar_espacios(texto_antes) == quitar_espacios(texto_despues)
    )

    if not equivalencia_sin_espacios:
        raise ValueError(
            "La normalización alteró el texto visible de "
            f"{ruta_entrada.name}; no se guardó la copia derivada."
        )

    if soup.head is None:
        cabeza = soup.new_tag("head")

        if soup.html is not None:
            soup.html.insert(0, cabeza)
        else:
            soup.insert(0, cabeza)

    for meta in soup.find_all("meta"):
        if meta.has_attr("charset"):
            meta["charset"] = "utf-8"

        if str(meta.get("http-equiv", "")).casefold() == "content-type":
            meta["content"] = "text/html; charset=utf-8"

    if soup.find("meta", attrs={"charset": True}) is None:
        meta_utf8 = soup.new_tag("meta")
        meta_utf8["charset"] = "utf-8"
        soup.head.insert(0, meta_utf8)

    destino = ruta_salida.resolve()
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(f".{destino.name}.tmp")
    temporal.write_text(str(soup), encoding="utf-8", newline="\n")
    temporal.replace(destino)

    return {
        "archivo_crudo": str(ruta_entrada.resolve()),
        "archivo_normalizado": str(destino),
        "sha256_crudo": calcular_sha256(ruta_entrada),
        "sha256_normalizado": calcular_sha256(destino),
        "encoding_salida": "utf-8",
        "encabezados_promovidos": promovidos,
        "cantidad_promovida": len(promovidos),
        "contenido_visible_equivalente": True,
        "tipo_equivalencia": (
            "exacta" if equivalencia_exacta else "solo_espaciado"
        ),
        "caracteres_visibles": len(texto_antes),
        "caracteres_visibles_normalizados": len(texto_despues),
    }


def normalizar_lote(
    ruta_seleccion: Path,
    directorio_crudo: Path,
    directorio_salida: Path,
) -> dict:
    """Normalize every available file named by the reproducible selection.
    [ES] Normaliza cada archivo disponible de la selección reproducible."""
    filas = cargar_seleccion(ruta_seleccion)
    resultados = []
    faltantes = []

    for fila in filas:
        nombre = nombre_archivo(fila)
        origen = directorio_crudo / nombre

        if not origen.is_file():
            faltantes.append(nombre)
            continue

        destino = directorio_salida / f"{Path(nombre).stem}.html"
        procedencia = promover_encabezados_articulos(origen, destino)
        resultados.append(
            {
                "dominio_adquisicion": fila["dominio"],
                "criterio": fila["criterio"],
                "id_norma": fila["id_norma"],
                "nombre_crudo": nombre,
                "nombre_normalizado": destino.name,
                **procedencia,
            }
        )

    return {
        "schema_version": 1,
        "transformacion": VERSION_TRANSFORMACION,
        "seleccion": str(ruta_seleccion.resolve()),
        "directorio_crudo": str(directorio_crudo.resolve()),
        "directorio_salida": str(directorio_salida.resolve()),
        "seleccionados": len(filas),
        "normalizados": len(resultados),
        "faltantes": sorted(faltantes),
        "equivalencia": {
            "exacta": sum(
                resultado["tipo_equivalencia"] == "exacta"
                for resultado in resultados
            ),
            "solo_espaciado": sum(
                resultado["tipo_equivalencia"] == "solo_espaciado"
                for resultado in resultados
            ),
        },
        "resultados": resultados,
    }


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.
    [ES] Construye la interfaz de línea de comandos."""
    parser = argparse.ArgumentParser(
        description=(
            "Normaliza copias HTML de InfoLEG; preserva fuentes y no toca la base."
        )
    )
    parser.add_argument("--seleccion", type=Path, default=SELECCION)
    parser.add_argument("--entrada", type=Path, default=TEXTOS_CRUDOS)
    parser.add_argument("--salida", type=Path, default=TEXTOS_NORMALIZADOS)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    return parser


def main() -> None:
    """Normalize the selected batch and persist its provenance manifest.
    [ES] Normaliza el lote y guarda su manifest de procedencia."""
    argumentos = construir_parser().parse_args()
    informe = normalizar_lote(
        ruta_seleccion=argumentos.seleccion,
        directorio_crudo=argumentos.entrada,
        directorio_salida=argumentos.salida,
    )
    manifest = guardar_informe(informe, argumentos.manifest)
    promovidos = sum(
        resultado["cantidad_promovida"]
        for resultado in informe["resultados"]
    )

    print(f"seleccionados : {informe['seleccionados']}")
    print(f"normalizados  : {informe['normalizados']}")
    print(f"faltantes     : {len(informe['faltantes'])}")
    print(f"encabezados   : {promovidos}")
    print(f"equiv. exacta : {informe['equivalencia']['exacta']}")
    print(f"solo espaciado: {informe['equivalencia']['solo_espaciado']}")
    print(f"salida        : {Path(informe['directorio_salida'])}")
    print(f"manifest      : {manifest}")
    print("fuentes crudas: no modificadas")
    print("PostgreSQL    : no modificado")


if __name__ == "__main__":
    main()
