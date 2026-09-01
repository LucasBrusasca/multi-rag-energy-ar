# Completitud de los hechos del extractor table-aware

**Hechos:** 11.167 · **Documentos:** 8 · **Tablas lógicas:** 442

**Huella del insumo:** `sha256:b19223730c2c999e68617f7d323667fb…`

**Receta de extracción:** `tablas-v0.1` · **Parser:** `docling 2.96.1`


> Mide **completitud**, no exactitud. No hay verdad de referencia tabular y el extractor
> no puede ser su propia referencia. Que un campo esté poblado no dice que el valor sea correcto.
> Es una métrica descriptiva **del extractor**, no del sistema de recuperación.


## 0 · Qué cuenta como poblado

Un centinela es un valor presente que significa «no se pudo determinar». Contarlo como
poblado inflaría la completitud sobre campos vacíos de contenido.


| campo | centinelas | `0` es centinela |
|---|---|---|
| `entidad` | `None`, `""`, **y `entidad == fuente`** (el extractor cae al nombre de archivo) | — |
| `concepto` (`row_label`) | `None`, `""`, solo puntos (`Información Legal ......`) | — |
| `valor` | `None` | **no** — un hecho puede valer 0 |
| `escala`, `moneda` | `None`, o `unit` ausente | — |
| `periodo` | `None`, o todos sus campos nulos | — |
| `ubicación` | `source_pages` vacío **y** `hoja` nula | **sí** en página: Docling numera desde 1 |
| `fila`, `columna` | `None` | **no** — la grilla es 0-indexada, `(0,0)` existe |

Texto tratado como nulo: `-`, `--`, `desconocido`, `n/a`, `na`, `no disponible`, `none`, `null`, `s/d`, `sd`.


### De dónde sale la confianza

De una **regla determinística del propio extractor** (`hechos.py`, `_confianza()`): no interviene
ningún LLM ni heurística aprendida. Depende de cuatro entradas: si hay `column_path`, si el
encabezado fue heredado de otra tabla, el origen de la unidad y si hay período declarado.


**No considera la ausencia de escala.** La función recibe únicamente las advertencias **de la
celda**; `escala_ausente` y `moneda_inferida_de_simbolo_pesos` se generan a nivel de **segmento**
y nunca llegan al cálculo. Por eso el punto 4 se redacta como **«la confianza no mide
completitud»** y no como descalibración: no es que mida mal algo que intenta medir, es que
nunca miró ese componente.


## 1 · Tipología propuesta — PENDIENTE DE RATIFICACIÓN

La obligatoriedad es **condicional al tipo**: una alícuota no tiene moneda, un ratio no tiene
escala en pesos. Exigírselos contaría como incompleto algo que el documento nunca declaró.


**Regla que evita circularidad:** el tipo se decide por la **forma del valor** y el **léxico de
la etiqueta**, nunca por los campos cuya completitud se está midiendo. Clasificar como
«monetario» porque tiene moneda, y después medir si tiene moneda, no mediría nada.


| tipo | hechos | % | componentes obligatorios |
|---|---:|---:|---|
| **monetario_presunto** | 9.332 |  83.6 % | `concepto`. `valor`. `escala`. `moneda`. `periodo` |
| **porcentaje_ratio** | 1.219 |  10.9 % | `concepto`. `valor`. `periodo` |
| **conteo** | 439 |   3.9 % | `concepto`. `valor`. `periodo` |
| **temporal** | 0 |   0.0 % | `concepto` |
| **no_interpretable** | 177 |   1.6 % | `concepto` |

`monetario_presunto` se llama *presunto* a propósito: se presume monetario por ser un estado
contable y no declarar porcentaje ni fecha. No se usa el campo `moneda` para decidirlo.


## 2a · Completitud semántica


| componente | poblados | % |
|---|---:|---:|
| `entidad` | 0 |   0.0 % |
| `concepto` | 10.798 |  96.7 % |
| `valor` | 10.990 |  98.4 % |
| `escala` | 5.034 |  45.1 % |
| `moneda` | 7.594 |  68.0 % |
| `periodo` | 7.263 |  65.0 % |

**Completitud exacta** (todos los obligatorios de su tipo, poblados):


| tipo | hechos | exactos | % |
|---|---:|---:|---:|
| monetario_presunto | 9.332 | 2.621 |  28.1 % |
| porcentaje_ratio | 1.219 | 763 |  62.6 % |
| conteo | 439 | 241 |  54.9 % |
| temporal | 0 | 0 |     —  |
| no_interpretable | 177 | 139 |  78.5 % |
| **global** | **11.167** | **3.764** | ** 33.7 %** |

## 2b · Completitud de procedencia


| componente | poblados | % |
|---|---:|---:|
| `documento` | 11.167 | 100.0 % |
| `ubicacion` | 11.167 | 100.0 % |
| `tabla` | 11.167 | 100.0 % |
| `fila` | 11.167 | 100.0 % |
| `columna` | 11.167 | 100.0 % |

**Completitud exacta** (todos los obligatorios de su tipo, poblados):


| tipo | hechos | exactos | % |
|---|---:|---:|---:|
| monetario_presunto | 9.332 | 9.332 | 100.0 % |
| porcentaje_ratio | 1.219 | 1.219 | 100.0 % |
| conteo | 439 | 439 | 100.0 % |
| temporal | 0 | 0 |     —  |
| no_interpretable | 177 | 177 | 100.0 % |
| **global** | **11.167** | **11.167** | **100.0 %** |

### Componente no extraído

`alcance` (consolidado/individual, escenario) **no existe como campo** en el extractor. No se
reporta como 0 % de completitud —sería leerlo como dato faltante— sino como fuera del alcance
actual de extracción. Si se decide exigirlo, hay que agregarlo primero al modelo.


## 3 · Unidad de análisis

El agregado sobre todos los hechos es **pseudorreplicación**: salen de pocos documentos, y los
hechos del mismo documento comparten parser, maquetado y errores. El número global se reporta,
pero la distribución es la que manda.


| documento | hechos | % del total | compl. sem. exacta | compl. proc. exacta |
|---|---:|---:|---:|---:|
| TGS_EEFF_2025_09 | 2.906 |  26.0 % |  32.1 % | 100.0 % |
| Pampa_EEFF_Consolidado_1Q2026 | 1.828 |  16.4 % |  38.1 % | 100.0 % |
| Estados_Contables_Neuquen | 1.759 |  15.8 % |  18.8 % | 100.0 % |
| Edenor_EEFF_Consolidado_2025_09 | 1.447 |  13.0 % |  27.8 % | 100.0 % |
| EEFF-ind-31-03-2019 | 1.243 |  11.1 % |  36.4 % | 100.0 % |
| FS-31-03-2019 | 917 |   8.2 % |  47.4 % | 100.0 % |
| TR-consolidado-03-2026_VF-Clean | 916 |   8.2 % |  43.3 % | 100.0 % |
| MSU_ON_ClaseIV | 151 |   1.4 % |  76.8 % | 100.0 % |

**Concentración:** los 3 documentos más grandes aportan ** 58.1 %** de los hechos.


**Por tabla:** 442 tablas lógicas. Mediana de hechos por tabla: 16. Máximo: 213.


## 4 · Confianza declarada contra completitud real

**La confianza no mide completitud.** No es descalibración: la regla nunca mira la ausencia de
escala ni la moneda inferida (ver §0). El cruce muestra el tamaño de esa ceguera.


| tipo | confianza | hechos | compl. sem. exacta |
|---|---|---:|---:|
| monetario_presunto | alta | 128 |  59.4 % |
| monetario_presunto | media | 8.902 |  28.6 % |
| monetario_presunto | baja | 302 |   0.0 % |
| porcentaje_ratio | alta | 84 | 100.0 % |
| porcentaje_ratio | media | 1.019 |  66.6 % |
| porcentaje_ratio | baja | 116 |   0.0 % |
| conteo | media | 427 |  56.4 % |
| conteo | baja | 12 |   0.0 % |
| no_interpretable | baja | 177 |  78.5 % |

### Caso testigo — no corregido


**53 hechos** con `confianza: alta` y `escala_ausente`. Se sabe la moneda y no la
escala: el número puede estar mil veces mal y se presenta como alta confianza.


```text
Estados_Contables_Neuquen  Petróleo                       = 75.551.037     moneda=ARS escala=None
Estados_Contables_Neuquen  Petróleo                       = 21.601.837     moneda=ARS escala=None
Estados_Contables_Neuquen  Gas                            = 1.543.027      moneda=ARS escala=None
Estados_Contables_Neuquen  Derecho de Asociación y otros  = 108.482.500    moneda=ARS escala=None
```

## Limitaciones

1. **Completitud no es exactitud.** Un campo poblado puede estar mal. Medir exactitud exige
   verificación humana contra el documento fuente; el piloto del punto 5 la prepara.

2. **Regenerable, no reproducible por un tercero.** El extractor es determinístico (sin
   aleatoriedad, sin LLM, sin temperatura) y las conversiones de Docling están cacheadas en el
   repo. Pero al momento de esta corrida el código **no estaba versionado** (`scripts/diagnostics/`
   y `src/multirag/ingestion/tablas/` figuran sin trackear en git), y la corrida original escribió
   a un directorio temporal. Hasta commitear, los números se pueden regenerar en esta máquina
   pero no auditar desde afuera.

3. **Pseudorreplicación.** Ver §3. Ningún número global debe leerse como una tasa poblacional.

4. **La tipología está sin ratificar.** Cambiarla cambia todos los números de completitud
   exacta, porque la obligatoriedad depende del tipo.


## Trazabilidad

| | |
|---|---|
| insumo | `experimentos\prototipo_tablas\hechos.jsonl` |
| huella del insumo | `sha256:b19223730c2c999e68617f7d323667fba0556bd38c951f67c760670543694fe6` |
| hechos | 11.167 |
| script | `scripts/diagnostics/caracterizar_completitud.py` |
| receta de extracción | `tablas-v0.1` |
| parser | `docling 2.96.1` |

Para regenerar estos números:


```bash
python -m scripts.diagnostics.caracterizar_completitud
```


Si la huella del insumo no coincide con la de arriba, los números no son estos.
