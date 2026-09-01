# Estado verificado consolidado — 16-ago-2026

> **Qué es este archivo.** Una lectura consolidada de la documentación canónica,
> con la fuente indicada para cada dato. Se produjo por pedido expreso.
>
> **Qué NO es.** No es documentación canónica. No reemplaza ni actualiza
> `ESTADO_VERIFICADO.md`, `DECISIONES_VIGENTES.md` ni ningún otro documento de
> `docs/`. Si contradice a uno de ellos, manda el de `docs/` según la regla de
> autoridad de `docs/README.md`.
>
> **Método.** Lectura en solo lectura de `PLAN_APROBADO.pdf` (23 pp.),
> `ESTADO_VERIFICADO.md`, `DECISIONES_VIGENTES.md`, `PENDIENTES_DIRECTOR.md`,
> `IDEAS_Y_ROADMAP.md`, `PROTOCOLO_EXPERIMENTAL.md`, `PROTOCOLO_GOLDEN.md`,
> `README.md` y `experimentos/`. No se consultó PostgreSQL ni se ejecutó código.
>
> **Orden de autoridad aplicado:** PLAN > ESTADO_VERIFICADO > DECISIONES >
> IDEAS_Y_ROADMAP.

## Leyenda de fuentes

| marca | archivo |
|---|---|
| `[PLAN p.N]` | `docs/PLAN_APROBADO.pdf`, página N |
| `[EV §N]` | `docs/ESTADO_VERIFICADO.md`, sección N (fechado 13-ago-2026) |
| `[DEC §N]` | `docs/DECISIONES_VIGENTES.md`, sección N (fechado 1-ago-2026) |
| `[PEND]` | `docs/PENDIENTES_DIRECTOR.md` (borrador para revisión) |
| `[IDEAS §N]` | `docs/IDEAS_Y_ROADMAP.md`, sección N |
| `[PEXP]` | `docs/PROTOCOLO_EXPERIMENTAL.md` (v1.2, 09-ago-2026) |
| `[PGOLD]` | `docs/PROTOCOLO_GOLDEN.md` (v0.7, borrador) |
| `[LECC]` | `experimentos/LECCIONES_METODOLOGICAS.md` |
| `[README]` | `docs/README.md` |

---

## 1. Corpus vigente

### 1.1 Snapshot activo

| dato | valor | fuente |
|---|---|---|
| Snapshot | v2 exploratorio, congelado el 9-ago-2026 | `[EV §1.1]` |
| Chunks | **4.789** | `[EV §1.1]` |
| Documentos | **24** | `[EV §1.1]` |
| Artefactos | **24** | `[EV §1.1]` |
| `chunk_uid` únicos y no nulos | 4.789 / 4.789 | `[EV §1.1]` |
| Motor | PostgreSQL con `pgvector`, tabla física `chunks` | `[EV §1.1]` |
| Índices | HNSW parciales por silo, físicamente verificados | `[EV §1.1]` |
| Huella determinista de la partición `chunk_uid → silo` | `630c6299540161e437828ae5590a4a8fb57622bb4d13191063ad376a7f61e4ac` | `[EV §1.1]` |

### 1.2 Distribución por silo

| silo | chunks | fuente |
|---|---:|---|
| financiero | 1.570 | `[EV §1.1]` |
| impositivo | 1.352 | `[EV §1.1]` |
| contable | 1.038 | `[EV §1.1]` |
| legal | 829 | `[EV §1.1]` |
| **total** | **4.789** | suma verificada |

### 1.3 Embeddings

| dato | valor | fuente |
|---|---|---|
| Modelo | `BAAI/bge-m3`, compartido por los cuatro silos | `[EV §1.1]`, `[DEC §4]` |
| Dimensión | **1.024**, densos | `[EV §1.1]`, `[DEC §4]` |
| Salidas sparse y multi-vector/ColBERT | **No se calculan ni persisten.** El código productivo guarda solo la representación densa | `[EV §4]`, `[IDEAS §1]` |

### 1.4 Temperatura del clasificador — **NO resuelta**

| dato | valor | fuente |
|---|---|---|
| Snapshot v1 generado con | `CLASIFICADOR_TEMP = 0.1` | `[DEC §6]` |
| Código actual declara | `CLASIFICADOR_TEMP = 0.05` | `[DEC §6]`, `[EV §3]` |
| Scores persistidos del v2 | "se parecen a una corrida con temperatura aproximada `0.1`" | `[EV §3]` |
| Valor congelado único | **No existe** | `[DEC §6]` |
| Regla activa | **Prohibido actualizar `silo` o `silo_scores`** hasta congelar receta, temperatura, prototipos y versión | `[DEC §6]`, `[EV §3]` |

**Respuesta directa: la divergencia 0.1 vs 0.05 sigue abierta.** La resolución
exige comparar y elegir el valor sobre desarrollo, versionar los prototipos y
emitir un manifest nuevo antes de cualquier reclasificación `[DEC §6]`.

### 1.5 Advertencias sobre el corpus

1. **El snapshot no sirve para el test confirmatorio.** La partición no es
   regenerable por recomputación: los prototipos del clasificador dependieron de
   los chunks existentes al comienzo de cada tanda y quedaron cacheados. Textual:
   *"solo está autorizado para diagnóstico exploratorio, no para el test
   confirmatorio"* `[EV §1.1]`.
2. **La base viva ya diverge del snapshot.** Cuatro documentos piloto
   (`DOC-0025` a `DOC-0028`) fueron ingeridos como 14 chunks adicionales `[EV §1.3]`.
3. **Los 24 registros del catálogo conservan `estado_inclusion = pendiente_revision`**,
   por lo que sus dominios documentales son propuestas descriptivas, no verdad
   humana confirmada `[EV §1.2]`.
4. **398 HTML de InfoLEG están normalizados pero NO ingeridos.** No se consideran
   corpus experimental hasta curar inclusión, fijar identidades, resolver
   metadatos y emitir un snapshot nuevo `[EV §1.3]`.
5. **Brecha con el plan:** el plan estima un corpus piloto de **300 a 500
   documentos** `[PLAN p.19]`. Hoy hay 24 ingeridos.

---

## 2. Hipótesis y aporte, tal como están redactados hoy

### 2.1 Objetivo general — textual del plan

> «Diseñar una arquitectura de sistema Multi-RAG Multimodal con Orquestación
> Reflexiva, fundamentada en la Tri-System Theory como un Sistema 3 de cognición
> artificial externa, destinada a la gestión eficiente del conocimiento en
> dominios corporativos de alta complejidad, mitigando el riesgo de entrega
> cognitiva (cognitive surrender) y optimizando la trazabilidad fáctica de la
> información en comparación con los enfoques monolíticos convencionales.»
> `[PLAN p.12]`

### 2.2 Objetivos específicos — textual del plan `[PLAN p.12]`

1. «Caracterizar la estructura semántica y ontológica de los dominios Financiero,
   Legal, Contable e Impositivo, con el fin de definir estrategias de
   preprocesamiento, chunking adaptativo y modelos de embedding especializados
   que minimicen la colisión semántica en el espacio latente.»
2. «Diseñar la arquitectura lógica y funcional del sistema integrando índices
   vectoriales independientes y un componente de Orquestación Reflexiva con
   Control de Confianza; este núcleo operará bajo un modelo de doble ruta basado
   en métricas de entropía de Shannon (H(p) > h) y márgenes de confianza
   (Δp < τ) para forzar la reactivación del procesamiento deliberativo
   (Sistema 2) del experto ante escenarios de alta incertidumbre.»
3. «Desarrollar un prototipo funcional que implemente capacidades de
   procesamiento multimodal nativo para la interpretación de documentos
   complejos, utilizando técnicas de parsing estructural y visión artificial
   validadas mediante checksums matemáticos para asegurar la integridad
   topológica de los datos y mitigar alucinaciones visuales.»
4. «Validar el desempeño del sistema mediante un protocolo experimental
   contrastado contra baselines de RAG monolítico, evaluando la capacidad de la
   arquitectura para preservar la autonomía epistémica y la retención de
   conocimientos del usuario en comparación con asistentes de respuesta directa.»

### 2.3 Variables declaradas `[PLAN p.20]`

- **Independiente:** Arquitectura del Sistema (RAG Monolítico Genérico vs.
  Multi-RAG con Orquestación Reflexiva).
- **Dependientes (rendimiento):** Context Precision, Faithfulness, Latencia.
- **Dependientes (seguridad cognitiva):** Tasa de Activación de la Zona Gris,
  Routing Accuracy.

### 2.4 Norte operativo vigente

> «Evaluar si una arquitectura Multi-RAG gobernada puede reducir la contaminación
> o colisión semántica interdominio y producir respuestas mejor fundamentadas que
> un RAG monolítico, sin degradar de forma inaceptable la recuperación.
> La superioridad de Multi-RAG es una hipótesis a demostrar, no una conclusión
> asumida.» `[DEC §1]`

### 2.5 ⚠️ La hipótesis NO está congelada

`[PEND]`, primera fila de la matriz, pide una decisión del director todavía no
tomada: confirmar que lo que se contrasta será **ventaja bajo colisión semántica
interdominio**, no superioridad universal del Multi-RAG. Recomendación
registrada: formular una hipótesis condicional y falsable, con escenarios donde
pueda ganar, empatar o perder.

`[PEND]` cierra con: *«No debe interpretarse el silencio como aprobación»* y
*«El experimento confirmatorio se ejecutará cuando los acuerdos anteriores y los
protocolos estén congelados»*.

---

## 3. Resultados citables y resultados prohibidos

### 3.1 Citables con número — hechos de implementación y auditoría

Ninguno de estos es un resultado de desempeño del sistema.

| dato | valor | fuente |
|---|---|---|
| Chunks / documentos / artefactos del snapshot | 4.789 / 24 / 24 | `[EV §1.1]` |
| Distribución por silo | ver §1.2 | `[EV §1.1]` |
| Pruebas automatizadas de la reorganización | 50 exitosas | `[EV §0]` |
| Selección InfoLEG | 400 registros seleccionados | `[EV §1.3]`, `[EV §5.2]` |
| HTML presentes | 398 de 400 | `[EV §1.3]` |
| Faltantes (HTTP 403) | 2: normas `317876` y `419824` | `[EV §5.2]` |
| Extras de descarga histórica | 20 archivos, 12 duplicados binarios, 8 sin decidir | `[EV §5.2]` |
| Normalización InfoLEG | 2.370 encabezados promovidos; equivalencia visible exacta en 394, diferencias de espaciado en 4 | `[EV §1.3]` |
| Archivos vacíos / no HTML / páginas de error | 0 / 0 / 0 | `[EV §5.2]` |

### 3.2 Prohibido citar — explícito en la documentación

| qué | motivo | fuente |
|---|---|---|
| **98 %, 84 %, 70 % y p-valores de la campaña 24–26 jul** | *«no deben usarse en la tesis hasta ser reproducidos con un protocolo congelado»* | `[EV §5]` |
| Familia «dosis de contaminación» | detector de cita intrusa defectuoso; el efecto no quedó establecido | `[LECC]` |
| Familia «abstención y fusión falsa» | tamaño insuficiente, sin pares discordantes | `[LECC]` |
| Consultas creadas desde títulos de chunks | fuga entre consulta y corpus | `[LECC]` |
| Pureza geométrica con etiquetas automáticas | circularidad entre representación y verdad | `[LECC]` |
| PCA o blanqueo por silo | no equivalen a embeddings expertos entrenados | `[LECC]` |
| Split simple por chunk | fuga documental | `[LECC]` |
| Router LLM con salida truncada o parser preliminar | arnés inválido | `[LECC]` |

### 3.3 Exploratorio — no contrasta la hipótesis, no debe presentarse como evidencia

| observación | límite declarado | fuente |
|---|---|---|
| B0/B1 con al menos un ancla en 10/14 ítems; 9/14 contextos y respuestas idénticos; ningún veto activado (k=3) | *«no demuestra equivalencia ni calidad»* | `[EV §5.1]` |
| B1d con 10/14 Hit@1 y 12/14 Hit@3 | *«no debe describirse como que "filtrar por documento gana" sin intervalo de incertidumbre, test independiente y control del oráculo»* | `[EV §5.1]` |
| 10/24 documentos multidominio y 8/24 en los cuatro dominios | todas las filas siguen pendientes de revisión; *«señal para diseñar la validación, no una tasa confirmada»* | `[EV §5.1]` |
| Piloto de sensibilidad del clasificador (centroides 14/14, descripciones 10/14, híbridas 12–13/14) | *«miden sensibilidad a la política de prototipos, no exactitud»* | `[EV §5.3]` |
| Coseno vs dominio humano: normativo 92 %, no normativo 11 %; contable 1/6, financiero 0/3 | medición exploratoria de 22 fuentes; diagnóstico de rumbo, no resultado de tesis | `[DEC §6]` |

### 3.4 Sobre «el benchmark silver quemado»

**No encontré ese término en el repositorio.** Búsqueda de `quemad` en todos los
`.md`, `.yaml` y `.json`: cero coincidencias. La palabra `silver` aparece
únicamente como la capa de metadatos Bronze/Silver en
`GUIA_ARQUITECTURA_Y_ESTUDIO.md`, no como un benchmark.

Lo más cercano a «un benchmark que quedó quemado» son dos cosas distintas:

1. **La campaña 24–26 jul** — sus porcentajes y p-valores están explícitamente
   prohibidos hasta reproducirlos con protocolo congelado `[EV §5]`, y sus siete
   familias de resultados figuran como retractaciones vigentes `[LECC]`.
2. **El snapshot v2** — quemado en otro sentido: su partición no es regenerable,
   así que sirve para diagnóstico pero **no** para el test confirmatorio
   `[EV §1.1]`.

Si te referías a otra cosa, precisala y la busco.

---

## 4. Arquitectura: implementado, a medias y roadmap

### 4.1 Implementado y corriendo `[EV §2]`

- Ingesta documental y chunking.
- Embeddings compartidos con BGE-M3.
- Clasificación contextual de cada chunk y persistencia de su silo.
- Recuperación monolítica y recuperación filtrada por silo.
- Router con decisión top-1/top-2 mediante intención y zona gris.
- Veto epistémico v1 (LettuceDetect).
- Catálogo objetivo con SHA-256 e identidad por capas.
- Vinculación persistida de los chunks con su documento y artefacto de origen.

### 4.2 A medias — existe pero no gobierna, o está declarado y no conectado

| componente | qué falta exactamente | fuente |
|---|---|---|
| `ROUTER_COBERTURA` | declarado, pero el router no lo utiliza | `[EV §3]`, `[IDEAS §2]` |
| `_evidencia_por_silo()` | implementado como sonda aislada; **no interviene** en `buscar_ruteado()` | `[EV §2]`, `[EV §3]` |
| Gate por entropía y margen | la zona gris existe; la **calibración está pendiente** y debe congelarse antes del test | `[IDEAS §2]` |
| Veto epistémico | LettuceDetect implementado pero **no validado para español regulatorio**; no puede ser métrica primaria hasta calibrarlo | `[DEC §5]`, `[EV §6]` |
| Metadata Ledger | existe catálogo por `artifact_id` y trazabilidad parcial; **no existe el ledger de ejecución** consulta → decisión → evidencia | `[IDEAS §3]` |
| Identidad documental por capas | el catálogo distingue las cuatro capas; `instrument_id` y `document_id` esperan curación humana | `[IDEAS §3]`, `[DEC §2.1]` |
| `schema.sql` | usa `CREATE TABLE IF NOT EXISTS`; **no migra** una tabla existente | `[EV §3]` |
| Prototipos del clasificador | dependen del estado inicial de la base y quedan cacheados durante el proceso | `[EV §3]` |

### 4.3 Roadmap — no demostrado `[EV §4]`, con su estado en el plan

| línea | ¿comprometida en el plan? | estado |
|---|---|---|
| Embedders especializados / adapters LoRA por dominio | **Sí**, p. 5 | no implementado; B0/B1/B2 comparten BGE-M3 `[DEC §4]`, `[DEC §10]` |
| Interoperabilidad MCP | **Sí**, pp. 4–5 | no implementada; la segregación es lógica en PostgreSQL `[IDEAS §1]`, `[DEC §14]` |
| Multimodalidad, RAPTOR, ColPali, checksums | **Sí**, pp. 4, 6, 9–10 | sin demostración experimental congelada `[EV §6]`, `[PEND]` |
| Caché semántico y tiering de modelos | **Sí**, pp. 7, 9–11 | ninguno implementado como política del sistema `[PEND]` |
| Veto basado en RAGAS | **Sí**, p. 9 | sustituido por LettuceDetect, sin acuerdo `[DEC §5]` |
| Fuentes sintéticas o anonimizadas (PPA, informes de gestión, auditoría) | **Sí**, pp. 19–20 | **ninguna fuente del corpus actual es sintética** `[PEND]` |
| Metadata Ledger completo | **Sí**, pp. 6–7 | no existe `[EV §4]` |
| Autonomía epistémica y retención del usuario | **Sí**, p. 12 | solo hay indicadores del comportamiento del sistema; ninguna evidencia sobre personas `[DEC §8]`, `[PEND]` |
| Búsqueda híbrida densa+sparse | No — mejora candidata | no validada experimentalmente `[EV §4]`, `[IDEAS §1]` |
| BM25 productivo | No | los scripts con PostgreSQL FTS **no deben llamarse BM25** sin verificar la función de ranking `[EV §4]` |
| Gobernanza bi-temporal | No — mejora candidata | campos vacíos `[EV §4]` |
| Grafo regulatorio, Second Brain, ledger de decisiones | No | preservados como ideas `[EV §4]`, `[DEC §12]` |
| **Evaluación confirmatoria B0/B1/B2 con Golden humano y split bloqueado** | Sí, p. 12 (obj. esp. 4) | **no demostrada** `[EV §4]` |

---

## 5. Protocolos y mediciones nuevas

### 5.1 Estado de los protocolos: **los dos siguen EN REVISIÓN**

| protocolo | versión | estado textual |
|---|---|---|
| `PROTOCOLO_EXPERIMENTAL.md` | v1.2 · 09-ago-2026 | **«ESTADO: EN REVISIÓN — NO AUTORIZA CORRIDAS TODAVÍA.»** Debe reconciliarse con el plan, el estado verificado y las decisiones vigentes. Hasta entonces es un borrador metodológico `[PEXP]` |
| `PROTOCOLO_GOLDEN.md` | v0.7 · borrador | **«ESTADO: EN REVISIÓN — NO INICIAR ETIQUETADO.»** Debe ser revisado por Lucas y validado por el director antes de construir ítems definitivos `[PGOLD]` |

Regla que los gobierna: *«un protocolo gobierna una corrida solo después de ser
revisado y congelado»* `[README]`, regla de autoridad #6.

**Ninguno fue aprobado. Ninguno está congelado.**

### 5.2 Mediciones nuevas desde el 27 de julio: sí, cuatro — todas exploratorias

| # | medición | fecha | estado | fuente |
|---|---|---|---|---|
| 1 | Sondas del snapshot v2: recuperación B0/B1/B1d, respuestas con k=3, índice semántico de documentos | ago-2026 | exploratoria; *«ayudan a diseñar el experimento, pero no contrastan la hipótesis»* | `[EV §5.1]` |
| 2 | Auditoría reproducible del lote InfoLEG | 12-ago-2026 | acredita completitud técnica de la adquisición, **no** calidad ni pertinencia jurídica | `[EV §5.2]` |
| 3 | Piloto de sensibilidad del clasificador de chunks (14 chunks, 4 documentos) | 13-ago-2026 | exploratorio; mide sensibilidad a la política de prototipos, no exactitud | `[EV §5.3]` |
| 4 | Piloto de contexto semántico `contexto_semantico_piloto_v1` (14 chunks + planilla ciega de 6 casos; revisores Claude ×2, Gemini, Qwen) | 15–16-ago-2026 | exploratorio; **no registrado todavía en `ESTADO_VERIFICADO.md`** | `experimentos/contexto_semantico_piloto_v1/` |

**Deuda:** la medición #4 es de esta semana y no figura en la documentación
canónica. Corresponde registrarla en `ESTADO_VERIFICADO.md` con fecha y
evidencia, según la regla de actualización de `[README]`.

---

## 6. Vigencia temporal — cuántos chunks están sustituidos por norma posterior

### Respuesta directa: **no se puede saber. La capacidad no existe.**

| dato | valor | fuente |
|---|---|---|
| `valid_from`, `valid_to`, `invalid_at`, `node_id` | **vacíos** | `[EV §4]` |
| Gobernanza bi-temporal | listada entre las capacidades **todavía no demostradas** | `[EV §4]` |
| Vigencia y relaciones temporales | «Mejora candidata. Campos bi-temporales existen pero están vacíos.» | `[IDEAS §3]` |

**Cuidado con la interpretación.** El número de chunks marcados como sustituidos
es **cero**, pero eso no significa que ninguno lo esté: significa que **nadie lo
registró nunca**. Es ausencia de dato, no evidencia de vigencia.

**Evidencia directa de que el problema es real.** Los chunks del corpus contienen
relaciones de modificación normativa **en texto libre, sin estructurar**. Ejemplo
verificado el 16-ago-2026 en el chunk
`cd1cfafa2b68b79259389389efb1a72f1b73b1e4cb2cb0797ac8031fda85d35f`:

> `(Párrafo incorporado por art. 1° del [Decreto N° 752/2019](…) B.O. 1/11/2019)`

Esa información existe en el corpus y hoy no es consultable de forma estructurada.

**Riesgo declarado en el plan.** El propio plan advierte el principio *Garbage In,
Garbage Out*: *«Si los documentos base contienen información desactualizada, el
sistema recuperará respuestas erróneas con total confianza»* `[PLAN p.6]`. Y una
de las aplicaciones prometidas es validar la legalidad de un documento
*«consultando exclusivamente el índice de "Legislación Vigente"»* `[PLAN p.8]` —
capacidad que hoy no existe.

---

## 7. Abierto esperando decisión del director

`[PEND]` lista **doce** decisiones. Ninguna registrada como cerrada.

| # | tema | qué se decide |
|---|---|---|
| 1 | **Hipótesis principal** | Confirmar que se contrasta *ventaja bajo colisión semántica interdominio*, no superioridad universal |
| 2 | **Margen de no-inferioridad del recall (`ΔR`)** | Acordar la pérdida máxima aceptable, **antes** del test y sin elegirla mirando el resultado |
| 3 | **Tamaño y diversidad del corpus** | Conservar el rango 300–500 del plan o ajustarlo con justificación |
| 4 | **Fuentes sintéticas o anonimizadas** | Si se incorporan, en qué proporción, cómo se valida su verosimilitud, cómo se identifican y qué se declara sobre validez externa |
| 5 | **Profundidad por dominio** | Si los cuatro dominios sostienen el experimento principal o si legal–impositivo es el caso profundo y los otros dos evidencia de extensibilidad |
| 6 | **Embeddings especializados** | Secuencia entre comparación arquitectónica y especialización LoRA |
| 7 | **Topología de silos y MCP** | Si la separación lógica satisface la intención académica y si MCP es requisito, demostración o diferible |
| 8 | **Exclusividad de pertenencia por chunk** | Autorizar la ablación A0/A1/A2: etiqueta única / conjunto calibrado / conjunto + compuerta de materialidad |
| 9 | **Veto epistémico** | Autorizar LettuceDetect, exigir RAGAS o aceptar una combinación |
| 10 | **Construcción del Golden** | Aprobar el cambio de RAGAS automatizado a verificación humana |
| 11 | **Autonomía y retención del usuario** | Estudio humano acotado, redefinición operacional o traslado a trabajo futuro |
| 12 | **Trazabilidad y Metadata Ledger** | Definir el mínimo implementable y evaluable |
| 12b | **Caché semántico y tiering de modelos** | Si deben estar implementados y medidos en la versión defendida |
| 12c | **Multimodalidad, RAPTOR y validaciones matemáticas** | Cuáles son requisitos y cuáles extensiones |

### Pendiente bloqueante adicional, fuera de esa matriz

`[DEC §6]` registra un bloqueo técnico que **no** requiere al director pero sí
antecede a cualquier reclasificación:

> ⚠️ *«No hay evidencia todavía de que el LLM supere al coseno sobre este corpus.
> Antes de reemplazar nada: **etiquetar a mano ~100 chunks** y medir la exactitud
> de ambos contra esa muestra. Si el LLM no gana con claridad, la decisión se
> revisa.»*

Y la prioridad declarada: *«el MCP espera. Primero el clasificador (camino
crítico a la hipótesis)»* `[DEC §14]`.

### Orden sugerido para la reunión `[PEND]`

1. Congelar la hipótesis y el alcance de la afirmación principal.
2. Acordar corpus, dominios y unidad de generalización, incluidas fuentes sintéticas.
3. Acordar B0/B1/B2, el margen `ΔR` y el lugar de LoRA.
4. Resolver Golden, RAGAS/LettuceDetect y criterio de verdad.
5. Definir el mínimo obligatorio de MCP, ledger, multimodalidad, RAPTOR y tiering.
6. Resolver cómo se evaluarán autonomía y retención.
7. Recién entonces aprobar y congelar los dos protocolos.

---

## 8. Discrepancias detectadas entre documentos canónicos

Se reportan sin modificar nada, conforme a la regla de autoridad.

| # | discrepancia | impacto | corrección mínima sugerida |
|---|---|---|---|
| 1 | `[PEND]`, fila «Tamaño y diversidad del corpus», dice *«El snapshot actual contiene **17 fuentes**»*. `[EV §1.1]` (posterior, 13-ago) declara **24 documentos y 24 artefactos**. | Bajo. `[PEND]` es del 1-ago y quedó desactualizado. La regla de autoridad da precedencia a `[EV]` sobre el estado real. | Actualizar la celda de `[PEND]` citando `[EV §1.1]`. |
| 2 | `[DEC §6]` afirma *«Etiquetar **3.561 chunks** a mano no es viable»*. `[EV §1.1]` registra **4.789** chunks. | Bajo. No cambia el argumento — sigue sin ser viable — pero el número está obsoleto. | Actualizar la cifra en `[DEC §6]`. |
| 3 | El piloto de contexto semántico (15–16-ago) no figura en `[EV]`. | Medio. `[EV]` es la fuente de verdad sobre qué existe, y le falta la medición más reciente. | Agregar una sección `5.4` a `[EV]` con fecha y evidencia. |
| 4 | `[PLAN p.20]` compromete evaluación automatizada con RAGAS *«prescindiendo de la subjetividad de evaluadores humanos»*; `[PGOLD]` exige verificación humana. | **Alto.** Es una desviación metodológica del plan aprobado. | Ya está registrada como fila 10 de `[PEND]`. No requiere acción documental, sí decisión del director. |

---

## 9. Síntesis

1. **Corpus:** 4.789 chunks, 24 documentos, cuatro silos, BGE-M3 denso de 1.024
   dimensiones. La divergencia de temperatura 0.1 vs 0.05 **no se resolvió** y
   está prohibido reclasificar. El snapshot **no es apto** para el test
   confirmatorio.
2. **Hipótesis:** existe redactada en el plan y operacionalizada en
   `[DEC §1]`, pero **no está congelada**: falta la decisión del director sobre
   si se contrasta ventaja condicional o superioridad general.
3. **Resultados:** hay cifras citables de implementación y auditoría. Los
   porcentajes de desempeño de julio están **prohibidos** y hay siete familias
   retractadas. Todo lo medido desde entonces es exploratorio.
4. **Arquitectura:** nueve componentes funcionando, ocho a medias y trece en
   roadmap — de los cuales **ocho están comprometidos en el plan aprobado** y no
   implementados.
5. **Protocolos:** los dos **en revisión**. Ninguna corrida confirmatoria está
   autorizada. Cuatro mediciones nuevas desde el 27-jul, todas exploratorias.
6. **Vigencia temporal:** capacidad inexistente. Cero chunks marcados, lo que es
   ausencia de dato y no evidencia de vigencia.
7. **Director:** doce decisiones abiertas, más un pendiente bloqueante técnico
   (~100 chunks etiquetados a mano) que antecede a cualquier reclasificación.

**Cuello de botella:** el camino crítico declarado es el clasificador, y su
desbloqueo depende de etiquetado humano, no de más código. Encima de eso, ningún
resultado confirmatorio es válido hasta que los protocolos se congelen, y eso
depende de la reunión con el director.
