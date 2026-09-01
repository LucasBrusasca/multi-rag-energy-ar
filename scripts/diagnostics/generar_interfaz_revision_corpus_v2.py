"""Two-stage blind review interface for the candidate corpus.

WHY TWO STAGES. The previous interface showed the automatic proposal next to the
question. That is anchoring: a reviewer who sees `contable, legal` before
deciding will agree with it far more often than one who does not, and the
agreement is then reported as if it validated the proposal. It validates
nothing - it measures the proposal's influence on the reviewer.

So the decision happens twice, and the order is enforced:

  STAGE 1, BLIND. The document, its file, and nothing else. No proposed entity,
  no proposed type, no proposed period, no proposed domains, no evidence. The
  reviewer decides from the document.

  STAGE 2, ADJUDICATION. Only after stage 1 is recorded does the proposal appear,
  with its evidence and confidence. The reviewer may keep the blind answer or
  change it, and BOTH are stored along with which one is final.

Every record therefore says whether the decision was taken before or after
seeing the machine. A corpus whose labels were all set after the reveal is a
corpus that copied the classifier, and this is the only way to know.

WHAT THE FORM ALLOWS. Type comes from a controlled vocabulary, domains are
checkboxes including an explicit `ninguno`, and the period must be `YYYY`,
`nTYYYY` or `YYYY-MM-DD`. Free text produced `31 DE MARZO DE 2026` and
`2T2026` for the same kind of thing; a form that accepts anything guarantees a
catalogue that means nothing.

SCOPE, STATED PLAINLY. This covers 59 documents: 24 active, 24 newly acquired
and 11 in quarantine. It does NOT cover the 150 selected InfoLEG norms.
Finishing these 59 does not make the domain gaps known.

[ES] Interfaz de revision ciega en dos etapas para el corpus candidato.

POR QUE DOS ETAPAS. La interfaz anterior mostraba la propuesta automatica al lado
de la pregunta. Eso es anclaje: un revisor que ve `contable, legal` antes de
decidir va a coincidir mucho mas seguido que uno que no lo ve, y despues esa
coincidencia se reporta como si validara la propuesta. No valida nada: mide la
influencia de la propuesta sobre el revisor.

Asi que la decision ocurre dos veces, y el orden se impone:

  ETAPA 1, A CIEGAS. El documento, su archivo, y nada mas. Sin entidad
  propuesta, sin tipo propuesto, sin periodo propuesto, sin dominios propuestos,
  sin evidencia. El revisor decide desde el documento.

  ETAPA 2, ADJUDICACION. Recien despues de registrada la etapa 1 aparece la
  propuesta, con su evidencia y su confianza. El revisor puede sostener la
  respuesta ciega o cambiarla, y se guardan LAS DOS junto con cual es la final.

Por eso cada registro dice si la decision se tomo antes o despues de ver a la
maquina. Un corpus cuyas etiquetas se fijaron todas despues de revelar es un
corpus que copio al clasificador, y esta es la unica forma de saberlo.

QUE PERMITE EL FORMULARIO. El tipo sale de un vocabulario controlado, los
dominios son casillas con un `ninguno` explicito, y el periodo tiene que ser
`YYYY`, `nTYYYY` o `YYYY-MM-DD`. El texto libre producia `31 DE MARZO DE 2026` y
`2T2026` para la misma clase de cosa; un formulario que acepta cualquier cosa
garantiza un catalogo que no significa nada.

ALCANCE, DICHO SIN VUELTAS. Esto abarca 59 documentos: 24 activos, 24 recien
adquiridos y 11 en cuarentena. NO abarca las 150 normas InfoLEG seleccionadas.
Terminar estos 59 no vuelve conocidas las brechas por dominio.
"""

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

from multirag.paths import DATA_DIR, EXPERIMENTS_DIR, PROJECT_ROOT


RECETA_VERSION = "interfaz-corpus-v2-ciega"

CARACTERIZACION = DATA_DIR / "catalog" / "candidates" / "caracterizacion_fase3v2.jsonl"
CSV_ACTIVOS = EXPERIMENTS_DIR / "revision_catalogo_24" / "revision_catalogo_24_v2.csv"

DOMINIOS = ("legal", "impositivo", "contable", "financiero")
OPCIONES = ("confirmar", "corregir", "dudoso", "excluir")

# Controlled vocabulary. Free text produced `EEFF`, `eeff`, `Estados
# Financieros` and `estado_financiero` for one thing.
# [ES] Vocabulario controlado. El texto libre producia `EEFF`, `eeff`, `Estados
# Financieros` y `estado_financiero` para una sola cosa.
VOCABULARIO_TIPO = (
    "estado_financiero", "memoria_anual", "reporte_resultados",
    "presentacion_inversores", "prospecto", "obligacion_negociable",
    "informe_calificacion", "reporte_sostenibilidad", "ley", "decreto",
    "resolucion", "resolucion_general", "disposicion", "texto_ordenado",
    "procedimiento_regulatorio", "terminos_y_condiciones", "codigo_de_etica",
    "no_determinado",
)


def huella(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def cargar_activos() -> list:
    with CSV_ACTIVOS.open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f))
    return [
        {
            "id": f["document_id"],
            "cohorte": "activo",
            "archivo": f["archivo_referencia"],
            "ruta": f"data/raw/{f['archivo_referencia']}",
            "titulo": f["titulo_oficial"] or f["fuente"],
            "paginas": f["paginas"],
            "propuesta": {
                "emisor": f"{f['emisor_nombre']} ({f['emisor_id']})",
                "confianza_emisor": "catalogo_curado",
                "tipo": f["tipo_documento"],
                "periodo": f["fecha_documento"],
                "confianza_periodo": "catalogo_curado",
                "dominios": [d.strip() for d in f["dominios_documentales"].split("|") if d.strip()],
                "evidencia": [],
                "avisos": [],
            },
        }
        for f in filas
    ]


def cargar_caracterizados() -> list:
    registros = [json.loads(l) for l in CARACTERIZACION.open(encoding="utf-8")]
    por_sha = collections.defaultdict(list)
    for r in registros:
        por_sha[r["sha256"]].append(r)

    salida = []
    for grupo in por_sha.values():
        r = sorted(grupo, key=lambda x: x["archivo"])[0]
        avisos = []
        if len(grupo) > 1:
            otros = ", ".join(g["archivo"] for g in grupo if g is not r)
            avisos.append(f"Duplicado binario exacto de: {otros}.")
        if r.get("fuentes_discrepan"):
            avisos.append("Las fuentes del período no coinciden entre sí.")
        if r.get("discrepa_con_url"):
            avisos.append(
                f"El período no coincide con el año del directorio de la URL "
                f"({r.get('anio_en_url')}), que es la fecha de PUBLICACIÓN."
            )
        if r.get("marcas_no_pertinente"):
            avisos.append("Posible no pertinente: " + ", ".join(r["marcas_no_pertinente"]))
        if r.get("confianza_entidad") in ("baja", "sin_entidad"):
            avisos.append("La entidad se dedujo del texto y es poco confiable.")

        evidencia = []
        for dominio, datos in (r.get("dominios") or {}).items():
            for e in (datos.get("evidencia") or [])[:2]:
                evidencia.append({
                    "dominio": dominio, "propuesto": datos["propuesto"],
                    "terminos": datos.get("terminos_distintos"),
                    "ocurrencias": datos.get("ocurrencias_totales"),
                    "paginas_termino": datos.get("max_paginas_de_un_termino"),
                    "motivo": datos.get("motivo_no_propuesto"),
                    "termino": e.get("termino"), "pagina": e.get("pagina"),
                    "cita": (e.get("cita") or "")[:280],
                })

        salida.append({
            "id": r["archivo"],
            "cohorte": "empresarial_nuevo" if r["zona"] == "incoming_candidates" else "cuarentena",
            "archivo": r["archivo"],
            "ruta": r["ruta"],
            "titulo": r.get("titulo") or r["archivo"],
            "paginas": r.get("paginas"),
            "formato": r.get("formato", "pdf"),
            "hojas": [h["hoja"] for h in (r.get("hojas") or [])],
            "unidades": r.get("unidades_detectadas", []),
            "celdas": (r.get("celdas_muestra") or [])[:6],
            "propuesta": {
                "emisor": r.get("entidad_propuesta") or "(no determinado)",
                "confianza_emisor": r.get("confianza_entidad", "?"),
                "tipo": r.get("tipo_propuesto") or "no_determinado",
                "tipo_fuente": r.get("tipo_fuente"),
                "periodo": r.get("periodo_propuesto") or "(no determinado)",
                "confianza_periodo": r.get("confianza", "?"),
                "periodo_candidatos": r.get("candidatos", []),
                "dominios": r.get("dominios_propuestos", []),
                "evidencia": evidencia,
                "avisos": avisos,
            },
        })
    return salida


PLANTILLA = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revisión ciega del corpus candidato</title>
<style>
:root{--tinta:#1c1c1e;--suave:#5b5f66;--linea:#dfe3e8;--fondo:#f5f6f8;--panel:#fff;
--acento:#2f5597;--ok:#1e7a46;--corr:#8a5a00;--duda:#7a4fb5;--excl:#a32020;
--aviso:#fff4e5;--avisoL:#e0a458;--ciego:#eef4ff;--ciegoL:#9db6e0}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--tinta);
font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{background:var(--panel);border-bottom:1px solid var(--linea);padding:12px 22px;
position:sticky;top:0;z-index:10}
.titulo{font-weight:650}.sub{color:var(--suave);font-size:13px}
.barra{height:8px;background:var(--linea);border-radius:99px;margin-top:10px;overflow:hidden}
.barra>div{height:100%;background:var(--acento);width:0}
.cont{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;font-size:13px}
main{max-width:1020px;margin:20px auto;padding:0 18px}
.ficha{background:var(--panel);border:1px solid var(--linea);border-radius:12px;padding:22px}
h1{font-size:20px;margin:0 0 2px}
.mono{font-family:ui-monospace,Consolas,monospace;font-size:12.5px;color:var(--suave)}
.chip{display:inline-block;border-radius:99px;padding:2px 10px;font-size:12px;
border:1px solid var(--linea);background:#eef2f8;color:var(--acento)}
.etapa{border:2px solid var(--ciegoL);background:var(--ciego);border-radius:10px;
padding:14px;margin:14px 0}
.etapa h2{font-size:14px;margin:0 0 4px;text-transform:uppercase;letter-spacing:.05em}
dl{display:grid;grid-template-columns:170px 1fr;gap:7px 16px;margin:14px 0}
dt{color:var(--suave);font-size:13px}dd{margin:0}
.aviso{background:var(--aviso);border:1px solid var(--avisoL);border-radius:8px;
padding:10px 13px;margin:8px 0;font-size:13.5px}
.ev{background:#fafbfc;border:1px solid var(--linea);border-radius:8px;padding:11px 13px;
margin:8px 0;font-size:13px}
.ev .rot{color:var(--suave);font-size:11.5px;text-transform:uppercase;margin-bottom:5px}
button{font:inherit;border:1px solid var(--linea);background:var(--panel);color:var(--tinta);
border-radius:8px;padding:9px 16px;cursor:pointer}
button:hover{border-color:var(--suave)}button:disabled{opacity:.45;cursor:not-allowed}
button.sel[data-d=confirmar]{background:var(--ok);border-color:var(--ok);color:#fff}
button.sel[data-d=corregir]{background:var(--corr);border-color:var(--corr);color:#fff}
button.sel[data-d=dudoso]{background:var(--duda);border-color:var(--duda);color:#fff}
button.sel[data-d=excluir]{background:var(--excl);border-color:var(--excl);color:#fff}
.acc{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 4px}
.campo{margin-bottom:11px}
.campo>span{display:block;color:var(--suave);font-size:12.5px;margin-bottom:3px}
input[type=text],select,textarea{width:100%;font:inherit;padding:8px 10px;
border:1px solid var(--linea);border-radius:6px;background:#fff}
textarea{min-height:66px}
input.malo{border-color:var(--excl);background:#fff6f6}
.chks{display:flex;gap:14px;flex-wrap:wrap}
.chks label{display:flex;gap:6px;align-items:center;font-size:14px;color:var(--tinta)}
.err{color:var(--excl);font-size:13px;margin-top:9px;min-height:18px}
.nav{display:flex;gap:10px;justify-content:space-between;margin-top:16px;flex-wrap:wrap}
.pie{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px;padding-top:16px;
border-top:1px solid var(--linea)}
.peligro{border-color:var(--excl);color:var(--excl)}
.oculto{display:none}
.alcance{background:#fff;border:1px solid var(--linea);border-left:4px solid var(--acento);
border-radius:8px;padding:12px 14px;margin-bottom:16px;font-size:13.5px}
</style></head><body>
<header>
<div class="titulo">Revisión ciega del corpus candidato</div>
<div class="sub" id="sub"></div>
<div class="barra"><div id="prog"></div></div>
<div class="cont">
<span>a ciegas <b id="c-ciego">0</b></span>
<span>adjudicados <b id="c-adj">0</b></span>
<span>· pendientes <b id="c-pend">0</b></span>
<span id="c-cambios"></span>
</div></header>
<main>
<div class="alcance" id="alcance"></div>
<div id="persist" class="aviso oculto"></div>
<section class="ficha">
<div class="mono" id="pos"></div>
<h1 id="titulo"></h1>
<div class="mono" id="ident"></div>
<div><span class="chip" id="cohorte"></span> <span class="chip" id="etapachip"></span></div>
<dl>
<dt>Archivo</dt><dd id="archivo"></dd>
<dt>Extensión</dt><dd id="paginas"></dd>
</dl>
<div class="acc"><button type="button" id="abrir">📄 Abrir documento</button></div>
<div class="mono" id="rutaabs"></div>

<div class="etapa" id="etapa1">
<h2>Etapa 1 — decisión a ciegas</h2>
<div class="sub" id="ayuda1"></div>
<div class="acc" id="acc1"></div>
<div id="form1"></div>
</div>

<div class="etapa oculto" id="etapa2" style="border-color:var(--avisoL);background:var(--aviso)">
<h2>Etapa 2 — propuesta automática y adjudicación</h2>
<div id="propuesta"></div>
<div id="evidencia"></div>
<div class="acc" id="acc2"></div>
<div id="form2"></div>
</div>

<div class="campo" style="margin-top:12px"><span id="rotobs">Observaciones</span>
<textarea id="obs"></textarea></div>
<div class="err" id="err"></div>
<div class="nav">
<div style="display:flex;gap:10px">
<button type="button" id="ant">← Anterior</button>
<button type="button" id="sig">Siguiente →</button>
<button type="button" id="revelar">Ver propuesta automática ▸</button></div>
<select id="salto" style="max-width:420px"></select></div>
</section>
<div class="pie">
<button type="button" id="csv" disabled>Descargar CSV</button>
<button type="button" id="json" disabled>Descargar JSON</button>
<button type="button" id="borrador">Descargar borrador</button>
<button type="button" id="borrar" class="peligro">Borrar decisiones</button>
</div>
<p class="sub" style="margin-top:12px">Todo se guarda solo en este navegador. Nada se
envía a internet y nada se aplica al catálogo.</p>
</main>
<script type="application/json" id="datos">__DATOS__</script>
<script>
/* === INICIO LOGICA PURA === */
function limpio(v){return (v===undefined||v===null)?"":String(v).trim();}

/* Period must be one of three shapes. Free text produced `31 DE MARZO DE 2026`
   and `2T2026` for the same kind of thing, and a catalogue where the same period
   is written three ways cannot be deduplicated or grouped.
   [ES] El periodo tiene que ser una de tres formas. El texto libre producia
   `31 DE MARZO DE 2026` y `2T2026` para la misma clase de cosa, y un catalogo
   donde el mismo periodo se escribe de tres formas no se puede deduplicar ni
   agrupar. */
function periodoValido(v){
  const s=limpio(v);
  if(s==="") return true;
  return /^(20\d{2}|[1-4]T20\d{2}|20\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$/.test(s);
}

function dominiosValidos(sel,vocab){
  const s=(sel||[]).filter(function(d){return d!=="ninguno";});
  if((sel||[]).indexOf("ninguno")>=0) return s.length===0;
  return s.every(function(d){return vocab.indexOf(d)>=0;});
}

function tipoValido(t,vocab){
  const s=limpio(t);
  return s==="" || vocab.indexOf(s)>=0;
}

function validarEtapa(doc,e,vocabTipo,vocabDom){
  const d=limpio(e.decision);
  if(d==="") return {ok:false,motivo:"Sin decisión."};
  if(d==="dudoso"&&limpio(e.observaciones)==="")
    return {ok:false,motivo:"«Dudoso» exige explicar la duda."};
  if(d==="excluir"&&limpio(e.observaciones)==="")
    return {ok:false,motivo:"«Excluir» exige justificar el motivo."};
  if(d==="corregir"){
    if(!tipoValido(e.tipo,vocabTipo))
      return {ok:false,motivo:"El tipo debe salir del vocabulario controlado."};
    if(!periodoValido(e.periodo))
      return {ok:false,motivo:"El período debe ser YYYY, nTYYYY o YYYY-MM-DD."};
    if(!dominiosValidos(e.dominios,vocabDom))
      return {ok:false,motivo:"Dominios inválidos: marcá «ninguno» o dominios reales."};
    const algo=limpio(e.emisor)||limpio(e.tipo)||limpio(e.periodo)||
      (e.dominios&&e.dominios.length>0);
    if(!algo) return {ok:false,motivo:"«Corregir» exige completar al menos un campo."};
  }
  return {ok:true,motivo:""};
}

/* A record is complete when the blind stage is valid AND the adjudication stage
   is valid. Stage two may simply repeat stage one; what matters is that it was
   made after seeing the proposal, and that fact is what gets stored.
   [ES] Un registro esta completo cuando la etapa ciega es valida Y la de
   adjudicacion tambien. La etapa dos puede repetir la uno; lo que importa es que
   se tomo despues de ver la propuesta, y ese hecho es lo que se guarda. */
function estadoDoc(doc,est,vocabTipo,vocabDom){
  const e=est[doc.id]||{};
  const c=validarEtapa(doc,e.ciega||{},vocabTipo,vocabDom);
  const a=validarEtapa(doc,e.adjudicada||{},vocabTipo,vocabDom);
  if(!c.ok) return {fase:"pendiente",motivo:c.motivo};
  if(!a.ok) return {fase:"ciega",motivo:a.motivo};
  return {fase:"adjudicada",motivo:""};
}

function contar(docs,est,vocabTipo,vocabDom){
  const c={pendiente:0,ciega:0,adjudicada:0,cambio_tras_revelar:0};
  for(const d of docs){
    const s=estadoDoc(d,est,vocabTipo,vocabDom);
    c[s.fase]+=1;
    if(s.fase==="adjudicada"){
      const e=est[d.id];
      if(JSON.stringify(e.ciega)!==JSON.stringify(e.adjudicada)) c.cambio_tras_revelar+=1;
    }
  }
  return c;
}

function celda(v){
  const s=(v===undefined||v===null)?"":String(v);
  return /[",\n\r]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;
}

function armarCsv(docs,est,vocabTipo,vocabDom){
  const cols=["id","cohorte","archivo","ruta","paginas",
    "decision_ciega","emisor_ciego","tipo_ciego","periodo_ciego","dominios_ciegos",
    "decision_final","emisor_final","tipo_final","periodo_final","dominios_finales",
    "cambio_tras_revelar","observaciones","propuesta_emisor","propuesta_tipo",
    "propuesta_periodo","propuesta_dominios"];
  const l=[cols.join(",")];
  for(const d of docs){
    const e=est[d.id]||{}; const c=e.ciega||{}; const a=e.adjudicada||{};
    const cambio=(JSON.stringify(e.ciega||{})!==JSON.stringify(e.adjudicada||{}));
    l.push([d.id,d.cohorte,d.archivo,d.ruta,d.paginas,
      limpio(c.decision),limpio(c.emisor),limpio(c.tipo),limpio(c.periodo),
      (c.dominios||[]).join("|"),
      limpio(a.decision),limpio(a.emisor),limpio(a.tipo),limpio(a.periodo),
      (a.dominios||[]).join("|"),
      cambio?"si":"no", limpio(e.observaciones),
      d.propuesta.emisor,d.propuesta.tipo,d.propuesta.periodo,
      (d.propuesta.dominios||[]).join("|")
    ].map(celda).join(","));
  }
  return l.join("\n")+"\n";
}

function armarJson(meta,docs,est,vocabTipo,vocabDom){
  return {
    receta:meta.receta, alcance:meta.alcance, huella_fuentes:meta.huella_fuentes,
    fecha_exportacion:meta.fecha_exportacion, documentos:docs.length,
    conteos:contar(docs,est,vocabTipo,vocabDom),
    decisiones:docs.map(function(d){
      const e=est[d.id]||{};
      const s=estadoDoc(d,est,vocabTipo,vocabDom);
      return {id:d.id, cohorte:d.cohorte, fase:s.fase,
        ciega:e.ciega||{}, adjudicada:e.adjudicada||{},
        cambio_tras_revelar:(JSON.stringify(e.ciega||{})!==JSON.stringify(e.adjudicada||{})),
        observaciones:limpio(e.observaciones), propuesta:d.propuesta};
    }),
    salvedades:meta.salvedades
  };
}
/* === FIN LOGICA PURA === */

(function(){
"use strict";
const D=JSON.parse(document.getElementById("datos").textContent);
const VT=D.vocabulario_tipo, VD=D.dominios;
const CLAVE="revision_corpus_v2::"+D.huella_fuentes.slice(0,20);
let i=0, est={}, persiste=true, revelado={};
try{localStorage.setItem(CLAVE+"::p","1");localStorage.removeItem(CLAVE+"::p");}
catch(e){persiste=false;}
if(persiste){try{est=JSON.parse(localStorage.getItem(CLAVE)||"{}");}catch(e){est={};}}
function guardar(){if(persiste){try{localStorage.setItem(CLAVE,JSON.stringify(est));}
catch(e){persiste=false;avisarP();}}}
function avisarP(){const c=document.getElementById("persist");
if(persiste){c.classList.add("oculto");return;}
c.classList.remove("oculto");
c.textContent="⚠ Este navegador no permite guardado automático acá. Usá «Descargar borrador» seguido.";}
function E(d){if(!est[d.id])est[d.id]={ciega:{},adjudicada:{},observaciones:""};
if(!est[d.id].ciega)est[d.id].ciega={};if(!est[d.id].adjudicada)est[d.id].adjudicada={};
return est[d.id];}
function vaciar(n){while(n.firstChild)n.removeChild(n.firstChild);}
function txt(id,v){document.getElementById(id).textContent=
(v===null||v===undefined||v==="")?"—":String(v);}

function campoTexto(cont,etiqueta,valor,alCambiar,validador){
  const w=document.createElement("div");w.className="campo";
  const s=document.createElement("span");s.textContent=etiqueta;
  const inp=document.createElement("input");inp.type="text";inp.value=valor||"";
  inp.addEventListener("input",function(){
    if(validador&&!validador(inp.value))inp.classList.add("malo");
    else inp.classList.remove("malo");
    alCambiar(inp.value);});
  if(validador&&!validador(inp.value))inp.classList.add("malo");
  w.appendChild(s);w.appendChild(inp);cont.appendChild(w);
}

function campoSelect(cont,etiqueta,valor,opciones,alCambiar){
  const w=document.createElement("div");w.className="campo";
  const s=document.createElement("span");s.textContent=etiqueta;
  const sel=document.createElement("select");
  const vacia=document.createElement("option");vacia.value="";
  vacia.textContent="(sin cambio)";sel.appendChild(vacia);
  for(const o of opciones){const op=document.createElement("option");
  op.value=o;op.textContent=o;if(o===valor)op.selected=true;sel.appendChild(op);}
  sel.value=valor||"";
  sel.addEventListener("change",function(){alCambiar(sel.value);});
  w.appendChild(s);w.appendChild(sel);cont.appendChild(w);
}

function campoDominios(cont,valor,alCambiar){
  const w=document.createElement("div");w.className="campo";
  const s=document.createElement("span");
  s.textContent="dominios (marcá «ninguno» si el documento no aporta a ninguno)";
  const caja=document.createElement("div");caja.className="chks";
  const actuales=new Set(valor||[]);
  for(const d of VD.concat(["ninguno"])){
    const l=document.createElement("label");
    const c=document.createElement("input");c.type="checkbox";c.value=d;
    c.checked=actuales.has(d);
    c.addEventListener("change",function(){
      if(d==="ninguno"&&c.checked){actuales.clear();actuales.add("ninguno");}
      else if(c.checked){actuales.delete("ninguno");actuales.add(d);}
      else actuales.delete(d);
      alCambiar(Array.from(actuales));pintar();});
    const t=document.createElement("span");t.textContent=d;
    l.appendChild(c);l.appendChild(t);caja.appendChild(l);}
  w.appendChild(s);w.appendChild(caja);cont.appendChild(w);
}

function pintarFormulario(cont,e,alGuardar){
  vaciar(cont);
  if(limpio(e.decision)!=="corregir")return;
  campoTexto(cont,"emisor",e.emisor,function(v){e.emisor=v;alGuardar();});
  campoSelect(cont,"tipo (vocabulario controlado)",e.tipo,VT,
    function(v){e.tipo=v;alGuardar();});
  campoTexto(cont,"período (YYYY · nTYYYY · YYYY-MM-DD)",e.periodo,
    function(v){e.periodo=v;alGuardar();},periodoValido);
  campoDominios(cont,e.dominios,function(v){e.dominios=v;alGuardar();});
}

function pintarAcciones(cont,e,alGuardar){
  vaciar(cont);
  for(const op of OPCIONES_L){
    const b=document.createElement("button");b.type="button";b.dataset.d=op;
    b.textContent=D.etiquetas[op];
    if(e.decision===op)b.className="sel";
    b.addEventListener("click",function(){e.decision=op;alGuardar();pintar();});
    cont.appendChild(b);}
}
const OPCIONES_L=D.opciones;

function pintarPropuesta(d){
  const c=document.getElementById("propuesta");vaciar(c);
  const dl=document.createElement("dl");
  const filas=[["emisor",d.propuesta.emisor+"  ·  confianza: "+d.propuesta.confianza_emisor],
   ["tipo",d.propuesta.tipo],
   ["período",d.propuesta.periodo+"  ·  confianza: "+d.propuesta.confianza_periodo],
   ["dominios",(d.propuesta.dominios||[]).join(", ")||"(ninguno propuesto)"]];
  for(const [k,v] of filas){
    const dt=document.createElement("dt");dt.textContent=k;
    const dd=document.createElement("dd");dd.textContent=v;
    dl.appendChild(dt);dl.appendChild(dd);}
  c.appendChild(dl);
  for(const a of (d.propuesta.avisos||[])){
    const x=document.createElement("div");x.className="aviso";x.textContent="⚠ "+a;
    c.appendChild(x);}
  const ev=document.getElementById("evidencia");vaciar(ev);
  for(const e of (d.propuesta.evidencia||[])){
    const b=document.createElement("div");b.className="ev";
    const r=document.createElement("div");r.className="rot";
    r.textContent=(e.propuesto?"✓ ":"· ")+e.dominio+" — "+e.terminos+" términos, "+
      e.ocurrencias+" menciones, hasta "+e.paginas_termino+" páginas"+
      (e.motivo?"  ("+e.motivo+")":"")+"  — «"+e.termino+"» p."+e.pagina;
    const t=document.createElement("div");t.textContent="…"+e.cita+"…";
    b.appendChild(r);b.appendChild(t);ev.appendChild(b);}
}

function pintar(){
const d=D.documentos[i];const e=E(d);
txt("pos","Documento "+(i+1)+" de "+D.documentos.length);
txt("titulo",d.titulo);txt("ident",d.id);
txt("cohorte",D.etiquetas_cohorte[d.cohorte]||d.cohorte);
txt("archivo",d.ruta);
txt("paginas",(d.formato||"pdf")+(d.paginas?("  ·  "+d.paginas+
  ((d.formato==="xlsx")?" hojas":" páginas")):""));
document.getElementById("rutaabs").textContent="ruta local: "+D.raiz+"/"+d.ruta;

const estado=estadoDoc(d,est,VT,VD);
txt("etapachip",{pendiente:"etapa 1 — a ciegas",ciega:"etapa 2 — adjudicar",
  adjudicada:"completo"}[estado.fase]);

document.getElementById("ayuda1").textContent=
"Abrí el documento y decidí SIN ver la propuesta automática. Recién después "+
"vas a poder revelarla y adjudicar.";
/* Typing in a field has to refresh the error line and the reveal button too.
   Without it the form validated on the next repaint only, so a period the user
   had just corrected still showed the old error and `Ver propuesta` stayed
   disabled - the reviewer would have concluded the form was broken.
   [ES] Escribir en un campo tiene que refrescar tambien la linea de error y el
   boton de revelar. Sin eso el formulario validaba recien en el siguiente
   repintado, asi que un periodo recien corregido seguia mostrando el error viejo
   y `Ver propuesta` quedaba deshabilitado: el revisor habria concluido que el
   formulario estaba roto. */
function refrescar(){guardar();cab();val();refrescarRevelar();}

pintarAcciones(document.getElementById("acc1"),e.ciega,function(){guardar();});
pintarFormulario(document.getElementById("form1"),e.ciega,refrescar);

function refrescarRevelar(){
  const ok=validarEtapa(d,E(d).ciega,VT,VD).ok;
  document.getElementById("revelar").disabled=!ok||!!revelado[d.id];
}

const ciegaOk=validarEtapa(d,e.ciega,VT,VD).ok;
const mostrar=ciegaOk&&revelado[d.id];
refrescarRevelar();
document.getElementById("etapa2").classList.toggle("oculto",!mostrar);
if(mostrar){
  pintarPropuesta(d);
  pintarAcciones(document.getElementById("acc2"),e.adjudicada,function(){guardar();});
  pintarFormulario(document.getElementById("form2"),e.adjudicada,refrescar);
}

const ta=document.getElementById("obs");ta.value=e.observaciones||"";
ta.oninput=function(){e.observaciones=ta.value;guardar();cab();val();};
document.getElementById("abrir").onclick=function(){
  window.open("file:///"+D.raiz+"/"+d.ruta,"_blank");};

val();
document.getElementById("ant").disabled=(i===0);
document.getElementById("sig").disabled=(i===D.documentos.length-1);
cab();window.scrollTo(0,0);
}

function val(){const d=D.documentos[i];const s=estadoDoc(d,est,VT,VD);
document.getElementById("err").textContent=s.motivo||"";return s;}

function cab(){
const c=contar(D.documentos,est,VT,VD);
document.getElementById("c-ciego").textContent=String(c.ciega);
document.getElementById("c-adj").textContent=String(c.adjudicada);
document.getElementById("c-pend").textContent=String(c.pendiente);
document.getElementById("c-cambios").textContent=
"cambiaron tras revelar: "+c.cambio_tras_revelar;
document.getElementById("prog").style.width=
(c.adjudicada/D.documentos.length*100).toFixed(1)+"%";
document.getElementById("sub").textContent=c.adjudicada+" de "+D.documentos.length+
" adjudicados";
document.getElementById("csv").disabled=(c.adjudicada<D.documentos.length);
document.getElementById("json").disabled=(c.adjudicada<D.documentos.length);
const sel=document.getElementById("salto");vaciar(sel);
D.documentos.forEach(function(d,k){
const s=estadoDoc(d,est,VT,VD);
const o=document.createElement("option");o.value=String(k);
o.textContent={pendiente:"·",ciega:"◐",adjudicada:"✓"}[s.fase]+"  "+(k+1)+"  ["+
D.etiquetas_cohorte[d.cohorte]+"]  "+d.id.slice(0,44);
if(k===i)o.selected=true;sel.appendChild(o);});
sel.onchange=function(){i=parseInt(sel.value,10);pintar();};
}

function bajar(n,c,t){const b=new Blob([c],{type:t});const u=URL.createObjectURL(b);
const a=document.createElement("a");a.href=u;a.download=n;document.body.appendChild(a);
a.click();document.body.removeChild(a);URL.revokeObjectURL(u);}
function meta(){return{receta:D.receta,alcance:D.alcance,huella_fuentes:D.huella_fuentes,
fecha_exportacion:new Date().toISOString(),salvedades:D.salvedades};}

document.getElementById("ant").onclick=function(){if(i>0){i--;pintar();}};
document.getElementById("sig").onclick=function(){if(i<D.documentos.length-1){i++;pintar();}};
document.getElementById("revelar").onclick=function(){
const d=D.documentos[i];
if(!validarEtapa(d,E(d).ciega,VT,VD).ok)return;
revelado[d.id]=true;
const e=E(d);
if(!e.adjudicada||!e.adjudicada.decision)
  e.adjudicada=JSON.parse(JSON.stringify(e.ciega));
guardar();pintar();};
document.getElementById("csv").onclick=function(){
bajar("revision_corpus_v2_decisiones.csv","﻿"+armarCsv(D.documentos,est,VT,VD),
"text/csv;charset=utf-8");};
document.getElementById("json").onclick=function(){
bajar("revision_corpus_v2_decisiones.json",
JSON.stringify(armarJson(meta(),D.documentos,est,VT,VD),null,2),
"application/json;charset=utf-8");};
document.getElementById("borrador").onclick=function(){
bajar("revision_corpus_v2_borrador.json",
JSON.stringify(armarJson(meta(),D.documentos,est,VT,VD),null,2),
"application/json;charset=utf-8");};
document.getElementById("borrar").onclick=function(){
if(!window.confirm("¿Borrar TODAS las decisiones?"))return;
if(!window.confirm("Confirmá otra vez."))return;
est={};revelado={};try{localStorage.removeItem(CLAVE);}catch(e){}i=0;pintar();};

document.getElementById("alcance").textContent=D.alcance.texto;
avisarP();pintar();
})();
</script></body></html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--salida", type=Path,
        default=EXPERIMENTS_DIR / "revision_corpus" / "revision_corpus_v2.html",
    )
    args = parser.parse_args()

    documentos = cargar_activos() + cargar_caracterizados()

    fuentes = hashlib.sha256()
    for ruta in (CARACTERIZACION, CSV_ACTIVOS):
        if ruta.exists():
            fuentes.update(huella(ruta).encode())

    por_cohorte = collections.Counter(d["cohorte"] for d in documentos)

    datos = {
        "receta": RECETA_VERSION,
        "huella_fuentes": fuentes.hexdigest(),
        "raiz": str(PROJECT_ROOT).replace("\\", "/"),
        "documentos": documentos,
        "opciones": list(OPCIONES),
        "etiquetas": {"confirmar": "✓ Confirmar", "corregir": "✎ Corregir",
                      "dudoso": "? Dudoso", "excluir": "✕ Excluir"},
        "etiquetas_cohorte": {
            "activo": f"activo ({por_cohorte['activo']})",
            "empresarial_nuevo": f"nuevo ({por_cohorte['empresarial_nuevo']})",
            "cuarentena": f"cuarentena ({por_cohorte['cuarentena']})",
        },
        "dominios": list(DOMINIOS),
        "vocabulario_tipo": list(VOCABULARIO_TIPO),
        "alcance": {
            "documentos": len(documentos),
            "activos": por_cohorte["activo"],
            "empresariales_nuevos": por_cohorte["empresarial_nuevo"],
            "cuarentena": por_cohorte["cuarentena"],
            "infoleg_no_incluidos": 150,
            "texto": (
                f"ALCANCE: estos {len(documentos)} documentos son "
                f"{por_cohorte['activo']} activos, {por_cohorte['empresarial_nuevo']} "
                f"empresariales nuevos y {por_cohorte['cuarentena']} de cuarentena. "
                f"NO incluyen las 150 normas InfoLEG seleccionadas, que necesitan su "
                f"propia auditoría estratificada. Terminar estos "
                f"{len(documentos)} NO vuelve conocidas las brechas por dominio."
            ),
        },
        "salvedades": [
            "Revision en DOS ETAPAS: la decision ciega se toma antes de ver la "
            "propuesta automatica, y se guardan las dos.",
            "El campo `cambio_tras_revelar` dice si el revisor cambio de opinion al "
            "ver la maquina. Sin ese dato no se puede saber si el corpus la copio.",
            "Tipo desde vocabulario controlado; periodo validado como YYYY, nTYYYY o "
            "YYYY-MM-DD; dominios por casillas, con `ninguno` explicito.",
            "NO abarca las 150 normas InfoLEG. Terminar los 59 no vuelve conocidas "
            "las brechas.",
            "Nada se aplica al catalogo ni a PostgreSQL.",
        ],
    }

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(
        PLANTILLA.replace(
            "__DATOS__", json.dumps(datos, ensure_ascii=False).replace("<", "\\u003c")
        ),
        encoding="utf-8",
    )

    print(f"documentos  {len(documentos)}")
    for k, v in por_cohorte.most_common():
        print(f"  {k:20} {v}")
    print(f"  {'infoleg NO incluidos':20} 150")
    print(f"\nhtml  {args.salida}  ({args.salida.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
