from ragas.metrics.collections import Faithfulness
from llm import get_judge
from config import VETO_TAU_FAITHFULNESS

_scorer = None


def _get_scorer() -> Faithfulness:
    global _scorer
    if _scorer is None:
        _scorer = Faithfulness(llm=get_judge())
    return _scorer


def medir_faithfulness(pregunta: str, respuesta:str, chunks:list[dict]) -> float:
    contextos = [c["contenido"] for c in chunks]
    score = _get_scorer().score(
        user_input=pregunta,
        response=respuesta,
        retrieved_contexts=contextos
    ) 
    return score.value

def evaluar(pregunta: str, respuesta:str, chunks: list[dict],
    umbral: float = VETO_TAU_FAITHFULNESS) -> dict:
    f = medir_faithfulness(pregunta, respuesta, chunks)
    if f<umbral:
        return {"veto": True, "faithfulness":f, "respuesta": "No tengo evidencia suficiente para responder."}
    return {"veto": False, "faithfulness":f, "respuesta":respuesta}


if __name__ == "__main__":
    import sys
    from retriever import buscar
    from generador import generar_respuesta

    if len(sys.argv) < 2:
        print('Uso: python src/ingestion/veto.py "<tu pregunta>"')
        sys.exit(1)

    pregunta = " ".join(sys.argv[1:])
    chunks = buscar(pregunta)
    respuesta = generar_respuesta(pregunta,chunks)
    resultado = evaluar(pregunta, respuesta,chunks)

    print(f"PREGUNTA: {pregunta}\n")
    print(f"FAITHFULNESS: {resultado['faithfulness']:.3f}")
    print(f"VETO: {'SÍ - se abstiene' if resultado['veto'] else 'NO - responde'}\n")
    print(f"RESPUESTA FINAL:\n{resultado['respuesta']}")
