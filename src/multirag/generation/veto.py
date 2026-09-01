from typing import Any

from multirag.config import LETTUCE_MODEL, VETO_TAU_CONFIANZA

_detector: Any = None

def _get_detector() -> Any:
    """Lazy-load the LOCAL grounding detector (fixed weights, eval model). A pure functions of its inputs: no API, no sampling,
    no shared-server batching -> same (context, answer) yields the same spans, always.
    [ES] Carga perezosa del detector de grounding LOCAL (pesos fijos, modo eval). Función puea de sus entradas: sin API, sin sampling, sin batching de servidor -> mismo (contexto, respuesta) da los mismos spans, siempre."""
    global _detector
    if _detector is None:
        import torch
        from lettucedetect.models.inference import HallucinationDetector

        torch.set_num_threads(1)
        _detector = HallucinationDetector(method="transformer", model_path=LETTUCE_MODEL)
    return _detector

def detectar_no_respaldado(pregunta: str, respuesta: str, chunks: list[dict]) -> list[dict]:
    """Return the ANSWER spans NOT supported by the retrieved chunks (each: text, char offsets, confidence). Deterministic.
    [ES] Devuelve los tramos de la RESPUESTA NO respaldados por los chunks (cada uno: texto, offsets, confianza). Determinista."""
    contextos = [c["contenido"] for c in chunks]
    return _get_detector().predict(
        context= contextos, question=pregunta, answer=respuesta, output_format="spans"
    )

def _cobertura(respuesta: str, hallucinado: list[dict]) -> float:
    """Fraction of the answer NOT flagged as unsupported (by characters). Auditable grounding proxy for reporting.
    [ES] Fracción de la respuesta NO marcada como no-respaldada (por caracteres). Proxy de grounding auditable para reportar."""
    if not respuesta:
        return 1.0
    marcados = sum(s["end"] - s["start"] for s in hallucinado)
    return round(max(0.0, 1.0 - marcados / len(respuesta)), 3)

def medir_faithfulness(pregunta: str, respuesta: str, chunks: list[dict], umbral_confianza: float= VETO_TAU_CONFIANZA) -> float:
    """Deterministic grounding score (coverage of the answer supported by evidence). The veto DECISION uses the spans directly (see evaluar); this is the numeric summary for metrics/reporting.
    [ES] Score de grounding determinista (cobertura de la respuesta respaldada por la evidencia). La DECISIÓN del veto usa los spans directo (ver evaluar); esto es el resumen numético para métricas/reporte."""
    spans= detectar_no_respaldado(pregunta, respuesta, chunks)
    hallucinado = [s for s in spans if s["confidence"] >= umbral_confianza]
    return _cobertura(respuesta, hallucinado)

def evaluar(pregunta: str, respuesta: str, chunks: list[dict], umbral_confianza: float = VETO_TAU_CONFIANZA) -> dict:
    """Epistemic veto via LOCAL deterministic grounding (LettuceDetect). Abstain if the answer contains ANY claim NOT supported by evidence at confidence >= umbral (one ungrounded claim is enough in a regulated domain). Returns the offending spans -> fully auditable.
    [ES] Veto epistémico por grounding LOCAL determinista (LettuceDetect). Se abstiene si la respuesta contiene ALGUNA afirmación NO respaldada por la evudencia con confianza >= umbral (una sola alcanza en dominio regulado), Devuelve los spans marcados -> totalmente auditable"""
    spans = detectar_no_respaldado(pregunta, respuesta, chunks)
    hallucinado = [s for s in spans if s["confidence"] >= umbral_confianza]
    faithfulness = _cobertura(respuesta, hallucinado)
    if hallucinado:
        return {"veto": True, "faithfulness": faithfulness, "spans": spans, "hallucinado": hallucinado, "respuesta": "No tengo evidencia suficiente para responder."}
    return {"veto": False, "faithfulness": faithfulness, "spans": spans, "hallucinado": [], "respuesta": respuesta}

if __name__ == "__main__":
    import sys
    from multirag.generation.generador import generar_respuesta
    from multirag.orchestration.retriever import buscar_ruteado

    if len(sys.argv) < 2:
        print('Uso: python -m multirag.generation.veto "<tu pregunta>"')
        sys.exit(1)

    pregunta = " ".join(sys.argv[1:])
    chunks = buscar_ruteado(pregunta)
    respuesta = generar_respuesta(pregunta, chunks)
    resultado = evaluar(pregunta, respuesta, chunks)

    print(f"PREGUNTA: {pregunta}\n")
    print("GROUNDING (tramos NO respaldados por la evidencia):")
    if resultado["spans"]:
        for s in resultado["spans"]:
            marca = "VETA" if s["confidence"] >= VETO_TAU_CONFIANZA else " "
            print(f" [{marca}] conf {s['confidence']:.3f} '{s['text'].strip()}'")
    else:
            print(" (ninguno - todo respaldado)")
    print(f"\nFAITHFULNESS (cobertura respaldada): {resultado['faithfulness']:.3f}")
    print(f"VETO: {'SÍ - se abstiene' if resultado['veto'] else 'NO - responde'}\n")
    print(f"RESPUESTA FINAL:\n{resultado['respuesta']}")
