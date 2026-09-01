# Auditoria diagnostica de la representacion tabular

Solo lectura. No se reingirio, no se modificaron UID ni el snapshot.

## Diagnostico agregado

| clase | que significa | tablas |
|---|---|---|
| A | OCR: caracteres o digitos mal reconocidos | 0 |
| B | Estructura: Docling relaciono mal celdas o encabezados | 10 |
| C | Chunking: Docling la tenia y el pipeline la perdio | 0 |
| D | Retrieval: representacion completa, busqueda fallida | 0 |
| ok | sin perdida detectada | 5 |

## Casos auditados

### Transener_Calificacion_FIX.pdf - #/tables/3

_PDF digital, informe de calificacion_ - OCR: no

| que | valor |
|---|---|
| paginas | [10] |
| dimensiones | 35 x 7, 215 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | SI |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | NO |
| celdas marcadas encabezado de columna | 6 |
| celdas marcadas encabezado de fila | 29 |
| filas con fecha SIN marcar como encabezado | [2, 3] |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 8 |
| **chunk: conserva la unidad** | SI |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **B** |

Muestra de lo que quedo en el chunk:

> Normas Contables, Moneda Constante(*) = NIIF. Normas Contables, Moneda Constante(*) = NIIF. Normas Contables, Moneda Constante(*) = NIIF. Normas Contables, Moneda Constante(*) = NI...

### Transener_Calificacion_FIX.pdf - #/tables/4

_PDF digital, informe de calificacion_ - OCR: no

| que | valor |
|---|---|
| paginas | [11] |
| dimensiones | 19 x 7, 127 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | NO |
| **Docling: periodo en la tabla** | NO |
| Docling: moneda en la tabla | NO |
| celdas marcadas encabezado de columna | 6 |
| celdas marcadas encabezado de fila | 17 |
| filas con fecha SIN marcar como encabezado | ninguna |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 4 |
| **chunk: conserva la unidad** | SI |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **ok** |

Muestra de lo que quedo en el chunk:

> Flujo de Caja Operativo (FCO), (30.716) = 204.545. Flujo de Caja Operativo (FCO), (32.572) = 139.724. Flujo de Caja Operativo (FCO), (50.685) = 165.338. Flujo de Caja Operativo (FC...

### Transener_Calificacion_FIX.pdf - #/tables/0

_PDF digital, informe de calificacion_ - OCR: no

| que | valor |
|---|---|
| paginas | [1] |
| dimensiones | 10 x 3, 26 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | SI |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | SI |
| celdas marcadas encabezado de columna | 2 |
| celdas marcadas encabezado de fila | 7 |
| filas con fecha SIN marcar como encabezado | [1] |
| celdas con dos valores pegados | 1 ['1.029.320 1.030.565'] |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 1 |
| **chunk: conserva la unidad** | SI |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **B** |

Muestra de lo que quedo en el chunk:

> Compañía de Transporte de Energía Eléctrica en Alta Tensión Transener S.A., 1 = Compañía de Transporte de Energía Eléctrica en Alta Tensión Transener S.A.. Compañía de Transporte d...

### Pampa_EEFF_Consolidado_1Q2026.pdf - #/tables/8

_PDF digital, estado contable_ - OCR: no

| que | valor |
|---|---|
| paginas | [12] |
| dimensiones | 18 x 15, 256 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | NO |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | NO |
| celdas marcadas encabezado de columna | 16 |
| celdas marcadas encabezado de fila | 16 |
| filas con fecha SIN marcar como encabezado | [2, 4, 5, 6, 11, 12, 13, 15, 16, 17] |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 10 |
| **chunk: conserva la unidad** | NO |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **B** |

Muestra de lo que quedo en el chunk:

> Saldos al 31 de diciembre de 2024, Aporte de los propietarios.Capital social = 1.360. Saldos al 31 de diciembre de 2024, Aporte de los propietarios.Ajuste de capital = 7.126. Saldo...

### Pampa_EEFF_Consolidado_1Q2026.pdf - #/tables/23

_PDF digital, estado contable_ - OCR: no

| que | valor |
|---|---|
| paginas | [26] |
| dimensiones | 30 x 8, 193 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | SI |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | SI |
| celdas marcadas encabezado de columna | 11 |
| celdas marcadas encabezado de fila | 22 |
| filas con fecha SIN marcar como encabezado | [2, 23, 25] |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 8 |
| **chunk: conserva la unidad** | SI |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **B** |

Muestra de lo que quedo en el chunk:

> finalizado el 31.03.2026, En millones de dólares.Petróleo y gas = . finalizado el 31.03.2026, En millones de dólares.Generación = . finalizado el 31.03.2026, En millones de dólares...

### Pampa_EEFF_Consolidado_1Q2026.pdf - #/tables/26

_PDF digital, estado contable_ - OCR: no

| que | valor |
|---|---|
| paginas | [28] |
| dimensiones | 24 x 8, 186 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | SI |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | SI |
| celdas marcadas encabezado de columna | 9 |
| celdas marcadas encabezado de fila | 22 |
| filas con fecha SIN marcar como encabezado | [22] |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 6 |
| **chunk: conserva la unidad** | SI |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **B** |

Muestra de lo que quedo en el chunk:

> Ingresos por ventas - mercado local, En millones de dólares.Petróleo y gas = 94. Ingresos por ventas - mercado local, En millones de dólares.Generación = 194. Ingresos por ventas -...

### MSU_ON_ClaseIV.pdf - #/tables/4

_PDF digital, prospecto de ON_ - OCR: no

| que | valor |
|---|---|
| paginas | [28] |
| dimensiones | 38 x 3, 99 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | SI |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | SI |
| celdas marcadas encabezado de columna | 2 |
| celdas marcadas encabezado de fila | 30 |
| filas con fecha SIN marcar como encabezado | ninguna |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 3 |
| **chunk: conserva la unidad** | SI |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **ok** |

Muestra de lo que quedo en el chunk:

> ACTIVO, 31/3/2022 (en miles de Pesos) = . ACTIVO, 31/12/2021 = . ACTIVO NO CORRIENTE, 31/3/2022 (en miles de Pesos) = . ACTIVO NO CORRIENTE, 31/12/2021 = . Propiedad, planta y equi...

### MSU_ON_ClaseIV.pdf - #/tables/6

_PDF digital, prospecto de ON_ - OCR: no

| que | valor |
|---|---|
| paginas | [30] |
| dimensiones | 37 x 3, 96 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | SI |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | SI |
| celdas marcadas encabezado de columna | 3 |
| celdas marcadas encabezado de fila | 30 |
| filas con fecha SIN marcar como encabezado | [4, 33, 35] |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 4 |
| **chunk: conserva la unidad** | SI |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **B** |

Muestra de lo que quedo en el chunk:

> CAUSAS DE VARIACIÓN DEL EFECTIVO, 31/3/2022.(en miles de Pesos) = . CAUSAS DE VARIACIÓN DEL EFECTIVO, 31/3/2021.(en miles de Pesos) = . Actividades operativas, 31/3/2022.(en miles ...

### MSU_ON_ClaseIV.pdf - #/tables/8

_PDF digital, prospecto de ON_ - OCR: no

| que | valor |
|---|---|
| paginas | [32] |
| dimensiones | 23 x 3, 58 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | SI |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | SI |
| celdas marcadas encabezado de columna | 3 |
| celdas marcadas encabezado de fila | 17 |
| filas con fecha SIN marcar como encabezado | ninguna |
| celdas con dos valores pegados | 2 ['1  82,764,738', '1  13,312,311'] |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 2 |
| **chunk: conserva la unidad** | SI |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **B** |

Muestra de lo que quedo en el chunk:

> PATRIMONIO, 31/3/2022.(en miles de Pesos) = . PATRIMONIO, 31/12/2021.(en miles de Pesos) = . Capital social, 31/3/2022.(en miles de Pesos) = 468,160. Capital social, 31/12/2021.(en...

### Edenor_EEFF_Consolidado_2025_09.pdf - #/tables/3

_PDF digital, estado contable (caso DOC-0004)_ - OCR: no

| que | valor |
|---|---|
| paginas | [5] |
| dimensiones | 27 x 6, 137 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | NO |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | SI |
| celdas marcadas encabezado de columna | 7 |
| celdas marcadas encabezado de fila | 24 |
| filas con fecha SIN marcar como encabezado | [21, 22, 24] |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 5 |
| **chunk: conserva la unidad** | NO |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **B** |

Muestra de lo que quedo en el chunk:

> Ingresos por servicios, Nota = 8. Ingresos por servicios, Nueve meses.30.09.25 = 2.118.337. Ingresos por servicios, Nueve meses.30.09.24 Ajustado (1) = 1.861.603. Ingresos por serv...

### Edenor_EEFF_Consolidado_2025_09.pdf - #/tables/6

_PDF digital, estado contable (caso DOC-0004)_ - OCR: no

| que | valor |
|---|---|
| paginas | [8] |
| dimensiones | 12 x 13, 137 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | NO |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | NO |
| celdas marcadas encabezado de columna | 14 |
| celdas marcadas encabezado de fila | 10 |
| filas con fecha SIN marcar como encabezado | [4, 5, 7, 8, 9, 10, 11] |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 7 |
| **chunk: conserva la unidad** | NO |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **B** |

Muestra de lo que quedo en el chunk:

> Aumento de Reserva por Plan de Compensación en Acciones, Aportes de los propietarios.Capital social 875 = -. Aumento de Reserva por Plan de Compensación en Acciones, Aportes de los...

### Edenor_EEFF_Consolidado_2025_09.pdf - #/tables/5

_PDF digital, estado contable (caso DOC-0004)_ - OCR: no

| que | valor |
|---|---|
| paginas | [7] |
| dimensiones | 38 x 4, 124 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | NO |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | NO |
| celdas marcadas encabezado de columna | 3 |
| celdas marcadas encabezado de fila | 32 |
| filas con fecha SIN marcar como encabezado | ninguna |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 3 |
| **chunk: conserva la unidad** | NO |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **ok** |

Muestra de lo que quedo en el chunk:

> PATRIMONIO, Nota = . PATRIMONIO, 30.09.25 = . PATRIMONIO, 31.12.24 = . Capital y reservas atribuibles a los propietarios, Nota = . Capital y reservas atribuibles a los propietarios...

### TGS_EEFF_2025_09.pdf - #/tables/43

_PDF digital, estado contable complejo_ - OCR: no

| que | valor |
|---|---|
| paginas | [34] |
| dimensiones | 29 x 14, 352 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | NO |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | NO |
| celdas marcadas encabezado de columna | 16 |
| celdas marcadas encabezado de fila | 25 |
| filas con fecha SIN marcar como encabezado | ninguna |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 17 |
| **chunk: conserva la unidad** | NO |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **ok** |

Muestra de lo que quedo en el chunk:

> Gasoductos, Al comienzo del ejercicio = 2.256.018.551. Gasoductos, Aumentos = -. Gasoductos, Disminuciones = -. Gasoductos, Transferencias = 8.927.026. Gasoductos, Al cierre del pe...

### TGS_EEFF_2025_09.pdf - #/tables/96

_PDF digital, estado contable complejo_ - OCR: no

| que | valor |
|---|---|
| paginas | [70] |
| dimensiones | 28 x 14, 351 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | NO |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | NO |
| celdas marcadas encabezado de columna | 15 |
| celdas marcadas encabezado de fila | 24 |
| filas con fecha SIN marcar como encabezado | ninguna |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 17 |
| **chunk: conserva la unidad** | NO |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **ok** |

Muestra de lo que quedo en el chunk:

> Gasoductos, Al comienzo del ejercicio = 2.256.018.551. Gasoductos, Aumentos = -. Gasoductos, Disminuciones = -. Gasoductos, Transferencias = 8.927.026. Gasoductos, Al cierre del pe...

### TGS_EEFF_2025_09.pdf - #/tables/16

_PDF digital, estado contable complejo_ - OCR: no

| que | valor |
|---|---|
| paginas | [15] |
| dimensiones | 22 x 15, 248 celdas |
| caption | (sin caption) |
| **Docling: unidad en la tabla** | NO |
| **Docling: periodo en la tabla** | SI |
| Docling: moneda en la tabla | NO |
| celdas marcadas encabezado de columna | 33 |
| celdas marcadas encabezado de fila | 14 |
| filas con fecha SIN marcar como encabezado | [5, 9, 10, 11, 12, 13, 19, 20, 21] |
| celdas con dos valores pegados | 0  |
| celdas con sospecha de OCR | 0  |
| chunks que contienen la tabla | 16 |
| **chunk: conserva la unidad** | NO |
| **chunk: conserva el periodo** | SI |
| persistido en la base (fuente) | base no disponible durante la auditoria |
| **clasificacion** | **B** |

Muestra de lo que quedo en el chunk:

> Dispuesto por la Asamblea General Ordinaria, Extraordinaria y Especial, Capital.Acciones en circulación.Capital social.752.761 = . Dispuesto por la Asamblea General Ordinaria, Extr...
