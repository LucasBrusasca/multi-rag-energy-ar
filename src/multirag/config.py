# Configuración central del pipeline.


# --- Elecciones (se eligen por comparación) ---
EMBEDDING_MODEL = "BAAI/bge-m3"
CHUNK_SENALES = ("heading","mayus")


# --- Hiperparámetros (se calibran; provisorios) ---
CHUNK_MIN_CHARS = 80
CHUNK_MAX_CHARS = 1000
CHUNK_MAX_TOKENS = 512
RETRIEVAL_TOP_K = 3

# --- LLM: modelos por ROL (formato LiteLLM " <proveedor>/<modelo>") ---

LLM_MODELS = {
    "generator": "anthropic/claude-sonnet-4-6", # narrador con cita
    "judge": "anthropic/claude-sonnet-4-6", # juez del veto (RAGAS faithfulness)
    "router": "anthropic/claude-haiku-4-5" , # SLM local barato para rutear
    # "friction": , # razonamiento fuerte para el Red Team
}

VETO_TAU_FAITHFULNESS = 0.7

JUDGE_MAX_TOKENS = 64000

LETTUCE_MODEL = "KRLabsOrg/lettucedect-v2-mmbert-base"

VETO_TAU_CONFIANZA = 0.5

# Silos (dominios) del sistema. Cada uno describe MATERIA, no forma documental.
SILOS = {
    "legal":      "Materia jurídico-regulatoria del sector energético: organización del mercado eléctrico y de gas; quién puede generar, transportar o distribuir; concesiones, licencias, habilitaciones y pliegos; obligaciones de servicio, calidad y seguridad; régimen tarifario y audiencias públicas; facultades y procedimientos de los entes reguladores (ENRE, ENARGAS, Secretaría de Energía); contravenciones y sanciones regulatorias; contratos y litigios del sector.",
    "impositivo": "Materia tributaria: qué hechos están gravados y quién debe pagar; impuestos, tasas y contribuciones; IVA, Ganancias, Bienes Personales, Ingresos Brutos, impuestos internos y sobre combustibles; alícuotas y base imponible; retenciones, percepciones y agentes de retención; declaraciones juradas, determinación de oficio, prescripción, intereses resarcitorios y sanciones fiscales; facultades de AFIP/ARCA y organismos fiscales.",
    "contable":   "Materia contable: el registro y la exposición de la situación económica de una entidad. Estados contables y financieros (situación patrimonial, resultados, flujo de efectivo, cambios en el patrimonio); notas y anexos a los estados; activo, pasivo, patrimonio neto, ingresos, costos y resultados del período; criterios de valuación y normas contables (NIIF, RT FACPCE); registración, conciliaciones e informes de auditoría sobre los estados.",
    "financiero": "Materia financiera: instrumentos, financiamiento y análisis de valor. Emisión y colocación de deuda y capital (obligaciones negociables, prospectos, suplementos); calificaciones de riesgo crediticio; estructura de capital, apalancamiento y liquidez; valuación, proyecciones y flujos de fondos; presentaciones a inversores y análisis de desempeño; mercados, tasas y riesgo financiero.",
}

# Vocabulario controlado de materialidad del chunk, con su criterio.
# Fuente única: lo consumen el etiquetado humano y la revisión semántica.
MATERIALIDADES = {
    "sustantivo": (
        "Expresa una materia propia: una obligación, un derecho, una "
        "condición, un cálculo o un dato con contenido regulatorio, "
        "tributario, contable o financiero."
    ),
    "administrativo_no_material": (
        "Fórmula procedimental sin materia sustantiva: firmas, "
        "publicación, entrada en vigencia, archívese, comuníquese, "
        "encabezados, índices y cierres administrativos."
    ),
    "incierto": (
        "No puede determinarse leyendo este fragmento. Por ejemplo, una "
        "oración truncada o una remisión sin contenido propio."
    ),
}


CLASIFICADOR_TEMP = 0.05

ROUTER_COBERTURA = 0.70
