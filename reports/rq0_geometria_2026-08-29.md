# RQ0 — geometría del embedding frente a dominio, tipo y emisor

**Receta:** `rq0-v0.2-documento-como-unidad` · **Fecha:** 29-ago-2026

> **Esta versión reemplaza metodológicamente a la primera** (`rq0-v0.1-exploratoria`).
> Los números de aquella versión **no son válidos** y no deben citarse.
> Qué cambió y por qué, en la sección 7.

**Diagnóstico exploratorio.** No es evidencia confirmatoria.

## Salvedades, antes de los números

- Diagnostico EXPLORATORIO. No es evidencia confirmatoria.
- 24 documentos: todo el poder estadistico esta ahi. `financiero` tiene 3.
- Los metadatos del catalogo siguen PENDIENTES DE RATIFICACION HUMANA (estado_inclusion = pendiente_revision en los 24 registros).
- La unidad es el documento: un vector, un voto y un peso por documento. La version pesada por chunks es sensibilidad, no resultado.
- Las exactitudes crudas NO son comparables entre objetivos con distinta cantidad de clases. La comparacion entre objetivos es DESCRIPTIVA.
- La proyeccion 2-D es para mirar. No prueba separabilidad.
- No se cargaron los 398 documentos de InfoLEG. No se modifico PostgreSQL, ni la ingesta, ni los embeddings, ni la clasificacion persistida, ni ningun chunk_uid.

## Conjunto analizado

| | |
|---|---|
| documentos | `24` |
| chunks | `4789` |
| dimension_embedding | `1024` |
| chunks_descartados_no_objetivo | `14` |
| chunks_por_documento_min | `11` |
| chunks_por_documento_max | `812` |
| huella del conjunto | `sha256:d66fba1e1a7342af15c1c5d4c47d9737d94d9b3d4c2f6c72a16dae63ce3e45ac` |
| huella del catálogo | `sha256:2ce31fdf4f47eecf7a404f15827a283e89f6342396a4835f6b45ce99a5383b4d` |

## 1 · Resultado primario — los cuatro silos

Un vector y un voto por documento. Cuatro tareas uno-contra-el-resto sobre
`legal`, `impositivo`, `contable` y `financiero`: la arquitectura de la tesis.
Corrección de **Holm sobre estas cuatro pruebas**.

| dominio | docs + | docs − | exact. balanceada | IC 95 % | nulo | brecha | p | p (Holm) | supera |
|---|---:|---:|---:|:---:|---:|---:|---:|---:|:--:|
| `contable` | 8 | 16 |  93.8 % | 84.4 – 100.0 % |  49.0 % | +44.7 pp | <0.001 | 0.002 | sí |
| `financiero` | 3 | 21 |  81.0 % | omitido |  47.7 % | +33.2 pp | 0.051 | 0.051 | **no** |
| `impositivo` | 8 | 16 |  78.1 % | 59.4 – 93.8 % |  48.5 % | +29.7 pp | 0.011 | 0.022 | sí |
| `legal` | 8 | 16 |  93.8 % | 81.2 – 100.0 % |  49.0 % | +44.7 pp | <0.001 | 0.002 | sí |

- `financiero`: IC omitido — la clase evaluada más chica tiene 3 documentos (mínimo 5): un intervalo sería decorado.

### Conteos de confusión (nivel documento)

| dominio | + / + | + / − | − / + | − / − |
|---|---:|---:|---:|---:|
| `contable` | 8 | 0 | 2 | 14 |
| `financiero` | 2 | 1 | 1 | 20 |
| `impositivo` | 6 | 2 | 3 | 13 |
| `legal` | 7 | 1 | 0 | 16 |

`+ / −` es un documento del dominio que el espacio no reconoció como tal.

### Sensibilidad: centroides pesados por chunks

Análisis **secundario**. Muestra qué cambia cuando un documento de 812 chunks
pesa 270 veces más que uno de 3. No es el resultado.

| dominio | primario (1 voto/doc) | sensibilidad (chunks) | diferencia |
|---|---:|---:|---:|
| `contable` |  93.8 % |  93.8 % |  +0.0 pp |
| `financiero` |  81.0 % |  47.6 % | +33.3 pp |
| `impositivo` |  78.1 % |  84.4 % |  -6.2 pp |
| `legal` |  93.8 % |  90.6 % |  +3.1 pp |

## 2 · Metadatos documentales: tipo y emisor

Familia de **dos** pruebas, con su propia corrección de Holm.

| objetivo | clases | docs | exact. balanceada | IC 95 % | nulo | brecha | p | p (Holm) | supera |
|---|---:|---:|---:|:---:|---:|---:|---:|---:|:--:|
| `tipo_documento` | 4 | 17 |  41.7 % | omitido |  23.3 % | +18.4 pp | 0.119 | 0.119 | **no** |
| `emisor_id` | 5 | 17 |  45.0 % | omitido |  17.0 % | +28.0 pp | 0.025 | 0.051 | **no** |

- `tipo_documento`: IC omitido — la clase evaluada más chica tiene 2 documentos (mínimo 5): un intervalo sería decorado.
- `emisor_id`: IC omitido — la clase evaluada más chica tiene 2 documentos (mínimo 5): un intervalo sería decorado.

## 3 · Exploratorio suplementario — otros tokens de dominio

**No** forman parte de la arquitectura de cuatro silos. Corrección de Holm
**separada**, sobre esta familia y no junto a la principal.

| token | docs + | docs − | exact. balanceada | nulo | p | p (Holm supl.) |
|---|---:|---:|---:|---:|---:|---:|
| `ambiental` | 1 | 23 | no evaluable | — | — | — |
| `corporativo` | 4 | 20 |  72.5 % |  48.3 % | 0.141 | 0.283 |
| `laboral` | 1 | 23 | no evaluable | — | — | — |
| `operativo` | 4 | 20 |  62.5 % |  47.3 % | 0.228 | 0.283 |
| `regulatorio` | 17 | 7 |  92.9 % |  48.3 % | <0.001 | 0.002 |
| `tecnico` | 4 | 20 |  82.5 % |  48.0 % | 0.020 | 0.061 |

## 4 · Exploratorio — combinación completa de dominios

> ⚠️ **`dominio_combinacion` NO evalúa la arquitectura de cuatro silos y no puede**
> **resolver la compuerta de `PRIORIDADES` §2.** Trata cada combinación literal
> como una clase, así que descarta los documentos cuya combinación es única:
> **7 de 24**, y **los tres documentos**
> **`financiero` están entre ellos**. Se conserva solo como descripción.

Documentos descartados: `DOC-0001`, `DOC-0006`, `DOC-0007`, `DOC-0015`, `DOC-0020`, `DOC-0023`, `DOC-0024`.

Exactitud balanceada `87.5 %` sobre 17 documentos y 4 clases; nulo `23.7 %`; p <0.001.

## 5 · ¿Representa el espacio mejor dominio, tipo o emisor?

**Comparación descriptiva, no una prueba.** Las tareas tienen distinta cantidad
de clases y distinta estructura, así que un test de signos entre ellas no
sostiene «explica mejor» ni «explica peor». Se informa el recuento de documentos
discordantes para que se vea el tamaño real de la evidencia, y nada más.

| comparación | docs comunes | acierta solo el 1° | acierta solo el 2° | discordantes |
|---|---:|---:|---:|---:|
| `tipo_documento vs emisor_id` | 13 | 3 | 0 | 3 |
| `tipo_documento vs dominio_combinacion` | 14 | 0 | 3 | 3 |
| `emisor_id vs dominio_combinacion` | 14 | 0 | 7 | 7 |

### Lectura

**Dominio:** 3 de 4 silos superan su nulo tras Holm — `contable`, `impositivo`, `legal`. No lo superan: `financiero`.

**Metadatos:** 0 de 2 superan su nulo tras Holm — ninguno. No lo superan: `tipo_documento`, `emisor_id`.

**La compuerta de `PRIORIDADES` §2 no se dispara.** Esa compuerta pregunta si
tipo documental o emisor explican el espacio **mucho mejor** que dominio. Con
esta medición no se observó el patrón previsto por la compuerta: el dominio
sobrevive en más pruebas que los metadatos documentales. La explicación rival
**no** queda respaldada.

Eso **no** autoriza la afirmación simétrica. Que `tipo_documento` no supere su
nulo con 17 documentos y 4 clases es falta de evidencia, no evidencia de
ausencia; y las tareas tienen distinta forma, así que «dominio explica mejor»
sigue sin ser una afirmación que estos datos sostengan.

**RQ0 no concluyente con el corpus actual.**

Para la pregunta de ordenar dominio, tipo y emisor, 24 documentos no alcanzan: la
comparación entre objetivos es descriptiva y los documentos discordantes son un
puñado. Lo que sí quedó establecido es más acotado y más útil: bajo un voto por
documento, la geometría lleva información sobre varios de los silos por encima de
su propio nulo, con corrección por multiplicidad.

Lo que haría falta son **más documentos por clase**, no más chunks: todo el poder
de esta prueba está en 24 documentos, y `financiero` tiene 3.

## 6 · Distribución de clases a nivel documento

**`tipo_documento`**

| clase | documentos |
|---|---:|
| `estado_contable` | 7 |
| `texto_ordenado` | 6 |
| `decreto` | 2 |
| `resolucion` | 2 |
| `informe_calificacion` | 1 |
| `ley` | 1 |
| `memoria_anual` | 1 |
| `presentacion_corporativa` | 1 |
| `procedimiento_regulatorio` | 1 |
| `prospecto_financiero` | 1 |
| `resolucion_general` | 1 |

**`emisor_id`**

| clase | documentos |
|---|---:|
| `EMI-0006` | 6 |
| `EMI-0003` | 4 |
| `EMI-0001` | 3 |
| `EMI-0009` | 2 |
| `EMI-0011` | 2 |
| `EMI-0002` | 1 |
| `EMI-0004` | 1 |
| `EMI-0005` | 1 |
| `EMI-0007` | 1 |
| `EMI-0008` | 1 |
| `EMI-0010` | 1 |
| `EMI-0012` | 1 |

**`dominio_combinacion`**

| clase | documentos |
|---|---:|
| `contable|regulatorio` | 6 |
| `impositivo` | 6 |
| `legal|regulatorio` | 3 |
| `legal|regulatorio|tecnico|operativo` | 2 |
| `ambiental|contable|corporativo|laboral|operativo|regulatorio` | 1 |
| `contable|corporativo|regulatorio` | 1 |
| `financiero|corporativo|regulatorio|tecnico|operativo` | 1 |
| `financiero|legal|impositivo` | 1 |
| `financiero|regulatorio|corporativo` | 1 |
| `legal|impositivo|regulatorio` | 1 |
| `legal|regulatorio|tecnico` | 1 |

**tokens de dominio**

| token | documentos | familia |
|---|---:|---|
| `contable` | 8 | **principal (silo)** |
| `financiero` | 3 | **principal (silo)** |
| `impositivo` | 8 | **principal (silo)** |
| `legal` | 8 | **principal (silo)** |
| `ambiental` | 1 | suplementaria |
| `corporativo` | 4 | suplementaria |
| `laboral` | 1 | suplementaria |
| `operativo` | 4 | suplementaria |
| `regulatorio` | 17 | suplementaria |
| `tecnico` | 4 | suplementaria |

## 7 · Reemplazo metodológico de la primera versión

La primera versión (`rq0-v0.1-exploratoria`) tenía cuatro defectos que invalidan
sus números. Se conserva la traza, no los resultados.

| # | Defecto de la v0.1 | Corrección en la v0.2 |
|---|---|---|
| 1 | Centroides construidos con **chunks**: un documento de 812 chunks pesaba 270 veces más que uno de 3 | Un vector L2-normalizado **por documento**; cada documento pesa una vez. La versión por chunks queda como sensibilidad |
| 2 | El nulo conservaba las predicciones y permutaba solo la verdad: nulo de «estas predicciones no se relacionan con estas etiquetas», no del procedimiento supervisado | Cada permutación **reajusta todos los folds** y reconstruye los centroides con las etiquetas permutadas |
| 3 | `dominio_combinacion` se leía como si evaluara los silos; descarta 7 de 24 documentos y **los 3 `financiero`** | Los **cuatro silos** como OvR con Holm; `dominio_combinacion` queda como descripción explícitamente incapaz de resolver la compuerta |
| 4 | Bootstrap simple que perdía clases, y un test de signos leído como ranking | Bootstrap **estratificado** por clase verdadera, **omitido** cuando la clase más chica no lo sostiene; el test de signos baja a descriptivo |

También: los valores p se imprimen como `<0.001` y nunca como `0.000`.

## Manifest

```json
{
  "conjunto": {
    "chunks": 4789,
    "chunks_descartados_no_objetivo": 14,
    "chunks_por_documento_max": 812,
    "chunks_por_documento_min": 11,
    "dimension_embedding": 1024,
    "documentos": 24,
    "huella": "sha256:d66fba1e1a7342af15c1c5d4c47d9737d94d9b3d4c2f6c72a16dae63ce3e45ac",
    "huella_catalogo": "sha256:2ce31fdf4f47eecf7a404f15827a283e89f6342396a4835f6b45ce99a5383b4d",
    "huella_inventario": "sha256:d87c039ea362878c35f61b98fd2c79d38243a7fb8f7cca72571c2159d4db5c13"
  },
  "correccion_multiple": "Holm sobre los 4 silos; Holm separado sobre tipo/emisor; Holm separado sobre los tokens suplementarios",
  "dominios_centrales": [
    "contable",
    "financiero",
    "impositivo",
    "legal"
  ],
  "embedding": "BAAI/bge-m3 denso, leido de chunks.embedding sin recomputar",
  "figura": {
    "coloreada_por": "tipo_documento",
    "implementacion": "sklearn 1.9.0 (perplexity=7)",
    "metodo": "tsne",
    "ruta": "reports/figuras/rq0_proyeccion_2d.svg",
    "unidad": "documento"
  },
  "min_documentos_por_clase": 2,
  "minimo_clase_para_bootstrap": 5,
  "modelo": "centroide de clase mas cercano por coseno, sin parametros",
  "nulo": "permutacion de etiquetas por documento + reajuste completo de todos los folds",
  "particion": "Leave-One-Document-Out sobre 24 vectores documentales",
  "permutaciones": 2000,
  "receta": "rq0-v0.2-documento-como-unidad",
  "reemplaza": "rq0-v0.1-exploratoria (numeros invalidados)",
  "remuestras_bootstrap": 2000,
  "salvedades": [
    "Diagnostico EXPLORATORIO. No es evidencia confirmatoria.",
    "24 documentos: todo el poder estadistico esta ahi. `financiero` tiene 3.",
    "Los metadatos del catalogo siguen PENDIENTES DE RATIFICACION HUMANA (estado_inclusion = pendiente_revision en los 24 registros).",
    "La unidad es el documento: un vector, un voto y un peso por documento. La version pesada por chunks es sensibilidad, no resultado.",
    "Las exactitudes crudas NO son comparables entre objetivos con distinta cantidad de clases. La comparacion entre objetivos es DESCRIPTIVA.",
    "La proyeccion 2-D es para mirar. No prueba separabilidad.",
    "No se cargaron los 398 documentos de InfoLEG. No se modifico PostgreSQL, ni la ingesta, ni los embeddings, ni la clasificacion persistida, ni ningun chunk_uid."
  ],
  "semilla": 20260829,
  "unidad_de_analisis": "documento (un vector, un voto, un peso)"
}
```

Para regenerar:

```bash
python -m scripts.diagnostics.rq0_geometria_vs_metadatos
```
