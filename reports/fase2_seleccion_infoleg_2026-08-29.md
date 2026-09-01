# FASE 2 — Selección reproducible de normas InfoLEG

**Receta:** `seleccion-fase2-v1` · **Fecha:** 29-ago-2026

**Propuesta. No se ingirió nada.**

## Salvedades, antes de los números

- PROPUESTA. No se ingirio nada y no se toco PostgreSQL.
- `energia`/`impositivo` son CRITERIOS DE BUSQUEDA en InfoLEG, no etiquetas de dominio verificadas. Todo sale pendiente_revision.
- Los dos HTTP 403 no se evaden: se documentan y el cupo se completa con la misma regla sobre el pool restante.
- No se impuso tope por organismo: el PEN concentra decretos porque asi se dicta la normativa, y forzar una tabla pareja distorsionaria el corpus.
- Seleccion deterministica: mismo pool, misma salida, sin semilla.

## 1 · Resultado

| dominio de adquisición | candidato a | seleccionados | pool disponible |
|---|---|---:|---:|
| `energia` | legal/regulatorio | **75** / 75 | 200 |
| `impositivo` | impositivo | **75** / 75 | 198 |
| **total** | | **150** | |

## 2 · Los dos HTTP 403 — documentados, no evadidos

| id_norma | dominio | tipo | organismo | título |
|---|---|---|---|---|
| `317876` | impositivo | Acordada | TRIBUNAL FISCAL DE LA NACION | FERIA JUDICIAL |
| `419824` | impositivo | Acordada | TRIBUNAL FISCAL DE LA NACION | SUBROGANCIAS - REGULARIZAR |

No se intentó ningún rodeo. Estas normas quedan **fuera del pool**, y el cupo
se completó con la misma regla estratificada sobre las normas que sí están.
Sustituir a mano dos documentos elegidos por una persona rompería la
reproducibilidad de toda la selección para ganar dos documentos.

## 3 · Composición de lo seleccionado

### `energia` — 75 documentos

**Tipo de norma**

| valor | documentos | % |
|---|---:|---:|
| Decreto | 37 | 49 % |
| Resolución | 37 | 49 % |
| Ley | 1 | 1 % |

**Década**

| valor | documentos | % |
|---|---:|---:|
| 2020s | 44 | 59 % |
| 2010s | 31 | 41 % |

**Criterio de adquisición**

| valor | documentos | % |
|---|---:|---:|
| materia | 38 | 51 % |
| organismo | 37 | 49 % |

**Organismo emisor**

| valor | documentos | % |
|---|---:|---:|
| PODER EJECUTIVO NACIONAL (P.E.N.) | 37 | 49 % |
| ENTE NACIONAL REGULADOR DE LA ELECTRICIDAD | 12 | 16 % |
| SECRETARIA DE ENERGIA | 12 | 16 % |
| ENTE NACIONAL REGULADOR DEL GAS | 10 | 13 % |
| MINISTERIO DE ENERGIA Y MINERIA | 2 | 3 % |
| HONORABLE CONGRESO DE LA NACION ARGENTINA | 1 | 1 % |
| SECRETARIA DE POLITICAS INTEGRALES SOBRE DROGAS DE LA NACION | 1 | 1 % |

### `impositivo` — 75 documentos

**Tipo de norma**

| valor | documentos | % |
|---|---:|---:|
| Decreto | 31 | 41 % |
| Resolución | 28 | 37 % |
| Disposición | 9 | 12 % |
| Ley | 7 | 9 % |

**Década**

| valor | documentos | % |
|---|---:|---:|
| 2020s | 40 | 53 % |
| 2010s | 35 | 47 % |

**Criterio de adquisición**

| valor | documentos | % |
|---|---:|---:|
| materia | 38 | 51 % |
| organismo | 37 | 49 % |

**Organismo emisor**

| valor | documentos | % |
|---|---:|---:|
| PODER EJECUTIVO NACIONAL (P.E.N.) | 31 | 41 % |
| ADMINISTRACION FEDERAL DE INGRESOS PUBLICOS | 27 | 36 % |
| HONORABLE CONGRESO DE LA NACION ARGENTINA | 7 | 9 % |
| DIRECCION GENERAL DE ADUANAS | 5 | 7 % |
| SUBDIRECCION GENERAL DE OPERACIONES IMPOSITIVAS DEL INTERIOR | 2 | 3 % |
| TRIBUNAL FISCAL DE LA NACION | 2 | 3 % |
| SUBDIRECCION GENERAL DE OPERACIONES IMPOSITIVAS METROPOLITAN | 1 | 1 % |

## 4 · Concentración por organismo — limitación, no defecto corregido

El Poder Ejecutivo Nacional concentra buena parte de las normas porque **así se**
**dicta la normativa argentina**: los decretos salen del PEN. La estratificación
es por tipo de norma y década, que reparte organismos de forma indirecta, y **no**
se impuso un tope artificial por organismo: hacerlo distorsionaría la composición
real del corpus normativo para que una tabla se vea más pareja.

| dominio | organismos distintos | organismo más frecuente | su participación |
|---|---:|---|---:|
| `energia` | 7 | PODER EJECUTIVO NACIONAL (P.E.N.) | 49 % |
| `impositivo` | 7 | PODER EJECUTIVO NACIONAL (P.E.N.) | 41 % |

## 5 · Deduplicación aplicada dentro de la selección

Ninguna. Ningún par de normas seleccionadas comparte texto normalizado.

## 6 · Lo que esta selección NO afirma

- **No afirma el dominio de ninguna norma.** `energia` e `impositivo` son
  criterios de búsqueda en InfoLEG. Cada registro sale con
  `estado = pendiente_revision` y su dominio queda por decidir con el mismo
  instrumento de revisión humana que los 24 actuales.
- **No afirma que sean 75 documentos de dominio legal.** Son 75 normas
  *candidatas* a aportar membresías legal/regulatorias.
- **No incluye nada en el corpus.** Es una propuesta previa a la ingesta.

## Manifest

```json
{
  "ausentes_http_403": [
    "317876",
    "419824"
  ],
  "cupo": {
    "energia": 75,
    "impositivo": 75
  },
  "deduplicacion": "texto normalizado; ninguna norma repetida",
  "descartados_por_duplicado": 0,
  "estratificacion": "criterio_adquisicion x tipo_norma x decada",
  "pool_por_dominio": {
    "energia": 200,
    "impositivo": 198
  },
  "receta": "seleccion-fase2-v1",
  "reparto": "proporcional por restos mayores; orden por id_norma",
  "salvedades": [
    "PROPUESTA. No se ingirio nada y no se toco PostgreSQL.",
    "`energia`/`impositivo` son CRITERIOS DE BUSQUEDA en InfoLEG, no etiquetas de dominio verificadas. Todo sale pendiente_revision.",
    "Los dos HTTP 403 no se evaden: se documentan y el cupo se completa con la misma regla sobre el pool restante.",
    "No se impuso tope por organismo: el PEN concentra decretos porque asi se dicta la normativa, y forzar una tabla pareja distorsionaria el corpus.",
    "Seleccion deterministica: mismo pool, misma salida, sin semilla."
  ],
  "seleccionados": 150
}
```
