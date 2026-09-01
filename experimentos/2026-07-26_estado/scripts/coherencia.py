"""IDEA 6 DE LUCAS — INVERSION: buscar global primero, usar los silos DESPUES para juzgar.

Mecanismo (retrieve-then-govern):
  1. Busqueda GLOBAL top-N (sin filtro de silo) -> no hay error de ruteo posible.
  2. CONSENSO: los silos que acumulan >= gamma del peso de la evidencia (peso = similitud).
  3. PODA: se eliminan del resultado los chunks de silos fuera del consenso (intrusos).
  4. RELLENO: se completa k con los siguientes coherentes del pool.
  (variante NO-REGRET: el mejor global NUNCA se poda.)

Hipotesis: al podar un intruso del top-3, el chunk correcto que estaba 4to ENTRA
-> unica via vista hasta ahora para superar a B0 en recall Y limpieza a la vez.
"""
import sys, io, random
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from embedder import embed_query

DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}
K, N, GAMMA = 3, 10, 0.70
con = conectar()
cur = con.cursor()
cur.execute("SELECT DISTINCT fuente, titulo FROM chunks WHERE LENGTH(titulo) BETWEEN 15 AND 70")
todo = [(f, t) for f, t in cur.fetchall() if f in DOM]
random.seed(7)
por_dom = {}
for f, t in todo:
    por_dom.setdefault(DOM[f], []).append((f, t))
consultas = []
for d, l in por_dom.items():
    consultas += [(f, t, d) for f, t in random.sample(l, min(40, len(l)))]

BR = ["B0 monolitico", "COHERENCIA (idea 6)", "COHERENCIA no-regret", "ORACULO (ref)"]
hit = {b: 0 for b in BR}
cont = {b: [] for b in BR}
rescatadas, perdidas = 0, 0   # vs B0, para la variante no-regret

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    uids = {u for u, _ in origen}
    silos_reales = list({s for _, s in origen})
    q = embed_query(t)
    vec = "[" + ",".join(map(str, q)) + "]"

    cur.execute("SELECT chunk_uid, fuente, silo, 1 - (embedding <=> %s::vector) FROM chunks "
                "ORDER BY embedding <=> %s::vector LIMIT %s", (vec, vec, N))
    pool = cur.fetchall()                      # global top-N, ordenado

    # consenso: silos por peso de evidencia (similitud), hasta gamma
    peso = {}
    for _, _, s, sim in pool:
        peso[s] = peso.get(s, 0.0) + max(sim, 0.0)
    total = sum(peso.values()) or 1.0
    consenso, acum = set(), 0.0
    for s in sorted(peso, key=peso.get, reverse=True):
        consenso.add(s)
        acum += peso[s] / total
        if acum >= GAMMA:
            break

    b0 = pool[:K]
    coherentes = [c for c in pool if c[2] in consenso]
    plan_coh = coherentes[:K] if len(coherentes) >= K else (coherentes + [c for c in pool if c[2] not in consenso])[:K]
    # no-regret: el mejor global SIEMPRE queda
    nr = [pool[0]] + [c for c in coherentes if c[0] != pool[0][0]]
    plan_nr = nr[:K] if len(nr) >= K else (nr + [c for c in pool if c not in nr])[:K]

    cur.execute("SELECT chunk_uid, fuente, silo, 1 - (embedding <=> %s::vector) FROM chunks "
                "WHERE silo = ANY(%s) ORDER BY embedding <=> %s::vector LIMIT %s",
                (vec, silos_reales, vec, K))
    oraculo = cur.fetchall()

    planes = {"B0 monolitico": b0, "COHERENCIA (idea 6)": plan_coh,
              "COHERENCIA no-regret": plan_nr, "ORACULO (ref)": oraculo}
    for b, r in planes.items():
        hit[b] += bool(uids & {x[0] for x in r})
        cont[b].append(sum(1 for x in r if DOM.get(x[1]) != dom) / max(len(r), 1))

    h_b0 = bool(uids & {x[0] for x in b0})
    h_nr = bool(uids & {x[0] for x in plan_nr})
    rescatadas += (h_nr and not h_b0)
    perdidas += (h_b0 and not h_nr)

con.close()
n = len(consultas)
print(f"IDEA 6 — buscar global, juzgar con los silos DESPUES  ·  {n} consultas  ·  k={K}, pool={N}, gamma={GAMMA}")
print()
print(f"  {'sistema':24s} {'encuentra':>10s} {'sucio':>8s}")
for b in BR:
    marca = ""
    if b != "B0 monolitico" and hit[b] > hit["B0 monolitico"]:
        marca = "  <-- SUPERA A B0"
    print(f"  {b:24s} {hit[b]/n:9.1%} {np.mean(cont[b]):7.1%}{marca}")
print()
print(f"  variante no-regret vs B0: rescatadas {rescatadas} · perdidas {perdidas}")
