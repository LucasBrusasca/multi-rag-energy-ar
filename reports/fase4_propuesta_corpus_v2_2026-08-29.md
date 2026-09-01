# FASE 3 v2 + FASE 4 v2 — corpus candidato con conteos verificados

**Receta:** `propuesta-fase4-v2` · **Fecha:** 29-ago-2026

> **Reemplaza a la FASE 4 v1, que queda como borrador.** Los números de membresía
> por dominio de la v1 salían de asignar por decreto todo documento empresarial a
> `contable` **y** `financiero`. Con los documentos leídos, eso no se sostiene.

> **PROPUESTA PREVIA A LA INGESTA.** No se ingirió, no se descargó nada nuevo, no
> se tocó PostgreSQL, nada se movió a `data/raw`.

## Salvedades, antes de los números

- PROPUESTA. No se ingirio, no se descargo nada nuevo, no se toco PostgreSQL.
- Ningun documento tiene dominio verificado; todo es propuesta con evidencia.
- Las brechas son DESCONOCIDAS hasta terminar la revision humana de los 59.
- 198 disponibles sin cuarentena; 209 como techo con los 11 sin revisar.
- robots.txt se cumplio con evaluacion RFC 9309 propia: la biblioteca estandar de Python da la respuesta contraria en el caso de Edenor.
- Dos archivos de cuarentena son planillas y no se leyo su contenido.

## 1 · Conteos: verificado, propuesto y pendiente

| | documentos | qué significa |
|---|---:|---|
| activos | 24 | **verificado**: ingeridos, con catálogo curado |
| InfoLEG seleccionados | 150 | **verificado** que existen y están normalizados; su dominio es propuesta |
| empresariales nuevos | 24 | **verificado** que se descargaron y se leyeron; su dominio es propuesta |
| **disponibles sin cuarentena** | **198** | |
| cuarentena, sin revisar | 11 | **pendiente**: apartados por un motivo que nadie registró |
| **máximo potencial** | **209** | techo si toda la cuarentena sobrevive la revisión |

De los 11 de cuarentena, 2 son planillas cuyo contenido
**no se leyó**: no hay lector liviano instalado y no se inventa una
caracterización a partir del nombre.

## 2 · Membresías por dominio — PROPUESTAS, no verificadas

Cada documento empresarial fue **leído**, y su dominio se propone solo cuando
aparecen al menos 3 términos distintos de ese dominio,
con la cita y la página. Ya no se asigna `contable` + `financiero` por decreto.

| dominio | objetivo | InfoLEG (propuesto) | empresariales (propuesto) | total propuesto |
|---|---:|---:|---:|---:|
| `legal` | 75 | 75 | 20 | 95 |
| `impositivo` | 75 | 75 | 16 | 91 |
| `contable` | 75 | 0 | 17 | 17 |
| `financiero` | 75 | 0 | 4 | 4 |

**La columna `total propuesto` no es un conteo de membresías verificadas.** Los
dominios de InfoLEG salen del criterio de búsqueda; los empresariales, de un
umbral léxico. Los 59 documentos están sin revisar por una persona.

### Cómo se distribuyen las combinaciones (empresariales leídos)

Si todo documento empresarial fuera contable y financiero a la vez, esta tabla
tendría una sola fila. Tiene varias, y esa es la corrección.

| combinación propuesta | documentos |
|---|---:|
| `contable`, `impositivo`, `legal` | 14 |
| `contable`, `financiero`, `impositivo`, `legal` | 7 |
| *(ninguno)* | 2 |
| `legal` | 2 |
| `contable` | 2 |
| `contable`, `financiero`, `legal` | 2 |
| `impositivo`, `legal` | 2 |
| `financiero`, `legal` | 1 |
| `contable`, `financiero` | 1 |
| `financiero` | 1 |

## 3 · Brechas: DESCONOCIDAS hasta terminar la revisión

| dominio | objetivo | brecha |
|---|---:|---|
| `legal` | 75 | **desconocida** |
| `impositivo` | 75 | **desconocida** |
| `contable` | 75 | **desconocida** |
| `financiero` | 75 | **desconocida** |

Una brecha es la distancia entre un objetivo y un conteo **verificado**. No hay
conteo verificado: la revisión humana de los 59 documentos no ocurrió. Decir
«faltan 40» afirmaría como medido algo que depende por completo de decisiones que
nadie tomó todavía.

Lo que sí se puede acotar: para `contable` y `financiero`, los **264 documentos**
bloqueados por `robots.txt` siguen siendo la restricción material. Existen y son
públicos; su editor pidió que los clientes automáticos no los tomen.

## 4 · Distribución de los empresariales leídos

### Por emisor

| valor | documentos |
|---|---:|
| TRANSENER | 12 |
| TGS | 8 |
| Pampa Energía S.A | 3 |
| CEPU | 2 |
| METROGAS | 2 |
| PAMPA ENERGÍA S.A | 2 |
| MMESA Compañía Administradora del Mercado Eléctrico Mayorist | 2 |
| ? | 1 |
| To the shareholders of Pampa Energía S.A | 1 |
| On April 21, 2026, Fértil Pampa S.A.U | 1 |

### Por tipo documental propuesto

| valor | documentos |
|---|---:|
| estado_financiero | 22 |
| presentacion_inversores | 3 |
| memoria_anual | 2 |
| reporte_sostenibilidad | 2 |
| reporte_resultados | 2 |
| terminos_y_condiciones | 1 |
| codigo_de_etica | 1 |
| no_determinado | 1 |

### Por período propuesto

| valor | documentos |
|---|---:|
| 2025 | 6 |
| 1T2026 | 4 |
| 2T2026 | 3 |
| 2026 | 3 |
| 2026-03-31 | 1 |
| sin período | 1 |
| 2026-06-30 | 1 |
| 30 DE JUNIO DE 2026 | 1 |
| 31 DE DICIEMBRE DE 2025 | 1 |
| 2024 | 1 |
| 30 DE JUNIO DE 2017 | 1 |
| 30 DE JUNIO DE 2018 | 1 |
| 30 DE SEPTIEMBRE DE 2016 | 1 |
| 30 DE SEPTIEMBRE DE 2017 | 1 |
| 30 DE SEPTIEMBRE DE 2018 | 1 |
| 31 DE MARZO DE 2017 | 1 |
| 31 DE MARZO DE 2018 | 1 |
| 31 DE MARZO DE 2019 | 1 |
| 31 DE DICIEMBRE DE 2016 | 1 |
| 31 DE DICIEMBRE DE 2017 | 1 |
| 31 DE DICIEMBRE DE 2018 | 1 |
| 31 DE MARZO DE 2026 | 1 |

### Por confianza del período

| valor | documentos |
|---|---:|
| media | 17 |
| alta | 16 |
| sin_periodo | 1 |

## 5 · Pertinencia: candidatos a exclusión

Marcados **solo** cuando el documento además no trae materia de dominio regulado,
o cuando su propio tipo es el no pertinente. Una `Memoria y EEFF` que dedica un
capítulo a sostenibilidad **no** se marca: excluirla tiraría uno de los documentos
más ricos del corpus.

| documento | motivo |
|---|---|
| `CEPU__Anuncio_fecha_de_resultados_2T26.pdf` | aviso_o_convocatoria |
| `METROGAS__TyC-Notificaciones-Electronicas-2026.pdf` | terminos_y_condiciones |
| `METROGAS__TyC_Adhesion-al-Servicio-de-Factura-Digital_20` | terminos_y_condiciones |
| `TGS__Tgs-REPORTE-2024_13-6.pdf` | sostenibilidad |
| `TGS__tgs-Reporte-ASG-2025.pdf` | sostenibilidad |
| `TRANSENER__C_DIGO-DE-_TICA-2025.pdf` | codigo_de_etica |

## 6 · Deduplicación documental, más allá del SHA-256

Clave: entidad + tipo + período + título normalizado + páginas. Más una huella
del texto extraído.

| hallazgo | cantidad |
|---|---:|
| duplicados por texto extraído | 1 |
| duplicados por clave documental | 0 |

- Mismo texto: `0001292814-26-002185.pdf`, `20-F 2025.pdf`

### Transener 31-03-2019 contra el documento activo

| | nuevo | activo |
|---|---|---|
| archivo | `TRANSENER__EEFF-31-03-2019.pdf` | `EEFF-ind-31-03-2019.pdf` |
| SHA-256 | `f781730f9723da14…` | `236dda16539b6c6d…` |
| bytes | 956,023 | 1.130.180 |
| páginas | 41 | 40 |

**No son el mismo archivo ni el mismo texto.** Comparten fecha de cierre y, muy
probablemente, emisor. La diferencia de páginas sugiere individual contra
consolidado, o dos presentaciones del mismo cierre. **Esto lo decide la revisión
humana**: se marca como par a comparar, no como duplicado ni como documento
distinto.

## 7 · Instrumento de revisión

`experimentos/revision_corpus/revision_corpus.html` — offline, doble clic. Los 59
documentos en un solo lugar: 24 activos, 24 nuevos y 11 de cuarentena. Cada uno
con su evidencia citada, la confianza de cada propuesta, y correcciones
independientes de emisor, tipo, período y dominios.

Revisarlos en tres instrumentos separados volvería la única comparación que
importa —¿es este documento nuevo el mismo que aquel activo?— la más difícil de
hacer.

## 8 · Lo que esta propuesta NO afirma

- **No afirma el dominio de ningún documento.** Todo es propuesta con evidencia.
- **No afirma un tamaño de corpus.** 198 disponibles, 209 como techo.
- **No afirma brechas.** Son desconocidas hasta que la revisión termine.
- **No afirma la entidad de varios documentos de cuarentena.** Se dedujo del
  texto y la confianza es baja en cuatro de ellos.
- **No leyó dos archivos de cuarentena**, por ser planillas.

## Manifest

```json
{
  "activos": 24,
  "bloqueados_por_robots": 264,
  "brechas_por_dominio": {
    "contable": "desconocida",
    "financiero": "desconocida",
    "impositivo": "desconocida",
    "legal": "desconocida"
  },
  "cuarentena_unicos_sin_revisar": 11,
  "disponibles_sin_cuarentena": 198,
  "empresariales_nuevos": 24,
  "infoleg_seleccionados": 150,
  "maximo_potencial": 209,
  "objetivo_por_dominio": 75,
  "receta": "propuesta-fase4-v2",
  "reemplaza": "propuesta-fase4-v1 (borrador; membresias por decreto)",
  "salvedades": [
    "PROPUESTA. No se ingirio, no se descargo nada nuevo, no se toco PostgreSQL.",
    "Ningun documento tiene dominio verificado; todo es propuesta con evidencia.",
    "Las brechas son DESCONOCIDAS hasta terminar la revision humana de los 59.",
    "198 disponibles sin cuarentena; 209 como techo con los 11 sin revisar.",
    "robots.txt se cumplio con evaluacion RFC 9309 propia: la biblioteca estandar de Python da la respuesta contraria en el caso de Edenor.",
    "Dos archivos de cuarentena son planillas y no se leyo su contenido."
  ],
  "umbral_terminos": 3
}
```
