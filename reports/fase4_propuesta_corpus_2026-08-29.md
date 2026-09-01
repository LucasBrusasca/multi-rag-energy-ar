# FASE 4 — Manifest de candidatos y composición propuesta

**Receta:** `propuesta-fase4-v1` · **Fecha:** 29-ago-2026

> **PROPUESTA PREVIA A LA INGESTA.** No se ingirió nada, no se tocó PostgreSQL,
> no se movió nada a `data/raw` y ningún documento tiene dominio asignado.

## Titular

El objetivo era ~75 membresías por dominio. **Se llega en legal/regulatorio e**
**impositivo. No se llega en contable ni financiero**, y el motivo es concreto y
verificable: el `robots.txt` de Edenor y de Vista Energy prohíbe el acceso
automático a los directorios donde viven sus documentos para inversores. Se
respetó, y por eso `264` documentos descubiertos quedaron sin descargar.

La brecha se reporta **como brecha**, con la lista exacta de pendientes.

## 1 · Manifest de candidatos

| origen | documentos | estado | zona |
|---|---:|---|---|
| corpus activo | 24 | en uso, **no se toca** | `data/raw` |
| InfoLEG seleccionados (FASE 2) | 150 | `pendiente_revision` | `data/staged/infoleg/textos` |
| empresariales descargados (FASE 3) | 24 | `pendiente_revision` | `data/incoming/candidates` |
| cuarentena (únicos) | 11 | sin decidir | `data/quarantine/descartados` |
| **candidatos nuevos** | **185** | | |
| **corpus potencial** | **209** | | |

## 2 · Composición

### Por dominio candidato

`dominio candidato` es para qué dominio **podría** aportar membresías. No es una
etiqueta verificada: todo sale `pendiente_revision`.

| dominio | objetivo | candidatos hoy | brecha |
|---|---:|---:|---:|
| `legal/regulatorio` | 75 | 75 | 0 |
| `impositivo` | 75 | 75 | 0 |
| `contable` | 75 | 35 | 40 **faltan 40** |
| `financiero` | 75 | 35 | 40 **faltan 40** |

Los `35` documentos empresariales cuentan para contable **y** para financiero:
un estado financiero es las dos cosas. Contarlos una sola vez subestimaría el
corpus; contarlos como `70` documentos distintos lo inflaría.

### Por emisor (documentos empresariales)

| emisor | segmento | descargados | bloqueados por robots |
|---|---|---:|---:|
| `CEPU` | generacion | 2 | 0 |
| `EDENOR` | distribucion_electrica | 0 | 11 |
| `METROGAS` | distribucion_gas | 2 | 0 |
| `TGS` | transporte_gas | 8 | 0 |
| `TRANSENER` | transporte_electrico | 12 | 0 |
| `VIST` | upstream | 0 | 253 |

**Emisores con documentos efectivamente adquiridos: 4.** El objetivo
de diversidad era 10–15. **No se alcanza**, y la razón está en la columna de la
derecha.

### Por tipo documental propuesto (empresariales descargados)

| tipo propuesto | documentos |
|---|---:|
| `estado_financiero` | 12 |
| `no_determinado` | 7 |
| `presentacion_inversores` | 2 |
| `reporte_resultados` | 2 |
| `reporte_sostenibilidad` | 1 |

### Por período y formato

| período propuesto | documentos |
|---|---:|
| 2019 | 11 |
| 2025 | 2 |
| 2026 | 10 |
| 2T26 | 1 |

Formato: `pdf` en los 24 empresariales; `html` en los 150 de InfoLEG.

### InfoLEG: décadas y tipos

| dominio candidato | década 2010s | década 2020s | tipos distintos | organismos |
|---|---:|---:|---:|---:|
| `legal/regulatorio` | 31 | 44 | 3 | 7 |
| `impositivo` | 35 | 40 | 4 | 7 |

## 3 · Documentos únicos

Contados por documento y no por archivo, con la deduplicación de la FASE 1
aplicada.

| | documentos |
|---|---:|
| activos | 24 |
| InfoLEG seleccionados | 150 |
| empresariales descargados | 24 |
| cuarentena únicos | 11 |
| **total único** | **209** |

## 4 · Estimación de chunks

**Extrapolación, no pronóstico.** Sale de la mediana de chunks por documento
observada en los 24 activos, por tipo documental. Varios tipos tienen muestra de
**un solo documento**: ahí la «mediana» es ese documento.

| dominio candidato | documentos | chunks estimados | base de la estimación |
|---|---:|---:|---|
| `legal/regulatorio` | 75 | ~6,899 | mediana por tipo de norma |
| `impositivo` | 75 | ~7,145 | mediana por tipo de norma |
| `contable` + `financiero` | 24 | ~3,978 | mediana por tipo propuesto |
| **total candidatos nuevos** | **174** | **~18,022** | |

Sumado a los `4.789` chunks actuales, un corpus de esta composición rondaría los
**~22,811 chunks**. El número es sensible al tipo documental: un
`estado_contable` aportó entre `109` y `647` chunks en el corpus actual.

## 5 · Duplicados y exclusiones

| hallazgo | cantidad | qué es |
|---|---:|---|
| duplicados binarios reales (FASE 1) | 13 | 12 extras de InfoLEG que son copias exactas de la selección + 1 par en cuarentena |
| cuarentena: archivos → documentos | 12 → 11 | `0001292814-26-002185.pdf` **es** `20-F 2025.pdf` |
| bloqueados por robots.txt | 264 | no descargados, a propósito |
| omitidos por tope de emisor | 57 | evita que un emisor domine el corpus |
| normas InfoLEG ausentes (HTTP 403) | 2 | `317876`, `419824`; no se evaden |

**Los 20 extras históricos de InfoLEG son en realidad 8 documentos nuevos:** los
otros 12 son copias binarias exactas de archivos de la selección.

## 6 · Brechas que permanecen

| brecha | tamaño | causa | qué se necesita |
|---|---:|---|---|
| membresías contables | 40 | robots.txt de Edenor y Vista | descarga manual, o CNV/BYMA como fuente |
| membresías financieras | 40 | ídem | ídem |
| diversidad de emisores | 6–11 | 4 emisoras sin página de RI alcanzable | ver lista de pendientes |
| tipos empresariales faltantes | — | no aparecieron en las páginas alcanzables | prospectos, ON, memorias de más emisoras |

### Pendientes de descarga — emisoras sin página de RI alcanzable

**No se inventa ninguna URL.** Estas emisoras se sondearon y no respondieron en
las rutas probadas; la ruta real hay que descubrirla o cargarla a mano.

| emisora | host | rutas sondeadas | resultado |
|---|---|---|---|
| Pampa Energia | `www.pampaenergia.com` | `/inversores` → 404; `/es/inversores` → 404; `/investors` → 404; `/relacion-con-inversores` → 404 | sin página de RI |
| YPF | `www.ypf.com` | `/inversores` → 200; `/inversoresaccionistas` → 200; `/investors` → 200 | sin página de RI |
| Camuzzi Gas Pampeana | `www.camuzzigas.com.ar` | `/inversores` → 404; `/institucional` → 404 | sin página de RI |
| Compania General de Combustibles | `www.cgc.com.ar` | `/inversores` → 404; `/es/inversores` → 404 | sin página de RI |
| Albanesi | `www.albanesi.com.ar` | `/inversores` → bloqueado_por_robots; `/es/inversores` → bloqueado_por_robots | sin página de RI |

### Pendientes de descarga — bloqueados por robots.txt

Estos documentos **existen y son públicos**, pero su editor pidió que los
clientes automáticos no los tomen. Requieren descarga manual por una persona, o
una fuente alternativa (CNV es el repositorio oficial de estados contables de
emisoras listadas).

| emisor | documentos bloqueados | directorio prohibido |
|---|---:|---|
| `VIST` | 253 | `https://vista-energy.cdn.prismic.io/vista-energy/bEnwD3mIp9myby46_EstadosFinanci…` |
| `EDENOR` | 11 | `https://www.edenor.com/files/investors/2026-05/EDENOR_2026_03_Estados_Financiero…` |

## 7 · Selección recomendada para un corpus de ~300 documentos

| bloque | documentos | estado |
|---|---:|---|
| activos actuales | 24 | ya ingeridos, **no se tocan** |
| InfoLEG legal/regulatorio | 75 | seleccionados, sin ingerir |
| InfoLEG impositivo | 75 | seleccionados, sin ingerir |
| empresariales descargados | 24 | en `incoming/candidates` |
| cuarentena a promover | 11 | tras revisión humana |
| **subtotal disponible** | **209** | |
| **faltante para 300** | **91** | empresariales, por descarga manual o CNV |

**Recomendación:** no forzar los 300 con más InfoLEG. Ampliar solo la parte
normativa desbalancearía el corpus justo en el eje que la tesis quiere medir, y
dejaría contable y financiero apoyados en 4 emisoras. El faltante debe cubrirse
con documentos empresariales de emisoras distintas.

## 8 · Subconjunto curado para evaluación y Golden (48–60 documentos)

Criterio: **máxima diversidad por documento**, no máxima cantidad. El Golden se
puntúa a mano; cada documento cuesta tiempo humano.

| estrato | documentos | por qué |
|---|---:|---|
| activos con evidencia tabular verificada | 8 | ya tienen hechos extraídos y auditados |
| InfoLEG legal/regulatorio, tipos y décadas distintos | 12 | cubre la variedad normativa |
| InfoLEG impositivo, tipos y décadas distintos | 12 | ídem |
| empresariales: un estado financiero por emisor | 4–6 | evidencia tabular densa |
| empresariales: un no-financiero por emisor | 4–6 | presentación, memoria, calificación |
| documentos multidominio declarados | 6 | son los que discriminan entre silos |
| candidatos a abstención | 4 | preguntas cuya respuesta correcta es no responder |
| **total** | **50–54** | |

Este subconjunto **no se puede fijar todavía**: depende de la revisión humana de
dominios, que está abierta. Es la forma del subconjunto, no su contenido.

## 9 · Lo que esta propuesta NO afirma

- **No afirma el dominio de ningún documento.** Todo sale `pendiente_revision`.
- **No afirma que sean 300 documentos.** Son 209 disponibles y 91 faltantes.
- **No estima chunks con precisión.** Varios tipos tienen muestra de un documento.
- **No incluyó nada en el corpus.** Los empresariales están en
  `data/incoming/candidates`, fuera de `data/raw`.
- **No sabe si los documentos de cuarentena son de emisoras distintas.** Los
  metadatos del PDF identifican uno (Pampa Energía); el resto exige abrirlos.

## Manifest

```json
{
  "activos": 24,
  "cuarentena_unicos": 11,
  "duplicados_binarios": 13,
  "emisores_con_descargas": 4,
  "empresariales_bloqueados_por_robots": 264,
  "empresariales_descargados": 24,
  "infoleg_seleccionados": 150,
  "objetivo_por_dominio": 75,
  "receta": "propuesta-fase4-v1",
  "salvedades": [
    "PROPUESTA. No se ingirio, no se toco PostgreSQL, nada se movio a data/raw.",
    "Ningun documento tiene dominio asignado; todo sale pendiente_revision.",
    "robots.txt se cumplio: 264 documentos publicos quedaron sin descargar y figuran en la lista de pendientes.",
    "Las estimaciones de chunks son extrapolaciones desde muestras de 1 a 7 documentos por tipo.",
    "Los 24 activos no se modificaron."
  ]
}
```
