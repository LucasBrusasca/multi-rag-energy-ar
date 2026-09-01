"""Measure classifier accuracy against the documental domains of each source.

The reference is the SET of human domains of the document, from the curated
catalog. A chunk agrees when its silo belongs to that set. Agreeing does not
prove the chunk is right, because a document label does not transfer to every
one of its chunks; but a chunk assigned a domain the document does not have
anywhere is a classifier error or a human omission. It is therefore an upper
bound on agreement, and it is a fair instrument for COMPARING two classifiers
on the same chunks.

[ES] Mide la exactitud de los clasificadores contra los dominios documentales
de cada fuente.

La referencia es el CONJUNTO de dominios humanos del documento, tomado del
catalogo curado. Un chunk coincide cuando su silo pertenece a ese conjunto.
Coincidir no prueba que el chunk este bien, porque la etiqueta documental no se
traslada a cada uno de sus chunks; pero un chunk al que se le asigna un dominio
que el documento no tiene en ninguna parte es un error del clasificador o una
omision humana. Es entonces una cota superior del acuerdo, y es un instrumento
justo para COMPARAR dos clasificadores sobre los mismos chunks.
"""

import csv
import random
import time
from collections import defaultdict
from pathlib import Path

from multirag.config import SILOS
from multirag.db import conectar
from multirag.paths import DATA_DIR
from multirag.research.clasificador_llm import clasificar_llm

CATALOGO = DATA_DIR / "catalog" / "metadatos_curados.csv"
SALIDA = DATA_DIR / "medicion_clasificador.csv"

MUESTRA_POR_FUENTE = 10
SEED = 7


def cargar_dominios() -> dict:
    """Load the SET of human silos of each source from the curated catalog.

    The catalog uses a richer vocabulary than the four silos (regulatorio,
    corporativo, tecnico...). Those labels cannot be expressed by the current
    taxonomy and are left out of the comparison, but a source that keeps no
    silo at all is dropped instead of counting as a failure.

    [ES] Carga el CONJUNTO de silos humanos de cada fuente desde el catalogo.

    El catalogo usa un vocabulario mas rico que los cuatro silos (regulatorio,
    corporativo, tecnico...). Esas etiquetas no las puede expresar la taxonomia
    vigente y quedan fuera de la comparacion, pero una fuente que no conserve
    ningun silo se descarta en lugar de contar como fallo.
    """
    dominios = {}
    with CATALOGO.open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            crudos = {
                valor.strip()
                for valor in (
                    fila.get("dominios_documentales") or ""
                ).split("|")
                if valor.strip()
            }
            silos = crudos & set(SILOS)
            if silos:
                dominios[fila["fuente"]] = silos
    return dominios


def muestrear_chunks(dominios: dict) -> list:
    """Sample chunks stratified by source, with a fixed seed for reproducibility.
    [ES] Muestrea chunks estratificados por fuente, con semilla fija para reproducibilidad."""
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT fuente, chunk_uid, titulo, contenido, hierarchy, silo "
                "FROM chunks ORDER BY chunk_uid"
            )
            filas = cursor.fetchall()
    finally:
        conexion.close()

    por_fuente = defaultdict(list)
    for fuente, uid, titulo, contenido, hierarchy, silo in filas:
        if fuente in dominios:
            por_fuente[fuente].append((fuente, uid, titulo, contenido, hierarchy, silo))

    aleatorio = random.Random(SEED)
    muestra = []
    for fuente in sorted(por_fuente):
        candidatos = por_fuente[fuente]
        muestra += aleatorio.sample(candidatos, min(MUESTRA_POR_FUENTE, len(candidatos)))
    return muestra


def main() -> None:
    """Run the comparison and persist the per-chunk detail.
    [ES] Corre la comparacion y persiste el detalle por chunk."""
    dominios = cargar_dominios()
    muestra = muestrear_chunks(dominios)
    print(f"fuentes: {len(dominios)} · chunks muestreados: {len(muestra)}\n")

    resultados = []
    inicio = time.perf_counter()

    for numero, (fuente, uid, titulo, contenido, hierarchy, silo_coseno) in enumerate(muestra, 1):
        esperados = dominios[fuente]
        etiqueta = "|".join(sorted(esperados))
        silo_llm = clasificar_llm(contenido, titulo=titulo, hierarchy=hierarchy)
        resultados.append({
            "fuente": fuente,
            "chunk_uid": uid,
            "dominio_documental": etiqueta,
            "silo_coseno": silo_coseno,
            "silo_llm": silo_llm or "",
            # Agreement is membership in the document's set of domains, never
            # equality against a pipe-joined string.
            # [ES] La coincidencia es pertenencia al conjunto de dominios del
            # documento, nunca igualdad contra una cadena con barras.
            "coincide_coseno": silo_coseno in esperados,
            "coincide_llm": silo_llm in esperados,
            # Chance level for this chunk: how much of the taxonomy its
            # document's label accepts. Without it a high agreement over broad
            # labels looks like skill.
            # [ES] Nivel de azar de este chunk: cuanto de la taxonomia acepta
            # la etiqueta de su documento. Sin esto, un acuerdo alto sobre
            # etiquetas amplias parece merito.
            "azar": len(esperados) / len(SILOS),
            "contenido": contenido[:300].replace("\n", " "),
        })
        print(f"  {numero}/{len(muestra)}  {fuente[:30]:30s} "
              f"doc={etiqueta:24s} coseno={silo_coseno:11s} llm={str(silo_llm):11s}",
              flush=True)

    transcurrido = time.perf_counter() - inicio
    total = len(resultados)
    aciertos_coseno = sum(r["coincide_coseno"] for r in resultados)
    aciertos_llm = sum(r["coincide_llm"] for r in resultados)
    azar = sum(r["azar"] for r in resultados) / total
    sin_respuesta = sum(1 for r in resultados if not r["silo_llm"])

    print("\n" + "=" * 68)
    print(f"  azar   : {azar:.1%}   (linea base: cuanto acepta la etiqueta del documento)")
    print(f"  coseno : {aciertos_coseno}/{total}  ({aciertos_coseno / total:.1%})")
    print(f"  LLM    : {aciertos_llm}/{total}  ({aciertos_llm / total:.1%})")
    if sin_respuesta:
        print(f"  el LLM no devolvio un silo valido en {sin_respuesta} caso(s); cuentan como fallo")
    print(f"  tiempo : {transcurrido / 60:.1f} min")
    print("=" * 68)

    print("\nDesagregado por conjunto de dominios del documento:")
    print(f"\n{'dominios del documento':<28} {'chunks':>7} {'azar':>7} "
          f"{'coseno':>8} {'LLM':>8}")

    por_conjunto = defaultdict(list)
    for registro in resultados:
        por_conjunto[registro["dominio_documental"]].append(registro)

    for etiqueta in sorted(por_conjunto, key=lambda k: -len(por_conjunto[k])):
        grupo = por_conjunto[etiqueta]
        n = len(grupo)
        print(f"{etiqueta:<28} {n:>7} "
              f"{grupo[0]['azar']:>6.0%} "
              f"{sum(r['coincide_coseno'] for r in grupo) / n:>7.0%} "
              f"{sum(r['coincide_llm'] for r in grupo) / n:>7.0%}")

    print("\nFuentes donde el LLM discrepa (candidatas a documento mixto o a error):")
    for fuente in sorted({r["fuente"] for r in resultados}):
        de_la_fuente = [r for r in resultados if r["fuente"] == fuente]
        ok = sum(r["coincide_llm"] for r in de_la_fuente)
        if ok < len(de_la_fuente):
            print(f"  {fuente[:42]:42s} {ok}/{len(de_la_fuente)}")

    print("\nEs una COTA SUPERIOR del acuerdo, no una exactitud: la etiqueta")
    print("humana es del documento y la decision es del chunk. Sirve para")
    print("COMPARAR ambos clasificadores sobre los mismos chunks.")

    with SALIDA.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(resultados[0]),
                                  lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(resultados)
    print(f"\nDetalle guardado en: {SALIDA}")


if __name__ == "__main__":
    main()
