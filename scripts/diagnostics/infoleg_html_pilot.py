"""Run a read-only, reproducible HTML-conversion pilot for InfoLEG.

The sample contains one median-sized acquired file from every acquisition
domain/criterion group plus the largest selected file. The diagnostic inspects
the source DOM, converts it with the project's current Docling chunker and
reports structure recovery, article retention, Unicode integrity and probable
mid-sentence cuts. It writes only a derived JSON report and never touches
PostgreSQL or the acquired HTML files.

[ES] Ejecuta un piloto reproducible y de solo lectura sobre HTML de InfoLEG.

La muestra contiene un archivo de tamaño mediano por cada combinación de
dominio/criterio de adquisición más el mayor archivo seleccionado. Inspecciona
el DOM, convierte con el chunker Docling vigente y reporta estructura,
retención de artículos, Unicode y cortes probables. Solo escribe un informe
JSON derivado; no modifica los HTML ni PostgreSQL.
"""

import argparse
import re
from pathlib import Path
from typing import Callable

from bs4 import BeautifulSoup

from multirag.acquisition.providers.infoleg.audit import (
    cargar_seleccion,
    guardar_informe,
)
from multirag.acquisition.providers.infoleg.download import nombre_archivo
from multirag.ingestion.chunker import chunk_with_docling
from multirag.paths import DATA_DIR


DIRECTORIO = DATA_DIR / "incoming" / "infoleg"
SELECCION = DIRECTORIO / "seleccion.csv"
TEXTOS = DIRECTORIO / "textos"
SALIDA = (
    DATA_DIR
    / "derived"
    / "diagnostics"
    / "infoleg_html_pilot.json"
)

PATRON_ARTICULO = re.compile(r"\bART[ÍI]CULO\s+\d+", re.IGNORECASE)
ETIQUETAS_ENCABEZADO = ("h1", "h2", "h3", "h4", "h5", "h6")
MARCADORES_RUIDO = (
    "Google Analytics",
    "Global site tag",
    "function(i,s,o,g,r,a,m)",
)
MARCADORES_MOJIBAKE = ("Ã", "Â", "�")
TERMINADORES_FUERTES = (".", "?", "!", ":", ";", '"', "”", ")", "]")


def _fila_con_ruta(
    fila: dict[str, str],
    directorio_textos: Path,
) -> dict | None:
    """Attach the expected path and byte size when the file exists.
    [ES] Agrega ruta esperada y tamaño cuando el archivo existe."""
    ruta = directorio_textos / nombre_archivo(fila)

    if not ruta.is_file():
        return None

    return {
        "fila": fila,
        "ruta": ruta,
        "tamano_bytes": ruta.stat().st_size,
    }


def seleccionar_muestra(
    filas: list[dict[str, str]],
    directorio_textos: Path,
) -> list[dict]:
    """Select one median file per group plus the global maximum.
    [ES] Elige un archivo mediano por grupo más el máximo global."""
    disponibles = [
        registro
        for fila in filas
        if (registro := _fila_con_ruta(fila, directorio_textos)) is not None
    ]

    if not disponibles:
        raise ValueError("No hay archivos seleccionados disponibles para el piloto.")

    grupos: dict[tuple[str, str], list[dict]] = {}

    for registro in disponibles:
        fila = registro["fila"]
        clave = (fila["dominio"], fila["criterio"])
        grupos.setdefault(clave, []).append(registro)

    elegidos = []

    for clave in sorted(grupos):
        ordenados = sorted(
            grupos[clave],
            key=lambda registro: (
                registro["tamano_bytes"],
                registro["ruta"].name.casefold(),
            ),
        )
        elegidos.append(ordenados[(len(ordenados) - 1) // 2])

    mayor = max(
        disponibles,
        key=lambda registro: (
            registro["tamano_bytes"],
            registro["ruta"].name.casefold(),
        ),
    )

    if all(registro["ruta"] != mayor["ruta"] for registro in elegidos):
        elegidos.append(mayor)

    return elegidos


def _texto_visible_y_estructura(ruta: Path) -> dict:
    """Inspect source HTML without relying on its filename extension.
    [ES] Inspecciona el HTML fuente sin confiar en la extensión."""
    soup = BeautifulSoup(ruta.read_bytes(), "lxml")

    for etiqueta in soup(("script", "style", "noscript")):
        etiqueta.decompose()

    texto_visible = " ".join(soup.get_text(" ", strip=True).split())
    articulos = sorted(set(PATRON_ARTICULO.findall(texto_visible)))

    return {
        "encoding_detectado": soup.original_encoding,
        "caracteres_visibles": len(texto_visible),
        "encabezados_semanticos": sum(
            len(soup.find_all(nombre)) for nombre in ETIQUETAS_ENCABEZADO
        ),
        "divs": len(soup.find_all("div")),
        "saltos_br": len(soup.find_all("br")),
        "tablas": len(soup.find_all("table")),
        "imagenes": len(soup.find_all("img")),
        "articulos_distintos": articulos,
    }


def _es_corte_probable(anterior: str, siguiente: str) -> bool:
    """Heuristic: a weak ending followed by a lowercase continuation.
    [ES] Heurística: final débil seguido por continuación en minúscula."""
    izquierda = anterior.rstrip()
    derecha = siguiente.lstrip()

    if not izquierda or not derecha:
        return False

    return (
        izquierda[-1] not in TERMINADORES_FUERTES
        and derecha[0].islower()
    )


def diagnosticar_archivo(
    registro: dict,
    convertidor: Callable = chunk_with_docling,
) -> dict:
    """Inspect and convert one sample file, returning only derived metrics.
    [ES] Inspecciona y convierte un archivo, devolviendo métricas derivadas."""
    ruta = registro["ruta"]
    fila = registro["fila"]
    estructura = _texto_visible_y_estructura(ruta)
    chunks = convertidor(ruta, source=ruta.stem)
    contenidos = [chunk["content"] for chunk in chunks]
    texto_convertido = "\n".join(contenidos)
    articulos_convertidos = sorted(
        set(PATRON_ARTICULO.findall(texto_convertido))
    )
    cortes = [
        numero
        for numero in range(1, len(contenidos))
        if _es_corte_probable(contenidos[numero - 1], contenidos[numero])
    ]
    articulos_fuente = estructura["articulos_distintos"]
    recuperados = {
        articulo.casefold() for articulo in articulos_convertidos
    }
    esperados = {articulo.casefold() for articulo in articulos_fuente}

    return {
        "archivo": ruta.name,
        "dominio_adquisicion": fila["dominio"],
        "criterio": fila["criterio"],
        "id_norma": fila["id_norma"],
        "tipo_norma": fila.get("tipo_norma", ""),
        "numero_norma": fila.get("numero_norma", ""),
        "tamano_bytes": registro["tamano_bytes"],
        "fuente_html": estructura,
        "conversion": {
            "chunks": len(chunks),
            "caracteres_recuperados": len(texto_convertido),
            "chunks_con_titulo": sum(bool(chunk.get("title")) for chunk in chunks),
            "chunks_con_jerarquia": sum(
                bool(chunk.get("hierarchy")) for chunk in chunks
            ),
            "articulos_distintos": articulos_convertidos,
            "articulos_fuente_recuperados": len(esperados & recuperados),
            "articulos_fuente_total": len(esperados),
            "limites_con_corte_probable": cortes,
            "marcadores_mojibake": {
                marcador: texto_convertido.count(marcador)
                for marcador in MARCADORES_MOJIBAKE
            },
            "marcadores_ruido": {
                marcador: texto_convertido.count(marcador)
                for marcador in MARCADORES_RUIDO
            },
            "inicio_ascii": ascii(texto_convertido[:240]),
            "final_ascii": ascii(texto_convertido[-240:]),
        },
    }


def construir_informe(
    ruta_seleccion: Path,
    directorio_textos: Path,
    convertidor: Callable = chunk_with_docling,
) -> dict:
    """Build the complete pilot report.
    [ES] Construye el informe completo del piloto."""
    filas = cargar_seleccion(ruta_seleccion)
    muestra = seleccionar_muestra(filas, directorio_textos)
    resultados = [
        diagnosticar_archivo(registro, convertidor=convertidor)
        for registro in muestra
    ]

    return {
        "schema_version": 1,
        "seleccion": str(ruta_seleccion.resolve()),
        "directorio_textos": str(directorio_textos.resolve()),
        "criterio_muestra": (
            "archivo mediano inferior por dominio_adquisicion × criterio, "
            "más el mayor archivo global"
        ),
        "cantidad_archivos": len(resultados),
        "resultados": resultados,
    }


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.
    [ES] Construye la interfaz de línea de comandos."""
    parser = argparse.ArgumentParser(
        description=(
            "Piloto de conversión HTML InfoLEG; no modifica fuentes ni base."
        )
    )
    parser.add_argument("--seleccion", type=Path, default=SELECCION)
    parser.add_argument("--textos", type=Path, default=TEXTOS)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    return parser


def main() -> None:
    """Run the pilot and save its derived report.
    [ES] Ejecuta el piloto y guarda su informe derivado."""
    argumentos = construir_parser().parse_args()
    informe = construir_informe(
        ruta_seleccion=argumentos.seleccion,
        directorio_textos=argumentos.textos,
    )
    ruta = guardar_informe(informe, argumentos.salida)

    print(f"archivos del piloto: {informe['cantidad_archivos']}")

    for resultado in informe["resultados"]:
        conversion = resultado["conversion"]
        fuente = resultado["fuente_html"]
        print()
        print(
            f"{resultado['archivo']} | "
            f"{resultado['dominio_adquisicion']} × {resultado['criterio']}"
        )
        print(
            f"  bytes={resultado['tamano_bytes']} "
            f"encoding={fuente['encoding_detectado']} "
            f"h1-h6={fuente['encabezados_semanticos']}"
        )
        print(
            f"  chunks={conversion['chunks']} "
            f"con_titulo={conversion['chunks_con_titulo']} "
            f"con_jerarquia={conversion['chunks_con_jerarquia']}"
        )
        print(
            "  articulos="
            f"{conversion['articulos_fuente_recuperados']}/"
            f"{conversion['articulos_fuente_total']} "
            f"cortes_probables={len(conversion['limites_con_corte_probable'])}"
        )

    print()
    print(f"informe: {ruta}")
    print("PostgreSQL: no modificado")


if __name__ == "__main__":
    main()
