# Revisión de etiquetas: los 8 documentos que hoy dicen «de todo»

Estos documentos tienen puestos los 4 silos (`legal|impositivo|contable|financiero`).
Con esa etiqueta no se puede comprobar nada sobre sus fragmentos: cualquier asignación cae «dentro».

**Qué hacer:** para cada uno, mirá el título y el tipo y escribí en la última columna qué silos
describen su **materia principal**. Pueden ser varios; lo que no conviene es poner los 4 por las dudas.
Si un silo aparece solo en una nota al pie o en una mención, no va.

Guía rápida de lo que significa cada silo (está en `config.SILOS`):
- `legal`: regulación del sector energético, concesiones, tarifas, entes reguladores, sanciones.
- `impositivo`: qué está gravado, alícuotas, retenciones, AFIP/ARCA.
- `contable`: estados contables, notas, valuación, NIIF/RT.
- `financiero`: deuda, ON, prospectos, calificaciones, valuación, inversores.

**Decisión aparte:** `regulatorio` aparece en 17 de 24 documentos y no es un silo.
Marcá una de las dos al final del archivo.

| # | document_id | título | tipo | emisor | etiquetas actuales | **silos corregidos** |
|---|---|---|---|---|---|---|
| 1 | `DOC-0004` | Estados financieros consolidados condensados intermedios al 30 de s... | estado_contable | Empresa Distribuidora y Comercializadora Norte S.A. | `contable|financiero|impositivo|legal|regulatorio` |  |
| 2 | `DOC-0005` | Estados financieros individuales condensados intermedios al 31 de m... | estado_contable | Compañía de Transporte de Energía Eléctrica en Alta Tensión Transener S.A. | `contable|financiero|impositivo|legal|regulatorio` |  |
| 3 | `DOC-0007` | Estados financieros, reseña informativa e información adicional al ... | estado_contable | Gas y Petróleo del Neuquén S.A. | `contable|financiero|impositivo|legal|regulatorio|corporativo` |  |
| 4 | `DOC-0008` | Unaudited condensed consolidated financial statements as of March 3... | estado_contable | Compañía de Transporte de Energía Eléctrica en Alta Tensión Transener S.A. | `contable|financiero|impositivo|legal|regulatorio` |  |
| 5 | `DOC-0016` | Estados financieros consolidados condensados intermedios al 31 de m... | estado_contable | Pampa Energía S.A. | `contable|financiero|impositivo|legal|regulatorio` |  |
| 6 | `DOC-0020` | Memoria y estados financieros del ejercicio terminado el 31 de dici... | memoria_anual | Transportadora de Gas del Sur S.A. | `contable|financiero|impositivo|legal|regulatorio|corporativo|ambiental|laboral|operativo` |  |
| 7 | `DOC-0021` | Estados financieros al 30 de septiembre de 2025 y 2024 | estado_contable | Transportadora de Gas del Sur S.A. | `contable|financiero|impositivo|legal|regulatorio` |  |
| 8 | `DOC-0022` | Estados financieros consolidados condensados intermedios al 31 de m... | estado_contable | Compañía de Transporte de Energía Eléctrica en Alta Tensión Transener S.A. | `contable|financiero|impositivo|legal|regulatorio` |  |

## Decisión sobre `regulatorio`

- [ ] Se mapea a `legal` (la descripción de `legal` ya dice «materia jurídico-regulatoria»).
- [ ] Es un silo distinto que falta (implica cambiar la taxonomía antes de congelar).

_Fuente: `data/catalog/metadatos_curados.csv`, columna `dominios_documentales`. Este archivo no modifica nada: cuando termines, yo aplico los cambios al catálogo._