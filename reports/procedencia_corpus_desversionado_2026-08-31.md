# Procedencia de los documentos desversionados del corpus

Fecha: 31-ago-2026.

El repositorio **no versiona el corpus** (`data/` está en `.gitignore`): son
documentos de terceros y su peso no corresponde a un repositorio de código.
Hasta este checkpoint, cuatro archivos habían quedado versionados por haber
sido agregados antes de que existiera esa regla. Se los sacó del seguimiento
con `git rm --cached`; **siguen existiendo en disco** y **no se reescribió el
historial**: quien clone un commit anterior a este checkpoint todavía los
obtiene.

Este archivo es el registro que permite readquirirlos y verificar que lo
readquirido es lo mismo que se usó.

## Los cuatro archivos

Ambos documentos son **normas públicas oficiales argentinas** (`origen_fuente:
publica`), no material privado.

### DOC-0006 — Resolución ENRE 544/2024

Programa para la Mejora del Factor de Potencia.

| campo | valor |
|---|---|
| `document_id` | `DOC-0006` |
| `instrument_id` | `INS-0006` |
| `artifact_id` | `ART-SHA256-D4A042B747A7D3462BE6ECBAA70D71DA01685366D6336D448D1182EC16D6B947` |
| Emisor | Ente Nacional Regulador de la Electricidad (ENRE) |
| Fecha | 2024-08-15 |
| Jurisdicción | `argentina_nacional` |
| Archivo | `data/raw/ENRE_Resolucion_544_2024.pdf` |
| SHA-256 (original) | `d4a042b747a7d3462be6ecbaa70d71da01685366d6336d448d1182ec16d6b947` |
| Tamaño | 207.651 bytes |
| Derivado | `data/processed/ENRE_Resolucion_544_2024.md` — SHA-256 `7beac4428790d4276ed22a67824d46edc40380eac43ec397ae8e3b702ae29c0a`, 17.121 bytes |

### DOC-0019 — Resolución General AFIP 830/2000

Régimen de retención del Impuesto a las Ganancias.

| campo | valor |
|---|---|
| `document_id` | `DOC-0019` |
| `instrument_id` | `INS-0019` |
| `artifact_id` | `ART-SHA256-F979E469CDFB816C3516F09A6800255C52978B0AB7228D0189C94C00D43002E0` |
| Emisor | Administración Federal de Ingresos Públicos (AFIP/ARCA) |
| Fecha | 2000-04-26 |
| Jurisdicción | `argentina_nacional` |
| Archivo | `data/raw/RG_AFIP_830.pdf` |
| SHA-256 (original) | `f979e469cdfb816c3516f09a6800255c52978b0ab7228d0189c94c00d43002e0` |
| Tamaño | 1.193.140 bytes |
| Derivado | `data/processed/RG_AFIP_830.md` — SHA-256 `83a4437ce0d34c1287767f8acec19128ccb24497c8f1a4ecca18f1cdc7125093`, 167.763 bytes |

Los SHA-256 de los dos PDF fueron **verificados contra el archivo en disco** y
coinciden con el `artifact_id` registrado en el catálogo. Los `.md` son
derivados de la ingesta y no tienen entrada propia en el catálogo.

## ⚠️ URL de origen: pendiente

**`url_origen` está vacío para ambos documentos** en
`data/catalog/metadatos_curados.csv`. No se registró de dónde se descargaron.

**No se inventan URLs acá.** Los dos son normas publicadas en boletines
oficiales y en los sitios de sus organismos emisores, de modo que son
recuperables por identificador —«Resolución ENRE 544/2024», «RG AFIP
830/2000»— pero **el enlace exacto usado en su momento se perdió**.

Deuda declarada: completar `url_origen` para estos dos documentos, verificando
que el archivo recuperado tenga el SHA-256 de arriba. Si el hash no coincide,
**no es el mismo documento** —una reimpresión, un texto ordenado posterior o un
PDF regenerado— y eso invalida cualquier resultado que dependa de su paginación.

## Mecanismo de readquisición ya existente

`data/catalog/metadatos_curados.csv` es el registro canónico: tiene
`document_id`, `instrument_id`, `artifact_id`, `sha256`, `titulo_oficial`,
`emisor_nombre`, `fecha_documento`, `jurisdiccion`, `origen_fuente` y
`url_origen` para los 24 documentos.

⚠️ **Ese CSV vive en `data/` y por lo tanto tampoco se versiona.** Este informe
existe precisamente por eso: es la copia versionada de la procedencia de los
archivos que salieron del seguimiento. El resto del corpus depende del CSV
local, que **no tiene respaldo en el repositorio**.
