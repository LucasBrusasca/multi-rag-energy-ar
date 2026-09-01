-- Positional provenance of the chunk: page, structural path and offset.
--
-- The plan commits to citing "the exact source, page and paragraph" (p. 8) and
-- "the specific cell of a balance sheet" (p. 7). Docling already produces this
-- when parsing a PDF; the project was discarding it in chunker.py before it
-- reached the database.
--
-- THE chunk_uid DOES NOT CHANGE. It is the hash of `fuente + hierarchy +
-- contenido` (pipeline.py) and none of these columns enters it. The 4803
-- existing chunks keep their identity, so chunk_domain_membership,
-- chunk_materiality and every measurement already taken stay valid.
--
-- WHY `paginas` IS A LIST AND NOT A NUMBER: a merged chunk can span pages, and
-- the same text can appear more than once in a document — a repeated header, an
-- identical table row on two pages. Storing a list is what lets the citation
-- say "pages 3 and 12" instead of silently choosing the first one. It is the
-- same principle already adopted for domains: do not duplicate the chunk,
-- enrich the relation.
--
-- NOT EXECUTED by this task.
--
-- [ES] Procedencia posicional del chunk: página, ruta estructural y offset.
--
-- El plan compromete citar "la fuente exacta, página y párrafo" (p. 8) y "la
-- celda específica de un balance" (p. 7). Docling ya produce esto al parsear un
-- PDF; el proyecto lo descartaba en chunker.py antes de llegar a la base.
--
-- EL chunk_uid NO CAMBIA. Es el hash de `fuente + hierarchy + contenido`
-- (pipeline.py) y ninguna de estas columnas entra en él. Los 4803 chunks
-- existentes conservan su identidad, así que chunk_domain_membership,
-- chunk_materiality y toda medición ya tomada siguen válidas.
--
-- POR QUÉ `paginas` ES UNA LISTA Y NO UN NÚMERO: un chunk fusionado puede
-- abarcar varias páginas, y un mismo texto puede aparecer más de una vez en un
-- documento — un encabezado repetido, una fila de tabla idéntica en dos
-- páginas. Guardar una lista es lo que permite que la cita diga "páginas 3 y
-- 12" en vez de elegir la primera en silencio. Es el mismo principio ya
-- adoptado para los dominios: no duplicar el chunk, enriquecer la relación.
--
-- NO SE EJECUTA en esta tarea.

BEGIN;


ALTER TABLE chunks
    -- Every page the chunk occupies or repeats on. Empty for HTML, where the
    -- page does not exist as a concept.
    -- [ES] Todas las páginas que el chunk ocupa o en las que se repite. Vacío
    -- en HTML, donde la página no existe como concepto.
    ADD COLUMN IF NOT EXISTS paginas INTEGER[],

    -- Structural path of the Docling nodes ('#/texts/57', '#/tables/0').
    -- Always present, HTML included: for HTML it IS the equivalent of the
    -- paragraph number, and it is honest, because a rendered page would be an
    -- artifact of the browser and not a property of the document.
    -- [ES] Ruta estructural de los nodos de Docling. Siempre presente, HTML
    -- incluido: para HTML ES el equivalente del número de párrafo, y es
    -- honesto, porque una página renderizada sería un artefacto del navegador
    -- y no una propiedad del documento.
    ADD COLUMN IF NOT EXISTS doc_refs TEXT[],

    -- Character position accumulated in reading order. Docling does not give a
    -- global offset — its charspan restarts at 0 on each item — so it is
    -- computed during chunking. For a repeated text it keeps the FIRST
    -- occurrence: an offset describes one position, and the full set of
    -- locations lives in `paginas` and `doc_refs`.
    -- [ES] Posición de carácter acumulada en orden de lectura. Docling no da un
    -- offset global —su charspan reinicia en 0 en cada ítem—, así que se calcula
    -- durante el chunking. Para un texto repetido conserva la PRIMERA
    -- aparición: un offset describe una posición, y el conjunto completo de
    -- ubicaciones vive en `paginas` y `doc_refs`.
    ADD COLUMN IF NOT EXISTS offset_desde INTEGER,
    ADD COLUMN IF NOT EXISTS offset_hasta INTEGER;


-- Retrieve every chunk of a page: useful for auditing a citation and for
-- documentary expansion restricted to a section.
-- [ES] Recuperar todos los chunks de una página: sirve para auditar una cita y
-- para expansión documental acotada a una sección.
CREATE INDEX IF NOT EXISTS chunks_paginas_idx
    ON chunks USING gin (paginas);

CREATE INDEX IF NOT EXISTS chunks_doc_refs_idx
    ON chunks USING gin (doc_refs);


COMMIT;


-- Reversal. The columns are nullable and outside the chunk_uid hash, so
-- dropping them returns the table to its previous state without touching a
-- single identity.
--
-- [ES] Reversión. Las columnas son nullable y están fuera del hash del
-- chunk_uid, así que eliminarlas devuelve la tabla a su estado previo sin tocar
-- ninguna identidad.
--
-- BEGIN;
-- DROP INDEX IF EXISTS chunks_doc_refs_idx;
-- DROP INDEX IF EXISTS chunks_paginas_idx;
-- ALTER TABLE chunks
--     DROP COLUMN IF EXISTS offset_hasta,
--     DROP COLUMN IF EXISTS offset_desde,
--     DROP COLUMN IF EXISTS doc_refs,
--     DROP COLUMN IF EXISTS paginas;
-- COMMIT;
