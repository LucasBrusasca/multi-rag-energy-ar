"""Classify every chunk in the corpus with the LLM and persist the result.

Does not touch the database: writes a separate file so the partition can be
reviewed and frozen before anything is applied. The run is resumable.

[ES] Clasifica todos los chunks del corpus con el LLM y persiste el resultado.
No toca la base: escribe un archivo aparte para que la particion pueda revisarse
y congelarse antes de aplicar nada. La corrida se puede retomar.
"""

import csv
import time
from pathlib import Path

from multirag.db import conectar
from multirag.paths import DATA_DIR
from multirag.research.clasificador_llm import clasificar_llm

CATALOGO = DATA_DIR / "catalog" / "metadatos_curados.csv"
SALIDA = DATA_DIR / "clasificacion_llm.csv"

CAMPOS = ("chunk_uid", "fuente", "dominio_documental", "silo_coseno", "silo_llm")


def cargar_dominios() -> dict:
    """Load the human documental domain of each source.
    [ES] Carga el dominio documental humano de cada fuente."""
    dominios = {}
    with CATALOGO.open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            dominio = (fila.get("dominios_documentales") or "").strip()
            if dominio:
                dominios[fila["fuente"]] = dominio
    return dominios


def cargar_ya_hechos() -> set:
    """Return the chunk_uids already classified, so the run can resume.
    [ES] Devuelve los chunk_uid ya clasificados, para poder retomar la corrida."""
    if not SALIDA.is_file():
        return set()
    with SALIDA.open(encoding="utf-8-sig", newline="") as archivo:
        return {fila["chunk_uid"] for fila in csv.DictReader(archivo)}


def leer_chunks() -> list:
    """Read every chunk from the database, ordered for reproducibility.

    Title and hierarchy are read because the classifier uses them as the
    section path of the fragment. Omitting them here would run a WEAKER
    classifier than the one that was measured, and the measurement would stop
    describing this run.

    [ES] Lee todos los chunks de la base, ordenados para que sea reproducible.

    Se leen titulo y hierarchy porque el clasificador los usa como ruta de
    seccion del fragmento. Omitirlos aca correria un clasificador MAS DEBIL que
    el medido, y la medicion dejaria de describir esta corrida."""
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT chunk_uid, fuente, contenido, silo, titulo, hierarchy "
                "FROM chunks ORDER BY chunk_uid"
            )
            return cursor.fetchall()
    finally:
        conexion.close()


def main() -> None:
    """Classify the pending chunks, writing each result immediately.
    [ES] Clasifica los chunks pendientes, escribiendo cada resultado al instante."""
    dominios = cargar_dominios()
    ya_hechos = cargar_ya_hechos()
    chunks = leer_chunks()
    pendientes = [c for c in chunks if c[0] not in ya_hechos]

    print(f"chunks totales   : {len(chunks)}")
    print(f"ya clasificados  : {len(ya_hechos)}")
    print(f"pendientes       : {len(pendientes)}\n")

    if not pendientes:
        print("No queda nada pendiente.")
        return

    archivo_nuevo = not SALIDA.is_file()
    inicio = time.perf_counter()

    with SALIDA.open("a", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS, lineterminator="\n")
        if archivo_nuevo:
            escritor.writeheader()

        for numero, (uid, fuente, contenido, silo_coseno, titulo, hierarchy) in enumerate(pendientes, 1):
            silo_llm = clasificar_llm(
                contenido,
                titulo=titulo,
                hierarchy=hierarchy,
            )
            escritor.writerow({
                "chunk_uid": uid,
                "fuente": fuente,
                "dominio_documental": dominios.get(fuente, ""),
                "silo_coseno": silo_coseno,
                "silo_llm": silo_llm or "",
            })
            archivo.flush()

            if numero % 25 == 0 or numero == len(pendientes):
                transcurrido = time.perf_counter() - inicio
                resta = transcurrido / numero * (len(pendientes) - numero)
                print(f"  {numero}/{len(pendientes)}   "
                      f"{transcurrido / 60:.1f} min transcurridos · "
                      f"faltan ~{resta / 60:.1f} min", flush=True)

    print(f"\nGuardado en: {SALIDA}")


if __name__ == "__main__":
    main()
