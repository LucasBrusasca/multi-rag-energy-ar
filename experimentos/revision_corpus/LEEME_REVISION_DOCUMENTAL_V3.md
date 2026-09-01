# Revisión documental: una ficha por documento

## Archivo para Lucas

Abrir `revision_documental_v3.html` en el navegador. La v2 queda intacta.

1. Elegir un documento en la lista de la izquierda y abrir su original.
2. Indicar si sirve, si hay dudas o si se propone excluirlo. Completar los datos
   que se puedan verificar. Las ayudas debajo de cada campo explican qué mirar.
3. Escribir páginas/celdas de referencia y comentarios, dudas o problemas.
4. Pulsar **Guardar mi lectura y comparar en esta ficha**. La primera lectura
   se conserva. La sugerencia aparece en el mismo documento; los campos ya
   escritos pasan a ser la decisión final y no hay que rellenarlos otra vez.
5. Mantener o ajustar el criterio y pulsar **Terminar este documento y pasar al
   siguiente**. Una ficha terminada con dudas sigue pendiente de resolución:
   no es un documento validado.

**Guardar borrador y pasar al siguiente** permite postergar un documento sin
marcarlo como terminado. Se puede volver con la lista, la búsqueda o el filtro.

## Dominios de conocimiento: qué se está marcando

Se marca un tema cuando se puede **señalar** un pasaje o una tabla que aporte una
regla, una explicación o un dato concreto de ese tema. No hace falta que sea el
tema principal ni que ocupe un capítulo, y no hay umbral de menciones. Nombrarlo
al pasar, o remitir a otro documento sin desarrollarlo, no alcanza.

**Dominio documental ≠ pertinencia por fragmento.** Marcar `contable` en la
ficha dice que el documento *contiene* materia contable. No dice que todos sus
fragmentos sean contables, ni los asigna a ese silo: la etiqueta documental **no
se hereda** (`docs/DECISION_ARQUITECTURA_MULTILABEL.md`, regla 3). Un documento
mixto es perfectamente compatible con que cada fragmento tenga un único dominio.
La pertinencia por fragmento se decide en `chunk_domain_membership`, en otro
instrumento y con otra evidencia.

Cada dominio tiene una descripción visible y un desplegable «Qué incluye / Qué no
alcanza / Ejemplo», con ejemplos para normas, informes y planillas. Los ejemplos
son ejemplos: ningún tipo de archivo determina por sí solo un tema.

Las descripciones se contrastaron contra `config.SILOS`. Las diferencias
encontradas, y las dos que quedaron abiertas, están en
`reports/contraste_dominios_2026-08-30.md`. Las dos abiertas:

- **`regulatorio` no es un quinto tema.** Se mantienen cuatro silos: la materia
  regulatoria energética ya está dentro de «Legal / regulatorio energético», que
  conserva el identificador `legal`. Cuidado con la etiqueta histórica: en el
  catálogo viejo, `regulatorio` aparece en 10 documentos que **no** llevan
  `legal` —siete estados contables, una memoria anual, una presentación
  corporativa y un informe de calificación—. La hipótesis es que ahí significaba
  «esta empresa opera en un sector regulado»; **no está verificada**, porque
  ninguno de esos documentos se leyó todavía. En este campo, marcá el tema solo
  si podés señalar el pasaje. Detalle en
  `reports/revision_regulatorio_2026-08-30.md`.
- **Se marca por materia, no por forma jurídica.** Una ley tributaria sigue
  siendo una ley y aun así es `impositivo`, no `legal`.
- **Los conteos automáticos salieron de la vista principal.** Se muestran pasaje,
  página y el término encontrado; los umbrales quedan en el desplegable «Registro
  técnico», conservados para el registro. Ocultarlos reduce el anclaje pero **no
  convierte una revisión asistida en una lectura ciega**: quien ya vio la
  propuesta, la vio. La interfaz lo dice en pantalla.

## Criterio versionado y antecedentes

- Cada ficha **nueva** queda sellada con la versión del criterio vigente
  (`criterio-dominios-2026-08-30`) al guardar la primera lectura, y cada cierre
  queda sellado en el historial.
- Los registros anteriores **no se resellan**. Una ficha ya iniciada conserva su
  versión —o ninguna, si es anterior al versionado— aunque el archivo se
  regenere. Regenerar el HTML no reescribe la historia de una decisión.
- El JSON exportado declara `criterio_version` y `criterio_resumen`.
- Si antes de leer ya se había visto la propuesta automática o una revisión
  previa, hay una casilla para **declararlo**. El sistema no puede saberlo por su
  cuenta, así que la única opción honesta es dejarlo declarar: la lectura se
  registra como `revision_con_antecedente_declarado` y no como independiente. La
  casilla se bloquea una vez guardada la primera lectura.

## Guardado y recuperación

- El guardado automático usa una clave nueva del navegador, separada de la v2.
- Descargar el avance JSON en cualquier momento, incluso con una sola ficha.
- Antes de cambiar de navegador o mover el HTML, descargar un respaldo.
- **Recuperar avance** admite JSON v3 y JSON exportado desde v2 con la misma
  huella del inventario. Las fichas ya iniciadas en v3 no se sobrescriben.
- La v3 no puede recuperar automáticamente decisiones que estén únicamente en
  el almacenamiento de otra página o navegador. Exportarlas primero desde v2.
- La revisión v2 se conserva íntegra como antecedente. No se inventan campos a
  partir de la propuesta ni se supone que un «confirmar» vacío equivale a una
  ficha completa. Su nueva revisión no se declara independiente de la v2.
- JSON v3 es un formato versionado. No usar importadores de catálogo que solo
  interpreten CSV/JSON v2 sin adaptar y validar primero la correspondencia.

## Alcance y límites

El inventario y las propuestas proceden del snapshot embebido en
`revision_corpus_v2.html`: 59 documentos, sin agregar las 150 normas InfoLEG.
No se modifica catálogo, ingesta, embeddings, PostgreSQL ni decisiones previas.
Esta revisión documental no sustituye el Golden de preguntas y evidencias.

La propuesta no se presenta antes de guardar la primera lectura. Sigue embebida
en el archivo offline: esto es un resguardo del flujo de revisión, no un control
de acceso contra quien inspeccione el código fuente.

## Reproducir

Desde la raíz del proyecto:

```powershell
.venv/Scripts/python.exe scripts/diagnostics/generar_revision_documental_v3.py
.venv/Scripts/python.exe -m unittest tests.test_revision_documental_v3 tests.test_revision_documental_v3_dominios tests.test_interfaz_corpus_v2 tests.test_interfaz_corpus
```

Fuentes de interfaz en `scripts/diagnostics/revision_documental/`; el generador
inserta HTML, estilos, JavaScript e inventario en un archivo offline único.

Se probaron validación, fechas, comentarios, revelado, cierre, exportación y
recuperación mediante la lógica JavaScript real ejecutada en Node. La apertura
visual automatizada fue bloqueada por la política del navegador de la sesión;
no se declara verificación visual ni prueba de descargas en navegador.

El generador admite `--demo --salida <otro-nombre.html>` para producir dos
documentos ficticios con guardado separado y probar sin contaminar decisiones
del corpus real.
