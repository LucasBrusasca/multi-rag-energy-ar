# FASE 3 v2.1 + FASE 4 v2.1 — corpus candidato

**Receta:** `propuesta-fase4-v2.1` · **Fecha:** 29-ago-2026

> **Reemplaza a la v2.** Los conteos de membresía de la v2 estaban inflados por
> búsqueda por subcadena; las dos planillas de cuarentena figuraban como
> ilegibles y no lo eran.

> **PROPUESTA PREVIA A LA INGESTA.** No se ingirió, no se descargó nada, no se
> tocó PostgreSQL, nada se movió a `data/raw`.

## Salvedades, antes de los números

- PROPUESTA. No se ingirio, no se descargo nada, no se toco PostgreSQL.
- Ningun documento tiene dominio verificado.
- Las brechas son DESCONOCIDAS por dos motivos: nadie reviso, y la revision de los 59 no cubre las 150 normas InfoLEG.
- Los conteos de membresia de la v2 estaban inflados por busqueda por subcadena; `impositivo` paso de 23 a 7.
- Las dos planillas de cuarentena ahora se leen con openpyxl y son distintas entre si.
- La revision humana es CIEGA en dos etapas y registra si la decision cambio al ver la propuesta automatica.

## 1 · Qué cambió respecto de la v2, y por qué se movieron los números

| # | Defecto de la v2 | Corrección | Efecto medido |
|---|---|---|---|
| 1 | Términos buscados como **subcadena**: `iva` dentro de `comparativa`, `arca` dentro de `abarca`, `percepción de corrupción` como materia impositiva | Límites léxicos | `impositivo` bajó de **23 a 7** membresías |
| 2 | Una mención incidental bastaba para proponer un dominio | Materialidad mínima: ≥3 términos distintos, ≥6 menciones, algún término en ≥2 páginas | combinaciones distintas siguen siendo 10, con menos ruido |
| 3 | Las dos planillas figuraban como no leídas | Se leen con `openpyxl`: hojas, celdas, unidades | 2 documentos más caracterizados |
| 4 | `2025 Annual Report.pdf` fechado `2T2026` | El nombre de archivo tiene prioridad para el tipo, y un anual no acepta trimestre | ahora `2025` |
| 5 | Entidad = oración (`To the shareholders of…`) | Recorte de oración, rechazo de dígitos, y se elige la razón social **más frecuente** | 0 entidades que sean oraciones |
| 6 | Fechas de cierre como texto libre (`31 DE MARZO DE 2026`) | ISO `YYYY-MM-DD` | **0** períodos no normalizados (eran 14) |

## 2 · Conteos

| | documentos | qué significa |
|---|---:|---|
| activos | 24 | **verificado**: ingeridos, con catálogo curado |
| InfoLEG seleccionados | 150 | **verificado** que existen; su dominio es propuesta **sin auditar** |
| empresariales nuevos | 24 | **verificado** que se descargaron y se leyeron |
| **disponibles sin cuarentena** | **198** | |
| cuarentena, únicos | 11 | **pendiente** |
| **máximo potencial** | **209** | |

## 3 · Membresías por dominio — PROPUESTAS, y ahora sin falsos positivos

| dominio | objetivo | InfoLEG (sin auditar) | empresariales (leídos) | brecha |
|---|---:|---:|---:|---|
| `legal` | 75 | 75 | 24 | **desconocida** |
| `impositivo` | 75 | 75 | 7 | **desconocida** |
| `contable` | 75 | 0 | 24 | **desconocida** |
| `financiero` | 75 | 0 | 9 | **desconocida** |

### Por qué las brechas siguen desconocidas — ahora por DOS motivos

1. **Nadie revisó nada.** Una brecha es la distancia a un conteo *verificado*, y
   los 59 documentos están sin revisar por una persona.
2. **La revisión de los 59 no alcanza.** La interfaz cubre 24 activos + 24
   nuevos + 11 de cuarentena. Las **150 normas InfoLEG no están incluidas**, y
   son la totalidad de las membresías `legal` e `impositivo` propuestas.
   Terminar los 59 dejaría esos dos dominios apoyados en un filtro de búsqueda
   que nadie auditó.

## 4 · Auditoría estratificada de InfoLEG — definida, no ejecutada

Leer las 150 no es el punto y saltearlas deja media propuesta sin verificar. Una
muestra estratificada acota la tasa de error del filtro de adquisición sin
leerlas todas.

| | |
|---|---|
| estratos | dominio de adquisicion x criterio (materia/organismo) x decada |
| por_estrato | 4 |
| total_aproximado | 32 |
| pregunta | el criterio de busqueda de InfoLEG (`energia` / `impositivo`) coincide con el dominio real de la norma? |
| salida | tasa de acuerdo por estrato, con la que se puede acotar cuantas de las 150 estarian mal clasificadas sin leerlas todas |

Con ~32 normas revisadas se puede estimar, con su intervalo, cuántas de las 150
estarían mal clasificadas. **No se ejecutó**: es la propuesta del próximo paso.

## 5 · Las dos planillas de cuarentena, ahora leídas

La v2 las declaraba ilegibles «porque no hay lector liviano». `openpyxl` ya es
dependencia del proyecto y las lee. **Son archivos distintos y ambos relevantes.**

| archivo | hojas | unidades | dominios propuestos | evidencia de celda |
|---|---|---|---|---|
| `1Q26 (1).xlsx` | Conso, Gen ing, P&G ing, PTQ ing | miles, millones, porcentaje | (ninguno) | `Conso!B2`: Pampa's main operational KPIs |
| `1Q26.xlsx` | BCE ing, EERR-C ing, EFE ing, Res ing, Caja y Deuda ING, Proy | millones, porcentaje | contable, financiero | `BCE ing!B2`: In US$ million |

## 6 · Distribución de los documentos leídos

### Por tipo documental propuesto

| valor | documentos |
|---|---:|
| estado_financiero | 17 |
| memoria_anual | 7 |
| presentacion_inversores | 3 |
| reporte_resultados | 3 |
| reporte_sostenibilidad | 2 |
| no_determinado | 2 |
| terminos_y_condiciones | 1 |
| codigo_de_etica | 1 |

### Por período propuesto

| valor | documentos |
|---|---:|
| 2025 | 7 |
| 1T2026 | 6 |
| 2026 | 3 |
| 2026-03-31 | 2 |
| 2T2026 | 2 |
| 2026-06-30 | 2 |
| sin período | 1 |
| 2025-12-31 | 1 |
| 2024 | 1 |
| 2017-06-30 | 1 |
| 2018-06-30 | 1 |
| 2016-09-30 | 1 |
| 2017-09-30 | 1 |
| 2018-09-30 | 1 |
| 2017-03-31 | 1 |
| 2018-03-31 | 1 |
| 2019-03-31 | 1 |
| 2016-12-31 | 1 |
| 2017-12-31 | 1 |
| 2018-12-31 | 1 |

### Por confianza del período

| valor | documentos |
|---|---:|
| media | 19 |
| alta | 16 |
| sin_periodo | 1 |

### Por confianza de la entidad

| valor | documentos |
|---|---:|
| alta | 19 |
| media | 11 |
| sin_entidad | 3 |
| baja | 3 |

### Por combinación de dominios

| valor | documentos |
|---|---:|
| contable, legal | 11 |
| contable, impositivo, legal | 6 |
| (ninguno) | 5 |
| legal | 3 |
| financiero | 3 |
| contable | 2 |
| contable, financiero, legal | 2 |
| contable, financiero | 2 |
| financiero, legal | 1 |
| contable, financiero, impositivo, legal | 1 |

## 7 · Pertinencia y duplicación

| documento | motivo de exclusión propuesto |
|---|---|
| `CEPU__Anuncio_fecha_de_resultados_2T26.pdf` | aviso_o_convocatoria |
| `METROGAS__TyC-Notificaciones-Electronicas-2026.pdf` | terminos_y_condiciones |
| `METROGAS__TyC_Adhesion-al-Servicio-de-Factura-Digital_20` | terminos_y_condiciones |
| `TGS__Tgs-REPORTE-2024_13-6.pdf` | sostenibilidad |
| `TGS__tgs-Reporte-ASG-2025.pdf` | sostenibilidad |
| `TRANSENER__C_DIGO-DE-_TICA-2025.pdf` | codigo_de_etica |

- Mismo texto extraído: `0001292814-26-002185.pdf`, `20-F 2025.pdf`

**Transener 31-03-2019 contra el activo:** distinto SHA-256, 41 páginas contra 40, distinto texto. Mismo cierre (`2019-03-31`), probablemente individual contra consolidado. **Par a comparar en la revisión**, no duplicado ni documento distinto.

## 8 · robots.txt

`264` documentos públicos quedaron sin descargar porque su editor
los prohíbe a clientes automáticos. La evaluación se corrigió a RFC 9309 con
token de producto exacto, percent-encoding canónico, especificidad por octetos
coincidentes y grupos vacíos distinguidos de grupos ausentes. **No se volvió a**
**descargar nada.**

## 9 · Lo que esta propuesta NO afirma

- **No afirma el dominio de ningún documento.**
- **No afirma brechas.** Desconocidas por dos motivos, no uno.
- **No afirma que revisar los 59 cierre la cuestión.** Faltan las 150 InfoLEG.
- **No afirma la entidad de 6 documentos**, con confianza baja o ausente.
- **No incluyó nada en el corpus.**

## Manifest

```json
{
  "activos": 24,
  "alcance_de_la_revision": {
    "documentos_en_la_interfaz": 59,
    "infoleg_no_incluidos": 150,
    "nota": "terminar los 59 NO vuelve conocidas las brechas"
  },
  "auditoria_infoleg_propuesta": {
    "estratos": "dominio de adquisicion x criterio (materia/organismo) x decada",
    "por_estrato": 4,
    "pregunta": "el criterio de busqueda de InfoLEG (`energia` / `impositivo`) coincide con el dominio real de la norma?",
    "salida": "tasa de acuerdo por estrato, con la que se puede acotar cuantas de las 150 estarian mal clasificadas sin leerlas todas",
    "total_aproximado": 32
  },
  "brechas_por_dominio": {
    "contable": "desconocida",
    "financiero": "desconocida",
    "impositivo": "desconocida",
    "legal": "desconocida"
  },
  "cuarentena_unicos": 11,
  "disponibles_sin_cuarentena": 198,
  "documentos_caracterizados": 36,
  "empresariales_nuevos": 24,
  "infoleg_seleccionados_sin_auditar": 150,
  "maximo_potencial": 209,
  "membresias_empresariales_propuestas": {
    "contable": 24,
    "financiero": 9,
    "impositivo": 7,
    "legal": 24
  },
  "receta": "propuesta-fase4-v2.1",
  "reemplaza": "propuesta-fase4-v2 (membresias infladas por subcadena)",
  "salvedades": [
    "PROPUESTA. No se ingirio, no se descargo nada, no se toco PostgreSQL.",
    "Ningun documento tiene dominio verificado.",
    "Las brechas son DESCONOCIDAS por dos motivos: nadie reviso, y la revision de los 59 no cubre las 150 normas InfoLEG.",
    "Los conteos de membresia de la v2 estaban inflados por busqueda por subcadena; `impositivo` paso de 23 a 7.",
    "Las dos planillas de cuarentena ahora se leen con openpyxl y son distintas entre si.",
    "La revision humana es CIEGA en dos etapas y registra si la decision cambio al ver la propuesta automatica."
  ]
}
```
