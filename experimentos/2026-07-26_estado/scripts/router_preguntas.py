"""ROUTER SOBRE PREGUNTAS NATURALES — aisla la variable INSTRUMENTO.

En el corrida sobre TITULOS (router_llm.py) el LLM 3B saco 43% y el coseno 100%
(McNemar 27-0, p<1e-7). Pero un titulo como "CAPITULO XIV" NO TIENE INTENCION que
interpretar: es la cancha perfecta del coseno (el titulo salio del centroide contra el
que se lo compara) y la peor del LLM.

Este script corre EL MISMO modelo y EL MISMO prompt sobre PREGUNTAS NATURALES con
ground truth conocido. Diseno pareado. Si el LLM salta de 43% a ~85%, el problema era
el instrumento; si se queda en ~45%, el problema es el modelo de 3B.

Ademas responde la pregunta central del plan: ¿existe UNA sola consulta donde el LLM
acierta y el coseno falla? Eso seria la "informacion que los vectores no tienen"
(ejemplo textual del plan: "derivando una consulta tecnica sobre 'retenciones' al
modulo fiscal y no al financiero"). Se imprimen esos casos uno por uno.

FUENTE DEL GROUND TRUTH — declarado, no oculto:
  - 20 preguntas mono-dominio: silo correcto = dominio del DOCUMENTO del que salieron
    (etiquetado_n40.py). Verificable leyendo la pregunta.
  - 30 preguntas multi-dominio: conjunto de 2 silos declarado al redactarlas
    (multi_n30.py). Etiquetado por LLM, verificable por Lucas leyendo.
  ⚠️ El ground truth multi-dominio NO fue verificado por un humano todavia.

ESTADISTICA: McNemar exacto (binomial de dos colas sobre los discordantes) por
instrumento y agrupado. Se reporta el PISO de significancia: con nd discordantes todos
en una direccion, el minimo p alcanzable es 2^(1-nd). Si nd < 6 el test NO puede
alcanzar 0.05 ni siendo unanime — se dice explicitamente.
"""
import sys, io, json, time
from pathlib import Path
from math import comb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from clasificador import _coseno, _softmax, _centroide_l2
from config import CLASIFICADOR_TEMP

SILOS = ["legal", "impositivo", "contable", "financiero"]
DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}

# ---------- 20 preguntas mono-dominio (de etiquetado_n40.py) ----------
MONO = [
 ("¿Qué ocurre si una empresa del sector eléctrico incumple las obligaciones del marco regulatorio?", "Ley_24065_Energia_Electrica_TO"),
 ("¿Desde cuándo empieza a correr el término para que el fisco reclame un tributo?", "Ley_11683_Procedimiento_Fiscal_TO"),
 ("¿Qué facultades tiene el organismo de control del servicio eléctrico?", "Ley_24065_Energia_Electrica_TO"),
 ("¿Cómo se determina de oficio la materia imponible cuando no se presenta la declaración?", "Ley_11683_Procedimiento_Fiscal_TO"),
 ("¿Qué porcentaje corresponde retener sobre los pagos alcanzados por el régimen?", "RG_AFIP_830"),
 ("¿Cómo se remunera la energía en el mercado mayorista?", "Res_SE_61_1992_Los_Procedimientos"),
 ("¿Qué obligaciones tiene el transportista respecto del sistema de transporte?", "Res_SE_137_1992"),
 ("¿Cómo se compone el patrimonio neto al cierre del ejercicio?", "Estados_Contables_Neuquen"),
 ("¿Qué régimen se aplica a la distribución y comercialización de gas natural?", "Ley_24076_Gas_Natural_TO"),
 ("¿Qué sucede ante la falta de presentación de la declaración jurada en término?", "Decreto_821_1998_TO_Ley_11683"),
 ("¿Qué establece la reglamentación sobre el ente regulador del gas?", "Decreto_1738_1992_Reglamentario_Gas"),
 ("¿Qué recursos puede interponer el contribuyente contra una determinación?", "Ley_11683_Procedimiento_Fiscal_TO"),
 ("¿Cómo se calcula el despacho de cargas en el sistema eléctrico?", "Res_SE_61_1992_Los_Procedimientos"),
 ("¿Qué información contiene el estado de flujo de efectivo?", "FS-31-03-2019"),
 ("¿Qué condiciones tiene la emisión de obligaciones negociables?", "MSU_ON_ClaseIV"),
 ("¿Qué sanciones prevé el régimen para las infracciones formales?", "Decreto_821_1998_TO_Ley_11683"),
 ("¿Cómo se valúan los bienes de uso en los estados contables?", "EEFF-ind-31-03-2019"),
 ("¿Qué establece la resolución del ente sobre la calidad del servicio?", "ENRE_Resolucion_544_2024"),
 ("¿Qué factores considera la calificación crediticia de la compañía?", "Transener_Calificacion_FIX"),
 ("¿Qué reglamenta el decreto sobre el marco eléctrico?", "Decreto_1398_1992_Reglamentario_Electrico"),
]
# ---------- 30 preguntas multi-dominio (de multi_n30.py) ----------
MULTI = [
 ("¿Qué efecto tiene una sanción del ente regulador sobre los estados contables de la distribuidora?", {"legal","contable"}),
 ("¿Cómo se refleja en el estado de resultados el pago de penalidades regulatorias?", {"legal","contable"}),
 ("¿Cómo afecta el marco regulatorio del transporte eléctrico a la valuación de los activos?", {"legal","contable"}),
 ("¿Qué previsiones contables corresponden por incumplimientos del contrato de concesión?", {"legal","contable"}),
 ("¿Cómo se registra el canon de concesión que exige la normativa energética?", {"legal","contable"}),
 ("¿Qué impacto tiene el régimen tarifario regulado sobre la proyección de ingresos?", {"legal","financiero"}),
 ("¿Cómo influye el marco regulatorio en la calificación crediticia de una transportista?", {"legal","financiero"}),
 ("¿Qué riesgos regulatorios deben informarse a los inversores de una emisora energética?", {"legal","financiero"}),
 ("¿Cómo afecta una resolución del ENRE al flujo de fondos de la concesionaria?", {"legal","financiero"}),
 ("¿Qué garantías exige el marco regulatorio para el financiamiento de obras de transporte?", {"legal","financiero"}),
 ("¿Cómo se registra contablemente el impuesto a las ganancias determinado según el régimen fiscal?", {"impositivo","contable"}),
 ("¿Qué tratamiento contable corresponde a las previsiones por contingencias fiscales?", {"impositivo","contable"}),
 ("¿Cómo se contabilizan las retenciones sufridas por el contribuyente?", {"impositivo","contable"}),
 ("¿Qué asiento corresponde por el devengamiento de intereses resarcitorios impositivos?", {"impositivo","contable"}),
 ("¿Cómo se expone en el balance el saldo a favor de impuestos?", {"impositivo","contable"}),
 ("¿Cómo impactan las retenciones impositivas en el flujo de fondos de la compañía?", {"impositivo","financiero"}),
 ("¿Qué obligaciones fiscales genera la emisión de una obligación negociable?", {"impositivo","financiero"}),
 ("¿Qué impacto tiene el endeudamiento financiero en la determinación del impuesto a las ganancias?", {"impositivo","financiero"}),
 ("¿Cómo tributan los intereses pagados a inversores del exterior?", {"impositivo","financiero"}),
 ("¿Qué efecto fiscal tiene la colocación de deuda en el mercado de capitales?", {"impositivo","financiero"}),
 ("¿Cómo se vincula el resultado del ejercicio con la generación de caja operativa?", {"contable","financiero"}),
 ("¿Qué información contable sustenta el cálculo del nivel de endeudamiento?", {"contable","financiero"}),
 ("¿Cómo se refleja la deuda financiera en el estado de situación patrimonial?", {"contable","financiero"}),
 ("¿Qué relación hay entre las provisiones registradas y el riesgo financiero informado?", {"contable","financiero"}),
 ("¿Cómo impactan los intereses devengados en el resultado y en el flujo de efectivo?", {"contable","financiero"}),
 ("¿Qué régimen sancionatorio aplica al incumplimiento de obligaciones formales del sector energético?", {"legal","impositivo"}),
 ("¿Cómo se articulan las facultades del ente regulador con las del fisco ante un mismo hecho?", {"legal","impositivo"}),
 ("¿Qué plazos de prescripción rigen para las obligaciones regulatorias y para las fiscales?", {"legal","impositivo"}),
 ("¿Qué tributos alcanzan a la actividad de distribución de gas natural?", {"legal","impositivo"}),
 ("¿Cómo se recurre una determinación que involucra tanto materia regulatoria como fiscal?", {"legal","impositivo"}),
]

CASOS = ([{"q": q, "correctos": {DOM[d]}, "tipo": "mono"} for q, d in MONO] +
         [{"q": q, "correctos": c, "tipo": "multi"} for q, c in MULTI])

# ---------- router por coseno: idéntico a producción ----------
con = conectar(); cur = con.cursor()
cur.execute("SELECT silo, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
silo = np.array([r[0] for r in filas])
X = np.array([json.loads(r[1]) for r in filas]); X = X / np.linalg.norm(X, axis=1, keepdims=True)
proto = {s: np.array(_centroide_l2([X[i] for i in range(len(X)) if silo[i] == s])) for s in SILOS}
print(f"corpus {len(X)} chunks · prototipos por silo listos", flush=True)

# se usa la funcion DE PRODUCCION, no una reimplementacion: garantiza que el vector de
# la consulta se calcule igual que en el retriever real (mismo modelo, mismo tratamiento)
from embedder import embed_query
from config import EMBEDDING_MODEL
print(f"cargando embedder de produccion ({EMBEDDING_MODEL})...", flush=True)

def rutear_coseno(texto):
    q = np.array(embed_query(texto))
    q = q / np.linalg.norm(q)          # los prototipos y X estan L2-normalizados
    dist = _softmax({s: _coseno(q, proto[s]) for s in SILOS}, CLASIFICADOR_TEMP)
    orden = sorted(dist, key=dist.get, reverse=True)
    return orden, dist

# ---------- router por LLM local: MISMO prompt que la corrida de títulos ----------
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
M = "Qwen/Qwen2.5-3B-Instruct"
print(f"cargando {M} (CPU, bfloat16)...", flush=True)
t0 = time.time()
tok = AutoTokenizer.from_pretrained(M)
mod = AutoModelForCausalLM.from_pretrained(M, dtype=torch.bfloat16, device_map="cpu", low_cpu_mem_usage=True)
mod.eval()
print(f"  cargado en {time.time()-t0:.0f}s", flush=True)

DEFINICIONES = """legal = regulación del sector energético: ENRE, ENARGAS, CAMMESA, leyes de energía eléctrica y gas, concesiones, despacho, tarifas reguladas, sanciones del ente regulador.
impositivo = materia tributaria: AFIP/ARCA, impuestos, retenciones y percepciones fiscales, declaraciones juradas, determinación de oficio, prescripción tributaria.
contable = registración y estados contables: balances, patrimonio neto, estado de resultados, normas contables, asientos, valuación de activos.
financiero = finanzas corporativas: deuda, obligaciones negociables, flujos de fondos, tasas de interés, calificaciones crediticias, emisiones."""

# A1: prompt IDÉNTICO al de la corrida de títulos -> comparable punto a punto
P_UNO = """Sos un experto en normativa argentina. Clasificá la consulta en UNO de estos cuatro dominios:

{d}

Consulta: "{q}"

Respondé SOLO con una palabra: legal, impositivo, contable o financiero.
Dominio:"""

# A2: permite hasta DOS dominios -> mide cobertura en preguntas multi-dominio
P_DOS = """Sos un experto en normativa argentina. Una consulta puede necesitar UNO o DOS de estos dominios:

{d}

Consulta: "{q}"

Respondé SOLO con los dominios necesarios, del más al menos relevante, separados por coma.
Dominios:"""

def generar(prompt, max_new):
    msgs = [{"role": "user", "content": prompt}]
    t = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids = tok(t, return_tensors="pt")
    with torch.no_grad():
        out = mod.generate(**ids, max_new_tokens=max_new, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip().lower()

def parsear(txt):
    """devuelve los silos mencionados EN ORDEN de aparición, sin repetir"""
    pos = sorted([(txt.find(s), s) for s in SILOS if s in txt])
    return [s for _, s in pos]

res = []
salida = SCR / "router_preguntas_parcial.json"

# PASADA 1 — la comparacion PRINCIPAL (LLM-1 top-1 vs coseno top-1), n=50.
# Va primero y sola para que el resultado que decide este disponible en la mitad
# del tiempo; la pasada 2 (cobertura@2) es informacion adicional, no la respuesta.
print(f"\nPASADA 1/2 — comparacion principal (prompt IDENTICO al de titulos)", flush=True)
print(f"{'#':>3s} {'tipo':6s} {'objetivo':22s} {'LLM-1':12s} {'coseno':12s} ok", flush=True)
for k, c in enumerate(CASOS, 1):
    orden_cos, dist = rutear_coseno(c["q"])
    l1 = parsear(generar(P_UNO.format(d=DEFINICIONES, q=c["q"]), 6))
    top_cos = orden_cos[0]
    top_llm = l1[0] if l1 else None
    fila = {
        "q": c["q"], "tipo": c["tipo"], "correctos": sorted(c["correctos"]),
        "llm1": top_llm, "llm2": None, "coseno": orden_cos[:2],
        "dist_cos": {s: round(dist[s], 4) for s in SILOS},
        "ok_llm1": top_llm in c["correctos"],
        "ok_cos": top_cos in c["correctos"],
        "cob_llm2": None,
        "cob_cos2": c["correctos"] <= set(orden_cos[:2]),
    }
    res.append(fila)
    salida.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    marca = ("L" if fila["ok_llm1"] else "-") + ("C" if fila["ok_cos"] else "-")
    print(f"{k:3d} {c['tipo']:6s} {'/'.join(sorted(c['correctos'])):22s} "
          f"{str(top_llm):12s} {top_cos:12s} {marca}", flush=True)

# PASADA 2 — cobertura@2: solo sobre las multi-dominio, que son las unicas donde
# "abrir dos silos" tiene sentido. 30 llamadas en vez de 50.
print(f"\nPASADA 2/2 — cobertura@2 (solo multi-dominio, permite hasta 2 dominios)", flush=True)
for k, fila in enumerate(res, 1):
    if fila["tipo"] != "multi":
        continue
    l2 = parsear(generar(P_DOS.format(d=DEFINICIONES, q=fila["q"]), 20))
    fila["llm2"] = l2
    fila["cob_llm2"] = set(fila["correctos"]) <= set(l2[:2])
    salida.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{k:3d} objetivo={'/'.join(fila['correctos']):22s} LLM2={','.join(l2) or '-':26s} "
          f"{'OK' if fila['cob_llm2'] else '--'}", flush=True)

# ================= ESTADÍSTICA =================
def mcnemar(sub, ka, kb):
    b10 = sum(1 for r in sub if r[ka] and not r[kb])   # a favor de A
    b01 = sum(1 for r in sub if r[kb] and not r[ka])   # a favor de B
    nd = b10 + b01
    if nd == 0:
        return b10, b01, nd, 1.0, 1.0
    p = min(sum(comb(nd, i) for i in range(min(b10, b01) + 1)) / 2 ** nd * 2, 1.0)
    piso = 2.0 ** (1 - nd)          # mínimo p alcanzable con nd discordantes unánimes
    return b10, b01, nd, p, min(piso, 1.0)

print("\n" + "=" * 74)
print("ROUTER SOBRE PREGUNTAS NATURALES · LLM 3B local vs coseno a prototipos")
print("=" * 74)
for nom, sub in (("mono-dominio", [r for r in res if r["tipo"] == "mono"]),
                 ("multi-dominio", [r for r in res if r["tipo"] == "multi"]),
                 ("AGRUPADO", res)):
    m = len(sub)
    if not m:
        continue
    a = sum(r["ok_llm1"] for r in sub); b = sum(r["ok_cos"] for r in sub)
    b10, b01, nd, p, piso = mcnemar(sub, "ok_llm1", "ok_cos")
    print(f"\n  {nom}  (n={m})")
    print(f"     LLM-1 top-1 acierta : {a}/{m}  ({a/m:.1%})")
    print(f"     coseno  top-1 acierta: {b}/{m}  ({b/m:.1%})")
    print(f"     McNemar: {b10} a favor del LLM · {b01} a favor del coseno · discordantes={nd}")
    if nd == 0:
        print(f"     p = 1.0  ->  EMPATE EXACTO, ningun par discordante")
    elif piso > 0.05:
        print(f"     p = {p:.4f}  ->  NO CONCLUYENTE: con solo {nd} discordantes el minimo")
        print(f"                     p alcanzable es {piso:.4f} > 0.05. n insuficiente.")
    else:
        print(f"     p = {p:.4f}  ->  {'SIGNIFICATIVO' if p < 0.05 else 'no significativo'}"
              f"   (piso con n={nd}: {piso:.4f})")

sub_m = [r for r in res if r["tipo"] == "multi"]
if sub_m:
    m = len(sub_m)
    cl = sum(r["cob_llm2"] for r in sub_m); cc = sum(r["cob_cos2"] for r in sub_m)
    b10, b01, nd, p, piso = mcnemar(sub_m, "cob_llm2", "cob_cos2")
    print(f"\n  COBERTURA@2 en multi-dominio — ¿los DOS silos correctos entre los 2 primeros? (n={m})")
    print(f"     LLM-2  : {cl}/{m}  ({cl/m:.1%})")
    print(f"     coseno : {cc}/{m}  ({cc/m:.1%})")
    print(f"     McNemar: {b10}-{b01} · nd={nd} · p={p:.4f}" +
          ("  [NO CONCLUYENTE: piso %.4f]" % piso if piso > 0.05 else ""))

print("\n" + "-" * 74)
print("  LO QUE IMPORTA PARA EL PLAN: casos donde el LLM ACIERTA y el coseno FALLA")
print("  (seria la 'informacion que los vectores no tienen')")
gana = [r for r in res if r["ok_llm1"] and not r["ok_cos"]]
if not gana:
    print("     NINGUNO. El LLM de 3B no aporta ni un solo caso propio.")
for r in gana:
    print(f"     [{r['tipo']}] {r['q']}")
    print(f"        correcto={'/'.join(r['correctos'])}  LLM={r['llm1']}  coseno={r['coseno'][0]} "
          f"(p={r['dist_cos'][r['coseno'][0]]:.3f})")

print("\n  calibracion del LLM-1 — ¿tiene sesgo hacia algun dominio?")
from collections import Counter
cl = Counter(r["llm1"] for r in res); cc = Counter(r["coseno"][0] for r in res)
ct = Counter(s for r in res for s in r["correctos"])
print(f"     {'silo':12s} {'esperado':>9s} {'LLM dijo':>9s} {'coseno dijo':>12s}")
for s in SILOS:
    print(f"     {s:12s} {ct[s]:9d} {cl[s]:9d} {cc[s]:12d}")
print(f"\n  resultados en {salida}")
