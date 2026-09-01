"""EL EXPERIMENTO DE LA TESIS: ¿el contexto mezclado produce FUSION FALSA?

Preguntas TRAMPA: el corpus tiene las DOS piezas por separado, pero NO la respuesta.
Ej: "plazo de prescripcion de las sanciones del ENRE" -> hay prescripcion FISCAL (11.683)
y sanciones del ENRE (24.065), pero NO el plazo de prescripcion de sanciones del ENRE.

HIPOTESIS: B0 recupera las dos y las FUSIONA (aplica el plazo fiscal al regimen electrico)
= la infraccion. El segregado, dentro de un silo, no tiene con que fusionar -> se abstiene
o responde solo lo sostenido.

Es la colision semantica produciendo dano medible. Es el §2.1 de la tesis, en vivo.
"""
import sys, io, json, time, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from embedder import embed_query
from clasificador import _coseno, _softmax, _centroide_l2
from config import CLASIFICADOR_TEMP
from generador import generar_respuesta

SILOS = ["legal", "impositivo", "contable", "financiero"]
K, GAMMA = 3, 0.70
DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}

# (pregunta trampa, dominio al que PERTENECE, patron que delata la FUSION indebida)
TRAMPAS = [
    ("¿En qué plazo prescriben las sanciones que aplica el ENRE a una distribuidora eléctrica?",
     "legal", r"11\.?683|cinco \(?5\)? años|prescripción de impuestos|fisco"),
    ("¿Qué intereses resarcitorios corresponden por el pago fuera de término de la tasa de fiscalización del ENRE?",
     "legal", r"11\.?683|art[íi]culo 37|resarcitorios.*fisco|AFIP"),
    ("¿Cuál es el procedimiento de determinación de oficio que aplica el ENRE ante un incumplimiento?",
     "legal", r"11\.?683|determinación de oficio.*fisc|vista al contribuyente"),
    ("¿Qué régimen de retención se aplica sobre los pagos que realiza CAMMESA a los generadores?",
     "legal", r"RG.*830|830/2000|beneficiario del exterior"),
    ("¿Cuál es la multa por no presentar en término la declaración jurada ante el ENRE?",
     "legal", r"11\.?683|art[íi]culo 38|declaración jurada.*fisc|clausura"),
    ("¿Qué plazo tiene el contribuyente para apelar una sanción del ENARGAS ante el Tribunal Fiscal?",
     "legal", r"tribunal fiscal|11\.?683|apelación.*tribunal fiscal"),
    ("¿Cómo se computa la prescripción de la acción para reclamar el canon de transporte eléctrico?",
     "legal", r"11\.?683|prescripción de impuestos|acción del fisco"),
    ("¿Qué alícuota de IVA se aplica a las penalidades que cobra el ENRE?",
     "legal", r"IVA|al[íi]cuota.*21|impuesto al valor agregado"),
]

con = conectar(); cur = con.cursor()
cur.execute("SELECT silo, embedding::text FROM chunks")
E = {}
for s, v in cur.fetchall():
    E.setdefault(s, []).append(np.array(json.loads(v)))
proto = {s: np.array(_centroide_l2(v)) for s, v in E.items()}

def abst(r):
    return r.strip().lower().startswith("no tengo evidencia suficiente")

filas = []
print("¿EL CONTEXTO MEZCLADO PRODUCE FUSION FALSA? (preguntas trampa)")
print("el corpus tiene las dos piezas por separado, NO la respuesta")
print()
for i, (preg, dom, pat_fusion) in enumerate(TRAMPAS, 1):
    q = np.array(embed_query(preg))
    vec = "[" + ",".join(map(str, q.tolist())) + "]"
    cur.execute("SELECT titulo, contenido, fuente, silo FROM chunks "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (vec, K))
    b0 = [{"titulo": a, "contenido": b, "fuente": c, "silo": d} for a, b, c, d in cur.fetchall()]
    dist = _softmax({s: _coseno(q, p) for s, p in proto.items()}, CLASIFICADOR_TEMP)
    mejor = {}
    for s in SILOS:
        cur.execute("SELECT 1 - (embedding <=> %s::vector) FROM chunks WHERE silo = %s "
                    "ORDER BY embedding <=> %s::vector LIMIT 1", (vec, s, vec))
        r = cur.fetchone(); mejor[s] = float(r[0]) if r else 0.0
    comb = {s: dist[s] * max(mejor[s], 1e-6) for s in SILOS}
    tot = sum(comb.values()); p = {s: comb[s] / tot for s in SILOS}
    sel, acum = [], 0.0
    for s in sorted(p, key=p.get, reverse=True):
        sel.append(s); acum += p[s]
        if acum >= GAMMA:
            break
    cur.execute("SELECT titulo, contenido, fuente, silo FROM chunks WHERE silo = ANY(%s) "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (sel, vec, K))
    seg = [{"titulo": a, "contenido": b, "fuente": c, "silo": d} for a, b, c, d in cur.fetchall()]

    # ¿el contexto de cada uno MEZCLA dominios de documento?
    dom_b0 = {DOM.get(x["fuente"]) for x in b0}
    dom_seg = {DOM.get(x["fuente"]) for x in seg}
    r_b0 = generar_respuesta(preg, b0); time.sleep(0.3)
    r_seg = generar_respuesta(preg, seg); time.sleep(0.3)
    f_b0 = bool(re.search(pat_fusion, r_b0, re.I)) and not abst(r_b0)
    f_seg = bool(re.search(pat_fusion, r_seg, re.I)) and not abst(r_seg)
    filas.append({"pregunta": preg, "dom_ctx_b0": sorted(d for d in dom_b0 if d),
                  "dom_ctx_seg": sorted(d for d in dom_seg if d), "silos_seg": sel,
                  "abst_b0": abst(r_b0), "abst_seg": abst(r_seg),
                  "fusion_b0": f_b0, "fusion_seg": f_seg, "resp_b0": r_b0, "resp_seg": r_seg})
    print(f"[{i}/8] {preg[:60]}...")
    print(f"      B0  ctx de dominios={sorted(d for d in dom_b0 if d)}  "
          f"{'ABSTIENE' if abst(r_b0) else 'responde'}  {'*** FUSION INDEBIDA ***' if f_b0 else ''}")
    print(f"      SEG silos={sel} ctx={sorted(d for d in dom_seg if d)}  "
          f"{'ABSTIENE' if abst(r_seg) else 'responde'}  {'*** FUSION INDEBIDA ***' if f_seg else ''}")
    print()
con.close()
n = len(filas)
out = Path(str(Path(__file__).resolve().parent.parent / "resultados") + r"\fusion_resultados.json")
out.write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")
print("=" * 74)
print(f"  {'':28s} {'abstiene (ok)':>15s} {'FUSION INDEBIDA':>17s}")
print(f"  {'B0 monolitico':28s} {sum(f['abst_b0'] for f in filas)}/{n}{'':11s} {sum(f['fusion_b0'] for f in filas)}/{n}")
print(f"  {'SEGREGADO':28s} {sum(f['abst_seg'] for f in filas)}/{n}{'':11s} {sum(f['fusion_seg'] for f in filas)}/{n}")
print()
print(f"  contexto de B0 mezclo dominios en: {sum(1 for f in filas if len(f['dom_ctx_b0'])>1)}/{n} casos")
print(f"  contexto SEG mezclo dominios en  : {sum(1 for f in filas if len(f['dom_ctx_seg'])>1)}/{n} casos")
