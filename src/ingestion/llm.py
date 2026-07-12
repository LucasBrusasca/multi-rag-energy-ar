import litellm
from dotenv import load_dotenv
from config import LLM_MODELS, JUDGE_MAX_TOKENS

load_dotenv()


def llamar_llm(prompt: str, rol: str = "generator") -> str:
    """Single gateway to the LLM. 'rol' selects the model in config (generator, judge). temperature=0 for max determinism.
    [ES] Única puerta al LLM. 'rol' elige el modelo en config. temperature=0 máxima trazabilidad/reproducibilidad."""
    respuesta = litellm.completion(
        model = LLM_MODELS[rol],
        messages=[{"role": "user", "content":prompt}],
        temperature=0,
    )
    return respuesta.choices[0].message.content


def get_judge():
    from ragas.llms import llm_factory
    return llm_factory(LLM_MODELS["judge"],
                       provider = "litellm", 
                       client=litellm.acompletion,
                       drop_params=True, 
                       additional_drop_params=["top_p"],
                       max_tokens=JUDGE_MAX_TOKENS)

