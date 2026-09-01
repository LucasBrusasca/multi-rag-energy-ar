# Revisión previa de los registros con `regulatorio`

Fecha: 30-ago-2026. **Esto es una revisión preparatoria, no una normalización.**
El catálogo no fue modificado. No se tocó la base de datos ni la clasificación
persistida. Ninguna etiqueta histórica fue borrada.

## Decisión que se documenta

Se mantienen **cuatro silos**. Según `config.SILOS`, la materia regulatoria
energética ya está comprendida en `legal`. Por lo tanto:

| aspecto | valor |
|---|---|
| Identificador | `legal` (sin cambios) |
| Nombre visible | **Legal / regulatorio energético** |
| Quinto silo | **No se agrega** |
| `regulatorio` histórico | **Se conserva**; no se reescribe automáticamente |

Regla de asignación, para que la correspondencia no se lea al revés: **las
etiquetas se asignan por la materia que el documento desarrolla, no por su forma
jurídica.** Una ley tributaria sigue siendo una ley y aun así es `impositivo`,
no `legal`.

## Qué está comprobado y qué es hipótesis

Distinción necesaria, porque de esto depende qué se puede hacer sin leer los
documentos:

| afirmación | estatus |
|---|---|
| La distribución de etiquetas: 17 con `regulatorio`, 7 con `legal`, 10 sin `legal`, y el tipo y emisor de cada uno | **HECHO OBSERVADO.** Leído de `data/catalog/metadatos_curados.csv`, reproducible |
| Los dos grupos son homogéneos por tipo de documento y clase de emisor | **HECHO OBSERVADO** |
| Que `regulatorio` haya significado «materia jurídica» en el Grupo A | **HIPÓTESIS.** Nadie registró el criterio con que se etiquetó |
| Que `regulatorio` haya significado «empresa en sector regulado» en el Grupo B | **HIPÓTESIS.** Es la lectura más económica de por qué aparece en balances, pero no está documentada ni verificada |
| Que los 10 del Grupo B serían falsos positivos si se mapearan a `legal` | **HIPÓTESIS, NO VERIFICADA.** No se sabe si esos documentos desarrollan o no materia jurídica: no se abrió ninguno |

⚠️ **Lo único comprobado es la distribución.** El significado histórico de
`regulatorio` no está documentado en ninguna parte del repositorio, y esta
revisión no lo estableció: lo infiere del tipo y del emisor. **La lectura
documental sigue pendiente** y es la única vía para confirmarlo o refutarlo.

## Patrón observado en la distribución

Sobre los 24 documentos canónicos (`data/catalog/metadatos_curados.csv`),
`regulatorio` aparece en 17. Al cruzarlo con `legal` el corpus se parte en dos
grupos que no significan lo mismo:

- **7 documentos tienen `regulatorio` junto con `legal`.**
- **10 documentos tienen `regulatorio` SIN `legal`.**

Y los dos grupos son homogéneos por tipo y por emisor:

### Grupo A — `regulatorio` acompañado de `legal` (7 documentos)

Todos son normas, emitidas por organismos públicos.

| doc | tipo | dominios |
|---|---|---|
| DOC-0001 | decreto | `legal impositivo regulatorio` |
| DOC-0002 | decreto | `legal regulatorio` |
| DOC-0006 | resolucion | `legal regulatorio tecnico` |
| DOC-0013 | texto_ordenado | `legal regulatorio` |
| DOC-0014 | texto_ordenado | `legal regulatorio` |
| DOC-0017 | resolucion | `legal regulatorio tecnico operativo` |
| DOC-0018 | procedimiento_regulatorio | `legal regulatorio tecnico operativo` |

Emisores: Poder Ejecutivo Nacional, ENRE, Honorable Congreso, Secretaría de
Energía. Acá `regulatorio` **coexiste** con `legal` en todos los casos, así que
absorberlo no cambiaría el conjunto de silos de ninguno de los siete. Eso es una
propiedad de las etiquetas, verificable; **no** equivale a haber comprobado que
los siete desarrollen materia regulatoria energética.

### Grupo B — `regulatorio` sin `legal` (10 documentos)

Por tipo de documento, ninguno es una norma: siete estados contables, una
memoria anual, una presentación corporativa y un informe de calificación. Los
emisores son empresas.

| doc | tipo | dominios |
|---|---|---|
| DOC-0004 | estado_contable | `contable regulatorio` |
| DOC-0005 | estado_contable | `contable regulatorio` |
| DOC-0007 | estado_contable | `contable corporativo regulatorio` |
| DOC-0008 | estado_contable | `contable regulatorio` |
| DOC-0016 | estado_contable | `contable regulatorio` |
| DOC-0020 | memoria_anual | `ambiental contable corporativo laboral operativo regulatorio` |
| DOC-0021 | estado_contable | `contable regulatorio` |
| DOC-0022 | estado_contable | `contable regulatorio` |
| DOC-0023 | presentacion_corporativa | `financiero corporativo regulatorio tecnico operativo` |
| DOC-0024 | informe_calificacion | `financiero regulatorio corporativo` |

Ninguno es una norma y ninguno lleva `legal`. **Hipótesis** —no verificada— de
por qué se los etiquetó `regulatorio`: la etiqueta describiría al emisor, una
empresa que opera en un sector regulado, y no al contenido del documento. Es la
explicación más económica del patrón, y nada más que eso: **no se abrió ninguno
de los diez.**

## Por qué esto importa

⚠️ **Un mapeo automático `regulatorio → legal` pondría la etiqueta `legal` en 7
estados contables, una memoria anual, una presentación corporativa y un informe
de calificación**, dentro del corpus que se usa para medir segregación entre
silos.

**Cuántos de esos diez serían realmente falsos positivos es desconocido.** Un
estado contable puede tener una nota sobre un litigio regulatorio y merecer
`legal` por esa nota. Lo que está establecido es que **el mapeo se aplicaría sin
saberlo**, sobre el 59 % (10 de 17) de los documentos con `regulatorio`. Ese es
el motivo para no modificar el catálogo automáticamente: no es que el resultado
sea seguro que esté mal, es que **no habría forma de saber si está bien**.

## Qué NO se puede concluir todavía

Esta revisión es de **etiquetas**, leídas del catálogo. No se abrió ni un
documento. Por lo tanto:

- **No está verificado** que los 7 del Grupo A desarrollen materia regulatoria
  energética; se infiere del tipo y del emisor, que es una señal fuerte pero no
  es evidencia.
- **No está verificado** que los 10 del Grupo B carezcan de materia jurídica.
  Un estado contable puede tener una nota sobre un litigio regulatorio, y
  entonces sí correspondería `legal` —por esa nota, no por el `regulatorio`
  heredado—.
- La partición A/B se apoya en la presencia de `legal`, que es una etiqueta
  histórica de la misma tanda y de confiabilidad no establecida.

## Propuesta de normalización (NO aplicada, requiere tu decisión)

1. **Grupo A**: `regulatorio` queda absorbido por `legal`. Bajo riesgo: la
   etiqueta `legal` ya está presente, así que el conjunto de silos del documento
   no cambia.
2. **Grupo B**: `regulatorio` **no** se mapea a `legal`. Requiere lectura
   documento por documento para decidir si hay materia jurídica desarrollada.
   Estos diez deberían pasar por el instrumento de revisión documental v3 antes
   de tocar nada.
3. En ambos casos, la etiqueta histórica se **conserva** en un campo aparte; no
   se sobrescribe. Cualquier resultado anterior calculado con `regulatorio`
   sigue siendo reproducible.

**Nada de esto está implementado.** No hay script de normalización, a propósito.

## Alcance de lo que sí se hizo

- Se documentó la correspondencia.
- Se cambió el **nombre visible** del silo en el instrumento de revisión a
  «Legal / regulatorio energético», conservando el identificador `legal`.
- Se agregó en la interfaz la advertencia sobre los dos sentidos de
  `regulatorio`, para que quien revise no arrastre el sentido «empresa regulada».
- Sin cambios en corpus, catálogo, base de datos ni `git`.
