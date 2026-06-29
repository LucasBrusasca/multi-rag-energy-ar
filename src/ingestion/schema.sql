CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id      SERIAL PRIMARY KEY,
    silo    TEXT NOT NULL,
    silo_scores JSONB,
    titulo  TEXT,
    contenido  TEXT,
    embedding   vector(1024),
    fuente      TEXT,
    node_id     INTEGER,
    valid_from  DATE,
    valid_to    DATE,
    invalid_at  DATE
);


CREATE INDEX IF NOT EXISTS chunks_legal_hnsw  ON chunks USING hnsw (embedding vector_cosine_ops) WHERE silo = 'legal';
CREATE INDEX IF NOT EXISTS chunks_impositivo_hnsw ON chunks USING hnsw (embedding vector_cosine_ops) WHERE silo = 'impositivo';
CREATE INDEX IF NOT EXISTS chunk_financiero_hnsw ON chunks USING hnsw (embedding vector_cosine_ops) WHERE silo = 'financiero';
CREATE INDEX IF NOT EXISTS chunk_contable_hnsw ON chunks USING hnsw (embedding vector_cosine_ops) WHERE silo = 'contable';

CREATE INDEX IF NOT EXISTS chunks_silo_idx ON chunks (silo);