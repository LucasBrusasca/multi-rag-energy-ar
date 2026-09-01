# Lecciones metodológicas y retractaciones

Este archivo conserva las lecciones que deben respetar futuras evaluaciones. Los resultados
de estas campañas son exploratorios y no constituyen evidencia confirmatoria de la tesis.

## 1. Separar desarrollo y test

Repetir pruebas sobre el mismo corpus y las mismas preguntas, eligiendo después métricas,
umbrales o configuraciones, convierte ese material en desarrollo. El test confirmatorio debe
estar compuesto por documentos y preguntas independientes y abrirse una sola vez.

## 2. Dividir por documento, no por chunk

Excluir solo el chunk consultado deja chunks hermanos del mismo documento en entrenamiento
o recuperación. Eso filtra estilo, vocabulario y estructura documental. El split y la
incertidumbre estadística deben agruparse por `document_id`.

## 3. Evitar circularidad

No es válido evaluar pureza o calidad de un espacio usando como verdad etiquetas producidas
por el mismo embedder o clasificador. Tampoco `silos_necesarios` puede provenir del router
que se evalúa. La referencia debe derivarse de lectura y evidencia documental.

## 4. Definir correctamente el éxito multidominio

Si una pregunta necesita dos o más silos, recuperar solo uno no es éxito. La cobertura del
router es exacta respecto del conjunto completo de `silos_necesarios`.

## 5. Controlar igualdad entre brazos

B0, B1 y B2 deben usar el mismo embedder, `k` final, presupuesto de contexto, generador,
prompt, veto, reranker y semilla. Dar más chunks a un brazo confunde segregación con
presupuesto de recuperación.

## 6. Auditar detectores antes de calcular estadística

Un detector de cita intrusa basado en palabras genéricas como “ley” o “decreto” produjo
una señal espuria. Todo resultado derivado debe vincularse con la versión exacta del
detector y validarse sobre ejemplos positivos y negativos.

## 7. Verificar viabilidad estadística antes de correr

Experimentos con muy pocos ítems o cero pares discordantes no permiten concluir superioridad
ni equivalencia. El tamaño confirmatorio se calcula después de un piloto usando discordancia,
dependencia documental, efecto mínimo relevante e incertidumbre conservadora.

## 8. Diferenciar ausencia de evidencia de evidencia de ausencia

Que un efecto no resulte significativo en un diseño pequeño o defectuoso no demuestra que
el efecto no exista. La redacción correcta es “no establecido bajo este diseño”.

## 9. Fallar en voz alta ante salidas no utilizables

Un arnés de router truncó el razonamiento del modelo y convirtió respuestas vacías en errores
de clasificación; otro parser tomó una mención preliminar en vez del veredicto final.
Cada corrida debe registrar `TRUNCADO`, `VACÍO`, `SIN_ETIQUETA` y `ERROR`, y abortar si la
tasa no utilizable supera el umbral preregistrado.

## 10. Preservar trazabilidad de la corrida

Cada resultado debe conservar:

- script y versión del código;
- snapshot y hash del corpus;
- split documental;
- modelos, prompts y parámetros;
- semilla;
- salida cruda;
- versión de detectores y métricas;
- procedimiento estadístico.

Sin esta cadena, un porcentaje puede servir para diagnóstico, pero no para sostener una
afirmación científica.

## Retractaciones que siguen vigentes

| familia | motivo |
|---|---|
| dosis de contaminación | detector de cita intrusa defectuoso; el efecto no quedó establecido |
| abstención y fusión falsa | tamaño insuficiente y ausencia de pares discordantes |
| consultas creadas desde títulos de chunks | fuga entre consulta y corpus; no representan preguntas naturales |
| pureza geométrica con etiquetas automáticas | circularidad entre representación y verdad de referencia |
| PCA o blanqueo por silo | no equivalen a embeddings expertos entrenados |
| split simple por chunk | fuga documental |
| router LLM con salida truncada o parser preliminar | arnés inválido |

Los detalles por script y las salidas crudas permanecen en los subdirectorios fechados.
