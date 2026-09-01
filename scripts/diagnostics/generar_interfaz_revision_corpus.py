"""Offline HTML interface to review the whole candidate corpus, in one place.

WHAT IT COVERS. The 24 active documents, the 24 newly acquired corporate ones,
and the 11 unique documents sitting in quarantine: 59 records, one screen each.
Reviewing them in three separate instruments would make the one comparison that
matters - is this new document the same as that active one? - the hardest to
make.

WHAT IS PROPOSED AND WHAT IS NOT. Entity, type, period and candidate domains are
PROPOSALS, each shown with the evidence that produced it and a confidence label.
Corrections are four independent fields; an empty one keeps the current value.
Nothing is applied to the catalogue.

TEXT ONLY, NEVER innerHTML. Titles, excerpts and quoted evidence come from real
documents, and a document is untrusted input.

[ES] Interfaz HTML offline para revisar todo el corpus candidato, en un solo
lugar.

QUE ABARCA. Los 24 documentos activos, los 24 empresariales recien adquiridos, y
los 11 documentos unicos que estan en cuarentena: 59 registros, una pantalla cada
uno. Revisarlos en tres instrumentos separados volveria la unica comparacion que
importa -es este documento nuevo el mismo que aquel activo?- la mas dificil de
hacer.

QUE SE PROPONE Y QUE NO. Entidad, tipo, periodo y dominios candidatos son
PROPUESTAS, cada una mostrada con la evidencia que la produjo y una etiqueta de
confianza. Las correcciones son cuatro campos independientes; uno vacio conserva
el valor actual. Nada se aplica al catalogo.

SOLO TEXTO, NUNCA innerHTML. Titulos, extractos y citas de evidencia vienen de
documentos reales, y un documento es entrada no confiable.
"""

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

from multirag.paths import DATA_DIR, EXPERIMENTS_DIR, PROJECT_ROOT


RECETA_VERSION = "interfaz-corpus-v1"

CARACTERIZACION = DATA_DIR / "catalog" / "candidates" / "caracterizacion_fase3v2.jsonl"
CSV_ACTIVOS = EXPERIMENTS_DIR / "revision_catalogo_24" / "revision_catalogo_24_v2.csv"
CUARENTENA = DATA_DIR / "quarantine" / "descartados"

DOMINIOS = ("legal", "impositivo", "contable", "financiero")
OPCIONES = ("confirmar", "corregir", "dudoso", "excluir")
CAMPOS = ("emisor_corregido", "tipo_corregido", "periodo_corregido", "dominios_corregidos")


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
            "emisor_propuesto": f"{f['emisor_nombre']} ({f['emisor_id']})",
            "confianza_entidad": "catalogo_curado",
            "tipo_propuesto": f["tipo_documento"],
            "periodo_propuesto": f["fecha_documento"],
            "confianza_periodo": "catalogo_curado",
            "dominios_propuestos": [
                d.strip() for d in f["dominios_documentales"].split("|") if d.strip()
            ],
            "paginas": f["paginas"],
            "evidencia_extracto": f["evidencia_extracto"],
            "evidencia_dominios": [],
            "url_origen": f["url_origen"],
            "avisos": [],
            "recomendacion": "revisar",
        }
        for f in filas
    ]


def cargar_caracterizados() -> list:
    registros = [json.loads(l) for l in CARACTERIZACION.open(encoding="utf-8")]

    # Collapse the binary duplicate pair into one record and say so, instead of
    # asking the reviewer to judge the same bytes twice.
    # [ES] Colapsar el par de duplicado binario en un registro y decirlo, en
    # lugar de pedirle al revisor que juzgue los mismos bytes dos veces.
    por_sha = collections.defaultdict(list)
    for r in registros:
        por_sha[r["sha256"]].append(r)

    salida = []
    for sha, grupo in por_sha.items():
        r = sorted(grupo, key=lambda x: x["archivo"])[0]
        avisos = []
        if len(grupo) > 1:
            otros = ", ".join(g["archivo"] for g in grupo if g is not r)
            avisos.append(f"Duplicado binario exacto de: {otros}. Se muestra una sola vez.")
        if r.get("fuentes_discrepan"):
            avisos.append("Las fuentes del período no coinciden entre sí.")
        if r.get("discrepa_con_url"):
            avisos.append(
                f"El período propuesto no coincide con el año del directorio de la URL "
                f"({r.get('anio_en_url')}). El directorio es la fecha de PUBLICACIÓN, "
                f"no la del período."
            )
        if r.get("marcas_no_pertinente"):
            avisos.append(
                "Marcado como posible no pertinente: "
                + ", ".join(r["marcas_no_pertinente"])
            )
        if r.get("confianza_entidad") in ("baja", "sin_entidad"):
            avisos.append("La entidad se dedujo del texto y es poco confiable.")

        evidencias = []
        for dominio, datos in r.get("dominios", {}).items():
            for e in datos.get("evidencia", [])[:2]:
                evidencias.append(
                    {
                        "dominio": dominio,
                        "propuesto": datos["propuesto"],
                        "terminos": datos["terminos_distintos"],
                        "pagina": e.get("pagina"),
                        "cita": e.get("cita", "")[:280],
                        "termino": e.get("termino"),
                    }
                )

        salida.append(
            {
                "id": r["archivo"],
                "cohorte": "empresarial_nuevo" if r["zona"] == "incoming_candidates"
                else "cuarentena",
                "archivo": r["archivo"],
                "ruta": r["ruta"],
                "titulo": r.get("titulo") or r["archivo"],
                "emisor_propuesto": r.get("entidad_propuesta") or "(no determinado)",
                "confianza_entidad": r.get("confianza_entidad", "?"),
                "tipo_propuesto": r.get("tipo_propuesto") or "no_determinado",
                "periodo_propuesto": r.get("periodo_propuesto") or "(no determinado)",
                "confianza_periodo": r.get("confianza", "?"),
                "periodo_candidatos": r.get("candidatos", []),
                "dominios_propuestos": r.get("dominios_propuestos", []),
                "paginas": r.get("paginas"),
                "evidencia_extracto": "",
                "evidencia_dominios": evidencias,
                "url_origen": r.get("url_origen"),
                "fecha_acceso": r.get("fecha_acceso"),
                "avisos": avisos,
                "recomendacion": r.get("recomendacion", "revisar"),
            }
        )
    return salida


def cargar_cuarentena_no_pdf() -> list:
    """The spreadsheets in quarantine: present, unread, and declared as such.

    There is no cheap reader for them here, and inventing a characterisation
    from a file name would be exactly the kind of guess this whole pass exists
    to remove.

    [ES] Las planillas de cuarentena: presentes, no leidas, y declaradas como
    tales.

    Aca no hay lector barato para ellas, e inventar una caracterizacion a partir
    de un nombre de archivo seria justamente el tipo de conjetura que esta pasada
    existe para sacar.
    """
    salida = []
    for ruta in sorted(CUARENTENA.iterdir()):
        if ruta.suffix.lower() == ".pdf" or not ruta.is_file():
            continue
        salida.append(
            {
                "id": ruta.name,
                "cohorte": "cuarentena",
                "archivo": ruta.name,
                "ruta": str(ruta.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "titulo": ruta.name,
                "emisor_propuesto": "(no determinado)",
                "confianza_entidad": "sin_entidad",
                "tipo_propuesto": "no_determinado",
                "periodo_propuesto": "(no determinado)",
                "confianza_periodo": "sin_periodo",
                "periodo_candidatos": [],
                "dominios_propuestos": [],
                "paginas": None,
                "evidencia_extracto": "",
                "evidencia_dominios": [],
                "url_origen": None,
                "avisos": [
                    f"Formato `{ruta.suffix.lstrip('.')}`: no se leyó su contenido. "
                    "No hay lector liviano instalado y no se inventa una "
                    "caracterización a partir del nombre."
                ],
                "recomendacion": "revisar",
            }
        )
    return salida


PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revisión del corpus candidato</title>
<style>
:root{--tinta:#1c1c1e;--suave:#5b5f66;--linea:#dfe3e8;--fondo:#f5f6f8;--panel:#fff;
--acento:#2f5597;--ok:#1e7a46;--corr:#8a5a00;--duda:#7a4fb5;--excl:#a32020;
--aviso:#fff4e5;--avisoL:#e0a458}
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
.cohorte{display:inline-block;border-radius:99px;padding:2px 10px;font-size:12px;
border:1px solid var(--linea);background:#eef2f8;color:var(--acento)}
dl{display:grid;grid-template-columns:180px 1fr;gap:7px 16px;margin:16px 0}
dt{color:var(--suave);font-size:13px}dd{margin:0}
.conf{font-size:11px;border:1px solid var(--linea);border-radius:99px;padding:1px 7px;
margin-left:6px;color:var(--suave)}
.tags{display:flex;gap:6px;flex-wrap:wrap}
.tag{background:#eaf0fb;color:var(--acento);border:1px solid #cfdcf5;border-radius:99px;
padding:2px 10px;font-size:13px}
.tag.no{background:#f4f4f5;color:var(--suave);border-color:var(--linea)}
.aviso{background:var(--aviso);border:1px solid var(--avisoL);border-radius:8px;
padding:10px 13px;margin:8px 0;font-size:13.5px}
.ev{background:#fafbfc;border:1px solid var(--linea);border-radius:8px;padding:11px 13px;
margin:8px 0;font-size:13px}
.ev .rot{color:var(--suave);font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;
margin-bottom:5px}
.acc{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 4px}
button{font:inherit;border:1px solid var(--linea);background:var(--panel);color:var(--tinta);
border-radius:8px;padding:9px 16px;cursor:pointer}
button:hover{border-color:var(--suave)}button:disabled{opacity:.45;cursor:not-allowed}
button.sel[data-d=confirmar]{background:var(--ok);border-color:var(--ok);color:#fff}
button.sel[data-d=corregir]{background:var(--corr);border-color:var(--corr);color:#fff}
button.sel[data-d=dudoso]{background:var(--duda);border-color:var(--duda);color:#fff}
button.sel[data-d=excluir]{background:var(--excl);border-color:var(--excl);color:#fff}
.corr{border:1px dashed var(--corr);border-radius:8px;padding:13px;margin-top:12px}
.corr label{display:block;margin-bottom:9px}
.corr span{display:block;color:var(--suave);font-size:12.5px;margin-bottom:3px}
input[type=text],textarea{width:100%;font:inherit;padding:8px 10px;border:1px solid var(--linea);
border-radius:6px}
textarea{min-height:70px}
.actual{color:var(--suave);font-size:12px;margin-top:2px}
.err{color:var(--excl);font-size:13px;margin-top:9px;min-height:18px}
.nav{display:flex;gap:10px;justify-content:space-between;margin-top:16px;flex-wrap:wrap}
select{font:inherit;padding:8px;border:1px solid var(--linea);border-radius:6px}
.pie{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px;padding-top:16px;
border-top:1px solid var(--linea)}
.peligro{border-color:var(--excl);color:var(--excl)}
.oculto{display:none}
</style></head>
<body>
<header>
<div class="titulo">Revisión del corpus candidato — activos, nuevos y cuarentena</div>
<div class="sub" id="sub"></div>
<div class="barra"><div id="prog"></div></div>
<div class="cont">
<span>✓ confirmados <b id="c-confirmar">0</b></span>
<span>✎ corregidos <b id="c-corregir">0</b></span>
<span>? dudosos <b id="c-dudoso">0</b></span>
<span>✕ excluidos <b id="c-excluir">0</b></span>
<span>· pendientes <b id="c-pend">0</b></span>
</div></header>
<main>
<div id="persist" class="aviso oculto"></div>
<section class="ficha">
<div class="mono" id="pos"></div>
<h1 id="titulo"></h1>
<div class="mono" id="ident"></div>
<div id="avisos"></div>
<dl>
<dt>Cohorte</dt><dd><span class="cohorte" id="cohorte"></span></dd>
<dt>Archivo</dt><dd id="archivo"></dd>
<dt>Emisor propuesto</dt><dd id="emisor"></dd>
<dt>Tipo propuesto</dt><dd id="tipo"></dd>
<dt>Período propuesto</dt><dd id="periodo"></dd>
<dt>Dominios propuestos</dt><dd><div class="tags" id="dominios"></div></dd>
<dt>Páginas</dt><dd id="paginas"></dd>
<dt>Origen</dt><dd id="origen"></dd>
</dl>
<div id="evidencia"></div>
<div class="acc" id="acciones"></div>
<div class="corr oculto" id="correcciones"></div>
<label style="display:block;margin-top:12px">
<span style="display:block;color:#5b5f66;font-size:12.5px" id="rotobs">Observaciones</span>
<textarea id="obs"></textarea></label>
<div class="err" id="err"></div>
<div class="nav">
<div style="display:flex;gap:10px">
<button type="button" id="ant">← Anterior</button>
<button type="button" id="sig">Siguiente →</button></div>
<select id="salto"></select></div>
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

function hayCorreccion(doc,est,campos,origen){
  for(const c of campos){
    const n=limpio(est[c]);
    if(n!=="" && n!==limpio(doc[origen[c]])) return true;
  }
  return false;
}

function validar(doc,est,campos,origen){
  const d=limpio(est.decision);
  if(d==="") return {ok:false,motivo:"Sin decisión."};
  if(d==="confirmar"){
    for(const c of campos) if(limpio(est[c])!=="")
      return {ok:false,motivo:"«Confirmar» no admite correcciones cargadas."};
    return {ok:true,motivo:""};
  }
  if(d==="corregir"){
    if(!hayCorreccion(doc,est,campos,origen))
      return {ok:false,motivo:"Completá al menos un campo con un valor distinto del actual."};
    return {ok:true,motivo:""};
  }
  if(d==="dudoso"&&limpio(est.observaciones)==="")
    return {ok:false,motivo:"«Dudoso» exige explicar la duda."};
  if(d==="excluir"&&limpio(est.observaciones)==="")
    return {ok:false,motivo:"«Excluir» exige justificar el motivo."};
  return {ok:true,motivo:""};
}

function contar(docs,est,ops,campos,origen){
  const c={pendientes:0}; for(const o of ops) c[o]=0;
  for(const d of docs){
    const e=est[d.id]||{};
    if(validar(d,e,campos,origen).ok) c[limpio(e.decision)]+=1; else c.pendientes+=1;
  }
  return c;
}

function celda(v){
  const s=(v===undefined||v===null)?"":String(v);
  return /[",\n\r]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;
}

function armarCsv(docs,est,cols,humanas){
  const l=[cols.map(celda).join(",")];
  for(const d of docs){
    const e=est[d.id]||{};
    l.push(cols.map(function(c){
      if(humanas.indexOf(c)>=0) return celda(limpio(e[c]));
      const v=d[c];
      return celda(Array.isArray(v)?v.join("|"):v);
    }).join(","));
  }
  return l.join("\n")+"\n";
}

function armarJson(meta,docs,est,ops,campos,origen,humanas){
  return {
    receta:meta.receta, huella_fuentes:meta.huella_fuentes,
    fecha_exportacion:meta.fecha_exportacion, documentos:docs.length,
    conteos:contar(docs,est,ops,campos,origen),
    decisiones:docs.map(function(d){
      const e=est[d.id]||{}; const r={id:d.id,cohorte:d.cohorte};
      for(const c of humanas) r[c]=limpio(e[c]);
      r.valida=validar(d,e,campos,origen).ok;
      return r;
    }),
    salvedades:meta.salvedades
  };
}
/* === FIN LOGICA PURA === */

(function(){
"use strict";
const D=JSON.parse(document.getElementById("datos").textContent);
const CAMPOS=D.campos, ORIGEN=D.origen_de_correccion, HUMANAS=D.columnas_humanas;
const CLAVE="revision_corpus::"+D.huella_fuentes.slice(0,20);
let i=0, est={}, persiste=true;
try{localStorage.setItem(CLAVE+"::p","1");localStorage.removeItem(CLAVE+"::p");}
catch(e){persiste=false;}
if(persiste){try{est=JSON.parse(localStorage.getItem(CLAVE)||"{}");}catch(e){est={};}}
function guardar(){if(persiste){try{localStorage.setItem(CLAVE,JSON.stringify(est));}
catch(e){persiste=false;avisarP();}}}
function avisarP(){const c=document.getElementById("persist");
if(persiste){c.classList.add("oculto");return;}
c.classList.remove("oculto");
c.textContent="⚠ Este navegador no permite guardado automático acá. Tus decisiones NO se "+
"conservan si cerrás la pestaña. Usá «Descargar borrador» seguido.";}
function E(d){if(!est[d.id])est[d.id]={};return est[d.id];}
function vaciar(n){while(n.firstChild)n.removeChild(n.firstChild);}
function txt(id,v){document.getElementById(id).textContent=
(v===null||v===undefined||v==="")?"—":String(v);}
function conf(padre,valor){const s=document.createElement("span");
s.className="conf";s.textContent="confianza: "+valor;padre.appendChild(s);}

function pintar(){
const d=D.documentos[i];
txt("pos","Documento "+(i+1)+" de "+D.documentos.length);
txt("titulo",d.titulo);
txt("ident",d.id+"  ·  "+d.archivo);
txt("cohorte",D.etiquetas_cohorte[d.cohorte]||d.cohorte);
txt("archivo",d.ruta);
txt("paginas",d.paginas);
const em=document.getElementById("emisor");vaciar(em);
em.appendChild(document.createTextNode(d.emisor_propuesto));conf(em,d.confianza_entidad);
txt("tipo",d.tipo_propuesto);
const pe=document.getElementById("periodo");vaciar(pe);
pe.appendChild(document.createTextNode(d.periodo_propuesto));conf(pe,d.confianza_periodo);
if(d.periodo_candidatos&&d.periodo_candidatos.length>1){
const alt=document.createElement("div");alt.className="actual";
alt.textContent="otras fuentes: "+d.periodo_candidatos.map(function(c){
return c.valor+" ("+c.fuente+")";}).join(" · ");pe.appendChild(alt);}

const dom=document.getElementById("dominios");vaciar(dom);
for(const nombre of D.dominios){
const s=document.createElement("span");
const puesto=d.dominios_propuestos.indexOf(nombre)>=0;
s.className=puesto?"tag":"tag no";
s.textContent=(puesto?"✓ ":"· ")+nombre;dom.appendChild(s);}

const or=document.getElementById("origen");vaciar(or);
if(d.url_origen&&/^https?:\/\//i.test(d.url_origen)){
const a=document.createElement("a");a.href=d.url_origen;a.textContent=d.url_origen;
a.target="_blank";a.rel="noreferrer noopener";or.appendChild(a);
}else{or.appendChild(document.createTextNode(d.url_origen||"—"));}

const av=document.getElementById("avisos");vaciar(av);
for(const a of d.avisos){const x=document.createElement("div");x.className="aviso";
x.textContent="⚠ "+a;av.appendChild(x);}

const ev=document.getElementById("evidencia");vaciar(ev);
if(d.evidencia_extracto){const b=document.createElement("div");b.className="ev";
const r=document.createElement("div");r.className="rot";r.textContent="Extracto textual";
const t=document.createElement("div");t.textContent=d.evidencia_extracto;
b.appendChild(r);b.appendChild(t);ev.appendChild(b);}
for(const e of d.evidencia_dominios){
const b=document.createElement("div");b.className="ev";
const r=document.createElement("div");r.className="rot";
r.textContent=(e.propuesto?"✓ ":"· ")+e.dominio+" — "+e.terminos+
" términos distintos — «"+e.termino+"» p."+e.pagina;
const t=document.createElement("div");t.textContent="…"+e.cita+"…";
b.appendChild(r);b.appendChild(t);ev.appendChild(b);}

const ac=document.getElementById("acciones");vaciar(ac);
const e0=E(d);
for(const op of D.opciones){
const b=document.createElement("button");b.type="button";b.dataset.d=op;
b.textContent=D.etiquetas_decision[op];
if(e0.decision===op)b.className="sel";
b.addEventListener("click",function(){e0.decision=op;
if(op==="confirmar")for(const c of CAMPOS)e0[c]="";guardar();pintar();});
ac.appendChild(b);}

const co=document.getElementById("correcciones");vaciar(co);
if(e0.decision==="corregir"){co.classList.remove("oculto");
const n=document.createElement("div");n.className="actual";
n.textContent="Completá solo lo que cambia. Un campo vacío conserva el valor actual.";
co.appendChild(n);
for(const c of CAMPOS){
const l=document.createElement("label");
const s=document.createElement("span");s.textContent=c;
const inp=document.createElement("input");inp.type="text";inp.value=e0[c]||"";
inp.addEventListener("input",function(){e0[c]=inp.value;guardar();cab();val();});
const a=document.createElement("div");a.className="actual";
const actual=d[ORIGEN[c]];
a.textContent="actual: "+(Array.isArray(actual)?actual.join("|"):(actual||"—"));
l.appendChild(s);l.appendChild(inp);l.appendChild(a);co.appendChild(l);}
}else{co.classList.add("oculto");}

const ta=document.getElementById("obs");
document.getElementById("rotobs").textContent=
(e0.decision==="dudoso")?"Observaciones — obligatorio: explicá la duda":
(e0.decision==="excluir")?"Observaciones — obligatorio: justificá el motivo":
"Observaciones (opcional)";
ta.value=e0.observaciones||"";
ta.oninput=function(){e0.observaciones=ta.value;guardar();cab();val();};

val();
document.getElementById("ant").disabled=(i===0);
document.getElementById("sig").disabled=(i===D.documentos.length-1);
cab();window.scrollTo(0,0);
}

function val(){const d=D.documentos[i];const v=validar(d,E(d),CAMPOS,ORIGEN);
document.getElementById("err").textContent=(E(d).decision&&!v.ok)?v.motivo:"";return v;}

function cab(){
const c=contar(D.documentos,est,D.opciones,CAMPOS,ORIGEN);
for(const o of D.opciones)document.getElementById("c-"+o).textContent=String(c[o]);
document.getElementById("c-pend").textContent=String(c.pendientes);
const h=D.documentos.length-c.pendientes;
document.getElementById("prog").style.width=(h/D.documentos.length*100).toFixed(1)+"%";
document.getElementById("sub").textContent=h+" de "+D.documentos.length+
" con decisión válida";
document.getElementById("csv").disabled=(c.pendientes>0);
document.getElementById("json").disabled=(c.pendientes>0);
const sel=document.getElementById("salto");vaciar(sel);
D.documentos.forEach(function(d,k){
const e=est[d.id]||{};const v=validar(d,e,CAMPOS,ORIGEN);
const o=document.createElement("option");o.value=String(k);
o.textContent=(v.ok?D.marcas[e.decision]:"·")+"  "+(k+1)+"  ["+
D.etiquetas_cohorte[d.cohorte]+"]  "+d.id.slice(0,46);
if(k===i)o.selected=true;sel.appendChild(o);});
sel.onchange=function(){i=parseInt(sel.value,10);pintar();};
}

function bajar(n,c,t){const b=new Blob([c],{type:t});const u=URL.createObjectURL(b);
const a=document.createElement("a");a.href=u;a.download=n;document.body.appendChild(a);
a.click();document.body.removeChild(a);URL.revokeObjectURL(u);}
function meta(){return{receta:D.receta,huella_fuentes:D.huella_fuentes,
fecha_exportacion:new Date().toISOString(),salvedades:D.salvedades};}

document.getElementById("ant").onclick=function(){if(i>0){i--;pintar();}};
document.getElementById("sig").onclick=function(){if(i<D.documentos.length-1){i++;pintar();}};
document.getElementById("csv").onclick=function(){
bajar("revision_corpus_decisiones.csv","﻿"+armarCsv(D.documentos,est,D.columnas,HUMANAS),
"text/csv;charset=utf-8");};
document.getElementById("json").onclick=function(){
bajar("revision_corpus_decisiones.json",JSON.stringify(
armarJson(meta(),D.documentos,est,D.opciones,CAMPOS,ORIGEN,HUMANAS),null,2),
"application/json;charset=utf-8");};
document.getElementById("borrador").onclick=function(){
bajar("revision_corpus_borrador.json",JSON.stringify(
armarJson(meta(),D.documentos,est,D.opciones,CAMPOS,ORIGEN,HUMANAS),null,2),
"application/json;charset=utf-8");};
document.getElementById("borrar").onclick=function(){
if(!window.confirm("¿Borrar TODAS las decisiones?"))return;
if(!window.confirm("Confirmá otra vez."))return;
est={};try{localStorage.removeItem(CLAVE);}catch(e){}i=0;pintar();};

avisarP();pintar();
})();
</script></body></html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--salida", type=Path,
        default=EXPERIMENTS_DIR / "revision_corpus" / "revision_corpus.html",
    )
    args = parser.parse_args()

    documentos = cargar_activos() + cargar_caracterizados() + cargar_cuarentena_no_pdf()

    columnas = [
        "id", "cohorte", "archivo", "ruta", "titulo", "emisor_propuesto",
        "tipo_propuesto", "periodo_propuesto", "dominios_propuestos", "paginas",
        "url_origen", "recomendacion",
        "decision", "emisor_corregido", "tipo_corregido", "periodo_corregido",
        "dominios_corregidos", "observaciones",
    ]

    fuentes = hashlib.sha256()
    for ruta in (CARACTERIZACION, CSV_ACTIVOS):
        if ruta.exists():
            fuentes.update(huella(ruta).encode())

    datos = {
        "receta": RECETA_VERSION,
        "huella_fuentes": fuentes.hexdigest(),
        "columnas": columnas,
        "columnas_humanas": ["decision"] + list(CAMPOS) + ["observaciones"],
        "campos": list(CAMPOS),
        "origen_de_correccion": {
            "emisor_corregido": "emisor_propuesto",
            "tipo_corregido": "tipo_propuesto",
            "periodo_corregido": "periodo_propuesto",
            "dominios_corregidos": "dominios_propuestos",
        },
        "opciones": list(OPCIONES),
        "etiquetas_decision": {
            "confirmar": "✓ Confirmar", "corregir": "✎ Corregir",
            "dudoso": "? Dudoso", "excluir": "✕ Excluir",
        },
        "marcas": {"confirmar": "✓", "corregir": "✎", "dudoso": "?", "excluir": "✕"},
        "etiquetas_cohorte": {
            "activo": "activo (24)", "empresarial_nuevo": "nuevo (24)",
            "cuarentena": "cuarentena (11)",
        },
        "dominios": list(DOMINIOS),
        "documentos": documentos,
        "salvedades": [
            "Entidad, tipo, periodo y dominios son PROPUESTAS con evidencia, no verdad.",
            "Un campo de correccion vacio conserva el valor actual.",
            "La exportacion es una propuesta: no se aplico nada al catalogo ni a "
            "PostgreSQL.",
            "Los 24 activos no se modificaron; se revisan, no se tocan.",
        ],
    }

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(
        PLANTILLA.replace(
            "__DATOS__", json.dumps(datos, ensure_ascii=False).replace("<", "\\u003c")
        ),
        encoding="utf-8",
    )

    por_cohorte = collections.Counter(d["cohorte"] for d in documentos)
    print(f"documentos  {len(documentos)}")
    for k, v in por_cohorte.most_common():
        print(f"  {k:20} {v}")
    print(f"\nhtml  {args.salida}  ({args.salida.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
