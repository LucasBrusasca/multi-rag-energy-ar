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
SILOS = {
    "legal":      "Dominio legal y regulatorio del sector energético: leyes, decretos, resoluciones y normativa (ENRE, ENARGAS, Secretaría de Energía); contratos, concesiones, licencias y pliegos; dictámenes y opiniones legales; compliance, derechos, obligaciones, sanciones y litigios.",
    "impositivo": "Dominio impositivo y tributario: impuestos, tasas y contribuciones; retenciones y percepciones; IVA, Ganancias, Ingresos Brutos; alícuotas, régimen fiscal, AFIP/ARCA; declaraciones juradas, determinaciones, planificación y obligaciones tributarias.",
    "financiero": "Dominio financiero: finanzas corporativas, mercados e inversiones; financiamiento, deuda y capital; flujos de fondos, tasas de interés, rentabilidad y valuación; presupuestos, proyecciones e informes financieros; instrumentos y riesgo financiero.",
    "contable":   "Dominio contable: contabilidad y registración; balances y estados contables (situación patrimonial, resultados); normas contables (RT FACPCE, NIIF); activos, pasivos, patrimonio neto, ingresos y egresos; asientos, conciliaciones y auditoría.",
}


CLASIFICADOR_TEMP = 0.1

