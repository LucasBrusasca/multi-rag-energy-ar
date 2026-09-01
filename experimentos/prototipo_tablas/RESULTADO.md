# Prototipo de representación table-aware

**Fecha:** 24-ago-2026
**Estado de la verdad:** `prototipo_no_validado_contra_golden`.
**Alcance:** dos casos de aceptación, verificados a mano. No es una medición sobre el corpus.

## Salvedades, antes de cualquier resultado

1. **No hay evidencia de que esto mejore la recuperación ni la respuesta.** Lo único
   demostrado es que la información sobrevive a la extracción. Que un `Multi-RAG` responda
   mejor con ella es una hipótesis distinta, y no se puede medir sin el Golden.
2. **Dos documentos no son una muestra.** Se eligieron porque son los dos casos que la
   auditoría había señalado como irrecuperables, no por representatividad.
3. **La inferencia de encabezado es una heurística de forma.** Acierta en los casos
   probados; puede fallar en una tabla cuya primera columna contenga años como dato, o en
   una tabla íntegramente textual (ver §6).
4. **No se reingirió, no se tocó la base y no cambió ningún `chunk_uid`.** Todo lo que
   sigue se produjo con scripts de solo lectura.

## 1. Dónde se pierde `TableData`, exactamente

El punto es una sola línea. En `src/multirag/ingestion/chunker.py`, dentro de
`chunk_with_docling`, el bucle sobre `troceador.chunk(dl_doc=document)` construye el dict del
chunk con `"content": ch.text` y **nunca abre `document.tables`**.

`ch.text` es la tabla ya serializada por el `TripletTableSerializer` de Docling en la forma
`fila, columna = valor`. En ese colapso se pierden, de una vez:

| lo que Docling tenía | dónde | qué pasa hoy |
|---|---|---|
| grilla con índices de fila y columna | `table.data.table_cells[].start_row_offset_idx` / `start_col_offset_idx` | se descarta |
| spans de celdas combinadas | `row_span`, `col_span` | se descarta |
| marcas de encabezado del parser | `column_header`, `row_header`, `row_section` | se descarta |
| bbox de cada celda | `table_cells[].bbox` | se descarta |
| página de la tabla | `table.prov[].page_no` | sobrevive **solo** como rango del chunk |
| caption | `table.captions` | vacío en las 15 tablas auditadas |
| orden de lectura | `document.body.children` | se descarta |

`extraer_procedencia` (agregada el 23-ago) rescata página y `self_ref` **a nivel de chunk**,
no de celda. Es procedencia suficiente para citar un párrafo y insuficiente para citar un
número.

La consecuencia concreta, en `Transener_Calificacion_FIX.pdf`: `#/tables/4` (pág. 11) es la
continuación de `#/tables/3` (pág. 10). Docling marca la fila 0 de la continuación como
encabezado de columna, pero esa fila es `Variación del Capital de Trabajo | (30.716) | …`,
que son datos. La serialización emite entonces, textualmente:

```text
Flujo de Caja Operativo (FCO), (30.716) = 204.545
```

un importe usado como nombre de columna. **Con la grilla guardada ese error es reparable sin
volver a parsear; con el texto ya colapsado, no.** Esa es la razón del prototipo.

## 2. Diseño

Tres objetos, ninguno de los cuales toca `chunks`.

### `SegmentoTabla` — una tabla FÍSICA

Una tabla de Docling, o un bloque de encabezado de una hoja de cálculo. Conserva la grilla
completa, las marcas del parser **tal cual las emitió**, y al lado nuestra propia inferencia.

- `table_segment_uid` — identidad de la tabla física.
- `table_uid` — identidad de la tabla LÓGICA (cabecera + continuaciones).
- `continuation_of` — `table_segment_uid` de la tabla que continúa, o `null`.
- `source_pages`, `hoja`, `ancla` (`#/tables/4`, `'EERR-C ing'!B40:F52`).
- `banda_encabezado`, `columna_etiqueta` — **inferencia propia**, separada de las marcas del
  parser que viven en cada `Celda`.
- `unidad` — con `origen` y `evidencia_ref`.
- `parser`, `parser_version`, `extraction_warnings`, `reglas`.

Los uid son determinísticos: `sha256(artifact_id | ancla | extraccion_version)`. Dos recetas
de extracción distintas conviven sin colisionar y sin reescribir un solo `chunk_uid`.

### `HechoTabular` — un número interpretable

Uno por celda de dato. Es la unidad citable:

`row_label` · `row_section` · `table_title` · `column_path` · `period` · `unit` · `value` ·
`value_raw` · `cell_coordinates` (fila, col, spans, coordenada, página, bbox) ·
`source_pages` · `table_uid` / `table_segment_uid` / `continuation_of` ·
`document_id` / `artifact_id` / `fuente` / `entidad` · `parser` / `parser_version` /
`extraccion_version` · `extraction_warnings` · `reglas` · `confianza`.

### Cuatro decisiones que conviene poder defender

1. **`confianza` es una etiqueta con motivo, no un número.** `alta` / `media` / `baja`,
   acompañada de la lista de reglas que se aplicaron. Un score numérico inventado sugeriría
   una calibración que no existe.
2. **`origen` de la unidad es parte del dato.** «millones» leído en el encabezado de la tabla
   y «millones» leído en un párrafo cercano no son la misma afirmación. El orden de prioridad
   es `celda_encabezado` > `caption` > `texto_adyacente` > `heredada_de_continuacion`, y el
   `self_ref` del texto que la justificó viaja con ella.
3. **Las notas se distinguen de las advertencias.** `nota:encabezado_discrepa_con_parser` mide
   al parser; no degrada la cifra. Mezclarlas haría que el 100 % de los hechos pareciera
   deficiente y taparía las advertencias que sí limitan (`celdas_colapsadas`,
   `unidad_ausente`).
4. **El supuesto de locale se declara.** `3.169` es 3169 en es-AR y 3,169 en en-US. Se lee
   es-AR —convención del corpus— y se emite `separador_de_miles_asumido_es_ar` junto al valor.
   Con los dos separadores presentes (`1.029.320,50` vs `1,029,320.50`) no hay ambigüedad y
   no se avisa nada.

### Regla de continuación: conservadora, auditable, reversible

`B` continúa a `A` solo si se cumplen **todas**:

1. mismo `artifact_id`;
2. inmediatamente consecutivas en orden de lectura;
3. `pág(B) == pág(A) + 1`;
4. mismo número de columnas;
5. `A` tiene banda de encabezado inferida y `B` **no**;
6. `B` es mayormente numérica (≥ 0,60 de sus celdas no vacías);
7. misma columna de etiqueta.

Cada condición evaluada queda registrada en `reglas`, y la primera que falla queda registrada
con su motivo (`paginas_no_consecutivas:6->10`, `tiene_encabezado_propio:[0, 1]`). El vínculo
**no fusiona nada**: los dos segmentos conservan su uid, sus páginas y sus celdas. Deshacerlo
es borrar `continuation_of`.

## 3. Caso A — Transener, tabla partida entre páginas

Verificado sobre `data/raw/Transener_Calificacion_FIX.pdf` (`DOC-0024`).

| criterio | resultado |
|---|---|
| reconocer que la tabla continúa entre páginas | ✅ `#/tables/4` → `continuation_of` = segmento de `#/tables/3`; comparten `table_uid` |
| recuperar el encabezado de la página anterior | ✅ `column_path = ('Moneda Constante(*)', 'NIIF', 'sept-25', '9 meses')` |
| no tomar «Variación del Capital de Trabajo» como encabezado | ✅ banda inferida de `#/tables/4` = vacía; la frase no aparece en ningún `column_path` |
| conservar ambas páginas como procedencia | ✅ `source_pages = (10, 11)`, más `cell_coordinates.segmento = '#/tables/4'` y su bbox |

**ANTES** — lo que hoy queda en `chunks.contenido`:

```text
Flujo de Caja Operativo (FCO), (30.716) = 204.545. Flujo de Caja Operativo (FCO),
(32.572) = 139.724. Flujo de Caja Operativo (FCO), (50.685) = 165.338. […]
```

**DESPUÉS** — el mismo número, recuperable:

```text
Transener - Cifras Consolidadas - Flujo de Caja Operativo (FCO) - periodo de 9 meses
terminado el 2025-09-30 - millones de ARS (moneda constante) - valor 139.724 -
paginas 10 y 11   [confianza: media]
```

La unidad se tomó de `#/texts/376`, `(millones de ARS, año fiscal finalizado en diciembre)`,
el texto inmediatamente anterior a `#/tables/3` en orden de lectura. El barrido hacia atrás
**frena en la tabla anterior**, para no atribuirle a una tabla la unidad de otra. La confianza
es `media`, no `alta`, precisamente porque el encabezado es heredado y la unidad no está en el
encabezado.

**Verificación externa del supuesto de locale:** la tabla dice `Deuda Corto Plazo = 3.169` en
millones de ARS. Leído es-AR son 3169 millones de ARS ≈ USD 2,3 M al tipo de cambio del
período, y `#/texts/31` del mismo documento afirma «deuda financiera de USD 2,3 millones». Es
una comprobación puntual, no un mecanismo: el prototipo **no** hace este contraste
automáticamente.

## 4. Caso B — planilla, encabezados combinados y jerárquicos

Verificado sobre `data/quarantine/descartados/1Q26.xlsx`, hojas `EERR-C ing` y `BCE ing`.

| criterio | resultado |
|---|---|
| leer con openpyxl | ✅ `parser = 'openpyxl'`, sin Docling y sin OCR |
| resolver encabezados combinados y jerárquicos | ✅ `D2:F2` combinada proyectada sobre D y F → `column_path = ('First quarter', '2026')` |
| asociar concepto, año/mes, unidad y valor | ✅ ver abajo |
| no convertir a PDF ni pasar por OCR | ✅ no se invoca ningún modelo |

```text
1Q26 - In US$ million - Selling expenses - First quarter / 2026 - millones de USD -
valor -26 - hoja 'EERR-C ing' celda D11   [confianza: alta]
```

Esto es exactamente lo que la auditoría declaró imposible por la vía de Docling: «no hay forma
de reconstruir que *Selling expenses* vale −26».

Dos cosas que el diseño resuelve y conviene no dar por obvias:

- **Las 9 columnas vacías** que usa la planilla como separadores visuales no generan hechos:
  se descartan por no tener ningún dato.
- **La hoja no es una tabla.** `EERR-C ing` repite su encabezado seis veces, una por
  conciliación. Cada repetición abre un bloque distinto, y los bloques **no** son continuación
  uno de otro. Sin eso habría seis filas llamadas `Reporting EBITDA` indistinguibles; con el
  título del bloque, cada una dice de qué segmento habla.

## 5. Corrida completa

```text
hechos totales: 503
por confianza: alta 233, media 269, baja 1
hechos con advertencia que limita el dato: 172
hechos con nota de discrepancia con el parser: 277  (todos los del PDF)
```

Desglose de advertencias:

| advertencia | hechos | qué significa |
|---|---:|---|
| `nota:encabezado_discrepa_con_parser` | 277 | en las 5 tablas del PDF la marca de Docling difiere de la inferencia propia |
| `separador_de_miles_asumido_es_ar` | 121 | valores del tipo `3.169`, leídos como miles |
| `encabezado_heredado_de` | 108 | los hechos de la continuación, con su cabecera declarada |
| `moneda_inferida_de_simbolo_pesos` | 13 | `$ Millones` leído como ARS |
| `celdas_colapsadas` | 1 | `1.029.320 1.030.565`: dos columnas fusionadas por el parser, sin valor emitido |

El 277 no es un defecto de la extracción: es la medición del hallazgo que motivó todo esto.
Se guarda para poder contarlo sobre el corpus más adelante.

## 6. Límites y casos ambiguos

1. **Tabla íntegramente textual.** Sin importes no hay forma de distinguir por forma el
   encabezado del dato. `#/tables/1` y `#/tables/2` (resoluciones y decretos) quedan marcadas
   `tabla_sin_valores_numericos` y **no producen hechos**: las sigue sirviendo su chunk de
   texto, que para ellas funciona bien. Efecto colateral: si esas dos tablas fueran una sola
   partida entre las páginas 5 y 6, el prototipo no lo detecta.
2. **Continuación huérfana no enlazable.** Si la continuación cae a dos páginas de distancia,
   o cambia el ancho, no se enlaza. Se emiten los hechos igual, con `column_path` vacío,
   `confianza: baja` y `sin_encabezado_recuperable`. Es una pérdida declarada, no silenciosa.
3. **Números en formato en-US dentro de un PDF.** `1,029.50` se reconoce; `1,029` a secas
   cae en `valor_no_numerico` y no emite hecho. Ningún documento del corpus probado lo
   presenta, pero el prospecto de MSU está en inglés y podría hacerlo.
4. **Un año como dato en la primera fila.** Una tabla cuya fila 0 sea `1998 | 2001 | 2004`
   como valores se leería como encabezado. No apareció en los casos probados; es el riesgo
   conocido de la regla `ANIO`.
5. **`fecha_fin` de un año suelto.** `2024 / 12 meses` deja `fecha_fin = null`: el documento no
   dice cuándo cierra el ejercicio dentro de la tabla. `#/texts/376` sí lo dice («año fiscal
   finalizado en diciembre»), pero componerlo sería inferir, y el prototipo no lo hace.
6. **La entidad de las CIFRAS no está en el catálogo.** `metadatos_curados.csv` tiene
   `emisor_nombre`, que para `DOC-0024` es *FIX SCR S.A.* — la calificadora, no Transener.
   Leer uno por el otro le atribuiría a FIX SCR el flujo de caja de Transener. El prototipo
   deja `entidad` en null y la acepta por parámetro. **Es una decisión de catálogo, no de
   código**, y va a `PENDIENTES_DIRECTOR.md`.
7. **Sin verificación humana.** Los dos casos los verifiqué contra el PDF y la planilla; no
   pasaron por revisión ciega ni entraron al Golden.

## 7. Cómo integrarlo sin destruir el baseline

En este orden, y **no antes del Golden**, porque sin él no hay forma de medir si mejora algo.

1. **Nada todavía en producción.** El prototipo corre como script de diagnóstico y escribe a
   `experimentos/`. El pipeline actual no cambia.
2. **Persistir en tablas nuevas** (`tabla_segmento`, `celda_tabla`, `hecho_tabular`), en la
   misma reingesta ya prevista por la procedencia posicional. `chunk_uid` como **valor**, sin
   clave foránea, igual que el ledger: la relación tiene que sobrevivir a una reingesta.
   `extraccion_version` versiona la receta; dos corridas no se mezclan.
3. **Excel entra por `openpyxl`**, en su propia rama del pipeline. Es la única decisión de
   parser que esta fase habilita, y es de bajo costo: hoy el `.xlsx` está en cuarentena y no
   se ingiere.
4. **Recién entonces, evaluar como ablación** contra el Golden, con su control. Dos variantes
   a medir **por separado**, porque mezclarlas impediría atribuir la mejora:
   - **T1** — enriquecer el bloque de contexto del generador con entidad, unidad y período
     cuando el chunk recuperado pertenece a una tabla;
   - **T2** — expansión estructural: dado un chunk con filas de la tabla `T`, traer el
     encabezado de `T` siempre.
   `E1` (expansión documental) ya existe y es otra cosa: trae el vecino por proximidad
   documental, no porque entienda que ese texto es el encabezado de esa tabla.
5. **Reversión:** eliminar las tres tablas nuevas devuelve la base a su estado previo. No se
   creó nada fuera de ellas, no se modificó `chunks` y no se tocó ningún `chunk_uid`.

## 8. Reproducir

```bash
python -m scripts.diagnostics.prototipo_tablas \
    --pdf data/raw/Transener_Calificacion_FIX.pdf \
    --excel "data/quarantine/descartados/1Q26.xlsx" \
    --hojas "EERR-C ing" "BCE ing" \
    --entidad "Transener_Calificacion_FIX.pdf=Transener"
```

```bash
python -m unittest tests.test_tablas -v
```

La conversión de Docling queda cacheada en
`experimentos/auditoria_tablas/docling_export/`; la segunda corrida no reconvierte.
