"""Download the full text of the selected InfoLEG norms.

Public Argentine legislation. Requests are rate-limited and the run is
resumable: an already-downloaded norm is skipped. Raw bytes are stored so the
original encoding is preserved for the chunker.

The --criterio and --dominio filters exist because the two inclusion criteria
select different document families (short resolutions vs long laws and
decrees), and their size must be measured separately before deciding how many
documents to fetch.

[ES] Descarga el texto completo de las normas seleccionadas de InfoLEG.

Legislacion publica argentina. Las peticiones van limitadas en frecuencia y la
corrida es retomable: una norma ya bajada se saltea. Se guardan los bytes
crudos para preservar la codificacion original.

Los filtros --criterio y --dominio existen porque los dos criterios de
inclusion eligen familias documentales distintas (resoluciones cortas frente a
leyes y decretos largos), y su tamanio debe medirse por separado antes de
decidir cuantos documentos bajar.
"""

import argparse
import collections
import csv
import time
import urllib.error
import urllib.request
from pathlib import Path

from multirag.paths import DATA_DIR


DIRECTORIO = DATA_DIR / "incoming" / "infoleg"
SELECCION = DIRECTORIO / "seleccion.csv"
TEXTOS = DIRECTORIO / "textos"

PAUSA_SEGUNDOS = 1.0
TIEMPO_LIMITE = 30
AGENTE = "Mozilla/5.0 (compatible; tesis-academica-UA/1.0)"


def nombre_archivo(fila: dict) -> str:
    """Stable filename for one norm: domain, criterion and its InfoLEG id.
    [ES] Nombre estable para una norma: dominio, criterio e id de InfoLEG."""
    return f"{fila['dominio']}_{fila['criterio']}_{fila['id_norma']}.htm"


def descargar(url: str, destino: Path) -> int:
    """Fetch one norm and write its raw bytes. Returns the size written.
    [ES] Baja una norma y escribe sus bytes crudos. Devuelve el tamanio."""
    peticion = urllib.request.Request(url, headers={"User-Agent": AGENTE})

    with urllib.request.urlopen(peticion, timeout=TIEMPO_LIMITE) as respuesta:
        contenido = respuesta.read()

    destino.write_bytes(contenido)

    return len(contenido)


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.
    [ES] Construye el analizador de argumentos de linea de comandos."""
    parser = argparse.ArgumentParser(
        description="Descarga los textos de la seleccion de InfoLEG."
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Baja solo las primeras N pendientes.",
    )
    parser.add_argument(
        "--criterio",
        choices=("organismo", "materia"),
        default=None,
        help="Baja solo las normas de ese criterio de inclusion.",
    )
    parser.add_argument(
        "--dominio",
        default=None,
        help="Baja solo las normas de ese dominio.",
    )
    return parser


def main() -> None:
    """Download the selection, honouring the filters and the limit.
    [ES] Descarga la seleccion, respetando los filtros y el limite."""
    argumentos = construir_parser().parse_args()

    if not SELECCION.is_file():
        raise FileNotFoundError(f"No existe la seleccion: {SELECCION}")

    TEXTOS.mkdir(parents=True, exist_ok=True)

    with SELECCION.open(encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    candidatas = [
        fila
        for fila in filas
        if (argumentos.criterio is None
            or fila["criterio"] == argumentos.criterio)
        and (argumentos.dominio is None
             or fila["dominio"] == argumentos.dominio)
    ]

    pendientes = [
        fila
        for fila in candidatas
        if not (TEXTOS / nombre_archivo(fila)).is_file()
    ]

    if argumentos.limite:
        pendientes = pendientes[: argumentos.limite]

    print(f"en la seleccion : {len(filas)}")
    print(f"tras el filtro  : {len(candidatas)}")
    print(f"a descargar     : {len(pendientes)}")
    print()

    bajadas = 0
    bytes_totales = 0
    fallidas = []
    por_grupo = collections.Counter()

    for numero, fila in enumerate(pendientes, start=1):
        destino = TEXTOS / nombre_archivo(fila)

        try:
            tamanio = descargar(fila["url"], destino)
            bajadas += 1
            bytes_totales += tamanio
            por_grupo[(fila["dominio"], fila["criterio"])] += 1
            print(
                f"  {numero}/{len(pendientes)}  {destino.name}  "
                f"{tamanio:,} bytes"
            )
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            fallidas.append((fila["id_norma"], type(error).__name__))
            print(
                f"  {numero}/{len(pendientes)}  FALLO {fila['id_norma']}  "
                f"{type(error).__name__}"
            )

        time.sleep(PAUSA_SEGUNDOS)

    print()
    print(f"descargadas : {bajadas}")
    print(f"fallidas    : {len(fallidas)}")

    for identificador, motivo in fallidas[:10]:
        print(f"    {identificador}  {motivo}")

    if bajadas:
        print(f"promedio    : {bytes_totales // bajadas:,} bytes por norma")

    for (dominio, criterio), cantidad in sorted(por_grupo.items()):
        print(f"    {dominio:11} {criterio:11} {cantidad}")

    print(f"destino     : {TEXTOS}")


if __name__ == "__main__":
    main()
