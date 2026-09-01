"""ROUTER GEMMA 4 (local, via Ollama) vs ROUTER COSENO — sobre 50 preguntas naturales.

POR QUE ESTE TEST ES EL QUE IMPORTA (C.74, desvio 3): el plan aprobado pide que el
orquestador sea "un modelo de lenguaje avanzado" que interpreta la INTENCION de la
consulta. Se construyo un router por coseno a prototipos (ADR A8, por determinismo).
La version del plan nunca se probo.

LO YA MEDIDO:
  · Qwen2.5-3B sobre TITULOS   : 44% vs coseno 100% (McNemar 45-0, p=5.7e-14)
    ^ instrumento desfavorable: un titulo ("CAPITULO XIV") no tiene intencion que leer
  · Qwen2.5-3B sobre PREGUNTAS : 76% vs coseno 76% (empate, n=17, 3-3 discordantes)
    ^ y el coseno NO es 100%: su 100% en titulos era fuga (el titulo salio del centroide)
  · el coseno acierta el 1er silo el 76% y tiene el correcto en el top-2 el 94%
    ^ los 4.3 pp que separan a la arquitectura de su techo son error de ruteo (C.72)

HIPOTESIS: un modelo grande sabe que "patrimonio neto" es contable y "retencion
impositiva" es fiscal — conocimiento del mundo que el vector no tiene. Es la
"informacion ortogonal" que se busco dos dias sin encontrar.

MODELO: Gemma 4 local via Ollama (temperature=0, seed fijo, sin API, sin costo).
Se usa el servidor HTTP (localhost:11434), NO el CLI: el CLI escupe spinners que
contaminan la salida y habria que adivinar donde termina el progreso.

GROUND TRUTH — declarado:
  · 20 mono-dominio: el silo del DOCUMENTO del que salio la pregunta (etiquetado_n40)
  · 30 multi-dominio: conjunto de 2 silos declarado al redactarlas (multi_n30)
  ⚠️ el multi-dominio fue etiquetado por LLM y NO lo verifico un humano todavia.

ESTADISTICA: McNemar exacto pareado. Se reporta el PISO de significancia: con nd
discordantes unanimes el minimo p bilateral es 2^(1-nd); si ese piso supera 0.05 el
test NO PUEDE concluir y se dice explicitamente (leccion de C.75).
"""
import sys, io, json, time, urllib.request
from pathlib import Path
from math import comb
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from clasificador import _coseno, _softmax, _centroide_l2
from config import CLASIFICADOR_TEMP

MODELO = "gemma4:latest"
OLLAMA = "http://localhost:11434/api/generate"
SEMILLA = 7
# Gemma 4 RAZONA antes de contestar. Con num_predict=8 gastaba el presupuesto pensando
# y devolvia cadena VACIA -> se contaba como error del modelo cuando en realidad nunca
# se lo dejo terminar. Golpeaba sobre todo a las multi-dominio (las que obligan a
# deliberar) = justo el estrato que decide la tesis. Presupuesto amplio + deteccion
# explicita de truncamiento.
NUM_PREDICT = 512
PENSAR = False        # ruta S1 (rapida). True = ruta S2 (reflexiva)
SILOS = ["legal", "impositivo", "contable", "financiero"]
DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal",
       "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable",
       "FS-31-03-2019": "contable", "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}

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
MULTI = [
 ("¿Qué efecto tiene una sanción del ente regulador sobre los estados contables de la distribuidora?", {"legal", "contable"}),
 ("¿Cómo se refleja en el estado de resultados el pago de penalidades regulatorias?", {"legal", "contable"}),
 ("¿Cómo afecta el marco regulatorio del transporte eléctrico a la valuación de los activos?", {"legal", "contable"}),
 ("¿Qué previsiones contables corresponden por incumplimientos del contrato de concesión?", {"legal", "contable"}),
 ("¿Cómo se registra el canon de concesión que exige la normativa energética?", {"legal", "contable"}),
 ("¿Qué impacto tiene el régimen tarifario regulado sobre la proyección de ingresos?", {"legal", "financiero"}),
 ("¿Cómo influye el marco regulatorio en la calificación crediticia de una transportista?", {"legal", "financiero"}),
 ("¿Qué riesgos regulatorios deben informarse a los inversores de una emisora energética?", {"legal", "financiero"}),
 ("¿Cómo afecta una resolución del ENRE al flujo de fondos de la concesionaria?", {"legal", "financiero"}),
 ("¿Qué garantías exige el marco regulatorio para el financiamiento de obras de transporte?", {"legal", "financiero"}),
 ("¿Cómo se registra contablemente el impuesto a las ganancias determinado según el régimen fiscal?", {"impositivo", "contable"}),
 ("¿Qué tratamiento contable corresponde a las previsiones por contingencias fiscales?", {"impositivo", "contable"}),
 ("¿Cómo se contabilizan las retenciones sufridas por el contribuyente?", {"impositivo", "contable"}),
 ("¿Qué asiento corresponde por el devengamiento de intereses resarcitorios impositivos?", {"impositivo", "contable"}),
 ("¿Cómo se expone en el balance el saldo a favor de impuestos?", {"impositivo", "contable"}),
 ("¿Cómo impactan las retenciones impositivas en el flujo de fondos de la compañía?", {"impositivo", "financiero"}),
 ("¿Qué obligaciones fiscales genera la emisión de una obligación negociable?", {"impositivo", "financiero"}),
 ("¿Qué impacto tiene el endeudamiento financiero en la determinación del impuesto a las ganancias?", {"impositivo", "financiero"}),
 ("¿Cómo tributan los intereses pagados a inversores del exterior?", {"impositivo", "financiero"}),
 ("¿Qué efecto fiscal tiene la colocación de deuda en el mercado de capitales?", {"impositivo", "financiero"}),
 ("¿Cómo se vincula el resultado del ejercicio con la generación de caja operativa?", {"contable", "financiero"}),
 ("¿Qué información contable sustenta el cálculo del nivel de endeudamiento?", {"contable", "financiero"}),
 ("¿Cómo se refleja la deuda financiera en el estado de situación patrimonial?", {"contable", "financiero"}),
 ("¿Qué relación hay entre las provisiones registradas y el riesgo financiero informado?", {"contable", "financiero"}),
 ("¿Cómo impactan los intereses devengados en el resultado y en el flujo de efectivo?", {"contable", "financiero"}),
 ("¿Qué régimen sancionatorio aplica al incumplimiento de obligaciones formales del sector energético?", {"legal", "impositivo"}),
 ("¿Cómo se articulan las facultades del ente regulador con las del fisco ante un mismo hecho?", {"legal", "impositivo"}),
 ("¿Qué plazos de prescripción rigen para las obligaciones regulatorias y para las fiscales?", {"legal", "impositivo"}),
 ("¿Qué tributos alcanzan a la actividad de distribución de gas natural?", {"legal", "impositivo"}),
 ("¿Cómo se recurre una determinación que involucra tanto materia regulatoria como fiscal?", {"legal", "impositivo"}),
]
CASOS = ([{"q": q, "correctos": {DOM[d]}, "tipo": "mono"} for q, d in MONO] +
         [{"q": q, "correctos": c, "tipo": "multi"} for q, c in MULTI])

# ---------- router por coseno: el MISMO mecanismo de produccion (ADR A8) ----------
con = conectar(); cur = con.cursor()
cur.execute("SELECT silo, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
silo = np.array([r[0] for r in filas])
X = np.array([json.loads(r[1]) for r in filas])
X = X / np.linalg.norm(X, axis=1, keepdims=True)
proto = {s: np.array(_centroide_l2([X[i] for i in range(len(X)) if silo[i] == s])) for s in SILOS}
print(f"corpus {len(X)} chunks · prototipos por silo listos", flush=True)

from embedder import embed_query   # la funcion DE PRODUCCION, no una reimplementacion
from config import EMBEDDING_MODEL
print(f"embedder de produccion: {EMBEDDING_MODEL}", flush=True)


def rutear_coseno(texto):
    q = np.array(embed_query(texto))
    q = q / np.linalg.norm(q)
    dist = _softmax({s: _coseno(q, proto[s]) for s in SILOS}, CLASIFICADOR_TEMP)
    return sorted(dist, key=dist.get, reverse=True), dist


# ---------- router Gemma 4 por HTTP ----------
DEFINICIONES = """legal = regulación del sector energético: ENRE, ENARGAS, CAMMESA, leyes de energía eléctrica y gas, concesiones, despacho, tarifas reguladas, sanciones del ente regulador.
impositivo = materia tributaria: AFIP/ARCA, impuestos, retenciones y percepciones fiscales, declaraciones juradas, determinación de oficio, prescripción tributaria.
contable = registración y estados contables: balances, patrimonio neto, estado de resultados, normas contables, asientos, valuación de activos.
financiero = finanzas corporativas: deuda, obligaciones negociables, flujos de fondos, tasas de interés, calificaciones crediticias, emisiones."""

P_UNO = """Sos un experto en normativa argentina. Clasificá la consulta en UNO de estos cuatro dominios:

{d}

Consulta: "{q}"

Respondé SOLO con una palabra: legal, impositivo, contable o financiero.
Dominio:"""


def rutear_gemma(texto, reintentos=2):
    """Determinista: temperature=0 + seed fijo. Devuelve el silo o None."""
    cuerpo = json.dumps({
        "model": MODELO,
        "prompt": P_UNO.format(d=DEFINICIONES, q=texto),
        "stream": False,
        "options": {"temperature": 0, "seed": SEMILLA, "num_predict": NUM_PREDICT},
        # think=False -> el modelo responde directo, sin deliberar. Medido: 14s vs 147s
        # (10x) con la MISMA respuesta correcta. Ademas es la unica config viable en
        # produccion: un router de 147s por consulta no es usable.
        # NOTA DE DISEÑO: think=True queda disponible como RUTA S2 del plan (reflexiva),
        # activada por el gate de entropia solo en la zona gris. Las dos rutas del plan
        # son el mismo modelo con este flag, no dos componentes distintos.
        "think": PENSAR,
    }).encode()
    for intento in range(reintentos + 1):
        try:
            pedido = urllib.request.Request(OLLAMA, data=cuerpo,
                                            headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(pedido, timeout=900) as resp:
                d = json.loads(resp.read())
            txt = (d.get("response") or "").strip().lower()
            if d.get("done_reason") == "length":
                # se corto por presupuesto: NO es un error del modelo, es del arnes
                return None, "TRUNCADO"
            if not txt:
                return None, "VACIO"
            # se toma la ULTIMA mencion: si razona, el veredicto viene al final
            pos = [(txt.rfind(s), s) for s in SILOS if s in txt]
            if not pos:
                return None, f"SIN_SILO:{txt[:60]}"
            return max(pos)[1], "OK"
        except Exception as e:
            if intento == reintentos:
                return None, f"ERROR:{type(e).__name__}"
            time.sleep(3)


salida = SCR / "router_gemma_parcial.json"
# REANUDABLE: la maquina se saturo a mitad de la corrida anterior (dos procesos pesados
# a la vez). Se rescatan las respuestas UTILIZABLES ya obtenidas y solo se repiten las
# que fallaron por arnes (ERROR/TRUNCADO/VACIO), que no son culpa del modelo.
res = []
if salida.exists():
    previos = json.loads(salida.read_text(encoding="utf-8"))
    hechos = {r["q"]: r for r in previos if r.get("motivo") == "OK"}
    res = [r for r in previos if r.get("motivo") == "OK"]
    print(f"[reanudar] {len(res)} respuestas validas rescatadas · "
          f"{len(previos)-len(res)} a repetir por fallo de arnes", flush=True)
else:
    hechos = {}

print(f"\nMODELO: {MODELO} (Ollama local, T=0, seed={SEMILLA}) · {len(CASOS)} preguntas", flush=True)
print(f"{'#':>3s} {'tipo':6s} {'objetivo':22s} {'GEMMA4':12s} {'coseno':12s} ok   seg", flush=True)
t_ini = time.time()
for k, c in enumerate(CASOS, 1):
    if c["q"] in hechos:
        continue
    orden_cos, dist = rutear_coseno(c["q"])
    t0 = time.time()
    g, motivo = rutear_gemma(c["q"])
    dt = time.time() - t0
    fila = {"q": c["q"], "tipo": c["tipo"], "correctos": sorted(c["correctos"]),
            "gemma": g, "motivo": motivo, "coseno": orden_cos[:2],
            "dist_cos": {s: round(dist[s], 4) for s in SILOS},
            "ok_gemma": g in c["correctos"], "ok_cos": orden_cos[0] in c["correctos"],
            "seg": round(dt, 1)}
    res.append(fila)
    salida.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    marca = ("G" if fila["ok_gemma"] else "-") + ("C" if fila["ok_cos"] else "-")
    malos = [r for r in res if r["motivo"] != "OK"]
    if len(malos) >= 5 and len(malos) / len(res) > 0.15:
        print(f"\n  ABORTADO: {len(malos)}/{len(res)} respuestas no utilizables "
              f"({Counter(r['motivo'].split(':')[0] for r in malos)}). El arnes esta fallando: "
              f"medir asi produciria un resultado invalido como el de la corrida anterior.", flush=True)
        sys.exit(1)
    og = sum(r["ok_gemma"] for r in res); oc = sum(r["ok_cos"] for r in res)
    print(f"{k:3d} {c['tipo']:6s} {'/'.join(sorted(c['correctos'])):22s} "
          f"{str(g):12s} {orden_cos[0]:12s} {marca}  {dt:5.1f}  [G {og}/{k} · C {oc}/{k}]", flush=True)


# ================= ESTADISTICA =================
def mcnemar(sub, ka, kb):
    b10 = sum(1 for r in sub if r[ka] and not r[kb])
    b01 = sum(1 for r in sub if r[kb] and not r[ka])
    nd = b10 + b01
    if nd == 0:
        return b10, b01, 0, 1.0, 1.0
    p = min(sum(comb(nd, i) for i in range(min(b10, b01) + 1)) / 2 ** nd * 2, 1.0)
    return b10, b01, nd, p, min(2.0 ** (1 - nd), 1.0)


print("\n" + "=" * 78)
print(f"  ROUTER {MODELO} vs COSENO · {len(res)} preguntas naturales")
print("=" * 78)
for nom, sub in (("mono-dominio", [r for r in res if r["tipo"] == "mono"]),
                 ("multi-dominio", [r for r in res if r["tipo"] == "multi"]),
                 ("AGRUPADO", res)):
    m = len(sub)
    if not m:
        continue
    a = sum(r["ok_gemma"] for r in sub); b = sum(r["ok_cos"] for r in sub)
    b10, b01, nd, p, piso = mcnemar(sub, "ok_gemma", "ok_cos")
    print(f"\n  {nom}  (n={m})")
    print(f"     GEMMA 4 : {a}/{m} = {a/m:.1%}")
    print(f"     coseno  : {b}/{m} = {b/m:.1%}   ({(a-b)/m*100:+.1f} pp)")
    print(f"     McNemar: {b10} pro-Gemma · {b01} pro-coseno · nd={nd}")
    if nd == 0:
        print(f"     p = 1.0 -> EMPATE EXACTO, ningun par discordante")
    elif piso > 0.05:
        print(f"     p = {p:.4f} -> NO CONCLUYENTE: con {nd} discordantes el minimo p")
        print(f"                    alcanzable es {piso:.4f} > 0.05. n insuficiente.")
    else:
        print(f"     p = {p:.4f} -> {'SIGNIFICATIVO' if p < 0.05 else 'no significativo'}"
              f" (piso con nd={nd}: {piso:.4f})")

print("\n" + "-" * 78)
print("  LO QUE DECIDE TODO: casos donde GEMMA acierta y el coseno FALLA")
print("  (= la 'informacion que los vectores no tienen'; si esto existe, hay palanca)")
gana = [r for r in res if r["ok_gemma"] and not r["ok_cos"]]
if not gana:
    print("     NINGUNO. Gemma no aporta ni un caso propio -> el ruteo no se arregla por LLM.")
for r in gana:
    print(f"     [{r['tipo']}] {r['q'][:70]}")
    print(f"        correcto={'/'.join(r['correctos'])} · gemma={r['gemma']} · "
          f"coseno={r['coseno'][0]} (p={r['dist_cos'][r['coseno'][0]]:.3f})")

print("\n  y al reves: donde el COSENO acierta y Gemma falla")
pierde = [r for r in res if r["ok_cos"] and not r["ok_gemma"]]
if not pierde:
    print("     ninguno")
for r in pierde:
    print(f"     [{r['tipo']}] {r['q'][:70]}")
    print(f"        correcto={'/'.join(r['correctos'])} · gemma={r['gemma']} · coseno={r['coseno'][0]}")

u = sum(1 for r in res if r["ok_gemma"] or r["ok_cos"])
og = sum(r["ok_gemma"] for r in res); oc = sum(r["ok_cos"] for r in res)
n = len(res)
print(f"\n  COMPLEMENTARIEDAD (el argumento para un router HIBRIDO):")
print(f"     solo coseno          : {oc}/{n} = {oc/n:.1%}")
print(f"     solo Gemma           : {og}/{n} = {og/n:.1%}")
print(f"     al menos uno acierta : {u}/{n} = {u/n:.1%}   <- techo de un hibrido perfecto")
print(f"\n  tiempo total: {(time.time()-t_ini)/60:.1f} min · "
      f"promedio {np.mean([r['seg'] for r in res]):.1f} s/pregunta")
