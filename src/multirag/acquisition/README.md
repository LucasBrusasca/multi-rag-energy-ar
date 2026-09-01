# Adquisición de fuentes

Esta capa obtiene artefactos de sistemas externos. No clasifica chunks, no
decide silos y no forma parte de la comparación B0/B1/B2.

Cada proveedor vive en `providers/<proveedor>/` y puede implementar su propia
selección, descarga, autenticación y límites. El adaptador actual es InfoLEG:

```powershell
python -B -m multirag.acquisition.providers.infoleg.select --help
python -B -m multirag.acquisition.providers.infoleg.download --help
python -B -m multirag.acquisition.providers.infoleg.audit --help
python -B -m multirag.acquisition.providers.infoleg.normalize --help
python -B -m multirag.acquisition.providers.infoleg.enrich --help
```

La auditoría compara la selección con los bytes recibidos y genera un informe
derivado. No borra extras o duplicados, no interpreta normas y no toca la base.

La frontera canónica es el catálogo objetivo: una vez aterrizado un archivo,
`multirag.ingestion.catalogo` calcula su identidad por contenido y el resto del
pipeline deja de depender de dónde provino.

El enriquecedor cruza la plantilla objetiva con hechos publicados en la
selección de InfoLEG. Mantiene los registros en revisión, no asigna dominios
documentales y no convierte los estratos de adquisición en etiquetas Golden.
