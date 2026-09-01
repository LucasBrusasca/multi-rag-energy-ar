# Casos de regresión de desarrollo

Este archivo registra fallos descubiertos durante el desarrollo del sistema.

Estos casos:

- pueden utilizarse para diagnosticar y mejorar la arquitectura;
- pueden utilizarse como pruebas de regresión;
- no pertenecen al conjunto confirmatorio;
- no deben utilizarse para estimar el resultado final de la tesis;
- están separados del Golden para evitar contaminación experimental.

---

## DEV-COL-001 — Resultado neto versus resultados financieros netos

### Origen del caso

Caso descubierto después de observar el comportamiento de B0, B1 y B2.

Por lo tanto, es un caso **post hoc de desarrollo** y no puede incorporarse
silenciosamente al conjunto confirmatorio.

### Identidad documental

- `instrument_id`: `INS-0021`
- `document_id`: `DOC-0021`
- `artifact_id`: `ART-SHA256-64DEE6344349B2EC33D448E61E80B04F5CC271ED8A47692EF7B35429FD296270`
- `fuente`: `TGS_EEFF_2025_09`

### Consulta original

> ¿Cuál fue el resultado neto de TGS al 30 de septiembre de 2025?

### Consulta reformulada

> ¿Cuál fue la utilidad neta del período de nueve meses de TGS terminado el 30 de septiembre de 2025?

### Evidencia de referencia provisional

- `chunk_uid`: `65d2eaa6a6ad39f446f023c66592e72093cc19b0e977834ed8fc07aab422be40`
- título: `TRANSPORTADORA DE GAS DEL SUR S.A.`
- concepto: utilidad neta del período de nueve meses terminado el 30 de septiembre de 2025
- valor: `275.226.693`
- unidad documental: miles de pesos
- dominio humano provisional: `contable`
- dominio automático: `financiero`

La evidencia y el dominio humano permanecen sujetos a verificación documental.

### Distractor semántico principal

- `chunk_uid`: `ac31257a8ee41d0a5426bd1a8a8660ce13f65509bdaa97cf352c409a748614b2`
- título: `k) Resultados financieros, netos`
- concepto confundido: resultados financieros netos del período
- valor de nueve meses de 2025: `(49.211.068)`
- dominio automático: `financiero`

El distractor comparte las palabras `resultado`, `neto` y el mismo período,
pero representa un concepto contable diferente de la utilidad neta.

### Resultado con la consulta original

| brazo | rango de la evidencia correcta | evidencia en top-3 |
|---|---:|---:|
| B0 | no recuperada | no |
| B1 — oráculo contable provisional | no recuperada | no |
| B2 | no recuperada | no |

El router de B2 abrió `financiero` y `contable`.

### Resultado con la consulta reformulada

| brazo | rango de la evidencia correcta | Hit@1 | Recall@3 | MRR |
|---|---:|---:|---:|---:|
| B0 | 2 | 0 | 1 | 0,5 |
| B1 — oráculo contable provisional | no recuperada | 0 | 0 | 0 |
| B2 | 2 | 0 | 1 | 0,5 |

El router de B2 volvió a abrir `financiero` y `contable`.

### Silo scores de la evidencia correcta

| silo | score |
|---|---:|
| financiero | 0,7340 |
| contable | 0,2083 |
| legal | 0,0387 |
| impositivo | 0,0190 |

### Diagnóstico provisional

La reformulación mejora el recall, pero no coloca la evidencia correcta en
la primera posición.

El caso revela tres riesgos:

1. la asignación rígida a un solo silo puede excluir evidencia válida;
2. la similitud densa puede priorizar un concepto léxicamente próximo pero incorrecto;
3. B2 puede comportarse como B0 cuando los candidatos de un silo dominan la fusión.

### Hipótesis de mejora para evaluar

Estas alternativas no se consideran soluciones demostradas. Deben compararse
mediante ablación sobre un conjunto de desarrollo:

- reformulación o expansión terminológica de la consulta;
- reranking de candidatos;
- pertenencia multietiqueta o suave de chunks;
- recuperación documental contextual;
- búsqueda híbrida densa y léxica.

No se modifican umbrales ni etiquetas canónicas basándose únicamente en este caso.