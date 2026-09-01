# Multi-RAG Energy AR

Sistema de investigación para evaluar si una arquitectura Multi-RAG gobernada
reduce la colisión semántica entre dominios legal, impositivo, contable y
financiero sin degradar de forma inaceptable la recuperación de evidencia.

El caso de estudio es el sector energético argentino. El repositorio implementa
la ingesta multimodal, identidad documental, clasificación por chunk,
recuperación monolítica y por silos, generación con citas, veto epistémico y
sondas experimentales B0/B1/B2.

## Estructura canónica

```text
src/multirag/
  config.py                 configuración central del sistema
  db.py                     acceso a PostgreSQL/pgvector
  paths.py                  rutas estables del proyecto
  ingestion/                catálogo, metadatos, Docling, chunks y embeddings
  acquisition/              adquisición de fuentes, separada por proveedor
    providers/infoleg/      adaptador actual para InfoLEG
  orchestration/            clasificador, compuerta y recuperación
  generation/               LLM, generación fundamentada y veto
  evaluation/               comparación B0/B1/B2 y sondas reutilizables
  research/                 prototipos y análisis no productivos
scripts/
  admin/                    operaciones explícitas sobre la base
  diagnostics/              comprobaciones manuales de desarrollo
tests/                      pruebas automatizadas del código activo
experimentos/               corridas, protocolos piloto y resultados fechados
docs/                       memoria canónica de la tesis
data/                       corpus y artefactos locales; no se publica
```

Los directorios fechados de `experimentos/` son evidencia histórica. No forman
parte del paquete activo y se conservan en sus rutas originales para no romper
su trazabilidad ni sus supuestos de ejecución.

## Instalación local

Desde la raíz del repositorio, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps --no-build-isolation
docker compose up -d
```

La instalación editable hace importable `multirag` sin modificar `sys.path` en
cada script. Los cambios realizados dentro de `src/multirag/` se reflejan sin
reinstalar el paquete.

## Verificación

```powershell
python -B -m unittest discover -v
python -B -m compileall -q src\multirag scripts tests
```

## Flujos principales

Catalogar de forma neutral los archivos disponibles en `data/raw/`:

```powershell
python -B -m multirag.ingestion.catalogo `
  --salida data/catalog/inventario_objetivo.jsonl
```

Generar la plantilla de metadatos curados:

```powershell
python -B -m multirag.ingestion.metadatos `
  --catalogo data/catalog/inventario_objetivo.jsonl `
  --salida data/catalog/metadatos_curados.csv
```

Ingerir documentos ya catalogados y curados:

```powershell
python -B -m multirag.ingestion.pipeline data/raw/documento.pdf
```

Comparar recuperación con el mismo `k` final:

```powershell
python -B -m multirag.evaluation.comparar `
  --pregunta "¿Qué establece la Ley 24.065 sobre el acceso abierto?" `
  --silos-oraculo legal `
  --k 3
```

El código de adquisición no está acoplado conceptualmente a InfoLEG. InfoLEG es
el primer adaptador bajo `acquisition/providers/`; otros proveedores deben
incorporarse como adaptadores hermanos con su propia política de selección y
descarga.

```powershell
python -B -m multirag.acquisition.providers.infoleg.select --help
python -B -m multirag.acquisition.providers.infoleg.download --help
python -B -m multirag.acquisition.providers.infoleg.audit --help
```

La explicación completa de cada componente, sus entradas, salidas y relación
con la tesis está en
[`docs/GUIA_ARQUITECTURA_Y_ESTUDIO.md`](docs/GUIA_ARQUITECTURA_Y_ESTUDIO.md).

## Estado y autoridad documental

El [plan aprobado](docs/PLAN_APROBADO.pdf) define el compromiso académico. El
[estado verificado](docs/ESTADO_VERIFICADO.md) describe qué existe realmente y
las [decisiones vigentes](docs/DECISIONES_VIGENTES.md) fundamentan la
arquitectura actual. Las ideas candidatas permanecen en
[IDEAS_Y_ROADMAP.md](docs/IDEAS_Y_ROADMAP.md) hasta ser promovidas mediante una
falla medida y una ablación definida.

Proyecto en desarrollo para la Maestría en Explotación de Datos y Gestión del
Conocimiento, Universidad Austral.

**Autor:** Lucas Brusasca

**Director:** Hernán Merlino
