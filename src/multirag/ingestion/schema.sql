CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id      SERIAL PRIMARY KEY,
    silo    TEXT NOT NULL,
    silo_scores JSONB,
    titulo  TEXT,
    contenido  TEXT,
    embedding   vector(1024),
    fuente        TEXT,
    instrument_id TEXT,
    document_id   TEXT,
    artifact_id   TEXT,
    hierarchy     TEXT[],
    node_id     INTEGER,
    valid_from  DATE,
    valid_to    DATE,
    invalid_at  DATE,
    chunk_uid TEXT UNIQUE,
    -- Positional provenance. Outside the chunk_uid hash on purpose: see
    -- migrations/004_add_chunk_provenance.sql.
    -- [ES] Procedencia posicional. Deliberadamente fuera del hash del
    -- chunk_uid: ver migrations/004_add_chunk_provenance.sql.
    paginas       INTEGER[],
    doc_refs      TEXT[],
    offset_desde  INTEGER,
    offset_hasta  INTEGER,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS chunks_paginas_idx  ON chunks USING gin (paginas);
CREATE INDEX IF NOT EXISTS chunks_doc_refs_idx ON chunks USING gin (doc_refs);

CREATE INDEX IF NOT EXISTS chunks_legal_hnsw  ON chunks USING hnsw (embedding vector_cosine_ops) WHERE silo = 'legal';
CREATE INDEX IF NOT EXISTS chunks_impositivo_hnsw ON chunks USING hnsw (embedding vector_cosine_ops) WHERE silo = 'impositivo';
CREATE INDEX IF NOT EXISTS chunk_financiero_hnsw ON chunks USING hnsw (embedding vector_cosine_ops) WHERE silo = 'financiero';
CREATE INDEX IF NOT EXISTS chunk_contable_hnsw ON chunks USING hnsw (embedding vector_cosine_ops) WHERE silo = 'contable';

CREATE INDEX IF NOT EXISTS chunks_silo_idx ON chunks (silo);

CREATE INDEX IF NOT EXISTS chunks_instrument_id_idx
    ON chunks (instrument_id);

CREATE INDEX IF NOT EXISTS chunks_document_id_idx
    ON chunks (document_id);

CREATE INDEX IF NOT EXISTS chunks_artifact_id_idx
    ON chunks (artifact_id);

-- Multilabel domain membership and chunk materiality (pilot).
-- Mirror of migrations/002_add_chunk_domain_memberships.sql, for fresh
-- installations. The canonical chunk exists exactly once: neither content nor
-- embedding is duplicated, and chunks.silo is preserved for A0.
--
-- [ES] Pertenencia multietiqueta de dominio y materialidad del chunk (piloto).
-- Espejo de migrations/002_add_chunk_domain_memberships.sql, para
-- instalaciones desde cero. El chunk canónico existe una sola vez: no se
-- duplica contenido ni embedding, y chunks.silo se conserva para A0.

CREATE TABLE IF NOT EXISTS chunk_domain_membership (
    id BIGSERIAL PRIMARY KEY,
    chunk_uid TEXT NOT NULL
        REFERENCES chunks (chunk_uid) ON DELETE CASCADE,
    domain_id TEXT NOT NULL,
    score DOUBLE PRECISION,
    score_kind TEXT,
    assignment_method TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'automatic'
        CHECK (review_status IN ('automatic', 'confirmed', 'rejected')),
    assignment_version TEXT NOT NULL,
    taxonomy_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chunk_domain_membership_score_con_tipo
        CHECK (score IS NULL OR score_kind IS NOT NULL),
    CONSTRAINT chunk_domain_membership_unica
        UNIQUE (chunk_uid, domain_id, assignment_version)
);

CREATE INDEX IF NOT EXISTS chunk_domain_membership_version_dominio_idx
    ON chunk_domain_membership (assignment_version, domain_id, review_status);

CREATE INDEX IF NOT EXISTS chunk_domain_membership_chunk_version_idx
    ON chunk_domain_membership (chunk_uid, assignment_version);

CREATE INDEX IF NOT EXISTS chunk_domain_membership_taxonomia_idx
    ON chunk_domain_membership (taxonomy_version);

-- Materiality is a property of the chunk, not of each domain.
-- [ES] La materialidad es propiedad del chunk, no de cada dominio.
CREATE TABLE IF NOT EXISTS chunk_materiality (
    id BIGSERIAL PRIMARY KEY,
    chunk_uid TEXT NOT NULL
        REFERENCES chunks (chunk_uid) ON DELETE CASCADE,
    materiality TEXT NOT NULL
        CHECK (
            materiality IN (
                'sustantivo',
                'administrativo_no_material',
                'incierto'
            )
        ),
    score DOUBLE PRECISION,
    score_kind TEXT,
    assignment_method TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'automatic'
        CHECK (review_status IN ('automatic', 'confirmed', 'rejected')),
    materiality_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chunk_materiality_score_con_tipo
        CHECK (score IS NULL OR score_kind IS NOT NULL),
    CONSTRAINT chunk_materiality_unica
        UNIQUE (chunk_uid, materiality_version)
);

CREATE INDEX IF NOT EXISTS chunk_materiality_version_valor_idx
    ON chunk_materiality (materiality_version, materiality, review_status);



-- Execution ledger (query -> decision -> evidence -> answer -> veto).
-- Mirror of migrations/003_add_execution_ledger.sql, for fresh installations.
-- ledger_evidencia deliberately has NO foreign key to chunks: the ledger is a
-- historical record and must survive a re-ingestion of the snapshot.
--
-- [ES] Ledger de ejecucion (consulta -> decision -> evidencia -> respuesta -> veto).
-- Espejo de migrations/003_add_execution_ledger.sql, para instalaciones desde cero.
-- ledger_evidencia deliberadamente NO tiene clave foranea a chunks: el ledger es un
-- registro historico y tiene que sobrevivir a una reingesta del snapshot.

-- One experimental run, with the configuration that governed it.
-- [ES] Una corrida experimental, con la configuracion que la goberno.
CREATE TABLE IF NOT EXISTS ledger_corrida (
    corrida_id TEXT PRIMARY KEY,

    -- What was being compared. B0/B1/B2 are the retrieval arms; A and E are
    -- the orthogonal assignment and expansion variants.
    -- [ES] Que se estaba comparando. B0/B1/B2 son los brazos de recuperacion;
    -- A y E son las variantes ortogonales de asignacion y expansion.
    brazos TEXT[] NOT NULL,
    variante_asignacion TEXT NOT NULL DEFAULT 'A0',
    variante_expansion TEXT NOT NULL DEFAULT 'E0',
    assignment_version TEXT,
    materiality_version TEXT,

    -- Fingerprint of the frozen classifier recipe
    -- (multirag.research.receta_clasificador). It is what lets anyone verify
    -- months later WHICH classifier produced the partition this run used.
    -- [ES] Huella de la receta congelada del clasificador. Es lo que permite
    -- verificar meses despues CUAL clasificador produjo la particion que uso
    -- esta corrida.
    receta_clasificador_sha256 TEXT,

    -- Everything the protocol requires to be identical across arms.
    -- [ES] Todo lo que el protocolo exige identico entre brazos.
    k_final INTEGER NOT NULL,
    modelo_generador TEXT,
    modelo_router TEXT,
    modelo_embedding TEXT,
    prompt_generador_sha256 TEXT,
    veto_mecanismo TEXT,
    veto_umbral DOUBLE PRECISION,

    -- Which question set, and which stage. Mixing development and confirmatory
    -- questions in one analysis invalidates the test.
    -- [ES] Que conjunto de preguntas, y que etapa. Mezclar preguntas de
    -- desarrollo y confirmatorias en un analisis invalida el test.
    conjunto_preguntas TEXT,
    etapa TEXT CHECK (etapa IN ('desarrollo', 'piloto', 'confirmatorio')),

    semilla INTEGER,
    snapshot TEXT,
    observaciones TEXT,
    creada_en TIMESTAMPTZ NOT NULL DEFAULT now()
);


CREATE INDEX IF NOT EXISTS ledger_corrida_etapa_idx
    ON ledger_corrida (etapa, creada_en);


-- One question, executed by one arm, within one run.
-- [ES] Una pregunta, ejecutada por un brazo, dentro de una corrida.
CREATE TABLE IF NOT EXISTS ledger_consulta (
    id BIGSERIAL PRIMARY KEY,

    corrida_id TEXT NOT NULL
        REFERENCES ledger_corrida (corrida_id) ON DELETE CASCADE,

    -- Identifier of the Golden item, so the run can be joined back to the
    -- human reference without copying it.
    -- [ES] Identificador del item del Golden, para poder unir la corrida con
    -- la referencia humana sin copiarla.
    item_golden TEXT,
    estrato TEXT,
    pregunta TEXT NOT NULL,

    brazo TEXT NOT NULL,

    -- The routing decision, kept as it was made: which silos were opened, with
    -- which scores, and whether the gate considered the question ambiguous.
    -- Reconstructing this afterwards from the model is impossible.
    -- [ES] La decision de ruteo, tal como se tomo: que silos se abrieron, con
    -- que scores, y si el gate considero ambigua la pregunta. Reconstruir esto
    -- despues a partir del modelo es imposible.
    silos_abiertos TEXT[],
    router_scores JSONB,
    router_modo TEXT,
    router_entropia DOUBLE PRECISION,
    router_margen DOUBLE PRECISION,

    respuesta TEXT,
    abstuvo BOOLEAN,

    -- The veto: whether it fired, why, and the exact spans it flagged. Storing
    -- the spans is what makes the veto auditable instead of a bare number.
    -- [ES] El veto: si se activo, por que, y los tramos exactos que marco.
    -- Guardar los tramos es lo que vuelve al veto auditable en lugar de un
    -- numero pelado.
    veto_activado BOOLEAN,
    veto_spans JSONB,
    faithfulness DOUBLE PRECISION,

    latencia_ms INTEGER,
    tokens_entrada INTEGER,
    tokens_salida INTEGER,
    costo_usd DOUBLE PRECISION,

    registrada_en TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- One arm answers each question once per run.
    -- [ES] Un brazo responde cada pregunta una vez por corrida.
    CONSTRAINT ledger_consulta_unica
        UNIQUE (corrida_id, item_golden, brazo)
);


CREATE INDEX IF NOT EXISTS ledger_consulta_corrida_idx
    ON ledger_consulta (corrida_id, brazo);

CREATE INDEX IF NOT EXISTS ledger_consulta_item_idx
    ON ledger_consulta (item_golden);


-- One chunk delivered to the generator, in the order it was delivered.
-- [ES] Un chunk entregado al generador, en el orden en que se entrego.
CREATE TABLE IF NOT EXISTS ledger_evidencia (
    id BIGSERIAL PRIMARY KEY,

    consulta_id BIGINT NOT NULL
        REFERENCES ledger_consulta (id) ON DELETE CASCADE,

    -- Position in the delivered context. Order matters: a rank-aware precision
    -- metric cannot be computed from an unordered set.
    -- [ES] Posicion en el contexto entregado. El orden importa: una metrica de
    -- precision sensible al rango no se puede calcular sobre un conjunto sin
    -- orden.
    posicion INTEGER NOT NULL,

    -- Plain value, NOT a foreign key: see the note at the top of this file.
    -- [ES] Valor llano, NO clave foranea: ver la nota al principio del archivo.
    chunk_uid TEXT NOT NULL,

    -- Documentary identity copied at delivery time, so the trail survives even
    -- if the snapshot is regenerated.
    -- [ES] Identidad documental copiada al momento de la entrega, para que la
    -- pista sobreviva aunque se regenere el snapshot.
    document_id TEXT,
    instrument_id TEXT,
    artifact_id TEXT,
    fuente TEXT,

    -- Inherited physical silo, and the domains the chunk was actually
    -- retrieved through. They are different things and both are needed to
    -- measure contamination.
    -- [ES] Silo fisico heredado, y los dominios por los que el chunk fue
    -- efectivamente recuperado. Son cosas distintas y hacen falta las dos para
    -- medir contaminacion.
    silo TEXT,
    dominios_recuperacion TEXT[],
    origen_recuperacion TEXT,

    similitud DOUBLE PRECISION,

    CONSTRAINT ledger_evidencia_unica
        UNIQUE (consulta_id, posicion)
);


CREATE INDEX IF NOT EXISTS ledger_evidencia_consulta_idx
    ON ledger_evidencia (consulta_id, posicion);

CREATE INDEX IF NOT EXISTS ledger_evidencia_chunk_idx
    ON ledger_evidencia (chunk_uid);

CREATE INDEX IF NOT EXISTS ledger_evidencia_documento_idx
    ON ledger_evidencia (document_id);


COMMIT;


-- Reversal (only if the ledger is discarded). It creates nothing outside these
-- three tables, so dropping them returns the database to its previous state.
--
-- [ES] Reversion (solo si se descarta el ledger). No crea nada fuera de estas
-- tres tablas, asi que eliminarlas devuelve la base a su estado previo.
--
-- BEGIN;
-- DROP TABLE IF EXISTS ledger_evidencia;
-- DROP TABLE IF EXISTS ledger_consulta;
-- DROP TABLE IF EXISTS ledger_corrida;
--
