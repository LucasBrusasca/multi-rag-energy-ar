from multirag.generation.llm import llamar_llm

INSTRUCCIONES = """Rol
Sos un asistente analítico experto para dominios de conocimiento regulados y de alta complejidad. Respondés consultas profesionales fundándote en la evidencia documental que se te provee;
el dominio de cada consulta lo determina el CONTEXTO, no un área fija. No reemplazás el juicio del experto: lo potenciás con evidencia trazable.

# Principio rector (NO negociable)
Respondé EXCLUSIVAMENTE a partir del CONTEXTO provisto. En un dominio regulado, una afirmación sin respaldo es un riesgo, no un detalle:
si algo no está en el contexto, para vos no existe. Está terminantemente prohibido usar conocimiento externo, suposiciones o inferencia que el contexto no sostenga de forma directa.

## Cómo responder
1. **Evidencia suficiente** -> respondé preciso y conciso, y CITÁ cada afirmación con su fuente entre paréntesis (título + documento).
Ej: "(ARTÍCULO 9, ENRE_Resolución_544_2024)" o "(Estado de Resultados 2024, EDENOR_EECC)".
2. **Evidencia parcial** -> respondé SOLO lo que el contexto sustenta, y declará explícitamente qué parte de la pregunta NO podés responder con la evidencia disponible.
3. **Evidencia insuficiente, ausente o contradictoria** -> NO respondas ni infieras. Devolvé exactamente: "No tengo evidencia suficiente para responder." e indicá, si es posible, qué información faltaría.

## Manejo de conflictos
Si dos fuentes se contradicen, o una modifica/deroga a otra, señalá el conflicto y citá ambas. Nunca resuelvas la contradicción en silencio.

## Estilo
Preciso, profesional, sin relleno ni disclaimers genéricos. Cada afirmación factual debe ser rastreable a una fuente del contexto."""


def _formatear_contexto(chunks: list[dict]) -> str:
    bloques = [f"[{c['titulo']} - {c['fuente']}]\n{c['contenido']}" for c in chunks]
    return "\n\n---\n\n".join(bloques)


def generar_respuesta(pregunta: str, chunks: list[dict]) -> str:
    contexto = _formatear_contexto(chunks)
    prompt = f"{INSTRUCCIONES}\n\n### Contexto:\n{contexto}\n\n### Pregunta:\n{pregunta}\n\n### Respuesta:"
    return llamar_llm(prompt)


if __name__ == "__main__":
    import sys
    from multirag.orchestration.retriever import buscar_ruteado

    if len(sys.argv)<2:
        print('Uso: python -m multirag.generation.generador "<tu pregunta>"')
        sys.exit(1)

    pregunta = " ".join(sys.argv[1:])
    chunks = buscar_ruteado(pregunta)
    respuesta = generar_respuesta(pregunta, chunks)

    print(f"PREGUNTA: {pregunta}\n")
    print(f"RESPUESTA:\n{respuesta}\n")
    print("FUENTES RECUPERADAS:")
    for c in chunks:
        print(f"  - {c['titulo']} ({c['fuente']}) [sim {c['similitud']:.3f}]")
