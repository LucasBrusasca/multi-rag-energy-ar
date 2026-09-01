"""EL DESVIO 3 (C.74): el plan pide un ROUTER LLM; se construyo un router por COSENO.

Plan aprobado, textual: "El componente central y diferenciador de esta arquitectura es el
'Orquestador con Control de Confianza Cognitivo', UN MODELO DE LENGUAJE AVANZADO que actua
como capa de control superior... analiza la INTENCION PROFUNDA de la consulta... y enruta
la peticion exclusivamente hacia los modulos expertos pertinentes (por ejemplo, derivando
una consulta tecnica sobre 'retenciones' al modulo fiscal y no al financiero)".

Implementado (ADR A8, por determinismo): coseno a prototipos -> 96.2% de acierto (C.47).

HIPOTESIS: un LLM sabe que "retencion impositiva" es fiscal y "retencion de obra" es
contractual — conocimiento del mundo que NO esta en el embedding. Es exactamente la
"informacion que los vectores no tienen" que se venia buscando.

Se usa Qwen2.5-3B-Instruct LOCAL (sin API, sin creditos). Escritura incremental.
"""
import sys, io, json, random, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from clasificador import _coseno, _softmax, _centroide_l2
from config import CLASIFICADOR_TEMP

SILOS = ["legal", "impositivo", "contable", "financiero"]
N_EVAL = 80
DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}

con = conectar(); cur = con.cursor()
cur.execute("SELECT silo, titulo, fuente, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
silo = np.array([r[0] for r in filas]); tit = np.array([r[1] for r in filas])
fue = np.array([r[2] for r in filas])
X = np.array([json.loads(r[3]) for r in filas]); X = X / np.linalg.norm(X, axis=1, keepdims=True)
n = len(filas)
random.seed(7)
pd_ = {}
for i, f in enumerate(fue):
    if f in DOM and 15 <= len(tit[i]) <= 70:
        pd_.setdefault(DOM[f], []).append(i)
consultas = []
for dd, l in pd_.items():
    consultas += random.sample(l, min(40, len(l)))
random.seed(31); random.shuffle(consultas)
consultas = consultas[:N_EVAL]
proto = {s: np.array(_centroide_l2([X[i] for i in range(n) if silo[i] == s])) for s in SILOS}
print(f"consultas de evaluacion: {len(consultas)}", flush=True)

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
M = "Qwen/Qwen2.5-3B-Instruct"
print("cargando Qwen2.5-3B (CPU, puede tardar varios minutos)...", flush=True)
t0 = time.time()
tok = AutoTokenizer.from_pretrained(M)
mod = AutoModelForCausalLM.from_pretrained(M, dtype=torch.bfloat16, device_map="cpu", low_cpu_mem_usage=True)
mod.eval()
print(f"  cargado en {time.time()-t0:.0f}s", flush=True)

PLANTILLA = """Sos un experto en normativa argentina. Clasificá la consulta en UNO de estos cuatro dominios:

legal = regulación del sector energético: ENRE, ENARGAS, CAMMESA, leyes de energía eléctrica y gas, concesiones, despacho, tarifas reguladas, sanciones del ente regulador.
impositivo = materia tributaria: AFIP/ARCA, impuestos, retenciones y percepciones fiscales, declaraciones juradas, determinación de oficio, prescripción tributaria.
contable = registración y estados contables: balances, patrimonio neto, estado de resultados, normas contables, asientos, valuación de activos.
financiero = finanzas corporativas: deuda, obligaciones negociables, flujos de fondos, tasas de interés, calificaciones crediticias, emisiones.

Consulta: "{q}"

Respondé SOLO con una palabra: legal, impositivo, contable o financiero.
Dominio:"""

def rutear_llm(texto):
    msgs = [{"role": "user", "content": PLANTILLA.format(q=texto)}]
    t = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids = tok(t, return_tensors="pt")
    with torch.no_grad():
        out = mod.generate(**ids, max_new_tokens=6, do_sample=False, pad_token_id=tok.eos_token_id)
    r = tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip().lower()
    for s in SILOS:
        if s in r:
            return s
    return None

res = []
salida = SCR / "router_llm_parcial.json"
print(f"\n{'#':>4s} {'objetivo':12s} {'LLM':12s} {'coseno':12s}  consulta", flush=True)
t_ini = time.time()
for k, i in enumerate(consultas, 1):
    correcto = {silo[j] for j in np.where((fue == fue[i]) & (tit == tit[i]))[0]}
    q = np.array(X[i])
    dist = _softmax({s: _coseno(q, proto[s]) for s in SILOS}, CLASIFICADOR_TEMP)
    cos_top = max(dist, key=dist.get)
    try:
        llm_top = rutear_llm(str(tit[i]))
    except Exception as e:
        llm_top = None
    res.append({"i": int(i), "titulo": str(tit[i]), "correctos": sorted(correcto),
                "llm": llm_top, "coseno": cos_top,
                "ok_llm": llm_top in correcto, "ok_cos": cos_top in correcto})
    salida.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    ok_l = sum(r["ok_llm"] for r in res); ok_c = sum(r["ok_cos"] for r in res)
    print(f"{k:4d} {'/'.join(sorted(correcto))[:12]:12s} {str(llm_top):12s} {cos_top:12s}  "
          f"[LLM {ok_l}/{k} · cos {ok_c}/{k}]  {str(tit[i])[:40]}", flush=True)

m = len(res)
ok_l = sum(r["ok_llm"] for r in res); ok_c = sum(r["ok_cos"] for r in res)
b01 = sum(1 for r in res if r["ok_cos"] and not r["ok_llm"])
b10 = sum(1 for r in res if r["ok_llm"] and not r["ok_cos"])
from math import comb
nd = b01 + b10
p = (sum(comb(nd, k) for k in range(min(b01, b10) + 1)) / 2 ** nd * 2) if nd else 1.0
print()
print("=" * 66)
print(f"  ROUTER LLM (Qwen2.5-3B local) : {ok_l}/{m}  ({ok_l/m:.1%})")
print(f"  ROUTER COSENO (produccion)    : {ok_c}/{m}  ({ok_c/m:.1%})")
print(f"  diferencia                    : {(ok_l-ok_c)/m*100:+.1f} pp")
print(f"  McNemar: {b10} a favor del LLM · {b01} a favor del coseno · p = {min(p,1.0):.4f}")
print(f"  tiempo total: {(time.time()-t_ini)/60:.0f} min")
