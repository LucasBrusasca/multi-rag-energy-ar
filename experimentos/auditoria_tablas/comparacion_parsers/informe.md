# Benchmark estructural Docling–Marker

Este informe es exploratorio y de solo lectura. No modifica la ingesta ni la base.

**Estado de la verdad:** `semilla_exploratoria_pendiente_de_verificacion_humana`.
Los casos deben verificarse visualmente y congelarse antes de usarlos como Golden confirmatorio.

**Política de página Marker:** Marker 2.0.0 chunks puede emitir page=374 para IDs /page/0/...; se usa el segmento /page/N del ID como procedencia canonica y solo se recurre al campo page cuando el ID no la contiene.

## Resultado agregado

| parser/corrida | disponibles | componentes | misma tabla | asociación fila/columna | procedencia | respondibles |
|---|---:|---:|---:|---:|---:|---:|
| docling-current | 6/6 | 6/6 | 5/6 | 5/6 | 5/6 | **5/6** |
| marker:fast/run_01 | 2/6 | 2/2 | 1/2 | 1/2 | 1/2 | **1/2** |
| marker:fast/run_02 | 2/6 | 2/2 | 1/2 | 1/2 | 1/2 | **1/2** |

`componentes` solo exige que los datos aparezcan en alguna tabla. `respondibles` exige además asociación estructural correcta y todas las páginas fuente. Las métricas de calidad usan como denominador solo los casos disponibles para esa corrida.

## Comparación pareada contra Docling

| corrida Marker | casos compartidos | Docling respondibles | Marker respondibles | diferencia |
|---|---:|---:|---:|---:|
| marker:fast/run_01 | 2 | 1 | 1 | +0 |
| marker:fast/run_02 | 2 | 1 | 1 | +0 |

## Detalle por caso

| parser | caso | componentes | misma tabla | asociación | procedencia | respondible | páginas observadas |
|---|---|---:|---:|---:|---:|---:|---|
| docling-current | transener_resumen_ebitda | sí | sí | sí | sí | **sí** | [1] |
| docling-current | transener_fco_tabla_partida | sí | no | no | no | **no** | — |
| docling-current | msu_ventas_unidad | sí | sí | sí | sí | **sí** | [27] |
| docling-current | pampa_ingresos_periodo | sí | sí | sí | sí | **sí** | [8] |
| docling-current | edenor_ingresos_nueve_meses | sí | sí | sí | sí | **sí** | [5] |
| docling-current | tgs_intereses_nueve_meses | sí | sí | sí | sí | **sí** | [68] |
| marker:fast/run_01 | transener_resumen_ebitda | sí | sí | sí | sí | **sí** | [1] |
| marker:fast/run_01 | transener_fco_tabla_partida | sí | no | no | no | **no** | — |
| marker:fast/run_01 | msu_ventas_unidad | no | no | no | no | **no** | — |
| marker:fast/run_01 | pampa_ingresos_periodo | no | no | no | no | **no** | — |
| marker:fast/run_01 | edenor_ingresos_nueve_meses | no | no | no | no | **no** | — |
| marker:fast/run_01 | tgs_intereses_nueve_meses | no | no | no | no | **no** | — |
| marker:fast/run_02 | transener_resumen_ebitda | sí | sí | sí | sí | **sí** | [1] |
| marker:fast/run_02 | transener_fco_tabla_partida | sí | no | no | no | **no** | — |
| marker:fast/run_02 | msu_ventas_unidad | no | no | no | no | **no** | — |
| marker:fast/run_02 | pampa_ingresos_periodo | no | no | no | no | **no** | — |
| marker:fast/run_02 | edenor_ingresos_nueve_meses | no | no | no | no | **no** | — |
| marker:fast/run_02 | tgs_intereses_nueve_meses | no | no | no | no | **no** | — |

## Regla de decisión

Marker no reemplaza a Docling por velocidad, marketing ni apariencia. Solo se promueve si mejora relaciones respondibles en los casos congelados, conserva procedencia y su costo operativo es aceptable. Excel permanece en lectura nativa con openpyxl.
