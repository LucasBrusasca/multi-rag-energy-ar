# Contraste: ayuda de dominios de la v3 vs. definiciones documentadas

Fecha: 30-ago-2026. Alcance: solamente la ayuda que lee la persona en
`experimentos/revision_corpus/revision_documental_v3.html`. **No se cambió el
significado de ninguna etiqueta, ni el corpus, ni la clasificación persistida,
ni la base de datos.**

Fuentes contrastadas:

- `src/multirag/config.py` → `SILOS` (definición vigente de los cuatro dominios).
- `src/multirag/config.py` → `MATERIALIDADES`.
- `docs/DECISION_ARQUITECTURA_MULTILABEL.md` (etiqueta documental vs. fragmento).
- La ayuda anterior de la v3, embebida en `interfaz.js`.

## Las cuatro contradicciones encontradas

### C1 — `legal` decía algo mucho más amplio que la definición del proyecto

- La ayuda anterior decía: «Normas, obligaciones, contratos o regulación.»
- `SILOS["legal"]` dice: «Materia jurídico-regulatoria **del sector
  energético**: organización del mercado eléctrico y de gas; […] concesiones,
  licencias […]; régimen tarifario y audiencias públicas; facultades de ENRE,
  ENARGAS, Secretaría de Energía […]».

Con la redacción anterior, una ley impositiva es «una norma» y por lo tanto
`legal`. Con `SILOS`, esa misma ley es `impositivo` y no `legal`, porque `legal`
está acotado al sector energético. La diferencia no es de matiz: cambia la
etiqueta de cualquier documento normativo que no sea del sector.

**Resuelto en la ayuda nueva** siguiendo `SILOS`: la descripción visible dice
«Reglas del sector energético», y el desplegable enumera los mismos elementos
que `SILOS`. **Nadie reetiquetó nada**: esto solo afecta lo que se le muestra a
la persona de acá en adelante.

### C2 — «financiero» en el habla corriente ≠ `financiero` en `SILOS`

`SILOS["contable"]` incluye textualmente «Estados contables **y financieros**».
Es decir: **un juego de estados financieros es `contable`**, no `financiero`,
aunque el archivo se llame «estados financieros». La lectura de sentido común
dice exactamente lo contrario, y la ayuda anterior («Financiero: financiación,
deuda, inversión o análisis financiero») no lo desambiguaba.

**Resuelto en la ayuda nueva**: es el desplegable «Contable o financiero: cómo
distinguirlos» y el aviso destacado sobre la casilla `contable`. Es una
aclaración de la definición existente, no un cambio de definición.

### C3 — `regulatorio` existe en los datos y no existe como casilla ✅ RESUELTA (30-ago-2026)

> **Actualización.** Resuelta por decisión: se mantienen cuatro silos, el nombre
> visible pasa a **«Legal / regulatorio energético»** y el identificador sigue
> siendo `legal`. Al revisar los registros apareció algo que esta sección no
> sabía: `regulatorio` se usó con **dos sentidos**, y en 10 de 17 documentos no
> significa materia jurídica. Ver `reports/revision_regulatorio_2026-08-30.md`
> y la decisión en `docs/DECISION_ARQUITECTURA_MULTILABEL.md`. El texto que
> sigue se conserva como estaba cuando se escribió.



El catálogo tiene `regulatorio` como valor de `dominios_documentales` en 17 de
los 24 documentos canónicos, pero `regulatorio` **no es uno de los cuatro
silos**. `docs/DECISION_ARQUITECTURA_MULTILABEL.md` registra esto como una
pregunta explícitamente **no decidida**: si `regulatorio` se mapea a `legal` o
si es un silo que falta.

La interfaz ofrece cuatro casillas, así que **una persona que quiera decir
«esto es regulatorio pero no encaja en legal» no tiene cómo escribirlo**.

**NO se resolvió acá**, porque resolverlo sería agregar una categoría nueva y
eso está fuera del encargo. Mitigación aplicada: la ayuda de `legal` describe
explícitamente el alcance regulatorio energético, así que el caso frecuente
(regulación del sector) tiene dónde ir. El caso residual —regulación no
energética— sigue sin casilla; corresponde escribirlo en comentarios.

👉 **Decisión pendiente de dirección**, no de implementación.

### C4 — Dos instrumentos con dos criterios distintos, en la misma pantalla ⚠️ MITIGADA, NO ELIMINADA

> **Actualización (30-ago-2026).** Los conteos salieron de la vista principal:
> ahora se muestran pasaje, página y el término encontrado, y los umbrales
> (`motivo`, `ocurrencias`, `terminos`, `paginas_termino`) quedan en un
> desplegable «Registro técnico», conservados. Se agregó un aviso explícito:
> a partir del revelado, la ficha es una **revisión asistida, no una lectura
> ciega**, y ocultar los conteos no cambia eso. El texto que sigue se conserva.



La propuesta automática usa umbrales de conteo (≥3 términos distintos, ≥6
ocurrencias, ≥2 páginas) y el panel de evidencia **muestra esos conteos**. La
consigna humana nueva prohíbe expresamente los umbrales de cantidad: alcanza con
poder señalar un pasaje.

Los dos criterios son distintos a propósito —el automático necesita un corte
mecánico, la persona no—, pero conviven en la misma ficha, y la persona ve los
conteos después de guardar su lectura. El riesgo es de anclaje: que empiece a
razonar con los umbrales de la máquina.

**Mitigado, no eliminado**: la propuesta no se muestra hasta después de guardar
la primera lectura, y la primera lectura queda congelada en `inicial`. Pero a
partir del segundo documento la persona ya conoce el criterio automático. **Esto
es una limitación del instrumento, y queda declarada.**

## Lo que NO se tocó

- No se agregaron categorías nuevas.
- No se modificó el corpus, el catálogo, la clasificación persistida ni PostgreSQL.
- No se reetiquetó ni un documento.
- No se cambió el flujo por documento.
- Ninguna decisión ya guardada fue modificada, ni se le atribuyó el criterio nuevo.
