"""Select the InfoLEG norms that will be downloaded, with a fixed seed.

This IS the documented inclusion criterion. Two criteria are applied and kept
separate because they select different document families:

  A) by issuing organism  -> resolutions and dispositions of the sector's
     bodies. High volume, mostly single-domain. Provides corpus mass.
  B) by subject matter    -> laws and decrees whose title refers to the domain.
     Criterion A cannot see them because Congress and the Executive issue them.
     Lower volume, mostly MULTI-domain. These are the documents the thesis is
     about.

Downloads nothing: writes the selection so it can be reviewed first.

[ES] Selecciona las normas de InfoLEG que se van a descargar, con semilla fija.

Este script ES el criterio de inclusion documentado. Se aplican dos criterios,
separados porque eligen familias documentales distintas:

  A) por organismo emisor -> resoluciones y disposiciones de los organismos del
     sector. Mucho volumen, mayormente monodominio. Aporta masa al corpus.
  B) por materia          -> leyes y decretos cuyo titulo refiere al dominio.
     El criterio A no puede verlas porque las emiten el Congreso y el Ejecutivo.
     Menos volumen, mayormente MULTIDOMINIO. Son los documentos de los que
     trata la tesis.

No descarga nada: escribe la seleccion para poder revisarla antes.
"""

import argparse
import collections
import csv
import random
import re
import unicodedata
from pathlib import Path

from multirag.paths import DATA_DIR


DIRECTORIO = DATA_DIR / "incoming" / "infoleg"
ENTRADA = DIRECTORIO / "base-infoleg-normativa-nacional.csv"
SALIDA = DIRECTORIO / "seleccion.csv"

# --- Criterio A: por organismo emisor ---
ORGANISMOS = {
    "energia": ("ENERG", "ENARGAS", "ELECTRIC", "GAS",
                "HIDROCARBURO", "COMBUSTIBLE"),
    "impositivo": ("INGRESOS PUBLICOS", "IMPOSITIV", "ADUANA",
                   "TRIBUNAL FISCAL"),
}
EXCLUIR_ORGANISMO = ("PROVINCIAL",)

# --- Criterio B: por materia del titulo, solo para normas de marco ---
TIPOS_MARCO = ("Ley", "Decreto", "Decreto/Ley")
MATERIA = {
    "energia": re.compile(
        r"(ENERG|ELECTRIC|GASODUCT|HIDROCARBUR|COMBUSTIBL|TARIFA)|\bGAS\b"
    ),
    "impositivo": re.compile(
        r"(IMPUEST|TRIBUT|IMPOSITIV|ADUANER|ARANCEL|FISCAL)"
        r"|\bIVA\b|\bGANANCIAS\b"
    ),
}

DOMINIOS = ("energia", "impositivo")
CRITERIOS = ("organismo", "materia")

CAMPOS = ("dominio", "criterio", "id_norma", "tipo_norma", "numero_norma",
          "organismo_origen", "fecha_sancion", "titulo_resumido", "url")


def sin_tildes(texto: str) -> str:
    """Uppercase without accents, for robust matching.
    [ES] Mayusculas sin tildes, para comparar de forma robusta."""
    return "".join(
        unicodedata.normalize("NFD", caracter)[0]
        for caracter in (texto or "").upper()
    )


def clasificar(fila: dict) -> tuple[str, str] | None:
    """Return (domain, criterion) or None if the norm is out of scope.

    Criterion A asks WHO issued it; criterion B asks WHAT it is about. A is
    checked first, so a sector resolution never falls into B.

    [ES] Devuelve (dominio, criterio) o None si la norma esta fuera de alcance.

    El criterio A pregunta QUIEN la emitio; el B, DE QUE trata. Se evalua A
    primero, asi una resolucion del sector nunca cae en B.
    """
    organismo = sin_tildes(fila.get("organismo_origen"))

    if not any(palabra in organismo for palabra in EXCLUIR_ORGANISMO):
        for dominio, claves in ORGANISMOS.items():
            if any(clave in organismo for clave in claves):
                return dominio, "organismo"

    if fila.get("tipo_norma") in TIPOS_MARCO:
        titulo = sin_tildes(
            f"{fila.get('titulo_resumido') or ''} "
            f"{fila.get('titulo_sumario') or ''}"
        )

        for dominio, patron in MATERIA.items():
            if patron.search(titulo):
                return dominio, "materia"

    return None


def candidatos(desde: int, hasta: int) -> dict:
    """Group every eligible norm by (domain, criterion, year).
    [ES] Agrupa las normas elegibles por (dominio, criterio, anio)."""
    grupos = collections.defaultdict(list)

    with ENTRADA.open(encoding="utf-8", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            url = (
                (fila.get("texto_actualizado") or "").strip()
                or (fila.get("texto_original") or "").strip()
            )

            if not url:
                continue

            clase = clasificar(fila)

            if clase is None:
                continue

            dominio, criterio = clase
            anio = (fila.get("fecha_sancion") or "")[:4]

            if not anio.isdigit() or not desde <= int(anio) <= hasta:
                continue

            grupos[(dominio, criterio, int(anio))].append(
                {
                    "dominio": dominio,
                    "criterio": criterio,
                    "id_norma": fila["id_norma"],
                    "tipo_norma": fila["tipo_norma"],
                    "numero_norma": fila["numero_norma"],
                    "organismo_origen": fila["organismo_origen"],
                    "fecha_sancion": fila["fecha_sancion"],
                    "titulo_resumido": fila.get("titulo_resumido") or "",
                    "url": url,
                }
            )

    return grupos


def muestrear(grupos: dict, dominio: str, criterio: str,
              anios: list, cupo: int, azar: random.Random) -> list:
    """Draw up to `cupo` norms for one (domain, criterion), spread over years.
    [ES] Toma hasta `cupo` normas de un (dominio, criterio), repartidas por anio."""
    por_anio = max(1, cupo // len(anios))
    elegidos = []

    for anio in anios:
        disponibles = grupos.get((dominio, criterio, anio), [])
        elegidos.extend(
            azar.sample(disponibles, min(por_anio, len(disponibles)))
        )

    if len(elegidos) < cupo:
        ya = {registro["id_norma"] for registro in elegidos}
        resto = [
            registro
            for anio in anios
            for registro in grupos.get((dominio, criterio, anio), [])
            if registro["id_norma"] not in ya
        ]
        azar.shuffle(resto)
        elegidos.extend(resto[: cupo - len(elegidos)])

    return elegidos[:cupo]


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.
    [ES] Construye el analizador de argumentos de linea de comandos."""
    parser = argparse.ArgumentParser(
        description="Selecciona normas de InfoLEG. No descarga nada."
    )
    parser.add_argument("--desde", type=int, default=2015)
    parser.add_argument("--hasta", type=int, default=2026)
    parser.add_argument(
        "--por-grupo",
        type=int,
        default=100,
        help=(
            "Cantidad por cada combinacion dominio x criterio. "
            "Con 2 dominios y 2 criterios, 100 da 400 documentos."
        ),
    )
    parser.add_argument("--semilla", type=int, default=7)
    return parser


def main() -> None:
    """Write the seeded stratified selection and report its composition.
    [ES] Escribe la seleccion estratificada con semilla y reporta su composicion."""
    argumentos = construir_parser().parse_args()

    if not ENTRADA.is_file():
        raise FileNotFoundError(f"No existe el indice: {ENTRADA}")

    grupos = candidatos(argumentos.desde, argumentos.hasta)
    anios = list(range(argumentos.desde, argumentos.hasta + 1))
    azar = random.Random(argumentos.semilla)

    disponibles = collections.Counter()

    for (dominio, criterio, _), registros in grupos.items():
        disponibles[(dominio, criterio)] += len(registros)

    seleccion = []

    for dominio in DOMINIOS:
        for criterio in CRITERIOS:
            seleccion.extend(
                muestrear(
                    grupos, dominio, criterio, anios,
                    argumentos.por_grupo, azar,
                )
            )

    with SALIDA.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(seleccion)

    print(f"ventana       : {argumentos.desde}-{argumentos.hasta}")
    print(f"semilla       : {argumentos.semilla}")
    print(f"cupo por grupo: {argumentos.por_grupo}")
    print()
    print("grupo                      disponibles  seleccionadas")
    print("-" * 54)

    for dominio in DOMINIOS:
        for criterio in CRITERIOS:
            tomadas = sum(
                1 for r in seleccion
                if r["dominio"] == dominio and r["criterio"] == criterio
            )
            print(
                f"{dominio:11} {criterio:11} "
                f"{disponibles[(dominio, criterio)]:>11}  {tomadas:>13}"
            )

    print()
    print(f"TOTAL seleccionadas: {len(seleccion)}")
    print(
        "por tipo: "
        + str(dict(collections.Counter(
            r["tipo_norma"] for r in seleccion
        ).most_common()))
    )
    print(f"salida  : {SALIDA}")


if __name__ == "__main__":
    main()
