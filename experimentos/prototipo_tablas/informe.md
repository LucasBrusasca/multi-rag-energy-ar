# Prototipo de representacion table-aware

- receta de extraccion: `tablas-v0.1`
- corpus base: `data/` del proyecto (los documentos se identifican por
  `document_id` y `artifact_id`, no por ruta local; el corpus no se versiona)
- **de solo lectura**: no se conecto a la base, no se reingirio, no se modifico ningun `chunk_uid`.

## PDF — `Edenor_EEFF_Consolidado_2025_09.pdf`

- identidad: `DOC-0004` / `ART-SHA256-F940AA7DB1B72CA1B9D216296C7B047FF98815CEDA2F68FC7FA7FE0B5E151393`
- entidad de las cifras: **no declarada**
- tablas detectadas: 64 — hechos emitidos: 1447

### `#/tables/0`

- **procedencia:** paginas [2]
- **table_uid:** `TBL-b4a47d9fba5ccba3`
- **table_segment_uid:** `TSEG-b4a47d9fba5ccba3`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** millones de ARS (moneda constante) (origen `texto_adyacente`, evidencia `#/texts/2`)
- **extraction_warnings:** ['sin_encabezado_propio', 'sin_encabezado_recuperable']
- **reglas:** —

**DESPUES** — hechos recuperables (37 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Información Legal ................................ ................................ ................................ ................................ ....... - (periodo no declarado) - millones de ARS (moneda constante) - valor 4 - pagina 2   [confianza: baja]
Edenor_EEFF_Consolidado_2025_09 - Estado del Resultado Integral Consolidado Condensado Intermedio ................................ ........................ - (periodo no declarado) - millones de ARS (moneda constante) - valor 5 - pagina 2   [confianza: baja]
Edenor_EEFF_Consolidado_2025_09 - Estado de Situación Financiera Consolidado Condensado Intermedio ................................ ...................... - (periodo no declarado) - millones de ARS (moneda constante) - valor 6 - pagina 2   [confianza: baja]
Edenor_EEFF_Consolidado_2025_09 - Estado de Cambios en el Patrimonio Consolidado Condensado Intermedio ................................ ............. - (periodo no declarado) - millones de ARS (moneda constante) - valor 8 - pagina 2   [confianza: baja]
Edenor_EEFF_Consolidado_2025_09 - Nota 1 | - (periodo no declarado) - millones de ARS (moneda constante) - valor ................. 11 - pagina 2   [confianza: baja]
Edenor_EEFF_Consolidado_2025_09 - Nota 2 | - (periodo no declarado) - millones de ARS (moneda constante) - valor 13 - pagina 2   [confianza: baja]
```

### `#/tables/1`

- **procedencia:** paginas [3]
- **table_uid:** `TBL-3a0b0704d56babad`
- **table_segment_uid:** `TSEG-3a0b0704d56babad`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=2']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/2`

- **procedencia:** paginas [4]
- **table_uid:** `TBL-39c379b2f45c79fd`
- **table_segment_uid:** `TSEG-39c379b2f45c79fd`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/25`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (4 en total, se muestran 4):

```text
Edenor_EEFF_Consolidado_2025_09 - Clase de acciones - Acciones escriturales ordinarias, de valor nominal 1, de 1 voto por acción / Clase A - (periodo no declarado) - ARS - valor 462.292.111 - pagina 4   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Clase de acciones - Acciones escriturales ordinarias, de valor nominal 1, de 1 voto por acción / Clase B (1) - (periodo no declarado) - ARS - valor 442.566.330 - pagina 4   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Clase de acciones - Acciones escriturales ordinarias, de valor nominal 1, de 1 voto por acción / Clase C (2) - (periodo no declarado) - ARS - valor 1.596.659 - pagina 4   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Clase de acciones - Acciones escriturales ordinarias, de valor nominal 1, de 1 voto por acción /  - (periodo no declarado) - ARS - valor 906.455.100 - pagina 4   [confianza: media]
```

### `#/tables/3`

- **procedencia:** paginas [5]
- **table_uid:** `TBL-8be64f3ac4071598`
- **table_segment_uid:** `TSEG-8be64f3ac4071598`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de ARS (moneda constante) (origen `texto_adyacente`, evidencia `#/texts/53`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:2!=6']

**DESPUES** — hechos recuperables (101 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Ingresos por servicios - (periodo no declarado) - millones de ARS (moneda constante) - valor 8 - pagina 5   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ingresos por servicios - al 2025-09-30 - millones de ARS (moneda constante) - valor 2.118.337 - pagina 5   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ingresos por servicios - al 2024-09-30 - millones de ARS (moneda constante) - valor 1.861.603 - pagina 5   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ingresos por servicios - al 2025-09-30 - millones de ARS (moneda constante) - valor 740.837 - pagina 5   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ingresos por servicios - al 2024-09-30 - millones de ARS (moneda constante) - valor 732.638 - pagina 5   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Compras de energía - (periodo no declarado) - millones de ARS (moneda constante) - valor 8 - pagina 5   [confianza: media]
```

### `#/tables/4`

- **procedencia:** paginas [6]
- **table_uid:** `TBL-9dbb486626e4fa77`
- **table_segment_uid:** `TSEG-9dbb486626e4fa77`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (moneda constante) (origen `texto_adyacente`, evidencia `#/texts/81`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:6!=4']

**DESPUES** — hechos recuperables (37 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - ACTIVO NO CORRIENTE / Propiedades, plantas y equipos - (periodo no declarado) - millones de ARS (moneda constante) - valor 13 - pagina 6   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - ACTIVO NO CORRIENTE / Propiedades, plantas y equipos - al 2025-09-30 - millones de ARS (moneda constante) - valor 3.803.789 - pagina 6   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - ACTIVO NO CORRIENTE / Propiedades, plantas y equipos - al 2024-12-31 - millones de ARS (moneda constante) - valor 3.662.175 - pagina 6   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - ACTIVO NO CORRIENTE / Participación en negocios conjuntos - al 2025-09-30 - millones de ARS (moneda constante) - valor 78 - pagina 6   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - ACTIVO NO CORRIENTE / Participación en negocios conjuntos - al 2024-12-31 - millones de ARS (moneda constante) - valor 148 - pagina 6   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - ACTIVO NO CORRIENTE / Activos por derecho de uso - (periodo no declarado) - millones de ARS (moneda constante) - valor 14 - pagina 6   [confianza: media]
```

### `#/tables/5`

- **procedencia:** paginas [7]
- **table_uid:** `TBL-1c0bfd218515b344`
- **table_segment_uid:** `TSEG-1c0bfd218515b344`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (moneda constante) (origen `texto_adyacente`, evidencia `#/texts/94`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0]']

**DESPUES** — hechos recuperables (83 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Capital y reservas atribuibles a los propietarios / Capital social - (periodo no declarado) - millones de ARS (moneda constante) - valor 21 - pagina 7   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Capital y reservas atribuibles a los propietarios / Capital social - al 2025-09-30 - millones de ARS (moneda constante) - valor 875 - pagina 7   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Capital y reservas atribuibles a los propietarios / Capital social - al 2024-12-31 - millones de ARS (moneda constante) - valor 875 - pagina 7   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Capital y reservas atribuibles a los propietarios / Ajuste sobre capital social - (periodo no declarado) - millones de ARS (moneda constante) - valor 21 - pagina 7   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Capital y reservas atribuibles a los propietarios / Ajuste sobre capital social - al 2025-09-30 - millones de ARS (moneda constante) - valor 905.716 - pagina 7   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Capital y reservas atribuibles a los propietarios / Ajuste sobre capital social - al 2024-12-31 - millones de ARS (moneda constante) - valor 905.716 - pagina 7   [confianza: media]
```

### `#/tables/6`

- **procedencia:** paginas [8]
- **table_uid:** `TBL-7fe3a3212fc9463d`
- **table_segment_uid:** `TSEG-7fe3a3212fc9463d`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de ARS (moneda constante) (origen `texto_adyacente`, evidencia `#/texts/121`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=13']

**DESPUES** — hechos recuperables (43 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Aumento de Reserva por Plan de Compensación en Acciones - (periodo no declarado) - millones de ARS (moneda constante) - valor 74 - pagina 8   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Aumento de Reserva por Plan de Compensación en Acciones - (periodo no declarado) - millones de ARS (moneda constante) - valor 74 - pagina 8   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Pago en acciones por el Plan de Compensación en Acciones - (periodo no declarado) - millones de ARS (moneda constante) - valor 50 - pagina 8   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Pago en acciones por el Plan de Compensación en Acciones - (periodo no declarado) - millones de ARS (moneda constante) - valor (50) - pagina 8   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Pago en acciones por el Plan de Compensación en Acciones - (periodo no declarado) - millones de ARS (moneda constante) - valor 74 - pagina 8   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Pago en acciones por el Plan de Compensación en Acciones - (periodo no declarado) - millones de ARS (moneda constante) - valor (74) - pagina 8   [confianza: media]
```

### `#/tables/7`

- **procedencia:** paginas [9]
- **table_uid:** `TBL-501aebcb1f5bbade`
- **table_segment_uid:** `TSEG-501aebcb1f5bbade`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (moneda constante) (origen `texto_adyacente`, evidencia `#/texts/146`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:13!=4']

**DESPUES** — hechos recuperables (78 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Flujo de efectivo de las actividades operativas / Resultado del período - al 2025-09-30 - millones de ARS (moneda constante) - valor 179.461 - pagina 9   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Flujo de efectivo de las actividades operativas / Resultado del período - al 2024-09-30 - millones de ARS (moneda constante) - valor 351.744 - pagina 9   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ajustes para arribar al flujo neto de efectivo provenientes de las actividades operativas: / Depreciaciones de propiedades, plantas y equipos - (periodo no declarado) - millones de ARS (moneda constante) - valor 13 - pagina 9   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ajustes para arribar al flujo neto de efectivo provenientes de las actividades operativas: / Depreciaciones de propiedades, plantas y equipos - al 2025-09-30 - millones de ARS (moneda constante) - valor 136.018 - pagina 9   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ajustes para arribar al flujo neto de efectivo provenientes de las actividades operativas: / Depreciaciones de propiedades, plantas y equipos - al 2024-09-30 - millones de ARS (moneda constante) - valor 138.378 - pagina 9   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ajustes para arribar al flujo neto de efectivo provenientes de las actividades operativas: / Amortizaciones de activos por derecho de uso - (periodo no declarado) - millones de ARS (moneda constante) - valor 14 - pagina 9   [confianza: media]
```

### `#/tables/8`

- **procedencia:** paginas [10]
- **table_uid:** `TBL-e051e7a68abcf0fb`
- **table_segment_uid:** `TSEG-e051e7a68abcf0fb`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (moneda constante) (origen `texto_adyacente`, evidencia `#/texts/174`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0]']

**DESPUES** — hechos recuperables (39 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Flujo de efectivo de las actividades de inversión / Pago por adquisiciones de propiedades, plantas y equipos - al 2025-09-30 - millones de ARS (moneda constante) - valor (250.194) - pagina 10   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Flujo de efectivo de las actividades de inversión / Pago por adquisiciones de propiedades, plantas y equipos - al 2024-09-30 - millones de ARS (moneda constante) - valor (306.816) - pagina 10   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Flujo de efectivo de las actividades de inversión / Venta (Compra) neta de Títulos valores y Fondos comunes de inversión - al 2025-09-30 - millones de ARS (moneda constante) - valor 27.129 - pagina 10   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Flujo de efectivo de las actividades de inversión / Venta (Compra) neta de Títulos valores y Fondos comunes de inversión - al 2024-09-30 - millones de ARS (moneda constante) - valor (157.046) - pagina 10   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Flujo de efectivo de las actividades de inversión / Pago por adquisiciones de participaciones minoritarias - al 2025-09-30 - millones de ARS (moneda constante) - valor (30.730) - pagina 10   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Flujo de efectivo de las actividades de inversión / Pago por adquisición de subsidiaria - al 2024-09-30 - millones de ARS (moneda constante) - valor (142) - pagina 10   [confianza: media]
```

### `#/tables/9`

- **procedencia:** paginas [13]
- **table_uid:** `TBL-4d2cccf2d55ff691`
- **table_segment_uid:** `TSEG-4d2cccf2d55ff691`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** moneda homogenea (origen `celda_encabezado`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:10->13']

**DESPUES** — hechos recuperables (19 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Resultado antes de impuestos - al 2024-09-30 - moneda homogenea - valor 157.702 - pagina 13   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resultado antes de impuestos - (periodo no declarado) - moneda homogenea - valor 50.122 - pagina 13   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resultado antes de impuestos - al 2024-09-30 - moneda homogenea - valor 207.824 - pagina 13   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resultado antes de impuestos - al 2024-09-30 - moneda homogenea - valor 207.824 - pagina 13   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Impuesto a las ganancias - al 2024-09-30 - moneda homogenea - valor 77.367 - pagina 13   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Impuesto a las ganancias - (periodo no declarado) - moneda homogenea - valor 24.588 - pagina 13   [confianza: media]
```

### `#/tables/10`

- **procedencia:** paginas [15]
- **table_uid:** `TBL-26d94636ec1dc1f7`
- **table_segment_uid:** `TSEG-26d94636ec1dc1f7`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0],inferido=[0, 1, 2]', 'unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:13->15']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Resolución - ENRE N° 224/2025 - (periodo no declarado) - (unidad no declarada) - valor 3,50% - pagina 15   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resolución - ENRE N° 304/2025 - (periodo no declarado) - (unidad no declarada) - valor 3,00% - pagina 15   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resolución - ENRE N° 401/2025 - (periodo no declarado) - (unidad no declarada) - valor 3,24% - pagina 15   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resolución - ENRE N° 469/2025 - (periodo no declarado) - (unidad no declarada) - valor 0,75% - pagina 15   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resolución - ENRE N° 568/2025 - (periodo no declarado) - (unidad no declarada) - valor 2,10% - pagina 15   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resolución - ENRE N° 614/2025 - (periodo no declarado) - (unidad no declarada) - valor 2,97% - pagina 15   [confianza: media]
```

### `#/tables/11`

- **procedencia:** paginas [20]
- **table_uid:** `TBL-22f1444a52eb78a0`
- **table_segment_uid:** `TSEG-22f1444a52eb78a0`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:15->20']

**DESPUES** — hechos recuperables (43 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - ACTIVO CORRIENTE / Otros créditos - (periodo no declarado) - (unidad no declarada) - valor 7,5 - pagina 20   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - ACTIVO CORRIENTE / Otros créditos - (periodo no declarado) - (unidad no declarada) - valor 1371,000 - pagina 20   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - ACTIVO CORRIENTE / Otros créditos - al 2025-09-30 - (unidad no declarada) - valor 10.283 - pagina 20   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - ACTIVO CORRIENTE / Otros créditos - al 2024-12-31 - (unidad no declarada) - valor 2.008 - pagina 20   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - (periodo no declarado) - (unidad no declarada) - valor 3,1 - pagina 20   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - (periodo no declarado) - (unidad no declarada) - valor 1371,000 - pagina 20   [confianza: media]
```

### `#/tables/12`

- **procedencia:** paginas [21]
- **table_uid:** `TBL-4ca13cbdf2de6215`
- **table_segment_uid:** `TSEG-4ca13cbdf2de6215`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 13],inferido=[0]', 'unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:6!=4']

**DESPUES** — hechos recuperables (14 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Otros créditos: / Activos cedidos y en custodia - (periodo no declarado) - (unidad no declarada) - valor 8.073 - pagina 21   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Activos financieros a valor razonable con cambios en resultados: / Títulos valores - (periodo no declarado) - (unidad no declarada) - valor 89.337 - pagina 21   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Activos financieros a valor razonable con cambios en resultados: / Fondos comunes de inversión - (periodo no declarado) - (unidad no declarada) - valor 347.807 - pagina 21   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Activos financieros a valor razonable con cambios en resultados: / Acciones - (periodo no declarado) - (unidad no declarada) - valor 33.792 - pagina 21   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Efectivo y equivalentes de efectivo: / Fondos comunes de inversión - (periodo no declarado) - (unidad no declarada) - valor 597 - pagina 21   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Efectivo y equivalentes de efectivo: / Total activos - (periodo no declarado) - (unidad no declarada) - valor 445.814 - pagina 21   [confianza: media]
```

### `#/tables/13`

- **procedencia:** paginas [21]
- **table_uid:** `TBL-cd73223b1dc4fc98`
- **table_segment_uid:** `TSEG-cd73223b1dc4fc98`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:21->21']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/14`

- **procedencia:** paginas [24]
- **table_uid:** `TBL-3c4a727f7f3f417c`
- **table_segment_uid:** `TSEG-3c4a727f7f3f417c`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:21->24']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/15`

- **procedencia:** paginas [24]
- **table_uid:** `TBL-0acdd600306f3cd3`
- **table_segment_uid:** `TSEG-0acdd600306f3cd3`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:24->24']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/16`

- **procedencia:** paginas [25]
- **table_uid:** `TBL-697767f0e85b46a1`
- **table_segment_uid:** `TSEG-697767f0e85b46a1`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/17`

- **procedencia:** paginas [25]
- **table_uid:** `TBL-539d6b2f59e0c58d`
- **table_segment_uid:** `TSEG-539d6b2f59e0c58d`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** ARS (origen `celda_encabezado`, evidencia `r1c2`)
- **extraction_warnings:** ['moneda_inferida_de_simbolo_pesos', 'escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:25->25']

**DESPUES** — hechos recuperables (28 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Ventas de energía / Pequeñas demandas: Uso residencial y alumbrado público (T1) - al 2025-09-30 - ARS - valor 10.245 - pagina 25   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ventas de energía / Pequeñas demandas: Uso residencial y alumbrado público (T1) - al 2025-09-30 - ARS - valor 1.393.214 - pagina 25   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ventas de energía / Pequeñas demandas: Uso residencial y alumbrado público (T1) - al 2024-09-30 - ARS - valor 10.312 - pagina 25   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ventas de energía / Pequeñas demandas: Uso residencial y alumbrado público (T1) - al 2024-09-30 - ARS - valor 1.153.318 - pagina 25   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ventas de energía / Demanda mediana: Comercial e industrial (T2) - al 2025-09-30 - ARS - valor 1.153 - pagina 25   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ventas de energía / Demanda mediana: Comercial e industrial (T2) - al 2025-09-30 - ARS - valor 249.439 - pagina 25   [confianza: media]
```

### `#/tables/18`

- **procedencia:** paginas [26]
- **table_uid:** `TBL-5b2eafb36dc5faf9`
- **table_segment_uid:** `TSEG-5b2eafb36dc5faf9`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0]']

**DESPUES** — hechos recuperables (59 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Concepto - Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 132.936 - pagina 26   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Concepto - Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 15.802 - pagina 26   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Concepto - Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 37.631 - pagina 26   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Concepto - Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 186.369 - pagina 26   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Concepto - Planes de pensión - (periodo no declarado) - (unidad no declarada) - valor 3.883 - pagina 26   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Concepto - Planes de pensión - (periodo no declarado) - (unidad no declarada) - valor 462 - pagina 26   [confianza: media]
```

### `#/tables/19`

- **procedencia:** paginas [26]
- **table_uid:** `TBL-da9f8df976b23eed`
- **table_segment_uid:** `TSEG-da9f8df976b23eed`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/636`)
- **extraction_warnings:** ['moneda_inferida_de_simbolo_pesos', 'escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:26->26']

**DESPUES** — hechos recuperables (59 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Concepto - Remuneraciones y cargas sociales - (periodo no declarado) - ARS - valor 143.966 - pagina 26   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Concepto - Remuneraciones y cargas sociales - (periodo no declarado) - ARS - valor 18.707 - pagina 26   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Concepto - Remuneraciones y cargas sociales - (periodo no declarado) - ARS - valor 43.745 - pagina 26   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Concepto - Remuneraciones y cargas sociales - (periodo no declarado) - ARS - valor 206.418 - pagina 26   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Concepto - Planes de pensión - (periodo no declarado) - ARS - valor 11.622 - pagina 26   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Concepto - Planes de pensión - (periodo no declarado) - ARS - valor 1.510 - pagina 26   [confianza: media]
```

### `#/tables/20`

- **procedencia:** paginas [27]
- **table_uid:** `TBL-f9e37e5f8ecac8e9`
- **table_segment_uid:** `TSEG-f9e37e5f8ecac8e9`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:5!=4']

**DESPUES** — hechos recuperables (34 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Otros ingresos operativos / Cargos por mora de clientes - al 2025-09-30 - (unidad no declarada) - valor 20.911 - pagina 27   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Otros ingresos operativos / Cargos por mora de clientes - al 2024-09-30 - (unidad no declarada) - valor 20.877 - pagina 27   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Otros ingresos operativos / Comisiones por cobranzas - al 2025-09-30 - (unidad no declarada) - valor 2.190 - pagina 27   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Otros ingresos operativos / Comisiones por cobranzas - al 2024-09-30 - (unidad no declarada) - valor 2.796 - pagina 27   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Otros ingresos operativos / Multas a proveedores - al 2025-09-30 - (unidad no declarada) - valor 1.629 - pagina 27   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Otros ingresos operativos / Multas a proveedores - al 2024-09-30 - (unidad no declarada) - valor 1.089 - pagina 27   [confianza: media]
```

### `#/tables/21`

- **procedencia:** paginas [27]
- **table_uid:** `TBL-fc50a0683ed0459d`
- **table_segment_uid:** `TSEG-fc50a0683ed0459d`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:27->27']

**DESPUES** — hechos recuperables (28 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Gastos financieros / Intereses comerciales - al 2025-09-30 - (unidad no declarada) - valor (112.125) - pagina 27   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Gastos financieros / Intereses comerciales - al 2024-09-30 - (unidad no declarada) - valor (275.594) - pagina 27   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Gastos financieros / Intereses por préstamos - al 2025-09-30 - (unidad no declarada) - valor (76.677) - pagina 27   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Gastos financieros / Intereses por préstamos - al 2024-09-30 - (unidad no declarada) - valor (33.883) - pagina 27   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Gastos financieros / Intereses por sanciones - al 2025-09-30 - (unidad no declarada) - valor (662) - pagina 27   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Gastos financieros / Intereses por sanciones - al 2024-09-30 - (unidad no declarada) - valor (88.762) - pagina 27   [confianza: media]
```

### `#/tables/22`

- **procedencia:** paginas [28]
- **table_uid:** `TBL-92e4a4ab75053818`
- **table_segment_uid:** `TSEG-92e4a4ab75053818`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=5']

**DESPUES** — hechos recuperables (12 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Resultado del período atribuible a los propietarios de la Sociedad - saldo al 2025-09-30 - (unidad no declarada) - valor 179.461 - pagina 28   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resultado del período atribuible a los propietarios de la Sociedad - saldo al 2024-09-30 - (unidad no declarada) - valor 351.744 - pagina 28   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resultado del período atribuible a los propietarios de la Sociedad - saldo al 2025-09-30 - (unidad no declarada) - valor 40.638 - pagina 28   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resultado del período atribuible a los propietarios de la Sociedad - saldo al 2024-09-30 - (unidad no declarada) - valor 152.402 - pagina 28   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Promedio ponderado de acciones ordinarias en circulación - saldo al 2025-09-30 - (unidad no declarada) - valor 875 - pagina 28   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Promedio ponderado de acciones ordinarias en circulación - saldo al 2024-09-30 - (unidad no declarada) - valor 875 - pagina 28   [confianza: media]
```

### `#/tables/23`

- **procedencia:** paginas [29]
- **table_uid:** `TBL-f2e8e882109a92a2`
- **table_segment_uid:** `TSEG-f2e8e882109a92a2`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:5!=9']

**DESPUES** — hechos recuperables (75 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.24 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 99.270 - pagina 29   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.24 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 899.400 - pagina 29   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.24 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 2.278.607 - pagina 29   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.24 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 1.021.365 - pagina 29   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.24 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 362.286 - pagina 29   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.24 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 1.099.635 - pagina 29   [confianza: media]
```

### `#/tables/24`

- **procedencia:** paginas [30]
- **table_uid:** `TBL-1e7cfb954210ebaf`
- **table_segment_uid:** `TSEG-1e7cfb954210ebaf`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0]']

**DESPUES** — hechos recuperables (74 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.23 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 97.388 - pagina 30   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.23 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 877.037 - pagina 30   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.23 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 2.202.192 - pagina 30   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.23 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 976.896 - pagina 30   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.23 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 311.144 - pagina 30   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31.12.23 / Valor de origen - (periodo no declarado) - (unidad no declarada) - valor 864.195 - pagina 30   [confianza: media]
```

### `#/tables/25`

- **procedencia:** paginas [31]
- **table_uid:** `TBL-a9f4627375c32e61`
- **table_segment_uid:** `TSEG-a9f4627375c32e61`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:9!=3']

**DESPUES** — hechos recuperables (2 en total, se muestran 2):

```text
Edenor_EEFF_Consolidado_2025_09 - Total activos por derecho de uso - al 2025-09-30 - (unidad no declarada) - valor 9.838 - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Total activos por derecho de uso - al 2024-12-31 - (unidad no declarada) - valor 12.747 - pagina 31   [confianza: media]
```

### `#/tables/26`

- **procedencia:** paginas [31]
- **table_uid:** `TBL-68f256f0950604c6`
- **table_segment_uid:** `TSEG-68f256f0950604c6`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:31->31']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Saldo al inicio del ejercicio - al 2025-09-30 - (unidad no declarada) - valor 12.747 - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Saldo al inicio del ejercicio - al 2024-09-30 - (unidad no declarada) - valor 9.401 - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Altas - al 2025-09-30 - (unidad no declarada) - valor 2.476 - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Altas - al 2024-09-30 - (unidad no declarada) - valor 5.128 - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Amortizaciones - al 2025-09-30 - (unidad no declarada) - valor (5.385) - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Amortizaciones - al 2024-09-30 - (unidad no declarada) - valor (8.553) - pagina 31   [confianza: media]
```

### `#/tables/27`

- **procedencia:** paginas [31]
- **table_uid:** `TBL-1cc3194b2d62afb3`
- **table_segment_uid:** `TSEG-1cc3194b2d62afb3`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:31->31']

**DESPUES** — hechos recuperables (2 en total, se muestran 2):

```text
Edenor_EEFF_Consolidado_2025_09 - Materiales y repuestos - al 2025-09-30 - (unidad no declarada) - valor 210.550 - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Materiales y repuestos - al 2024-12-31 - (unidad no declarada) - valor 182.672 - pagina 31   [confianza: media]
```

### `#/tables/28`

- **procedencia:** paginas [31]
- **table_uid:** `TBL-dd048c33ccbf7cee`
- **table_segment_uid:** `TSEG-dd048c33ccbf7cee`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:31->31']

**DESPUES** — hechos recuperables (22 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - No corriente: / Sociedades relacionadas - al 2025-09-30 - (unidad no declarada) - valor 526 - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente: / Sociedades relacionadas - al 2024-12-31 - (unidad no declarada) - valor 150 - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente: / Activos cedidos y en custodia (1) - al 2025-09-30 - (unidad no declarada) - valor 8.073 - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente: / Activos cedidos y en custodia (1) - al 2024-12-31 - (unidad no declarada) - valor 10.910 - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente: / Depósitos judiciales - al 2025-09-30 - (unidad no declarada) - valor 2.149 - pagina 31   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente: / Depósitos judiciales - al 2024-12-31 - (unidad no declarada) - valor 1.791 - pagina 31   [confianza: media]
```

### `#/tables/29`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-01eba8407c41140a`
- **table_segment_uid:** `TSEG-01eba8407c41140a`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=3']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Saldo al inicio del ejercicio - al 2025-09-30 - (unidad no declarada) - valor 63 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Saldo al inicio del ejercicio - al 2024-09-30 - (unidad no declarada) - valor 157 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Previsión por deterioro del valor - al 2025-09-30 - (unidad no declarada) - valor 1.874 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Previsión por deterioro del valor - al 2024-09-30 - (unidad no declarada) - valor 78 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RECPAM - al 2025-09-30 - (unidad no declarada) - valor (146) - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RECPAM - al 2024-09-30 - (unidad no declarada) - valor (145) - pagina 32   [confianza: media]
```

### `#/tables/30`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-714e89df4d21c5dd`
- **table_segment_uid:** `TSEG-714e89df4d21c5dd`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:32->32']

**DESPUES** — hechos recuperables (16 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Corriente: / Por venta de energía - Facturada - al 2025-09-30 - (unidad no declarada) - valor 254.665 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente: / Por venta de energía - Facturada - al 2024-12-31 - (unidad no declarada) - valor 200.178 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente: / En gestión judicial - al 2025-09-30 - (unidad no declarada) - valor 1.341 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente: / En gestión judicial - al 2024-12-31 - (unidad no declarada) - valor 556 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente: / Previsión por desvalorización de créditos por ventas - al 2025-09-30 - (unidad no declarada) - valor (26.437) - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente: / Previsión por desvalorización de créditos por ventas - al 2024-12-31 - (unidad no declarada) - valor (13.861) - pagina 32   [confianza: media]
```

### `#/tables/31`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-4b2e90481f96f270`
- **table_segment_uid:** `TSEG-4b2e90481f96f270`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:32->32']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Saldo al inicio del ejercicio - al 2025-09-30 - (unidad no declarada) - valor 13.861 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Saldo al inicio del ejercicio - al 2024-09-30 - (unidad no declarada) - valor 16.577 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Previsión por deterioro del valor - al 2025-09-30 - (unidad no declarada) - valor 19.530 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Previsión por deterioro del valor - al 2024-09-30 - (unidad no declarada) - valor 16.515 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Utilizaciones - al 2025-09-30 - (unidad no declarada) - valor (3.818) - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Utilizaciones - al 2024-09-30 - (unidad no declarada) - valor (3.161) - pagina 32   [confianza: media]
```

### `#/tables/32`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-aeededcccd993906`
- **table_segment_uid:** `TSEG-aeededcccd993906`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:32->32']

**DESPUES** — hechos recuperables (2 en total, se muestran 2):

```text
Edenor_EEFF_Consolidado_2025_09 - Títulos valores - al 2025-09-30 - (unidad no declarada) - valor 10.339 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Títulos valores - al 2024-12-31 - (unidad no declarada) - valor 12.440 - pagina 32   [confianza: media]
```

### `#/tables/33`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-830e230fc16e14a1`
- **table_segment_uid:** `TSEG-830e230fc16e14a1`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:32->32']

**DESPUES** — hechos recuperables (7 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - No corriente / Acciones - al 2025-09-30 - (unidad no declarada) - valor 33.792 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Títulos valores - al 2025-09-30 - (unidad no declarada) - valor 89.337 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Títulos valores - al 2024-12-31 - (unidad no declarada) - valor 139.643 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Fondos comunes de inversión - al 2025-09-30 - (unidad no declarada) - valor 347.807 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Fondos comunes de inversión - al 2024-12-31 - (unidad no declarada) - valor 303.522 - pagina 32   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Total corriente - al 2025-09-30 - (unidad no declarada) - valor 437.144 - pagina 32   [confianza: media]
```

### `#/tables/34`

- **procedencia:** paginas [33]
- **table_uid:** `TBL-1fe93235c304ad24`
- **table_segment_uid:** `TSEG-1fe93235c304ad24`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/769`)
- **extraction_warnings:** ['moneda_inferida_de_simbolo_pesos', 'escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (11 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Caja y bancos - al 2025-09-30 - ARS - valor 29.602 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Caja y bancos - al 2024-12-31 - ARS - valor 24.615 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Caja y bancos - al 2024-09-30 - ARS - valor 2.954 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Depósitos a plazo fijo - al 2025-09-30 - ARS - valor 7.128 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Depósitos a plazo fijo - al 2024-12-31 - ARS - valor 4.011 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Fondos comunes de inversión - al 2025-09-30 - ARS - valor 597 - pagina 33   [confianza: media]
```

### `#/tables/35`

- **procedencia:** paginas [33]
- **table_uid:** `TBL-2b90e4ac81b34ff6`
- **table_segment_uid:** `TSEG-2b90e4ac81b34ff6`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:33->33']

**DESPUES** — hechos recuperables (9 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Efectivo y equivalentes de efectivo - al 2025-09-30 - (unidad no declarada) - valor 37.327 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Efectivo y equivalentes de efectivo - al 2024-12-31 - (unidad no declarada) - valor 29.173 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Efectivo y equivalentes de efectivo - al 2024-09-30 - (unidad no declarada) - valor 3.500 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Giros en descubierto (Nota 25) - al 2025-09-30 - (unidad no declarada) - valor (21.805) - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Giros en descubierto (Nota 25) - al 2024-12-31 - (unidad no declarada) - valor (67.655) - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Giros en descubierto (Nota 25) - al 2024-09-30 - (unidad no declarada) - valor (46.804) - pagina 33   [confianza: media]
```

### `#/tables/36`

- **procedencia:** paginas [33]
- **table_uid:** `TBL-5ceb57d447c4d6b8`
- **table_segment_uid:** `TSEG-5ceb57d447c4d6b8`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:33->33']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Al 31 de diciembre de 2023 - (periodo no declarado) - (unidad no declarada) - valor 925.991 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31 de diciembre de 2023 - (periodo no declarado) - (unidad no declarada) - valor 12.524 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31 de diciembre de 2023 - (periodo no declarado) - (unidad no declarada) - valor 938.515 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Pago en acciones por el Plan de Compensación en Acciones - (periodo no declarado) - (unidad no declarada) - valor 74 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Pago en acciones por el Plan de Compensación en Acciones - (periodo no declarado) - (unidad no declarada) - valor 74 - pagina 33   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Al 31 de diciembre de 2024 y al 30 de septiembre de 2025 - (periodo no declarado) - (unidad no declarada) - valor 925.991 - pagina 33   [confianza: media]
```

### `#/tables/37`

- **procedencia:** paginas [34]
- **table_uid:** `TBL-f7a4b6e0ee834cea`
- **table_segment_uid:** `TSEG-f7a4b6e0ee834cea`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=3']

**DESPUES** — hechos recuperables (22 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - No corriente / Garantías de clientes - al 2025-09-30 - (unidad no declarada) - valor 4.082 - pagina 34   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Garantías de clientes - al 2024-12-31 - (unidad no declarada) - valor 3.147 - pagina 34   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Contribuciones de clientes - al 2025-09-30 - (unidad no declarada) - valor 248 - pagina 34   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Contribuciones de clientes - al 2024-12-31 - (unidad no declarada) - valor 292 - pagina 34   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Total no corriente - al 2025-09-30 - (unidad no declarada) - valor 4.330 - pagina 34   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Total no corriente - al 2024-12-31 - (unidad no declarada) - valor 3.439 - pagina 34   [confianza: media]
```

### `#/tables/38`

- **procedencia:** paginas [34]
- **table_uid:** `TBL-fdce5e356cbcff5d`
- **table_segment_uid:** `TSEG-fdce5e356cbcff5d`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/789`)
- **extraction_warnings:** ['moneda_inferida_de_simbolo_pesos', 'escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:34->34']

**DESPUES** — hechos recuperables (21 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - No corriente / Plan de pagos CAMMESA - al 2025-09-30 - ARS - valor 348.018 - pagina 34   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Plan de pagos CAMMESA - al 2024-12-31 - ARS - valor 220.751 - pagina 34   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Sanciones y bonificaciones ENRE - al 2025-09-30 - ARS - valor 5.549 - pagina 34   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Sanciones y bonificaciones ENRE - al 2024-12-31 - ARS - valor 2.032 - pagina 34   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Arrendamiento financiero (1) - al 2025-09-30 - ARS - valor 3.974 - pagina 34   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Arrendamiento financiero (1) - al 2024-12-31 - ARS - valor 6.110 - pagina 34   [confianza: media]
```

### `#/tables/39`

- **procedencia:** paginas [34]
- **table_uid:** `TBL-93433883a7aa6a9d`
- **table_segment_uid:** `TSEG-93433883a7aa6a9d`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:34->34']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/40`

- **procedencia:** paginas [35]
- **table_uid:** `TBL-fbd3837dbf5ca16e`
- **table_segment_uid:** `TSEG-fbd3837dbf5ca16e`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/802`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:2!=3']

**DESPUES** — hechos recuperables (14 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Saldo al inicio del ejercicio - al 2025-09-30 - ARS - valor 10.838 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Saldo al inicio del ejercicio - al 2024-09-30 - ARS - valor 7.736 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Altas - al 2025-09-30 - ARS - valor 2.275 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Altas - al 2024-09-30 - ARS - valor 3.250 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Pagos - al 2025-09-30 - ARS - valor (9.582) - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Pagos - al 2024-09-30 - ARS - valor (10.048) - pagina 35   [confianza: media]
```

### `#/tables/41`

- **procedencia:** paginas [35]
- **table_uid:** `TBL-0fe7df2f6e79db98`
- **table_segment_uid:** `TSEG-0fe7df2f6e79db98`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:35->35']

**DESPUES** — hechos recuperables (15 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - No corriente / Obligaciones Negociables (1) - al 2025-09-30 - (unidad no declarada) - valor 482.009 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Obligaciones Negociables (1) - al 2024-12-31 - (unidad no declarada) - valor 432.913 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Préstamos financieros (2) - al 2025-09-30 - (unidad no declarada) - valor 65.000 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Total no corriente - al 2025-09-30 - (unidad no declarada) - valor 547.009 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Total no corriente - al 2024-12-31 - (unidad no declarada) - valor 432.913 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Obligaciones Negociables (1) - al 2025-09-30 - (unidad no declarada) - valor 125.056 - pagina 35   [confianza: media]
```

### `#/tables/42`

- **procedencia:** paginas [35]
- **table_uid:** `TBL-bc0e107810944c46`
- **table_segment_uid:** `TSEG-bc0e107810944c46`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** ARS (origen `celda_encabezado`, evidencia `r0c1`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:35->35']

**DESPUES** — hechos recuperables (41 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Credicoop - (periodo no declarado) - ARS - valor 37% - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Credicoop - saldo al 2025-09-30 - ARS - valor 3.214 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Credicoop - (periodo no declarado) - ARS - valor 45% - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Credicoop - saldo al 2025-09-30 - ARS - valor 3.089 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Credicoop - saldo al 2024-12-31 - ARS - valor 6.123 - pagina 35   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Credicoop - saldo al 2025-09-30 - ARS - valor 6.303 - pagina 35   [confianza: media]
```

### `#/tables/43`

- **procedencia:** paginas [37]
- **table_uid:** `TBL-dda316f2ee578228`
- **table_segment_uid:** `TSEG-dda316f2ee578228`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de ARS (origen `celda_encabezado`, evidencia `r0c7`)
- **extraction_warnings:** ['moneda_inferida_de_simbolo_pesos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:35->37']

**DESPUES** — hechos recuperables (42 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Tasa variable - Vencimiento 2025 (*) - (periodo no declarado) - millones de ARS - valor 4 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa variable - Vencimiento 2025 (*) - saldo al 2024-12-31 - millones de ARS - valor 24.301.486 - pagina 37   [confianza: alta]
Edenor_EEFF_Consolidado_2025_09 - Tasa variable - Vencimiento 2025 (*) - (periodo no declarado) - millones de ARS - valor (24.301.486) - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa variable - Vencimiento 2025 (*) - saldo al 2024-12-31 - millones de ARS - valor 31.203 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa fija - Vencimiento 2025 - (periodo no declarado) - millones de ARS - valor 1 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa fija - Vencimiento 2025 - saldo al 2024-12-31 - millones de ARS - valor 8.218.667 - pagina 37   [confianza: alta]
```

### `#/tables/44`

- **procedencia:** paginas [37]
- **table_uid:** `TBL-1efa55a18a53fa34`
- **table_segment_uid:** `TSEG-1efa55a18a53fa34`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de USD (origen `celda_encabezado`, evidencia `r0c7`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:37->37']

**DESPUES** — hechos recuperables (39 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Tasa fija - Vencimiento 2024 - (periodo no declarado) - millones de USD - valor 2 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa fija - Vencimiento 2024 - saldo al 2023-12-31 - millones de USD - valor 60.945.000 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa fija - Vencimiento 2024 - (periodo no declarado) - millones de USD - valor (39.700.207) - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa fija - Vencimiento 2024 - (periodo no declarado) - millones de USD - valor (21.244.793) - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa fija - Vencimiento 2024 - saldo al 2023-12-31 - millones de ARS - valor 132.413 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa variable - Vencimiento 2025 (*) 4 - (periodo no declarado) - millones de USD - valor 24.301.486 - pagina 37   [confianza: media]
```

### `#/tables/45`

- **procedencia:** paginas [37]
- **table_uid:** `TBL-31d2298d566f70c5`
- **table_segment_uid:** `TSEG-31d2298d566f70c5`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** USD (origen `texto_adyacente`, evidencia `#/texts/849`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:37->37']

**DESPUES** — hechos recuperables (13 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Tasa fija / Menos de 1 año - al 2025-09-30 - USD - valor 227.630 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa fija / Menos de 1 año - al 2024-12-31 - USD - valor 85.083 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa fija / Entre 1 y 2 años - al 2025-09-30 - USD - valor 134.616 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa fija / Entre 1 y 2 años - al 2024-12-31 - USD - valor 119.768 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa fija / Entre 2 y 5 años - al 2025-09-30 - USD - valor 347.393 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa fija / Entre 2 y 5 años - al 2024-12-31 - USD - valor 313.145 - pagina 37   [confianza: media]
```

### `#/tables/46`

- **procedencia:** paginas [37]
- **table_uid:** `TBL-fb413f46f7f42aa2`
- **table_segment_uid:** `TSEG-fb413f46f7f42aa2`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:37->37']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Pesos argentinos - al 2025-09-30 - (unidad no declarada) - valor 201.039 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Pesos argentinos - al 2024-12-31 - (unidad no declarada) - valor 122.028 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Dólares estadounidenses - al 2025-09-30 - (unidad no declarada) - valor 602.565 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Dólares estadounidenses - al 2024-12-31 - (unidad no declarada) - valor 448.135 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Total préstamos - al 2025-09-30 - (unidad no declarada) - valor 803.604 - pagina 37   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Total préstamos - al 2024-12-31 - (unidad no declarada) - valor 570.163 - pagina 37   [confianza: media]
```

### `#/tables/47`

- **procedencia:** paginas [38]
- **table_uid:** `TBL-01a757e9e27b1f6c`
- **table_segment_uid:** `TSEG-01a757e9e27b1f6c`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0]']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - No corriente / Contribuciones de clientes no sujetas a devolución - al 2025-09-30 - (unidad no declarada) - valor 35.323 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Contribuciones de clientes no sujetas a devolución - al 2024-12-31 - (unidad no declarada) - valor 27.321 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Acuerdo de Regularización de Obligaciones - Plan de inversiones (1) - al 2025-09-30 - (unidad no declarada) - valor 97.964 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Acuerdo de Regularización de Obligaciones - Plan de inversiones (1) - al 2024-12-31 - (unidad no declarada) - valor 104.562 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Total no corriente - al 2025-09-30 - (unidad no declarada) - valor 133.287 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Total no corriente - al 2024-12-31 - (unidad no declarada) - valor 131.883 - pagina 38   [confianza: media]
```

### `#/tables/48`

- **procedencia:** paginas [38]
- **table_uid:** `TBL-b657bd6a4feea7bb`
- **table_segment_uid:** `TSEG-b657bd6a4feea7bb`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/869`)
- **extraction_warnings:** ['moneda_inferida_de_simbolo_pesos', 'escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:38->38']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - No corriente / Bonificación por antigüedad - al 2025-09-30 - ARS - valor 10.154 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - No corriente / Bonificación por antigüedad - al 2024-12-31 - ARS - valor 7.593 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Remuneraciones a pagar y provisiones - al 2025-09-30 - ARS - valor 33.435 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Remuneraciones a pagar y provisiones - al 2024-12-31 - ARS - valor 52.716 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Cargas sociales a pagar - al 2025-09-30 - ARS - valor 21.759 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Cargas sociales a pagar - al 2024-12-31 - ARS - valor 22.441 - pagina 38   [confianza: media]
```

### `#/tables/49`

- **procedencia:** paginas [38]
- **table_uid:** `TBL-01bd550174b6d005`
- **table_segment_uid:** `TSEG-01bd550174b6d005`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:38->38']

**DESPUES** — hechos recuperables (7 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Impuesto diferido - al 2025-09-30 - (unidad no declarada) - valor 56.859 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Impuesto diferido - al 2024-09-30 - (unidad no declarada) - valor 141.008 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Impuesto corriente - al 2025-09-30 - (unidad no declarada) - valor (95.810) - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Diferencia entre la provisión del impuesto a las ganancias del ejercicio anterior y la declaración jurada a presentar - al 2025-09-30 - (unidad no declarada) - valor 2.913 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Diferencia entre la provisión del impuesto a las ganancias del ejercicio anterior y la declaración jurada a presentar - al 2024-09-30 - (unidad no declarada) - valor 2.912 - pagina 38   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - (Cargo) Beneficio por impuesto a las ganancias - al 2025-09-30 - (unidad no declarada) - valor (36.038) - pagina 38   [confianza: media]
```

### `#/tables/50`

- **procedencia:** paginas [39]
- **table_uid:** `TBL-371274a324c2c995`
- **table_segment_uid:** `TSEG-371274a324c2c995`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0]']

**DESPUES** — hechos recuperables (25 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Activos por impuesto diferido / Quebrantos impositivos - al 2024-12-31 - (unidad no declarada) - valor 17.928 - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Activos por impuesto diferido / Créditos por ventas y otros créditos - al 2025-09-30 - (unidad no declarada) - valor 10.418 - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Activos por impuesto diferido / Créditos por ventas y otros créditos - al 2024-12-31 - (unidad no declarada) - valor 5.624 - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Activos por impuesto diferido / Remuneraciones y cargas sociales a pagar y Planes de beneficios definidos - al 2025-09-30 - (unidad no declarada) - valor 10.042 - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Activos por impuesto diferido / Remuneraciones y cargas sociales a pagar y Planes de beneficios definidos - al 2024-12-31 - (unidad no declarada) - valor 8.408 - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Activos por impuesto diferido / Deudas fiscales - al 2025-09-30 - (unidad no declarada) - valor 424 - pagina 39   [confianza: media]
```

### `#/tables/51`

- **procedencia:** paginas [39]
- **table_uid:** `TBL-9135c55ff110c820`
- **table_segment_uid:** `TSEG-9135c55ff110c820`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:39->39']

**DESPUES** — hechos recuperables (16 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Resultado del período antes del impuesto a las ganancias - al 2025-09-30 - (unidad no declarada) - valor 215.499 - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resultado del período antes del impuesto a las ganancias - al 2024-09-30 - (unidad no declarada) - valor 207.824 - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa del impuesto vigente - al 2025-09-30 - (unidad no declarada) - valor 35% - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Tasa del impuesto vigente - al 2024-09-30 - (unidad no declarada) - valor 35% - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resultado del período a la tasa del impuesto - al 2025-09-30 - (unidad no declarada) - valor (75.425) - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Resultado del período a la tasa del impuesto - al 2024-09-30 - (unidad no declarada) - valor (72.738) - pagina 39   [confianza: media]
```

### `#/tables/52`

- **procedencia:** paginas [39]
- **table_uid:** `TBL-82535c90684b0010`
- **table_segment_uid:** `TSEG-82535c90684b0010`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:39->39']

**DESPUES** — hechos recuperables (3 en total, se muestran 3):

```text
Edenor_EEFF_Consolidado_2025_09 - Corriente / Provisión impuesto a las ganancias - al 2025-09-30 - (unidad no declarada) - valor 95.810 - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Anticipos y retenciones - al 2025-09-30 - (unidad no declarada) - valor (19.426) - pagina 39   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Corriente / Total corriente - al 2025-09-30 - (unidad no declarada) - valor 76.384 - pagina 39   [confianza: media]
```

### `#/tables/53`

- **procedencia:** paginas [39]
- **table_uid:** `TBL-3b40b5587342c079`
- **table_segment_uid:** `TSEG-3b40b5587342c079`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:39->39']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/54`

- **procedencia:** paginas [40]
- **table_uid:** `TBL-6f4eb16947bc8e9f`
- **table_segment_uid:** `TSEG-6f4eb16947bc8e9f`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:2!=3']

**DESPUES** — hechos recuperables (12 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Contribuciones y fondos nacionales, provinciales y municipales - al 2025-09-30 - (unidad no declarada) - valor 28.328 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Contribuciones y fondos nacionales, provinciales y municipales - al 2024-12-31 - (unidad no declarada) - valor 12.828 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - IVA a pagar - al 2025-09-30 - (unidad no declarada) - valor 12.013 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - IVA a pagar - al 2024-12-31 - (unidad no declarada) - valor 11.976 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Retenciones y percepciones - Fiscales - al 2025-09-30 - (unidad no declarada) - valor 17.658 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Retenciones y percepciones - Fiscales - al 2024-12-31 - (unidad no declarada) - valor 12.552 - pagina 40   [confianza: media]
```

### `#/tables/55`

- **procedencia:** paginas [40]
- **table_uid:** `TBL-640aa7744c420479`
- **table_segment_uid:** `TSEG-640aa7744c420479`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:40->40']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Saldos al inicio del ejercicio - al 2025-09-30 - (unidad no declarada) - valor 26.225 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Saldos al inicio del ejercicio - al 2024-09-30 - (unidad no declarada) - valor 26.190 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Constituciones - al 2025-09-30 - (unidad no declarada) - valor 2.286 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Constituciones - al 2024-09-30 - (unidad no declarada) - valor 9.748 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RECPAM - al 2025-09-30 - (unidad no declarada) - valor (5.386) - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RECPAM - al 2024-09-30 - (unidad no declarada) - valor (14.661) - pagina 40   [confianza: media]
```

### `#/tables/56`

- **procedencia:** paginas [40]
- **table_uid:** `TBL-bdbc629960c09441`
- **table_segment_uid:** `TSEG-bdbc629960c09441`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:40->40']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Saldos al inicio del ejercicio - al 2025-09-30 - (unidad no declarada) - valor 9.871 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Saldos al inicio del ejercicio - al 2024-09-30 - (unidad no declarada) - valor 7.620 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Constituciones - al 2025-09-30 - (unidad no declarada) - valor 18.608 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Constituciones - al 2024-09-30 - (unidad no declarada) - valor 9.979 - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Utilizaciones - al 2025-09-30 - (unidad no declarada) - valor (3.854) - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Utilizaciones - al 2024-09-30 - (unidad no declarada) - valor (4.197) - pagina 40   [confianza: media]
```

### `#/tables/57`

- **procedencia:** paginas [40]
- **table_uid:** `TBL-db7e3e171fccac50`
- **table_segment_uid:** `TSEG-db7e3e171fccac50`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:40->40']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Sociedad - EDELCOS S.A. - al 2025-09-30 - (unidad no declarada) - valor (47.691) - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Sociedad - EDELCOS S.A. - al 2024-09-30 - (unidad no declarada) - valor (36.976) - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Sociedad - SACME - al 2025-09-30 - (unidad no declarada) - valor (3.299) - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Sociedad - SACME - al 2024-09-30 - (unidad no declarada) - valor (1.456) - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Sociedad - Andina PLC - al 2024-09-30 - (unidad no declarada) - valor (270) - pagina 40   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Sociedad - Quantum Finanzas S.A. - al 2025-09-30 - (unidad no declarada) - valor (3.143) - pagina 40   [confianza: media]
```

### `#/tables/58`

- **procedencia:** paginas [41]
- **table_uid:** `TBL-3b0bfb1eccf5f3ad`
- **table_segment_uid:** `TSEG-3b0bfb1eccf5f3ad`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 1],inferido=[0]', 'unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=3']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Remuneraciones - al 2025-09-30 - (unidad no declarada) - valor 18.371 - pagina 41   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Remuneraciones - al 2024-09-30 - (unidad no declarada) - valor 13.086 - pagina 41   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - SACME - al 2025-09-30 - (unidad no declarada) - valor 526 - pagina 41   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - SACME - al 2024-09-30 - (unidad no declarada) - valor 150 - pagina 41   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Deudas comerciales / EDELCOS - al 2025-09-30 - (unidad no declarada) - valor (10.416) - pagina 41   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Deudas comerciales / EDELCOS - al 2024-09-30 - (unidad no declarada) - valor (11.710) - pagina 41   [confianza: media]
```

### `#/tables/59`

- **procedencia:** paginas [42]
- **table_uid:** `TBL-1ba3e04abfa27266`
- **table_segment_uid:** `TSEG-1ba3e04abfa27266`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/954`)
- **extraction_warnings:** ['moneda_inferida_de_simbolo_pesos', 'escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=6']

**DESPUES** — hechos recuperables (47 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Resultado operativo antes de otros ingresos y egresos operativos, participación en negocios conjuntos - al 2025-09-30 - ARS - valor 88.955 - pagina 42   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Resultado operativo antes de otros ingresos y egresos operativos, participación en negocios conjuntos - al 2024-09-30 - ARS - valor 33.644 - pagina 42   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Resultado operativo antes de otros ingresos y egresos operativos, participación en negocios conjuntos - al 2023-09-30 - ARS - valor (177.952) - pagina 42   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Resultado operativo antes de otros ingresos y egresos operativos, participación en negocios conjuntos - al 2022-09-30 - ARS - valor (170.780) - pagina 42   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Resultado operativo antes de otros ingresos y egresos operativos, participación en negocios conjuntos - al 2021-09-30 - ARS - valor (13.379) - pagina 42   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Otros ingresos operativos - al 2025-09-30 - ARS - valor 47.791 - pagina 42   [confianza: media]
```

### `#/tables/60`

- **procedencia:** paginas [42]
- **table_uid:** `TBL-ec151d2334e9182c`
- **table_segment_uid:** `TSEG-ec151d2334e9182c`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:42->42']

**DESPUES** — hechos recuperables (40 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Activo corriente - al 2025-09-30 - (unidad no declarada) - valor 1.225.108 - pagina 42   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Activo corriente - al 2024-09-30 - (unidad no declarada) - valor 1.178.518 - pagina 42   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Activo corriente - al 2023-09-30 - (unidad no declarada) - valor 739.352 - pagina 42   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Activo corriente - al 2022-09-30 - (unidad no declarada) - valor 679.343 - pagina 42   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Activo corriente - al 2021-09-30 - (unidad no declarada) - valor 732.361 - pagina 42   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Activo no corriente - al 2025-09-30 - (unidad no declarada) - valor 3.848.023 - pagina 42   [confianza: media]
```

### `#/tables/61`

- **procedencia:** paginas [43]
- **table_uid:** `TBL-33cd77475b443460`
- **table_segment_uid:** `TSEG-33cd77475b443460`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0]']

**DESPUES** — hechos recuperables (20 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Flujo neto de efectivo generado por las actividades operativas - al 2025-09-30 - (unidad no declarada) - valor 136.110 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Flujo neto de efectivo generado por las actividades operativas - al 2024-09-30 - (unidad no declarada) - valor 174.558 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Flujo neto de efectivo generado por las actividades operativas - al 2023-09-30 - (unidad no declarada) - valor 176.012 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Flujo neto de efectivo generado por las actividades operativas - al 2022-09-30 - (unidad no declarada) - valor 218.310 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Flujo neto de efectivo generado por las actividades operativas - al 2021-09-30 - (unidad no declarada) - valor 306.615 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - RUBROS - Flujo neto de efectivo utilizado en las actividades de inversión - al 2025-09-30 - (unidad no declarada) - valor (253.795) - pagina 43   [confianza: media]
```

### `#/tables/62`

- **procedencia:** paginas [43]
- **table_uid:** `TBL-d8da4ff28264c0a0`
- **table_segment_uid:** `TSEG-d8da4ff28264c0a0`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:43->43']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Ventas de energía (1) - al 2025-09-30 - (unidad no declarada) - valor 17.572 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ventas de energía (1) - al 2024-09-30 - (unidad no declarada) - valor 17.552 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ventas de energía (1) - al 2023-09-30 - (unidad no declarada) - valor 18.277 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ventas de energía (1) - al 2022-09-30 - (unidad no declarada) - valor 17.369 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Ventas de energía (1) - al 2021-09-30 - (unidad no declarada) - valor 16.469 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Compras de energía (1) - al 2025-09-30 - (unidad no declarada) - valor 20.858 - pagina 43   [confianza: media]
```

### `#/tables/63`

- **procedencia:** paginas [43]
- **table_uid:** `TBL-d2c32fdb94c24451`
- **table_segment_uid:** `TSEG-d2c32fdb94c24451`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:43->43']

**DESPUES** — hechos recuperables (20 en total, se muestran 6):

```text
Edenor_EEFF_Consolidado_2025_09 - Liquidez - al 2025-09-30 - (unidad no declarada) - valor 1,04 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Liquidez - al 2024-09-30 - (unidad no declarada) - valor 0,82 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Liquidez - al 2023-09-30 - (unidad no declarada) - valor 0,93 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Liquidez - al 2022-09-30 - (unidad no declarada) - valor 0,42 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Liquidez - al 2021-09-30 - (unidad no declarada) - valor 0,56 - pagina 43   [confianza: media]
Edenor_EEFF_Consolidado_2025_09 - Solvencia - al 2025-09-30 - (unidad no declarada) - valor 0,66 - pagina 43   [confianza: media]
```

## PDF — `Pampa_EEFF_Consolidado_1Q2026.pdf`

- identidad: `DOC-0016` / `ART-SHA256-937417C04B4E10E5C252CC4B0CD8C6036B3B6E93C5544253B4F6D481F3771FE2`
- entidad de las cifras: **no declarada**
- tablas detectadas: 105 — hechos emitidos: 1828

### `#/tables/0`

- **procedencia:** paginas [8]
- **table_uid:** `TBL-504eb92f6c1c245c`
- **table_segment_uid:** `TSEG-504eb92f6c1c245c`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/207`)
- **extraction_warnings:** —
- **reglas:** —

**DESPUES** — hechos recuperables (59 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Ingresos por ventas - (periodo no declarado) - millones de ARS - valor 8 - pagina 8   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos por ventas - al 2026-03-31 - millones de ARS - valor 807.831 - pagina 8   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos por ventas - al 2025-03-31 - millones de ARS - valor 438.715 - pagina 8   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Costo de ventas - (periodo no declarado) - millones de ARS - valor 9 - pagina 8   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Costo de ventas - al 2026-03-31 - millones de ARS - valor (548.251) - pagina 8   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Costo de ventas - al 2025-03-31 - millones de ARS - valor (301.010) - pagina 8   [confianza: media]
```

### `#/tables/1`

- **procedencia:** paginas [8]
- **table_uid:** `TBL-0e0d761002c689dc`
- **table_segment_uid:** `TSEG-0e0d761002c689dc`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:8->8']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/2`

- **procedencia:** paginas [9]
- **table_uid:** `TBL-e5ae2483718cfab4`
- **table_segment_uid:** `TSEG-e5ae2483718cfab4`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/211`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (15 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: / Propietarios de la Sociedad - al 2026-03-31 - millones de ARS - valor 293.366 - pagina 9   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: / Propietarios de la Sociedad - al 2025-03-31 - millones de ARS - valor 161.886 - pagina 9   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: / Participación no controladora - al 2026-03-31 - millones de ARS - valor 3.301 - pagina 9   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: / Participación no controladora - al 2025-03-31 - millones de ARS - valor 832 - pagina 9   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: /  - al 2026-03-31 - millones de ARS - valor 296.667 - pagina 9   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: /  - al 2025-03-31 - millones de ARS - valor 162.718 - pagina 9   [confianza: media]
```

### `#/tables/3`

- **procedencia:** paginas [9]
- **table_uid:** `TBL-d07e2c7418845347`
- **table_segment_uid:** `TSEG-d07e2c7418845347`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:9->9']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/4`

- **procedencia:** paginas [10]
- **table_uid:** `TBL-59f151fffe4226be`
- **table_segment_uid:** `TSEG-59f151fffe4226be`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/215`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (40 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Propiedades, planta y equipo - (periodo no declarado) - millones de ARS - valor 11.1 - pagina 10   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Propiedades, planta y equipo - al 2026-03-31 - millones de ARS - valor 4.675.860 - pagina 10   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Propiedades, planta y equipo - al 2025-12-31 - millones de ARS - valor 4.805.587 - pagina 10   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Activos intangibles - (periodo no declarado) - millones de ARS - valor 11.2 - pagina 10   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Activos intangibles - al 2026-03-31 - millones de ARS - valor 122.835 - pagina 10   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Activos intangibles - al 2025-12-31 - millones de ARS - valor 130.376 - pagina 10   [confianza: media]
```

### `#/tables/5`

- **procedencia:** paginas [10]
- **table_uid:** `TBL-a50e235a9085dcdf`
- **table_segment_uid:** `TSEG-a50e235a9085dcdf`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:10->10']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/6`

- **procedencia:** paginas [11]
- **table_uid:** `TBL-c399843b9d9a96ec`
- **table_segment_uid:** `TSEG-c399843b9d9a96ec`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/219`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (78 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - PATRIMONIO / Capital social - (periodo no declarado) - millones de ARS - valor 13.1 - pagina 11   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - PATRIMONIO / Capital social - al 2026-03-31 - millones de ARS - valor 1.360 - pagina 11   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - PATRIMONIO / Capital social - al 2025-12-31 - millones de ARS - valor 1.360 - pagina 11   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - PATRIMONIO / Ajuste de capital - al 2026-03-31 - millones de ARS - valor 7.127 - pagina 11   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - PATRIMONIO / Ajuste de capital - al 2025-12-31 - millones de ARS - valor 7.126 - pagina 11   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - PATRIMONIO / Prima de emisión - al 2026-03-31 - millones de ARS - valor 21.217 - pagina 11   [confianza: media]
```

### `#/tables/7`

- **procedencia:** paginas [11]
- **table_uid:** `TBL-ef0cada1a2575f55`
- **table_segment_uid:** `TSEG-ef0cada1a2575f55`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:11->11']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/8`

- **procedencia:** paginas [12]
- **table_uid:** `TBL-c05c15b5456fd193`
- **table_segment_uid:** `TSEG-c05c15b5456fd193`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/223`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=15']

**DESPUES** — hechos recuperables (109 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31 de diciembre de 2024 - (periodo no declarado) - millones de ARS - valor 1.360 - pagina 12   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31 de diciembre de 2024 - (periodo no declarado) - millones de ARS - valor 7.126 - pagina 12   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31 de diciembre de 2024 - (periodo no declarado) - millones de ARS - valor 19.950 - pagina 12   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31 de diciembre de 2024 - (periodo no declarado) - millones de ARS - valor 4 - pagina 12   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31 de diciembre de 2024 - (periodo no declarado) - millones de ARS - valor 21 - pagina 12   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31 de diciembre de 2024 - (periodo no declarado) - millones de ARS - valor (211) - pagina 12   [confianza: media]
```

### `#/tables/9`

- **procedencia:** paginas [12]
- **table_uid:** `TBL-022f0b3e331eca70`
- **table_segment_uid:** `TSEG-022f0b3e331eca70`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:12->12']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/10`

- **procedencia:** paginas [13]
- **table_uid:** `TBL-a89c24aa53852d72`
- **table_segment_uid:** `TSEG-a89c24aa53852d72`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/227`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (49 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Flujos de efectivo de las actividades operativas: / Ganancia del período - al 2026-03-31 - millones de ARS - valor 296.667 - pagina 13   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Flujos de efectivo de las actividades operativas: / Ganancia del período - al 2025-03-31 - millones de ARS - valor 162.718 - pagina 13   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Flujos de efectivo de las actividades operativas: / Ajustes para arribar a los flujos netos de efectivo de las actividades operativas - (periodo no declarado) - millones de ARS - valor 14.1 - pagina 13   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Flujos de efectivo de las actividades operativas: / Ajustes para arribar a los flujos netos de efectivo de las actividades operativas - al 2026-03-31 - millones de ARS - valor 46.668 - pagina 13   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Flujos de efectivo de las actividades operativas: / Ajustes para arribar a los flujos netos de efectivo de las actividades operativas - al 2025-03-31 - millones de ARS - valor 8.017 - pagina 13   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Flujos de efectivo de las actividades operativas: / Cambios en activos y pasivos operativos - (periodo no declarado) - millones de ARS - valor 14.2 - pagina 13   [confianza: media]
```

### `#/tables/11`

- **procedencia:** paginas [13]
- **table_uid:** `TBL-7065935e27ef6f19`
- **table_segment_uid:** `TSEG-7065935e27ef6f19`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:13->13']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/12`

- **procedencia:** paginas [16]
- **table_uid:** `TBL-6ff6b728ce66c87b`
- **table_segment_uid:** `TSEG-6ff6b728ce66c87b`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:13->16']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/13`

- **procedencia:** paginas [21]
- **table_uid:** `TBL-ddea93d21bdedc65`
- **table_segment_uid:** `TSEG-ddea93d21bdedc65`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/372`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:16->21']

**DESPUES** — hechos recuperables (38 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Sociedad - Recursos Energéticos S.A.U. - al 2026-03-31 - porcentaje - valor 100,00% - pagina 21   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Sociedad - Recursos Energéticos S.A.U. - al 2025-12-31 - porcentaje - valor 100,00% - pagina 21   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Sociedad - EISA - al 2026-03-31 - porcentaje - valor 100,00% - pagina 21   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Sociedad - EISA - al 2025-12-31 - porcentaje - valor 100,00% - pagina 21   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Sociedad - Enecor S.A. - al 2026-03-31 - porcentaje - valor 70,00% - pagina 21   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Sociedad - Enecor S.A. - al 2025-12-31 - porcentaje - valor 70,00% - pagina 21   [confianza: media]
```

### `#/tables/14`

- **procedencia:** paginas [22]
- **table_uid:** `TBL-8f80e3d439af18f6`
- **table_segment_uid:** `TSEG-8f80e3d439af18f6`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:5!=7']

**DESPUES** — hechos recuperables (20 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / SESA - (periodo no declarado) - (unidad no declarada) - valor 1.203 - pagina 22   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / SESA - (periodo no declarado) - (unidad no declarada) - valor 889 - pagina 22   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / SESA - (periodo no declarado) - (unidad no declarada) - valor 132.254 - pagina 22   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / SESA - (periodo no declarado) - porcentaje - valor 20,00% - pagina 22   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / VMOS - (periodo no declarado) - (unidad no declarada) - valor 159.133 - pagina 22   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / VMOS - (periodo no declarado) - (unidad no declarada) - valor (50.292) - pagina 22   [confianza: media]
```

### `#/tables/15`

- **procedencia:** paginas [22]
- **table_uid:** `TBL-0ef727804ec4e156`
- **table_segment_uid:** `TSEG-0ef727804ec4e156`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/390`)
- **extraction_warnings:** ['moneda_inferida_de_simbolo_pesos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:22->22']

**DESPUES** — hechos recuperables (16 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / SESA - al 2026-03-31 - millones de ARS - valor 26.451 - pagina 22   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / SESA - al 2025-12-31 - millones de ARS - valor 17.315 - pagina 22   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / VMOS - al 2026-03-31 - millones de ARS - valor 60.135 - pagina 22   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / VMOS - al 2025-12-31 - millones de ARS - valor 44.672 - pagina 22   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / Total asociadas - al 2026-03-31 - millones de ARS - valor 86.586 - pagina 22   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / Total asociadas - al 2025-12-31 - millones de ARS - valor 61.987 - pagina 22   [confianza: media]
```

### `#/tables/16`

- **procedencia:** paginas [22]
- **table_uid:** `TBL-298a08546dd25339`
- **table_segment_uid:** `TSEG-298a08546dd25339`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:22->22']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/17`

- **procedencia:** paginas [23]
- **table_uid:** `TBL-1aa4bc281fcff400`
- **table_segment_uid:** `TSEG-1aa4bc281fcff400`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/394`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (13 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / SESA - al 2026-03-31 - millones de ARS - valor 3.854 - pagina 23   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / VMOS - al 2026-03-31 - millones de ARS - valor 1.194 - pagina 23   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Asociadas / Total asociadas - al 2026-03-31 - millones de ARS - valor 5.048 - pagina 23   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Negocios conjuntos / CIESA - al 2026-03-31 - millones de ARS - valor 42.840 - pagina 23   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Negocios conjuntos / CIESA - al 2025-03-31 - millones de ARS - valor 26.702 - pagina 23   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Negocios conjuntos / Citelec - al 2026-03-31 - millones de ARS - valor 16.035 - pagina 23   [confianza: media]
```

### `#/tables/18`

- **procedencia:** paginas [23]
- **table_uid:** `TBL-60ec810640c6f588`
- **table_segment_uid:** `TSEG-60ec810640c6f588`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:23->23']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2026-03-31 - (unidad no declarada) - valor 1.541.388 - pagina 23   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2025-03-31 - (unidad no declarada) - valor 1.024.769 - pagina 23   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aporte de capital - al 2026-03-31 - (unidad no declarada) - valor 23.277 - pagina 23   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aporte de capital - al 2025-03-31 - (unidad no declarada) - valor 33.327 - pagina 23   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Participación en resultado - al 2026-03-31 - (unidad no declarada) - valor 93.833 - pagina 23   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Participación en resultado - al 2025-03-31 - (unidad no declarada) - valor 48.144 - pagina 23   [confianza: media]
```

### `#/tables/19`

- **procedencia:** paginas [23]
- **table_uid:** `TBL-490c69e3b711e503`
- **table_segment_uid:** `TSEG-490c69e3b711e503`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:23->23']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/20`

- **procedencia:** paginas [24]
- **table_uid:** `TBL-53e90a94f6de2924`
- **table_segment_uid:** `TSEG-53e90a94f6de2924`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones (origen `texto_adyacente`, evidencia `#/texts/414`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (14 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Activo no corriente - al 2026-03-31 - millones - valor 186.504 - pagina 24   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Activo no corriente - al 2025-12-31 - millones - valor 176.789 - pagina 24   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Activo corriente - al 2026-03-31 - millones - valor 11.724 - pagina 24   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Activo corriente - al 2025-12-31 - millones - valor 11.724 - pagina 24   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Total del activo - al 2026-03-31 - millones - valor 198.228 - pagina 24   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Total del activo - al 2025-12-31 - millones - valor 188.513 - pagina 24   [confianza: media]
```

### `#/tables/21`

- **procedencia:** paginas [24]
- **table_uid:** `TBL-719402f6941fd766`
- **table_segment_uid:** `TSEG-719402f6941fd766`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:24->24']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/22`

- **procedencia:** paginas [25]
- **table_uid:** `TBL-4aeccd3ef26bcedd`
- **table_segment_uid:** `TSEG-4aeccd3ef26bcedd`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/23`

- **procedencia:** paginas [26]
- **table_uid:** `TBL-e256772fcce99fb1`
- **table_segment_uid:** `TSEG-e256772fcce99fb1`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de USD (origen `celda_encabezado`, evidencia `r0c1`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 1, 29],inferido=[0, 1]']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=8']

**DESPUES** — hechos recuperables (106 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2026 / Ingresos por ventas - mercado local - (periodo no declarado) - millones de USD - valor 111 - pagina 26   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2026 / Ingresos por ventas - mercado local - (periodo no declarado) - millones de USD - valor 279 - pagina 26   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2026 / Ingresos por ventas - mercado local - (periodo no declarado) - millones de USD - valor 53 - pagina 26   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2026 / Ingresos por ventas - mercado local - (periodo no declarado) - millones de USD - valor 8 - pagina 26   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2026 / Ingresos por ventas - mercado local - (periodo no declarado) - millones de USD - valor 451 - pagina 26   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2026 / Ingresos por ventas - mercado local - (periodo no declarado) - millones de ARS - valor 634.638 - pagina 26   [confianza: media]
```

### `#/tables/24`

- **procedencia:** paginas [27]
- **table_uid:** `TBL-c8ecca1c8245a0e3`
- **table_segment_uid:** `TSEG-c8ecca1c8245a0e3`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de USD (origen `celda_encabezado`, evidencia `r0c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0, 1]']

**DESPUES** — hechos recuperables (33 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de USD - valor 105 - pagina 27   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de USD - valor 88 - pagina 27   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de USD - valor (8) - pagina 27   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de USD - valor 29 - pagina 27   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de USD - valor 214 - pagina 27   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de ARS - valor 293.366 - pagina 27   [confianza: media]
```

### `#/tables/25`

- **procedencia:** paginas [27]
- **table_uid:** `TBL-b13a9f36598e0fb8`
- **table_segment_uid:** `TSEG-b13a9f36598e0fb8`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:27->27']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/26`

- **procedencia:** paginas [28]
- **table_uid:** `TBL-d5862928255661f9`
- **table_segment_uid:** `TSEG-d5862928255661f9`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de USD (origen `celda_encabezado`, evidencia `r0c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=8']

**DESPUES** — hechos recuperables (105 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Ingresos por ventas - mercado local - (periodo no declarado) - millones de USD - valor 94 - pagina 28   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos por ventas - mercado local - (periodo no declarado) - millones de USD - valor 194 - pagina 28   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos por ventas - mercado local - (periodo no declarado) - millones de USD - valor 57 - pagina 28   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos por ventas - mercado local - (periodo no declarado) - millones de USD - valor 7 - pagina 28   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos por ventas - mercado local - (periodo no declarado) - millones de USD - valor 352 - pagina 28   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos por ventas - mercado local - (periodo no declarado) - millones de ARS - valor 372.894 - pagina 28   [confianza: media]
```

### `#/tables/27`

- **procedencia:** paginas [28]
- **table_uid:** `TBL-74f8fc2b6ccdc35c`
- **table_segment_uid:** `TSEG-74f8fc2b6ccdc35c`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:28->28']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/28`

- **procedencia:** paginas [29]
- **table_uid:** `TBL-7f0ccfe82a1d3ce0`
- **table_segment_uid:** `TSEG-7f0ccfe82a1d3ce0`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de USD (origen `celda_encabezado`, evidencia `r0c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=8']

**DESPUES** — hechos recuperables (34 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2025 - Ganancia (Pérdida) del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de USD - valor (49) - pagina 29   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2025 - Ganancia (Pérdida) del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de USD - valor 124 - pagina 29   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2025 - Ganancia (Pérdida) del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de USD - valor 42 - pagina 29   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2025 - Ganancia (Pérdida) del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de USD - valor 36 - pagina 29   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2025 - Ganancia (Pérdida) del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de USD - valor 153 - pagina 29   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - finalizado el 31.03.2025 - Ganancia (Pérdida) del período atribuible a: / Propietarios de la Sociedad - (periodo no declarado) - millones de ARS - valor 161.886 - pagina 29   [confianza: media]
```

### `#/tables/29`

- **procedencia:** paginas [29]
- **table_uid:** `TBL-feeb607f843bc9a7`
- **table_segment_uid:** `TSEG-feeb607f843bc9a7`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:29->29']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/30`

- **procedencia:** paginas [30]
- **table_uid:** `TBL-2673aab99bd95f68`
- **table_segment_uid:** `TSEG-2673aab99bd95f68`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/461`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (38 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Ventas de gas - al 2026-03-31 - millones de ARS - valor 124.548 - pagina 30   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ventas de gas - al 2025-03-31 - millones de ARS - valor 100.130 - pagina 30   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ventas de petróleo - al 2026-03-31 - millones de ARS - valor 150.656 - pagina 30   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ventas de petróleo - al 2025-03-31 - millones de ARS - valor 23.796 - pagina 30   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Otras ventas - al 2026-03-31 - millones de ARS - valor 3.217 - pagina 30   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Otras ventas - al 2025-03-31 - millones de ARS - valor 3.615 - pagina 30   [confianza: media]
```

### `#/tables/31`

- **procedencia:** paginas [30]
- **table_uid:** `TBL-56ec98674e56f454`
- **table_segment_uid:** `TSEG-56ec98674e56f454`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:30->30']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/32`

- **procedencia:** paginas [31]
- **table_uid:** `TBL-aa12735a3e82152f`
- **table_segment_uid:** `TSEG-aa12735a3e82152f`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/468`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (48 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Inventarios al inicio del ejercicio - al 2026-03-31 - millones de ARS - valor 335.514 - pagina 31   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Inventarios al inicio del ejercicio - al 2025-03-31 - millones de ARS - valor 230.095 - pagina 31   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Más: Cargos del período / Compras de inventarios, energía y gas - al 2026-03-31 - millones de ARS - valor 169.378 - pagina 31   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Más: Cargos del período / Compras de inventarios, energía y gas - al 2025-03-31 - millones de ARS - valor 102.918 - pagina 31   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Más: Cargos del período / Remuneraciones y cargas sociales - al 2026-03-31 - millones de ARS - valor 30.015 - pagina 31   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Más: Cargos del período / Remuneraciones y cargas sociales - al 2025-03-31 - millones de ARS - valor 24.665 - pagina 31   [confianza: media]
```

### `#/tables/33`

- **procedencia:** paginas [31]
- **table_uid:** `TBL-74bff7592b4cd1d5`
- **table_segment_uid:** `TSEG-74bff7592b4cd1d5`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:31->31']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/34`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-bc3f3126e4f2dbad`
- **table_segment_uid:** `TSEG-bc3f3126e4f2dbad`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/472`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (15 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Remuneraciones y cargas sociales - al 2026-03-31 - millones de ARS - valor 1.809 - pagina 32   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Remuneraciones y cargas sociales - al 2025-03-31 - millones de ARS - valor 1.540 - pagina 32   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Beneficios al personal - al 2026-03-31 - millones de ARS - valor 60 - pagina 32   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Beneficios al personal - al 2025-03-31 - millones de ARS - valor 40 - pagina 32   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Honorarios y retribuciones por servicios - al 2026-03-31 - millones de ARS - valor 1.164 - pagina 32   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Honorarios y retribuciones por servicios - al 2025-03-31 - millones de ARS - valor 513 - pagina 32   [confianza: media]
```

### `#/tables/35`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-809a3a5809a8946f`
- **table_segment_uid:** `TSEG-809a3a5809a8946f`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 18, 19],inferido=[0]', 'unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:32->32']

**DESPUES** — hechos recuperables (35 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Remuneraciones y cargas sociales - al 2026-03-31 - (unidad no declarada) - valor 24.804 - pagina 32   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Remuneraciones y cargas sociales - al 2025-03-31 - (unidad no declarada) - valor 18.814 - pagina 32   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Beneficios al personal - al 2026-03-31 - (unidad no declarada) - valor 1.504 - pagina 32   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Beneficios al personal - al 2025-03-31 - (unidad no declarada) - valor 1.636 - pagina 32   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Planes de beneficios definidos - al 2026-03-31 - (unidad no declarada) - valor 1.903 - pagina 32   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Planes de beneficios definidos - al 2025-03-31 - (unidad no declarada) - valor 2.374 - pagina 32   [confianza: media]
```

### `#/tables/36`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-4333c07e12583939`
- **table_segment_uid:** `TSEG-4333c07e12583939`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:32->32']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/37`

- **procedencia:** paginas [33]
- **table_uid:** `TBL-c642a9b1bc1a8339`
- **table_segment_uid:** `TSEG-c642a9b1bc1a8339`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (30 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Otros ingresos operativos / Recupero de seguros - al 2026-03-31 - (unidad no declarada) - valor 2.662 - pagina 33   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Otros ingresos operativos / Recupero de seguros - al 2025-03-31 - (unidad no declarada) - valor 9.260 - pagina 33   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Otros ingresos operativos / Resultado por venta de propiedades, planta y equipo - al 2026-03-31 - (unidad no declarada) - valor 406 - pagina 33   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Otros ingresos operativos / Recupero provisión para contingencias - al 2026-03-31 - (unidad no declarada) - valor 145 - pagina 33   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Otros ingresos operativos / Recupero provisión para contingencias - al 2025-03-31 - (unidad no declarada) - valor 18.292 - pagina 33   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Otros ingresos operativos / Dividendos ganados - al 2026-03-31 - (unidad no declarada) - valor 3.424 - pagina 33   [confianza: media]
```

### `#/tables/38`

- **procedencia:** paginas [33]
- **table_uid:** `TBL-a2477f14a0a96810`
- **table_segment_uid:** `TSEG-a2477f14a0a96810`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:33->33']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/39`

- **procedencia:** paginas [34]
- **table_uid:** `TBL-4b222398cd4d0403`
- **table_segment_uid:** `TSEG-4b222398cd4d0403`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/481`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (32 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Ingresos financieros / Intereses financieros - al 2026-03-31 - millones de ARS - valor 4.944 - pagina 34   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos financieros / Intereses financieros - al 2025-03-31 - millones de ARS - valor 35.269 - pagina 34   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos financieros / Otros intereses - al 2026-03-31 - millones de ARS - valor 104 - pagina 34   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos financieros / Otros intereses - al 2025-03-31 - millones de ARS - valor 225 - pagina 34   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos financieros / Total ingresos financieros - al 2026-03-31 - millones de ARS - valor 5.048 - pagina 34   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ingresos financieros / Total ingresos financieros - al 2025-03-31 - millones de ARS - valor 35.494 - pagina 34   [confianza: media]
```

### `#/tables/40`

- **procedencia:** paginas [34]
- **table_uid:** `TBL-8612166eebbf8224`
- **table_segment_uid:** `TSEG-8612166eebbf8224`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:34->34']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/41`

- **procedencia:** paginas [35]
- **table_uid:** `TBL-63c63b4452e6cbcb`
- **table_segment_uid:** `TSEG-63c63b4452e6cbcb`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/491`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (7 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Impuesto corriente - al 2026-03-31 - millones de ARS - valor 156.666 - pagina 35   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Impuesto corriente - al 2025-03-31 - millones de ARS - valor 55.387 - pagina 35   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Impuesto diferido - al 2026-03-31 - millones de ARS - valor (254.303) - pagina 35   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Impuesto diferido - al 2025-03-31 - millones de ARS - valor (58.464) - pagina 35   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Diferencia entre la provisión de impuesto a las ganancias del ejercicio anterior y la declaración jurada - al 2025-03-31 - millones de ARS - valor 48 - pagina 35   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Total cargo por impuesto a las ganancias - Ganancia - al 2026-03-31 - millones de ARS - valor (97.637) - pagina 35   [confianza: media]
```

### `#/tables/42`

- **procedencia:** paginas [35]
- **table_uid:** `TBL-459aa9702ba8cb5d`
- **table_segment_uid:** `TSEG-459aa9702ba8cb5d`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:35->35']

**DESPUES** — hechos recuperables (24 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Resultado del período antes del impuesto a las ganancias - al 2026-03-31 - (unidad no declarada) - valor 199.030 - pagina 35   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Resultado del período antes del impuesto a las ganancias - al 2025-03-31 - (unidad no declarada) - valor 159.689 - pagina 35   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Tasa del impuesto vigente - al 2026-03-31 - (unidad no declarada) - valor 35% - pagina 35   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Tasa del impuesto vigente - al 2025-03-31 - (unidad no declarada) - valor 35% - pagina 35   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Resultado del período a la tasa del impuesto - al 2026-03-31 - (unidad no declarada) - valor 69.661 - pagina 35   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Resultado del período a la tasa del impuesto - al 2025-03-31 - (unidad no declarada) - valor 55.891 - pagina 35   [confianza: media]
```

### `#/tables/43`

- **procedencia:** paginas [35]
- **table_uid:** `TBL-0fe53fa26956b0e1`
- **table_segment_uid:** `TSEG-0fe53fa26956b0e1`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:35->35']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/44`

- **procedencia:** paginas [36]
- **table_uid:** `TBL-2668bc3606ae85cd`
- **table_segment_uid:** `TSEG-2668bc3606ae85cd`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/498`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=7']

**DESPUES** — hechos recuperables (51 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Terrenos - (periodo no declarado) - millones de ARS - valor 15.313 - pagina 36   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Terrenos - (periodo no declarado) - millones de ARS - valor (768) - pagina 36   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Terrenos - Valores de incorporación / Al cierre - millones de ARS - valor 14.545 - pagina 36   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Edificios - (periodo no declarado) - millones de ARS - valor 258.531 - pagina 36   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Edificios - (periodo no declarado) - millones de ARS - valor 346 - pagina 36   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Edificios - (periodo no declarado) - millones de ARS - valor (12.959) - pagina 36   [confianza: media]
```

### `#/tables/45`

- **procedencia:** paginas [36]
- **table_uid:** `TBL-8386a3ab0bb0e1a6`
- **table_segment_uid:** `TSEG-8386a3ab0bb0e1a6`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:36->36']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/46`

- **procedencia:** paginas [37]
- **table_uid:** `TBL-c9d161a300fd24d6`
- **table_segment_uid:** `TSEG-c9d161a300fd24d6`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=8']

**DESPUES** — hechos recuperables (61 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Terrenos - Valores residuales / Al cierre - (unidad no declarada) - valor 14.545 - pagina 37   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Terrenos - saldo al 2025-12-31 - (unidad no declarada) - valor 15.313 - pagina 37   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Edificios - (periodo no declarado) - (unidad no declarada) - valor (113.562) - pagina 37   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Edificios - (periodo no declarado) - (unidad no declarada) - valor (2.559) - pagina 37   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Edificios - (periodo no declarado) - (unidad no declarada) - valor 5.746 - pagina 37   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Edificios - Depreciaciones / Al cierre - (unidad no declarada) - valor (110.375) - pagina 37   [confianza: media]
```

### `#/tables/47`

- **procedencia:** paginas [37]
- **table_uid:** `TBL-5a9a92b59c8be941`
- **table_segment_uid:** `TSEG-5a9a92b59c8be941`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:37->37']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/48`

- **procedencia:** paginas [38]
- **table_uid:** `TBL-182250a478d81254`
- **table_segment_uid:** `TSEG-182250a478d81254`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/506`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=6']

**DESPUES** — hechos recuperables (24 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Acuerdos de concesión - (periodo no declarado) - millones de ARS - valor 2.692 - pagina 38   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Acuerdos de concesión - (periodo no declarado) - millones de ARS - valor (135) - pagina 38   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Acuerdos de concesión - Valores de incorporación / Al cierre - millones de ARS - valor 2.557 - pagina 38   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Llaves de negocio - (periodo no declarado) - millones de ARS - valor 50.354 - pagina 38   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Llaves de negocio - (periodo no declarado) - millones de ARS - valor (2.526) - pagina 38   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Llaves de negocio - Valores de incorporación / Al cierre - millones de ARS - valor 47.828 - pagina 38   [confianza: media]
```

### `#/tables/49`

- **procedencia:** paginas [38]
- **table_uid:** `TBL-5dd3acac2af50d45`
- **table_segment_uid:** `TSEG-5dd3acac2af50d45`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:38->38']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/50`

- **procedencia:** paginas [39]
- **table_uid:** `TBL-9e48d13f666aa2ac`
- **table_segment_uid:** `TSEG-9e48d13f666aa2ac`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/559`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (26 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Quebrantos impositivos - al 2026-03-31 - millones de ARS - valor 11.644 - pagina 39   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Quebrantos impositivos - al 2025-12-31 - millones de ARS - valor 1.958 - pagina 39   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Propiedades, planta y equipo, derechos de uso, activos intangibles e inventarios - al 2026-03-31 - millones de ARS - valor 267.620 - pagina 39   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Propiedades, planta y equipo, derechos de uso, activos intangibles e inventarios - al 2025-12-31 - millones de ARS - valor 138.377 - pagina 39   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Instrumentos financieros derivados - al 2026-03-31 - millones de ARS - valor 89.499 - pagina 39   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Créditos por ventas y otros créditos - al 2026-03-31 - millones de ARS - valor 276 - pagina 39   [confianza: media]
```

### `#/tables/51`

- **procedencia:** paginas [39]
- **table_uid:** `TBL-4a0cc92201136f12`
- **table_segment_uid:** `TSEG-4a0cc92201136f12`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:39->39']

**DESPUES** — hechos recuperables (4 en total, se muestran 4):

```text
Pampa_EEFF_Consolidado_1Q2026 - Activo por impuesto diferido, neto - al 2026-03-31 - (unidad no declarada) - valor 404.919 - pagina 39   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Activo por impuesto diferido, neto - al 2025-12-31 - (unidad no declarada) - valor 62.442 - pagina 39   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Pasivo por impuesto diferido, neto - al 2026-03-31 - (unidad no declarada) - valor (63.246) - pagina 39   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Pasivo por impuesto diferido, neto - al 2025-12-31 - (unidad no declarada) - valor (81.493) - pagina 39   [confianza: media]
```

### `#/tables/52`

- **procedencia:** paginas [39]
- **table_uid:** `TBL-d69d2b93275b50a8`
- **table_segment_uid:** `TSEG-d69d2b93275b50a8`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:39->39']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/53`

- **procedencia:** paginas [40]
- **table_uid:** `TBL-7cb9b9f2371e30b0`
- **table_segment_uid:** `TSEG-7cb9b9f2371e30b0`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Materiales y repuestos - al 2026-03-31 - (unidad no declarada) - valor 225.121 - pagina 40   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Materiales y repuestos - al 2025-12-31 - (unidad no declarada) - valor 229.357 - pagina 40   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Anticipo a proveedores - al 2026-03-31 - (unidad no declarada) - valor 16.874 - pagina 40   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Anticipo a proveedores - al 2025-12-31 - (unidad no declarada) - valor 13.326 - pagina 40   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Productos en proceso y terminados - al 2026-03-31 - (unidad no declarada) - valor 86.408 - pagina 40   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Productos en proceso y terminados - al 2025-12-31 - (unidad no declarada) - valor 92.831 - pagina 40   [confianza: media]
```

### `#/tables/54`

- **procedencia:** paginas [40]
- **table_uid:** `TBL-6607520ce2c4105d`
- **table_segment_uid:** `TSEG-6607520ce2c4105d`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de USD (origen `texto_adyacente`, evidencia `#/texts/567`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:40->40']

**DESPUES** — hechos recuperables (17 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Contingencias - al 2026-03-31 - millones de USD - valor 35.799 - pagina 40   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Contingencias - al 2025-12-31 - millones de USD - valor 77.937 - pagina 40   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Abandono de pozos y desmantelamiento de aerogeneradores - al 2026-03-31 - millones de USD - valor 40.390 - pagina 40   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Abandono de pozos y desmantelamiento de aerogeneradores - al 2025-12-31 - millones de USD - valor 41.624 - pagina 40   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Remediación ambiental - al 2026-03-31 - millones de USD - valor 24.685 - pagina 40   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Remediación ambiental - al 2025-12-31 - millones de USD - valor 25.990 - pagina 40   [confianza: media]
```

### `#/tables/55`

- **procedencia:** paginas [40]
- **table_uid:** `TBL-7a737eedb6f65e90`
- **table_segment_uid:** `TSEG-7a737eedb6f65e90`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:40->40']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/56`

- **procedencia:** paginas [41]
- **table_uid:** `TBL-c6460df59e3c9a50`
- **table_segment_uid:** `TSEG-c6460df59e3c9a50`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/574`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 1, 8, 9],inferido=[0, 1]']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (34 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2026-03-31 - millones de ARS - valor 77.937 - pagina 41   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2026-03-31 - millones de ARS - valor 48.501 - pagina 41   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2026-03-31 - millones de ARS - valor 31.309 - pagina 41   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento - al 2026-03-31 - millones de ARS - valor 5.550 - pagina 41   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento - al 2026-03-31 - millones de ARS - valor 875 - pagina 41   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento - al 2026-03-31 - millones de ARS - valor 129 - pagina 41   [confianza: media]
```

### `#/tables/57`

- **procedencia:** paginas [41]
- **table_uid:** `TBL-702a4acc73948b76`
- **table_segment_uid:** `TSEG-702a4acc73948b76`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:41->41']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/58`

- **procedencia:** paginas [42]
- **table_uid:** `TBL-d3792f0ce0ccb6d7`
- **table_segment_uid:** `TSEG-d3792f0ce0ccb6d7`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[1],inferido=[0, 1]', 'unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (28 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - 11.6 Pasivo por impuesto a las ganancias e impuesto a la ganancia mínima presunta - No corriente / Impuesto a las ganancias - al 2026-03-31 - (unidad no declarada) - valor 33.737 - pagina 42   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - 11.6 Pasivo por impuesto a las ganancias e impuesto a la ganancia mínima presunta - No corriente / Impuesto a las ganancias - al 2025-12-31 - (unidad no declarada) - valor 32.508 - pagina 42   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - 11.6 Pasivo por impuesto a las ganancias e impuesto a la ganancia mínima presunta - No corriente / Impuesto a la ganancia mínima presunta - al 2026-03-31 - (unidad no declarada) - valor 2.402 - pagina 42   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - 11.6 Pasivo por impuesto a las ganancias e impuesto a la ganancia mínima presunta - No corriente / Impuesto a la ganancia mínima presunta - al 2025-12-31 - (unidad no declarada) - valor 6.026 - pagina 42   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - 11.6 Pasivo por impuesto a las ganancias e impuesto a la ganancia mínima presunta - No corriente / Total no corriente - al 2026-03-31 - (unidad no declarada) - valor 36.139 - pagina 42   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - 11.6 Pasivo por impuesto a las ganancias e impuesto a la ganancia mínima presunta - No corriente / Total no corriente - al 2025-12-31 - (unidad no declarada) - valor 38.534 - pagina 42   [confianza: media]
```

### `#/tables/59`

- **procedencia:** paginas [42]
- **table_uid:** `TBL-7ff2d47751b654b9`
- **table_segment_uid:** `TSEG-7ff2d47751b654b9`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:42->42']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/60`

- **procedencia:** paginas [43]
- **table_uid:** `TBL-a671d6e8a368d9eb`
- **table_segment_uid:** `TSEG-a671d6e8a368d9eb`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/586`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (31 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Acciones - al 2026-03-31 - millones de ARS - valor 45.853 - pagina 43   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Acciones - al 2025-12-31 - millones de ARS - valor 48.275 - pagina 43   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Total no corriente - al 2026-03-31 - millones de ARS - valor 45.853 - pagina 43   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Total no corriente - al 2025-12-31 - millones de ARS - valor 48.275 - pagina 43   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Títulos de deuda pública - al 2026-03-31 - millones de ARS - valor 545.112 - pagina 43   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Títulos de deuda pública - al 2025-12-31 - millones de ARS - valor 448.832 - pagina 43   [confianza: media]
```

### `#/tables/61`

- **procedencia:** paginas [43]
- **table_uid:** `TBL-ec1343b356436bbe`
- **table_segment_uid:** `TSEG-ec1343b356436bbe`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:43->43']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/62`

- **procedencia:** paginas [44]
- **table_uid:** `TBL-b54d51de6345c94b`
- **table_segment_uid:** `TSEG-b54d51de6345c94b`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (43 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Deudores comunes - al 2026-03-31 - (unidad no declarada) - valor 332.809 - pagina 44   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Deudores comunes - al 2025-12-31 - (unidad no declarada) - valor 361.965 - pagina 44   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / CAMMESA - al 2026-03-31 - (unidad no declarada) - valor 229.104 - pagina 44   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / CAMMESA - al 2025-12-31 - (unidad no declarada) - valor 171.648 - pagina 44   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Saldos con partes relacionadas - (periodo no declarado) - (unidad no declarada) - valor 16 - pagina 44   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Corriente / Saldos con partes relacionadas - al 2026-03-31 - (unidad no declarada) - valor 11.871 - pagina 44   [confianza: media]
```

### `#/tables/63`

- **procedencia:** paginas [44]
- **table_uid:** `TBL-ab4afbf9c123915c`
- **table_segment_uid:** `TSEG-ab4afbf9c123915c`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:44->44']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/64`

- **procedencia:** paginas [45]
- **table_uid:** `TBL-d492e6892b255033`
- **table_segment_uid:** `TSEG-d492e6892b255033`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/598`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2026-03-31 - millones de ARS - valor 29.085 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2025-03-31 - millones de ARS - valor 833 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento - al 2026-03-31 - millones de ARS - valor 5.988 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento - al 2025-03-31 - millones de ARS - valor 128 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Disminución - al 2026-03-31 - millones de ARS - valor (4.359) - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Reclasificación - al 2026-03-31 - millones de ARS - valor (23.549) - pagina 45   [confianza: media]
```

### `#/tables/65`

- **procedencia:** paginas [45]
- **table_uid:** `TBL-491d322fda0c443c`
- **table_segment_uid:** `TSEG-491d322fda0c443c`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:45->45']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2026-03-31 - (unidad no declarada) - valor 1.008 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2025-03-31 - (unidad no declarada) - valor 14 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento - al 2026-03-31 - (unidad no declarada) - valor 732 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento - al 2025-03-31 - (unidad no declarada) - valor 2 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Disminución - al 2026-03-31 - (unidad no declarada) - valor (913) - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Disminución - al 2025-03-31 - (unidad no declarada) - valor (1) - pagina 45   [confianza: media]
```

### `#/tables/66`

- **procedencia:** paginas [45]
- **table_uid:** `TBL-6ee2bee34202d1b0`
- **table_segment_uid:** `TSEG-6ee2bee34202d1b0`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:45->45']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Caja - al 2026-03-31 - (unidad no declarada) - valor 277 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Caja - al 2025-12-31 - (unidad no declarada) - valor 291 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Bancos - al 2026-03-31 - (unidad no declarada) - valor 177.420 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Bancos - al 2025-12-31 - (unidad no declarada) - valor 487.206 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Depósito a plazo - al 2026-03-31 - (unidad no declarada) - valor 10.053 - pagina 45   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Depósito a plazo - al 2025-12-31 - (unidad no declarada) - valor 16 - pagina 45   [confianza: media]
```

### `#/tables/67`

- **procedencia:** paginas [45]
- **table_uid:** `TBL-519f454625d09a4d`
- **table_segment_uid:** `TSEG-519f454625d09a4d`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:45->45']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/68`

- **procedencia:** paginas [46]
- **table_uid:** `TBL-cf6cb56413735863`
- **table_segment_uid:** `TSEG-cf6cb56413735863`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/605`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (14 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Préstamos financieros - al 2026-03-31 - millones de ARS - valor 62.190 - pagina 46   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Préstamos financieros - al 2025-12-31 - millones de ARS - valor 65.475 - pagina 46   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Obligaciones negociables - al 2026-03-31 - millones de ARS - valor 2.483.408 - pagina 46   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Obligaciones negociables - al 2025-12-31 - millones de ARS - valor 2.618.272 - pagina 46   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Total no corriente - al 2026-03-31 - millones de ARS - valor 2.545.598 - pagina 46   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Total no corriente - al 2025-12-31 - millones de ARS - valor 2.683.747 - pagina 46   [confianza: media]
```

### `#/tables/69`

- **procedencia:** paginas [46]
- **table_uid:** `TBL-6179c4cbdec65e0f`
- **table_segment_uid:** `TSEG-6179c4cbdec65e0f`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:46->46']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/70`

- **procedencia:** paginas [47]
- **table_uid:** `TBL-ca94650511e272b0`
- **table_segment_uid:** `TSEG-ca94650511e272b0`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (19 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Préstamos al inicio del ejercicio - al 2026-03-31 - (unidad no declarada) - valor 2.753.689 - pagina 47   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Préstamos al inicio del ejercicio - al 2025-03-31 - (unidad no declarada) - valor 2.145.013 - pagina 47   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Préstamos recibidos - al 2025-03-31 - (unidad no declarada) - valor 47.700 - pagina 47   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Préstamos pagados - al 2026-03-31 - (unidad no declarada) - valor (32.581) - pagina 47   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Préstamos pagados - al 2025-03-31 - (unidad no declarada) - valor (74.142) - pagina 47   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Intereses devengados - al 2026-03-31 - (unidad no declarada) - valor 45.831 - pagina 47   [confianza: media]
```

### `#/tables/71`

- **procedencia:** paginas [47]
- **table_uid:** `TBL-e5a3285883d7f7dd`
- **table_segment_uid:** `TSEG-e5a3285883d7f7dd`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:47->47']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/72`

- **procedencia:** paginas [48]
- **table_uid:** `TBL-abe24a3c7defa576`
- **table_segment_uid:** `TSEG-abe24a3c7defa576`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de USD (origen `texto_adyacente`, evidencia `#/texts/629`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (37 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Garantías de clientes - al 2026-03-31 - millones de USD - valor 33 - pagina 48   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Garantías de clientes - al 2025-12-31 - millones de USD - valor 35 - pagina 48   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Deudas comerciales - al 2026-03-31 - millones de USD - valor 33 - pagina 48   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Deudas comerciales - al 2025-12-31 - millones de USD - valor 35 - pagina 48   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Acuerdos de compensación - al 2026-03-31 - millones de USD - valor 97.041 - pagina 48   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - No corriente / Acuerdos de compensación - al 2025-12-31 - millones de USD - valor 102.166 - pagina 48   [confianza: media]
```

### `#/tables/73`

- **procedencia:** paginas [48]
- **table_uid:** `TBL-e8e546868ba79212`
- **table_segment_uid:** `TSEG-e8e546868ba79212`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:48->48']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/74`

- **procedencia:** paginas [49]
- **table_uid:** `TBL-cf12687d42365cea`
- **table_segment_uid:** `TSEG-cf12687d42365cea`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/634`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=5']

**DESPUES** — hechos recuperables (20 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de marzo de 2026 - Activos financieros a valor razonable con cambios en resultados / Títulos de deuda pública - (periodo no declarado) - millones de ARS - valor 545.112 - pagina 49   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de marzo de 2026 - Activos financieros a valor razonable con cambios en resultados / Títulos de deuda pública - (periodo no declarado) - millones de ARS - valor 545.112 - pagina 49   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de marzo de 2026 - Activos financieros a valor razonable con cambios en resultados / Obligaciones negociables - (periodo no declarado) - millones de ARS - valor 34.409 - pagina 49   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de marzo de 2026 - Activos financieros a valor razonable con cambios en resultados / Obligaciones negociables - (periodo no declarado) - millones de ARS - valor 34.409 - pagina 49   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de marzo de 2026 - Activos financieros a valor razonable con cambios en resultados / Fondos comunes de inversión - (periodo no declarado) - millones de ARS - valor 23.490 - pagina 49   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de marzo de 2026 - Activos financieros a valor razonable con cambios en resultados / Fondos comunes de inversión - (periodo no declarado) - millones de ARS - valor 23.490 - pagina 49   [confianza: media]
```

### `#/tables/75`

- **procedencia:** paginas [49]
- **table_uid:** `TBL-ed3da23d90559084`
- **table_segment_uid:** `TSEG-ed3da23d90559084`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:49->49']

**DESPUES** — hechos recuperables (19 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de diciembre de 2025 - Activos financieros a valor razonable con cambios en resultados / Títulos de deuda pública - (periodo no declarado) - (unidad no declarada) - valor 448.832 - pagina 49   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de diciembre de 2025 - Activos financieros a valor razonable con cambios en resultados / Títulos de deuda pública - (periodo no declarado) - (unidad no declarada) - valor 448.832 - pagina 49   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de diciembre de 2025 - Activos financieros a valor razonable con cambios en resultados / Obligaciones negociables - (periodo no declarado) - (unidad no declarada) - valor 68.219 - pagina 49   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de diciembre de 2025 - Activos financieros a valor razonable con cambios en resultados / Obligaciones negociables - (periodo no declarado) - (unidad no declarada) - valor 68.219 - pagina 49   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de diciembre de 2025 - Activos financieros a valor razonable con cambios en resultados / Fondos comunes de inversión - (periodo no declarado) - (unidad no declarada) - valor 12.023 - pagina 49   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Al 31 de diciembre de 2025 - Activos financieros a valor razonable con cambios en resultados / Fondos comunes de inversión - (periodo no declarado) - (unidad no declarada) - valor 12.023 - pagina 49   [confianza: media]
```

### `#/tables/76`

- **procedencia:** paginas [49]
- **table_uid:** `TBL-08698df609fe625a`
- **table_segment_uid:** `TSEG-08698df609fe625a`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:49->49']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/77`

- **procedencia:** paginas [51]
- **table_uid:** `TBL-4ebc66d0670b6204`
- **table_segment_uid:** `TSEG-4ebc66d0670b6204`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/666`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:49->51']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2026-03-31 - millones de ARS - valor 51.216 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2026-03-31 - millones de ARS - valor 267.965 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Variación del período - al 2026-03-31 - millones de ARS - valor (2.638) - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Variación del período - al 2026-03-31 - millones de ARS - valor (13.802) - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldo al cierre del período - al 2026-03-31 - millones de ARS - valor 48.578 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldo al cierre del período - al 2026-03-31 - millones de ARS - valor 254.163 - pagina 51   [confianza: media]
```

### `#/tables/78`

- **procedencia:** paginas [51]
- **table_uid:** `TBL-567b8227ca66639b`
- **table_segment_uid:** `TSEG-567b8227ca66639b`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:51->51']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2025-03-31 - (unidad no declarada) - valor 35.932 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldo al inicio del ejercicio - al 2025-03-31 - (unidad no declarada) - valor 187.995 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Variación del período - al 2025-03-31 - (unidad no declarada) - valor 1.518 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Variación del período - al 2025-03-31 - (unidad no declarada) - valor 7.941 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldo al cierre del período - al 2025-03-31 - (unidad no declarada) - valor 37.450 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldo al cierre del período - al 2025-03-31 - (unidad no declarada) - valor 195.936 - pagina 51   [confianza: media]
```

### `#/tables/79`

- **procedencia:** paginas [51]
- **table_uid:** `TBL-35ba8102a6592735`
- **table_segment_uid:** `TSEG-35ba8102a6592735`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:51->51']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Ganancia atribuible a los propietarios de la Sociedad - al 2026-03-31 - (unidad no declarada) - valor 293.366 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia atribuible a los propietarios de la Sociedad - al 2025-03-31 - (unidad no declarada) - valor 161.886 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Promedio ponderado de acciones ordinarias en circulación - al 2026-03-31 - (unidad no declarada) - valor 1.360 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Promedio ponderado de acciones ordinarias en circulación - al 2025-03-31 - (unidad no declarada) - valor 1.360 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia por acción básica y diluida - al 2026-03-31 - (unidad no declarada) - valor 215,71 - pagina 51   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Ganancia por acción básica y diluida - al 2025-03-31 - (unidad no declarada) - valor 119,03 - pagina 51   [confianza: media]
```

### `#/tables/80`

- **procedencia:** paginas [51]
- **table_uid:** `TBL-98662faf8c6d419d`
- **table_segment_uid:** `TSEG-98662faf8c6d419d`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:51->51']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/81`

- **procedencia:** paginas [52]
- **table_uid:** `TBL-954280ac29433755`
- **table_segment_uid:** `TSEG-954280ac29433755`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (44 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Impuesto a las ganancias - (periodo no declarado) - (unidad no declarada) - valor 10.6 - pagina 52   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Impuesto a las ganancias - al 2026-03-31 - (unidad no declarada) - valor (97.637) - pagina 52   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Impuesto a las ganancias - al 2025-03-31 - (unidad no declarada) - valor (3.029) - pagina 52   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Intereses devengados - al 2026-03-31 - (unidad no declarada) - valor 47.648 - pagina 52   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Intereses devengados - al 2025-03-31 - (unidad no declarada) - valor 8.008 - pagina 52   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Depreciaciones y amortizaciones - al 2026-03-31 - (unidad no declarada) - valor 173.620 - pagina 52   [confianza: media]
```

### `#/tables/82`

- **procedencia:** paginas [52]
- **table_uid:** `TBL-43fd342c3762b6e2`
- **table_segment_uid:** `TSEG-43fd342c3762b6e2`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:52->52']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/83`

- **procedencia:** paginas [53]
- **table_uid:** `TBL-a783f66e16005352`
- **table_segment_uid:** `TSEG-a783f66e16005352`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/683`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (18 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Aumento de créditos por ventas y otros créditos - al 2026-03-31 - millones de ARS - valor (670.632) - pagina 53   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento de créditos por ventas y otros créditos - al 2025-03-31 - millones de ARS - valor (120.920) - pagina 53   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento de inventarios - al 2026-03-31 - millones de ARS - valor (624) - pagina 53   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento de inventarios - al 2025-03-31 - millones de ARS - valor (25.664) - pagina 53   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento de deudas comerciales y otras deudas - al 2026-03-31 - millones de ARS - valor 36.008 - pagina 53   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento de deudas comerciales y otras deudas - al 2025-03-31 - millones de ARS - valor 82.195 - pagina 53   [confianza: media]
```

### `#/tables/84`

- **procedencia:** paginas [53]
- **table_uid:** `TBL-a1b9808501833d15`
- **table_segment_uid:** `TSEG-a1b9808501833d15`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:53->53']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Adquisiciones de propiedades, planta y equipo a través de un aumento de deudas comerciales - al 2026-03-31 - (unidad no declarada) - valor (138.795) - pagina 53   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Adquisiciones de propiedades, planta y equipo a través de un aumento de deudas comerciales - al 2025-03-31 - (unidad no declarada) - valor (105.002) - pagina 53   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Costos financieros capitalizados en propiedades, planta y equipo - al 2026-03-31 - (unidad no declarada) - valor (4.570) - pagina 53   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Disminución de otros créditos a través un aumento de activos financieros a valor razonable con cambios en resultados - al 2026-03-31 - (unidad no declarada) - valor 205.156 - pagina 53   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Disminución de provisiones a través de un aumento en otros deudas - al 2026-03-31 - (unidad no declarada) - valor (44.313) - pagina 53   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Aumento de activos intangibles mediante la disminución de otros créditos - al 2026-03-31 - (unidad no declarada) - valor (490) - pagina 53   [confianza: media]
```

### `#/tables/85`

- **procedencia:** paginas [53]
- **table_uid:** `TBL-b8cfec501abbdd2b`
- **table_segment_uid:** `TSEG-b8cfec501abbdd2b`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:53->53']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/86`

- **procedencia:** paginas [54]
- **table_uid:** `TBL-5544468b35f709f0`
- **table_segment_uid:** `TSEG-5544468b35f709f0`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/696`)
- **extraction_warnings:** ['moneda_inferida_de_simbolo_pesos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (14 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.03.2026 - Asociadas y negocios conjuntos / CTB - (periodo no declarado) - millones de ARS - valor 224 - pagina 54   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.03.2026 - Asociadas y negocios conjuntos / CTB - (periodo no declarado) - millones de ARS - valor 15 - pagina 54   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.03.2026 - Asociadas y negocios conjuntos / TGS - (periodo no declarado) - millones de ARS - valor 11.430 - pagina 54   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.03.2026 - Asociadas y negocios conjuntos / TGS - (periodo no declarado) - millones de ARS - valor 3.526 - pagina 54   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.03.2026 - Asociadas y negocios conjuntos / TGS - (periodo no declarado) - millones de ARS - valor 22.783 - pagina 54   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.03.2026 - Asociadas y negocios conjuntos / Transener - (periodo no declarado) - millones de ARS - valor 55 - pagina 54   [confianza: media]
```

### `#/tables/87`

- **procedencia:** paginas [54]
- **table_uid:** `TBL-563f6007551c8cf2`
- **table_segment_uid:** `TSEG-563f6007551c8cf2`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:54->54']

**DESPUES** — hechos recuperables (14 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.12.2025 - Asociadas y negocios conjuntos / CTB - (periodo no declarado) - (unidad no declarada) - valor 235 - pagina 54   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.12.2025 - Asociadas y negocios conjuntos / CTB - (periodo no declarado) - (unidad no declarada) - valor 15 - pagina 54   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.12.2025 - Asociadas y negocios conjuntos / TGS - (periodo no declarado) - (unidad no declarada) - valor 11.207 - pagina 54   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.12.2025 - Asociadas y negocios conjuntos / TGS - (periodo no declarado) - (unidad no declarada) - valor 6.326 - pagina 54   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.12.2025 - Asociadas y negocios conjuntos / TGS - (periodo no declarado) - (unidad no declarada) - valor 23.305 - pagina 54   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Saldos al 31.12.2025 - Asociadas y negocios conjuntos / Transener - (periodo no declarado) - (unidad no declarada) - valor 43 - pagina 54   [confianza: media]
```

### `#/tables/88`

- **procedencia:** paginas [54]
- **table_uid:** `TBL-92061bc92f61a068`
- **table_segment_uid:** `TSEG-92061bc92f61a068`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:54->54']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/89`

- **procedencia:** paginas [55]
- **table_uid:** `TBL-da9eb8641c3553cc`
- **table_segment_uid:** `TSEG-da9eb8641c3553cc`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/705`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=9']

**DESPUES** — hechos recuperables (27 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Asociadas y negocios conjuntos / CTB - Ventas de bienes y servicios (1) / 2026 - millones de ARS - valor 564 - pagina 55   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Asociadas y negocios conjuntos / CTB - Ventas de bienes y servicios (1) / 2025 - millones de ARS - valor 423 - pagina 55   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Asociadas y negocios conjuntos / TGS - Ventas de bienes y servicios (1) / 2026 - millones de ARS - valor 21.253 - pagina 55   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Asociadas y negocios conjuntos / TGS - Ventas de bienes y servicios (1) / 2025 - millones de ARS - valor 13.112 - pagina 55   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Asociadas y negocios conjuntos / TGS - Compras de bienes y servicios (2) / 2026 - millones de ARS - valor (39.246) - pagina 55   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Asociadas y negocios conjuntos / TGS - Compras de bienes y servicios (2) / 2025 - millones de ARS - valor (27.614) - pagina 55   [confianza: media]
```

### `#/tables/90`

- **procedencia:** paginas [55]
- **table_uid:** `TBL-f710d8d356a0975c`
- **table_segment_uid:** `TSEG-f710d8d356a0975c`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/709`)
- **extraction_warnings:** ['moneda_inferida_de_simbolo_pesos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:55->55']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Asociadas y negocios conjuntos / TGS - Ingresos financieros (1) / 2026 - millones de ARS - valor 104 - pagina 55   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Asociadas y negocios conjuntos / TGS - Ingresos financieros (1) / 2025 - millones de ARS - valor 224 - pagina 55   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Otras partes relacionadas / Oldelval - Dividendos cobrados / 2026 - millones de ARS - valor 375 - pagina 55   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Otras partes relacionadas /  - Ingresos financieros (1) / 2026 - millones de ARS - valor 104 - pagina 55   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Otras partes relacionadas /  - Ingresos financieros (1) / 2025 - millones de ARS - valor 224 - pagina 55   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Operaciones por el período de tres meses - Otras partes relacionadas /  - Dividendos cobrados / 2026 - millones de ARS - valor 375 - pagina 55   [confianza: media]
```

### `#/tables/91`

- **procedencia:** paginas [55]
- **table_uid:** `TBL-bf8cde8c98b1a925`
- **table_segment_uid:** `TSEG-bf8cde8c98b1a925`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:55->55']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/92`

- **procedencia:** paginas [56]
- **table_uid:** `TBL-5bc1c89eb15fb1bb`
- **table_segment_uid:** `TSEG-5bc1c89eb15fb1bb`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/716`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=6']

**DESPUES** — hechos recuperables (110 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Otros créditos - (periodo no declarado) - ARS - valor 44,17 - pagina 56   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Otros créditos - (periodo no declarado) - ARS - valor 1.382,00 - pagina 56   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Otros créditos - al 2026-03-31 - ARS - valor 61.042 - pagina 56   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Otros créditos - al 2025-12-31 - ARS - valor 61.210 - pagina 56   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Total del activo no corriente - al 2026-03-31 - ARS - valor 61.042 - pagina 56   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - ACTIVO NO CORRIENTE / Total del activo no corriente - al 2025-12-31 - ARS - valor 61.210 - pagina 56   [confianza: media]
```

### `#/tables/93`

- **procedencia:** paginas [56]
- **table_uid:** `TBL-0c3f3679b2393137`
- **table_segment_uid:** `TSEG-0c3f3679b2393137`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:56->56']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/94`

- **procedencia:** paginas [57]
- **table_uid:** `TBL-cfd170eef28d4f09`
- **table_segment_uid:** `TSEG-cfd170eef28d4f09`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/95`

- **procedencia:** paginas [58]
- **table_uid:** `TBL-cf2a80274b72b29e`
- **table_segment_uid:** `TSEG-cf2a80274b72b29e`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/96`

- **procedencia:** paginas [59]
- **table_uid:** `TBL-2b1008173c43330a`
- **table_segment_uid:** `TSEG-2b1008173c43330a`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/97`

- **procedencia:** paginas [60]
- **table_uid:** `TBL-3555df36541b2e79`
- **table_segment_uid:** `TSEG-3555df36541b2e79`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/765`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (27 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Activo no corriente - al 2026-03-31 - millones de ARS - valor 7.124.911 - pagina 60   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Activo no corriente - al 2025-03-31 - millones de ARS - valor 4.623.629 - pagina 60   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Activo no corriente - al 2024-03-31 - millones de ARS - valor 3.125.919 - pagina 60   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Activo corriente - al 2026-03-31 - millones de ARS - valor 2.572.602 - pagina 60   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Activo corriente - al 2025-03-31 - millones de ARS - valor 2.033.990 - pagina 60   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Activo corriente - al 2024-03-31 - millones de ARS - valor 1.342.307 - pagina 60   [confianza: media]
```

### `#/tables/98`

- **procedencia:** paginas [60]
- **table_uid:** `TBL-b877bf0880ad0812`
- **table_segment_uid:** `TSEG-b877bf0880ad0812`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:60->60']

**DESPUES** — hechos recuperables (36 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Resultado operativo antes de resultados por participaciones y venta de sociedades - al 2026-03-31 - (unidad no declarada) - valor 145.839 - pagina 60   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Resultado operativo antes de resultados por participaciones y venta de sociedades - al 2025-03-31 - (unidad no declarada) - valor 80.845 - pagina 60   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Resultado operativo antes de resultados por participaciones y venta de sociedades - al 2024-03-31 - (unidad no declarada) - valor 47.038 - pagina 60   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Resultado por participaciones y ventas de sociedades - al 2026-03-31 - (unidad no declarada) - valor 93.833 - pagina 60   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Resultado por participaciones y ventas de sociedades - al 2025-03-31 - (unidad no declarada) - valor 48.144 - pagina 60   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Resultado por participaciones y ventas de sociedades - al 2024-03-31 - (unidad no declarada) - valor 52.874 - pagina 60   [confianza: media]
```

### `#/tables/99`

- **procedencia:** paginas [60]
- **table_uid:** `TBL-978b5a4dd6d36415`
- **table_segment_uid:** `TSEG-978b5a4dd6d36415`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:60->60']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/100`

- **procedencia:** paginas [61]
- **table_uid:** `TBL-0014b438a429193a`
- **table_segment_uid:** `TSEG-0014b438a429193a`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/770`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (12 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Flujos netos de efectivo (aplicado a) generados por las actividades operativas - al 2026-03-31 - millones de ARS - valor (330.230) - pagina 61   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Flujos netos de efectivo (aplicado a) generados por las actividades operativas - al 2025-03-31 - millones de ARS - valor 93.885 - pagina 61   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Flujos netos de efectivo (aplicado a) generados por las actividades operativas - al 2024-03-31 - millones de ARS - valor (14.214) - pagina 61   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Flujos netos de efectivo aplicados a las actividades de inversión - al 2026-03-31 - millones de ARS - valor (290.751) - pagina 61   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Flujos netos de efectivo aplicados a las actividades de inversión - al 2025-03-31 - millones de ARS - valor (50.561) - pagina 61   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Flujos netos de efectivo aplicados a las actividades de inversión - al 2024-03-31 - millones de ARS - valor (32.967) - pagina 61   [confianza: media]
```

### `#/tables/101`

- **procedencia:** paginas [61]
- **table_uid:** `TBL-969008acfd2a8847`
- **table_segment_uid:** `TSEG-969008acfd2a8847`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:61->61']

**DESPUES** — hechos recuperables (36 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Liquidez / Activo corriente - al 2026-03-31 - (unidad no declarada) - valor 2.572.602 - pagina 61   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Liquidez / Activo corriente - al 2025-03-31 - (unidad no declarada) - valor 2.033.990 - pagina 61   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Liquidez / Activo corriente - al 2024-03-31 - (unidad no declarada) - valor 1.342.307 - pagina 61   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Liquidez / Pasivo corriente - al 2026-03-31 - (unidad no declarada) - valor 1.260.156 - pagina 61   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Liquidez / Pasivo corriente - al 2025-03-31 - (unidad no declarada) - valor 1.114.995 - pagina 61   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Liquidez / Pasivo corriente - al 2024-03-31 - (unidad no declarada) - valor 510.440 - pagina 61   [confianza: media]
```

### `#/tables/102`

- **procedencia:** paginas [61]
- **table_uid:** `TBL-cb62169b988e7675`
- **table_segment_uid:** `TSEG-cb62169b988e7675`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:61->61']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/103`

- **procedencia:** paginas [62]
- **table_uid:** `TBL-8dd1bc9ecbb63264`
- **table_segment_uid:** `TSEG-8dd1bc9ecbb63264`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (24 en total, se muestran 6):

```text
Pampa_EEFF_Consolidado_1Q2026 - Petróleo y gas (en miles de boe/día) / Petróleo - al 2026-03-31 - (unidad no declarada) - valor 19 - pagina 62   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Petróleo y gas (en miles de boe/día) / Petróleo - al 2025-03-31 - (unidad no declarada) - valor 3 - pagina 62   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Petróleo y gas (en miles de boe/día) / Petróleo - al 2024-03-31 - (unidad no declarada) - valor 4 - pagina 62   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Petróleo y gas (en miles de boe/día) / Gas - al 2026-03-31 - (unidad no declarada) - valor 81 - pagina 62   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Petróleo y gas (en miles de boe/día) / Gas - al 2025-03-31 - (unidad no declarada) - valor 70 - pagina 62   [confianza: media]
Pampa_EEFF_Consolidado_1Q2026 - Petróleo y gas (en miles de boe/día) / Gas - al 2024-03-31 - (unidad no declarada) - valor 69 - pagina 62   [confianza: media]
```

### `#/tables/104`

- **procedencia:** paginas [62]
- **table_uid:** `TBL-ee94ebe4d35ec7c3`
- **table_segment_uid:** `TSEG-ee94ebe4d35ec7c3`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:62->62']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

## PDF — `MSU_ON_ClaseIV.pdf`

- identidad: `DOC-0015` / `ART-SHA256-3634553D38F42E039868F9537C0DC8879715412BD5C1A31B6B1FF41D613D4E5E`
- entidad de las cifras: **no declarada**
- tablas detectadas: 13 — hechos emitidos: 151

### `#/tables/0`

- **procedencia:** paginas [3]
- **table_uid:** `TBL-6477244fdff7464d`
- **table_segment_uid:** `TSEG-6477244fdff7464d`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente', 'sin_encabezado_propio', 'sin_encabezado_recuperable']
- **reglas:** —

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
MSU_ON_ClaseIV - ÍNDICE ................................ ................................ ................................ ................................ .......... - (periodo no declarado) - (unidad no declarada) - valor 3 - pagina 3   [confianza: baja]
MSU_ON_ClaseIV - AVISO A LOS INVERSORES Y DECLARACIONES ................................ ................................ - (periodo no declarado) - (unidad no declarada) - valor ........ 4 - pagina 3   [confianza: baja]
MSU_ON_ClaseIV - OFERTA DE LAS OBLIGACIONES NEGOCIABLES ................................ ................................ - (periodo no declarado) - (unidad no declarada) - valor 9 - pagina 3   [confianza: baja]
MSU_ON_ClaseIV - PLAN DE DISTRIBUCIÓN ................................ ................................ ................................ ............ - (periodo no declarado) - (unidad no declarada) - valor ....... 16 - pagina 3   [confianza: baja]
MSU_ON_ClaseIV - FACTORES DE RIESGO ................................ ................................ ................................ ............. - (periodo no declarado) - (unidad no declarada) - valor 24 - pagina 3   [confianza: baja]
MSU_ON_ClaseIV - INFORMACIÓN FINANCIERA ................................ ................................ ................................ ...... - (periodo no declarado) - (unidad no declarada) - valor 27 - pagina 3   [confianza: baja]
```

### `#/tables/1`

- **procedencia:** paginas [10]
- **table_uid:** `TBL-bee79994f804543f`
- **table_segment_uid:** `TSEG-bee79994f804543f`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:3->10']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/2`

- **procedencia:** paginas [11]
- **table_uid:** `TBL-54abac5a692e2547`
- **table_segment_uid:** `TSEG-54abac5a692e2547`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:no_enlazada:el_anterior_tampoco_tiene_encabezado']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/3`

- **procedencia:** paginas [27]
- **table_uid:** `TBL-868ef5e23e87f003`
- **table_segment_uid:** `TSEG-868ef5e23e87f003`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2, 3, 4]
- **unidad:** miles de ARS (origen `celda_encabezado`, evidencia `r1c1`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 1],inferido=[0, 1, 2, 3, 4]']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:11->27']

**DESPUES** — hechos recuperables (9 en total, se muestran 6):

```text
MSU_ON_ClaseIV - Gastos de comercialización - periodo de 3 meses terminado el 2022-03-31 - miles de ARS - valor (39,979) - pagina 27   [confianza: alta]
MSU_ON_ClaseIV - Gastos de comercialización - periodo de 3 meses terminado el 2021-03-31 - miles de ARS - valor (33,890) - pagina 27   [confianza: alta]
MSU_ON_ClaseIV - Gastos de administración - periodo de 3 meses terminado el 2022-03-31 - miles de ARS - valor (138,042) - pagina 27   [confianza: alta]
MSU_ON_ClaseIV - Gastos de administración - periodo de 3 meses terminado el 2021-03-31 - miles de ARS - valor (108,857) - pagina 27   [confianza: alta]
MSU_ON_ClaseIV - Cargo por impuesto a las ganancias - periodo de 3 meses terminado el 2022-03-31 - miles de ARS - valor (341,193) - pagina 27   [confianza: alta]
MSU_ON_ClaseIV - Cargo por impuesto a las ganancias - periodo de 3 meses terminado el 2021-03-31 - miles de ARS - valor (829,521) - pagina 27   [confianza: alta]
```

### `#/tables/4`

- **procedencia:** paginas [28]
- **table_uid:** `TBL-c620366407f37c89`
- **table_segment_uid:** `TSEG-c620366407f37c89`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles de ARS (origen `celda_encabezado`, evidencia `r0c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0]']

**DESPUES** — hechos recuperables (20 en total, se muestran 6):

```text
MSU_ON_ClaseIV - ACTIVO NO CORRIENTE / Créditos impositivos y aduaneros - al 2022-03-31 - miles de ARS - valor 230,508 - pagina 28   [confianza: alta]
MSU_ON_ClaseIV - ACTIVO NO CORRIENTE / Créditos impositivos y aduaneros - al 2021-12-31 - miles de ARS - valor 215,410 - pagina 28   [confianza: alta]
MSU_ON_ClaseIV - ACTIVO NO CORRIENTE / Otros créditos - al 2022-03-31 - miles de ARS - valor 530,336 - pagina 28   [confianza: alta]
MSU_ON_ClaseIV - ACTIVO NO CORRIENTE / Otros créditos - al 2021-12-31 - miles de ARS - valor 503,639 - pagina 28   [confianza: alta]
MSU_ON_ClaseIV - ACTIVO CORRIENTE / Créditos impositivos y aduaneros - al 2022-03-31 - miles de ARS - valor 426,398 - pagina 28   [confianza: alta]
MSU_ON_ClaseIV - ACTIVO CORRIENTE / Créditos impositivos y aduaneros - al 2021-12-31 - miles de ARS - valor 272,105 - pagina 28   [confianza: alta]
```

### `#/tables/5`

- **procedencia:** paginas [29]
- **table_uid:** `TBL-be4e036847d72c45`
- **table_segment_uid:** `TSEG-be4e036847d72c45`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2]
- **unidad:** miles de ARS (origen `celda_encabezado`, evidencia `r2c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=8']

**DESPUES** — hechos recuperables (9 en total, se muestran 6):

```text
MSU_ON_ClaseIV - 13,160,627 - (periodo no declarado) - miles de ARS - valor 468,160 - pagina 29   [confianza: media]
MSU_ON_ClaseIV - 13,160,627 - (periodo no declarado) - miles de ARS - valor (424,764) - pagina 29   [confianza: media]
MSU_ON_ClaseIV - 13,160,627 - (periodo no declarado) - miles de ARS - valor 190,783 - pagina 29   [confianza: media]
MSU_ON_ClaseIV - - - (periodo no declarado) - miles de ARS - valor 333,702 - pagina 29   [confianza: media]
MSU_ON_ClaseIV - - - (periodo no declarado) - miles de ARS - valor 656,174 - pagina 29   [confianza: media]
MSU_ON_ClaseIV - - - (periodo no declarado) - miles de ARS - valor (989,876) - pagina 29   [confianza: media]
```

### `#/tables/6`

- **procedencia:** paginas [30]
- **table_uid:** `TBL-86aed786a66c8d68`
- **table_segment_uid:** `TSEG-86aed786a66c8d68`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `celda_encabezado`, evidencia `r1c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:8!=3']

**DESPUES** — hechos recuperables (33 en total, se muestran 6):

```text
MSU_ON_ClaseIV - Actividades operativas / Ganancia del período - al 2021-03-31 - miles de ARS - valor 802,730 - pagina 30   [confianza: alta]
MSU_ON_ClaseIV - Ajustes correspondientes a partidas que no generan ni consumen fondos: / Impuesto a las ganancias devengado - al 2022-03-31 - miles de ARS - valor 341,193 - pagina 30   [confianza: alta]
MSU_ON_ClaseIV - Ajustes correspondientes a partidas que no generan ni consumen fondos: / Impuesto a las ganancias devengado - al 2021-03-31 - miles de ARS - valor 829,521 - pagina 30   [confianza: alta]
MSU_ON_ClaseIV - Ajustes correspondientes a partidas que no generan ni consumen fondos: / Depreciaciones de propiedad, planta y equipos - al 2022-03-31 - miles de ARS - valor 672,262 - pagina 30   [confianza: alta]
MSU_ON_ClaseIV - Ajustes correspondientes a partidas que no generan ni consumen fondos: / Depreciaciones de propiedad, planta y equipos - al 2021-03-31 - miles de ARS - valor 589,232 - pagina 30   [confianza: alta]
MSU_ON_ClaseIV - Ajustes correspondientes a partidas que no generan ni consumen fondos: / Diferencia de cambio, neta - al 2022-03-31 - miles de ARS - valor 264,970 - pagina 30   [confianza: alta]
```

### `#/tables/7`

- **procedencia:** paginas [30]
- **table_uid:** `TBL-9683c49ff971b18c`
- **table_segment_uid:** `TSEG-9683c49ff971b18c`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:30->30']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
MSU_ON_ClaseIV - Índice - Solvencia - al 2022-03-31 - (unidad no declarada) - valor 14.91% - pagina 30   [confianza: media]
MSU_ON_ClaseIV - Índice - Solvencia - al 2021-12-31 - (unidad no declarada) - valor 13.17% - pagina 30   [confianza: media]
MSU_ON_ClaseIV - Índice - Liquidez corriente - al 2022-03-31 - (unidad no declarada) - valor 78.55% - pagina 30   [confianza: media]
MSU_ON_ClaseIV - Índice - Liquidez corriente - al 2021-12-31 - (unidad no declarada) - valor 88.72% - pagina 30   [confianza: media]
MSU_ON_ClaseIV - Índice - Inmovilización inmediata - al 2022-03-31 - (unidad no declarada) - valor 89.37% - pagina 30   [confianza: media]
MSU_ON_ClaseIV - Índice - Inmovilización inmediata - al 2021-12-31 - (unidad no declarada) - valor 88.42% - pagina 30   [confianza: media]
```

### `#/tables/8`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-953e1c2345bb380a`
- **table_segment_uid:** `TSEG-953e1c2345bb380a`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `celda_encabezado`, evidencia `r1c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:30->32']

**DESPUES** — hechos recuperables (14 en total, se muestran 6):

```text
MSU_ON_ClaseIV - PATRIMONIO / Capital social - al 2022-03-31 - miles de ARS - valor 468,160 - pagina 32   [confianza: alta]
MSU_ON_ClaseIV - PATRIMONIO / Capital social - al 2021-12-31 - miles de ARS - valor 468,160 - pagina 32   [confianza: alta]
MSU_ON_ClaseIV - PATRIMONIO / Prima de fusión - al 2022-03-31 - miles de ARS - valor (424,764) - pagina 32   [confianza: alta]
MSU_ON_ClaseIV - PATRIMONIO / Prima de fusión - al 2021-12-31 - miles de ARS - valor (424,764) - pagina 32   [confianza: alta]
MSU_ON_ClaseIV - PATRIMONIO / Reserva legal - al 2022-03-31 - miles de ARS - valor 190,783 - pagina 32   [confianza: alta]
MSU_ON_ClaseIV - PATRIMONIO / Reserva legal - al 2021-12-31 - miles de ARS - valor 190,783 - pagina 32   [confianza: alta]
```

### `#/tables/9`

- **procedencia:** paginas [33]
- **table_uid:** `TBL-d448a56ba5225c75`
- **table_segment_uid:** `TSEG-d448a56ba5225c75`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2]
- **unidad:** miles de ARS (origen `celda_encabezado`, evidencia `r1c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=5']

**DESPUES** — hechos recuperables (40 en total, se muestran 6):

```text
MSU_ON_ClaseIV - Ventas - periodo de 3 meses terminado el 2022-03-31 - miles de ARS - valor 5.472.931 - pagina 33   [confianza: alta]
MSU_ON_ClaseIV - Ventas - periodo de 3 meses terminado el 2021-03-31 - miles de ARS - valor 4.815.176 - pagina 33   [confianza: alta]
MSU_ON_ClaseIV - Ventas - (periodo no declarado) - miles de ARS - valor 657.755 - pagina 33   [confianza: media]
MSU_ON_ClaseIV - Ventas - (periodo no declarado) - porcentaje - valor 14% - pagina 33   [confianza: media]
MSU_ON_ClaseIV - Costo de ventas - periodo de 3 meses terminado el 2022-03-31 - miles de ARS - valor (1.313.703) - pagina 33   [confianza: alta]
MSU_ON_ClaseIV - Costo de ventas - periodo de 3 meses terminado el 2021-03-31 - miles de ARS - valor (1.135.144) - pagina 33   [confianza: alta]
```

### `#/tables/10`

- **procedencia:** paginas [35]
- **table_uid:** `TBL-de5119b8d18d400d`
- **table_segment_uid:** `TSEG-de5119b8d18d400d`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `celda_encabezado`, evidencia `r1c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:33->35']

**DESPUES** — hechos recuperables (5 en total, se muestran 5):

```text
MSU_ON_ClaseIV - Ganancia del período - al 2021-03-31 - miles de ARS - valor 802,730 - pagina 35   [confianza: alta]
MSU_ON_ClaseIV - Impuesto a las ganancias - al 2022-03-31 - miles de ARS - valor 341,193 - pagina 35   [confianza: alta]
MSU_ON_ClaseIV - Impuesto a las ganancias - al 2021-03-31 - miles de ARS - valor 829,521 - pagina 35   [confianza: alta]
MSU_ON_ClaseIV - Depreciaciones - al 2022-03-31 - miles de ARS - valor 672,262 - pagina 35   [confianza: alta]
MSU_ON_ClaseIV - Depreciaciones - al 2021-03-31 - miles de ARS - valor 589,232 - pagina 35   [confianza: alta]
```

### `#/tables/11`

- **procedencia:** paginas [35]
- **table_uid:** `TBL-23d0d05dde7fc336`
- **table_segment_uid:** `TSEG-23d0d05dde7fc336`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2]
- **unidad:** miles de ARS (origen `celda_encabezado`, evidencia `r0c1`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0],inferido=[0, 1, 2]']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:35->35']

**DESPUES** — hechos recuperables (2 en total, se muestran 2):

```text
MSU_ON_ClaseIV - Flujo neto de efectivo aplicado a las actividades de inversión - al 2022-03-31 - miles de ARS - valor (2,852) - pagina 35   [confianza: alta]
MSU_ON_ClaseIV - Diferencia de cambio - al 2022-03-31 - miles de ARS - valor 274,625 - pagina 35   [confianza: alta]
```

### `#/tables/12`

- **procedencia:** paginas [36]
- **table_uid:** `TBL-c6e3a5ebc7dfa0b4`
- **table_segment_uid:** `TSEG-c6e3a5ebc7dfa0b4`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2, 3, 4]
- **unidad:** miles de ARS (origen `celda_encabezado`, evidencia `r0c1`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0],inferido=[0, 1, 2, 3, 4]']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0, 1, 2, 3, 4]']

**DESPUES** — hechos recuperables (1 en total, se muestran 1):

```text
MSU_ON_ClaseIV - Diferencia de cambio - al 2021-03-31 - miles de ARS - valor 68,338 - pagina 36   [confianza: alta]
```

## PDF — `TGS_EEFF_2025_09.pdf`

- identidad: `DOC-0021` / `ART-SHA256-64DEE6344349B2EC33D448E61E80B04F5CC271ED8A47692EF7B35429FD296270`
- entidad de las cifras: **no declarada**
- tablas detectadas: 112 — hechos emitidos: 2906

### `#/tables/0`

- **procedencia:** paginas [4]
- **table_uid:** `TBL-0723ce5d693ae7bc`
- **table_segment_uid:** `TSEG-0723ce5d693ae7bc`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** —

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/1`

- **procedencia:** paginas [5]
- **table_uid:** `TBL-605bf36a7d1bb370`
- **table_segment_uid:** `TSEG-605bf36a7d1bb370`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** millones (origen `texto_adyacente`, evidencia `#/texts/43`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 1],inferido=[]', 'sin_encabezado_propio', 'continuacion_huerfana:ancho_distinto:3!=4', 'sin_encabezado_recuperable']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (28 en total, se muestran 6):

```text
TGS_EEFF_2025_09 -  - (periodo no declarado) - millones - valor 2025 2024 - pagina 5   [confianza: baja]
TGS_EEFF_2025_09 - Etano 227.222 - (periodo no declarado) - millones - valor 209.555 - pagina 5   [confianza: baja]
TGS_EEFF_2025_09 - Etano 227.222 - (periodo no declarado) - millones - valor 17.667 - pagina 5   [confianza: baja]
TGS_EEFF_2025_09 - Etano 227.222 - (periodo no declarado) - millones - valor 8,4% - pagina 5   [confianza: baja]
TGS_EEFF_2025_09 - Propano 153.344 - (periodo no declarado) - millones - valor 161.505 - pagina 5   [confianza: baja]
TGS_EEFF_2025_09 - Propano 153.344 - (periodo no declarado) - millones - valor (8.161) - pagina 5   [confianza: baja]
```

### `#/tables/2`

- **procedencia:** paginas [6]
- **table_uid:** `TBL-02e1dc9fe1d94875`
- **table_segment_uid:** `TSEG-02e1dc9fe1d94875`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de ARS (origen `texto_adyacente`, evidencia `#/texts/52`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 1],inferido=[0]']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=3']

**DESPUES** — hechos recuperables (2 en total, se muestran 2):

```text
TGS_EEFF_2025_09 - Concepto MM de $ % s/ total MM de $ % s/ total MM de $ % / Totales 652.948 - 2025 2024 Variación - millones de ARS - valor 619.324 - pagina 6   [confianza: media]
TGS_EEFF_2025_09 - Concepto MM de $ % s/ total MM de $ % s/ total MM de $ % / Totales 652.948 - 2025 2024 Variación - millones de ARS - valor 33.624 - pagina 6   [confianza: media]
```

### `#/tables/3`

- **procedencia:** paginas [6]
- **table_uid:** `TBL-cbfef02cedc46e05`
- **table_segment_uid:** `TSEG-cbfef02cedc46e05`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** millones (origen `texto_adyacente`, evidencia `#/texts/57`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 1],inferido=[]', 'sin_encabezado_propio', 'continuacion_huerfana:paginas_no_consecutivas:6->6', 'sin_encabezado_recuperable']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:6->6']

**DESPUES** — hechos recuperables (5 en total, se muestran 5):

```text
TGS_EEFF_2025_09 -  - (periodo no declarado) - millones - valor 2025 2024 - pagina 6   [confianza: baja]
TGS_EEFF_2025_09 - Diferencia de cambio 119.826 87.935 / Subtotal 156.583 - (periodo no declarado) - millones - valor 141.781 - pagina 6   [confianza: baja]
TGS_EEFF_2025_09 - Diferencia de cambio (205.686) (143.141) / Subtotal (194.997) - (periodo no declarado) - millones - valor (260.369) - pagina 6   [confianza: baja]
TGS_EEFF_2025_09 - Otros resultados financieros / Ganancia por valuación a valor razonable de activos financieros con cambios en resultados - (periodo no declarado) - millones - valor 118.381 119.942 - pagina 6   [confianza: baja]
TGS_EEFF_2025_09 - Otros resultados financieros (7.765) (13.620) / Resultado por cambio en el poder adquisitivo de la moneda ("RECPAM") - (periodo no declarado) - millones - valor (41.239) (48.835) - pagina 6   [confianza: baja]
```

### `#/tables/4`

- **procedencia:** paginas [7]
- **table_uid:** `TBL-8d09482ad995e2e5`
- **table_segment_uid:** `TSEG-8d09482ad995e2e5`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de ARS (origen `celda_encabezado`, evidencia `r1c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (5 en total, se muestran 5):

```text
TGS_EEFF_2025_09 - Flujo neto de efectivo aplicado a las actividades de inversión (210.496) (328.098) 117.602 / Flujo neto de efectivo aplicado a las actividades de financiación - 2025 2024 Variación / (en millones de pesos) - millones de ARS - valor (186.812) (12.236) (174.576) - pagina 7   [confianza: baja]
TGS_EEFF_2025_09 - Flujo neto de efectivo aplicado a las actividades de inversión (210.496) (328.098) 117.602 / Variación neta de efectivo y equivalentes de efectivo - 2025 2024 Variación / (en millones de pesos) - millones de ARS - valor 13.695 48.353 (34.657) - pagina 7   [confianza: baja]
TGS_EEFF_2025_09 - Efectivo y equivalente de efectivo al inicio del ejercicio 73.141 17.526 55.615 / Efecto variación del tipo de cambio sobre el efectivo y los equivalentes de efectivo - 2025 2024 Variación / (en millones de pesos) - millones de ARS - valor (6) 265 (271) - pagina 7   [confianza: baja]
TGS_EEFF_2025_09 - Efectivo y equivalente de efectivo al inicio del ejercicio 73.141 17.526 55.615 / Efecto variación RECPAM generado por el efectivo y equivalente de efectivo - 2025 2024 Variación / (en millones de pesos) - millones de ARS - valor (13.801) (24.728) 10.927 - pagina 7   [confianza: baja]
TGS_EEFF_2025_09 - Efectivo y equivalente de efectivo al inicio del ejercicio 73.141 17.526 55.615 / Efectivo y equivalente de efectivo al cierre del período - 2025 2024 Variación / (en millones de pesos) - millones de ARS - valor 73.030 41.416 31.614 - pagina 7   [confianza: baja]
```

### `#/tables/5`

- **procedencia:** paginas [7]
- **table_uid:** `TBL-378a12829580c3d1`
- **table_segment_uid:** `TSEG-378a12829580c3d1`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:7->7']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/6`

- **procedencia:** paginas [8]
- **table_uid:** `TBL-b9239b2bdfc88579`
- **table_segment_uid:** `TSEG-b9239b2bdfc88579`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** millones de USD (origen `texto_adyacente`, evidencia `#/texts/73`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:2!=4']

**DESPUES** — hechos recuperables (27 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Etano 91.137 - (periodo no declarado) - millones de USD - valor 53.394 - pagina 8   [confianza: media]
TGS_EEFF_2025_09 - Etano 91.137 - (periodo no declarado) - millones de USD - valor 37.743 - pagina 8   [confianza: media]
TGS_EEFF_2025_09 - Etano 91.137 - (periodo no declarado) - porcentaje - valor 71% - pagina 8   [confianza: media]
TGS_EEFF_2025_09 - Propano 69.633 - (periodo no declarado) - millones de USD - valor 63.249 - pagina 8   [confianza: media]
TGS_EEFF_2025_09 - Propano 69.633 - (periodo no declarado) - millones de USD - valor 6.384 - pagina 8   [confianza: media]
TGS_EEFF_2025_09 - Propano 69.633 - (periodo no declarado) - porcentaje - valor 10% - pagina 8   [confianza: media]
```

### `#/tables/7`

- **procedencia:** paginas [8]
- **table_uid:** `TBL-b758f6e93da3a82e`
- **table_segment_uid:** `TSEG-b758f6e93da3a82e`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones (origen `texto_adyacente`, evidencia `#/texts/76`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:8->8']

**DESPUES** — hechos recuperables (2 en total, se muestran 2):

```text
TGS_EEFF_2025_09 - Concepto MM de $ % s/ total MM de $ % s/ total MM de $ % / Totales 245.622 - 2025 2024 Variación - millones - valor 200.051 - pagina 8   [confianza: media]
TGS_EEFF_2025_09 - Concepto MM de $ % s/ total MM de $ % s/ total MM de $ % / Totales 245.622 - 2025 2024 Variación - millones - valor 45.571 - pagina 8   [confianza: media]
```

### `#/tables/8`

- **procedencia:** paginas [9]
- **table_uid:** `TBL-8d471ad1d152ce83`
- **table_segment_uid:** `TSEG-8d471ad1d152ce83`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** millones (origen `texto_adyacente`, evidencia `#/texts/79`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 1],inferido=[]', 'sin_encabezado_propio', 'continuacion_huerfana:ancho_distinto:3!=5', 'sin_encabezado_recuperable']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=5']

**DESPUES** — hechos recuperables (1 en total, se muestran 1):

```text
TGS_EEFF_2025_09 -  - (periodo no declarado) - millones - valor 2025 2024 2023 2022 2021 - pagina 9   [confianza: baja]
```

### `#/tables/9`

- **procedencia:** paginas [9]
- **table_uid:** `TBL-b9fff92291de28bd`
- **table_segment_uid:** `TSEG-b9fff92291de28bd`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:9->9']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/10`

- **procedencia:** paginas [10]
- **table_uid:** `TBL-65a476e415ba9da7`
- **table_segment_uid:** `TSEG-65a476e415ba9da7`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 1],inferido=[0]', 'unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:1!=11']

**DESPUES** — hechos recuperables (159 en total, se muestran 6):

```text
TGS_EEFF_2025_09 -  - Trimestre julio - septiembre de - (unidad no declarada) - valor 2025 2024 2023 2022 2021 2025 2024 2023 2022 2021 - pagina 10   [confianza: baja]
TGS_EEFF_2025_09 -  - Trimestre julio - septiembre de - (unidad no declarada) - valor 2025 2024 2023 2022 2021 2025 2024 2023 2022 2021 - pagina 10   [confianza: baja]
TGS_EEFF_2025_09 -  - Trimestre julio - septiembre de - (unidad no declarada) - valor 2025 2024 2023 2022 2021 2025 2024 2023 2022 2021 - pagina 10   [confianza: baja]
TGS_EEFF_2025_09 - Transporte de Gas Natural / Capacidad en firme contratada promedio (Millones de m3/día) - Acumulado al 30 de septiembre de - (unidad no declarada) - valor 89,6 - pagina 10   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural / Capacidad en firme contratada promedio (Millones de m3/día) - Acumulado al 30 de septiembre de - (unidad no declarada) - valor 83,0 - pagina 10   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural / Capacidad en firme contratada promedio (Millones de m3/día) - Acumulado al 30 de septiembre de - (unidad no declarada) - valor 83,3 - pagina 10   [confianza: media]
```

### `#/tables/11`

- **procedencia:** paginas [10]
- **table_uid:** `TBL-d2c7581579c9366b`
- **table_segment_uid:** `TSEG-d2c7581579c9366b`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0],inferido=[]', 'unidad_ausente', 'sin_encabezado_propio', 'continuacion_huerfana:paginas_no_consecutivas:10->10', 'sin_encabezado_recuperable']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:10->10']

**DESPUES** — hechos recuperables (13 en total, se muestran 6):

```text
TGS_EEFF_2025_09 -  - (periodo no declarado) - (unidad no declarada) - valor 2025 2024 2023 2022 2021 - pagina 10   [confianza: baja]
TGS_EEFF_2025_09 - Liquidez (a) 3,72 - (periodo no declarado) - (unidad no declarada) - valor 2,73 - pagina 10   [confianza: baja]
TGS_EEFF_2025_09 - Liquidez (a) 3,72 - (periodo no declarado) - (unidad no declarada) - valor 3,56 - pagina 10   [confianza: baja]
TGS_EEFF_2025_09 - Liquidez (a) 3,72 - (periodo no declarado) - (unidad no declarada) - valor 3,65 - pagina 10   [confianza: baja]
TGS_EEFF_2025_09 - Liquidez (a) 3,72 - (periodo no declarado) - (unidad no declarada) - valor 1,75 - pagina 10   [confianza: baja]
TGS_EEFF_2025_09 - Solvencia (b) 2,11 - (periodo no declarado) - (unidad no declarada) - valor 1,92 - pagina 10   [confianza: baja]
```

### `#/tables/12`

- **procedencia:** paginas [11]
- **table_uid:** `TBL-cc89642fd55dc13c`
- **table_segment_uid:** `TSEG-cc89642fd55dc13c`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0],inferido=[]', 'unidad_ausente', 'sin_encabezado_propio', 'continuacion_huerfana:ancho_distinto:5!=1', 'sin_encabezado_recuperable']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:5!=1']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/13`

- **procedencia:** paginas [12]
- **table_uid:** `TBL-099933f273c90df1`
- **table_segment_uid:** `TSEG-099933f273c90df1`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/203`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0],inferido=[0, 1]', 'escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:1!=2']

**DESPUES** — hechos recuperables (3 en total, se muestran 3):

```text
TGS_EEFF_2025_09 - Clase “A” - Al 30 de septiembre de 2025 / Monto suscripto, integrado y autorizado a la oferta pública (Nota 20 a los presentes Estados Financieros Consolidados Condensados Intermedios) - ARS - valor 405.192.594 - pagina 12   [confianza: media]
TGS_EEFF_2025_09 - Clase “B” - Al 30 de septiembre de 2025 / Monto suscripto, integrado y autorizado a la oferta pública (Nota 20 a los presentes Estados Financieros Consolidados Condensados Intermedios) - ARS - valor 347.568.464 - pagina 12   [confianza: media]
TGS_EEFF_2025_09 - Total - Al 30 de septiembre de 2025 / Monto suscripto, integrado y autorizado a la oferta pública (Nota 20 a los presentes Estados Financieros Consolidados Condensados Intermedios) - ARS - valor 752.761.058 - pagina 12   [confianza: media]
```

### `#/tables/14`

- **procedencia:** paginas [13]
- **table_uid:** `TBL-80cd7d87f4bf7fa0`
- **table_segment_uid:** `TSEG-80cd7d87f4bf7fa0`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/212`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:2!=6']

**DESPUES** — hechos recuperables (86 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Ingresos por ventas y otros - Por los períodos de tres meses / 2025 - miles de ARS - valor 426.518.170 - pagina 13   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas y otros - Por los períodos de tres meses / 2024 - miles de ARS - valor 337.927.610 - pagina 13   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas y otros - Por los períodos de nueve meses terminados el 30 de septiembre de / 2025 - miles de ARS - valor 1.156.194.101 - pagina 13   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas y otros - Por los períodos de nueve meses terminados el 30 de septiembre de / 2024 - miles de ARS - valor 1.062.597.297 - pagina 13   [confianza: media]
TGS_EEFF_2025_09 - Costo de ventas netas - Por los períodos de tres meses / 2025 - miles de ARS - valor (204.119.562) - pagina 13   [confianza: media]
TGS_EEFF_2025_09 - Costo de ventas netas - Por los períodos de tres meses / 2024 - miles de ARS - valor (166.157.944) - pagina 13   [confianza: media]
```

### `#/tables/15`

- **procedencia:** paginas [14]
- **table_uid:** `TBL-f6eb44a2f7aa2ae5`
- **table_segment_uid:** `TSEG-f6eb44a2f7aa2ae5`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/224`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:6!=4']

**DESPUES** — hechos recuperables (81 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Propiedad, planta y equipos - (periodo no declarado) - miles de ARS - valor 13 - pagina 14   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Propiedad, planta y equipos - al 2025-09-30 - miles de ARS - valor 2.913.180.409 - pagina 14   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Propiedad, planta y equipos - al 2024-12-31 - miles de ARS - valor 2.908.480.272 - pagina 14   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Inversiones en compañías asociadas - (periodo no declarado) - miles de ARS - valor 10 - pagina 14   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Inversiones en compañías asociadas - al 2025-09-30 - miles de ARS - valor 2.596.056 - pagina 14   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Inversiones en compañías asociadas - al 2024-12-31 - miles de ARS - valor 1.494.353 - pagina 14   [confianza: media]
```

### `#/tables/16`

- **procedencia:** paginas [15]
- **table_uid:** `TBL-cd51c8202c13f72a`
- **table_segment_uid:** `TSEG-cd51c8202c13f72a`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/237`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0, 1, 2, 3],inferido=[0, 1, 2]']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=15']

**DESPUES** — hechos recuperables (88 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor 752.761 - pagina 15   [confianza: media]
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor 899.934.947 - pagina 15   [confianza: media]
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor 41.734 - pagina 15   [confianza: media]
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor 49.893.494 - pagina 15   [confianza: media]
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor (90.347.853) - pagina 15   [confianza: media]
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor (26.209.113) - pagina 15   [confianza: media]
```

### `#/tables/17`

- **procedencia:** paginas [15]
- **table_uid:** `TBL-f18f57b07990c286`
- **table_segment_uid:** `TSEG-f18f57b07990c286`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:15->15']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/18`

- **procedencia:** paginas [16]
- **table_uid:** `TBL-6e56f064ebaabbad`
- **table_segment_uid:** `TSEG-6e56f064ebaabbad`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/242`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=3']

**DESPUES** — hechos recuperables (69 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - FLUJO DE EFECTIVO GENERADO POR LAS OPERACIONES - Utilidad integral total del período - 2025 - miles de ARS - valor 275.226.903 - pagina 16   [confianza: media]
TGS_EEFF_2025_09 - FLUJO DE EFECTIVO GENERADO POR LAS OPERACIONES - Utilidad integral total del período - 2024 - miles de ARS - valor 293.355.978 - pagina 16   [confianza: media]
TGS_EEFF_2025_09 - FLUJO DE EFECTIVO GENERADO POR LAS OPERACIONES - generado por las operaciones: / Depreciación de propiedad, planta y equipos - 2025 - miles de ARS - valor 139.262.695 - pagina 16   [confianza: media]
TGS_EEFF_2025_09 - FLUJO DE EFECTIVO GENERADO POR LAS OPERACIONES - generado por las operaciones: / Depreciación de propiedad, planta y equipos - 2024 - miles de ARS - valor 116.599.475 - pagina 16   [confianza: media]
TGS_EEFF_2025_09 - FLUJO DE EFECTIVO GENERADO POR LAS OPERACIONES - generado por las operaciones: / Baja de propiedad, planta y equipos - 2025 - miles de ARS - valor 4.939.697 - pagina 16   [confianza: media]
TGS_EEFF_2025_09 - FLUJO DE EFECTIVO GENERADO POR LAS OPERACIONES - generado por las operaciones: / Baja de propiedad, planta y equipos - 2024 - miles de ARS - valor 2.369.834 - pagina 16   [confianza: media]
```

### `#/tables/19`

- **procedencia:** paginas [18]
- **table_uid:** `TBL-fa1b5cd3be7a39c8`
- **table_segment_uid:** `TSEG-fa1b5cd3be7a39c8`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/274`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[],inferido=[0]', 'escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:16->18']

**DESPUES** — hechos recuperables (1 en total, se muestran 1):

```text
TGS_EEFF_2025_09 - Sociedad - Telcosur - (periodo no declarado) - porcentaje - valor 99,98 - pagina 18   [confianza: media]
```

### `#/tables/20`

- **procedencia:** paginas [25]
- **table_uid:** `TBL-2d606c37e02adb61`
- **table_segment_uid:** `TSEG-2d606c37e02adb61`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/412`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:18->25']

**DESPUES** — hechos recuperables (5 en total, se muestran 5):

```text
TGS_EEFF_2025_09 - Saldos por financiación obtenida de proveedores para la adquisición de PPE - 2025 - ARS - valor 23.216.446 - pagina 25   [confianza: media]
TGS_EEFF_2025_09 - Saldos por financiación obtenida de proveedores para la adquisición de PPE - 2024 - ARS - valor 20.962.808 - pagina 25   [confianza: media]
TGS_EEFF_2025_09 - Cancelación de capital de pasivos por arrendamientos (1) - 2025 - ARS - valor 6.435.865 - pagina 25   [confianza: media]
TGS_EEFF_2025_09 - Cancelación de capital de pasivos por arrendamientos (1) - 2024 - ARS - valor 6.495.109 - pagina 25   [confianza: media]
TGS_EEFF_2025_09 - Cancelación impuesto a las ganancias con activos financieros a valor razonable con cambios en resultados - 2025 - ARS - valor 153.937.379 - pagina 25   [confianza: media]
```

### `#/tables/21`

- **procedencia:** paginas [26]
- **table_uid:** `TBL-888ba4eaa4adaee9`
- **table_segment_uid:** `TSEG-888ba4eaa4adaee9`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/432`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=7']

**DESPUES** — hechos recuperables (32 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Ingresos por ventas - Ventas intersegmentos - (periodo no declarado) - ARS - valor 20.358.180 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - Ventas intersegmentos - (periodo no declarado) - ARS - valor (20.358.180) - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - Costo de ventas - (periodo no declarado) - ARS - valor (207.887.187) - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - Costo de ventas - (periodo no declarado) - ARS - valor (244.724.157) - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - Costo de ventas - (periodo no declarado) - ARS - valor (95.460.719) - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - Costo de ventas - (periodo no declarado) - ARS - valor (4.209.263) - pagina 26   [confianza: media]
```

### `#/tables/22`

- **procedencia:** paginas [26]
- **table_uid:** `TBL-51e76c8d2781e272`
- **table_segment_uid:** `TSEG-51e76c8d2781e272`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:26->26']

**DESPUES** — hechos recuperables (37 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Ingresos por ventas - (periodo no declarado) - (unidad no declarada) - valor 374.641.517 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - (periodo no declarado) - (unidad no declarada) - valor 485.135.701 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - (periodo no declarado) - (unidad no declarada) - valor 196.985.382 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - (periodo no declarado) - (unidad no declarada) - valor 5.834.697 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - (periodo no declarado) - (unidad no declarada) - valor 1.062.597.297 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Ventas intersegmentos - (periodo no declarado) - (unidad no declarada) - valor 9.671.377 - pagina 26   [confianza: media]
```

### `#/tables/23`

- **procedencia:** paginas [26]
- **table_uid:** `TBL-36d5bf3ba79cbc93`
- **table_segment_uid:** `TSEG-36d5bf3ba79cbc93`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:26->26']

**DESPUES** — hechos recuperables (24 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Por mercado / Mercado externo - Período de nueve meses terminado el 30 de septiembre de 2025 / Producción y comercialización de Líquidos - (unidad no declarada) - valor 169.414.218 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Por mercado / Mercado externo - (periodo no declarado) - (unidad no declarada) - valor 169.414.218 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2025 / Transporte de Gas Natural - (unidad no declarada) - valor 488.347.656 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2025 / Producción y comercialización de Líquidos - (unidad no declarada) - valor 248.206.242 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2025 / Midstream - (unidad no declarada) - valor 233.592.921 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2025 / Telecomunicaciones - (unidad no declarada) - valor 5.049.962 - pagina 26   [confianza: media]
```

### `#/tables/24`

- **procedencia:** paginas [26]
- **table_uid:** `TBL-7602508681261d3d`
- **table_segment_uid:** `TSEG-7602508681261d3d`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:26->26']

**DESPUES** — hechos recuperables (24 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Por mercado / Mercado externo - Período de nueve meses terminado el 30 de septiembre de 2024 / Producción y comercialización de Líquidos - (unidad no declarada) - valor 209.067.926 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Por mercado / Mercado externo - (periodo no declarado) - (unidad no declarada) - valor 209.067.926 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2024 / Transporte de Gas Natural - (unidad no declarada) - valor 374.641.517 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2024 / Producción y comercialización de Líquidos - (unidad no declarada) - valor 261.650.573 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2024 / Midstream - (unidad no declarada) - valor 196.985.382 - pagina 26   [confianza: media]
TGS_EEFF_2025_09 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2024 / Telecomunicaciones - (unidad no declarada) - valor 5.834.697 - pagina 26   [confianza: media]
```

### `#/tables/25`

- **procedencia:** paginas [27]
- **table_uid:** `TBL-ae6c26eb4139b519`
- **table_segment_uid:** `TSEG-ae6c26eb4139b519`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/447`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:6!=5']

**DESPUES** — hechos recuperables (26 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Saldo a favor Impuesto a los Ingresos Brutos - al 2024-12-31 - ARS - valor 129.308 - pagina 27   [confianza: media]
TGS_EEFF_2025_09 - Saldo a favor IVA - al 2024-12-31 - ARS - valor 1.954.230 - pagina 27   [confianza: media]
TGS_EEFF_2025_09 - Saldo a favor impuesto a las ganancias (1) - al 2025-09-30 - ARS - valor 689.273 - pagina 27   [confianza: media]
TGS_EEFF_2025_09 - Saldo a favor impuesto a las ganancias (1) - al 2024-12-31 - ARS - valor 488.471 - pagina 27   [confianza: media]
TGS_EEFF_2025_09 - Otros créditos impositivos - al 2025-09-30 - ARS - valor 3.929.578 - pagina 27   [confianza: media]
TGS_EEFF_2025_09 - Otros créditos impositivos - al 2024-12-31 - ARS - valor 745.611 - pagina 27   [confianza: media]
```

### `#/tables/26`

- **procedencia:** paginas [27]
- **table_uid:** `TBL-c060bb1ae8a121c6`
- **table_segment_uid:** `TSEG-c060bb1ae8a121c6`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:27->27']

**DESPUES** — hechos recuperables (20 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Con terceros - al 2025-09-30 - (unidad no declarada) - valor 169.708.409 - pagina 27   [confianza: media]
TGS_EEFF_2025_09 - Con terceros - al 2024-12-31 - (unidad no declarada) - valor 174.225.935 - pagina 27   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2025-09-30 - (unidad no declarada) - valor 75.690.497 - pagina 27   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2024-12-31 - (unidad no declarada) - valor 76.767.234 - pagina 27   [confianza: media]
TGS_EEFF_2025_09 - Producción y Comercialización de Líquidos - al 2025-09-30 - (unidad no declarada) - valor 40.029.196 - pagina 27   [confianza: media]
TGS_EEFF_2025_09 - Producción y Comercialización de Líquidos - al 2024-12-31 - (unidad no declarada) - valor 55.637.047 - pagina 27   [confianza: media]
```

### `#/tables/27`

- **procedencia:** paginas [27]
- **table_uid:** `TBL-b2c31bef65fe454a`
- **table_segment_uid:** `TSEG-b2c31bef65fe454a`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente', 'sin_encabezado_propio', 'continuacion_huerfana:paginas_no_consecutivas:27->27', 'sin_encabezado_recuperable']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:27->27']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Saldos al 31/12/2023 - (periodo no declarado) - (unidad no declarada) - valor 801.423 - pagina 27   [confianza: baja]
TGS_EEFF_2025_09 - Efecto RECPAM - (periodo no declarado) - (unidad no declarada) - valor (403.588) - pagina 27   [confianza: baja]
TGS_EEFF_2025_09 - Saldos al 30/09/2024 - (periodo no declarado) - (unidad no declarada) - valor 397.835 - pagina 27   [confianza: baja]
TGS_EEFF_2025_09 - Efecto RECPAM - (periodo no declarado) - (unidad no declarada) - valor (29.811) - pagina 27   [confianza: baja]
TGS_EEFF_2025_09 - Saldos al 31/12/2024 - (periodo no declarado) - (unidad no declarada) - valor 368.024 - pagina 27   [confianza: baja]
TGS_EEFF_2025_09 - Efecto RECPAM - (periodo no declarado) - (unidad no declarada) - valor (538.227) - pagina 27   [confianza: baja]
```

### `#/tables/28`

- **procedencia:** paginas [28]
- **table_uid:** `TBL-90018f547031b3aa`
- **table_segment_uid:** `TSEG-90018f547031b3aa`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/463`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:2!=3']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Caja y bancos - al 2025-09-30 - miles de ARS - valor 6.169.690 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Caja y bancos - al 2024-12-31 - miles de ARS - valor 51.048.994 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Caja y bancos UT - al 2025-09-30 - miles de ARS - valor 1.933 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Caja y bancos UT - al 2024-12-31 - miles de ARS - valor 286 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Fondos comunes en mercado local - al 2025-09-30 - miles de ARS - valor 66.422.698 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Fondos comunes en mercado local - al 2024-12-31 - miles de ARS - valor 21.606.711 - pagina 28   [confianza: media]
```

### `#/tables/29`

- **procedencia:** paginas [28]
- **table_uid:** `TBL-bd7185b5de393784`
- **table_segment_uid:** `TSEG-bd7185b5de393784`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:28->28']

**DESPUES** — hechos recuperables (15 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2025-09-30 - (unidad no declarada) - valor 2.984.597 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2025-09-30 - (unidad no declarada) - valor 40.602.613 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2024-12-31 - (unidad no declarada) - valor 2.984.597 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2024-12-31 - (unidad no declarada) - valor 42.841.220 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Producción y Comercialización de Líquidos - al 2024-12-31 - (unidad no declarada) - valor 872.410 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Midstream - al 2025-09-30 - (unidad no declarada) - valor 5.223.203 - pagina 28   [confianza: media]
```

### `#/tables/30`

- **procedencia:** paginas [28]
- **table_uid:** `TBL-2302731491b75577`
- **table_segment_uid:** `TSEG-2302731491b75577`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:28->28']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Provisión honorarios a directores y síndicos - al 2025-09-30 - (unidad no declarada) - valor 232.983 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Provisión honorarios a directores y síndicos - al 2024-12-31 - (unidad no declarada) - valor 290.103 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Otros - al 2025-09-30 - (unidad no declarada) - valor 7.678 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Otros - al 2024-12-31 - (unidad no declarada) - valor 7.447 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Total - al 2025-09-30 - (unidad no declarada) - valor 240.661 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Total - al 2024-12-31 - (unidad no declarada) - valor 297.550 - pagina 28   [confianza: media]
```

### `#/tables/31`

- **procedencia:** paginas [28]
- **table_uid:** `TBL-e3c4a0b64ae513da`
- **table_segment_uid:** `TSEG-e3c4a0b64ae513da`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:28->28']

**DESPUES** — hechos recuperables (12 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Tasa de seguridad e higiene - al 2025-09-30 - (unidad no declarada) - valor 408.836 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Tasa de seguridad e higiene - al 2024-12-31 - (unidad no declarada) - valor 343.353 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Retenciones y percepciones efectuadas a terceros - al 2025-09-30 - (unidad no declarada) - valor 6.491.559 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Retenciones y percepciones efectuadas a terceros - al 2024-12-31 - (unidad no declarada) - valor 7.373.488 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a los ingresos brutos a pagar - al 2025-09-30 - (unidad no declarada) - valor 2.550.414 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a los ingresos brutos a pagar - al 2024-12-31 - (unidad no declarada) - valor 2.481.416 - pagina 28   [confianza: media]
```

### `#/tables/32`

- **procedencia:** paginas [28]
- **table_uid:** `TBL-0a254ca5e614255d`
- **table_segment_uid:** `TSEG-0a254ca5e614255d`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:28->28']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Proveedores comunes - al 2025-09-30 - (unidad no declarada) - valor 62.603.672 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Proveedores comunes - al 2024-12-31 - (unidad no declarada) - valor 65.972.535 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Proveedores comunes UT - al 2025-09-30 - (unidad no declarada) - valor 1.129.914 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Proveedores comunes UT - al 2024-12-31 - (unidad no declarada) - valor 1.313.181 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Saldos acreedores de clientes - al 2025-09-30 - (unidad no declarada) - valor 1.498.737 - pagina 28   [confianza: media]
TGS_EEFF_2025_09 - Saldos acreedores de clientes - al 2024-12-31 - (unidad no declarada) - valor 72.296 - pagina 28   [confianza: media]
```

### `#/tables/33`

- **procedencia:** paginas [29]
- **table_uid:** `TBL-89d7435e38051f45`
- **table_segment_uid:** `TSEG-89d7435e38051f45`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/478`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=5']

**DESPUES** — hechos recuperables (12 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Venta de bienes y servicios - Período de tres meses terminado el 30 de septiembre de / 2025 - ARS - valor 421.416.824 - pagina 29   [confianza: media]
TGS_EEFF_2025_09 - Venta de bienes y servicios - Período de tres meses terminado el 30 de septiembre de / 2024 - ARS - valor 331.968.216 - pagina 29   [confianza: media]
TGS_EEFF_2025_09 - Venta de bienes y servicios - Período de nueve meses terminado el 30 de septiembre de / 2025 - ARS - valor 1.144.610.999 - pagina 29   [confianza: media]
TGS_EEFF_2025_09 - Venta de bienes y servicios - Período de nueve meses terminado el 30 de septiembre de / 2024 - ARS - valor 1.048.180.095 - pagina 29   [confianza: media]
TGS_EEFF_2025_09 - Subsidios - Período de tres meses terminado el 30 de septiembre de / 2025 - ARS - valor 5.101.346 - pagina 29   [confianza: media]
TGS_EEFF_2025_09 - Subsidios - Período de tres meses terminado el 30 de septiembre de / 2024 - ARS - valor 5.959.394 - pagina 29   [confianza: media]
```

### `#/tables/34`

- **procedencia:** paginas [29]
- **table_uid:** `TBL-038fb3deea1fba80`
- **table_segment_uid:** `TSEG-038fb3deea1fba80`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:29->29']

**DESPUES** — hechos recuperables (20 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Existencia al inicio - Período de tres meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 12.983.606 - pagina 29   [confianza: media]
TGS_EEFF_2025_09 - Existencia al inicio - Período de tres meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 18.821.244 - pagina 29   [confianza: media]
TGS_EEFF_2025_09 - Existencia al inicio - Período de nueve meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 4.469.295 - pagina 29   [confianza: media]
TGS_EEFF_2025_09 - Existencia al inicio - Período de nueve meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 20.367.601 - pagina 29   [confianza: media]
TGS_EEFF_2025_09 - Compras - Período de tres meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 88.696.588 - pagina 29   [confianza: media]
TGS_EEFF_2025_09 - Compras - Período de tres meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 49.369.521 - pagina 29   [confianza: media]
```

### `#/tables/35`

- **procedencia:** paginas [30]
- **table_uid:** `TBL-3e4dd41d44f4d193`
- **table_segment_uid:** `TSEG-3e4dd41d44f4d193`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2, 3]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/489`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:5!=8']

**DESPUES** — hechos recuperables (122 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - 2025 / Total - ARS - valor 96.551.378 - pagina 30   [confianza: media]
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - 2025 / Costos de explotación / Actividad regulada - ARS - valor 40.444.575 - pagina 30   [confianza: media]
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - 2025 / Costos de explotación / Actividad / no regulada - ARS - valor 34.643.181 - pagina 30   [confianza: media]
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - 2025 / Gastos de administración - ARS - valor 16.617.718 - pagina 30   [confianza: media]
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - 2025 / Gastos de / comercialización - ARS - valor 4.845.904 - pagina 30   [confianza: media]
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - 2024 / Total - ARS - valor 92.858.079 - pagina 30   [confianza: media]
```

### `#/tables/36`

- **procedencia:** paginas [31]
- **table_uid:** `TBL-7bf171c10aca598d`
- **table_segment_uid:** `TSEG-7bf171c10aca598d`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/502`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:8!=5']

**DESPUES** — hechos recuperables (44 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Ingresos Financieros / Intereses - Período de tres meses terminado el 30 de septiembre de / 2025 - ARS - valor 6.274.176 - pagina 31   [confianza: media]
TGS_EEFF_2025_09 - Ingresos Financieros / Intereses - Período de tres meses terminado el 30 de septiembre de / 2024 - ARS - valor 27.621.660 - pagina 31   [confianza: media]
TGS_EEFF_2025_09 - Ingresos Financieros / Intereses - Período de nueve meses terminado el 30 de septiembre de / 2025 - ARS - valor 21.954.699 - pagina 31   [confianza: media]
TGS_EEFF_2025_09 - Ingresos Financieros / Intereses - Período de nueve meses terminado el 30 de septiembre de / 2024 - ARS - valor 68.648.616 - pagina 31   [confianza: media]
TGS_EEFF_2025_09 - Ingresos Financieros / Diferencia de cambio - Período de tres meses terminado el 30 de septiembre de / 2025 - ARS - valor 60.158.500 - pagina 31   [confianza: media]
TGS_EEFF_2025_09 - Ingresos Financieros / Diferencia de cambio - Período de tres meses terminado el 30 de septiembre de / 2024 - ARS - valor 26.625.707 - pagina 31   [confianza: media]
```

### `#/tables/37`

- **procedencia:** paginas [31]
- **table_uid:** `TBL-1785f6f1ce938268`
- **table_segment_uid:** `TSEG-1785f6f1ce938268`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:31->31']

**DESPUES** — hechos recuperables (28 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Evento climático (1) - Período de tres meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor (10.248.322) - pagina 31   [confianza: media]
TGS_EEFF_2025_09 - Evento climático (1) - Período de nueve meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor (45.741.370) - pagina 31   [confianza: media]
TGS_EEFF_2025_09 - Resultado por baja de Propiedad, planta y equipos - Período de tres meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 27 - pagina 31   [confianza: media]
TGS_EEFF_2025_09 - Resultado por baja de Propiedad, planta y equipos - Período de tres meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 121.084 - pagina 31   [confianza: media]
TGS_EEFF_2025_09 - Resultado por baja de Propiedad, planta y equipos - Período de nueve meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 162.034 - pagina 31   [confianza: media]
TGS_EEFF_2025_09 - Resultado por baja de Propiedad, planta y equipos - Período de nueve meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor (1.378.110) - pagina 31   [confianza: media]
```

### `#/tables/38`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-666ee0a583098edc`
- **table_segment_uid:** `TSEG-666ee0a583098edc`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/519`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:5!=3']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Plazo fijo en moneda extranjera - al 2025-09-30 - ARS - valor 330.889.750 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Plazo fijo en moneda extranjera - al 2024-12-31 - ARS - valor 293.466.141 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Otras colocaciones a plazo - al 2025-09-30 - ARS - valor 40.997.499 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Otras colocaciones a plazo - al 2024-12-31 - ARS - valor 37.775.605 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Total - al 2025-09-30 - ARS - valor 371.887.249 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Total - al 2024-12-31 - ARS - valor 331.241.746 - pagina 32   [confianza: media]
```

### `#/tables/39`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-0775b3fc765b2e89`
- **table_segment_uid:** `TSEG-0775b3fc765b2e89`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:32->32']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Títulos de deuda privada partes relacionadas - al 2025-09-30 - (unidad no declarada) - valor 14.783.377 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Títulos de deuda privada partes relacionadas - al 2024-12-31 - (unidad no declarada) - valor 24.966.043 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Títulos de deuda privada - al 2025-09-30 - (unidad no declarada) - valor 256.522.866 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Títulos de deuda privada - al 2024-12-31 - (unidad no declarada) - valor 240.485.203 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Títulos de deuda pública - al 2025-09-30 - (unidad no declarada) - valor 128.473.529 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Títulos de deuda pública - al 2024-12-31 - (unidad no declarada) - valor 246.179.054 - pagina 32   [confianza: media]
```

### `#/tables/40`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-55d6b6bb076a07d1`
- **table_segment_uid:** `TSEG-55d6b6bb076a07d1`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:32->32']

**DESPUES** — hechos recuperables (11 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Provisión vacaciones - al 2025-09-30 - (unidad no declarada) - valor 9.970.778 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Provisión vacaciones - al 2024-12-31 - (unidad no declarada) - valor 10.933.152 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Provisión sueldo anual complementario - al 2025-09-30 - (unidad no declarada) - valor 1.917.193 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Gratificaciones a pagar - al 2025-09-30 - (unidad no declarada) - valor 6.443.286 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Gratificaciones a pagar - al 2024-12-31 - (unidad no declarada) - valor 8.604.463 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Cargas sociales a pagar - al 2025-09-30 - (unidad no declarada) - valor 3.320.094 - pagina 32   [confianza: media]
```

### `#/tables/41`

- **procedencia:** paginas [32]
- **table_uid:** `TBL-3576d8661f8f81f5`
- **table_segment_uid:** `TSEG-3576d8661f8f81f5`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:32->32']

**DESPUES** — hechos recuperables (7 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Gas Link S.A. - al 2025-09-30 - (unidad no declarada) - valor $1 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Gas Link S.A. - al 2025-09-30 - (unidad no declarada) - valor 502.962 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Gas Link S.A. - al 2025-09-30 - (unidad no declarada) - valor 284.517 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Gas Link S.A. - al 2025-09-30 - (unidad no declarada) - valor 2.596.056 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Gas Link S.A. - al 2024-12-31 - (unidad no declarada) - valor 1.494.353 - pagina 32   [confianza: media]
TGS_EEFF_2025_09 - Total - al 2025-09-30 - (unidad no declarada) - valor 2.596.056 - pagina 32   [confianza: media]
```

### `#/tables/42`

- **procedencia:** paginas [33]
- **table_uid:** `TBL-ce6c83c5e39cd8c0`
- **table_segment_uid:** `TSEG-ce6c83c5e39cd8c0`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/533`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:6!=5']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - TGU (liquidada) - 30 de septiembre de / 2024 - ARS - valor (6.029) - pagina 33   [confianza: media]
TGS_EEFF_2025_09 - TGU (liquidada) - el 30 de septiembre de / 2024 - ARS - valor 12.831 - pagina 33   [confianza: media]
TGS_EEFF_2025_09 - Link - 30 de septiembre de / 2025 - ARS - valor 760.718 - pagina 33   [confianza: media]
TGS_EEFF_2025_09 - Link - 30 de septiembre de / 2024 - ARS - valor 299.338 - pagina 33   [confianza: media]
TGS_EEFF_2025_09 - Link - el 30 de septiembre de / 2025 - ARS - valor 1.101.703 - pagina 33   [confianza: media]
TGS_EEFF_2025_09 - Link - el 30 de septiembre de / 2024 - ARS - valor 158.342 - pagina 33   [confianza: media]
```

### `#/tables/43`

- **procedencia:** paginas [34]
- **table_uid:** `TBL-516e05805810d612`
- **table_segment_uid:** `TSEG-516e05805810d612`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/546`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:5!=14']

**DESPUES** — hechos recuperables (213 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Gasoductos - (periodo no declarado) - miles de ARS - valor 2.256.018.551 - pagina 34   [confianza: media]
TGS_EEFF_2025_09 - Gasoductos - (periodo no declarado) - miles de ARS - valor 8.927.026 - pagina 34   [confianza: media]
TGS_EEFF_2025_09 - Gasoductos - Al cierre del período - miles de ARS - valor 2.264.945.577 - pagina 34   [confianza: media]
TGS_EEFF_2025_09 - Gasoductos - al 2025-09-30 - miles de ARS - valor 1.318.547.153 - pagina 34   [confianza: media]
TGS_EEFF_2025_09 - Gasoductos - (periodo no declarado) - miles de ARS - valor 44.392.706 - pagina 34   [confianza: media]
TGS_EEFF_2025_09 - Gasoductos - (periodo no declarado) - porcentaje - valor 2,2 - pagina 34   [confianza: media]
```

### `#/tables/44`

- **procedencia:** paginas [35]
- **table_uid:** `TBL-4577830e5572c1ab`
- **table_segment_uid:** `TSEG-4577830e5572c1ab`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/559`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:14!=3']

**DESPUES** — hechos recuperables (17 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Deudas financieras corrientes / Intereses ON 2031 - al 2025-09-30 - miles de ARS - valor 10.537.450 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Deudas financieras corrientes / Intereses ON 2031 - al 2024-12-31 - miles de ARS - valor 22.715.218 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Deudas financieras corrientes / Préstamos bancarios - al 2025-09-30 - miles de ARS - valor 96.161.090 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Deudas financieras corrientes / Préstamos bancarios - al 2024-12-31 - miles de ARS - valor 63.370.726 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Deudas financieras corrientes / Pasivo por arrendamiento - al 2025-09-30 - miles de ARS - valor 10.533.390 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Deudas financieras corrientes / Pasivo por arrendamiento - al 2024-12-31 - miles de ARS - valor 9.522.475 - pagina 35   [confianza: media]
```

### `#/tables/45`

- **procedencia:** paginas [35]
- **table_uid:** `TBL-bc60b3e83d32cc70`
- **table_segment_uid:** `TSEG-bc60b3e83d32cc70`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:35->35']

**DESPUES** — hechos recuperables (30 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Saldo inicial - al 2025-09-30 - (unidad no declarada) - valor 17.045.878 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Saldo inicial - al 2025-09-30 - (unidad no declarada) - valor 690.427.648 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Saldo inicial - al 2024-09-30 - (unidad no declarada) - valor 45.721.862 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Saldo inicial - al 2024-09-30 - (unidad no declarada) - valor 1.206.853.560 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Efecto RECPAM - al 2025-09-30 - (unidad no declarada) - valor (6.152.929) - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Efecto RECPAM - al 2025-09-30 - (unidad no declarada) - valor (129.395.167) - pagina 35   [confianza: media]
```

### `#/tables/46`

- **procedencia:** paginas [35]
- **table_uid:** `TBL-a327131a259e1109`
- **table_segment_uid:** `TSEG-a327131a259e1109`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:35->35']

**DESPUES** — hechos recuperables (17 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - ON 2031 - Del 01/10/2029 en adelante - (unidad no declarada) - valor 662.578.012 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - ON 2031 - (periodo no declarado) - (unidad no declarada) - valor 662.578.012 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Intereses ON 2031 - al 2026-09-30 - (unidad no declarada) - valor 10.537.450 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Intereses ON 2031 - (periodo no declarado) - (unidad no declarada) - valor 10.537.450 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Pasivos por arrendamiento - al 2026-09-30 - (unidad no declarada) - valor 10.533.390 - pagina 35   [confianza: media]
TGS_EEFF_2025_09 - Pasivos por arrendamiento - Del 1/10/2026 al 30/09/2027 - (unidad no declarada) - valor 1.134.816 - pagina 35   [confianza: media]
```

### `#/tables/47`

- **procedencia:** paginas [36]
- **table_uid:** `TBL-9c33b744896afbb6`
- **table_segment_uid:** `TSEG-9c33b744896afbb6`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** millones de USD (origen `texto_adyacente`, evidencia `#/texts/645`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:8!=3']

**DESPUES** — hechos recuperables (7 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Monto en US$ - ON 2031 - millones de USD - valor 490.000.000 - pagina 36   [confianza: media]
TGS_EEFF_2025_09 - Monto en US$ - ON 2031 - millones de USD - valor 490.000.000 - pagina 36   [confianza: media]
TGS_EEFF_2025_09 - Tasa de Interés - ON 2031 - millones de USD - valor 8,50% - pagina 36   [confianza: media]
TGS_EEFF_2025_09 - Tasa de Interés - ON 2031 - millones de USD - valor 8,50% - pagina 36   [confianza: media]
TGS_EEFF_2025_09 - Precio de emisión - ON 2031 - millones de USD - valor 98,712% - pagina 36   [confianza: media]
TGS_EEFF_2025_09 - Precio de emisión - ON 2031 - millones de USD - valor 98,712% - pagina 36   [confianza: media]
```

### `#/tables/48`

- **procedencia:** paginas [37]
- **table_uid:** `TBL-50d322f331ea0941`
- **table_segment_uid:** `TSEG-50d322f331ea0941`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles (origen `celda_encabezado`, evidencia `r0c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (1 en total, se muestran 1):

```text
TGS_EEFF_2025_09 - Moneda - US$ - (periodo no declarado) - miles - valor 44.995.670 - pagina 37   [confianza: media]
```

### `#/tables/49`

- **procedencia:** paginas [37]
- **table_uid:** `TBL-70e4a078d252b0ee`
- **table_segment_uid:** `TSEG-70e4a078d252b0ee`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** millones de USD (origen `texto_adyacente`, evidencia `#/texts/669`)
- **extraction_warnings:** ['sin_encabezado_propio', 'continuacion_huerfana:paginas_no_consecutivas:37->37', 'sin_encabezado_recuperable']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:37->37']

**DESPUES** — hechos recuperables (1 en total, se muestran 1):

```text
TGS_EEFF_2025_09 - Monto en US$ - (periodo no declarado) - millones de USD - valor 24.000.000 - pagina 37   [confianza: baja]
```

### `#/tables/50`

- **procedencia:** paginas [38]
- **table_uid:** `TBL-45a789688649e8a4`
- **table_segment_uid:** `TSEG-45a789688649e8a4`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/680`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:2!=5']

**DESPUES** — hechos recuperables (12 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Impuesto a las ganancias - corriente - Período de tres meses terminado el 30 de septiembre de / 2025 - miles de ARS - valor (56.000.873) - pagina 38   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a las ganancias - corriente - Período de tres meses terminado el 30 de septiembre de / 2024 - miles de ARS - valor (32.532.485) - pagina 38   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a las ganancias - corriente - Período de nueve meses terminado el 30 de septiembre de / 2025 - miles de ARS - valor (152.544.887) - pagina 38   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a las ganancias - corriente - Período de nueve meses terminado el 30 de septiembre de / 2024 - miles de ARS - valor (203.291.450) - pagina 38   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a las ganancias - diferido - Período de tres meses terminado el 30 de septiembre de / 2025 - miles de ARS - valor 137.475 - pagina 38   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a las ganancias - diferido - Período de tres meses terminado el 30 de septiembre de / 2024 - miles de ARS - valor (1.466.569) - pagina 38   [confianza: media]
```

### `#/tables/51`

- **procedencia:** paginas [38]
- **table_uid:** `TBL-00c3cb898c7a8458`
- **table_segment_uid:** `TSEG-00c3cb898c7a8458`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:38->38']

**DESPUES** — hechos recuperables (21 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Activos financieros a valor razonable con cambio en resultados - al 2025-09-30 - (unidad no declarada) - valor 8.045.094 - pagina 38   [confianza: media]
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Activos financieros a valor razonable con cambio en resultados - al 2024-12-31 - (unidad no declarada) - valor 9.445.857 - pagina 38   [confianza: media]
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Provisiones para reclamos de terceros y otros - al 2025-09-30 - (unidad no declarada) - valor 1.622.224 - pagina 38   [confianza: media]
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Provisiones para reclamos de terceros y otros - al 2024-12-31 - (unidad no declarada) - valor 418.739 - pagina 38   [confianza: media]
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Arrendamientos financieros - al 2025-09-30 - (unidad no declarada) - valor 3.826.281 - pagina 38   [confianza: media]
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Arrendamientos financieros - al 2024-12-31 - (unidad no declarada) - valor 5.966.057 - pagina 38   [confianza: media]
```

### `#/tables/52`

- **procedencia:** paginas [39]
- **table_uid:** `TBL-e72e10829b89c3bb`
- **table_segment_uid:** `TSEG-e72e10829b89c3bb`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/694`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0]']

**DESPUES** — hechos recuperables (15 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Saldos al 31/12/2023 - (periodo no declarado) - miles de ARS - valor 6.571.930 - pagina 39   [confianza: media]
TGS_EEFF_2025_09 - Efecto RECPAM - (periodo no declarado) - miles de ARS - valor (3.389.428) - pagina 39   [confianza: media]
TGS_EEFF_2025_09 - Aumentos - (periodo no declarado) - miles de ARS - valor 544.460 - pagina 39   [confianza: media]
TGS_EEFF_2025_09 - Aumentos - (periodo no declarado) - miles de ARS - valor (1) - pagina 39   [confianza: baja]
TGS_EEFF_2025_09 - Saldos al 30/09/2024 - (periodo no declarado) - miles de ARS - valor 3.726.962 - pagina 39   [confianza: media]
TGS_EEFF_2025_09 - Efecto RECPAM - (periodo no declarado) - miles de ARS - valor (283.655) - pagina 39   [confianza: media]
```

### `#/tables/53`

- **procedencia:** paginas [40]
- **table_uid:** `TBL-2a5da09b90e18bf5`
- **table_segment_uid:** `TSEG-2a5da09b90e18bf5`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/710`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (21 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Créditos por ventas - 30 de septiembre de 2025 / Activos financieros a costo amortizado - miles de ARS - valor 187.049.318 - pagina 40   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Créditos por ventas - 30 de septiembre de 2025 / Total - miles de ARS - valor 187.049.318 - pagina 40   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Otros créditos - 30 de septiembre de 2025 / Activos financieros a costo amortizado - miles de ARS - valor 12.374.502 - pagina 40   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Otros créditos - 30 de septiembre de 2025 / Total - miles de ARS - valor 12.374.502 - pagina 40   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - 30 de septiembre de 2025 / Activos financieros a costo amortizado - miles de ARS - valor 371.887.249 - pagina 40   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - 30 de septiembre de 2025 / Total - miles de ARS - valor 371.887.249 - pagina 40   [confianza: media]
```

### `#/tables/54`

- **procedencia:** paginas [40]
- **table_uid:** `TBL-b099855a9bea7bae`
- **table_segment_uid:** `TSEG-b099855a9bea7bae`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:40->40']

**DESPUES** — hechos recuperables (16 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas comerciales - (periodo no declarado) - (unidad no declarada) - valor 98.535.388 - pagina 40   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas comerciales - (periodo no declarado) - (unidad no declarada) - valor 98.535.388 - pagina 40   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas financieras - (periodo no declarado) - (unidad no declarada) - valor 117.231.930 - pagina 40   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas financieras - (periodo no declarado) - (unidad no declarada) - valor 117.231.930 - pagina 40   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 18.748.418 - pagina 40   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 18.748.418 - pagina 40   [confianza: media]
```

### `#/tables/55`

- **procedencia:** paginas [41]
- **table_uid:** `TBL-d86464bf2cb4e23d`
- **table_segment_uid:** `TSEG-d86464bf2cb4e23d`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/724`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0, 1]']

**DESPUES** — hechos recuperables (21 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Créditos por ventas - 31 de diciembre de 2024 / Activos financieros a costo amortizado - miles de ARS - valor 190.270.112 - pagina 41   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Créditos por ventas - 31 de diciembre de 2024 / Total - miles de ARS - valor 190.270.112 - pagina 41   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Otros créditos - 31 de diciembre de 2024 / Activos financieros a costo amortizado - miles de ARS - valor 14.467.017 - pagina 41   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Otros créditos - 31 de diciembre de 2024 / Total - miles de ARS - valor 14.467.017 - pagina 41   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - 31 de diciembre de 2024 / Activos financieros a costo amortizado - miles de ARS - valor 331.241.746 - pagina 41   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - 31 de diciembre de 2024 / Total - miles de ARS - valor 331.241.746 - pagina 41   [confianza: media]
```

### `#/tables/56`

- **procedencia:** paginas [41]
- **table_uid:** `TBL-84d31ecb352d53a7`
- **table_segment_uid:** `TSEG-84d31ecb352d53a7`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:41->41']

**DESPUES** — hechos recuperables (16 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas comerciales - (periodo no declarado) - (unidad no declarada) - valor 93.567.063 - pagina 41   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas comerciales - (periodo no declarado) - (unidad no declarada) - valor 93.567.063 - pagina 41   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas financieras - (periodo no declarado) - (unidad no declarada) - valor 95.608.419 - pagina 41   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas financieras - (periodo no declarado) - (unidad no declarada) - valor 95.608.419 - pagina 41   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 19.635.623 - pagina 41   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 19.635.623 - pagina 41   [confianza: media]
```

### `#/tables/57`

- **procedencia:** paginas [42]
- **table_uid:** `TBL-2f2f41954e9b7a03`
- **table_segment_uid:** `TSEG-2f2f41954e9b7a03`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/739`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=5']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Efectivo y equivalentes de efectivo - 30 de septiembre de 2025 / Nivel 1 - miles de ARS - valor 66.422.698 - pagina 42   [confianza: media]
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Efectivo y equivalentes de efectivo - 30 de septiembre de 2025 / Total - miles de ARS - valor 66.422.698 - pagina 42   [confianza: media]
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Activos financieros corrientes a valor razonable con cambios en resultado - 30 de septiembre de 2025 / Nivel 1 - miles de ARS - valor 430.437.002 - pagina 42   [confianza: media]
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Activos financieros corrientes a valor razonable con cambios en resultado - 30 de septiembre de 2025 / Total - miles de ARS - valor 430.437.002 - pagina 42   [confianza: media]
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Total - 30 de septiembre de 2025 / Nivel 1 - miles de ARS - valor 496.859.700 - pagina 42   [confianza: media]
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Total - 30 de septiembre de 2025 / Total - miles de ARS - valor 496.859.700 - pagina 42   [confianza: media]
```

### `#/tables/58`

- **procedencia:** paginas [42]
- **table_uid:** `TBL-82299295396f7c88`
- **table_segment_uid:** `TSEG-82299295396f7c88`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:42->42']

**DESPUES** — hechos recuperables (2 en total, se muestran 2):

```text
TGS_EEFF_2025_09 - ON 2031 - (periodo no declarado) - (unidad no declarada) - valor 673.115.462 - pagina 42   [confianza: media]
TGS_EEFF_2025_09 - ON 2031 - (periodo no declarado) - (unidad no declarada) - valor 798.046.101 - pagina 42   [confianza: media]
```

### `#/tables/59`

- **procedencia:** paginas [43]
- **table_uid:** `TBL-a222a8f6e41e60b1`
- **table_segment_uid:** `TSEG-a222a8f6e41e60b1`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `celda_encabezado`, evidencia `r1c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=8']

**DESPUES** — hechos recuperables (75 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Efectivo y equivalentes de efectivo - al 2025-09-30 - miles de ARS - valor 12.403 - pagina 43   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Efectivo y equivalentes de efectivo - al 2025-09-30 - miles de ARS - valor 1.371,00 (1) - pagina 43   [confianza: baja]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Efectivo y equivalentes de efectivo - al 2025-09-30 - miles de ARS - valor 17.003.996 - pagina 43   [confianza: alta]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Efectivo y equivalentes de efectivo - al 2024-12-31 - miles de ARS - valor 40.373 - pagina 43   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Efectivo y equivalentes de efectivo - al 2024-12-31 - miles de ARS - valor 50.664.978 - pagina 43   [confianza: alta]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - al 2025-09-30 - miles de ARS - valor 271.253 - pagina 43   [confianza: media]
```

### `#/tables/60`

- **procedencia:** paginas [45]
- **table_uid:** `TBL-e51ffe8a1e8ea477`
- **table_segment_uid:** `TSEG-e51ffe8a1e8ea477`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:43->45']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Clases de Acciones - Clase “A” - (periodo no declarado) - (unidad no declarada) - valor 405.192.594 - pagina 45   [confianza: media]
TGS_EEFF_2025_09 - Clases de Acciones - Clase “A” - (periodo no declarado) - (unidad no declarada) - valor 405.192.594 - pagina 45   [confianza: media]
TGS_EEFF_2025_09 - Clases de Acciones - Clase “B” - (periodo no declarado) - (unidad no declarada) - valor 347.568.464 - pagina 45   [confianza: media]
TGS_EEFF_2025_09 - Clases de Acciones - Clase “B” - (periodo no declarado) - (unidad no declarada) - valor 41.734.225 - pagina 45   [confianza: media]
TGS_EEFF_2025_09 - Clases de Acciones - Clase “B” - (periodo no declarado) - (unidad no declarada) - valor 389.302.689 - pagina 45   [confianza: media]
TGS_EEFF_2025_09 - Clases de Acciones - Total - (periodo no declarado) - (unidad no declarada) - valor 752.761.058 - pagina 45   [confianza: media]
```

### `#/tables/61`

- **procedencia:** paginas [46]
- **table_uid:** `TBL-46d9153b744a92fa`
- **table_segment_uid:** `TSEG-46d9153b744a92fa`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/813`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[0],inferido=[0, 1]']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=2']

**DESPUES** — hechos recuperables (3 en total, se muestran 3):

```text
TGS_EEFF_2025_09 - Clase “A” - Al 30 de septiembre de 2025 / Monto suscripto, integrado y autorizado a la oferta pública - miles de ARS - valor 405.192.594 - pagina 46   [confianza: media]
TGS_EEFF_2025_09 - Clase “B” - Al 30 de septiembre de 2025 / Monto suscripto, integrado y autorizado a la oferta pública - miles de ARS - valor 347.568.464 - pagina 46   [confianza: media]
TGS_EEFF_2025_09 - Total - Al 30 de septiembre de 2025 / Monto suscripto, integrado y autorizado a la oferta pública - miles de ARS - valor 752.761.058 - pagina 46   [confianza: media]
```

### `#/tables/62`

- **procedencia:** paginas [47]
- **table_uid:** `TBL-2fee06dc72a5a309`
- **table_segment_uid:** `TSEG-2fee06dc72a5a309`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:2!=5']

**DESPUES** — hechos recuperables (19 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Controlante: / CIESA - al 2025-09-30 - (unidad no declarada) - valor 31 - pagina 47   [confianza: media]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía (1) - al 2025-09-30 - (unidad no declarada) - valor 25.509.070 - pagina 47   [confianza: media]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía (1) - al 2025-09-30 - (unidad no declarada) - valor 22.337.857 - pagina 47   [confianza: media]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía (1) - al 2024-12-31 - (unidad no declarada) - valor 16.112.034 - pagina 47   [confianza: media]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía (1) - al 2024-12-31 - (unidad no declarada) - valor 26.673.720 - pagina 47   [confianza: media]
TGS_EEFF_2025_09 - Entes sobre los que se ejerce influencia significativa: / Link - al 2025-09-30 - (unidad no declarada) - valor 39.118 - pagina 47   [confianza: media]
```

### `#/tables/63`

- **procedencia:** paginas [53]
- **table_uid:** `TBL-5742cdfd42428450`
- **table_segment_uid:** `TSEG-5742cdfd42428450`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:47->53']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/64`

- **procedencia:** paginas [56]
- **table_uid:** `TBL-3433d8333affc770`
- **table_segment_uid:** `TSEG-3433d8333affc770`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/1218`)
- **extraction_warnings:** ['nota:encabezado_discrepa_con_parser:parser=[],inferido=[0]', 'escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:53->56']

**DESPUES** — hechos recuperables (3 en total, se muestran 3):

```text
TGS_EEFF_2025_09 - Clases de Acciones Acciones ordinarias y escriturales de valor nominal 1, de 1 voto: - Clase “A” - (periodo no declarado) - ARS - valor 405.192.594 - pagina 56   [confianza: media]
TGS_EEFF_2025_09 - Clases de Acciones Acciones ordinarias y escriturales de valor nominal 1, de 1 voto: - Clase “B” - (periodo no declarado) - ARS - valor 347.568.464 - pagina 56   [confianza: media]
TGS_EEFF_2025_09 - Clases de Acciones Acciones ordinarias y escriturales de valor nominal 1, de 1 voto: - Total - (periodo no declarado) - ARS - valor 752.761.058 - pagina 56   [confianza: media]
```

### `#/tables/65`

- **procedencia:** paginas [56]
- **table_uid:** `TBL-2e9be9a9672e78e1`
- **table_segment_uid:** `TSEG-2e9be9a9672e78e1`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:56->56']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/66`

- **procedencia:** paginas [56]
- **table_uid:** `TBL-fffa8dcfe1df0592`
- **table_segment_uid:** `TSEG-fffa8dcfe1df0592`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:56->56']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/67`

- **procedencia:** paginas [57]
- **table_uid:** `TBL-fa3644ca25562c34`
- **table_segment_uid:** `TSEG-fa3644ca25562c34`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/1222`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=6']

**DESPUES** — hechos recuperables (78 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Ingresos por ventas y otros - Por los períodos de tres meses terminados el 30 de septiembre de / 2025 - miles de ARS - valor 425.090.727 - pagina 57   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas y otros - Por los períodos de tres meses terminados el 30 de septiembre de / 2024 - miles de ARS - valor 336.536.442 - pagina 57   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas y otros - Por los períodos de nueve meses terminados el 30 de septiembre de / 2025 - miles de ARS - valor 1.151.907.520 - pagina 57   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas y otros - Por los períodos de nueve meses terminados el 30 de septiembre de / 2024 - miles de ARS - valor 1.057.958.417 - pagina 57   [confianza: media]
TGS_EEFF_2025_09 - Costo de ventas netas - Por los períodos de tres meses terminados el 30 de septiembre de / 2025 - miles de ARS - valor (203.227.446) - pagina 57   [confianza: media]
TGS_EEFF_2025_09 - Costo de ventas netas - Por los períodos de tres meses terminados el 30 de septiembre de / 2024 - miles de ARS - valor (165.425.601) - pagina 57   [confianza: media]
```

### `#/tables/68`

- **procedencia:** paginas [57]
- **table_uid:** `TBL-8b450760700f3d4c`
- **table_segment_uid:** `TSEG-8b450760700f3d4c`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:57->57']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/69`

- **procedencia:** paginas [58]
- **table_uid:** `TBL-d30e16a768af383a`
- **table_segment_uid:** `TSEG-d30e16a768af383a`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/1230`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:2!=4']

**DESPUES** — hechos recuperables (76 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Propiedad, planta y equipos - (periodo no declarado) - miles de ARS - valor 7 - pagina 58   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Propiedad, planta y equipos - al 2025-09-30 - miles de ARS - valor 2.913.180.409 - pagina 58   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Propiedad, planta y equipos - al 2024-12-31 - miles de ARS - valor 2.908.480.272 - pagina 58   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Inversiones en compañías subsidiarias y asociadas - (periodo no declarado) - miles de ARS - valor 5 - pagina 58   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Inversiones en compañías subsidiarias y asociadas - al 2025-09-30 - miles de ARS - valor 14.737.872 - pagina 58   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO - Activo no corriente / Inversiones en compañías subsidiarias y asociadas - al 2024-12-31 - miles de ARS - valor 12.464.139 - pagina 58   [confianza: media]
```

### `#/tables/70`

- **procedencia:** paginas [59]
- **table_uid:** `TBL-11f090836d098e13`
- **table_segment_uid:** `TSEG-11f090836d098e13`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/1242`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=13']

**DESPUES** — hechos recuperables (73 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor 752.761 - pagina 59   [confianza: media]
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor 899.934.947 - pagina 59   [confianza: media]
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor 41.734 - pagina 59   [confianza: media]
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor 49.893.494 - pagina 59   [confianza: media]
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor (90.347.853) - pagina 59   [confianza: media]
TGS_EEFF_2025_09 - Saldos al 31 de diciembre de 2023 - (periodo no declarado) - miles de ARS - valor (26.209.113) - pagina 59   [confianza: media]
```

### `#/tables/71`

- **procedencia:** paginas [59]
- **table_uid:** `TBL-cfadecc1c509cdd0`
- **table_segment_uid:** `TSEG-cfadecc1c509cdd0`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['tabla_sin_valores_numericos']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:59->59']

**DESPUES** — hechos recuperables (0 en total, se muestran 0):

```text
```

### `#/tables/72`

- **procedencia:** paginas [60]
- **table_uid:** `TBL-1496e974640781e3`
- **table_segment_uid:** `TSEG-1496e974640781e3`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/1248`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=3']

**DESPUES** — hechos recuperables (69 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - generado por las operaciones: / Depreciación de propiedad, planta y equipos - 2025 - miles de ARS - valor 139.262.695 - pagina 60   [confianza: media]
TGS_EEFF_2025_09 - generado por las operaciones: / Depreciación de propiedad, planta y equipos - 2024 - miles de ARS - valor 116.599.475 - pagina 60   [confianza: media]
TGS_EEFF_2025_09 - generado por las operaciones: / Baja de propiedad, planta y equipos - 2025 - miles de ARS - valor 4.939.697 - pagina 60   [confianza: media]
TGS_EEFF_2025_09 - generado por las operaciones: / Baja de propiedad, planta y equipos - 2024 - miles de ARS - valor 2.369.834 - pagina 60   [confianza: media]
TGS_EEFF_2025_09 - generado por las operaciones: / Deterioro de Propiedad, planta y equipos por evento climático - 2025 - miles de ARS - valor 3.856.661 - pagina 60   [confianza: media]
TGS_EEFF_2025_09 - generado por las operaciones: / Resultado inversiones en asociadas y subsidiarias - 2025 - miles de ARS - valor (2.273.733) - pagina 60   [confianza: media]
```

### `#/tables/73`

- **procedencia:** paginas [63]
- **table_uid:** `TBL-66e2a26b173e1f7e`
- **table_segment_uid:** `TSEG-66e2a26b173e1f7e`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/1300`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:60->63']

**DESPUES** — hechos recuperables (25 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Ingresos por ventas Ventas intersegmentos - (periodo no declarado) - ARS - valor 488.347.655 20.358.180 - pagina 63   [confianza: baja]
TGS_EEFF_2025_09 - Costo de ventas - (periodo no declarado) - ARS - valor (244.724.157) - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Costo de ventas - (periodo no declarado) - ARS - valor (95.460.719) - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Costo de ventas - (periodo no declarado) - ARS - valor (20.358.180) 20.358.180 - pagina 63   [confianza: baja]
TGS_EEFF_2025_09 - Costo de ventas - (periodo no declarado) - ARS - valor (529.299.946) - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Gastos de administración - (periodo no declarado) - ARS - valor (209.473.250) (27.600.949) - pagina 63   [confianza: baja]
```

### `#/tables/74`

- **procedencia:** paginas [63]
- **table_uid:** `TBL-0f7748d60c7f1012`
- **table_segment_uid:** `TSEG-0f7748d60c7f1012`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:63->63']

**DESPUES** — hechos recuperables (31 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Ingresos por ventas - (periodo no declarado) - (unidad no declarada) - valor 374.641.517 - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - (periodo no declarado) - (unidad no declarada) - valor 485.135.701 - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - (periodo no declarado) - (unidad no declarada) - valor 198.181.199 - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Ingresos por ventas - (periodo no declarado) - (unidad no declarada) - valor 1.057.958.417 - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Ventas intersegmentos - (periodo no declarado) - (unidad no declarada) - valor 9.671.377 - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Ventas intersegmentos - (periodo no declarado) - (unidad no declarada) - valor (9.671.377) - pagina 63   [confianza: media]
```

### `#/tables/75`

- **procedencia:** paginas [63]
- **table_uid:** `TBL-0fcd3037b42d3ae8`
- **table_segment_uid:** `TSEG-0fcd3037b42d3ae8`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:63->63']

**DESPUES** — hechos recuperables (20 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2025 - Por mercado / Mercado externo - Período de nueve meses terminado el 30 de septiembre de 2025 / Producción y comercialización de Líquidos - (unidad no declarada) - valor 169.414.218 - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2025 - Por mercado / Mercado externo - Período de nueve meses terminado el 30 de septiembre de 2025 / Total - (unidad no declarada) - valor 169.414.218 - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2025 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2025 / Transporte de Gas Natural - (unidad no declarada) - valor 488.347.655 - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2025 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2025 / Producción y comercialización de Líquidos - (unidad no declarada) - valor 248.206.242 - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2025 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2025 / Midstream - (unidad no declarada) - valor 234.356.303 - pagina 63   [confianza: media]
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2025 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2025 / Total - (unidad no declarada) - valor 970.910.200 - pagina 63   [confianza: media]
```

### `#/tables/76`

- **procedencia:** paginas [64]
- **table_uid:** `TBL-27b5d50862fea4a4`
- **table_segment_uid:** `TSEG-27b5d50862fea4a4`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/1316`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0, 1]']

**DESPUES** — hechos recuperables (20 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2024 - Por mercado / Mercado externo - Período de nueve meses terminado el 30 de septiembre de 2024 / Producción y comercialización de Líquidos - ARS - valor 209.067.926 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2024 - Por mercado / Mercado externo - Período de nueve meses terminado el 30 de septiembre de 2024 / Total - ARS - valor 209.067.926 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2024 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2024 / Transporte de Gas Natural - ARS - valor 374.641.517 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2024 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2024 / Producción y comercialización de Líquidos - ARS - valor 261.650.573 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2024 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2024 / Midstream - ARS - valor 198.181.199 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Período de nueve meses terminado el 30 de septiembre de 2024 - Por mercado / Mercado local - Período de nueve meses terminado el 30 de septiembre de 2024 / Total - ARS - valor 834.473.289 - pagina 64   [confianza: media]
```

### `#/tables/77`

- **procedencia:** paginas [64]
- **table_uid:** `TBL-dee186eebd0dd807`
- **table_segment_uid:** `TSEG-dee186eebd0dd807`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:64->64']

**DESPUES** — hechos recuperables (22 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Saldo a favor Impuesto a los Ingresos Brutos - al 2024-12-31 - (unidad no declarada) - valor 129.308 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Saldo a favor IVA - al 2024-12-31 - (unidad no declarada) - valor 1.954.230 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Otros créditos impositivos - al 2025-09-30 - (unidad no declarada) - valor 3.929.578 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Otros créditos impositivos - al 2024-12-31 - (unidad no declarada) - valor 733.755 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Gastos pagados por adelantado - al 2025-09-30 - (unidad no declarada) - valor 2.367.483 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Gastos pagados por adelantado - al 2024-12-31 - (unidad no declarada) - valor 7.917.062 - pagina 64   [confianza: media]
```

### `#/tables/78`

- **procedencia:** paginas [64]
- **table_uid:** `TBL-d76eb75e166b22b2`
- **table_segment_uid:** `TSEG-d76eb75e166b22b2`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:64->64']

**DESPUES** — hechos recuperables (20 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Con terceros - al 2025-09-30 - (unidad no declarada) - valor 168.865.523 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Con terceros - al 2024-12-31 - (unidad no declarada) - valor 173.518.715 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2025-09-30 - (unidad no declarada) - valor 75.690.497 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2024-12-31 - (unidad no declarada) - valor 76.767.234 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Producción y Comercialización de Líquidos - al 2025-09-30 - (unidad no declarada) - valor 40.029.196 - pagina 64   [confianza: media]
TGS_EEFF_2025_09 - Producción y Comercialización de Líquidos - al 2024-12-31 - (unidad no declarada) - valor 55.637.047 - pagina 64   [confianza: media]
```

### `#/tables/79`

- **procedencia:** paginas [65]
- **table_uid:** `TBL-4ba6546fc904f219`
- **table_segment_uid:** `TSEG-4ba6546fc904f219`
- **continuation_of:** —
- **banda de encabezado inferida:** ninguna
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/1331`)
- **extraction_warnings:** ['escala_ausente', 'sin_encabezado_propio', 'continuacion_huerfana:ancho_distinto:3!=2', 'sin_encabezado_recuperable']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=2']

**DESPUES** — hechos recuperables (8 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Saldos al 31/12/2023 - (periodo no declarado) - ARS - valor 801.423 - pagina 65   [confianza: baja]
TGS_EEFF_2025_09 - Efecto RECPAM - (periodo no declarado) - ARS - valor (403.588) - pagina 65   [confianza: baja]
TGS_EEFF_2025_09 - Saldos al 30/09/2024 - (periodo no declarado) - ARS - valor 397.835 - pagina 65   [confianza: baja]
TGS_EEFF_2025_09 - Efecto RECPAM - (periodo no declarado) - ARS - valor (29.811) - pagina 65   [confianza: baja]
TGS_EEFF_2025_09 - Saldos al 31/12/2024 - (periodo no declarado) - ARS - valor 368.024 - pagina 65   [confianza: baja]
TGS_EEFF_2025_09 - Efecto RECPAM - (periodo no declarado) - ARS - valor (538.227) - pagina 65   [confianza: baja]
```

### `#/tables/80`

- **procedencia:** paginas [65]
- **table_uid:** `TBL-b3a82a754e51ec4a`
- **table_segment_uid:** `TSEG-b3a82a754e51ec4a`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:65->65']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Caja y bancos - al 2025-09-30 - (unidad no declarada) - valor 6.125.196 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Caja y bancos - al 2024-12-31 - (unidad no declarada) - valor 51.042.033 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Caja y bancos UT - al 2025-09-30 - (unidad no declarada) - valor 1.933 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Caja y bancos UT - al 2024-12-31 - (unidad no declarada) - valor 286 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Fondos comunes en mercado local - al 2025-09-30 - (unidad no declarada) - valor 65.326.237 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Fondos comunes en mercado local - al 2024-12-31 - (unidad no declarada) - valor 20.925.979 - pagina 65   [confianza: media]
```

### `#/tables/81`

- **procedencia:** paginas [65]
- **table_uid:** `TBL-0db4cb96183d600b`
- **table_segment_uid:** `TSEG-0db4cb96183d600b`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:65->65']

**DESPUES** — hechos recuperables (15 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2025-09-30 - (unidad no declarada) - valor 2.984.597 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2025-09-30 - (unidad no declarada) - valor 40.602.613 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2024-12-31 - (unidad no declarada) - valor 2.984.597 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Transporte de Gas Natural - al 2024-12-31 - (unidad no declarada) - valor 42.841.220 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Producción y Comercialización de Líquidos - al 2024-12-31 - (unidad no declarada) - valor 872.410 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Midstream - al 2025-09-30 - (unidad no declarada) - valor 5.120.562 - pagina 65   [confianza: media]
```

### `#/tables/82`

- **procedencia:** paginas [65]
- **table_uid:** `TBL-39b7d30460612f11`
- **table_segment_uid:** `TSEG-39b7d30460612f11`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:65->65']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Provisión honorarios a directores y síndicos - al 2025-09-30 - (unidad no declarada) - valor 232.983 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Provisión honorarios a directores y síndicos - al 2024-12-31 - (unidad no declarada) - valor 290.103 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Otros - al 2025-09-30 - (unidad no declarada) - valor 212 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Otros - al 2024-12-31 - (unidad no declarada) - valor 332 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Total - al 2025-09-30 - (unidad no declarada) - valor 233.195 - pagina 65   [confianza: media]
TGS_EEFF_2025_09 - Total - al 2024-12-31 - (unidad no declarada) - valor 290.435 - pagina 65   [confianza: media]
```

### `#/tables/83`

- **procedencia:** paginas [66]
- **table_uid:** `TBL-1f1734a7b043d04c`
- **table_segment_uid:** `TSEG-1f1734a7b043d04c`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/1346`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0]']

**DESPUES** — hechos recuperables (12 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Tasa de seguridad e higiene - al 2025-09-30 - ARS - valor 408.836 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Tasa de seguridad e higiene - al 2024-12-31 - ARS - valor 343.353 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Retenciones y percepciones efectuadas a terceros - al 2025-09-30 - ARS - valor 6.491.559 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Retenciones y percepciones efectuadas a terceros - al 2024-12-31 - ARS - valor 7.373.488 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a los ingresos brutos a pagar - al 2025-09-30 - ARS - valor 2.550.414 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a los ingresos brutos a pagar - al 2024-12-31 - ARS - valor 2.481.416 - pagina 66   [confianza: media]
```

### `#/tables/84`

- **procedencia:** paginas [66]
- **table_uid:** `TBL-34cec794555864ff`
- **table_segment_uid:** `TSEG-34cec794555864ff`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:66->66']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Proveedores comunes - al 2025-09-30 - (unidad no declarada) - valor 62.445.170 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Proveedores comunes - al 2024-12-31 - (unidad no declarada) - valor 65.552.410 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Proveedores comunes UT - al 2025-09-30 - (unidad no declarada) - valor 1.129.914 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Proveedores comunes UT - al 2024-12-31 - (unidad no declarada) - valor 1.313.182 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Saldos acreedores de clientes - al 2025-09-30 - (unidad no declarada) - valor 1.498.737 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Saldos acreedores de clientes - al 2024-12-31 - (unidad no declarada) - valor 72.296 - pagina 66   [confianza: media]
```

### `#/tables/85`

- **procedencia:** paginas [66]
- **table_uid:** `TBL-d00e19bfd69c8fa4`
- **table_segment_uid:** `TSEG-d00e19bfd69c8fa4`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:66->66']

**DESPUES** — hechos recuperables (12 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Venta de bienes y servicios - Período de tres meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 419.989.381 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Venta de bienes y servicios - Período de tres meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 330.577.048 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Venta de bienes y servicios - Período de nueve meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 1.140.324.418 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Venta de bienes y servicios - Período de nueve meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 1.043.541.215 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Subsidios - Período de tres meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 5.101.346 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Subsidios - Período de tres meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 5.959.394 - pagina 66   [confianza: media]
```

### `#/tables/86`

- **procedencia:** paginas [66]
- **table_uid:** `TBL-9eebf1e53d5c78b2`
- **table_segment_uid:** `TSEG-9eebf1e53d5c78b2`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:66->66']

**DESPUES** — hechos recuperables (20 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Existencia al inicio - Período de tres meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 12.983.606 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Existencia al inicio - Período de tres meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 18.821.244 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Existencia al inicio - Período de nueve meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 4.469.295 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Existencia al inicio - Período de nueve meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 20.367.601 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Compras - Período de tres meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 88.696.588 - pagina 66   [confianza: media]
TGS_EEFF_2025_09 - Compras - Período de tres meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 49.369.520 - pagina 66   [confianza: media]
```

### `#/tables/87`

- **procedencia:** paginas [67]
- **table_uid:** `TBL-e0a0c149c7777529`
- **table_segment_uid:** `TSEG-e0a0c149c7777529`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/1359`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:5!=9']

**DESPUES** — hechos recuperables (121 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - (periodo no declarado) - ARS - valor 93.854.918 - pagina 67   [confianza: media]
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - (periodo no declarado) - ARS - valor 40.444.575 - pagina 67   [confianza: media]
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - (periodo no declarado) - ARS - valor 32.372.123 - pagina 67   [confianza: media]
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - (periodo no declarado) - ARS - valor 16.344.248 - pagina 67   [confianza: media]
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - (periodo no declarado) - ARS - valor 4.693.972 - pagina 67   [confianza: media]
TGS_EEFF_2025_09 - Remuneraciones y otros beneficios al personal - (periodo no declarado) - ARS - valor 90.189.100 - pagina 67   [confianza: media]
```

### `#/tables/88`

- **procedencia:** paginas [68]
- **table_uid:** `TBL-4d9a40191df00887`
- **table_segment_uid:** `TSEG-4d9a40191df00887`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/1371`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:9!=5']

**DESPUES** — hechos recuperables (44 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Ingresos Financieros / Intereses - Período de tres meses terminado el 30 de septiembre de / 2025 - ARS - valor 6.500.985 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Ingresos Financieros / Intereses - Período de tres meses terminado el 30 de septiembre de / 2024 - ARS - valor 23.915.898 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Ingresos Financieros / Intereses - Período de nueve meses terminado el 30 de septiembre de / 2025 - ARS - valor 22.155.212 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Ingresos Financieros / Intereses - Período de nueve meses terminado el 30 de septiembre de / 2024 - ARS - valor 64.217.464 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Ingresos Financieros / Diferencia de cambio - Período de tres meses terminado el 30 de septiembre de / 2025 - ARS - valor 61.832.150 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Ingresos Financieros / Diferencia de cambio - Período de tres meses terminado el 30 de septiembre de / 2024 - ARS - valor 25.740.984 - pagina 68   [confianza: media]
```

### `#/tables/89`

- **procedencia:** paginas [68]
- **table_uid:** `TBL-06bc7873f7499d5b`
- **table_segment_uid:** `TSEG-06bc7873f7499d5b`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:68->68']

**DESPUES** — hechos recuperables (28 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Evento climático (1) - Período de tres meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor (10.280.737) - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Evento climático (1) - Período de nueve meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor (45.738.029) - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Resultado por baja de Propiedad, planta y equipos - Período de tres meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 27 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Resultado por baja de Propiedad, planta y equipos - Período de tres meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 121.084 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Resultado por baja de Propiedad, planta y equipos - Período de nueve meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 162.034 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Resultado por baja de Propiedad, planta y equipos - Período de nueve meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor (1.378.110) - pagina 68   [confianza: media]
```

### `#/tables/90`

- **procedencia:** paginas [68]
- **table_uid:** `TBL-743e487ef46314f8`
- **table_segment_uid:** `TSEG-743e487ef46314f8`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:68->68']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Plazo fijo en moneda extranjera - al 2025-09-30 - (unidad no declarada) - valor 330.889.750 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Plazo fijo en moneda extranjera - al 2024-12-31 - (unidad no declarada) - valor 293.466.141 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Otras colocaciones a plazo - al 2025-09-30 - (unidad no declarada) - valor 40.997.499 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Otras colocaciones a plazo - al 2024-12-31 - (unidad no declarada) - valor 37.775.605 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Total - al 2025-09-30 - (unidad no declarada) - valor 371.887.249 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Total - al 2024-12-31 - (unidad no declarada) - valor 331.241.746 - pagina 68   [confianza: media]
```

### `#/tables/91`

- **procedencia:** paginas [68]
- **table_uid:** `TBL-8a37e7d775cfa79f`
- **table_segment_uid:** `TSEG-8a37e7d775cfa79f`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:68->68']

**DESPUES** — hechos recuperables (10 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Títulos de deuda privada partes relacionadas - al 2025-09-30 - (unidad no declarada) - valor 14.783.377 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Títulos de deuda privada partes relacionadas - al 2024-12-31 - (unidad no declarada) - valor 24.966.043 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Títulos de deuda privada - al 2025-09-30 - (unidad no declarada) - valor 253.537.566 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Títulos de deuda privada - al 2024-12-31 - (unidad no declarada) - valor 236.323.899 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Títulos de deuda pública - al 2025-09-30 - (unidad no declarada) - valor 119.856.591 - pagina 68   [confianza: media]
TGS_EEFF_2025_09 - Títulos de deuda pública - al 2024-12-31 - (unidad no declarada) - valor 238.432.421 - pagina 68   [confianza: media]
```

### `#/tables/92`

- **procedencia:** paginas [69]
- **table_uid:** `TBL-1f6493cabef19b9a`
- **table_segment_uid:** `TSEG-1f6493cabef19b9a`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/1392`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0]']

**DESPUES** — hechos recuperables (11 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Provisión vacaciones - al 2025-09-30 - miles de ARS - valor 9.596.352 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Provisión vacaciones - al 2024-12-31 - miles de ARS - valor 10.527.059 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Provisión sueldo anual complementario - al 2025-09-30 - miles de ARS - valor 1.860.737 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Gratificaciones a pagar - al 2025-09-30 - miles de ARS - valor 6.252.930 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Gratificaciones a pagar - al 2024-12-31 - miles de ARS - valor 8.347.526 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Cargas sociales a pagar - al 2025-09-30 - miles de ARS - valor 3.224.379 - pagina 69   [confianza: media]
```

### `#/tables/93`

- **procedencia:** paginas [69]
- **table_uid:** `TBL-b165e503bebc4cc6`
- **table_segment_uid:** `TSEG-b165e503bebc4cc6`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:69->69']

**DESPUES** — hechos recuperables (12 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Telcosur S.A. - al 2025-09-30 - (unidad no declarada) - valor $1 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Telcosur S.A. - al 2025-09-30 - (unidad no declarada) - valor 4.421.942 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Telcosur S.A. - al 2025-09-30 - (unidad no declarada) - valor 2.501.779 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Telcosur S.A. - al 2025-09-30 - (unidad no declarada) - valor 12.141.816 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Telcosur S.A. - al 2024-12-31 - (unidad no declarada) - valor 10.969.786 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Gas Link S.A. - al 2025-09-30 - (unidad no declarada) - valor $1 - pagina 69   [confianza: media]
```

### `#/tables/94`

- **procedencia:** paginas [69]
- **table_uid:** `TBL-2188c04ca6d89b9b`
- **table_segment_uid:** `TSEG-2188c04ca6d89b9b`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:69->69']

**DESPUES** — hechos recuperables (16 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Telcosur - Período de tres meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 715.811 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Telcosur - Período de tres meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 728.786 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Telcosur - Período de nueve meses terminado el 30 de septiembre de / 2025 - (unidad no declarada) - valor 1.172.030 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Telcosur - Período de nueve meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor (1.558.823) - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - TGU (liquidada) - Período de tres meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor (7.202) - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - TGU (liquidada) - Período de nueve meses terminado el 30 de septiembre de / 2024 - (unidad no declarada) - valor 12.831 - pagina 69   [confianza: media]
```

### `#/tables/95`

- **procedencia:** paginas [69]
- **table_uid:** `TBL-9e5c9f94a6f825a0`
- **table_segment_uid:** `TSEG-9e5c9f94a6f825a0`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:69->69']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Saldo al inicio del ejercicio - al 2025-09-30 - (unidad no declarada) - valor 12.464.139 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Saldo al inicio del ejercicio - al 2024-12-31 - (unidad no declarada) - valor 13.372.758 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Resultados - al 2025-09-30 - (unidad no declarada) - valor 2.273.733 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Resultados - al 2024-12-31 - (unidad no declarada) - valor (908.619) - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Saldo al cierre del período - al 2025-09-30 - (unidad no declarada) - valor 14.737.872 - pagina 69   [confianza: media]
TGS_EEFF_2025_09 - Saldo al cierre del período - al 2024-12-31 - (unidad no declarada) - valor 12.464.139 - pagina 69   [confianza: media]
```

### `#/tables/96`

- **procedencia:** paginas [70]
- **table_uid:** `TBL-a929a2196957e20b`
- **table_segment_uid:** `TSEG-a929a2196957e20b`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1, 2]
- **unidad:** ARS (origen `texto_adyacente`, evidencia `#/texts/1412`)
- **extraction_warnings:** ['escala_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=14']

**DESPUES** — hechos recuperables (213 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Gasoductos - (periodo no declarado) - ARS - valor 2.256.018.551 - pagina 70   [confianza: media]
TGS_EEFF_2025_09 - Gasoductos - (periodo no declarado) - ARS - valor 8.927.026 - pagina 70   [confianza: media]
TGS_EEFF_2025_09 - Gasoductos - Al cierre del período - ARS - valor 2.264.945.577 - pagina 70   [confianza: media]
TGS_EEFF_2025_09 - Gasoductos - al 2025-09-30 - ARS - valor 1.318.547.153 - pagina 70   [confianza: media]
TGS_EEFF_2025_09 - Gasoductos - (periodo no declarado) - ARS - valor 44.392.706 - pagina 70   [confianza: media]
TGS_EEFF_2025_09 - Gasoductos - (periodo no declarado) - porcentaje - valor 2,2 - pagina 70   [confianza: media]
```

### `#/tables/97`

- **procedencia:** paginas [71]
- **table_uid:** `TBL-02c18573a0cd0fbc`
- **table_segment_uid:** `TSEG-02c18573a0cd0fbc`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/1424`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:14!=3']

**DESPUES** — hechos recuperables (19 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Deudas financieras corrientes / Intereses ON 2031 - al 2025-09-30 - miles de ARS - valor 10.537.450 - pagina 71   [confianza: media]
TGS_EEFF_2025_09 - Deudas financieras corrientes / Intereses ON 2031 - al 2024-12-31 - miles de ARS - valor 22.715.218 - pagina 71   [confianza: media]
TGS_EEFF_2025_09 - Deudas financieras corrientes / Préstamos bancarios - al 2025-09-30 - miles de ARS - valor 62.705.650 - pagina 71   [confianza: media]
TGS_EEFF_2025_09 - Deudas financieras corrientes / Préstamos bancarios - al 2024-12-31 - miles de ARS - valor 32.735.702 - pagina 71   [confianza: media]
TGS_EEFF_2025_09 - Deudas financieras corrientes / Préstamos partes relacionadas (Nota 13) - al 2025-09-30 - miles de ARS - valor 31.875.681 - pagina 71   [confianza: media]
TGS_EEFF_2025_09 - Deudas financieras corrientes / Préstamos partes relacionadas (Nota 13) - al 2024-12-31 - miles de ARS - valor 28.841.156 - pagina 71   [confianza: media]
```

### `#/tables/98`

- **procedencia:** paginas [71]
- **table_uid:** `TBL-ab9500a5b36558a1`
- **table_segment_uid:** `TSEG-ab9500a5b36558a1`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:71->71']

**DESPUES** — hechos recuperables (30 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Saldo inicial - al 2025-09-30 - (unidad no declarada) - valor 17.045.878 - pagina 71   [confianza: media]
TGS_EEFF_2025_09 - Saldo inicial - al 2025-09-30 - (unidad no declarada) - valor 688.633.780 - pagina 71   [confianza: media]
TGS_EEFF_2025_09 - Saldo inicial - al 2024-09-30 - (unidad no declarada) - valor 45.721.862 - pagina 71   [confianza: media]
TGS_EEFF_2025_09 - Saldo inicial - al 2024-09-30 - (unidad no declarada) - valor 1.153.914.177 - pagina 71   [confianza: media]
TGS_EEFF_2025_09 - Efecto RECPAM - al 2025-09-30 - (unidad no declarada) - valor (6.152.929) - pagina 71   [confianza: media]
TGS_EEFF_2025_09 - Efecto RECPAM - al 2025-09-30 - (unidad no declarada) - valor (136.248.181) - pagina 71   [confianza: media]
```

### `#/tables/99`

- **procedencia:** paginas [72]
- **table_uid:** `TBL-0190e0d55a0d2963`
- **table_segment_uid:** `TSEG-0190e0d55a0d2963`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/1444`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:5!=8']

**DESPUES** — hechos recuperables (19 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - ON 2031 - A vencer / Del 01/10/2029 en adelante - miles de ARS - valor 662.578.012 - pagina 72   [confianza: media]
TGS_EEFF_2025_09 - ON 2031 - (periodo no declarado) - miles de ARS - valor 662.578.012 - pagina 72   [confianza: media]
TGS_EEFF_2025_09 - Intereses ON 2031 - al 2026-09-30 - miles de ARS - valor 10.537.450 - pagina 72   [confianza: media]
TGS_EEFF_2025_09 - Intereses ON 2031 - (periodo no declarado) - miles de ARS - valor 10.537.450 - pagina 72   [confianza: media]
TGS_EEFF_2025_09 - Pasivos por arrendamiento - al 2026-09-30 - miles de ARS - valor 10.533.390 - pagina 72   [confianza: media]
TGS_EEFF_2025_09 - Pasivos por arrendamiento - A vencer / Del 1/10/2026 al 30/09/2027 - miles de ARS - valor 1.134.816 - pagina 72   [confianza: media]
```

### `#/tables/100`

- **procedencia:** paginas [72]
- **table_uid:** `TBL-902a954e96607a84`
- **table_segment_uid:** `TSEG-902a954e96607a84`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** miles (origen `celda_encabezado`, evidencia `r0c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:72->72']

**DESPUES** — hechos recuperables (1 en total, se muestran 1):

```text
TGS_EEFF_2025_09 - Moneda - US$ - (periodo no declarado) - miles - valor 67.860.951 - pagina 72   [confianza: media]
```

### `#/tables/101`

- **procedencia:** paginas [73]
- **table_uid:** `TBL-6fc2db3901ae8ce6`
- **table_segment_uid:** `TSEG-6fc2db3901ae8ce6`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/1465`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:4!=5']

**DESPUES** — hechos recuperables (12 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Impuesto a las ganancias - corriente - Período de tres meses terminado el 30 de septiembre de / 2025 - miles de ARS - valor (56.315.899) - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a las ganancias - corriente - Período de tres meses terminado el 30 de septiembre de / 2024 - miles de ARS - valor (32.168.883) - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a las ganancias - corriente - Período de nueve meses terminado el 30 de septiembre de / 2025 - miles de ARS - valor (152.466.269) - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a las ganancias - corriente - Período de nueve meses terminado el 30 de septiembre de / 2024 - miles de ARS - valor (201.732.598) - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a las ganancias - diferido - Período de tres meses terminado el 30 de septiembre de / 2025 - miles de ARS - valor (264.347) - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Impuesto a las ganancias - diferido - Período de tres meses terminado el 30 de septiembre de / 2024 - miles de ARS - valor (1.365.303) - pagina 73   [confianza: media]
```

### `#/tables/102`

- **procedencia:** paginas [73]
- **table_uid:** `TBL-ebee4781274e2623`
- **table_segment_uid:** `TSEG-ebee4781274e2623`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:73->73']

**DESPUES** — hechos recuperables (21 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Activos financieros a valor razonable con cambio en resultados - al 2025-09-30 - (unidad no declarada) - valor 8.045.094 - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Activos financieros a valor razonable con cambio en resultados - al 2024-12-31 - (unidad no declarada) - valor 9.445.857 - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Provisiones para reclamos legales y otros - al 2025-09-30 - (unidad no declarada) - valor 1.622.224 - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Provisiones para reclamos legales y otros - al 2024-12-31 - (unidad no declarada) - valor 418.739 - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Arrendamientos financieros - al 2025-09-30 - (unidad no declarada) - valor 3.826.281 - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Activos y (pasivos) diferidos - Arrendamientos financieros - al 2024-12-31 - (unidad no declarada) - valor 5.966.057 - pagina 73   [confianza: media]
```

### `#/tables/103`

- **procedencia:** paginas [73]
- **table_uid:** `TBL-8c41fff38251080a`
- **table_segment_uid:** `TSEG-8c41fff38251080a`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:73->73']

**DESPUES** — hechos recuperables (15 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Saldos al 31/12/2023 - (periodo no declarado) - (unidad no declarada) - valor 6.571.930 - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Efecto RECPAM - (periodo no declarado) - (unidad no declarada) - valor (3.389.428) - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Aumentos - (periodo no declarado) - (unidad no declarada) - valor 544.460 - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Aumentos - (periodo no declarado) - (unidad no declarada) - valor (1) - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Saldos al 30/09/2024 - (periodo no declarado) - (unidad no declarada) - valor 3.726.962 - pagina 73   [confianza: media]
TGS_EEFF_2025_09 - Efecto RECPAM - (periodo no declarado) - (unidad no declarada) - valor (283.655) - pagina 73   [confianza: media]
```

### `#/tables/104`

- **procedencia:** paginas [74]
- **table_uid:** `TBL-b8bd63fb8a09ea16`
- **table_segment_uid:** `TSEG-b8bd63fb8a09ea16`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/1484`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:3!=4']

**DESPUES** — hechos recuperables (21 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Créditos por ventas - 30 de septiembre de 2025 / Activos financieros a costo amortizado - miles de ARS - valor 186.728.865 - pagina 74   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Créditos por ventas - 30 de septiembre de 2025 / Total - miles de ARS - valor 186.728.865 - pagina 74   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Otros créditos - 30 de septiembre de 2025 / Activos financieros a costo amortizado - miles de ARS - valor 12.364.531 - pagina 74   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Otros créditos - 30 de septiembre de 2025 / Total - miles de ARS - valor 12.364.531 - pagina 74   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - 30 de septiembre de 2025 / Activos financieros a costo amortizado - miles de ARS - valor 371.887.249 - pagina 74   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - 30 de septiembre de 2025 / Total - miles de ARS - valor 371.887.249 - pagina 74   [confianza: media]
```

### `#/tables/105`

- **procedencia:** paginas [74]
- **table_uid:** `TBL-f4f12698678dd8f4`
- **table_segment_uid:** `TSEG-f4f12698678dd8f4`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:74->74']

**DESPUES** — hechos recuperables (16 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas comerciales - (periodo no declarado) - (unidad no declarada) - valor 98.863.894 - pagina 74   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas comerciales - (periodo no declarado) - (unidad no declarada) - valor 98.863.894 - pagina 74   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas financieras - (periodo no declarado) - (unidad no declarada) - valor 115.652.171 - pagina 74   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas financieras - (periodo no declarado) - (unidad no declarada) - valor 115.652.171 - pagina 74   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 18.183.636 - pagina 74   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 18.183.636 - pagina 74   [confianza: media]
```

### `#/tables/106`

- **procedencia:** paginas [75]
- **table_uid:** `TBL-fb71a0beb31a0454`
- **table_segment_uid:** `TSEG-fb71a0beb31a0454`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/1498`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:mismo_ancho', 'continuidad:el_anterior_tiene_encabezado', 'continuidad:no_enlazada:tiene_encabezado_propio:[0, 1]']

**DESPUES** — hechos recuperables (21 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Créditos por ventas - 31 de diciembre de 2024 / Activos financieros a costo amortizado - miles de ARS - valor 189.448.939 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Créditos por ventas - 31 de diciembre de 2024 / Total - miles de ARS - valor 189.448.939 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Otros créditos - 31 de diciembre de 2024 / Activos financieros a costo amortizado - miles de ARS - valor 14.487.547 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Otros créditos - 31 de diciembre de 2024 / Total - miles de ARS - valor 14.487.547 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - 31 de diciembre de 2024 / Activos financieros a costo amortizado - miles de ARS - valor 331.241.746 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - 31 de diciembre de 2024 / Total - miles de ARS - valor 331.241.746 - pagina 75   [confianza: media]
```

### `#/tables/107`

- **procedencia:** paginas [75]
- **table_uid:** `TBL-b2860999bd42817f`
- **table_segment_uid:** `TSEG-b2860999bd42817f`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:75->75']

**DESPUES** — hechos recuperables (16 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas comerciales - (periodo no declarado) - (unidad no declarada) - valor 93.146.939 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas comerciales - (periodo no declarado) - (unidad no declarada) - valor 93.146.939 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas financieras - (periodo no declarado) - (unidad no declarada) - valor 93.814.551 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Deudas financieras - (periodo no declarado) - (unidad no declarada) - valor 93.814.551 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 18.972.596 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - PASIVO CORRIENTE / Remuneraciones y cargas sociales - (periodo no declarado) - (unidad no declarada) - valor 18.972.596 - pagina 75   [confianza: media]
```

### `#/tables/108`

- **procedencia:** paginas [75]
- **table_uid:** `TBL-e4399648e6e8a251`
- **table_segment_uid:** `TSEG-e4399648e6e8a251`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:75->75']

**DESPUES** — hechos recuperables (6 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Efectivo y equivalentes de efectivo - 30 de septiembre de 2025 / Nivel 1 - (unidad no declarada) - valor 65.326.237 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Efectivo y equivalentes de efectivo - 30 de septiembre de 2025 / Total - (unidad no declarada) - valor 65.326.237 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Activos financieros corrientes a valor razonable con cambios en resultados - 30 de septiembre de 2025 / Nivel 1 - (unidad no declarada) - valor 418.834.764 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Activos financieros corrientes a valor razonable con cambios en resultados - 30 de septiembre de 2025 / Total - (unidad no declarada) - valor 418.834.764 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Total - 30 de septiembre de 2025 / Nivel 1 - (unidad no declarada) - valor 484.161.001 - pagina 75   [confianza: media]
TGS_EEFF_2025_09 - Activos financieros a valor razonable / Total - 30 de septiembre de 2025 / Total - (unidad no declarada) - valor 484.161.001 - pagina 75   [confianza: media]
```

### `#/tables/109`

- **procedencia:** paginas [76]
- **table_uid:** `TBL-34f34e8de449aec9`
- **table_segment_uid:** `TSEG-34f34e8de449aec9`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `celda_encabezado`, evidencia `r1c1`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:5!=8']

**DESPUES** — hechos recuperables (75 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Efectivo y equivalentes de efectivo - al 2025-09-30 - miles de ARS - valor 12.098 - pagina 76   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Efectivo y equivalentes de efectivo - al 2025-09-30 - miles de ARS - valor 1.371,00 (1) - pagina 76   [confianza: baja]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Efectivo y equivalentes de efectivo - al 2025-09-30 - miles de ARS - valor 16.585.772 - pagina 76   [confianza: alta]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Efectivo y equivalentes de efectivo - al 2024-12-31 - miles de ARS - valor 39.999 - pagina 76   [confianza: media]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Efectivo y equivalentes de efectivo - al 2024-12-31 - miles de ARS - valor 50.195.682 - pagina 76   [confianza: alta]
TGS_EEFF_2025_09 - ACTIVO CORRIENTE / Activos financieros a costo amortizado - al 2025-09-30 - miles de ARS - valor 271.253 - pagina 76   [confianza: media]
```

### `#/tables/110`

- **procedencia:** paginas [77]
- **table_uid:** `TBL-daeac0cbea62de38`
- **table_segment_uid:** `TSEG-daeac0cbea62de38`
- **continuation_of:** —
- **banda de encabezado inferida:** [0, 1]
- **unidad:** miles de ARS (origen `texto_adyacente`, evidencia `#/texts/1527`)
- **extraction_warnings:** —
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:paginas_consecutivas', 'continuidad:no_enlazada:ancho_distinto:8!=5']

**DESPUES** — hechos recuperables (22 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Controlante: / CIESA - al 2025-09-30 - miles de ARS - valor 31 - pagina 77   [confianza: media]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía (1) - al 2025-09-30 - miles de ARS - valor 25.474.356 - pagina 77   [confianza: media]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía (1) - al 2025-09-30 - miles de ARS - valor 22.337.857 - pagina 77   [confianza: media]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía (1) - al 2024-12-31 - miles de ARS - valor 16.068.732 - pagina 77   [confianza: media]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía (1) - al 2024-12-31 - miles de ARS - valor 26.673.720 - pagina 77   [confianza: media]
TGS_EEFF_2025_09 - Controlada: / Telcosur (2) (3) - al 2025-09-30 - miles de ARS - valor 580.304 - pagina 77   [confianza: media]
```

### `#/tables/111`

- **procedencia:** paginas [77]
- **table_uid:** `TBL-a54b5d657eadf7e1`
- **table_segment_uid:** `TSEG-a54b5d657eadf7e1`
- **continuation_of:** —
- **banda de encabezado inferida:** [0]
- **unidad:** — (origen `ausente`)
- **extraction_warnings:** ['unidad_ausente']
- **reglas:** ['continuidad:mismo_artefacto', 'continuidad:no_enlazada:paginas_no_consecutivas:77->77']

**DESPUES** — hechos recuperables (25 en total, se muestran 6):

```text
TGS_EEFF_2025_09 - Controlante: / CIESA - (periodo no declarado) - (unidad no declarada) - valor 97 - pagina 77   [confianza: baja]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía - (periodo no declarado) - (unidad no declarada) - valor 20.430.830 - pagina 77   [confianza: baja]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía - (periodo no declarado) - (unidad no declarada) - valor 9.165.429 - pagina 77   [confianza: media]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía - (periodo no declarado) - (unidad no declarada) - valor 63.976.682 - pagina 77   [confianza: baja]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía - (periodo no declarado) - (unidad no declarada) - valor 28.213.292 - pagina 77   [confianza: baja]
TGS_EEFF_2025_09 - Ente que ejerce control conjunto sobre la sociedad controlante: / Pampa Energía - (periodo no declarado) - (unidad no declarada) - valor 21.606.915 - pagina 77   [confianza: media]
```

## Resumen

- hechos totales: **6332**
- por confianza: {'baja': 167, 'media': 6006, 'alta': 159}
- hechos con advertencia que limita el dato: 4591
- hechos donde nuestra inferencia de encabezado difiere de la del parser: 551

El ultimo numero no es un defecto de la extraccion: mide cada cuanto las marcas de encabezado de Docling no coinciden con la inferencia propia. Es el hallazgo que motivo esta representacion, y se guarda para poder contarlo.
