"""EL EXPERIMENTO QUE FALTA: colision contable⚔financiero con preguntas PARAFRASEADAS.

Todo lo medido el 24-25/jul uso los TITULOS LITERALES como consulta -> la busqueda global
los encuentra trivialmente -> cancha favorable a B0. Este experimento corrige eso:

  1. Se eligen chunks de la ZONA DE COLISION: chunks cuyos vecinos abarcan contable Y
     financiero (los que realmente se pisan; pureza medida del silo contable: 69%).
  2. Un LLM redacta una pregunta profesional que ESE chunk responde, con PROHIBICION
     EXPLICITA de reusar su vocabulario distintivo (regla anti-fuga de PROTOCOLO_GOLDEN).
  3. Se mide si el chunk de origen aparece en el top-3: B0 global vs filtrado al silo.

Es, de hecho, el MINI-GOLDEN del estrato de colision. Instrumento nuevo, no el silver.
"""
import sys, io, json, re, time, random
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from embedder import embed_query
from llm import llamar_llm

N_CASOS = 30
K = 3
PAR = ("contable", "financiero")

con = conectar(); cur = con.cursor()
cur.execute("SELECT chunk_uid, silo, titulo, contenido, fuente, embedding::text FROM chunks")
filas = cur.fetchall()
uid = np.array([r[0] for r in filas]); silo = np.array([r[1] for r in filas])
tit = [r[2] for r in filas]; cont = [r[3] for r in filas]; fue = np.array([r[4] for r in filas])
X = np.array([json.loads(r[5]) for r in filas]); X = X / np.linalg.norm(X, axis=1, keepdims=True)
n = len(filas)

# --- 1. zona de colision: chunks del par cuyos vecinos abarcan AMBOS silos del par ---
cands = []
for i in range(n):
    if silo[i] not in PAR or len(cont[i]) < 400:
        continue
    sims = X @ X[i]; sims[i] = -2
    vec = np.argpartition(-sims, 12)[:12]
    ss = set(silo[vec])
    if PAR[0] in ss and PAR[1] in ss:          # vecindario mezclado = colision real
        mezcla = min(sum(silo[vec] == PAR[0]), sum(silo[vec] == PAR[1]))
        cands.append((mezcla, i))
cands.sort(reverse=True)
random.seed(11)
elegidos = [i for _, i in cands[:120]]
random.shuffle(elegidos)
elegidos = elegidos[:N_CASOS]
print(f"zona de colision {PAR[0]}⚔{PAR[1]}: {len(cands)} chunks candidatos · se usan {len(elegidos)}")
print()

PROMPT = """Sos un profesional del sector energético argentino. Leé el siguiente fragmento de un documento y escribí UNA pregunta profesional que ese fragmento responda.

REGLAS ESTRICTAS:
- La pregunta NO debe reutilizar las palabras distintivas del fragmento (títulos, rubros, nombres propios de cuentas). Usá sinónimos y lenguaje de consulta profesional.
- Debe sonar a una consulta real de un contador o analista, no a un título de sección.
- Una sola oración, entre 10 y 25 palabras.
- Devolvé SOLO la pregunta, sin comillas ni explicaciones.

FRAGMENTO:
{texto}

PREGUNTA:"""

def solape_lexico(preg, texto):
    """fraccion de palabras (>4 letras) de la pregunta que aparecen en el fragmento"""
    pw = {w.lower() for w in re.findall(r"\w{5,}", preg)}
    tw = {w.lower() for w in re.findall(r"\w{5,}", texto)}
    return len(pw & tw) / max(len(pw), 1)

print("generando preguntas parafraseadas (1 llamada por caso)...")
casos = []
for j, i in enumerate(elegidos, 1):
    try:
        preg = llamar_llm(PROMPT.format(texto=cont[i][:1200])).strip().split("\n")[0].strip(' "')
    except Exception as e:
        continue
    if len(preg) < 20:
        continue
    casos.append({"i": i, "preg": preg, "solape": solape_lexico(preg, cont[i])})
    time.sleep(0.25)
    if j % 10 == 0:
        print(f"  {j}/{len(elegidos)}", flush=True)
print(f"  generadas: {len(casos)}")
print(f"  solape léxico medio con el fragmento: {np.mean([c['solape'] for c in casos]):.1%}  "
      f"(cuanto MENOR, menos fuga)")
print()

# --- 3. medir ---
hit_b0 = hit_silo = 0
b01 = b10 = 0
detalle = []
for c in casos:
    i = c["i"]
    q = np.array(embed_query(c["preg"])); q /= np.linalg.norm(q)
    sims = X @ q
    top = np.argpartition(-sims, K)[:K]
    a = i in set(top.tolist())
    mask = silo == silo[i]
    sf = np.where(mask, sims, -2)
    tops = np.argpartition(-sf, K)[:K]
    b = i in set(tops.tolist())
    hit_b0 += a; hit_silo += b
    b01 += (a and not b); b10 += (b and not a)
    detalle.append((c["preg"][:60], silo[i], a, b))
con.close()

m = len(casos)
from math import comb
nd = b01 + b10
p = (sum(comb(nd, k) for k in range(min(b01, b10) + 1)) / 2 ** nd * 2) if nd else 1.0
print("=" * 70)
print(f"COLISION {PAR[0]}⚔{PAR[1]} · preguntas PARAFRASEADAS · n={m} · recall@{K} del chunk de origen")
print()
print(f"  B0 monolitico        : {hit_b0}/{m}  ({hit_b0/m:.1%})")
print(f"  filtrado al SILO     : {hit_silo}/{m}  ({hit_silo/m:.1%})")
print(f"  diferencia           : {(hit_silo-hit_b0)/m*100:+.1f} pp")
print()
print(f"  McNemar exacto: {b10} a favor del silo · {b01} a favor de B0 · discordantes={nd}")
print(f"  p = {min(p,1.0):.4f}  ->  {'SIGNIFICATIVO' if p < 0.05 else 'no significativo'}")
print()
print("  casos donde SOLO el silo lo encontro (los que B0 pierde por colision):")
for pr, s, a, b in detalle:
    if b and not a:
        print(f"     [{s}] \"{pr}...\"")
