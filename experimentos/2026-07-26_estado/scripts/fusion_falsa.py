"""FUSION FALSA — el experimento que mide LO QUE EL PLAN PIDE.

El plan aprobado (pag. 3) define el problema asi, textual:
  "una consulta sobre un termino como 'retencion' activara vectores provenientes de
   normativas fiscales, registros contables y contratos legales SIMULTANEAMENTE.
   Esto no solo contamina el contexto enviado al LLM, sino que exacerba [...] la
   Entrega Cognitiva (cognitive surrender)"

Y el objetivo general (pag. 12) es mitigar la ENTREGA COGNITIVA y optimizar la
TRAZABILIDAD, no mejorar el recall.

DOS CONDICIONES QUE LAS MEDICIONES ANTERIORES VIOLABAN (medido hoy):
  1. La pregunta tiene que ser AMBIGUA DE VERDAD. Con preguntas que llevan el dominio
     adentro ("agentes DEL MERCADO ELECTRICO") la mezcla es 0% con cualquier k.
  2. La k tiene que ser REALISTA. Con preguntas desnudas la mezcla del contexto de B0 es
     25% a k=3, 62% a k=5, 75% a k=8, 100% a k=20. El proyecto venia midiendo con k=3,
     que es la unica k donde el problema casi no aparece.

DISEÑO (P4: ningun brazo se degrada — misma k, mismo generador, mismo prompt):
  B0    : top-k GLOBAL           -> el contexto PUEDE traer los dos regimenes
  MULTI : top-k dentro del silo que elige el router -> NO PUEDE, por construccion

METRICA — FUSION FALSA:
  la respuesta cita normas de DOS regimenes distintos SIN distinguir que son regimenes
  distintos. Eso es exactamente "presentar como una sola verdad lo que son dos marcos
  normativos" = la entrega cognitiva del plan.
  Se mide con identificadores UNICOS de norma (no con etiquetas de silo, leccion de C.39)
  + deteccion de marcadores de distincion explicita.

Generador: Gemma 4 local (Ollama, T=0, think=False). Sin API, sin costo.
"""
import sys, io, json, re, time, urllib.request
from pathlib import Path
from math import comb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from embedder import embed_query
from clasificador import _coseno, _softmax, _centroide_l2
from config import CLASIFICADOR_TEMP

MODELO = "gemma4:latest"
OLLAMA = "http://localhost:11434/api/generate"
K = 8                 # k realista de produccion; a k=3 el fenomeno casi no aparece
SEMILLA = 7
NUM_PREDICT = 1500    # el truncamiento invalido 2 mediciones hoy: presupuesto amplio

# preguntas DESNUDAS: el termino polisemico SIN contexto que lo desambigue.
# Los terminos salieron del corpus (paso 1), no elegidos a dedo.
DESNUDAS = [
    "¿Qué obligaciones tienen los agentes?",
    "¿En qué casos corresponde una compensación?",
    "¿Cuándo queda firme una decisión?",
    "¿Qué plazos hay que cumplir?",
    "¿Qué requisitos hay que presentar?",
    "¿Qué sanciones corresponden?",
    "¿Cómo se presenta la solicitud?",
    "¿Qué pasa si hay un incumplimiento?",
    "¿Cómo se calculan los intereses?",
    "¿Qué información hay que suministrar?",
    "¿Quién puede solicitar una prórroga?",
    "¿Qué efectos tiene la notificación?",
]

REGIMEN = {
    "legal": {
        "docs": {"Ley_24065_Energia_Electrica_TO", "Ley_24076_Gas_Natural_TO",
                 "Decreto_1738_1992_Reglamentario_Gas", "Decreto_1398_1992_Reglamentario_Electrico",
                 "Res_SE_61_1992_Los_Procedimientos", "Res_SE_137_1992", "ENRE_Resolucion_544_2024"},
        "marcas": [r"24\s*\.?\s*065", r"24\s*\.?\s*076", r"\bENRE\b", r"\bENARGAS\b", r"\bCAMMESA\b",
                   r"\bMEM\b", r"mercado\s+el[eé]ctrico", r"\bOED\b", r"1\s*\.?\s*738", r"1\s*\.?\s*398",
                   r"Res(?:oluci[oó]n)?\.?\s*(?:S\.?E\.?)?\s*n?[°º]?\s*(?:61|137)\b"],
    },
    "impositivo": {
        "docs": {"Ley_11683_Procedimiento_Fiscal_TO", "Decreto_821_1998_TO_Ley_11683", "RG_AFIP_830"},
        "marcas": [r"11\s*\.?\s*683", r"\bAFIP\b", r"\bARCA\b", r"\bfisco\b",
                   r"resoluci[oó]n\s+general\s*n?[°º]?\s*830", r"r\.?\s*g\.?\s*n?[°º]?\s*830",
                   r"decreto\s*n?[°º]?\s*821", r"determinaci[oó]n\s+de\s+oficio",
                   r"declaraci[oó]n\s+jurada", r"tributar", r"impositiv"],
    },
}
# marcadores de que el sistema DISTINGUE los regimenes en vez de fusionarlos
DISTINGUE = [r"seg[uú]n\s+se\s+trate", r"dos\s+(?:reg[ií]menes|marcos|acepciones|sentidos|contextos)",
             r"por\s+un\s+lado.{0,80}por\s+otro", r"en\s+materia\s+tributaria.{0,200}en\s+materia",
             r"distinto[s]?\s+reg[ií]menes", r"depende\s+del\s+(?:contexto|[aá]mbito|r[eé]gimen)",
             r"ambig", r"no\s+queda\s+claro\s+a\s+cu[aá]l", r"puede\s+referirse\s+a"]


def cita(txt, reg):
    return any(re.search(p, txt, re.I) for p in REGIMEN[reg]["marcas"])


def distingue(txt):
    return any(re.search(p, txt, re.I) for p in DISTINGUE)


con = conectar(); cur = con.cursor()
cur.execute("SELECT id, silo, titulo, contenido, fuente, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
silo = np.array([r[1] for r in filas]); tit = np.array([r[2] for r in filas])
cont = [r[3] for r in filas]; fue = np.array([r[4] for r in filas])
X = np.array([json.loads(r[5]) for r in filas]); X = X / np.linalg.norm(X, axis=1, keepdims=True)
SIL = sorted(set(silo.tolist()))
proto = {s: np.array(_centroide_l2([X[i] for i in range(len(X)) if silo[i] == s])) for s in SIL}
print(f"corpus {len(X)} chunks · {len(DESNUDAS)} preguntas desnudas · k={K}\n", flush=True)

INSTR = """Respondé la pregunta usando EXCLUSIVAMENTE el contexto provisto.
Citá la norma y el artículo en los que fundás cada afirmación.
Si el contexto no alcanza, respondé exactamente: "No tengo evidencia suficiente para responder."
No uses conocimiento externo al contexto."""


def generar(pregunta, idxs):
    ctx = "\n\n---\n\n".join(f"[{tit[j]} - {fue[j]}]\n{cont[j]}" for j in idxs)
    cuerpo = json.dumps({
        "model": MODELO, "stream": False, "think": False,
        "prompt": f"{INSTR}\n\n### Contexto:\n{ctx}\n\n### Pregunta:\n{pregunta}\n\n### Respuesta:",
        "options": {"temperature": 0, "seed": SEMILLA, "num_predict": NUM_PREDICT},
    }).encode()
    try:
        p = urllib.request.Request(OLLAMA, data=cuerpo, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(p, timeout=1200) as r:
            d = json.loads(r.read())
        if d.get("done_reason") == "length":
            return None, "TRUNCADO"
        t = (d.get("response") or "").strip()
        return (t, "OK") if t else (None, "VACIO")
    except Exception as e:
        return None, f"ERROR:{type(e).__name__}"


res = []
print(f"{'pregunta':40s} {'sis':6s} {'ctx':6s} {'regimenes citados':22s} {'FUSION'}")
for q in DESNUDAS:
    v = np.array(embed_query(q)); v /= np.linalg.norm(v)
    s = X @ v
    dist = _softmax({x: _coseno(v, proto[x]) for x in SIL}, CLASIFICADOR_TEMP)
    top_silo = max(dist, key=dist.get)
    brazos = {
        "B0": list(np.argsort(-s)[:K]),
        "MULTI": list(np.argsort(-np.where(silo == top_silo, s, -2))[:K]),
    }
    for nom, idxs in brazos.items():
        regs_ctx = {r for j in idxs for r, d in REGIMEN.items() if fue[j] in d["docs"]}
        txt, motivo = generar(q, idxs)
        if txt is None:
            print(f"{q[:40]:40s} {nom:6s}  -- descartado ({motivo})")
            continue
        cl, ci = cita(txt, "legal"), cita(txt, "impositivo")
        dist_expl = distingue(txt)
        fusion = (cl and ci) and not dist_expl          # cita dos regimenes SIN distinguirlos
        abst = "no tengo evidencia suficiente" in txt.lower()
        res.append({"pregunta": q, "sistema": nom, "ctx_mezclado": len(regs_ctx) > 1,
                    "silo_router": top_silo, "cita_legal": cl, "cita_impositivo": ci,
                    "distingue": dist_expl, "fusion_falsa": fusion, "abstiene": abst,
                    "respuesta": txt[:1200]})
        (SCR / "fusion_falsa.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        regs = "+".join([r for r, c in (("legal", cl), ("imposit", ci)) if c]) or "-"
        print(f"{q[:40]:40s} {nom:6s} {'MEZC' if len(regs_ctx)>1 else 'limpio':6s} {regs:22s} "
              f"{'*** SI ***' if fusion else 'no'}{'  [distingue]' if dist_expl else ''}"
              f"{'  [abstuvo]' if abst else ''}", flush=True)

print("\n" + "=" * 76)
print("  FUSION FALSA = cita normas de DOS regimenes SIN distinguir que son distintos")
print("=" * 76)
for nom in ("B0", "MULTI"):
    g = [r for r in res if r["sistema"] == nom]
    if not g:
        continue
    n = len(g)
    print(f"\n  {nom}  (n={n})")
    print(f"     contexto que mezcla regimenes : {sum(r['ctx_mezclado'] for r in g)}/{n}")
    print(f"     FUSION FALSA                  : {sum(r['fusion_falsa'] for r in g)}/{n}")
    print(f"     distingue explicitamente      : {sum(r['distingue'] for r in g)}/{n}")
    print(f"     se abstuvo                    : {sum(r['abstiene'] for r in g)}/{n}")

pares = {}
for r in res:
    pares.setdefault(r["pregunta"], {})[r["sistema"]] = r
comp = [(v["MULTI"], v["B0"]) for v in pares.values() if "MULTI" in v and "B0" in v]
b10 = sum(1 for m, b in comp if b["fusion_falsa"] and not m["fusion_falsa"])   # MULTI mejor
b01 = sum(1 for m, b in comp if m["fusion_falsa"] and not b["fusion_falsa"])
nd = b10 + b01
p = min(sum(comb(nd, i) for i in range(min(b10, b01) + 1)) / 2 ** nd * 2, 1.0) if nd else 1.0
piso = min(2.0 ** (1 - nd), 1.0) if nd else 1.0
print(f"\n  McNemar sobre FUSION FALSA (n={len(comp)} pares)")
print(f"     {b10} a favor de MULTI · {b01} a favor de B0 · discordantes={nd}")
if nd == 0:
    print(f"     p = 1.0 -> EMPATE EXACTO: ningun par discordante, no hay efecto detectable")
elif piso > 0.05:
    print(f"     p = {p:.4f} -> NO CONCLUYENTE: con {nd} discordantes el minimo p es {piso:.4f} > 0.05")
else:
    print(f"     p = {p:.4f} -> {'SIGNIFICATIVO' if p < 0.05 else 'no significativo'} (piso {piso:.4f})")
print(f"\n  guardado en fusion_falsa.json")
