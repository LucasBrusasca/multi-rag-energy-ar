import litellm
from dotenv import load_dotenv
from config import LLM_MODELS, JUDGE_MAX_TOKENS

load_dotenv()


def llamar_llm(prompt: str, rol: str = "generator") -> str:
    """Única puerta al LLM. 'rol' elige el modelo en config (generator, judge, ---)."""
    respuesta = litellm.completion(
        model = LLM_MODELS[rol],
        messages=[{"role": "user", "content":prompt}],
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

