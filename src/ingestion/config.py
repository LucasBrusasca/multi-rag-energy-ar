# Configuración central del pipeline.


# --- Elecciones (se eligen por comparación) ---
EMBEDDING_MODEL = "BAAI/bge-m3"
CHUNK_SENALES = ("heading","mayus")


# --- Hiperparámetros (se calibran; provisorios) ---
CHUNK_MIN_CHARS = 80
CHUNK_MAX_CHARS = 1000
RETRIEVAL_TOP_K = 3

# --- LLM: modelos por ROL (formato LiteLLM " <proveedor>/<modelo>") ---

LLM_MODELS = {
    "generator": "anthropic/claude-sonnet-4-6", # narrador con cita
    "judge": "anthropic/claude-sonnet-4-6", # juez del veto (RAGAS faithfulness)
    # "router": , # SLM local barato para rutear
    # "friction": , # razonamiento fuerte para el Red Team
}

VETO_TAU_FAITHFULNESS = 0.7

JUDGE_MAX_TOKENS = 64000


# Silos (dominios) del sistema
SILOS = ("legal", "impositivo","financiero","contable")

