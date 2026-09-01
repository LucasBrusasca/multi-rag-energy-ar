"""Smoke test of the full pipeline: retrieval -> generation -> epistemic veto.

Runs B0 (monolithic) and B1 (physical-location oracle) over the same items with
the same k, and answers one question: do the arms produce DIFFERENT answers?

If both arms receive the SAME ordered context, generation runs once: at
temperature 0 the answer is identical by construction and a second call would
only cost money.

Read-only over the database. Writes one JSON with the raw outputs.

EXPLORATORY. Not confirmatory: the items have no verified collision distractors,
the partition is not reproducible, and legal correctness is NOT scored here.

[ES] Prueba de humo del sistema completo: recuperacion -> generacion -> veto.

Corre B0 (monolitico) y B1 (oraculo de ubicacion fisica) sobre los mismos items
con el mismo k, y responde una pregunta: los brazos producen respuestas DISTINTAS?

Si los dos reciben el MISMO contexto ordenado, genera una sola vez: a temperatura
0 la respuesta es identica por construccion y la segunda llamada solo gastaria.

Solo lectura sobre la base. Escribe un JSON con las salidas crudas.

EXPLORATORIO. No confirmatorio: los items no tienen distractores verificados, la
particion no es reproducible, y aca NO se puntua correccion juridica.
"""

import argparse
import json

from multirag.config import RETRIEVAL_TOP_K
from multirag.db import conectar
from multirag.evaluation.sonda_b0_b1 import (
        ESTRATO_PREDETERMINADO,
        RAIZ_PROYECTO,
        RUTA_BORRADOR,
        RUTA_YAML,
        cargar_items_borrador,
        cargar_items_yaml,
        huella_particion,
        ubicacion_de_anclas,
        unir_items,
)
from multirag.generation.generador import generar_respuesta
from multirag.orchestration.retriever import buscar


RUTA_SALIDA = RAIZ_PROYECTO / "experimentos" / "sonda_respuestas.json"


def recuperar(pregunta: str, k: int, silos: list[str] = None) -> list[dict]:
    """Build one arm's context. silos=None -> monolithic (B0).

    Mirrors the merge rule of ranking_b1 in sonda_b0_b1, but returns the full
    chunks because the generator needs their text.

    [ES] Arma el contexto de un brazo. silos=None -> monolitico (B0).

    Replica la regla de union de ranking_b1, pero devuelve los chunks completos
    porque el generador necesita su texto.
    """
    if not silos:
        return buscar(pregunta, silo=None, k=k)

    candidatos = []

    for silo in silos:
        candidatos.extend(buscar(pregunta, silo=silo, k=k))

    candidatos.sort(
        key=lambda registro: float(registro["similitud"]),
        reverse=True,
    )

    return candidatos[:k]


def evaluar_veto(pregunta: str, respuesta: str, chunks: list[dict]) -> dict:
    """Run the epistemic veto as an AUXILIARY signal.

    LettuceDetect is not validated for Spanish regulatory text: this is not a
    primary metric. Failures are captured so the run never dies because of it.

    [ES] Corre el veto epistemico como senal AUXILIAR.

    LettuceDetect no esta validado en espanol regulatorio: no es metrica
    primaria. Los fallos se capturan para que la corrida nunca muera por esto.
    """
    try:
        from multirag.generation.veto import evaluar

        resultado = evaluar(pregunta, respuesta, chunks)

        return {
            "veto": resultado["veto"],
            "faithfulness": resultado["faithfulness"],
        }
    except Exception as error:
        return {
            "veto": None,
            "faithfulness": None,
            "error": f"{type(error).__name__}: {error}",
        }


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.
    [ES] Construye el analizador de argumentos de linea de comandos."""
    parser = argparse.ArgumentParser(
        description=(
            "Prueba de humo del sistema completo sobre el snapshot congelado. "
            "Genera respuestas con B0 y B1 y las compara."
        )
    )
    parser.add_argument(
        "--estrato",
        default=ESTRATO_PREDETERMINADO,
        help=f"Estrato a evaluar. Predeterminado: {ESTRATO_PREDETERMINADO}.",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=RETRIEVAL_TOP_K,
        help=(
            "Chunks por brazo, identico en los dos. Predeterminado: "
            f"{RETRIEVAL_TOP_K}."
        ),
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Procesa solo los primeros N items. Sirve para controlar el gasto.",
    )
    parser.add_argument(
        "--sin-veto",
        action="store_true",
        help="No ejecuta el veto. La corrida es mas rapida.",
    )
    return parser


def main() -> None:
    """Run the smoke test and write the raw outputs.
    [ES] Ejecuta la prueba de humo y escribe las salidas crudas."""
    argumentos = construir_parser().parse_args()

    items = unir_items(
        cargar_items_borrador(RUTA_BORRADOR, argumentos.estrato),
        cargar_items_yaml(RUTA_YAML, argumentos.estrato),
    )

    conexion = conectar()

    try:
        huella = huella_particion(conexion)
        print(f"huella_particion: {huella}")
        print(f"estrato         : {argumentos.estrato}")
        print(f"k por brazo     : {argumentos.k}")
        print()

        preparados = []

        for identificador, datos in items.items():
            if not datos["anclas"] or not datos["pregunta"]:
                continue

            silos, docs, ausentes = ubicacion_de_anclas(
                conexion,
                datos["anclas"],
            )

            if ausentes:
                continue

            preparados.append((identificador, datos, silos, docs))
    finally:
        conexion.close()

    if argumentos.limite:
        preparados = preparados[: argumentos.limite]

    print(f"items a procesar: {len(preparados)}")
    print()

    registros = []
    llamadas = 0

    for identificador, datos, silos, docs in preparados:
        pregunta = datos["pregunta"]
        anclas = datos["anclas"]

        contextos = {
            "B0": recuperar(pregunta, argumentos.k),
            "B1": recuperar(pregunta, argumentos.k, silos),
        }

        uids = {
            nombre: [chunk["chunk_uid"] for chunk in chunks]
            for nombre, chunks in contextos.items()
        }

        contexto_identico = uids["B0"] == uids["B1"]

        respuestas = {}

        if contexto_identico:
            respuesta = generar_respuesta(pregunta, contextos["B0"])
            llamadas += 1
            respuestas["B0"] = respuesta
            respuestas["B1"] = respuesta
        else:
            for nombre, chunks in contextos.items():
                respuestas[nombre] = generar_respuesta(pregunta, chunks)
                llamadas += 1

        brazos = {}

        for nombre in ("B0", "B1"):
            evaluacion = (
                {"veto": None, "faithfulness": None}
                if argumentos.sin_veto
                else evaluar_veto(
                    pregunta,
                    respuestas[nombre],
                    contextos[nombre],
                )
            )

            brazos[nombre] = {
                "chunk_uids": uids[nombre],
                "silos_recuperados": [
                    chunk["silo"] for chunk in contextos[nombre]
                ],
                "ancla_en_contexto": any(
                    uid in anclas for uid in uids[nombre]
                ),
                "respuesta": respuestas[nombre],
                **evaluacion,
            }

        registros.append(
            {
                "id": identificador,
                "pregunta": pregunta,
                "anclas": anclas,
                "silos_oraculo": silos,
                "document_ids": docs,
                "contexto_identico": contexto_identico,
                "respuesta_identica": respuestas["B0"] == respuestas["B1"],
                "brazos": brazos,
            }
        )

        marca = "=" if contexto_identico else "≠"
        print(
            f"[{marca}] {identificador}  "
            f"ancla_en_contexto B0={brazos['B0']['ancla_en_contexto']} "
            f"B1={brazos['B1']['ancla_en_contexto']}  "
            f"veto B0={brazos['B0']['veto']} B1={brazos['B1']['veto']}"
        )

    RUTA_SALIDA.write_text(
        json.dumps(
            {
                "huella_particion": huella,
                "estrato": argumentos.estrato,
                "k": argumentos.k,
                "llamadas_al_generador": llamadas,
                "items": registros,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    total = len(registros)

    if not total:
        print("\nNo hubo items procesables.")
        return

    identicos = sum(1 for r in registros if r["contexto_identico"])
    resp_distintas = sum(1 for r in registros if not r["respuesta_identica"])

    print()
    print(f"items procesados          : {total}")
    print(f"contexto IDENTICO         : {identicos}/{total}")
    print(f"contexto DISTINTO         : {total - identicos}/{total}")
    print(f"respuestas DISTINTAS      : {resp_distintas}/{total}")
    print(f"llamadas al generador     : {llamadas}")
    print()

    for nombre in ("B0", "B1"):
        con_ancla = sum(
            1 for r in registros if r["brazos"][nombre]["ancla_en_contexto"]
        )
        vetados = sum(
            1 for r in registros if r["brazos"][nombre]["veto"] is True
        )
        print(
            f"{nombre}: ancla en contexto {con_ancla}/{total}  "
            f"veto disparado {vetados}/{total}"
        )

    print()
    print(f"salidas crudas en: {RUTA_SALIDA}")
    print()
    print(
        "EXPLORATORIO. No se puntua correccion juridica. El veto es senal "
        "auxiliar sin validar en espanol."
    )


if __name__ == "__main__":
    main()
