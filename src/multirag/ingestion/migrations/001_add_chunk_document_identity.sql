BEGIN;

ALTER TABLE chunks
    ADD COLUMN IF NOT EXISTS instrument_id TEXT,
    ADD COLUMN IF NOT EXISTS document_id TEXT,
    ADD COLUMN IF NOT EXISTS artifact_id TEXT;


CREATE INDEX IF NOT EXISTS chunks_instrument_id_idx
    ON chunks (instrument_id);


CREATE INDEX IF NOT EXISTS chunks_document_id_idx
    ON chunks (document_id);


CREATE INDEX IF NOT EXISTS chunks_artifact_id_idx
    ON chunks (artifact_id);


COMMIT;
