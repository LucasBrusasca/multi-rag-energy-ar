# Experimentos 24–26 jul 2026 — TODO EN SUSPENSO

> **Estado de este directorio: EN SUSPENSO.**
> Ningún número de acá se usa como evidencia de la tesis hasta que **Lucas lo corra y verifique**.
> Los scripts se preservan para que sean **auditables desde el repo**, no para respaldar afirmaciones.
>
> Las reservas transversales están consolidadas en
> [`../LECCIONES_METODOLOGICAS.md`](../LECCIONES_METODOLOGICAS.md).

> ### Qué es y qué no es este directorio
>
> - **Código exploratorio e histórico.** Es el registro de una sesión de trabajo
>   de julio de 2026, conservado tal como quedó. No se mantiene, no se
>   actualiza y no se corrige salvo para dejar constancia.
> - **NO forma parte del pipeline canónico.** El sistema vigente es
>   `src/multirag/` con sus utilidades en `scripts/`. Nada de este directorio se
>   importa, se ejecuta ni se prueba desde ahí. Un script de acá que coincida en
>   nombre con uno del pipeline **no es** su versión buena.
> - **Ningún resultado es confirmatorio.** Todo lo de acá es exploratorio. Las
>   afirmaciones de la tesis no se apoyan en estos números, y varios ya fueron
>   descartados o retractados (ver el detalle por script más abajo).
> - **Dependen del snapshot vigente al momento de ejecutarlos.** Leen la base
>   viva, no un corpus congelado: correrlos hoy puede dar números distintos de
>   los guardados en `resultados/`, sin que ninguno de los dos sea un error. Por
>   eso los resultados guardados no son verificables de forma independiente.

> ### `resultados/golden_anclas.json` no se publica
>
> Se conserva **localmente** pero queda fuera del repositorio: contiene
> fragmentos literales de los documentos fuente. Una publicación futura deberá
> usar una versión **sanitizada**, que reemplace el texto por identificadores
> (`document_id`, `artifact_id`), hashes y localizadores (página, artículo,
> `chunk_uid`). Los scripts que lo producen y lo consumen sí están en el repo,
> así que el archivo se regenera.

## Cómo correr cualquiera

Los scripts ya **no tienen rutas absolutas**: resuelven la raíz del repo y su carpeta de resultados
desde su propia ubicación. Desde la raíz del proyecto, con el `.venv` activo y Docker levantado:

```bash
python experimentos/2026-07-26_estado/scripts/<nombre>.py
```

**Requisitos por script** (varían): base Postgres levantada · Ollama corriendo (`gemma4:latest`) ·
créditos de API Anthropic (solo los de generación con LLM remoto).

**Reproducibilidad:** los scripts fijan `seed=7` y `temperature=0` cuando corresponde.

---

## Los 6 que conviene auditar primero

| script | qué mide | por qué importa |
|---|---|---|
| `verificacion_total.py` | Integridad de la base, schema vs código y constantes | Punto de partida para verificar el estado del proyecto |
| `router_gemma.py` | Compara coseno vs Gemma-4 | Explora alternativas para el router |
| `no_interferencia.py` | Geometría del corpus al incorporar otros silos | Explora la interferencia entre dominios |
| `golden_colisiones.py` | Descubre del corpus los términos que viven en 2 silos (`agentes`, `compensación`, `firme`…) | Materia prima del Golden |
| `golden_anclas.py` | Saca los artículos reales donde vive cada término de colisión | Insumo del Golden |
| `auditoria_significancia.py` | Recalcula con tests exactos la significancia de los experimentos guardados | Es el que **descartó** varios resultados |

---

## Estado por script

### ⚠️ Utilidades o insumos — no son resultados confirmatorios

| script | resultado obtenido | reserva declarada |
|---|---|---|
| `verificacion_total.py` | chequeos del camino de ejecución y consistencia estructural | en suspenso hasta que Lucas lo ejecute |
| `router_gemma.py` | comparación parcial entre router por coseno y Gemma-4 | en suspenso |
| `no_interferencia.py` | medición exploratoria de cambios de vecindario entre silos | en suspenso |
| `golden_colisiones.py` / `golden_anclas.py` / `golden_colision_items.py` | términos y anclas de colisión del corpus | protocolo silver: fuga declarada |
| `a14_gratis_pureza.py` | test de A14 sin costo | quedó a medias (se cortó) |

### ❌ Descartados — arnés roto o n insuficiente

| script | por qué se descarta |
|---|---|
| `dosis.py` | detector con bug (`fuente.split("_")[0]` = "ley"/"decreto") → el p=0.0007 era artefacto |
| `dosis_recalculo.py` | el recálculo correcto con identificadores únicos de norma → **p=0.53, no significativo** |
| `abstencion.py`, `fusion.py` | n=8 y **0 pares discordantes**. Cero señal, imposible de concluir |
| `fusion_falsa.py` | n=9; 3 casos perdidos por falta de CPU (dos procesos pesados en paralelo) |
| `colision_pares_minimos.py` | las preguntas llevaban el dominio adentro ("agentes **del mercado eléctrico**") → nunca colisionan |
| `router_llm.py` | Qwen-3B sobre **títulos**; el título salió del mismo centroide contra el que se compara (fuga) |
| `router_preguntas.py` | corrida cortada a mitad |

### ❌ Descartados por circularidad

| script | por qué |
|---|---|
| `geometria.py` | pureza de vecindario medida con **las mismas etiquetas y el mismo embedder** que las generó |
| `pureza_por_embedder.py` | mismo defecto: compara embedders contra etiquetas que produjo bge-m3 |
| `espacios_por_silo.py`, `normalizacion.py` | PCA/blanqueo **no son** los embedders especializados que pide el plan |

### Resto (sesión 24–25 jul)

`afinar.py` · `algebra.py` · `coherencia.py` · `compresion.py` · `densidad.py` · `ecuacion.py` ·
`escala.py` · `estratos.py` · `final*.py` · `frontera*.py` · `gamma.py` · `grafo.py` · `hibrido.py` ·
`k_justo.py` · `k_paridad.py` · `lda_cv.py` · `lda_fino.py` · `metricas.py` · `picos.py` ·
`proporcional.py` · `reanalisis.py` · `regla_final.py` · `rescate*.py` · `routers.py` · `seis.py` ·
`sin_arrepentimiento.py` · `vigencia*.py` y otros.

Las retractaciones y reglas metodológicas comunes están en
[`../LECCIONES_METODOLOGICAS.md`](../LECCIONES_METODOLOGICAS.md). El detalle por script y
sus resultados crudos permanece en este directorio.

⚠️ **Advertencia metodológica que aplica a casi todos:** usan el **protocolo silver** (el título de un
chunk como consulta, los chunks hermanos como objetivo). Tiene **fuga declarada** título→chunk y
**favorece sistemáticamente al monolítico**. Sirve para comparar brazos entre sí, **no** como
evidencia primaria de la tesis.

---

## Qué falta para que esto sea reproducible de verdad

Lo que hay acá es el código y los resultados crudos. **Falta la cadena completa:**

- [ ] `chunks_snapshot.parquet` — el corpus congelado (hoy los scripts leen la base viva)
- [ ] `manifest.json` — cantidad, fuentes, distribución, commit, SHA-256
- [ ] `split.json` — train/dev/test bloqueado **por documento**, sin fuga
- [ ] Versión de modelos y prompts usados en cada corrida
- [ ] Los resultados crudos con su hash

**Sin eso, un tercero no puede reproducir estos números — y por eso están en suspenso.**
