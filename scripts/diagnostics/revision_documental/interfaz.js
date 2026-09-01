/* === INICIO LOGICA PURA === */
const copiar = v => JSON.parse(JSON.stringify(v));
const limpio = v => typeof v === "string" ? v.trim() : "";
/* Version del criterio de revision. Se sella en cada ficha AL GUARDARLA, nunca
   sobre registros anteriores: una decision tomada con la consigna vieja no se
   convierte en una decision con la consigna nueva porque el archivo se haya
   regenerado. Los registros sin sello quedan con `null` y se leen como
   "anterior al versionado". */
const CRITERIO_VERSION="criterio-dominios-2026-08-30";
const CRITERIO_RESUMEN="Dominios de conocimiento: se marca un tema si puede senalarse un pasaje o tabla con contenido sustantivo de ese tema; no se exige que sea el tema principal ni un umbral de menciones.";
function nuevaFicha(){return {decision:"",emisor:"",tipo:"",periodo:"",periodo_desconocido:false,dominios:[],evidencia:"",comentarios:"",consultado:false,antecedente_declarado:false};}
function periodoValido(v){
  if(/^\d{4}$/.test(v)||/^[1-4]T\d{4}$/.test(v))return true;
  if(!/^\d{4}-\d{2}-\d{2}$/.test(v))return false;
  const fecha=new Date(v+"T00:00:00Z");
  return Number.isFinite(fecha.getTime())&&fecha.toISOString().slice(0,10)===v;
}
function validarFicha(f,tipos,dominios){
  if(!["incluir","dudoso","excluir"].includes(f.decision))return "Elegí si sirve, si tenés dudas o si proponés excluirlo.";
  if(!f.consultado)return "Abrí el original y marcá que lo consultaste. Si no abre, dejá un comentario y guardá el borrador.";
  if(f.decision!=="incluir"&&!limpio(f.comentarios))return "Explicá la duda o el motivo de exclusión en Comentarios.";
  if(f.tipo&&!tipos.includes(f.tipo))return "Elegí un tipo de la lista.";
  if(!Array.isArray(f.dominios)||f.dominios.some(d=>!dominios.concat("ninguno").includes(d))||new Set(f.dominios).size!==f.dominios.length)return "Revisá los temas seleccionados.";
  if(f.dominios.includes("ninguno")&&f.dominios.length>1)return "«Ninguno» no se puede combinar con otros temas.";
  if(f.periodo_desconocido&&limpio(f.periodo))return "Si no determinaste el período, dejá ese campo vacío.";
  if(limpio(f.periodo)&&!periodoValido(limpio(f.periodo)))return "Revisá el período: ejemplos válidos 2025, 1T2026 o 2026-03-31 (fecha real).";
  if(f.decision==="incluir"){
    if(!limpio(f.emisor))return "Indicá quién emite el documento. Si no está claro, marcá «Tengo una duda».";
    if(!f.tipo)return "Elegí el tipo de documento, o «No determinado» si corresponde.";
    if(!limpio(f.periodo)&&!f.periodo_desconocido)return "Completá el período o marcá que no pudiste determinarlo / no corresponde.";
    if(!f.dominios.length)return "Marcá los temas pertinentes o «Ninguno de estos cuatro».";
  }
  return "";
}
function cambiarDominio(actual,d,marcado){
  const s=new Set(actual);
  if(d==="ninguno"&&marcado)return ["ninguno"];
  if(marcado){s.delete("ninguno");s.add(d);}else s.delete(d);
  return Array.from(s).sort();
}
function contenidoComparable(f){
  return JSON.stringify([f.decision,limpio(f.emisor),f.tipo,limpio(f.periodo),!!f.periodo_desconocido,[...(f.dominios||[])].sort()]);
}
function cambioDeCriterio(e){return e.inicial ? contenidoComparable(e.inicial)!==contenidoComparable(e.borrador) : null;}
function estadoRegistro(e){
  if(!e)return "pendiente";
  return e.finalizado_en ? e.borrador.decision : "pendiente";
}
function tieneAvance(e){
  if(!e)return false;
  return !!(e.inicial||e.antecedente_v2||e.finalizado_en||
    Object.keys(nuevaFicha()).some(k=>JSON.stringify(e.borrador[k])!==JSON.stringify(nuevaFicha()[k])));
}
function guardarLectura(e,fecha,tipos,dominios){
  const error=validarFicha(e.borrador,tipos,dominios);
  if(error)throw new Error(error);
  if(!e.inicial){
    e.inicial=copiar(e.borrador);e.revelada_en=fecha;
    /* Un antecedente importado NO se convierte retroactivamente en lectura
       ciega, y uno declarado por la persona tampoco: el sistema no puede saber
       que vio antes de abrir la ficha, asi que lo unico honesto es dejar que lo
       declare y registrarlo. */
    e.origen_lectura=e.antecedente_v2 ? "revision_con_antecedentes_v2"
      : (e.borrador.antecedente_declarado ? "revision_con_antecedente_declarado"
      : "manual_pre_revelado");
    e.criterio_version=CRITERIO_VERSION;
  }
}
function finalizar(e,fecha,tipos,dominios){
  if(!e.inicial||!e.revelada_en)throw new Error("Primero guardá tu lectura y compará la propuesta en esta ficha.");
  const error=validarFicha(e.borrador,tipos,dominios);if(error)throw new Error(error);
  e.finalizado_en=fecha;
  e.criterio_version_final=CRITERIO_VERSION;
  e.historial=e.historial||[];
  e.historial.push({fecha,decision:copiar(e.borrador),cambio_tras_revelar:cambioDeCriterio(e),
    criterio_version:CRITERIO_VERSION});
}
function exportarEstado(D,est,fecha){
  const decisiones=D.documentos.map(d=>({id:d.id,archivo:d.archivo,ruta:d.ruta,cohorte:d.cohorte,
    registro:copiar(est[d.id]||{borrador:nuevaFicha()}),estado:estadoRegistro(est[d.id]),
    cambio_tras_revelar:est[d.id]?cambioDeCriterio(est[d.id]):null}));
  return {receta:D.receta,huella_fuentes:D.huella_fuentes,fecha_exportacion:fecha,
    criterio_version:CRITERIO_VERSION,criterio_resumen:CRITERIO_RESUMEN,
    alcance:D.alcance,decisiones,
    advertencias:["No aplica cambios al corpus. Dudoso no significa validado.",
      "La primera lectura se preserva; los antecedentes v2 no se convierten en referencias ciegas nuevas.",
      "La etiqueta documental no sustituye el Golden de preguntas y evidencias."]};
}
function importarEstado(D,paquete,actual){
  if(!paquete||paquete.huella_fuentes!==D.huella_fuentes)throw new Error("El archivo corresponde a otro inventario. No se importó nada.");
  const v3=paquete.receta===D.receta;
  if(!v3&&paquete.receta!=="interfaz-corpus-v2-ciega")throw new Error("Formato no reconocido: usá un JSON de esta interfaz o de la v2.");
  if(!Array.isArray(paquete.decisiones))throw new Error("El JSON no contiene decisiones.");
  const salida=copiar(actual), ids=new Set(D.documentos.map(d=>d.id)), vistos=new Set();
  for(const d of paquete.decisiones){
    if(!ids.has(d.id)||vistos.has(d.id))throw new Error("Identificador desconocido o repetido. No se importó nada.");
    vistos.add(d.id);
    // Importación aditiva: jamás pisar lo ya escrito en esta interfaz.
    if(tieneAvance(salida[d.id]))continue;
    if(v3){
      const e=d.registro;
      if(!e||!e.borrador||typeof e.borrador!=="object")throw new Error("Registro sin ficha válida.");
      for(const f of [e.borrador,e.inicial].filter(Boolean)){
        for(const k of ["decision","emisor","tipo","periodo","evidencia","comentarios"])
          if(typeof f[k]!=="string")throw new Error("Campos de ficha inválidos.");
        if(!Array.isArray(f.dominios)||typeof f.consultado!=="boolean"||typeof f.periodo_desconocido!=="boolean")throw new Error("Campos de ficha inválidos.");
      if(f.antecedente_declarado===undefined)f.antecedente_declarado=false;
      }
      if(e.finalizado_en&&(!e.inicial||!e.revelada_en||validarFicha(e.borrador,D.vocabulario_tipo,D.dominios)))throw new Error("El archivo marca como terminada una ficha incompleta.");
      if(tieneAvance(e))salida[d.id]=copiar(e);
    }else{
      const c=d.ciega||{}, a=d.adjudicada||{};
      if(!Object.keys(c).length&&!Object.keys(a).length&&!limpio(d.observaciones))continue;
      const f=nuevaFicha();const revision=Object.keys(a).length?a:c;
      for(const k of ["emisor","tipo","periodo"])f[k]=limpio(revision[k]);
      f.dominios=Array.isArray(revision.dominios)?revision.dominios.filter(x=>D.dominios.concat("ninguno").includes(x)):[];
      f.comentarios=[d.observaciones,c.observaciones,a.observaciones].map(limpio).filter(Boolean).join("\n");
      f.decision=({dudoso:"dudoso",excluir:"excluir"})[revision.decision]||"";
      // Confirmar en v2 podía dejar todos los campos vacíos: no inferir etiquetas.
      salida[d.id]={borrador:f,antecedente_v2:copiar(d),historial:[]};
    }
  }
  return salida;
}
/* === FIN LOGICA PURA === */

(function(){
"use strict";
const $=id=>document.getElementById(id);
const D=JSON.parse($("datos").textContent), CLAVE="revision_documental_v3::"+D.huella_fuentes;
let est={}, indice=0, persistencia=true, bloqueoAlmacen=false;
const nombresTipo={estado_financiero:"Estado financiero / balance",memoria_anual:"Memoria anual",reporte_resultados:"Reporte de resultados",presentacion_inversores:"Presentación a inversores",prospecto:"Prospecto",obligacion_negociable:"Obligación negociable",informe_calificacion:"Informe de calificación",reporte_sostenibilidad:"Reporte de sostenibilidad",ley:"Ley",decreto:"Decreto",resolucion:"Resolución",resolucion_general:"Resolución general",disposicion:"Disposición",texto_ordenado:"Texto ordenado",procedimiento_regulatorio:"Procedimiento regulatorio",terminos_y_condiciones:"Términos y condiciones",codigo_de_etica:"Código de ética",no_determinado:"No determinado"};
/* Descripciones alineadas con `config.SILOS`, que es la definicion vigente del
   proyecto. Dos diferencias con la ayuda anterior quedan registradas en
   reports/contraste_dominios_2026-08-30.md y NO se resolvieron aca:
   - `legal` en config.SILOS es materia juridico-regulatoria DEL SECTOR
     ENERGETICO; la ayuda anterior decia "normas, obligaciones, contratos o
     regulacion", que es generico y volveria legal a casi cualquier documento;
   - `contable` en config.SILOS incluye "estados contables Y FINANCIEROS", asi
     que un juego de estados financieros es contable. La lectura corriente diria
     lo contrario, y por eso se explica aparte. */
const temas={
 legal:["Legal / regulatorio energético","Reglas del sector energético: quién puede operar, con qué obligaciones y bajo qué control.",{
  incluye:"Organización del mercado eléctrico y de gas; quién puede generar, transportar o distribuir; concesiones, licencias, habilitaciones y pliegos; obligaciones de servicio, calidad y seguridad; régimen tarifario y audiencias públicas; facultades y procedimientos del ENRE, ENARGAS y la Secretaría de Energía; contravenciones y sanciones regulatorias; contratos y litigios del sector. La etiqueta se asigna por la MATERIA que el documento desarrolla, no por su forma jurídica: una ley tributaria sigue siendo una ley, y aun así es «impositivo», no «legal».",
  no_alcanza:"Citar el número de una norma en un listado sin decir qué dispone. Remitir a otro documento «según lo establecido en la Resolución X» sin desarrollarlo. Un pie de página con la fecha de publicación.",
  ejemplo:"Norma: el artículo que fija el procedimiento de audiencia pública. · Informe: la nota que explica cómo la revisión tarifaria afecta los ingresos del período. · Planilla: la hoja con el cuadro tarifario aplicado a cada categoría."}],
 impositivo:["Impositivo","Qué hechos están gravados, quién debe pagar y cómo se determina.",{
  incluye:"Impuestos, tasas y contribuciones; IVA, Ganancias, Bienes Personales, Ingresos Brutos, internos y sobre combustibles; alícuotas y base imponible; retenciones, percepciones y agentes de retención; declaraciones juradas, determinación de oficio, prescripción, intereses resarcitorios y sanciones fiscales; facultades de AFIP/ARCA.",
  no_alcanza:"La línea «impuesto a las ganancias» dentro de un cuadro de resultados, sin cálculo ni explicación: eso es exposición contable. Nombrar a AFIP como destinatario de una presentación.",
  ejemplo:"Norma: el artículo que fija una alícuota o define el hecho imponible. · Informe: la nota de impuesto diferido que explica cómo se determinó. · Planilla: la hoja con el detalle de la carga fiscal por concepto."}],
 contable:["Contable","Cómo se registra y se expone la situación económica de una entidad.",{
  incluye:"Estados contables y financieros (situación patrimonial, resultados, flujo de efectivo, cambios en el patrimonio); notas y anexos; activo, pasivo, patrimonio neto, ingresos, costos y resultados del período; criterios de valuación y normas contables (NIIF, RT FACPCE); registración, conciliaciones e informes de auditoría sobre los estados.",
  no_alcanza:"Una cifra de facturación suelta en una gacetilla, sin el estado ni la nota que la sostenga. Un titular con el resultado del trimestre.",
  ejemplo:"Informe: el estado de situación patrimonial y sus notas. · Planilla: la hoja de balance con activo y pasivo por rubro. · Norma: el artículo que fija un criterio de valuación.",
  aviso:"Un juego de estados financieros es CONTABLE, aunque diga «financiero» en el título."}],
 financiero:["Financiero","Instrumentos, financiamiento y análisis de valor.",{
  incluye:"Emisión y colocación de deuda y capital (obligaciones negociables, prospectos, suplementos de precio); calificaciones de riesgo crediticio; estructura de capital, apalancamiento y liquidez; valuación, proyecciones y flujos de fondos; presentaciones a inversores y análisis de desempeño; mercados, tasas y riesgo financiero.",
  no_alcanza:"El rubro «préstamos» del pasivo sin condiciones ni análisis: eso es contable. Mencionar que la empresa tiene deuda, sin desarrollarla.",
  ejemplo:"Informe: la sección que describe una emisión y sus condiciones (tasa, vencimiento, garantías). · Planilla: la hoja de caja y deuda con el perfil de vencimientos. · Norma: es poco frecuente; podría aparecer en un régimen de oferta pública."}],
 ninguno:["Ninguno de estos cuatro","No pude señalar contenido sustantivo de ninguno de los cuatro temas.",{
  incluye:"Marcalo cuando el documento no desarrolla materia de ninguno de los cuatro dominios, o cuando lo que hay es puramente administrativo: firmas, publicación, entrada en vigencia, índices, cierres.",
  no_alcanza:"No es «no estoy seguro». Si dudás, elegí «Tengo una duda que hay que resolver» y explicá por qué en los comentarios.",
  ejemplo:"Un código de ética. Unos términos y condiciones de facturación digital. Un aviso de convocatoria."}]};
const etiquetas={pendiente:"Sin terminar",incluir:"Revisado para incluir",dudoso:"Duda pendiente",excluir:"Propuesto para excluir"};
function elemento(tag,texto,clase){const n=document.createElement(tag);if(texto!==undefined)n.textContent=texto;if(clase)n.className=clase;return n;}
function aviso(texto){$("mensaje").textContent=texto;$("mensaje").hidden=false;}
try{
  const previo=localStorage.getItem(CLAVE);
  if(previo){const p=JSON.parse(previo);est=importarEstado(D,p,{});}
}catch(e){persistencia=false;bloqueoAlmacen=true;aviso("No se pudo recuperar el guardado local. No lo sobrescribiremos. Recuperá tu JSON de respaldo o descargá el nuevo avance por separado.");}
function guardar(){
  const p=exportarEstado(D,est,new Date().toISOString());
  if(!bloqueoAlmacen){try{localStorage.setItem(CLAVE,JSON.stringify(p));persistencia=true;}catch(e){persistencia=false;}}
  $("guardado").textContent=persistencia?"Guardado en este navegador · descargá un respaldo antes de cerrar.":"No hay guardado automático disponible: descargá el avance antes de salir.";
}
function actual(){const id=D.documentos[indice].id;return est[id]||{borrador:nuevaFicha(),historial:[]};}
function asignar(e){est[D.documentos[indice].id]=e;}
function editar(campo,valor){const e=actual();e.borrador[campo]=valor;delete e.finalizado_en;asignar(e);guardar();pintarEstado();}
function estadoLista(){
  const conteos={pendiente:0,incluir:0,dudoso:0,excluir:0};
  D.documentos.forEach(d=>conteos[estadoRegistro(est[d.id])]++);
  const terminados=D.documentos.length-conteos.pendiente;
  $("progreso").textContent=terminados+" de "+D.documentos.length+" fichas terminadas · "+conteos.dudoso+" con dudas";
  $("barra").max=D.documentos.length;$("barra").value=terminados;
  const lista=$("lista");lista.replaceChildren();
  const q=$("buscar").value.trim().toLocaleLowerCase(),filtro=$("filtro").value;
  D.documentos.forEach((d,k)=>{
    const s=estadoRegistro(est[d.id]);
    if(filtro!=="todos"&&s!==filtro)return;
    if(q&&!(d.id+" "+d.archivo).toLocaleLowerCase().includes(q))return;
    const b=elemento("button",undefined,"docbutton");b.type="button";b.setAttribute("aria-current",String(k===indice));
    b.append(elemento("strong",(k+1)+". "+d.archivo),elemento("small",etiquetas[s]));
    b.onclick=()=>{indice=k;pintar();};lista.append(b);
  });
  if(!lista.childElementCount)lista.append(elemento("p","No hay documentos con este filtro.","help"));
}
function pintarEstado(){
  const e=actual(),error=validarFicha(e.borrador,D.vocabulario_tipo,D.dominios);
  $("estado").textContent=etiquetas[estadoRegistro(est[D.documentos[indice].id])];
  $("error").textContent=error;
  $("comparar").disabled=!!error;$("terminar").disabled=!!error;
  $("hay-cambio").textContent=e.inicial?(cambioDeCriterio(e)?"Tu decisión final cambia respecto de tu primera lectura. Ambas quedan guardadas.":"Mantenés tu criterio inicial. No hace falta completar la ficha otra vez."):"";
  estadoLista();
}
function valores(f){return [f.emisor||"No indicado",nombresTipo[f.tipo]||f.tipo||"No indicado",f.periodo_desconocido?"No determinado / no corresponde":f.periodo||"No indicado",(f.dominios||[]).join(", ")||"No indicados"];}
function pintarComparacion(d,e){
  $("comparacion").hidden=!e.inicial;$("comparar").hidden=!!e.inicial;
  $("tabla-comparacion").replaceChildren();$("fundamentos").replaceChildren();
  if(!e.inicial)return;
  const tabla=elemento("table",undefined,"comparison"),thead=elemento("thead"),fila=elemento("tr");
  ["Dato","Tu primera lectura","Sugerencia automática"].forEach(t=>fila.append(elemento("th",t)));thead.append(fila);tabla.append(thead);
  const tbody=elemento("tbody"),p=d.propuesta||{},iv=valores(e.inicial),pv=valores(p);
  ["Emisor","Tipo","Período","Temas"].forEach((t,k)=>{const tr=elemento("tr");[t,iv[k],pv[k]].forEach(v=>tr.append(elemento("td",v)));tbody.append(tr);});
  tabla.append(tbody);$("tabla-comparacion").append(tabla);
  const fund=$("fundamentos");
  fund.append(elemento("p","Confianza automática: emisor "+(p.confianza_emisor||"no informada")+"; período "+(p.confianza_periodo||"no informada")+". No equivale a validación humana.","help"));
  fund.append(elemento("p","A partir de acá esta ficha es una revisión asistida, no una lectura ciega. Tu primera lectura quedó conservada aparte; lo que decidas después de ver esto ya está influido por la propuesta, y eso no lo cambia el hecho de que los conteos estén guardados fuera de la vista.","note warning"));
  (p.avisos||[]).forEach(t=>fund.append(elemento("p",t,"note warning")));
  /* Vista principal: pasaje, pagina y por que se propuso, en palabras. Los
     conteos (`motivo`, `ocurrencias`, `terminos`, `paginas_termino`) son el
     criterio de corte de la maquina, no el criterio humano, asi que bajan al
     registro tecnico. Ocultarlos NO vuelve ciega la revision: quien ya vio la
     propuesta, la vio. */
  (p.evidencia||[]).forEach(ev=>{
    const donde="página "+(ev.pagina||"no indicada");
    fund.append(elemento("p",(ev.dominio||"")+" · "+donde
      +(ev.termino?" · se encontró «"+ev.termino+"»":"")+": "+(ev.cita||""),"help"));
  });
  if(!(p.evidencia||[]).length)fund.append(elemento("p","Sin extractos justificativos en esta propuesta. Contrastá con el original.","help"));
  const tecnicos=(p.evidencia||[]).filter(ev=>ev.motivo||ev.ocurrencias!==undefined);
  if(tecnicos.length){
    const dt=elemento("details"),ds=elemento("summary","Registro técnico: cómo contó la máquina");
    dt.append(ds,elemento("p","Estos conteos son el corte automático. Tu criterio no usa umbrales: alcanza con que puedas señalar el pasaje.","help"));
    tecnicos.forEach(ev=>dt.append(elemento("p",(ev.dominio||"")+" · "+(ev.termino||"")+" · "+(ev.motivo||"")
      +(ev.propuesto===false?" · no alcanzó el corte":""),"help")));
    fund.append(dt);
  }
  const det=elemento("details"),sum=elemento("summary","Ver comentarios de tu primera lectura"),par=elemento("p",e.inicial.comentarios||"No dejaste comentarios inicialmente.");
  det.append(sum,par,elemento("p","Referencia inicial: "+(e.inicial.evidencia||"no indicada")));fund.append(det);
}
function pintar(){
  const d=D.documentos[indice],e=actual(),f=e.borrador;
  $("numero").textContent="Documento "+(indice+1)+" / "+D.documentos.length;
  // Nombres de archivo, no títulos inferidos: la lista tampoco revela propuestas.
  $("nombre").textContent=d.archivo;$("identidad").textContent=d.id+" · "+(D.etiquetas_cohorte[d.cohorte]||d.cohorte);
  const ruta=D.raiz+"/"+d.ruta;$("ruta").textContent=ruta;
  $("abrir").href="file:///"+ruta.split("/").map(encodeURIComponent).join("/").replace(/^([A-Za-z])%3A\//,"$1:/");
  $("copiar").onclick=async()=>{try{await navigator.clipboard.writeText(ruta);aviso("Ruta copiada. Pegala en el Explorador de archivos.");}catch(err){aviso("No se pudo copiar automáticamente. Seleccioná la ruta visible debajo del botón y copiala.");}};
  $("encabezado-ficha").textContent=e.inicial?"Tu decisión final sobre este documento":"Tu lectura del documento";
  $("indicacion").textContent=e.inicial?"La primera lectura está conservada. Si cambiás algo, se actualiza solo tu decisión final; tendrás que terminar nuevamente la ficha.":"Completá lo que ves en el original. Los campos no se rellenan con la propuesta automática.";
  for(const id of ["decision","emisor","tipo","periodo","evidencia"])$(id).value=f[id]||"";
  $("comentarios").value=f.comentarios||"";$("consultado").checked=!!f.consultado;
  $("antecedente-declarado").checked=!!f.antecedente_declarado;
  $("antecedente-declarado").disabled=!!e.inicial;
  $("periodo-desconocido").checked=!!f.periodo_desconocido;$("periodo").disabled=!!f.periodo_desconocido;
  document.querySelectorAll("input[data-dominio]").forEach(c=>c.checked=f.dominios.includes(c.value));
  $("anterior-importado").hidden=!e.antecedente_v2;
  $("anterior-importado").textContent=e.antecedente_v2?"Recuperamos tu revisión anterior como antecedente. No está marcada como terminada: verificá los campos y el original. Esta nueva lectura NO se etiquetará como independiente de la revisión v2.":"";
  pintarComparacion(d,e);pintarEstado();
  $("anterior").disabled=indice===0;$("siguiente").disabled=indice===D.documentos.length-1;
}
function avanzar(){if(indice<D.documentos.length-1)indice++;pintar();$("nombre").scrollIntoView({block:"start"});}
const vacio=elemento("option","Elegí un tipo…");vacio.value="";$("tipo").append(vacio);
D.vocabulario_tipo.forEach(t=>{const o=elemento("option",nombresTipo[t]||t);o.value=t;$("tipo").append(o);});
D.dominios.concat("ninguno").forEach(t=>{
  const caja=elemento("div",undefined,"domainbox");
  const label=elemento("label",undefined,"domain"),c=elemento("input");c.type="checkbox";c.value=t;c.dataset.dominio=t;
  const span=elemento("span"),descripcion=temas[t]||[t,"",{}];
  span.append(elemento("strong",descripcion[0]),elemento("small",descripcion[1]));
  label.append(c,span);caja.append(label);
  const ayuda=descripcion[2]||{};
  if(ayuda.aviso)caja.append(elemento("p","⚠ "+ayuda.aviso,"aviso-tema"));
  if(ayuda.incluye||ayuda.no_alcanza||ayuda.ejemplo){
    const det=elemento("details");det.append(elemento("summary","Qué incluye / Qué no alcanza / Ejemplo"));
    const dl=elemento("dl");
    [["Qué incluye",ayuda.incluye],["Qué no alcanza",ayuda.no_alcanza],["Ejemplo",ayuda.ejemplo]]
      .forEach(([k,v])=>{if(v){dl.append(elemento("dt",k),elemento("dd",v));}});
    det.append(dl);caja.append(det);
  }
  $("dominios").append(caja);
  c.onchange=()=>{editar("dominios",cambiarDominio(actual().borrador.dominios,t,c.checked));document.querySelectorAll("input[data-dominio]").forEach(x=>x.checked=actual().borrador.dominios.includes(x.value));};
});
$("formulario").onsubmit=e=>e.preventDefault();
for(const id of ["decision","emisor","tipo","periodo","evidencia","comentarios"]){
  $(id).addEventListener(["decision","tipo"].includes(id)?"change":"input",()=>editar(id,$(id).value));
}
$("consultado").onchange=()=>editar("consultado",$("consultado").checked);
/* Solo se puede declarar antes de guardar la primera lectura: despues, el
   antecedente ya quedo registrado en `origen_lectura` y cambiarlo reescribiria
   la historia de esa ficha. */
$("antecedente-declarado").onchange=()=>editar("antecedente_declarado",$("antecedente-declarado").checked);
$("periodo-desconocido").onchange=()=>{
  const marcado=$("periodo-desconocido").checked;
  if(marcado&&$("periodo").value){$("periodo-desconocido").checked=false;aviso("Para declarar período no determinado, primero vaciá el período escrito. No borramos tu dato automáticamente.");return;}
  editar("periodo_desconocido",marcado);$("periodo").disabled=marcado;
};
$("comparar").onclick=()=>{
  const e=actual();try{guardarLectura(e,new Date().toISOString(),D.vocabulario_tipo,D.dominios);asignar(e);guardar();pintar();$("comparacion").scrollIntoView({block:"start"});}catch(err){aviso(err.message);}
};
$("terminar").onclick=()=>{
  const e=actual();try{finalizar(e,new Date().toISOString(),D.vocabulario_tipo,D.dominios);asignar(e);guardar();
    /* Sin persistencia el trabajo sigue en memoria, pero decir "quedaron
       guardados" seria falso: se pierde al cerrar la pestana. */
    aviso("Ficha terminada: "+etiquetas[e.borrador.decision]+(persistencia
      ?". Tu lectura y comentarios quedaron guardados."
      :". ATENCIÓN: sin guardado automático. Tu lectura está solo en memoria y se pierde al cerrar. Descargá el avance."));avanzar();}catch(err){aviso(err.message);}
};
$("anterior").onclick=()=>{if(indice>0){indice--;pintar();}};$("siguiente").onclick=()=>{guardar();avanzar();};
$("buscar").oninput=estadoLista;$("filtro").onchange=estadoLista;
function descargar(){
  const data=JSON.stringify(exportarEstado(D,est,new Date().toISOString()),null,2);
  const url=URL.createObjectURL(new Blob([data],{type:"application/json;charset=utf-8"}));
  const a=elemento("a");a.href=url;a.download="revision_documental_avance_"+new Date().toISOString().replace(/[:.]/g,"-")+".json";
  document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  aviso("Se solicitó la descarga del avance. Comprobá que el JSON esté en Descargas antes de cerrar.");
}
$("exportar").onclick=descargar;$("exportar-abajo").onclick=descargar;
$("importar").onclick=()=>$("archivo-importar").click();
$("archivo-importar").onchange=async()=>{
  const archivo=$("archivo-importar").files[0];if(!archivo)return;
  try{
    if(archivo.size>20*1024*1024)throw new Error("El archivo supera 20 MB. Verificá que sea el JSON de revisión.");
    const paquete=JSON.parse((await archivo.text()).replace(/^\uFEFF/,""));
    const antes=Object.keys(est).length;est=importarEstado(D,paquete,est);guardar();pintar();
    aviso("Avance recuperado: "+(Object.keys(est).length-antes)+" fichas incorporadas. Las fichas que ya habías empezado aquí no se sobrescribieron.");
  }catch(err){aviso("No se importó el archivo: "+err.message);}finally{$("archivo-importar").value="";}
};
$("alcance").textContent=D.alcance.texto;
pintar();
$("guardado").textContent=persistencia?"Descargá un respaldo si trabajaste en otra versión; podés recuperarlo con el botón de arriba.":"El guardado automático no está disponible. Usá la descarga de avance.";
})();
