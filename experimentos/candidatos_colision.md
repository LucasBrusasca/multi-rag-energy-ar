# Candidatos para preguntas de colisión

Cada bloque es un **ancla** (evidencia posible) con sus **distractores** más cercanos,
tomados de documentos cuyo dominio humano NO se cruza con el del ancla.

**Cómo usarlo:** leé el ancla y preguntate qué consulta real se respondería con eso.
Después mirá el distractor: si un buscador podría traerlo por parecido de vocabulario
pero NO sirve para responder, tenés un ítem de colisión. Si el distractor en realidad
también responde, no es colisión — descartalo y pasá al siguiente.

⚠️ La cercanía la calcula el embedding y es solo una ayuda para buscar. El dominio
de cada fragmento sale de la etiqueta humana de su documento. Que un par esté acá
**no** significa que sea una colisión: eso lo decidís leyendo, como pide el protocolo.

---

## 2. Ancla — dominio `impositivo`

- **fuente:** Ley_23349_IVA_TO
- **document_id:** `DOC-0011`
- **chunk_uid:** `19cd6c750f2401100591d31fd102af7d5ac91fca59ac010c6edcb9036d49773a`
- **ubicación:** OPERACIONES DE RESPONSABLES NO INSCRIPTOS
- **título:** OPERACIONES DE RESPONSABLES NO INSCRIPTOS

> ARTICULO 40 — (Artículo derogado por art. 1°, inciso a), punto 6 de la Ley N° 25.865 B.O. 19/1/2004. Vigencia: a partir del día de su publicación en el Boletín Oficial. Las disposiciones contenidas en el Título I de la norma de referencia surtirán efectos a partir de la fecha que disponga el Poder Ejecutivo nacional, la que no podrá superar los ciento ochenta (180) días contados desde la fecha de publicación oficial.)

**Distractores candidatos:**

- `0.636` · **Res_SE_61_1992_Los_Procedimientos** · dominios `legal` · chunk `4df74a31c9eb58c3...`
  > Art. 24. — Derógase, a partir del 1º de mayo del 2000, la Resolución SECRETARIA DE ENERGIA Nº 404 del 26 de julio de 1999. - Art. 25. — Establécese que la aplicación efectiva de la presente Resolución será a partir del 1º de mayo del 2000, excepto la regulación referida a Mercado Spot Anticipado Dia...

- `0.633` · **Ley_24065_Energia_Electrica_TO** · dominios `legal` · chunk `0e87efbaa001e600...`
  > - -Artículo 1 º sustituido por art . 1 del Decreto N ° 804/2001 (/normativa/nacional/norma -67414) B . O . 21/6/2001 . Sustitución derogada por art . 1 ° de la Ley N ° 25. 5. 468 (/normativa/nacional/norma -69315) B . O . 16/10/2001; - -Artículo 3 º , tercer y cuarto párrafos incorporados por art . ...

- `0.624` · **Decreto_1738_1992_Reglamentario_Gas** · dominios `legal` · chunk `085e0ca81c71dd64...`
  > Artículo 1 ° — Apruébase la ' Reglamentación de la Ley N º 24 . 076 ' , que como Anexo I forma parte integrante del presente Decreto . Art . 2 ° — Deróganse a partir del 1 de enero de 1993 todas las normas referidas a la fijación de precios contrarias a las disposiciones de la Ley 24 . 076 y su regl...

---

## 3. Ancla — dominio `impositivo`

- **fuente:** Decreto_821_1998_TO_Ley_11683
- **document_id:** `DOC-0003`
- **chunk_uid:** `1aa2b1a6b039d61f3bb2b6dfa6c03afa01665c0733746cdda49ce56d0b58c1a0`
- **ubicación:** VERIFICACION Y FISCALIZACION
- **título:** VERIFICACION Y FISCALIZACION

> ARTICULO 33 — Con el fin de asegurar la verificación oportuna de la situación impositiva de los contribuyentes y demás responsables, podrá la ADMINISTRACION FEDERAL DE INGRESOS PUBLICOS exigir que éstos, y aún los terceros cuando fuere realmente necesario , lleven libros o registros especiales de las negociaciones y operaciones propias y de terceros que se vinculen con la materia imponible, siempre que no se trate de comerciantes matriculados que lleven libros rubricados en forma correcta, que a juicio de la ADMINISTRACION FEDERAL haga fácil su fiscalización y registren todas las operaciones q...

**Distractores candidatos:**

- `0.626` · **Estados_Contables_Neuquen** · dominios `contable` · chunk `92928ab183a8ae9d...`
  > Para poder emitir una opinión sobre los estados contables mencionados en el apartado anterior, he realizado el examen de acuerdo con las normas de auditoría vigentes establecidas por la Resolución Técnica No.37 emitida por la Federación Argentina de Consejos Profesionales de Ciencias Económicas y ap...

- `0.625` · **TGS_EEFF_2024_4T** · dominios `contable` · chunk `e967303f580c2988...`
  > - a) Identificamos y evaluamos los riesgos de incorrección significativa en los estados financieros consolidados, debida a fraude o error, diseñamos y aplicamos procedimientos de auditoría para responder a dichos riesgos y obtenemos elementos de juicio suficientes y adecuados para proporcionar una b...

- `0.622` · **FS-31-03-2019** · dominios `contable` · chunk `adb2001a047c7c81...`
  > IAS 29 "Financial reporting in hyperinflationary economies" requires that the financial statements of an entity whose functional currency is that of a hyperinflationary economy, regardless of whether they are based on the historical cost method or the current cost method, be restated in constant cur...

---

## 4. Ancla — dominio `impositivo`

- **fuente:** Ley_11683_Procedimiento_Fiscal_TO
- **document_id:** `DOC-0009`
- **chunk_uid:** `26cdf6887d1798fde36878dcf4981c519b7d958d57c42fd2d449a031cf040fba`
- **ubicación:** Competencia del Tribunal
- **título:** Competencia del Tribunal

> ARTICULO 159 — El TRIBUNAL FISCAL DE LA NACION será competente para conocer: - a) De los recursos de apelación contra las resoluciones de la AFIP que determinen tributos y sus accesorios , en forma cierta o presuntiva , o ajusten quebrantos , por un importe superior a PESOS VEINTICINCO MIL ($ 25 . 000) o PESOS CINCUENTA MIL ($ 50 . 000) , respectivamente . (Montos sustituidos por art . 74 de la Ley N ° 26 . 784 (/normativa/nacional/norma -204228) B . O . 05/11/2012) - b) De los recursos de apelación contra las resoluciones de la AFIP que , impongan multas superiores a PESOS VEINTICINCO MIL ($ ...

**Distractores candidatos:**

- `0.624` · **Ley_24065_Energia_Electrica_TO** · dominios `legal` · chunk `e0cc6f36385ff70e...`
  > . -El Ente dictará las normas de procedimiento con sujeción a las cuales se realizarán las audiencias públicas y se aplicarán las sanciones previstas en este Capítulo debiéndose asegurar en todos los casos el cumplimiento de los principios del debido Las sanciones aplicadas por el Ente podrán impugn...

---

## 5. Ancla — dominio `impositivo`

- **fuente:** Ley_11683_Procedimiento_Fiscal_TO
- **document_id:** `DOC-0009`
- **chunk_uid:** `337ddd889b557ca11dee7e6dcbdd26de5b3a48e39120941e38cc8071612016fe`
- **ubicación:** Procedimiento judicial
- **título:** Procedimiento judicial

> (Nota Infoleg: Por art . 1 º del Decreto N º 1390/2001 (/normativa/nacional/norma -69689) B . O . 05/11/2001, 1, se especifica que las designaciones de Agentes Fiscales previstas en el presente artículo deberán recaer en abogados que acrediten un mínimo de TRES (3) años de antigüedad en la matrícula respectiva . ) Artículo ... : Las entidades financieras , así como las demás personas físicas o jurídicas depositarias de bienes embargados , serán responsables en forma solidaria por hasta el valor del bien o la suma de dinero que se hubiere podido embargar , cuando con conocimiento previo del emb...

**Distractores candidatos:**

- `0.604` · **Estados_Contables_Neuquen** · dominios `contable` · chunk `65af2a7a3fa0d917...`
  > Cumplimiento.Parcial = . Recomendación I.1: Garantizar la divulgación por parte del Órgano de Administración de políticas aplicables a la relación de la Emisora con el grupo económico que encabeza y/o integra y con sus partes relacionadas, Incumpli miento.Incumpli miento = . Recomendación I.1: Gar...

---

## 7. Ancla — dominio `contable`

- **fuente:** Estados_Contables_Neuquen
- **document_id:** `DOC-0007`
- **chunk_uid:** `5a0f18fcd51b50882647af36cc6d871c106bb5d21ac7829074dbc3acd6430b5e`
- **ubicación:** 24.3 Riesgo de liquidez
- **título:** 24.3 Riesgo de liquidez

> La Sociedad administra su liquidez para garantizar los fondos necesarios para respaldar su estratégiade negocios. El perfil de los vencimientos de los pasivos financieros de la Sociedad que surgen dé' los acuerdos respectivos se encuentra descripto en la nota 14.2. BE TO J. SAGGESE Presidente Firmado a efectos de su identificación con nuestro informe de fecha 09-03-2015 VIQ't,.&, acu5n y Fjrri:!iz.15 1.5Js y F'ISTRELLI, H 'l'IN Y ASOCIADOS S.R.L. TOMAS CAMP NNI Peopy.lión Fis atizadora 1- -9 (1) ( rn n n cn = 00 -o § • c cn GERMÁN E. CANTALUPI Socio dor Público U.B.A. C.P.C.E. m m · · · · · · ...

**Distractores candidatos:**

- `0.611` · **MSU_ON_ClaseIV** · dominios `financiero|impositivo|legal` · chunk `3ff7de96bdc4a155...`
  > Nuestros requisitos de capital alcanzan en primera medida a los costos operativos y de mantenimiento relativos a nuestros activos operativos, inversiones en activos fijos relacionadas con el proyecto de expansión y conversión a ciclo combinado, y pagos del servicio de deuda. Nuestras fuentes princip...

---

## 8. Ancla — dominio `contable`

- **fuente:** TGS_EEFF_2024_4T
- **document_id:** `DOC-0020`
- **chunk_uid:** `5c79636b418694adb26bd130ce6bc85d4432c419bcf73a6c8b7e0cc45c66dda1`
- **ubicación:** Resultados
- **título:** Resultados

> Comprende las ganancias o pérdidas acumuladas sin asignación específica, que siendo positivas pueden ser distribuibles mediante decisión de la Asamblea de Accionistas, en tanto no estén sujetas a restricciones legales, como la mencionada en el apartado "Reserva Legal". Firmado a efectos de su identificación con nuestro informe de fecha 27 de febrero de 2025 PISTRELLI, HENRY MARTIN Y ASOCIADOS S.A. C.P.C.E.C.A.B.A. T° 1 - F° 13 Hernán Crocci Socio Contador Público U.B.A. C.P.C.E.C.A.B.A. T° 410 - F° 166 Véase nuestro informe de fecha 27 de febrero de 2025 PRICE WATERHOUSE & CO. S.R.L . (Socia) ...

**Distractores candidatos:**

- `0.635` · **Ley_20628_Impuesto_Ganancias_TO** · dominios `impositivo` · chunk `eac9ac0cd8435ef3...`
  > Art. 148 -Los titulares residentes en el país de los establecimientos estables definidos en el artículo 128, se asignarán los resultados impositivos de fuente extranjera de los mismos, aun cuando los beneficios no les hubieran sido remesados ni acreditados en sus cuentas. Idéntico criterio aplicarán...

- `0.628` · **RG_AFIP_830** · dominios `impositivo` · chunk `90a431fe1b9b6253...`
  > ñ) Cualquier otra cesión o locación de derechos, excepto las que correspondan a operaciones realizadas por intermedio de mercados de cereales a término que se resuelvan en el curso del término (arbitrajes) y de mercados de futuros y opciones. (Sustituido por Art. 1° Pto. 3.4 de la Resolución General...

- `0.620` · **Ley_20628_Impuesto_Ganancias_TO** · dominios `impositivo` · chunk `448b350323afdfe5...`
  > - Art. 2° -A los efectos de esta ley son ganancias, sin perjuicio de lo dispuesto especialmente en cada categoría y aun cuando no se indiquen en ellas: - 1) los rendimientos, rentas o enriquecimientos susceptibles de una periodicidad que implique la permanencia de la fuente que los produce y su habi...

---

## 9. Ancla — dominio `impositivo`

- **fuente:** Ley_20628_Impuesto_Ganancias_TO
- **document_id:** `DOC-0010`
- **chunk_uid:** `77f2a7fb2bd648cd6690459007f077012ac05c994fc3424aafdc17e8c76e6fd6`
- **ubicación:** Antecedentes Normativos
- **título:** Antecedentes Normativos

> - -Artículo 81, inciso c), primer párrafo sustituido por art. 65 de la Ley N° 25.600 B.O. 12/6/2002; - -Artículo 105: — La Ley N° 25.558 B.O. 8/1/2002, art. 1º se prorroga hasta el 31 de diciembre de 2005 la vigencia de la presente Ley. Vigencia: a partir del 1° de enero de 2002, inclusive; - -Artículo 23, apartado b), inciso 3), sustituido por art. 1° del Decreto N° 860/2001 B.O. 2/7/2001. Vigencia: desde el año fiscal en curso a la fecha de publicación del Decreto 860/2001; - -Artículo 23, apartado c), sustituido por art. 1° del Decreto N° 860/2001 B.O. 2/7/2001. Vigencia: desde el año fisca...

**Distractores candidatos:**

- `0.618` · **Ley_24065_Energia_Electrica_TO** · dominios `legal` · chunk `0e87efbaa001e600...`
  > - -Artículo 1 º sustituido por art . 1 del Decreto N ° 804/2001 (/normativa/nacional/norma -67414) B . O . 21/6/2001 . Sustitución derogada por art . 1 ° de la Ley N ° 25. 5. 468 (/normativa/nacional/norma -69315) B . O . 16/10/2001; - -Artículo 3 º , tercer y cuarto párrafos incorporados por art . ...

- `0.613` · **Ley_24065_Energia_Electrica_TO** · dominios `legal` · chunk `dd110c02bf55cb69...`
  > - -Artículo 21 sustituido por art . 7 ° del Decreto N ° 804/2001 (/normativa/nacional/norma -67414) B . O . 21/6/2001 . Sustitución derogada por art . 1 ° de la Ley N ° 25. 5. 468 (/normativa/nacional/norma -69315) B . O . 16/10/2001; - -Artículo 36 sustituido por art . 8 ° del Decreto N ° 804/2001 ...

- `0.600` · **Decreto_1738_1992_Reglamentario_Gas** · dominios `legal` · chunk `b1237830cfacceac...`
  > (5) El pedido de prórroga deberá ser solicitado con una antelación mayor a los CINCUENTA Y CUATRO (54) meses previos al vencimiento del plazo de licencia siempre que , a juicio de la Autoridad Regulatoria , resultare igualmente factible la evaluación de desempeño del solicitante y fuere aconsejable ...

---

## 10. Ancla — dominio `legal`

- **fuente:** Res_SE_61_1992_Los_Procedimientos
- **document_id:** `DOC-0018`
- **chunk_uid:** `976020e85039219b2a681400d334332e257fa817cc8de25cc2cf9de3fd51fa6f`
- **ubicación:** 2.4.7.3.1. VALOR SEMANAL DE LA ENERGIA ADICIONAL
- **título:** 2.4.7.3.1. VALOR SEMANAL DE LA ENERGIA ADICIONAL

> Al finalizar cada semana "s", , el OED debe evaluar el saldo de las pérdidas en el Mercado calculando la Diferencia por Energía que resulta y el monto semanal correspondiente, de acuerdo a la metodología establecida en el punto 2.4.7.1. Los montos calculados se deben repartir entre la demanda total del MEM abastecida en dicha semana. Para ello , el OED debe calcular el Valor Semanal de la Diferencia por Energía (VALSEME), dividiendo el Monto Semanal de Diferencia por Energía (SEMDIFE s ) por la integración de la demanda (PDEM) total abastecida en cada intervalo Spot de la semana. siendo: * h =...

**Distractores candidatos:**

- `0.638` · **Edenor_EEFF_Consolidado_2025_09** · dominios `contable` · chunk `e33ab7753573c1e3...`
  > N O T A S Compra de energía, 1 = La Sociedad factura a sus usuarios el costo de sus compras de energía, que incluye cargos por compras de energía y potencia. La Sociedad compra energía eléctrica a precios estacionales aprobados por la SE. El precio de la energía eléctrica de la Sociedad refleja los ...

- `0.606` · **Edenor_EEFF_Consolidado_2025_09** · dominios `contable` · chunk `aede19a7a58cb921...`
  > Asimismo, con fecha 26 de septiembre de 2025, mediante Resolución SE N° 379/2025 y en línea con el Decreto PEN N° 450/2025, la Secretaría de Energía creó el "Programa de Gestión de Demanda de Energía" de carácter voluntario, programado y remunerado. Se trata de un mecanismo orientado a reducir o eli...

- `0.603` · **Pampa_EEFF_Consolidado_1Q2026** · dominios `contable` · chunk `614f3fb11edde541...`
  > En el marco del nuevo régimen de Subsidios Energéticos Focalizados (SEF), el Decreto PEN N° 26/26 establece que el precio adjudicado a cada productor participante del Plan Gas.Ar puede ubicarse por encima, por debajo o en línea con el Precio Anual Uniforme ("PAU"), según el período del año y conside...

---

## 11. Ancla — dominio `financiero`

- **fuente:** Transener_Calificacion_FIX
- **document_id:** `DOC-0024`
- **chunk_uid:** `9bdd0f2ce76211ad067c47e8ee1457d795e73bc75944810e586e396c1a328c1a`
- **ubicación:** Fuentes
- **título:** Fuentes

> debe confiar en la labor de los expertos, incluyendo los auditores independientes, con respecto a los estados financieros y abogados con respecto a los aspectos legales y fiscales. Además, las calificaciones son intrínsecamente una visión hacia el futuro e incorporan las hipótesis y predicciones sobre acontecimientos que pueden suceder y que por su naturaleza no se pueden comprobar como hechos. Como resultado, a pesar de la comprobación de los hechos actuales, las calificaciones pueden verse afectadas por eventos futuros o condiciones que no se previeron en el momento en que se emitió o confir...

**Distractores candidatos:**

- `0.633` · **Estados_Contables_Neuquen** · dominios `contable` · chunk `1610b679a0e0e4e5...`
  > 3. Nuestra responsabilidad es expresar una opinión sobre los estados financieros mencionados en el párrafo 1 basada en nuestra auditoría. Hemos realizado nuestro trabajo de conformidad con las Normas Internacionales de Auditoría emitidas por el Consejo de Normas Internacionales de Auditoría y Asegur...

- `0.622` · **TGS_EEFF_2025_09** · dominios `contable` · chunk `d8e8bb2eb33e2385...`
  > Una revisión de información financiera intermedia consiste en la realización de indagaciones, principalmente a las personas responsables de los temas financieros y contables, y aplicar procedimientos analíticos y otros procedimientos de revisión. Una revisión tiene un alcance significativamente meno...

- `0.622` · **Ley_20628_Impuesto_Ganancias_TO** · dominios `impositivo` · chunk `b77de2befeb3de6e...`
  > Facúltase al PODER EJECUTIVO a fijar con carácter general porcentajes inferiores al establecido en el párrafo anterior cuando la aplicación de aquél pudiere dar lugar a resultados no acordes con la realidad. Art. 11 -Son de fuente argentina los ingresos provenientes de operaciones de seguros o rease...

---

## 12. Ancla — dominio `legal`

- **fuente:** Res_SE_61_1992_Los_Procedimientos
- **document_id:** `DOC-0018`
- **chunk_uid:** `aac0f34ec85c2e3bb7e42fbc2b507c648b31b8dcbd0b881a317ccdab7c92855c`
- **ubicación:** 4.2. HABILITACION COMO RESERVA DE CORTO PLAZO .
- **título:** 4.2. HABILITACION COMO RESERVA DE CORTO PLAZO .

> - Debido a las condiciones indicadas por el GUI, el OED no podrá verificar el cumplimiento de la interrumpibilidad ofertada como reserva de DIEZ (10) minutos. · El Gran Usuario ha ofertado previamente parte de su demanda como reserva de DIEZ (10) minutos y , al serle requerido el retiro de la misma, registró incumplimientos en el compromiso establecido , en la cantidad de potencia retirada y/o en el tiempo transcurrido para llevar a cabo dicha interrupción, que llevaron a su inhabilitación como reserva de DIEZ (10) minutos por un plazo que aún no ha finalizado para el período de vigencia de la...

**Distractores candidatos:**

- `0.645` · **RG_AFIP_830** · dominios `impositivo` · chunk `8a17ddbaec5c0651...`
  > 1. la omisión de liquidar e ingresar —total o parcialmente— las obligaciones comprendidas en este anexo, o 2. la realización de actos conducentes a la misma finalidad. Asimismo , cuando se verifique alguna de las situaciones previstas en el inciso b) del párrafo anterior, r, este Organismo emitirá u...

- `0.639` · **RG_AFIP_830** · dominios `impositivo` · chunk `78b2eeb8ed4bcb43...`
  > Los sujetos quedarán asimismo , inhabilitados para solicitar un nuevo certificado de exclusión por el término de UN (1) año , contado a partir del día inmediato siguiente, inclusive, a la fecha de notificación del acto administrativo que establezca la revocatoria del certificado otorgado , cuando: a...

- `0.616` · **RG_AFIP_830** · dominios `impositivo` · chunk `75f3990cf130fe63...`
  > Los sujetos quedarán inhabilitados para solicitar un nuevo certificado de exclusión, por el término de UN (1) año contado a partir del día inmediato siguiente, inclusive, a la fecha de notificación del acto administrativo que establezca la revocatoria del certificado otorgado , cuando ésta fuere con...

---

## 13. Ancla — dominio `financiero`

- **fuente:** Transener-Company-Presentation-April-2026
- **document_id:** `DOC-0023`
- **chunk_uid:** `b070e21307582542e0c5c156562d69c108148f2efc6b5d6e00e5a8f276fedb77`
- **ubicación:** Legal Disclaimer
- **título:** Legal Disclaimer

> The material that follows is a presentation of general information about TRANSENER as of the date indicated herein and is based on publicly available information . It is in summary form, does not purport to be complete, is not intended to be relied upon as advice to potential investors and may not be disclosed to any other person . No representation or warranty, express or implied, is made concerning, and no reliance should be placed on, the accuracy, fairness, or completeness of the information presented herein . This presentation contains statements that are forward-looking within the meanin...

**Distractores candidatos:**

- `0.646` · **EEFF-ind-31-03-2019** · dominios `contable` · chunk `5aac0c8e364fcc13...`
  > De acuerdo con lo dispuesto en el artículo Nº 294 de la Ley N º 19.550 y en las normas de la Comisión Nacional de Valores (en adelante "CNV"), hemos revisado los estados financieros individuales condensados intermedios adjuntos de Compañía de Transporte de Energía Eléctrica en Alta Tensión Transener...

- `0.643` · **FS-31-03-2019** · dominios `contable` · chunk `9be981a2810de457...`
  > General Meeting of Shareholders held on April 12, 2018:, Attributable to owners of the parent.Non controlling interests = . Ordinary General Meeting of Shareholders held on April 12, 2018:, Total equity = . - Legal reserve, Attributable to owners of the parent.Common Stock = 0. - Legal reserve, Att...

- `0.635` · **EEFF-ind-31-03-2019** · dominios `contable` · chunk `14d14a93b743415a...`
  > Hemos revisado los estados financieros individuales condensados intermedios adjuntos de Compañía de Transporte de Energía Eléctrica en Alta Tensión Transener S.A. (en adelante "la Sociedad") que comprenden el estado de situación financiera individual condensado intermedio al 31 de marzo de 2019 , lo...

---

## 14. Ancla — dominio `financiero`

- **fuente:** Transener_Calificacion_FIX
- **document_id:** `DOC-0024`
- **chunk_uid:** `c64625686122405e44be6e4bf911278b6c9c0b874c870dab49b85ecc081f6ad2`
- **ubicación:** Fuentes
- **título:** Fuentes

> - Estados financieros consolidados de períodos intermedios y anuales auditados hasta el 30/09/2025 . - Auditor externo a la fecha del último balance: Price Waterhouse & Co SRL. - Información de gestión de la compañía. Las calificaciones incluidas en este informe fueron solicitadas por el emisor o en su nombre y, por lo tanto FIX SCR S.A. AGENTE DE CALIFICACIÓN DE RIESGO (Afiliada de Fitch Ratings) – en adelante FIX SCR S.A. o la calificadora -, ha recibido honorarios correspondientes por la prestación de sus servicios de calificación.

**Distractores candidatos:**

- `0.710` · **TGS_EEFF_2025_09** · dominios `contable` · chunk `316ff5b5ba88bfd1...`
  > Nuestra revisión fue realizada de acuerdo con las normas de sindicatura vigentes. Dichas normas requieren que la revisión de los estados financieros intermedios se efectúe de acuerdo con las normas de revisión de información financiera intermedia vigentes e incluyen la verificación de la congruencia...

- `0.705` · **Pampa_EEFF_Consolidado_1Q2026** · dominios `contable` · chunk `9cdd69f0d8aa209c...`
  > Nuestra revisión fue realizada de acuerdo con las normas de sindicatura vigentes . Dichas normas requieren que la revisión de los estados financieros intermedios se efectúe de acuerdo con las normas de revisión de información financiera intermedia vigentes e incluyen la verificación de la congruenci...

- `0.704` · **TGS_EEFF_2024_4T** · dominios `contable` · chunk `7698ccb63ce8dd37...`
  > Hemos llevado a cabo nuestro examen de acuerdo con las normas de sindicatura vigentes. Dichas normas requieren que los exámenes de los estados financieros consolidados se efectúen de acuerdo con las normas de auditoría vigentes, e incluyan la verificación de la razonabilidad de la información signif...

---

## 15. Ancla — dominio `financiero`

- **fuente:** Transener_Calificacion_FIX
- **document_id:** `DOC-0024`
- **chunk_uid:** `c69484297c556148da02163eff7befdcbe68d48be7e78fd0f8be736d75a0a4b6`
- **ubicación:** Fuentes
- **título:** Fuentes

> Las calificaciones representan una opinión y no hacen ningún comentario sobre la adecuación del precio de mercado, la conveniencia de cualquier título para un inversor particular o la naturaleza impositiva o fiscal de los pagos efectuados en relación a los títulos. FIX SCR S.A . recibe honorarios por parte de los emisores, aseguradores, garantes, otros agentes y originadores de títulos, por las calificaciones. Dichos honorarios generalmente varían desde USD 1.000 a USD 200.000 (u otras monedas aplicables) por emisión. En algunos casos, FIX SCR S.A . calificará todas o algunas de las emisiones ...

**Distractores candidatos:**

- `0.621` · **FS-31-03-2019** · dominios `contable` · chunk `b9c2a9382481e7de...`
  > The estimated fair value of a financial instrument is the value to which this instrument can be exchanged in the market among interested parties, different from the value that can arise in a sale or forced liquidation. For the purpose of estimating the fair value of financial assets and liabilities,...

- `0.615` · **Ley_20628_Impuesto_Ganancias_TO** · dominios `impositivo` · chunk `b77de2befeb3de6e...`
  > Facúltase al PODER EJECUTIVO a fijar con carácter general porcentajes inferiores al establecido en el párrafo anterior cuando la aplicación de aquél pudiere dar lugar a resultados no acordes con la realidad. Art. 11 -Son de fuente argentina los ingresos provenientes de operaciones de seguros o rease...

---

## 16. Ancla — dominio `legal`

- **fuente:** ENRE_Resolucion_544_2024
- **document_id:** `DOC-0006`
- **chunk_uid:** `cbf6e1adbf6c40980c3045bd5a429617070dc304933033b8ea688cecd7c9331d`
- **ubicación:** RESUELVE:
- **título:** RESUELVE:

> ARTÍCULO 6.- EDESUR S.A. y EDENOR S.A. no podrán cobrar el "Recargo por apartamiento en el coseno (fi)" conjunto, en el caso inmuebles bajo el régimen de propiedad horizontal o conjunto inmobiliario, definido en el artículo 4 de la presente resolución, una vez que el inmueble o conjunto cuente con medidores inteligentes con capacidad de registrar coseno (fi) en todas las unidades de los mismos. Una vez instalados estos medidores, los recargos afectarán la facturación de cada unidad del local, inmueble o conjunto, incluida como una unidad la cuenta del consorcio de copropietarios por los servic...

**Distractores candidatos:**

- `0.607` · **Ley_23966_Combustibles_Liquidos_Gas** · dominios `impositivo` · chunk `16dc18c23c66c6db...`
  > ARTICULO 24 — El producido de los recargos sobre el precio de venta de la electricidad establecidos por el inciso e) del artículo 30 de la Ley Nº 15.336 y el inciso b) del artículo 2º de la Ley Nº 17.574 se destinará al Tesoro Nacional. Todos los gastos que demande el funcionamiento del CONSEJO FEDE...

---

## 17. Ancla — dominio `contable`

- **fuente:** Estados_Contables_Neuquen
- **document_id:** `DOC-0007`
- **chunk_uid:** `d661a9951fbfa5e26c9160b1d56f5b1259bedcaf72470634b527fb18e153a4a9`
- **ubicación:** GAS Y PETRÓLEO DEL NEUQUÉN S.A.
- **título:** GAS Y PETRÓLEO DEL NEUQUÉN S.A.

> indicar que es improbable que puedan realizarse cambios significativos en esa venta o distribución o que éstas puedan cancelarse. La Gerencia debe comprometerse a completar la venta o distribución y concretarlas dentro del año siguiente a la fecha de la clasificación. Las propiedades, planta y equipo y los activos intangibles no se someten a depreciación ni amortización una vez que son clasificados como mantenidos para la venta o para su distribución a los propietarios. Los activos y pasivos clasificados como mantenidos para la venta o su distribución a los propietarios se presentan en una lín...

**Distractores candidatos:**

- `0.603` · **Decreto_1738_1992_Reglamentario_Gas** · dominios `legal` · chunk `add0b4cc9c22cfb6...`
  > (3) En caso de corresponder la declaración de caducidad de la habilitación , el Ente dispondrá , atendiendo a las circunstancias del caso , a la configuración de las tenencias accionarias en la sociedad habilitada y a la mejor protección del interés público , (i) que la licitación involucre la venta...

---

## 18. Ancla — dominio `contable`

- **fuente:** TGS_EEFF_2025_09
- **document_id:** `DOC-0021`
- **chunk_uid:** `d6b27f9a47e89175655f24ba38d30063c13c0bb20164b54fd26d3bfbc7939a77`
- **ubicación:** Responsabilidad de los auditores
- **título:** Responsabilidad de los auditores

> 3. Nuestra responsabilidad es expresar una conclusión sobre los estados financieros mencionados en el párrafo 1 basada en nuestra revisión, la cual fue realizada de acuerdo con la Norma Internacional sobre Encargos de Revisión 2410 "Revisión de información financiera de períodos intermedios realizada por el auditor independiente de la entidad", emitida por el Consejo de Normas Internacionales de Auditoría y Aseguramiento ("IAASB" por su siglas en inglés), la cual fue adoptada como norma de revisión en Argentina mediante la Resolución Técnica N° 33 de FACPCE. Dicha norma requiere que el auditor...

**Distractores candidatos:**

- `0.631` · **Transener_Calificacion_FIX** · dominios `financiero` · chunk `c64625686122405e...`
  > - Estados financieros consolidados de períodos intermedios y anuales auditados hasta el 30/09/2025 . - Auditor externo a la fecha del último balance: Price Waterhouse & Co SRL. - Información de gestión de la compañía. Las calificaciones incluidas en este informe fueron solicitadas por el emisor o en...

- `0.608` · **Ley_11683_Procedimiento_Fiscal_TO** · dominios `impositivo` · chunk `b38716526a867321...`
  > (Artículo sustituido por art . 178 de la Ley N ° 27430 (/normativa/nacional/norma -305262) B . O . 29/12/2017. 7. Vigencia: el día siguiente al de su publicación en el Boletín Oficial y surtirán efecto de conformidad con lo previsto en cada uno de los Títulos que la componen . Ver art . 247 de la Le...

- `0.606` · **Ley_11683_Procedimiento_Fiscal_TO** · dominios `impositivo` · chunk `a7f23ded91e1a5ca...`
  > - 1 . A los tres (3) meses de efectuada la transferencia , si con una antelación de quince . (15) días ésta hubiera sido denunciada a la Administración Federal de Ingresos Públicos . - 2 . En cualquier momento en que la Administración Federal de Ingresos Públicos reconozca como suficiente la solvenc...

---

## 20. Ancla — dominio `contable`

- **fuente:** TGS_EEFF_2024_4T
- **document_id:** `DOC-0020`
- **chunk_uid:** `ddb998627c4dddf5888bc18b447ffcc6b0d6c78c7e3cec4d2396a713a6ce80a1`
- **ubicación:** TRANSPORTADORA DE GAS DEL SUR S.A.
- **título:** TRANSPORTADORA DE GAS DEL SUR S.A.

> Sin plazo, 31 de diciembre de 2024.Deudas financieras = -. Sin plazo, 31 de diciembre de 2024.Otros pasivos financieros = -. Sin plazo, 31 de diciembre de 2024.Arrendamientos financieros = -. Con plazo, 31 de diciembre de 2024.Deudas financieras = . Con plazo, 31 de diciembre de 2024.Otros pasivos financieros = . Con plazo, 31 de diciembre de 2024.Arrendamientos financieros = . Vencido, 31 de diciembre de 2024.Deudas financieras = . Vencido, 31 de diciembre de 2024.Otros pasivos financieros = . Vencido, 31 de diciembre de 2024.Arrendamientos financieros = . Hasta el 31-12-2023, 31 de diciembre...

**Distractores candidatos:**

- `0.707` · **MSU_ON_ClaseIV** · dominios `financiero|impositivo|legal` · chunk `5232d75248bfb18b...`
  > 31/3/2022.(en miles de Pesos) = 5,069. Deuda por arrendamiento financiero, 31/12/2021.(en miles de Pesos) = 6,076. Préstamos financieros, 31/3/2022.(en miles de Pesos) = 1,607,065. Préstamos financieros, 31/12/2021.(en miles de Pesos) = 1,487,052. Deuda a largo plazo, 31/3/2022.(en miles de Pesos) =...

- `0.698` · **MSU_ON_ClaseIV** · dominios `financiero|impositivo|legal` · chunk `9895f92367420b68...`
  > Deudas financieras, 31/12/2021 = 81,795,378. Total del pasivo no corriente, 31/3/2022 (en miles de Pesos) = 88,373,168. Total del pasivo no corriente, 31/12/2021 = 85,195,686. PASIVO CORRIENTE, 31/3/2022 (en miles de Pesos) = . PASIVO CORRIENTE, 31/12/2021 = . Deudas financieras, 31/3/2022 (en miles...

- `0.688` · **MSU_ON_ClaseIV** · dominios `financiero|impositivo|legal` · chunk `6aa145ecfaf3c98c...`
  > ACTIVO, 31/3/2022 (en miles de Pesos) = . ACTIVO, 31/12/2021 = . ACTIVO NO CORRIENTE, 31/3/2022 (en miles de Pesos) = . ACTIVO NO CORRIENTE, 31/12/2021 = . Propiedad, planta y equipo, 31/3/2022 (en miles de Pesos) = 101,602,705. Propiedad, planta y equipo, 31/12/2021 = 94,645,378. Préstamos financie...

---

## 21. Ancla — dominio `financiero`

- **fuente:** Transener-Company-Presentation-April-2026
- **document_id:** `DOC-0023`
- **chunk_uid:** `e2d25dd37700c71a855d85bd4ae90dabf8a4946609fbd190d8aaf37231fa72f0`
- **ubicación:** Regulatory Asset and Rate of Return in US$ MM
- **título:** Regulatory Asset and Rate of Return in US$ MM

> Regulatory Asset, Year 1 = 683. Regulatory Asset, Year 2 = 683. Regulatory Asset, Year 3 = 683. Regulatory Asset, Year 4 = 683. Regulatory Asset, Year 5 = 683. Rate of Return, Year 1 = 6,96%. Rate of Return, Year 2 = 6,96%. Rate of Return, Year 3 = 6,96%. Rate of Return, Year 4 = 6,96%. Rate of Return, Year 5 = 6,96%. $MM Net Income, Year 1 = 48. $MM Net Income, Year 2 = 48. $MM Net Income, Year 3 = 48. $MM Net Income, Year 4 = 48. $MM Net Income, Year 5 = 48. Total Return, Year 1 = 6,96%. Total Return, Year 2 = 6,96%. Total Return, Year 3 = 6,96%. Total Return, Year 4 = 6,96%. Total Return, Y...

**Distractores candidatos:**

- `0.610` · **TR-consolidado-03-2026_VF-Clean** · dominios `contable` · chunk `4eae40b6a9d46e6a...`
  > Recupero de siniestros, Período de tres meses finalizado el.31.03.2026 = 159.417. Recupero de siniestros, Período de tres meses finalizado el.31.03.2025 = 2.767.760. Provisiones regulatorias, Período de tres meses finalizado el.31.03.2026 = (344.085). Provisiones regulatorias, Período de tres meses ...

- `0.605` · **TGS_EEFF_2025_09** · dominios `contable` · chunk `5cb081b96198c79e...`
  > 461.725.091, (en miles de pesos ) = . Utilidad neta antes del impuesto a las ganancias 411.985.890 460.732.331 236.651.912 407.371.502 461.725.091, (en miles de pesos ) = . Impuesto a las ganancias (136.758.987) (167.376.353) (111.887.367) (139.089.906) (186.892.695), (en miles de pesos ) = . Impues...

- `0.603` · **Edenor_EEFF_Consolidado_2025_09** · dominios `contable` · chunk `35a483827e60938f...`
  > (522.161). Resultados financieros y por tenencia, 30.09.23 = (696.434). Resultados financieros y por tenencia, 30.09.22 = (503.368). Resultados financieros y por tenencia, 30.09.21 = (271.814). RECPAM, 30.09.25 = 209.782. RECPAM, 30.09.24 = 694.600. RECPAM, 30.09.23 = 879.071. RECPAM, 30.09.22 = 596...

---

## 23. Ancla — dominio `financiero`

- **fuente:** Transener-Company-Presentation-April-2026
- **document_id:** `DOC-0023`
- **chunk_uid:** `eeab949cfdb2f637a72ed4f7248bd6d73281e727c2f6ff09b1ca9c14effb49af`
- **ubicación:** Company Overview
- **título:** Company Overview

> + 13.341 km (8.290 miles) and supervises 2.116 km (1.315 miles) of independent transmitters 500 kV and 220 kV Lines + 1.170 Highly skilled employees developed through the organization's own training programs . + 54 (supervises 7 of independent transmitters) - Substations + 23.355 MVA (supervises 4.200 MVA of independent transmitters) of transformation capacity Own material resources for the execution of activities - Company Overview

**Distractores candidatos:**

- `0.685` · **Edenor_EEFF_Consolidado_2025_09** · dominios `contable` · chunk `463d997d4a099241...`
  > Materiales y repuestos = 15.963. Neto resultante, Total = 3.381.035. Altas, Terrenos y Edificios = 1.038. Altas, Subestaciones = 14. Altas, Redes de alta, media y baja tensión = 2.292. Altas, Medidores y Cámaras y plataformas de transformación = 11.379. Altas, Herramientas, Muebles y Útiles, Rodados...

- `0.681` · **Edenor_EEFF_Consolidado_2025_09** · dominios `contable` · chunk `b80629a2bded3e7f...`
  > (138.378) -. Neto resultante 30.09.24, Terrenos y Edificios = 69.217. Neto resultante 30.09.24, Subestaciones = 513.320. Neto resultante 30.09.24, Redes de alta, media y baja tensión = 1.218.569. Neto resultante 30.09.24, Medidores y Cámaras y plataformas de transformación = 530.899. Neto resultante...

- `0.655` · **Edenor_EEFF_Consolidado_2025_09** · dominios `contable` · chunk `c376ed387a69d568...`
  > Materiales y repuestos = 41.779. Neto resultante, Total = 3.662.175. Altas, Terrenos y Edificios = 1.420. Altas, Subestaciones = 61. Altas, Redes de alta, media y baja tensión = 2.136. Altas, Medidores y Cámaras y plataformas de transformación = 10.211. Altas, Herramientas, Muebles y Útiles, Rodados...

---
