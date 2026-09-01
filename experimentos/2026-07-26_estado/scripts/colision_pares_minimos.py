"""COLISION SEMANTICA — PARES MINIMOS, medida en la RESPUESTA (no en el retrieval).

DISEÑO:
  Para cada termino polisemico se arma un PAR MINIMO: dos preguntas que usan la MISMA
  palabra en dos regimenes distintos, cada una anclada a un articulo real del corpus.
    A) sentido LEGAL       ("agentes del mercado electrico")
    B) sentido IMPOSITIVO  ("agentes de retencion")
  Control interno perfecto: las dos preguntas comparten el termino y difieren solo en
  el regimen.

  Dos sistemas, MISMO k y MISMO generador (P4: ninguno se degrada):
    B0    = top-k global (puede mezclar los dos sentidos en el contexto)
    MULTI = top-k dentro del silo del sentido pedido (no puede mezclar por construccion)

METRICA (esta es la que importa, y ninguna de las 6 mediciones anteriores la miro):
  CONFUSION DE SENTIDO = la respuesta cita una norma del OTRO regimen.
  Se detecta por IDENTIFICADOR UNICO de norma (24.065, 11.683, RG 830, CAMMESA, ENRE...),
  NO por etiqueta de silo — la leccion de C.39 y C.75.

Generador: Gemma 4 local (Ollama, T=0, gratis). Sin API.
"""
import sys, io, json, re, time, urllib.request
from pathlib import Path
from math import comb
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from embedder import embed_query

MODELO = "gemma4:latest"
OLLAMA = "http://localhost:11434/api/generate"
K = 3
SEMILLA = 7

# --- identificadores UNICOS por REGIMEN (no por silo): asi se detecta la confusion ---
REGIMEN = {
    "legal": {
        "docs": {"Ley_24065_Energia_Electrica_TO", "Ley_24076_Gas_Natural_TO",
                 "Decreto_1738_1992_Reglamentario_Gas", "Decreto_1398_1992_Reglamentario_Electrico",
                 "Res_SE_61_1992_Los_Procedimientos", "Res_SE_137_1992", "ENRE_Resolucion_544_2024"},
        "marcas": [r"24\s*\.?\s*065", r"24\s*\.?\s*076", r"\bENRE\b", r"\bENARGAS\b",
                   r"\bCAMMESA\b", r"\bMEM\b", r"mercado\s+el[eé]ctrico\s+mayorista",
                   r"\bOED\b", r"1\s*\.?\s*738", r"1\s*\.?\s*398"],
    },
    "impositivo": {
        "docs": {"Ley_11683_Procedimiento_Fiscal_TO", "Decreto_821_1998_TO_Ley_11683", "RG_AFIP_830"},
        "marcas": [r"11\s*\.?\s*683", r"\bAFIP\b", r"\bARCA\b",
                   r"resoluci[oó]n\s+general\s*n?[°º]?\s*830", r"r\.?\s*g\.?\s*n?[°º]?\s*830",
                   r"decreto\s*n?[°º]?\s*821", r"determinaci[oó]n\s+de\s+oficio",
                   r"declaraci[oó]n\s+jurada"],
    },
}


def cita(txt, reg):
    return any(re.search(p, txt, re.I) for p in REGIMEN[reg]["marcas"])


# ---------------- PARES MINIMOS anclados al corpus ----------------
# Cada entrada: termino, y para cada regimen la pregunta + el documento donde vive
# la evidencia. Las preguntas usan el MISMO termino y difieren solo en el regimen.
PARES = [
    ("agentes",
     ("legal", "¿Qué sujetos revisten la condición de agentes del mercado eléctrico mayorista y qué deben cumplir para operar?"),
     ("impositivo", "¿Quién determina qué sujetos deben actuar como agentes de retención y en qué operaciones?")),
    ("firme",
     ("legal", "¿Qué implica que una autorización de exportación sea firme para su titular?"),
     ("impositivo", "¿Cuándo queda firme una determinación practicada de oficio por el fisco?")),
    ("compensación",
     ("legal", "¿En qué casos un generador debe pagar una compensación por incumplir su compromiso de reserva?"),
     ("impositivo", "¿Cómo se compensan de oficio los saldos acreedores de un contribuyente?")),
    ("intereses",
     ("impositivo", "¿Cómo se calculan los intereses que corresponden por el pago fuera de término de un tributo?"),
     ("financiero", "¿Cómo se determinan los intereses que devenga una obligación negociable?")),
    ("plazos",
     ("legal", "¿Cómo se computan los plazos para que el transportista cumpla sus obligaciones ante el ente regulador?"),
     ("impositivo", "¿Cómo se computan los plazos establecidos en días para los deberes del contribuyente?")),
    ("requisitos",
     ("legal", "¿Qué requisitos debe cumplir quien pretende obtener una concesión de transporte o distribución?"),
     ("impositivo", "¿Qué requisitos debe cumplir el contribuyente para constituir su domicilio fiscal electrónico?")),
    ("sanciones",
     ("legal", "¿Qué sanciones puede aplicar el ente regulador ante el incumplimiento del marco regulatorio?"),
     ("impositivo", "¿Qué sanciones corresponden por la falta de presentación de la declaración jurada?")),
    ("solicitud",
     ("legal", "¿Qué debe contener la solicitud para ser reconocido como agente del mercado?"),
     ("impositivo", "¿Qué debe contener la solicitud de devolución de un saldo a favor?")),
    ("presentación",
     ("legal", "¿Qué información debe presentar el generador ante el organismo despachante?"),
     ("impositivo", "¿Qué efectos tiene la presentación de la declaración jurada original omitida?")),
    ("actualización",
     ("impositivo", "¿Cómo se actualizan los montos de las multas previstas en el régimen fiscal?"),
     ("contable", "¿Cómo se actualizan los valores de los bienes en los estados contables?")),
]

# ---------------- corpus ----------------
con = conectar(); cur = con.cursor()
cur.execute("SELECT id, silo, titulo, contenido, fuente, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
ids = np.array([r[0] for r in filas]); silo = np.array([r[1] for r in filas])
tit = np.array([r[2] for r in filas]); cont = [r[3] for r in filas]
fue = np.array([r[4] for r in filas])
X = np.array([json.loads(r[5]) for r in filas]); X = X / np.linalg.norm(X, axis=1, keepdims=True)
print(f"corpus {len(X)} chunks · {len(PARES)} pares minimos = {2*len(PARES)} preguntas\n", flush=True)

INSTR = """Respondé la pregunta usando EXCLUSIVAMENTE el contexto provisto.
Citá la norma y el artículo en los que fundás cada afirmación.
Si el contexto no alcanza, respondé exactamente: "No tengo evidencia suficiente para responder."
No uses conocimiento externo al contexto."""


def generar(pregunta, idxs):
    ctx = "\n\n---\n\n".join(f"[{tit[j]} - {fue[j]}]\n{cont[j]}" for j in idxs)
    cuerpo = json.dumps({
        "model": MODELO, "stream": False, "think": False,
        "prompt": f"{INSTR}\n\n### Contexto:\n{ctx}\n\n### Pregunta:\n{pregunta}\n\n### Respuesta:",
        # 400 tokens truncaba las respuestas de B0 (mas variadas -> mas largas) y NO las
        # de MULTI: sesgo sistematico a favor del brazo propio. Tercera vez que el
        # truncamiento contamina una medicion en esta sesion. Presupuesto amplio + el
        # motivo de corte se registra y se descarta el item si no cerro.
        "options": {"temperature": 0, "seed": SEMILLA, "num_predict": 1500},
    }).encode()
    try:
        p = urllib.request.Request(OLLAMA, data=cuerpo, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(p, timeout=900) as r:
            d = json.loads(r.read())
        return (d.get("response") or "").strip(), d.get("done_reason")
    except Exception as e:
        return None, f"ERROR:{type(e).__name__}"


res = []
print(f"{'termino':15s} {'regimen':11s} {'sis':5s} {'ctx mezclado':13s} {'cita propio':12s} {'CITA INTRUSO'}")
for termino, a, b in PARES:
    for regimen, q in (a, b):
        otro = b[0] if regimen == a[0] else a[0]
        v = np.array(embed_query(q)); v /= np.linalg.norm(v)
        s = X @ v
        arms = {
            "B0": list(np.argsort(-s)[:K]),
            "MULTI": list(np.argsort(-np.where(silo == regimen, s, -2))[:K]),
        }
        for nom, idxs in arms.items():
            # ¿el contexto entregado mezcla los dos regimenes?
            regs = {r for j in idxs for r, d in REGIMEN.items() if fue[j] in d["docs"]}
            mezclado = len(regs) > 1
            r_txt, motivo = generar(q, idxs)
            if r_txt is None or motivo == "length":
                print(f"{termino:15s} {regimen:11s} {nom:5s}  -- respuesta no utilizable ({motivo})")
                continue
            propio = cita(r_txt, regimen) if regimen in REGIMEN else None
            intruso = cita(r_txt, otro) if otro in REGIMEN else None
            abst = "no tengo evidencia suficiente" in r_txt.lower()
            res.append({"termino": termino, "regimen": regimen, "otro": otro, "sistema": nom,
                        "pregunta": q, "ctx_mezclado": mezclado, "cita_propio": bool(propio),
                        "cita_intruso": bool(intruso), "abstiene": abst,
                        "respuesta": r_txt[:900]})
            (SCR / "colision_pares_minimos.json").write_text(
                json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{termino:15s} {regimen:11s} {nom:5s} {'SI' if mezclado else 'no':13s} "
                  f"{'SI' if propio else 'no':12s} {'*** SI ***' if intruso else 'no'}"
                  f"{'  [abstuvo]' if abst else ''}")

# ================= RESULTADOS =================
print("\n" + "=" * 80)
print("  CONFUSION DE SENTIDO — la respuesta cita una norma del OTRO regimen")
print("=" * 80)
for nom in ("B0", "MULTI"):
    g = [r for r in res if r["sistema"] == nom]
    if not g:
        continue
    n = len(g)
    print(f"\n  {nom}  (n={n})")
    print(f"     contexto que MEZCLA los dos regimenes : {sum(r['ctx_mezclado'] for r in g)}/{n}")
    print(f"     cita el regimen CORRECTO              : {sum(r['cita_propio'] for r in g)}/{n}")
    print(f"     CITA EL REGIMEN INTRUSO               : {sum(r['cita_intruso'] for r in g)}/{n}")
    print(f"     se abstuvo                            : {sum(r['abstiene'] for r in g)}/{n}")

# McNemar pareado sobre la MISMA pregunta
pares_q = {}
for r in res:
    pares_q.setdefault((r["termino"], r["regimen"]), {})[r["sistema"]] = r
comp = [(v["MULTI"], v["B0"]) for v in pares_q.values() if "MULTI" in v and "B0" in v]
for campo, etiqueta in (("cita_intruso", "CONFUSION DE SENTIDO (menos es mejor)"),
                        ("cita_propio", "cita el regimen correcto (mas es mejor)")):
    if campo == "cita_intruso":
        b10 = sum(1 for m, b in comp if b[campo] and not m[campo])   # MULTI mejor
        b01 = sum(1 for m, b in comp if m[campo] and not b[campo])
    else:
        b10 = sum(1 for m, b in comp if m[campo] and not b[campo])
        b01 = sum(1 for m, b in comp if b[campo] and not m[campo])
    nd = b10 + b01
    p = min(sum(comb(nd, i) for i in range(min(b10, b01) + 1)) / 2 ** nd * 2, 1.0) if nd else 1.0
    piso = min(2.0 ** (1 - nd), 1.0) if nd else 1.0
    print(f"\n  {etiqueta}  (n={len(comp)} pares)")
    print(f"     McNemar: {b10} pro-MULTI · {b01} pro-B0 · nd={nd} · p={p:.4f}", end="")
    print(f"   [piso {piso:.4f} -> NO CONCLUYENTE]" if nd and piso > 0.05 else "")

print(f"\n  guardado en colision_pares_minimos.json")
