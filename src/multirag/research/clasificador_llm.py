"""Classify a chunk into a silo using an LLM that READS it, instead of measuring geometry.

Returns None when the answer is not a valid silo: fails loudly, never silently.

[ES] Clasifica un chunk en un silo usando un LLM que lo LEE, no que mide geometria.
Devuelve None si la respuesta no es un silo valido: falla fuerte, nunca en silencio.
"""

import re

from multirag.config import SILOS
from multirag.generation.llm import llamar_llm


def _construir_prompt(
    texto: str,
    titulo: str | None = None,
    hierarchy: list | None = None,
) -> str:
    """Build the prompt from the silo descriptions and the chunk's section path.
    [ES] Arma el prompt con las descripciones de silo y la ruta de seccion del chunk."""
    cajas = "\n".join(f"- {silo}: {desc}" for silo, desc in SILOS.items())
    nombres = " | ".join(SILOS)
    return (
        "Sos un clasificador documental del sector energetico argentino.\n"
        "Asigna el FRAGMENTO a UNO de estos dominios segun su MATERIA:\n\n"
        f"{cajas}\n\n"
        "Reglas de desempate, en orden:\n"
        "1. La FORMA del documento (ley, decreto, resolucion, contrato, balance) NO decide\n"
        "   el dominio. Decide la MATERIA de la que trata el fragmento.\n"
        "2. Norma sobre tributos -> impositivo, aunque sea una ley, decreto o resolucion.\n"
        "3. Norma sobre el mercado electrico o de gas -> legal, aunque mencione tasas,\n"
        "   impuestos o cargos.\n"
        "4. Estado contable, nota o anexo de estados -> contable, aunque hable de deuda,\n"
        "   intereses o instrumentos financieros.\n"
        "5. Prospecto, calificacion de riesgo o presentacion a inversores -> financiero,\n"
        "   aunque incluya cifras contables o clausulas legales.\n\n"
        "La UBICACION indica de que trata la seccion que contiene al fragmento. Usala como\n"
        "contexto cuando el fragmento solo sea ambiguo, pero el FRAGMENTO siempre manda.\n\n"
        f"Responde UNA SOLA PALABRA, exactamente una de estas: {nombres}\n"
        "Sin explicacion, sin puntuacion, sin comillas.\n\n"
        f"{_contexto(titulo, hierarchy)}"
        "FRAGMENTO:\n"
        f"{texto}\n\n"
        "DOMINIO:"
    )


def _contexto(titulo: str | None, hierarchy: list | None) -> str:
    """Build a compact section-path line; empty when there is no usable metadata.
    [ES] Arma una linea compacta con la ruta de seccion; vacia si no hay metadato util."""
    partes = [p.strip() for p in (hierarchy or []) if p and p.strip()]
    if titulo and titulo.strip() and titulo.strip() not in partes:
        partes.append(titulo.strip())
    if not partes:
        return ""
    return "UBICACION EN EL DOCUMENTO: " + " > ".join(partes) + "\n\n"


def _limpiar(respuesta: str) -> str:
    """Strip Qwen3-style <think> blocks and surrounding punctuation.
    [ES] Saca el bloque <think> de Qwen3 y la puntuacion de alrededor."""
    sin_think = re.sub(r"<think>.*?</think>", "", respuesta, flags=re.DOTALL)
    return sin_think.strip().lower().strip(".\"' \n")


def clasificar_llm(
    texto: str,
    titulo: str | None = None,
    hierarchy: list | None = None,
) -> str | None:
    """Return the silo assigned by the LLM, or None if the answer is not a valid silo.
    [ES] Devuelve el silo que asigna el LLM, o None si la respuesta no es un silo valido."""
    respuesta = llamar_llm(_construir_prompt(texto, titulo, hierarchy), rol="router")
    limpia = _limpiar(respuesta)
    return limpia if limpia in SILOS else None


if __name__ == "__main__":
    import sys
    import time
    texto = " ".join(sys.argv[1:])
    if not texto:
        print('Uso: python -m multirag.research.clasificador_llm "<texto a clasificar>"')
        sys.exit(1)
    inicio = time.perf_counter()
    resultado = clasificar_llm(texto)
    print(f"{resultado}   ({time.perf_counter() - inicio:.1f} seg)")
