-- Execution ledger: the verifiable evidence trail promised by the plan (pp. 6-7).
--
-- Today a chunk can be traced back to its document. A RUN cannot be traced at
-- all: which question was asked, what the router decided, which silos it
-- opened, which fragments it delivered, what it answered, what the veto said.
-- Without that record the numbers of the thesis exist but cannot be audited,
-- and reconstructing them would mean running everything again.
--
-- Three levels, from coarse to fine:
--   ledger_corrida    one row per experimental run (its frozen configuration)
--   ledger_consulta   one row per question within a run
--   ledger_evidencia  one row per chunk delivered to the generator
--
-- WHY THERE IS NO FOREIGN KEY TO chunks:
-- the ledger is a HISTORICAL record and must outlive the snapshot. Re-ingesting
-- an artifact deletes and recreates its chunks (pipeline.py deletes by
-- artifact_id); a foreign key with ON DELETE CASCADE would erase the evidence
-- of runs already executed and reported. chunk_uid is stored as a plain value,
-- exactly as an accounting entry keeps the amount and not a pointer to it.
--
-- NOT EXECUTED by this task.
--
-- [ES] Ledger de ejecucion: la pista de evidencia verificable que promete el
-- plan (pp. 6-7).
--
-- Hoy un chunk se puede rastrear hasta su documento. Una CORRIDA no se puede
-- rastrear en absoluto: que se pregunto, que decidio el router, que silos
-- abrio, que fragmentos entrego, que respondio, que dijo el veto. Sin ese
-- registro los numeros de la tesis existen pero no son auditables, y
-- reconstruirlos implicaria volver a correr todo.
--
-- Tres niveles, de grueso a fino:
--   ledger_corrida    una fila por corrida experimental (su configuracion congelada)
--   ledger_consulta   una fila por pregunta dentro de una corrida
--   ledger_evidencia  una fila por chunk entregado al generador
--
-- POR QUE NO HAY CLAVE FORANEA A chunks:
-- el ledger es un registro HISTORICO y tiene que sobrevivir al snapshot.
-- Reingerir un artefacto borra y recrea sus chunks (pipeline.py borra por
-- artifact_id); una clave foranea con ON DELETE CASCADE borraria la evidencia
-- de corridas ya ejecutadas y reportadas. chunk_uid se guarda como valor llano,
-- igual que un asiento contable guarda el importe y no un puntero a el.
--
-- NO SE EJECUTA en esta tarea.

BEGIN;


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
-- COMMIT;
