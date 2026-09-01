# Planilla para escribir el Golden

**Qué es esto y para qué sirve.**

El Golden es el instrumento de medición de tu tesis: el conjunto de preguntas con la
respuesta correcta ya conocida y verificada. Sin él no se puede medir si B1 recupera mejor
que B0, porque no habría contra qué comparar. Es lo único del experimento que no puede
hacer una máquina.

Cada pregunta necesita tres cosas:

1. **Una pregunta realista**, del tipo que haría alguien que trabaja en el sector.
2. **La evidencia**: el fragmento concreto del corpus que la responde. No "está en la Ley
   24.065", sino el artículo exacto.
3. **Los dominios que hacen falta** para responderla: `legal`, `impositivo`, `contable` o
   `financiero`.

## Por qué las preguntas de colisión son las importantes

Tu hipótesis dice que segregar por dominio reduce la contaminación entre dominios. Una
pregunta solo puede confirmarla o refutarla si **hay algo que pueda contaminar**.

Un ítem de colisión tiene esa forma: la respuesta está en el dominio A, y existe otro
fragmento del dominio B que se le parece mucho por vocabulario pero **no sirve para
responder**. Si el sistema monolítico trae el equivocado y el segregado no, eso es
exactamente lo que tu tesis afirma.

Esta planilla te da esos pares ya buscados. Lo difícil de escribir un ítem de colisión no
es la pregunta: es encontrar un distractor plausible. Eso ya está hecho.

## Cómo trabajar con esto

Para cada bloque:

1. **Leé la evidencia.** Preguntate: ¿qué consulta real se respondería con esto?
2. **Mirá el distractor.** ¿Un buscador podría traerlo por parecido de palabras, aunque no
   sirva para responder?
   - Si **sí** → tenés un ítem de colisión. Escribí la pregunta.
   - Si el distractor **también responde** → no es colisión. Marcá `distractor_valido: no` y
     seguí de largo. Vas a descartar varios, es normal.
3. **Completá el bloque `COMPLETAR`.** Son cinco campos.

No busques que la pregunta salga perfecta. Salen mejores escribiendo diez que pensando una.

## Ejemplo, con un ítem que ya escribiste

De tu piloto (`G-P-005`):

> **pregunta:** "¿Qué sanciones corresponden por violar la ley del sector eléctrico,
> cometidas por terceros no concesionarios?"
> **evidencia:** Ley 24.065, artículo 63
> **silos_necesarios:** `[legal]`

Funciona como colisión porque "sanciones" también aparece en materia impositiva —multas
fiscales, intereses resarcitorios— y un buscador sin gobierno puede traer el régimen
sancionatorio equivocado.

## Los cinco campos que tenés que completar

| campo | qué poner |
|---|---|
| `pregunta` | La consulta, redactada como la haría una persona real. |
| `respuesta_referencia` | La respuesta correcta, breve. Una o dos oraciones. |
| `silos_necesarios` | Qué dominios hacen falta para responder. Casi siempre uno. |
| `dominios_evidencia` | De qué dominio es **el fragmento** de evidencia. Suele coincidir con el anterior, pero no siempre. |
| `distractor_valido` | `si` si el distractor se parece pero no responde. `no` si también responde. |

Todo lo demás —`document_id`, `artifact_id`, `sha256`, `chunk_uid`, `emisor_id`, el silo
persistido y los campos derivados— se completa solo después, desde el catálogo y la base.

⚠️ **Un aviso metodológico.** El parecido entre ancla y distractor lo calculó el embedding, y
es solo una ayuda para buscar. Que un par aparezca acá **no** lo convierte en colisión: eso
lo decidís leyendo. Y el dominio del distractor tiene que salir de tu lectura de su
contenido, nunca del silo automático.

---


## Ítem 1

> 📊 **La evidencia es una tabla.** Estos ítems son los que demuestran la parte multimodal de la tesis: priorizalos.

### Evidencia — dominio `financiero`

**Transener_Calificacion_FIX** · informe_calificacion · FIX SCR S.A.<br>
`DOC-0024` · ubicación: Anexo I. Resumen Financiero

> Flujo de Caja Operativo (FCO), (30.716) = 204.545. Flujo de Caja Operativo (FCO), (32.572) = 139.724. Flujo de Caja Operativo (FCO), (50.685) = 165.338. Flujo de Caja Operativo (FCO), (29.874) = 51.677. Flujo de Caja Operativo (FCO), (28.169) = 26.624. Flujo de Caja Operativo (FCO), 10.865 = 52.976. Flujo de Caja No Operativo / No Recurrente Total, (30.716) = (2). Flujo de Caja No Operativo / No Recurrente Total, (32.572) = (1). Flujo de Caja No Operativo / No Recurrente Total, (50.685) = (1). Flujo de Caja No Operativo / No Recurrente Total, (29.874) = 0. Flujo de Caja No Operativo / No Recurrente Total, (28.169) = 0. Flujo de Caja No Operativo / No Recurrente Total, 10.865 = 0. Inversiones de Capital, (30.716) = (76.223). Inversiones de Capital, (32.572) = (52.198). Inversiones de Capital, (50.685) = (58.424). Inversiones de Capital, (29.874) = (44.396). Inversiones de Capital, (28.169) = (27.195). Inversiones de Capital, 10.865 = (26.637). Dividendos, (30.716) = (134.200). Dividendos, (32.572) = (134.200). Dividendos, (50.685) = 0. Dividendos, (29.874) = 0. Dividendos, (28.169) = 0. Dividendos, 10.865 = 0. Flujo de Fondos Libre (FFL), (30.716) = (5.878). Flujo de Fondos Libre (F...

### Distractor candidato — dominio `contable` · parecido `0.78`

**Edenor_EEFF_Consolidado_2025_09**

> Flujo neto de efectivo generado por las actividades operativas, 30.09.25 = 136.110. Flujo neto de efectivo generado por las actividades operativas, 30.09.24 = 174.558. Flujo neto de efectivo generado por las actividades operativas, 30.09.23 = 176.012. Flujo neto de efectivo generado por las actividades operativas, 30.09.22 = 218.310. Flujo neto de efectivo generado por las actividades operativas, 30.09.21 = 306.615. Flujo neto de efectivo utilizado en las actividades de inversión, 30.09.25 = (25...

### COMPLETAR

```yaml
item: 1
pregunta: ""
respuesta_referencia: ""
silos_necesarios: [financiero]
dominios_evidencia: [financiero]
distractor_valido:
```

<sub>chunk evidencia: `5727b090aedcd7ad04d157e539f31f30191ce840964cc53a2e41262c312843e9` · chunk distractor: `cba3ca8cd1e064e295f177247b04580e77a24a1f6e5efa532e0e7d65161738f1`</sub>

---

## Ítem 2

> 📊 **La evidencia es una tabla.** Estos ítems son los que demuestran la parte multimodal de la tesis: priorizalos.

### Evidencia — dominio `financiero`

**Transener_Calificacion_FIX** · informe_calificacion · FIX SCR S.A.<br>
`DOC-0024` · ubicación: Anexo I. Resumen Financiero

> Caja, Moneda Constante(*) = . Flujo de Caja, Moneda Constante(*) = . Flujo Generado por las Operaciones (FGO), Moneda Constante(*) = 235.261. Flujo Generado por las Operaciones (FGO), Moneda Constante(*) = 172.296. Flujo Generado por las Operaciones (FGO), Moneda Constante(*) = 216.024. Flujo Generado por las Operaciones (FGO), Moneda Constante(*) = 81.551. Flujo Generado por las Operaciones (FGO), Moneda Constante(*) = 54.793. Flujo Generado por las Operaciones (FGO), Moneda Constante(*) = 42.111

### Distractor candidato — dominio `contable` · parecido `0.74`

**Pampa_EEFF_Consolidado_1Q2026**

> Flujos netos de efectivo (aplicado a) generados por las actividades operativas, 31.03.2026 = (330.230). Flujos netos de efectivo (aplicado a) generados por las actividades operativas, 31.03.2025 = 93.885. Flujos netos de efectivo (aplicado a) generados por las actividades operativas, 31.03.2024 = (14.214). Flujos netos de efectivo aplicados a las actividades de inversión, 31.03.2026 = (290.751). Flujos netos de efectivo aplicados a las actividades de inversión, 31.03.2025 = (50.561). Flujos neto...

### COMPLETAR

```yaml
item: 2
pregunta: ""
respuesta_referencia: ""
silos_necesarios: [financiero]
dominios_evidencia: [financiero]
distractor_valido:
```

<sub>chunk evidencia: `6d74d719fe815b0406e87a915b68d229317b49b5612c5458fc6f688f57c34c55` · chunk distractor: `c3763f2b03392bfabfc9c85f54f1b4e77c8d9ccc753d3916bee588806dcb71aa`</sub>

---

## Ítem 3

> 📊 **La evidencia es una tabla.** Estos ítems son los que demuestran la parte multimodal de la tesis: priorizalos.

### Evidencia — dominio `financiero`

**Transener-Company-Presentation-April-2026** · presentacion_corporativa · Compañía de Transporte de Energía Eléctrica en Alta Tensión Transener S.A.<br>
`DOC-0023` · ubicación: RQT Tariff Schedule- Five year Projection in US$ MM

> Revenues, Year 1 = 123. Revenues, Year 2 = 122. Revenues, Year 3 = 121. Revenues, Year 4 = 119. Revenues, Year 5 = 118. Revenues, Average = 121. Revenues, % = 100%. Penalties, Year 1 = 1. Penalties, Year 2 = 1. Penalties, Year 3 = 1. Penalties, Year 4 = 1. Penalties, Year 5 = 1. Penalties, Average = 1. Penalties, % = 1%. Operating Costs, Year 1 = 45. Operating Costs, Year 2 = 44. Operating Costs, Year 3 = 43. Operating Costs, Year 4 = 42. Operating Costs, Year 5 = 42. Operating Costs, Average = 43. Operating Costs, % = 36%. Capex, Year 1 = 24. Capex, Year 2 = 24. Capex, Year 3 = 24. Capex, Year 4 = 24. Capex, Year 5 = 24. Capex, Average = 24. Capex, % = 20%. Income Tax, Year 1 = 24. Income Tax, Year 2 = 24. Income Tax, Year 3 = 23. Income Tax, Year 4 = 23. Income Tax, Year 5 = 22. Income Tax, Average = 23. Income Tax, % = 19%. Net Income, Year 1 = 30. Net Income, Year 2 = 30. Net Income, Year 3 = 30. Net Income, Year 4 = 30. Net Income, Year 5 = 30. Net Income, Average = 30. Net Income, % = 25%

### Distractor candidato — dominio `contable` · parecido `0.63`

**EEFF-ind-31-03-2019**

> Ingresos por ventas, Nota = 6. Ingresos por ventas, Período de tres meses finalizado el.31.03.2019 = 1.813.473. Ingresos por ventas, Período de tres meses finalizado el.31.03.2018 = 2.029.066. Costos de explotación, Nota = 7. Costos de explotación, Período de tres meses finalizado el.31.03.2019 = (733 . 946). Costos de explotación, Período de tres meses finalizado el.31.03.2018 = (762.996). Resultado bruto, Nota = . Resultado bruto, Período de tres meses finalizado el.31.03.2019 = 1.079.527. Res...

### COMPLETAR

```yaml
item: 3
pregunta: ""
respuesta_referencia: ""
silos_necesarios: [financiero]
dominios_evidencia: [financiero]
distractor_valido:
```

<sub>chunk evidencia: `85ccb15214fcb05d983ca23e9e35afe958101899bd9c543d8ac490b449275216` · chunk distractor: `f6ed43c3b0ff7d086c20dc7adbe50ccc3d4bde35a5a866e434ccce38f5915dbf`</sub>

---

## Ítem 4

### Evidencia — dominio `impositivo`

**Ley_20628_Impuesto_Ganancias_TO** · texto_ordenado · Honorable Congreso de la Nación Argentina<br>
`DOC-0010` · ubicación: Art. 79 - Constituyen ganancias de cuarta categoría las provenientes:

> a) Del desempeño de cargos públicos nacionales, provinciales, municipales y de la Ciudad Autónoma de Buenos Aires, sin excepción, incluidos los cargos electivos de los Poderes Ejecutivos y Legislativos. En el caso de los Magistrados, Funcionarios y Empleados del Poder Judicial de la Nación y de las provincias y del Ministerio Público de la Nación cuando su nombramiento hubiera ocurrido a partir del año 2017, inclusive. (Inciso sustituido por art. 1° pto. 5 de la Ley N° 27.346 B.O. 27/12/2016. Vigencia: a partir de su publicación en el Boletín Oficial y surtirá efecto a partir del año fiscal 2017, inclusive). b) Del trabajo personal ejecutado en relación de dependencia. c) De las jubilaciones, pensiones, retiros o subsidios de cualquier especie en cuanto tengan su origen en el trabajo personal y en la medida que hayan estado sujeto al pago del impuesto , y de los consejeros de las sociedades cooperativas. (Inciso sustituido por art. 1° pto. 5 de la Ley N° 27.346 B.O. 27/12/2016. Vigencia: a partir de su publicación en el Boletín Oficial y surtirá efecto a partir del año fiscal 2017, inclusive). d) De los beneficios netos de aportes no deducibles, derivados del cumplimiento de los re...

### Distractor candidato — dominio `contable` · parecido `0.64`

**TGS_EEFF_2024_4T**

> El cargo por impuesto a las ganancias incluye el impuesto corriente y el diferido. El impuesto a las ganancias es reconocido en el Estado de Resultados Integrales. El impuesto a las ganancias corriente se calcula sobre la base de las leyes impositivas vigentes a la fecha de cierre del ejercicio. La Gerencia evalúa en forma periódica las posiciones tomadas en las declaraciones juradas con relación a situaciones en las cuales la legislación impositiva está sujeta a alguna interpretación y establec...

### COMPLETAR

```yaml
item: 4
pregunta: ""
respuesta_referencia: ""
silos_necesarios: [impositivo]
dominios_evidencia: [impositivo]
distractor_valido:
```

<sub>chunk evidencia: `bc2d533089dce975d9426eeda7795cd6ac09c01699ce8a9f221473df81ba8bbe` · chunk distractor: `e3891cdb0973f200b01849addec3d8f5de69a42cc1eadce79b579d993ded983a`</sub>

---

## Ítem 5

### Evidencia — dominio `impositivo`

**Ley_11683_Procedimiento_Fiscal_TO** · texto_ordenado · Honorable Congreso de la Nación Argentina<br>
`DOC-0009` · ubicación: Demanda por repetición

> ARTICULO 83 — En la demanda contenciosa por repetición de tributos no podrá el actor fundar sus pretensiones en hechos no alegados en la instancia administrativa ni ofrecer prueba que no hubiera sido ofrecida en dicha instancia , con excepción de los hechos nuevos y de la prueba sobre los mismos . (Párrafo sustituido por Título XV art . 18 inciso 4) de la Ley N º 25. 5. 239 (/normativa/nacional/norma -61784) B . O . 31/12/1999) Incumbe al mismo demostrar en qué medida el impuesto abonado es excesivo con relación al gravamen que según la ley le correspondía pagar , y no podrá , por tanto , limitar su reclamación a la mera impugnación de los fundamentos que sirvieron de base a la estimación de oficio administrativa cuando ésta hubiera tenido lugar . Sólo procederá la repetición por los períodos fiscales con relación a los cuales se haya satisfecho el impuesto hasta ese momento determinado por la ADMINISTRACION FEDERAL DE INGRESOS PUBLICOS .

### Distractor candidato — dominio `legal` · parecido `0.61`

**Decreto_1738_1992_Reglamentario_Gas**

> (5) No será necesario agotar la vía administrativa si por la índole de la cuestión controvertida , y los actos precedentes del Ente , la voluntad administrativa contraria a la posición sustentada por el interesado es conocida , resultando tal procedimiento una inútil demora . Este inciso no será aplicable cuando existan cuestiones de hecho controvertidas . (6) Toda la información recibida por el Ente de los titulares de las habilitaciones estará a disposición del público dentro de las pautas que...

### COMPLETAR

```yaml
item: 5
pregunta: ""
respuesta_referencia: ""
silos_necesarios: [impositivo]
dominios_evidencia: [impositivo]
distractor_valido:
```

<sub>chunk evidencia: `bc48fb4f2f288b622816838db34f8a083574f6d36d84c7764f1993dc462d2e5b` · chunk distractor: `271db1a37a5c1d44a4d1386b67027af831acb768fe242e42df28c5acb01296af`</sub>

---

## Ítem 6

> 📊 **La evidencia es una tabla.** Estos ítems son los que demuestran la parte multimodal de la tesis: priorizalos.

### Evidencia — dominio `contable`

**Pampa_EEFF_Consolidado_1Q2026** · estado_contable · Pampa Energía S.A.<br>
`DOC-0016` · ubicación: NOTA 5: (Continuación)

> Asociadas, Información sobre el emisor.Actividad principal = . Asociadas, Información sobre el emisor.Fecha = . Asociadas, Información sobre el emisor.Capital social = . Asociadas, Información sobre el emisor.Resultado del período = . Asociadas, Información sobre el emisor.Patrimonio = . Asociadas, Información sobre el emisor.% de participación directo e indirecto = . SESA, Información sobre el emisor.Actividad principal = Tratamiento de gas. SESA, Información sobre el emisor.Fecha = 31.03.2026. SESA, Información sobre el emisor.Capital social = 1.203. SESA, Información sobre el emisor.Resultado del período = 889. SESA, Información sobre el emisor.Patrimonio = 132.254. SESA, Información sobre el emisor.% de participación directo e indirecto = 20,00%. VMOS, Información sobre el emisor.Actividad principal = Transporte de hidrocarburos. VMOS, Información sobre el emisor.Fecha = 31.03.2026. VMOS, Información sobre el emisor.Capital social = 159.133. VMOS, Información sobre el emisor.Resultado del período = (50.292). VMOS, Información sobre el emisor.Patrimonio = 527.382. VMOS, Información sobre el emisor.% de participación directo e indirecto = 10,20%. Negocios conjuntos, Información s...

### Distractor candidato — dominio `financiero|impositivo|legal` · parecido `0.65`

**MSU_ON_ClaseIV**

> ACTIVO, 31/3/2022 (en miles de Pesos) = . ACTIVO, 31/12/2021 = . ACTIVO NO CORRIENTE, 31/3/2022 (en miles de Pesos) = . ACTIVO NO CORRIENTE, 31/12/2021 = . Propiedad, planta y equipo, 31/3/2022 (en miles de Pesos) = 101,602,705. Propiedad, planta y equipo, 31/12/2021 = 94,645,378. Préstamos financieros, 31/3/2022 (en miles de Pesos) = 5,100,553. Préstamos financieros, 31/12/2021 = 4,656,785. Créditos impositivos y aduaneros, 31/3/2022 (en miles de Pesos) = 230,508. Créditos impositivos y aduaner...

### COMPLETAR

```yaml
item: 6
pregunta: ""
respuesta_referencia: ""
silos_necesarios: [contable]
dominios_evidencia: [contable]
distractor_valido:
```

<sub>chunk evidencia: `c6132ce3432d2d0e51748a6e29dc64e8fff0ba64edbedbe793fab09e68a4d076` · chunk distractor: `6aa145ecfaf3c98c732de3dc4682897e01cf4a51c9bc964ab434168720dff420`</sub>

---

## Ítem 7

### Evidencia — dominio `impositivo`

**Decreto_821_1998_TO_Ley_11683** · texto_ordenado · Poder Ejecutivo Nacional<br>
`DOC-0003` · ubicación: DE LA SENTENCIA DEL TRIBUNAL

> Cuando en función de las facultades del artículo 164 el Tribunal Fiscal de la Nación recalifique o reduzca la sanción a aplicar, r, las costas se impondrán por el orden causado . No obstante, el Tribunal podrá imponer las costas al Fisco Nacional, cuando la tipificación o la cuantía de la sanción recurrida se demuestre temeraria o carente de justificación. (Párrafo sustituido por art. 241 de la Ley N° 27430 B.O. 29/12/2017. Vigencia: el día siguiente al de su publicación en el Boletín Oficial y surtirán efecto de conformidad con lo previsto en cada uno de los Títulos que la componen. Ver art. 247 de la Ley de referencia) (Artículo sustituido por art. 1° pto. XXIX de la Ley N° 26.044 B.O. 6/7/2005) ARTICULO 185 — La sentencia no podrá contener pronunciamiento respecto de la falta de validez constitucional de las leyes tributarias o aduaneras y sus reglamentaciones, a no ser que la Jurisprudencia de la Corte Suprema de Justicia de la Nación haya declarado la inconstitucionalidad de las mismas, en cuyo caso podrá seguirse la interpretación efectuada por ese TRIBUNAL de la NACION. ARTICULO 186 — El TRIBUNAL FISCAL DE LA NACION podrá declarar en el caso concreto , que la interpretación ...

### Distractor candidato — dominio `legal` · parecido `0.63`

**Decreto_1738_1992_Reglamentario_Gas**

> - (4) La aplicación de sanciones será independiente de la obligación de reintegrar o compensar las tarifas indebidamente percibidas de los usuarios , con intereses , o de indemnizar los perjuicios ocasionados al Estado , a los usuarios o a terceros por la infracción . - (5) Las infracciones a las normas reglamentarias tendrán carácter formal y se configurarán con independencia del dolo o de la culpa del infractor , salvo cuando se disponga expresamente lo contrario en este Decreto o en la habili...

### COMPLETAR

```yaml
item: 7
pregunta: ""
respuesta_referencia: ""
silos_necesarios: [impositivo]
dominios_evidencia: [impositivo]
distractor_valido:
```

<sub>chunk evidencia: `cb874fa502ba0ddcab0b49974caef47e1dd13720040c6b21f003af3dbd4dcd0d` · chunk distractor: `4447ef286aec86d0b8eb81834fd8ec5a0a504563195d016911122d08cf9cea27`</sub>

---

## Ítem 8

### Evidencia — dominio `legal`

**Ley_24065_Energia_Electrica_TO** · texto_ordenado · Honorable Congreso de la Nación Argentina<br>
`DOC-0013` · ubicación: CAPÍTULO VI

> Provisión de servicios ARTÍCULO 22 ARTÍCULO 23 ARTÍCULO 24 pedido ARTÍCULO 25 ARTÍCULO 26 ARTÍCULO 28 monto de sus inversiones conforme lo dispuesto en el artículo 41 de esta ley . ARTÍCULO 28 bis . -Si una obra de transporte no estuviera contemplada en los contratos de concesión de transporte en curso de ejecución , pero su ejecución resultara esencial técnica y económicamente para hacer frente a las necesidades del servicio público correspondiente en el Sistema Argentino de Interconexión (SADI) , previa consulta al OED , la SECRETARÍA DE ENERGÍA del MINISTERIO DE ECONOMÍA podrá resolver su inclusión , a cuyo fin podrá considerar la utilización de los recursos previstos en el segundo párrafo del artículo 31 de la Ley N ° 15 . 336 y sus modificatorias . Las condiciones económico -financieras asociadas a la obligación de la ampliación no pueden afectar el normal funcionamiento de la concesión . El ENTE NACIONAL REGULADOR DEL GAS Y LA ELECTRICIDAD seguirá los procedimientos habituales para aprobar la construcción de la obra , estableciendo su forma de financiación y , en su caso , incorporar el importe correspondiente a la recuperación de los costos de la ampliación en el respectivo ...

### Distractor candidato — dominio `impositivo` · parecido `0.66`

**Ley_23966_Combustibles_Liquidos_Gas**

> ARTICULO ... — Los sujetos que presten servicios de transporte público de pasajeros y/o de carga terrestre, fluvial o marítimo , podrán computar como pago a cuenta del impuesto al valor agregado , el cuarenta y cinco por ciento (45%) del impuesto previsto en el Capítulo I contenido en las compras de gasoil efectuadas en el respectivo periodo fiscal, que se utilicen como combustible de las unidades afectadas a la realización de los referidos servicios, en las condiciones que fije la reglamentació...

### COMPLETAR

```yaml
item: 8
pregunta: ""
respuesta_referencia: ""
silos_necesarios: [legal]
dominios_evidencia: [legal]
distractor_valido:
```

<sub>chunk evidencia: `cc140be829d812de16841e9b341c9ec20b26167f3e3879e30cef522704629629` · chunk distractor: `d36b66eb788fd77a67095a3dc24cbb0e0989b560bc65ab80210ced0ffc6a45c5`</sub>

---

## Ítem 9

### Evidencia — dominio `legal`

**Decreto_1738_1992_Reglamentario_Gas** · decreto · Poder Ejecutivo Nacional<br>
`DOC-0002` · ubicación: IV -Transporte y Distribución

> - a) Objeto . - b) Término de duración . - c) Régimen de prestación del servicio . - d) Régimen de los activos afectados al servicio . - e) Régimen de ocupación del dominio público . - f) Servidumbres y restricciones al dominio . - g) Régimen de ampliaciones y mejoras . - h) Reglamento del Servicio y Tarifas . - i) Régimen de penalidades . - j) Terminación de la licencia y consecuencias jurídicas de la misma . - k) Tratamiento de las quejas de los usuarios . - l) Régimen impositivo . - m) Régimen de suministros . - n) Relaciones con la Autoridad Regulatoria . - o) Ley aplicable y jurisdicción . - p) Causales de caducidad por inobservancia de la Licencia . Las licencias otorgadas no podrán ser objeto de rescate por la Administración , ni serán modificadas durante su vigencia sin el consentimiento de los licenciatarios . No se considerarán modificaciones a la licencia (i) las modificaciones que el Ente introduzca en el Reglamento del Servicio , sin perjuicio del derecho del Ente o del licenciatario a requerir el correspondiente ajuste de las tarifas si el efecto neto de tal modificación alterase en sentido favorable o desfavorable , respectivamente , el equilibrio económico -financie...

### Distractor candidato — dominio `contable` · parecido `0.66`

**EEFF-ind-31-03-2019**

> - 1) Regímenes jurídicos específicos y significativos que impliquen decaimientos o renacimientos contingentes de beneficios previstos por dichas disposiciones. No existen otros regímenes jurídicos específicos con excepción del marco regulatorio del sector eléctrico y de las entidades que participan en el establecido por la Ley N° 24.065 y normas reglamentarias y complementarias. - 2) Modificaciones significativas que afecten la comparabilidad con los períodos presentados anteriormente. No existe...

### COMPLETAR

```yaml
item: 9
pregunta: ""
respuesta_referencia: ""
silos_necesarios: [legal]
dominios_evidencia: [legal]
distractor_valido:
```

<sub>chunk evidencia: `f7a702f5f82ab1d597623a4f35c6c31ef0cf0d36048dba0f4f465fd058baabba` · chunk distractor: `a48d1005e999188871094d357fb73177c6d910f2b0f56624ec1a33d2e2835c41`</sub>

---

## Ítem 10

> 📊 **La evidencia es una tabla.** Estos ítems son los que demuestran la parte multimodal de la tesis: priorizalos.

### Evidencia — dominio `contable`

**TGS_EEFF_2024_4T** · memoria_anual · Transportadora de Gas del Sur S.A.<br>
`DOC-0020` · ubicación: Ejercicio terminado el 31 de diciembre de 2023

> Por mercado, Transporte de Gas Natural Producción y comercialización de Líquidos Midstream Total = . Por mercado, = . Mercado externo - 207.725.378 - 207.725.378, Transporte de Gas Natural Producción y comercialización de Líquidos Midstream Total = . Mercado externo - 207.725.378 - 207.725.378, = . Mercado local 215.700.088 351.693.053 187.380.086 754.773.227, Transporte de Gas Natural Producción y comercialización de Líquidos Midstream Total = . Mercado local 215.700.088 351.693.053 187.380.086 754.773.227, = . , Transporte de Gas Natural Producción y comercialización de Líquidos Midstream Total = Total 215.700.088 559.418.431 187.380.086 962.498.605. , = . Por oportunidad:, Transporte de Gas Natural Producción y comercialización de Líquidos Midstream Total = . Por oportunidad:, = . A lo largo del tiempo 215.700.088 32.098.542 187.380.086 435.178.716, Transporte de Gas Natural Producción y comercialización de Líquidos Midstream Total = . A lo largo del tiempo 215.700.088 32.098.542 187.380.086 435.178.716, = . En un determinado momento - 527.319.889 - 527.319.889, Transporte de Gas Natural Producción y comercialización de Líquidos Midstream Total = . En un determinado momento - 52...

### Distractor candidato — dominio `legal` · parecido `0.64`

**Ley_24076_Gas_Natural_TO**

> - b) Promover la competitividad de los mercados de oferta y demanda de gas natural y alentar inversiones para asegurar el suministro a largo plazo; - c) Propender a una mejor operación , confiabilidad , igualdad , libre acceso , no discriminación y uso generalizado de los servicios e instalaciones de transporte y distribución de gas natural; - d) Regular las actividades del transporte y distribución de gas natural , asegurando que las tarifas que se apliquen a los servicios sean justas y razonab...

### COMPLETAR

```yaml
item: 10
pregunta: ""
respuesta_referencia: ""
silos_necesarios: [contable]
dominios_evidencia: [contable]
distractor_valido:
```

<sub>chunk evidencia: `f9be28601fceac358b97b234ef402dd0d4776fac0bab08c6e76492a6415df82e` · chunk distractor: `3489a4b827637f98896eca967cf737f77fd454f66b14572c3785522e9099f608`</sub>

---
