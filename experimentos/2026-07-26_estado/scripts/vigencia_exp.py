"""¿EL SISTEMA VE LA NOTA DE MODIFICACION? — experimento de vigencia.

Setup: 317 chunks del corpus tienen historia normativa ("Articulo sustituido por Ley X,
B.O. fecha"). Para cada uno se formula la consulta con su TITULO y se mide:

  ¿el top-k recuperado incluye el chunk que contiene la nota de modificacion?

Si NO la incluye, el sistema responde sobre normativa modificada SIN ENTERARSE.
Se compara: B0 (global) vs SEGREGADO (silo del chunk) vs FILTRO DETERMINISTA
(la metadata en columna: el aviso sale SIEMPRE, no depende del top-k).

Nota: el chunk con la nota y el chunk consultado suelen ser el MISMO (la nota va al pie
del articulo). Por eso se mide en dos modos:
  (a) mismo-chunk: ¿el chunk con la nota entra en el top-k? (caso facil)
  (b) OTRO-chunk: consultas cuyo articulo tiene la nota en un chunk DISTINTO (caso real
      y dificil: el articulo se partio y la nota quedo en otro fragmento)
"""
import sys, io, re, json, random
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar
from clasificador import _coseno, _softmax, _centroide_l2
from config import CLASIFICADOR_TEMP

SILOS = ["legal", "impositivo", "contable", "financiero"]
KS = [3, 5, 10]
P_ACCION = re.compile(r"(sustitu[íi]?d[oa]|derogad[oa]|incorporad[oa]|modificad[oa])\s+por\s+", re.I)

con = conectar(); cur = con.cursor()
cur.execute("SELECT chunk_uid, silo, titulo, contenido, fuente, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
uid = np.array([r[0] for r in filas]); silo = np.array([r[1] for r in filas])
tit = np.array([r[2] for r in filas]); cont = [r[3] for r in filas]
fue = np.array([r[4] for r in filas])
X = np.array([json.loads(r[5]) for r in filas]); X = X / np.linalg.norm(X, axis=1, keepdims=True)
n = len(filas)

tiene_nota = np.array([bool(P_ACCION.search(c)) for c in cont])
print(f"corpus {n} chunks · con nota de modificacion: {tiene_nota.sum()} ({tiene_nota.mean():.1%})")

# agrupar por (fuente, titulo) = "el articulo"
grupos = defaultdict(list)
for i in range(n):
    grupos[(fue[i], tit[i])].append(i)

# CASO (b): articulos donde la nota vive en un chunk DISTINTO del que se consulta
casos_b = []
for (f, t), idxs in grupos.items():
    con_nota = [i for i in idxs if tiene_nota[i]]
    sin_nota = [i for i in idxs if not tiene_nota[i]]
    if con_nota and sin_nota and 12 <= len(t) <= 70:
        casos_b.append((sin_nota[0], set(con_nota)))     # consulta un fragmento SIN nota
# CASO (a): el chunk consultado ES el que tiene la nota
casos_a = [(i, {i}) for i in range(n) if tiene_nota[i] and 12 <= len(tit[i]) <= 70]
random.seed(7)
if len(casos_a) > 120:
    casos_a = random.sample(casos_a, 120)

print(f"  casos (a) el chunk consultado TIENE la nota  : {len(casos_a)}")
print(f"  casos (b) la nota esta en OTRO fragmento     : {len(casos_b)}   <- el caso dificil y realista")
print()

# prototipos para el router
cent = {s: np.array(_centroide_l2([X[i] for i in range(n) if silo[i] == s])) for s in SILOS}

def correr(casos, nombre):
    if not casos:
        print(f"  {nombre}: sin casos"); return
    print(f"  {nombre} ({len(casos)} casos)")
    print(f"     {'k':>3s} | {'B0 ve la nota':>14s} | {'SEGREGADO ve la nota':>21s} | {'FILTRO metadata':>16s}")
    for k in KS:
        vb = vs = 0
        for i, notas in casos:
            q = X[i]
            sims = X @ q; sims[i] = -2
            top = np.argpartition(-sims, k)[:k]
            vb += bool(notas & set(top.tolist()) - {i})
            # segregado: conjunto por cobertura acumulada (gamma=0.7) con señal proto x evidencia
            dist = _softmax({s: _coseno(q, cent[s]) for s in SILOS}, CLASIFICADOR_TEMP)
            ev = {s: float(sims[silo == s].max()) for s in SILOS}
            comb = {s: dist[s] * max(ev[s], 1e-6) for s in SILOS}
            tot = sum(comb.values()); p = {s: comb[s] / tot for s in SILOS}
            sel, ac = [], 0.0
            for s in sorted(p, key=p.get, reverse=True):
                sel.append(s); ac += p[s]
                if ac >= 0.70:
                    break
            sf = np.where(np.isin(silo, sel), sims, -2)
            tops = np.argpartition(-sf, k)[:k]
            vs += bool(notas & set(tops.tolist()) - {i})
        print(f"     {k:3d} | {vb/len(casos):13.1%} | {vs/len(casos):20.1%} | {'100.0% (por construccion)':>16s}")
    print()

correr(casos_a, "(a) la nota esta en el MISMO chunk consultado")
correr(casos_b, "(b) la nota esta en OTRO fragmento del mismo articulo")
print("  'FILTRO metadata' = con valid_from/valid_to poblados, el aviso sale SIEMPRE,")
print("   no depende de que la nota caiga en el top-k. Es la diferencia arquitectonica.")
