-- Multilabel domain membership and chunk materiality (pilot, reversible).
--
-- The canonical chunk keeps existing exactly once. Neither its content nor its
-- embedding is duplicated: membership is a relation that points back to
-- chunks.chunk_uid. The legacy column chunks.silo is preserved untouched, both
-- for compatibility and to run the A0 variant.
--
-- Retrieval NEVER selects "the latest version" on its own: every A1/A2 query
-- must receive an explicit assignment_version (and materiality_version for A2).
-- That is why no default value, no view and no trigger picks a version here.
--
-- NOT EXECUTED by this task. Applying it is a manual, separate decision.
--
-- [ES] Pertenencia multietiqueta de dominio y materialidad del chunk
-- (piloto, reversible).
--
-- El chunk canónico sigue existiendo una sola vez. No se duplica su contenido
-- ni su embedding: la pertenencia es una relación que apunta a
-- chunks.chunk_uid. La columna heredada chunks.silo se conserva intacta, por
-- compatibilidad y para ejecutar la variante A0.
--
-- La recuperación NUNCA elige "la última versión" por su cuenta: toda consulta
-- A1/A2 debe recibir una assignment_version explícita (y materiality_version
-- para A2). Por eso aquí no hay valor por defecto, vista ni disparador que
-- seleccione una versión.
--
-- NO SE EJECUTA en esta tarea. Aplicarla es una decisión manual y separada.

BEGIN;


-- Domain membership: a chunk may belong to one, several or no domains.
--
-- [ES] Pertenencia de dominio: un chunk puede pertenecer a uno, varios o
-- ningún dominio.
CREATE TABLE IF NOT EXISTS chunk_domain_membership (
    id BIGSERIAL PRIMARY KEY,

    -- Identity of the canonical chunk. ON DELETE CASCADE keeps the pilot
    -- consistent with the idempotent re-ingestion of pipeline.py, which
    -- deletes the previous chunks of an artifact before inserting the new
    -- ones: their memberships disappear with them instead of dangling.
    --
    -- [ES] Identidad del chunk canónico. ON DELETE CASCADE mantiene el piloto
    -- consistente con la reingesta idempotente de pipeline.py, que borra los
    -- chunks previos de un artefacto antes de insertar los nuevos: sus
    -- membresías desaparecen con ellos en lugar de quedar huérfanas.
    chunk_uid TEXT NOT NULL
        REFERENCES chunks (chunk_uid) ON DELETE CASCADE,

    -- Domain of config.SILOS. It is not constrained by CHECK on purpose: the
    -- taxonomy is versioned data (taxonomy_version), not a hand-written
    -- conditional frozen in the schema.
    --
    -- [ES] Dominio de config.SILOS. Deliberadamente sin CHECK: la taxonomía es
    -- un dato versionado (taxonomy_version), no un condicional escrito a mano
    -- y congelado en el esquema.
    domain_id TEXT NOT NULL,

    -- Optional evidence of the assignment. A human vote may carry no score.
    --
    -- [ES] Evidencia opcional de la asignación. Un voto humano puede no tener
    -- score.
    score DOUBLE PRECISION,

    -- What the score means: probabilidad, coseno, margen, voto_humano, etc.
    -- Open vocabulary; a score without its kind is not interpretable, so the
    -- pair is required together.
    --
    -- [ES] Qué significa el score: probabilidad, coseno, margen, voto_humano,
    -- etc. Vocabulario abierto; un score sin su tipo no es interpretable, por
    -- eso el par se exige junto.
    score_kind TEXT,

    -- How the membership was produced: humano, llm, lineal, regla, etc.
    -- [ES] Cómo se produjo la pertenencia: humano, llm, lineal, regla, etc.
    assignment_method TEXT NOT NULL,

    -- An automatic prediction is Silver, never human truth. 'confirmed' and
    -- 'rejected' record a human review; 'rejected' never participates in
    -- retrieval.
    --
    -- [ES] Una predicción automática es Silver, nunca verdad humana.
    -- 'confirmed' y 'rejected' registran revisión humana; 'rejected' no
    -- participa jamás en la recuperación.
    review_status TEXT NOT NULL DEFAULT 'automatic'
        CHECK (review_status IN ('automatic', 'confirmed', 'rejected')),

    -- Version of the run that produced this assignment. Several historical
    -- versions coexist without being mixed, because every query filters by an
    -- explicit value.
    --
    -- [ES] Versión de la corrida que produjo esta asignación. Varias versiones
    -- históricas conviven sin mezclarse, porque toda consulta filtra por un
    -- valor explícito.
    assignment_version TEXT NOT NULL,

    -- Version of the domain taxonomy the assignment refers to.
    -- [ES] Versión de la taxonomía de dominios a la que refiere la asignación.
    taxonomy_version TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chunk_domain_membership_score_con_tipo
        CHECK (score IS NULL OR score_kind IS NOT NULL),

    -- One decision per chunk, domain and version. Re-running a version is an
    -- update, not an accumulation of contradictory rows.
    --
    -- [ES] Una decisión por chunk, dominio y versión. Repetir una versión es
    -- una actualización, no una acumulación de filas contradictorias.
    CONSTRAINT chunk_domain_membership_unica
        UNIQUE (chunk_uid, domain_id, assignment_version)
);


-- Search by version and domain (A1/A2 scope).
-- [ES] Búsqueda por versión y dominio (alcance A1/A2).
CREATE INDEX IF NOT EXISTS chunk_domain_membership_version_dominio_idx
    ON chunk_domain_membership (assignment_version, domain_id, review_status);


-- Search by chunk within a version (membership ledger of a chunk).
-- [ES] Búsqueda por chunk dentro de una versión (ledger de un chunk).
CREATE INDEX IF NOT EXISTS chunk_domain_membership_chunk_version_idx
    ON chunk_domain_membership (chunk_uid, assignment_version);


-- Audit by taxonomy version.
-- [ES] Auditoría por versión de taxonomía.
CREATE INDEX IF NOT EXISTS chunk_domain_membership_taxonomia_idx
    ON chunk_domain_membership (taxonomy_version);


-- Materiality of the chunk (A2 gate).
--
-- Materiality is a property of the fragment, not of each domain: a signature
-- formula is administrative for every domain at once. Therefore it lives in a
-- separate table with one row per chunk and version, and NOT as a column of
-- chunk_domain_membership.
--
-- [ES] Materialidad del chunk (compuerta A2).
--
-- La materialidad es una propiedad del fragmento, no de cada dominio: una
-- fórmula de firma es administrativa para todos los dominios a la vez. Por eso
-- vive en una tabla separada con una fila por chunk y versión, y NO como
-- columna de chunk_domain_membership.
CREATE TABLE IF NOT EXISTS chunk_materiality (
    id BIGSERIAL PRIMARY KEY,

    chunk_uid TEXT NOT NULL
        REFERENCES chunks (chunk_uid) ON DELETE CASCADE,

    -- Controlled vocabulary of config.MATERIALIDADES.
    -- [ES] Vocabulario controlado de config.MATERIALIDADES.
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

    -- Independent from assignment_version: materiality and domain membership
    -- can be recalibrated separately.
    --
    -- [ES] Independiente de assignment_version: materialidad y pertenencia de
    -- dominio pueden recalibrarse por separado.
    materiality_version TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chunk_materiality_score_con_tipo
        CHECK (score IS NULL OR score_kind IS NOT NULL),

    CONSTRAINT chunk_materiality_unica
        UNIQUE (chunk_uid, materiality_version)
);


-- Search by version and materiality value (A2 gate).
-- [ES] Búsqueda por versión y valor de materialidad (compuerta A2).
CREATE INDEX IF NOT EXISTS chunk_materiality_version_valor_idx
    ON chunk_materiality (materiality_version, materiality, review_status);


COMMIT;


-- Reversal (do not run unless the pilot is discarded). The canonical snapshot
-- is untouched by this migration, so dropping both tables returns the database
-- to its previous state.
--
-- [ES] Reversión (no ejecutar salvo que se descarte el piloto). El snapshot
-- canónico no es alterado por esta migración, así que eliminar ambas tablas
-- devuelve la base a su estado previo.
--
-- BEGIN;
-- DROP TABLE IF EXISTS chunk_materiality;
-- DROP TABLE IF EXISTS chunk_domain_membership;
-- COMMIT;
