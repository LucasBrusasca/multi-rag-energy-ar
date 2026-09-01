# Auditoría diagnóstica de la representación tabular

**Fecha:** 24-ago-2026
**Alcance:** 15 tablas de 6 documentos PDF + 1 planilla Excel + el caso completo DOC-0004.
**Condiciones respetadas:** no se reingirió, no se agregó VLM ni se cambió el OCR, no se
alteró ningún `chunk_uid`, no se tocó el experimento confirmatorio. Todo de solo lectura.

**Scripts reproducibles:**
`scripts/diagnostics/auditar_tablas.py` · `scripts/diagnostics/auditar_excel.py`
El informe por caso, generado automáticamente, está en `informe.md`. Las conversiones de
Docling quedan cacheadas en `docling/*.json` para poder re-analizar sin reconvertir.

---

## 1. Diagnóstico agregado

| clase | qué significa | tablas | proporción |
|---|---|---|---|
| **A. OCR** | caracteres o dígitos mal reconocidos | **0** | 0 % |
| **B. Estructura** | Docling relacionó mal celdas o encabezados | **10** | **67 %** |
| **C. Chunking** | Docling la tenía y nuestro pipeline la perdió | **0** | 0 % |
| **D. Retrieval** | representación completa, búsqueda fallida | **1 de 1 probado** | — |
| sin pérdida detectada | | 5 | 33 % |

**El resultado principal es que C = 0.** Cuando Docling tiene la unidad dentro de la tabla,
nuestra serialización la conserva; en las 8 tablas donde Docling la tenía, el chunk la
mantuvo. En las 7 restantes, no la tenía ninguno de los dos.

Eso **refuta la hipótesis de trabajo** con la que se inició esta auditoría —que el pipeline
propio estaba descartando contexto que Docling entregaba— al menos para unidad y período.

---

## 2. Dónde se pierde realmente la información

### 2.1 El caso DOC-0004, completo

La cadena de las cuatro etapas, para el ejemplo que originó la auditoría.

| etapa | qué pasa |
|---|---|
| **1. Documento** | `Edenor_EEFF_Consolidado_2025_09.pdf`, pág. 12. Estado de flujos de efectivo consolidado, nueve meses al 30/09/2025, expresado en millones de pesos en moneda constante. |
| **2. Docling** | Extrae la tabla **y también** la línea de unidad, pero como elementos **separados**: la unidad queda en `#/texts/2` (y otras 13 apariciones) y el `caption` de la tabla queda **vacío**. Docling **no asocia** la línea con la tabla. |
| **3. Chunks / base** | La tabla cae en el chunk `15b0fc55…` (id 3866) y la línea de unidad en `ecdb1950…` (id 3867). Son chunks distintos del mismo `DOC-0004`. El chunk de la tabla conserva el período —vía `hierarchy`, que dice «nueve meses finalizado el 30 de septiembre de 2025»— pero **no la unidad, ni la entidad, ni la base de medición**. |
| **4. Retrieval** | Ante *"¿cuál fue el flujo neto de efectivo generado por las actividades operativas de Edenor al 30 de septiembre de 2025?"*, el chunk que **contiene literalmente la respuesta** aparece en la **posición 14**. Con `RETRIEVAL_TOP_K = 3` el sistema nunca lo ve. |

| campo | valor | ¿sobrevive? |
|---|---|---|
| entidad | Edenor | ❌ solo en `fuente`, fuera del texto y fuera del embedding |
| documento | `DOC-0004` | ✅ |
| tabla | `#/tables/…` | ❌ no se persiste |
| fila / concepto | Flujo neto de efectivo generado por las actividades operativas | ✅ |
| período / columna | 30.09.25 | ✅ en el texto y en el título |
| valor | 136.110 | ✅ |
| **unidad** | millones | ❌ |
| **moneda / base** | pesos, moneda constante | ❌ |
| página / celda | pág. 12, r?/c? | ❌ (la procedencia posicional se implementó el 23-ago, aún sin reingerir) |

**Clasificación del caso: B, no C.** Docling tenía las dos piezas y no las relacionó; nuestra
serialización no puede perder una asociación que nunca recibió.

**Punto exacto de pérdida:** el `caption` de la tabla queda vacío en Docling, y la línea
`(Expresados en millones de pesos en moneda constante – Nota 3)` sobrevive como texto suelto.
Verificado: hay **14 elementos de texto** con esa declaración en el documento, y **cero**
tablas con caption entre las auditadas.

### 2.2 La falla estructural dominante: encabezados mal marcados

En `Transener_Calificacion_FIX`, `#/tables/4` (pág. 11):

- Docling marca la **fila 0 como encabezado de columna**.
- Esa fila es `['Variación del Capital de Trabajo', '(30.716)', '(32.572)', …]` — **datos, no
  encabezado**.
- El `TripletTableSerializer` emite entonces
  `"Flujo de Caja Operativo (FCO), (30.716) = 204.545"`, usando un importe como nombre de
  columna.
- El encabezado real —`Año Móvil, sept-25, 2024, 2023, 2022, 2021` y `Moneda Constante`—
  está en `#/tables/3`, **en la página anterior**: es la misma tabla lógica partida entre
  páginas, y la continuación quedó huérfana.

Esto explica el texto ininteligible que aparece en los chunks tabulares del corpus. **No es
un defecto de nuestra serialización: es fiel a lo que Docling le dice.**

En `#/tables/0` del mismo documento, el problema es el complementario: Docling marca como
encabezado la fila 2 (`Año Móvil`, `12 Meses`) y **no** la fila 1, que es la que trae las
fechas (`30/09/25`, `31/12/24`) y la unidad (`$ Millones`).

### 2.3 La falla de recuperación (D)

El chunk con la respuesta está en posición 14 de 100. Causa probable, medida: **4 chunks del
corpus comparten exactamente el mismo título** que el chunk objetivo, porque la tabla se
partió en varios fragmentos que heredan el mismo encabezado de sección. Son casi duplicados
en el espacio de embeddings y compiten entre sí; el que trae la fila buscada no se
distingue.

Además, `fuente` (la entidad) **no entra al embedding**: `embedder.py` embebe
`título + contenido`. Una consulta que nombra a Edenor no encuentra ese término en el vector.

### 2.4 El caso Excel: la falla más grave, y sin OCR de por medio

El único `.xlsx` del proyecto es `data/quarantine/descartados/1Q26.xlsx`. **Está en
cuarentena y nunca se ingirió**, así que no hay etapa 3 ni 4 que auditar. Se audita igual
porque es el único caso de encabezado jerárquico disponible.

**Leído nativamente con openpyxl: íntegro.**

| celda | contenido |
|---|---|
| `B2` | `In US$ million` — la unidad |
| `D2:F2` (combinada) | `First quarter` — el período |
| `D3` / `F3` | `2026` / `2025` — los años |
| `B4` | `Sales revenue` |
| `D4` / `F4` | `573` / `414` |

Hoja `EERR-C ing`: 222 filas × 12 columnas, **12 celdas combinadas**, **0 fórmulas**,
y **9 de 12 columnas totalmente vacías** (separadores visuales).

**Leído por Docling: destruido.**

- **251 «tablas»** para 12 hojas.
- **167 de 251 (67 %) de una sola columna**; 83 de una sola celda.
- El estado de resultados queda repartido: conceptos en `#/tables/37`, valores 2026 en la
  `38`, valores 2025 en la `39`.
- **No hay forma de reconstruir que «Selling expenses» vale −26.**

**Causa raíz:** las columnas vacías usadas como separadores visuales fragmentan la hoja.

**Clasificación: B total.** Y a diferencia del caso PDF, acá la alternativa es trivial:
openpyxl lee el archivo correctamente sin ningún modelo.

### 2.5 El PDF escaneado

`Decreto_1398_1992_Reglamentario_Electrico.pdf` es el **único** documento del corpus que
dispara OCR (`_necesita_ocr`). Resultado: **produce cero tablas**. No hay falla A que
clasificar porque no hay tabla que evaluar.

**Corrección a la documentación vigente:** `IDEAS_Y_ROADMAP.md` §5 afirma que *"no hay motor
OCR funcional instalado"*. Es falso: **RapidOCR está instalado y se ejecutó** durante esta
auditoría, cargando `ch_PP-OCRv4_rec_mobile.pth` sobre CPU.

---

## 3. Recomendación

**Corregir nuestro pipeline. No hace falta todavía un benchmark de alternativas para PDF.**

El fundamento es que la información **existe en la salida de Docling**; lo que falta es el
vínculo:

- la unidad existe, como elemento de texto, en 14 lugares del documento de Edenor;
- la grilla de celdas es correcta —índices de fila y columna coherentes— aunque las marcas de
  encabezado no lo sean;
- el orden de lectura y los `self_ref` permiten saber qué texto precede a qué tabla.

Nada de eso llega hoy a la base, porque el pipeline conserva solo `ch.text`. **Esa es la
corrección concreta**, y es nuestra, no del parser.

Con dos matices que no conviene omitir:

1. **La marca de encabezado de Docling no es confiable: falla en 10 de 15 tablas.** Cualquier
   corrección propia tiene que incluir una inferencia de encabezado propia, y guardarla
   **separada** de la de Docling para poder medir la diferencia. Por eso la propuesta de
   representación incluye `es_encabezado_inferido` aparte de `es_encabezado_columna`.
2. **Para planillas, sí corresponde cambiar de lector.** Docling destruye el `.xlsx` y
   openpyxl lo lee perfecto. La recomendación es no usar Docling para hojas de cálculo. Es
   una decisión de bajo costo y alto impacto, y no requiere benchmark: la comparación ya está
   hecha en §2.4.

**Cuándo hacerlo:** en el mismo viaje de la reingesta ya prevista por la procedencia
posicional. No antes del Golden, porque sin él no hay forma de medir si mejora algo.

**Qué NO recomienda esta auditoría:** incorporar un VLM, cambiar el motor de OCR, ni migrar de
parser para PDF. Ninguna de las tres está justificada por lo medido.

---

## 4. Límites de esta auditoría

- **15 tablas de 6 documentos** no son una muestra aleatoria: se eligieron las de más celdas
  de cada documento, y los documentos se eligieron por variedad. Sirve para diagnosticar
  mecanismos, no para estimar frecuencias sobre el corpus.
- **La clasificación B se detecta por dos señales** —filas con fecha sin marcar como
  encabezado, y celdas con dos valores pegados—. Son heurísticas: pueden marcar de más en
  tablas cuya primera columna contiene años como dato.
- **D se probó sobre una sola consulta.** Basta para demostrar que el fallo ocurre, no para
  medir con qué frecuencia.
- **La etapa 3 quedó parcialmente sin verificar**: PostgreSQL estaba caído durante la corrida
  final, así que la columna «persistido» del informe automático está vacía. El caso DOC-0004
  sí se verificó contra la base antes de la caída.
- **No hay caso de PDF escaneado con tablas** en el corpus: el único documento con OCR no
  produce ninguna.
