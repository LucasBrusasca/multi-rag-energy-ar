# Golden piloto — BORRADOR EXPLORATORIO

> ⚠️ NO ES EVIDENCIA. Ítems propuestos, anclados a artículos leídos del corpus.
> Pendiente: verificación de lectura por Lucas + validación del director.
> Estratos según PROTOCOLO_GOLDEN §5: clara | colision | multi_silo | sin_respuesta | vigencia | degradada

## Estado: 40 ítems candidatos

| estrato | cantidad |
|---|---:|
| colision | 14 |
| clara | 14 |
| sin_respuesta | 4 |
| vigencia | 3 |
| multi_silo | 3 |
| degradada | 2 |
| **Total** | **40** |

## G-P-001 · clara · [impositivo]
**Pregunta:** ¿A partir de qué momento el agente de retención que omitió retener responde solidariamente por el tributo no retenido?
**Evidencia:** Ley 11.683, art. 8 inc. c (+ art. 6 inc. f)
**Respuesta ref.:** Vencido el plazo de 15 días desde la fecha en que correspondía retener, si no acredita que el contribuyente pagó el gravamen.
**Conducta:** responder
**Nota diagnóstica:** “agente de retención” aparece en distintos regímenes tributarios. Es una ambigüedad intra-dominio útil para desarrollo, pero no integra la colisión interdominio primaria.


## G-P-002 · clara · [impositivo]
**Pregunta:** ¿En qué plazo puede el contribuyente formular su descargo en el procedimiento de determinación de oficio?
**Evidencia:** Ley 11.683, art. 17 (primer párrafo)
**Respuesta ref.:** 15 días, prorrogables por otro lapso igual y por única vez.
**Conducta:** responder

## G-P-003 · clara · [impositivo]
**Pregunta:** Si el juez administrativo no dicta resolución, ¿cuándo caduca el procedimiento de determinación de oficio?
**Evidencia:** Ley 11.683, art. 17 (párrafo de pronto despacho)
**Respuesta ref.:** Transcurridos 90 días desde la evacuación de la vista o desde el vencimiento del plazo para hacerlo sin que se dicte resolución, el contribuyente puede requerir pronto despacho. Si pasan 30 días desde ese requerimiento sin resolución, caduca el procedimiento.
**Conducta:** responder

## G-P-004 · clara · [impositivo]
**Pregunta:** ¿Cómo se computan los términos establecidos en días en el procedimiento fiscal?
**Evidencia:** Ley 11.683, art. 4
**Respuesta ref.:** Se computan únicamente los días hábiles administrativos, salvo disposición expresa en contrario. Cuando las actuaciones se relacionan con organismos judiciales o con el Tribunal Fiscal, se consideran los días hábiles para esos organismos.
**Conducta:** responder

## G-P-005 · colision · [legal]
**Pregunta:** ¿Qué sanciones corresponden por violar la ley del sector eléctrico, cometidas por terceros no concesionarios?
**Evidencia:** Ley 24.065, art. 63
**Respuesta ref.:** Multa de $130.000 a $140.000.000; inhabilitación especial de 1 a 5 años; suspensión de hasta 90 días; decomiso.
**Conducta:** responder
**Colisión:** "multa/sanción" también es central en Ley 11.683 (arts. 39/45/46), régimen totalmente distinto.

## G-P-006 · colision · [legal]
**Pregunta:** ¿Qué tasa deben abonar anualmente los transportistas y distribuidores de electricidad, y con qué fin?
**Evidencia:** Ley 24.065, art. 56
**Respuesta ref.:** Una tasa de fiscalización y control, anual y por adelantado, fijada por el Ente en su presupuesto.
**Conducta:** responder
**Colisión:** "tasa/alícuota" pertenece al mundo impositivo.
**Chunk candidato:** 264911a2eb98feb8667a8568b968239e6d5b33c17ce448208518a51fe8f9d4a6

## G-P-007 · colision · [legal]
**Pregunta:** Para cobrar deudas por suministro eléctrico, ¿qué procedimiento se aplica y qué constituye título hábil?
**Evidencia:** Ley 24.065, art. 70
**Respuesta ref.:** Procedimiento ejecutivo, siendo título hábil la constancia de deuda que determine la reglamentación.
**Conducta:** responder
**Colisión:** casi idéntico a la ejecución fiscal de Ley 11.683.

## G-P-008 · vigencia · [legal]
**Pregunta:** En el texto actualizado de la Ley 24.065 incorporado al corpus, ¿qué organismo nombra el artículo 54 y a qué entes reemplaza la unificación indicada en la nota de actualización?
**Evidencia:** Ley 24.065, art. 54 + nota Infoleg vinculada al art. 161 de la Ley 27.742.
**Respuesta ref.:** El artículo 54 nombra al Ente Nacional Regulador del Gas y la Electricidad, creado por el artículo 161 de la Ley 27.742. La unificación dispuso que este organismo reemplazara y asumiera las funciones del ENRE y del ENARGAS.
**Conducta:** responder
**Chunks candidatos:** 11fe364c46da2b658967e4da964c2cde6e249a2947b05be18be6b81e29ba35b0 + b95931e40a3f795d7bc3524eeb0064e2be3700ac44e9eef95b10c276f0b0216c
**Por qué:** prueba si el sistema utiliza el texto actualizado o responde exclusivamente con la denominación histórica ENRE.

## G-P-009 · colision · [legal]
**Pregunta:** ¿Quiénes son los agentes del Mercado Eléctrico Mayorista?
**Evidencia:** Ley 24.065, art. 4
**Respuesta ref.:** Los actores reconocidos son los generadores o productores, transportistas, distribuidores y grandes usuarios o usuarios libres. También actúan los usuarios-generadores y los participantes identificados por la reglamentación, incluidos comercializadores y almacenistas.
**Conducta:** responder
**Colisión:** par directo de G-P-001 — "agentes" vive en los dos silos.
**Chunk candidato:** e54f4a9ae0518578e80f4e61d215991452dce1c32f780bef6b4274c02371ad7d

## G-P-010 · multi_silo · [legal, impositivo]
**Pregunta:** Según las versiones del corpus, ¿cómo se comparan las multas por una infracción formal tributaria común y por una violación de la Ley 24.065 cometida por un tercero no concesionario, y qué sanciones adicionales contempla el régimen eléctrico?
**Evidencia:** Ley 11.683, art. 39 + Ley 24.065, art. 63.
**Respuesta ref.:** La infracción formal tributaria común se sanciona con una multa de $150.000 a $2.500.000, que puede alcanzar $35.000.000 en los incumplimientos especialmente enumerados por el artículo 39. Para un tercero no concesionario, la Ley 24.065 prevé una multa de $130.000 a $140.000.000 y, además, inhabilitación especial de 1 a 5 años, suspensión de hasta 90 días y decomiso.
**Conducta:** responder
**Chunks candidatos:** d8cf1eae9a64b750ff39843f0bc076f33caab2de0ff9ef3e4a7aa5749e3e2641 + 6c713d63135678d98718d3e87bcbfa18c058a1c4b2367488f5cc4175a6146b2e
**Nota:** n_documentos = 2 → análisis secundario exploratorio (PROTOCOLO_EXPERIMENTAL §4.6).

## G-P-011 · colision · [impositivo]
**Pregunta:** Además de la multa, ¿qué se incluye en la determinación de oficio de un tributo cuando corresponde?
**Evidencia:** Ley 11.683, art. 17
**Respuesta ref.:** El interés resarcitorio y la actualización.
**Conducta:** responder
**Colisión:** "intereses" es central en EEFF (contable/financiero) — polisémico entre tres silos.

## G-P-012 · colision · [legal]
**Pregunta:** ¿Ante qué tribunal y en qué plazo se impugnan las sanciones del ente regulador de la electricidad?
**Evidencia:** Ley 24.065, art. 67 (in fine)
**Respuesta ref.:** Cámara Nacional de Apelaciones en lo Contencioso Administrativo Federal, mediante recurso directo dentro de los 30 días hábiles judiciales posteriores a la notificación.
**Conducta:** responder
**Colisión:** la vía recursiva fiscal de Ley 11.683 (Tribunal Fiscal) usa lenguaje casi idéntico.
**Chunk candidato:** e0cc6f36385ff70e955b85f65d4e1e0c8b3596272e9f9235bdc495131de6d2ff

## G-P-013 · sin_respuesta · []
**Pregunta:** Para el período fiscal 2026, ¿cuál es la alícuota del Impuesto sobre los Ingresos Brutos aplicable a la distribución de gas en la Provincia de Buenos Aires?
**Respuesta ref.:** No puede determinarse con el corpus disponible porque no contiene el Código Fiscal ni la Ley Impositiva 2026 de la Provincia de Buenos Aires.
**Conducta:** abstenerse
**Condición de abstención:** debe indicar que falta la normativa provincial aplicable y no proporcionar una alícuota. Las menciones incidentales a Ingresos Brutos o a combustibles y gas no constituyen evidencia suficiente.
**Verificación de ausencia:** catálogo de 24 artefactos + búsqueda integral en los chunks; no existe normativa tributaria bonaerense aplicable al período consultado.

## G-P-014 · sin_respuesta · []
**Pregunta:** Según el régimen de distribución secundaria de la Ley 23.548, ¿qué porcentaje corresponde a la Provincia del Neuquén?
**Respuesta ref.:** No puede determinarse con el corpus disponible porque no contiene el texto completo del régimen de coparticipación federal ni la distribución secundaria aplicable a Neuquén.
**Conducta:** abstenerse
**Condición de abstención:** debe informar la ausencia de la norma necesaria y no inferir un porcentaje a partir de referencias incidentales a la Ley 23.548.
**Verificación de ausencia:** catálogo de 24 artefactos + búsqueda integral en los chunks; existen menciones a la coparticipación, pero no la evidencia requerida para responder.

## G-P-015 · vigencia · [legal]
**Pregunta:** ¿Qué texto ordenado de la Ley 24.076 aprobó el Decreto 451/2025 y desde cuándo entró en vigencia?
**Evidencia:** Decreto 451/2025, arts. 1 y 2 + portada de la Ley 24.076 T.O. 2025.
**Respuesta ref.:** Aprobó la “Ley 24.076 - T.O. 2025”, que entró en vigencia el 7 de julio de 2025, fecha de su publicación en el Boletín Oficial.
**Conducta:** responder
**Chunk candidato:** 167fb0e8f1bae143b77e729b90d2f27507ecd3146fa65e9b3a28d649625c4487
**Por qué:** prueba si el sistema identifica el texto ordenado vigente desde una fecha explícita y evita responder solamente con la versión histórica de 1992.

## G-P-016 · clara · [legal]
**Pregunta:** ¿Qué debe convocar el ente antes de resolver una modificación tarifaria solicitada por un distribuidor?
**Evidencia:** Ley 24.065, art. 46
**Respuesta ref.:** El ente debe dar inmediata difusión pública a la solicitud durante 30 días y convocar una audiencia pública para el día hábil siguiente.
**Conducta:** responder

## G-P-017 · colision · [impositivo]
**Pregunta:** ¿Qué genera la falta total o parcial de pago de gravámenes, retenciones o anticipos, y desde cuándo?
**Evidencia:** Ley 11.683, art. 37
**Respuesta ref.:** Un interés resarcitorio, que se devenga desde los respectivos vencimientos y sin necesidad de interpelación alguna.
**Conducta:** responder
**Colisión:** "intereses" es central en los EEFF (contable/financiero) — Pampa, TGS, Edenor los reportan como resultado financiero. Término polisémico entre tres silos.

## G-P-018 · colision · [impositivo]
**Pregunta:** ¿Con qué multa se sanciona la omisión de presentar la declaración jurada dentro de los plazos generales?
**Evidencia:** Ley 11.683, art. 38 (montos según Ley 27.799, B.O. 2/1/2026)
**Respuesta ref.:** Multa de $220.000, que se eleva a $440.000 si se trata de sociedades, asociaciones o entidades constituidas en el país.
**Conducta:** responder
**Colisión:** "multa" también en Ley 24.065 art. 63 ($130.000 a $140.000.000). Mismo término, régimen y escala totalmente distintos.

## G-P-019 · colision · [impositivo]
**Pregunta:** ¿Qué sanción corresponde a quien no emite facturas o comprobantes por sus operaciones comerciales?
**Evidencia:** Ley 11.683, art. 40 inc. a
**Respuesta ref.:** Clausura de 2 a 6 días del establecimiento, siempre que el valor de los bienes o servicios exceda $20.000.
**Conducta:** responder
**Colisión FUERTE:** Ley 24.065 art. 63 inc. c prevé "suspensión de hasta 90 días en la prestación de servicios". Ambas cierran/suspenden una actividad, con plazos y regímenes distintos.
**Chunk candidato:** 3ae5e89457e267a9c881b5d1df3310096472ac455446af850f48950b7d74dccd + e08dc64299ad17862bccee9b88545c5cce9a167bc01baf7949014fd88484ca78

## G-P-020 · clara · [impositivo]
**Pregunta:** ¿Cuál es el rango de multa por violar disposiciones que establecen deberes formales tendientes a determinar la obligación tributaria?
**Evidencia:** Ley 11.683, art. 39 (montos según Ley 27.799, B.O. 2/1/2026)
**Respuesta ref.:** De $150.000 a $2.500.000; graduable hasta un máximo de $35.000.000 en los incumplimientos enumerados.
**Conducta:** responder

## G-P-021 · clara · [impositivo]
**Pregunta:** ¿Por cuánto tiempo deben conservarse los comprobantes y duplicados de las operaciones?
**Evidencia:** Ley 11.683, art. 33 (segundo párrafo)
**Respuesta ref.:** Diez (10) años, o excepcionalmente por un plazo mayor cuando se refieran a operaciones indispensables para la determinación cierta de la materia imponible.
**Conducta:** responder

## G-P-022 · colision · [impositivo]
**Pregunta:** ¿Cuándo puede AFIP disponer la clausura preventiva de un establecimiento?
**Evidencia:** Ley 11.683, art. 35 inc. f
**Respuesta ref.:** Cuando constate dos o más hechos u omisiones del art. 40, concurra grave perjuicio o el responsable registre antecedentes por la misma infracción en un período no mayor a dos años, con resolución condenatoria aun no firme.
**Conducta:** responder
**Colisión:** medida preventiva que suspende actividad — se solapa con las facultades preventivas del Ente (Ley 24.065 art. 59 y secuestro del art. 65).
**Chunk candidato:** 9fc2af0019a959ccfd99f7664a598edf8c8ff7867598b40cc6fdc464c828d6e6 + 30a70348651805aaf0412ffdd87de818c47684b31a24d4588df718f940b6ecf3

## G-P-023 · vigencia · [impositivo]
**Pregunta:** ¿Qué montos de multa para la omisión de presentar declaraciones juradas estableció el artículo 38 de la Ley 11.683 a partir del 2 de enero de 2026?
**Evidencia:** Ley 11.683, art. 38 + art. 15 de la Ley 27.799, publicada el 02.01.2026.
**Respuesta ref.:** $220.000 para los sujetos en general y $440.000 para sociedades, asociaciones, entidades y los demás establecimientos comprendidos por el artículo. Estos importes sustituyeron los montos anteriores de $200 y $400.
**Conducta:** responder
**Chunk candidato:** 5e307c7e67e620a01ec2eaaff15b784a962db43dac38b8ea237eb8981652af61
**Por qué:** prueba si el sistema distingue los montos sustituidos de los anteriores que todavía aparecen en la nota histórica.

## G-P-024 · sin_respuesta · []
**Pregunta:** Según el convenio para evitar la doble imposición entre Argentina y España, ¿en qué Estado pueden someterse a imposición las participaciones, dietas u honorarios que recibe un director de una sociedad residente en el otro Estado?
**Respuesta ref.:** No puede determinarse con el corpus disponible porque el convenio entre Argentina y España no forma parte de sus fuentes.
**Conducta:** abstenerse
**Condición de abstención:** debe indicar que falta el convenio internacional y no sustituirlo por la RG AFIP 830 ni por otra norma doméstica sobre retenciones.
**Verificación de ausencia:** catálogo de 24 artefactos + búsqueda integral en los chunks; existen referencias a honorarios de directores, pero no el convenio internacional requerido.

## G-P-025 · multi_silo · [impositivo, contable]
**Pregunta:** Según la Ley 11.683 y los estados financieros de Pampa Energía, ¿desde cuándo se devenga el interés resarcitorio por una deuda fiscal impaga y qué importe reconoció la empresa como intereses fiscales durante el período de tres meses finalizado el 31 de marzo de 2026?
**Evidencia:** Ley 11.683, art. 37 + Pampa Energía, Nota 10.5 “Resultados financieros”, al 31.03.2026.
**Respuesta ref.:** El interés resarcitorio se devenga desde el vencimiento de la obligación, sin necesidad de interpelación. Pampa reconoció $7.471 millones como intereses fiscales dentro de sus gastos financieros. El primer dato describe la regla tributaria y el segundo su reconocimiento contable; no deben interpretarse como conceptos automáticamente equivalentes.
**Conducta:** responder
**Chunks candidatos:** f83fc442427c82c8c31b329ad37ecc5351f4b30f67d6246bc299294b5aa06d8d + 385a20a5fe4060059b1561669154a3097459ac58684d3f1471d29eb2fe76f69e
**Nota:** n_documentos = 2 → análisis secundario exploratorio (PROTOCOLO_EXPERIMENTAL §4.6).

## G-P-026 · colision · [contable]
**Pregunta:** En el estado de resultados de Pampa Energía al 31/03/2026, ¿qué importe se registró en la línea "Impuesto a las ganancias" y con qué signo?
**Evidencia:** Pampa, Estado de Resultado Integral Consolidado al 31.03.2026, Nota 10.6
**Respuesta ref.:** En el estado de resultados se registró una ganancia por impuesto a las ganancias de $97.637 millones. La Nota 10.6 la descompone en un impuesto corriente de $156.666 millones y un beneficio por impuesto diferido de $254.303 millones.
**Conducta:** responder
**Colisión FUERTE:** "impuesto a las ganancias" es simultáneamente (a) una línea del estado contable y (b) el tributo de la Ley 20.628. Mismo término, dos silos. El monolítico puede traer la ley cuando se pregunta por el balance, o viceversa.
**Chunk candidato:** fd6b3947e848418535265f6e24dfd9597a6706c99f949930fd2214042350ebaf + 720db8d467660af2e8f112791e637b809769688237cb5ab7a35ddf8320db7ef7

## G-P-027 · colision · [contable]
**Pregunta:** ¿Qué importe registra Pampa en "Activo por impuesto diferido" dentro del activo no corriente al 31/03/2026?
**Evidencia:** Pampa, Estado de Situación Financiera Consolidado al 31.03.2026, Nota 11.3
**Respuesta ref.:** $404.919 millones.
**Conducta:** responder
**Colisión:** la palabra "impuesto" aparece dentro de un rubro puramente contable. Es un activo, no una obligación fiscal.
**Chunk candidato:** b7674a13915ab4fbffa1720dd0c8852030f82fa24373617ab33991bcf23a7941 + 1d17453a1d5f9d1d19f36d5dd65770b45c25a5e8a0115faacc0c8505f14b528c

## G-P-028 · clara · [contable]
**Pregunta:** ¿Cuál fue el resultado bruto y cuál el resultado operativo de Pampa en el trimestre cerrado el 31/03/2026?
**Evidencia:** Pampa, Estado de Resultado Integral Consolidado al 31.03.2026
**Respuesta ref.:** Resultado bruto $259.580 millones; resultado operativo $239.672 millones.
**Conducta:** responder
**Nota diagnóstica:** “resultado” es una palabra polisémica, pero no se identificó un distractor interdominio suficientemente específico. No integra la colisión interdominio primaria.

## G-P-029 · clara · [contable]
**Pregunta:** ¿Cuál es el total del activo de Pampa Energía al 31/03/2026 y cómo se descompone entre corriente y no corriente?
**Evidencia:** Pampa, Estado de Situación Financiera Consolidado al 31.03.2026
**Respuesta ref.:** Total del activo $9.697.513 millones: activo no corriente $7.124.911 millones y activo corriente $2.572.602 millones.
**Conducta:** responder
**Nota:** ítem apto para verificación aritmética (checksum): 7.124.911 + 2.572.602 = 9.697.513. La suma cierra exacta.

## G-P-030 · clara · [contable]
**Pregunta:** ¿Cómo se distribuye la ganancia del período de Pampa entre los propietarios de la sociedad y la participación no controladora al 31/03/2026?
**Evidencia:** Pampa, Estado de Resultado Integral Consolidado (Continuación) al 31.03.2026
**Respuesta ref.:** Propietarios de la Sociedad $293.366 millones; participación no controladora $3.301 millones; total $296.667 millones.
**Conducta:** responder
**Nota:** checksum: 293.366 + 3.301 = 296.667. Cierra exacta.

## G-P-031 · colision · [contable]
**Pregunta:** ¿Cuál fue el resultado financiero neto de Pampa en el trimestre cerrado el 31/03/2026?
**Evidencia:** Pampa, Estado de Resultado Integral Consolidado al 31.03.2026, Nota 10.5
**Respuesta ref.:** Pérdida de $40.642 millones (ingresos financieros $5.048; gastos financieros $55.582; otros resultados financieros $9.892).
**Conducta:** responder
**Colisión:** par de G-P-017 — "intereses/resultados financieros" contable vs. el interés resarcitorio del art. 37 de la Ley 11.683.
**Chunk candidato:** 385a20a5fe4060059b1561669154a3097459ac58684d3f1471d29eb2fe76f69e

## G-P-032 · clara · [legal]
**Pregunta:** En los estados financieros de Pampa, ¿qué significan las siglas ENRE, ENARGAS y CAMMESA?
**Evidencia:** Pampa, Glosario de términos de los EEFF al 31.03.2026
**Respuesta ref.:** ENRE: Ente Nacional Regulador de la Electricidad. ENARGAS: Ente Nacional Regulador del Gas. CAMMESA: Compañía Administradora del Mercado Eléctrico Mayorista S.A.
**Conducta:** responder
**Nota diagnóstica:** la evidencia está dentro de un documento contable, pero el contenido del fragmento es regulatorio. Este ítem permite comprobar que el dominio del chunk no debe heredarse del documento.

## G-P-033 · multi_silo · [contable, impositivo]
**Pregunta:** ¿Cómo se compone el resultado por impuesto a las ganancias reconocido por Pampa Energía al 31 de marzo de 2026 y por qué no equivale a la ganancia neta sujeta a impuesto regulada por el artículo 17 de la Ley 20.628?
**Evidencia:** Pampa Energía, Nota 10.6 “Impuesto a las ganancias”, al 31.03.2026 + Ley 20.628, art. 17.
**Respuesta ref.:** Pampa reconoció un impuesto corriente de $156.666 millones y un beneficio por impuesto diferido de $254.303 millones, cuya combinación produjo una ganancia contable por impuesto a las ganancias de $97.637 millones. En cambio, el artículo 17 establece que la ganancia neta y la ganancia neta sujeta a impuesto se determinan mediante las deducciones admitidas por la legislación tributaria. Por eso, el resultado contable por impuesto incluye componentes corrientes y diferidos y no constituye por sí mismo la base imponible determinada por la ley.
**Conducta:** responder
**Chunks candidatos:** 720db8d467660af2e8f112791e637b809769688237cb5ab7a35ddf8320db7ef7 + fce1d2b550cf6cc870598f49a878a0a62482486a8cc3d26722b8571077cbf533
**Nota:** n_documentos = 2 → análisis secundario exploratorio (PROTOCOLO_EXPERIMENTAL §4.6).

## G-P-034 · sin_respuesta · []
**Pregunta:** ¿Cuál fue el EBITDA ajustado de Central Puerto durante el primer trimestre de 2026?
**Respuesta ref.:** No puede determinarse con el corpus disponible porque no contiene los estados financieros ni un informe de resultados de Central Puerto correspondiente al primer trimestre de 2026.
**Conducta:** abstenerse
**Condición de abstención:** debe informar que falta la fuente empresarial correspondiente y no utilizar cifras de Pampa Energía, TGS, Edenor, Transener ni otra compañía.
**Verificación de ausencia:** catálogo de 24 artefactos + búsqueda integral en los chunks; Central Puerto aparece mencionada incidentalmente, pero no existen datos que permitan calcular o verificar su EBITDA ajustado.

## G-P-035 · clara · [contable]
**Pregunta:** ¿Cuál fue el total del pasivo y del patrimonio de Pampa Energía al 31 de marzo de 2026, y cómo se relacionan con el total del activo?
**Evidencia:** Pampa Energía, Estado de Situación Financiera Consolidado Condensado Intermedio al 31.03.2026.
**Respuesta ref.:** El pasivo total fue de $4.462.513 millones y el patrimonio total de $5.235.000 millones. Su suma es $9.697.513 millones, coincidente con el total del activo.
**Conducta:** responder

## G-P-036 · clara · [financiero]
**Pregunta:** ¿Cuál es el valor nominal máximo inicial de las Obligaciones Negociables Clase IV de MSU Energy, hasta qué monto puede ampliarse y cuál es su plazo de vencimiento?
**Evidencia:** MSU Energy, Suplemento de Prospecto de las Obligaciones Negociables Clase IV, portada y página 1.
**Respuesta ref.:** Valor nominal inicial de hasta US$15.000.000, ampliable hasta US$31.000.000, con vencimiento a los 24 meses desde la fecha de emisión y liquidación.
**Conducta:** responder
**Chunk candidato:** c0da91a938d0394d541ba193a9d35933ad53a2ed48abb6f8e780bd342df041ae

## G-P-037 · colision · [financiero]
**Pregunta:** ¿Cómo se determina y paga el interés de las Obligaciones Negociables Clase IV de MSU Energy, y cuándo se amortiza su capital?
**Evidencia:** MSU Energy, Suplemento de Prospecto de las Obligaciones Negociables Clase IV, página 1.
**Respuesta ref.:** Devengan una tasa de interés fija determinada mediante licitación, pagadera semestralmente por período vencido. El capital se amortiza íntegramente al vencimiento, a los 24 meses desde la emisión y liquidación.
**Conducta:** responder
**Colisión:** “interés” y “amortización” también aparecen con significados tributarios y contables.
**Chunk candidato:** a7f9ee400271a2fb4a94aeba2999eb1730b74f806e8cc01bbbdb05653bab4a12

## G-P-038 · clara · [financiero]
**Pregunta:** ¿Qué calificación de emisor de largo plazo y qué perspectiva asignó FIX SCR a Transener en su informe del 18 de diciembre de 2025?
**Evidencia:** FIX SCR, Informe Integral de Calificación de Transener, página 1.
**Respuesta ref.:** Calificación AA(arg), con perspectiva estable.
**Conducta:** responder
**Chunk candidato:** 058f8f478e478d4f0fa9fa12fc895ebdc11ec3d2121f106b0cbeda7f44c6bc0f

## G-P-039 · degradada · [legal]
**Pregunta:** Según la presentación de Transener de abril de 2026, ¿cuáles son las tasas de falla reportadas para Transener y Transba, cuáles son los límites máximos establecidos por sus respectivos contratos de concesión y se encuentran las tasas reportadas por debajo de esos límites?
**Evidencia:** Transener, Company Presentation, abril de 2026, página PDF 15, gráficos “Failure Rate Transener” y “Failure Rate Transba” y textos sobre los límites contractuales.
**Respuesta ref.:** Transener reporta 0,41 fallas por cada 100 km de línea frente a un límite máximo contractual de 2,5. Transba reporta 1,10 frente a un límite máximo de 7. En ambos casos, la tasa informada se encuentra por debajo del límite correspondiente.
**Conducta:** responder
**Modalidades de evidencia:** grafico + texto
**Por qué degradada:** la extracción conservó la explicación general y el límite de 2,5 para Transener, pero perdió las tasas mostradas dentro de los gráficos y el límite de 7 correspondiente a Transba.
**Chunk asociado incompleto:** c44a88685dcd6f5d6593cf6165d8eeaff18d2cf6d20d6a6419d3157b62fdb6ff
**Nota experimental:** diagnóstico exploratorio de ingesta multimodal; no sostiene por sí solo la comparación confirmatoria B0/B1/B2.

## G-P-040 · degradada · [financiero]
**Pregunta:** Según los gráficos de evolución de indicadores de Transener, ¿cuáles son el EBITDA y el CAPEX estimados para 2026 bajo la referencia RQT y en qué unidad están expresados?
**Evidencia:** Transener, Company Presentation, abril de 2026, página PDF 23, gráficos “EBITDA” y “CAPEX”.
**Respuesta ref.:** El EBITDA estimado para 2026 es de US$240 millones y el CAPEX estimado es de US$87 millones.
**Conducta:** responder
**Modalidad de evidencia:** grafico
**Por qué degradada:** la página es visualmente legible, pero la extracción no generó un chunk que conserve los valores, su asociación con 2026 (E) RQT y la unidad US$ MM.
**Chunk asociado:** ninguno; la evidencia visual está ausente de la representación textual.
**Nota experimental:** diagnóstico exploratorio de ingesta multimodal; no sostiene por sí solo la comparación confirmatoria B0/B1/B2.
