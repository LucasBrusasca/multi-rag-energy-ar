"""Compare raw InfoLEG HTML with temporary semantic heading promotion.

This diagnostic promotes only dispositive article starts (for example,
``ARTÍCULO 3º.-`` or ``Art. 2º —``) to HTML headings in a temporary copy. It
then runs the same Docling chunker on the raw and normalized inputs. Original
files and PostgreSQL are never modified.

[ES] Compara HTML InfoLEG crudo contra una promoción semántica temporal.

Solo convierte comienzos dispositivos de artículos en encabezados HTML dentro
de una copia temporal y ejecuta el mismo chunker sobre ambos brazos. Nunca
modifica las fuentes originales ni PostgreSQL.
"""

import argparse
import tempfile
from pathlib import Path
from typing import Callable

from multirag.acquisition.providers.infoleg.audit import (
    cargar_seleccion,
    guardar_informe,
)
from multirag.acquisition.providers.infoleg.normalize import (
    promover_encabezados_articulos,
)
from multirag.ingestion.chunker import chunk_with_docling
from multirag.paths import DATA_DIR
from scripts.diagnostics.infoleg_html_pilot import (
    SELECCION,
    TEXTOS,
    _es_corte_probable,
    seleccionar_muestra,
)


SALIDA = (
    DATA_DIR
    / "derived"
    / "diagnostics"
    / "infoleg_structure_ablation.json"
)

def resumir_chunks(chunks: list[dict]) -> dict:
    """Return comparable structure metrics for one conversion arm.
    [ES] Devuelve métricas comparables de un brazo de conversión."""
    contenidos = [chunk["content"] for chunk in chunks]
    cortes = [
        numero
        for numero in range(1, len(contenidos))
        if _es_corte_probable(contenidos[numero - 1], contenidos[numero])
    ]

    return {
        "chunks": len(chunks),
        "chunks_con_titulo": sum(bool(chunk.get("title")) for chunk in chunks),
        "chunks_con_jerarquia": sum(
            bool(chunk.get("hierarchy")) for chunk in chunks
        ),
        "limites_totales": max(0, len(chunks) - 1),
        "limites_con_corte_probable": cortes,
        "cantidad_cortes_probables": len(cortes),
        "caracteres_recuperados": sum(len(texto) for texto in contenidos),
    }


def comparar_archivo(
    registro: dict,
    directorio_temporal: Path,
    convertidor: Callable = chunk_with_docling,
) -> dict:
    """Run raw and normalized arms for one selected HTML file.
    [ES] Ejecuta los brazos crudo y normalizado para un HTML."""
    ruta = registro["ruta"]
    ruta_normalizada = directorio_temporal / f"{ruta.stem}_semantic.html"
    normalizacion = promover_encabezados_articulos(ruta, ruta_normalizada)
    chunks_crudos = convertidor(ruta, source=f"{ruta.stem}_raw")
    chunks_normalizados = convertidor(
        ruta_normalizada,
        source=f"{ruta.stem}_semantic",
    )
    fila = registro["fila"]

    return {
        "archivo": ruta.name,
        "dominio_adquisicion": fila["dominio"],
        "criterio": fila["criterio"],
        "id_norma": fila["id_norma"],
        "tamano_bytes": registro["tamano_bytes"],
        "normalizacion": normalizacion,
        "crudo": resumir_chunks(chunks_crudos),
        "normalizado": resumir_chunks(chunks_normalizados),
    }


def construir_informe(
    ruta_seleccion: Path,
    directorio_textos: Path,
    convertidor: Callable = chunk_with_docling,
) -> dict:
    """Build the complete temporary-structure ablation report.
    [ES] Construye el informe completo de la ablación estructural."""
    filas = cargar_seleccion(ruta_seleccion)
    muestra = seleccionar_muestra(filas, directorio_textos)

    with tempfile.TemporaryDirectory(prefix="infoleg_structure_") as temporal:
        directorio_temporal = Path(temporal)
        resultados = [
            comparar_archivo(
                registro,
                directorio_temporal,
                convertidor=convertidor,
            )
            for registro in muestra
        ]

    return {
        "schema_version": 1,
        "tipo": "ablacion_exploratoria_crudo_vs_encabezados_temporales",
        "cantidad_archivos": len(resultados),
        "resultados": resultados,
    }


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.
    [ES] Construye la interfaz de línea de comandos."""
    parser = argparse.ArgumentParser(
        description=(
            "Compara HTML crudo vs. encabezados temporales; no toca fuentes "
            "ni PostgreSQL."
        )
    )
    parser.add_argument("--seleccion", type=Path, default=SELECCION)
    parser.add_argument("--textos", type=Path, default=TEXTOS)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    return parser


def main() -> None:
    """Run the ablation and save only its derived report.
    [ES] Ejecuta la ablación y guarda solo el informe derivado."""
    argumentos = construir_parser().parse_args()
    informe = construir_informe(
        ruta_seleccion=argumentos.seleccion,
        directorio_textos=argumentos.textos,
    )
    ruta = guardar_informe(informe, argumentos.salida)

    print(f"archivos comparados: {informe['cantidad_archivos']}")

    for resultado in informe["resultados"]:
        crudo = resultado["crudo"]
        normalizado = resultado["normalizado"]
        normalizacion = resultado["normalizacion"]
        print()
        print(resultado["archivo"])
        print(
            f"  promovidos={normalizacion['cantidad_promovida']} "
            f"contenido_equivalente="
            f"{normalizacion['contenido_visible_equivalente']}"
        )
        print(
            "  crudo       "
            f"chunks={crudo['chunks']} "
            f"titulos={crudo['chunks_con_titulo']} "
            f"jerarquias={crudo['chunks_con_jerarquia']} "
            f"cortes={crudo['cantidad_cortes_probables']}"
        )
        print(
            "  normalizado "
            f"chunks={normalizado['chunks']} "
            f"titulos={normalizado['chunks_con_titulo']} "
            f"jerarquias={normalizado['chunks_con_jerarquia']} "
            f"cortes={normalizado['cantidad_cortes_probables']}"
        )

    print()
    print(f"informe: {ruta}")
    print("HTML originales: no modificados")
    print("PostgreSQL: no modificado")


if __name__ == "__main__":
    main()
