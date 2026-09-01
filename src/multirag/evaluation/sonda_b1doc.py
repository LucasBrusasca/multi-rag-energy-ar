"""Compare B0, B1 (silo oracle) and B1-doc (catalog domain of the document).

B1-doc is what the approved plan actually describes: the whole document belongs
to its domains, taken from the curated catalog, instead of each chunk being
classified on its own. It needs NO schema change and NO re-ingestion: the
document_id is already persisted, so only the retrieval filter changes.

Read-only over the frozen snapshot.

[ES] Compara B0, B1 (oraculo de silo) y B1-doc (dominio del catalogo).

B1-doc es lo que el plan aprobado describe: el documento entero pertenece a sus
dominios, tomados del catalogo curado, en vez de clasificar cada chunk por
separado. No necesita cambio de esquema ni reingesta: document_id ya esta
persistido, asi que solo cambia el filtro de recuperacion.

Solo lectura sobre el snapshot congelado.
"""

import collections
import csv

from multirag.db import conectar
from multirag.evaluation.sonda_b0_b1 import (
        ESTRATO_PREDETERMINADO,
        RAIZ_PROYECTO,
        RUTA_BORRADOR,
        RUTA_YAML,
        cargar_items_borrador,
        cargar_items_yaml,
        posiciones_de_anclas,
        ranking_b0,
        ranking_b1,
        ubicacion_de_anclas,
        unir_items,
)
from multirag.config import SILOS
from multirag.orchestration.retriever import buscar

CATALOGO = RAIZ_PROYECTO / "data" / "catalog" / "metadatos_curados.csv"
VALORES_K = (1, 3, 10)
K_MAXIMO = max(VALORES_K)


def leer_catalogo() -> tuple[dict, dict]:
    """Return document -> thesis domains, and domain -> documents.
    [ES] Devuelve documento -> dominios de la tesis, y dominio -> documentos."""
    silos = set(SILOS)
    por_documento = {}
    por_dominio = collections.defaultdict(set)

    with CATALOGO.open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            dominios = {
                valor.strip()
                for valor in (fila.get("dominios_documentales") or "").split("|")
                if valor.strip()
            } & silos

            por_documento[fila["document_id"]] = dominios

            for dominio in dominios:
                por_dominio[dominio].add(fila["document_id"])

    return por_documento, por_dominio


def documentos_del_mismo_dominio(documentos_evidencia: list,
                                 por_documento: dict,
                                 por_dominio: dict) -> tuple[list, list]:
    """Documents sharing a catalog domain with the evidence's documents.
    [ES] Documentos que comparten dominio de catalogo con los de la evidencia."""
    dominios = set()

    for documento in documentos_evidencia:
        dominios |= por_documento.get(documento, set())

    alcance = set()

    for dominio in dominios:
        alcance |= por_dominio.get(dominio, set())

    return sorted(dominios), sorted(alcance)


def main() -> None:
    """Run the three arms and print Hit@k.
    [ES] Corre los tres brazos e imprime Hit@k."""
    por_documento, por_dominio = leer_catalogo()

    items = unir_items(
        cargar_items_borrador(RUTA_BORRADOR, ESTRATO_PREDETERMINADO),
        cargar_items_yaml(RUTA_YAML, ESTRATO_PREDETERMINADO),
    )

    conexion = conectar()
    resultados = []

    try:
        for identificador, datos in items.items():
            if not datos["anclas"] or not datos["pregunta"]:
                continue

            silos, documentos, ausentes = ubicacion_de_anclas(
                conexion, datos["anclas"]
            )

            if ausentes:
                continue

            dominios, alcance = documentos_del_mismo_dominio(
                documentos, por_documento, por_dominio
            )

            if not alcance:
                print(
                    f"[SALTEADO] {identificador}: "
                    "sus documentos no tienen dominio de la tesis en el catalogo"
                )
                continue

            b1doc = [
                registro["chunk_uid"]
                for registro in buscar(
                    datos["pregunta"], k=K_MAXIMO, documentos=alcance
                )
            ]

            resultados.append(
                {
                    "id": identificador,
                    "dominios": dominios,
                    "n_docs": len(alcance),
                    "B0": posiciones_de_anclas(
                        ranking_b0(datos["pregunta"], K_MAXIMO), datos["anclas"]
                    ),
                    "B1": posiciones_de_anclas(
                        ranking_b1(datos["pregunta"], silos, K_MAXIMO),
                        datos["anclas"],
                    ),
                    "B1doc": posiciones_de_anclas(b1doc, datos["anclas"]),
                }
            )
    finally:
        conexion.close()

    if not resultados:
        print("No hay items evaluables.")
        return

    def primero(posiciones):
        return min(posiciones) if posiciones else "-"

    print()
    print("item      docs  dominios_catalogo         B0   B1   B1doc")
    print("-" * 62)

    for fila in resultados:
        print(
            f"{fila['id']:9} {fila['n_docs']:>4}  "
            f"{','.join(fila['dominios']):24} "
            f"{str(primero(fila['B0'])):>3}  "
            f"{str(primero(fila['B1'])):>3}  "
            f"{str(primero(fila['B1doc'])):>5}"
        )

    total = len(resultados)

    print()
    print("  k    B0      B1      B1doc")
    print("-" * 32)

    for k in VALORES_K:
        celdas = []

        for brazo in ("B0", "B1", "B1doc"):
            aciertos = sum(
                1 for f in resultados if any(p <= k for p in f[brazo])
            )
            celdas.append(f"{aciertos:>2}/{total:<4}")

        print(f"{k:>3}   " + "  ".join(celdas))

    print()
    print(
        "EXPLORATORIO. B1doc usa dominios del catalogo, que estan en "
        "estado pendiente_revision."
    )


if __name__ == "__main__":
    main()
