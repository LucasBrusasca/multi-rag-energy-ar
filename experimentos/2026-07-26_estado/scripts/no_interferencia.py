"""NO-INTERFERENCIA ENTRE DOMINIOS — la ventaja ESTRUCTURAL que ninguna medicion refuto.

EL ARGUMENTO (demostrable por teoria de conjuntos, no por afinado):
  En un indice UNICO, el top-k de una consulta es un argmax sobre TODO el corpus. Cada
  vector nuevo que se agrega compite por el top-k de TODA consulta. Entonces cargar
  documentos de un dominio PUEDE degradar consultas de otro dominio, sin haber tocado
  nada de ese otro dominio.
  En indices PARCIALES por silo (ADR A1, ya construido), el indice del silo legal no
  cambia cuando entran documentos impositivos. La invariancia es por construccion:
  el conjunto de candidatos de una consulta ruteada a `legal` es exactamente el mismo
  antes y despues.

POR QUE NINGUNA DE LAS 8 MEDICIONES NEGATIVAS LO TOCA:
  las 8 midieron el sistema ESTATICO (corpus congelado). Esta mide ESTABILIDAD BAJO
  ACTUALIZACION, que es un eje distinto y no se probo nunca.

DISEÑO (simulacion de carga incremental, con el corpus real):
  1. Estado inicial: indice con SOLO los documentos del dominio D.
     Se corren consultas de D y se guarda su top-k. Esa es la verdad de referencia.
  2. Estado final: se AGREGAN los documentos de los otros dominios al MISMO indice
     (= comportamiento monolitico). Se re-corren LAS MISMAS consultas.
  3. Se mide el daño:
       - % de consultas cuyo top-k CAMBIO
       - % de consultas donde un chunk de OTRO dominio DESPLAZO a uno propio
       - cuantos puestos del top-k quedaron ocupados por intrusos
  4. Brazo segregado: por construccion el resultado es IDENTICO al estado inicial
     (filtra a D). Daño = 0 exacto, no aproximado.

OBJECION QUE UN REVISOR VA A HACER, y la respuesta:
  "el monolitico tiene mas informacion, cambiar no es degradar".
  Respuesta: para una consulta cuya evidencia vive en D, un chunk de otro dominio que
  entra al top-k NO agrega evidencia relevante: ocupa un lugar. Se mide explicitamente
  si el chunk correcto SALE del top-k. Esa salida es degradacion, no cobertura.

Las consultas son los TITULOS de los chunks de D (protocolo silver). Tiene fuga
declarada, pero aca NO importa: la fuga afecta a los dos estados por igual, y lo que
se mide es la DIFERENCIA entre estados, no el nivel absoluto.
"""
import sys, io, json, random
from pathlib import Path
from math import comb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar

KS = [3, 5, 8]
N_CONSULTAS = 60
SEED = 7

con = conectar(); cur = con.cursor()
cur.execute("SELECT id, silo, titulo, contenido, fuente, embedding::text FROM chunks")
filas = cur.fetchall(); con.close()
ids = np.array([r[0] for r in filas]); silo = np.array([r[1] for r in filas])
tit = np.array([r[2] for r in filas]); fue = np.array([r[3 + 1] for r in filas])
X = np.array([json.loads(r[5]) for r in filas]); X = X / np.linalg.norm(X, axis=1, keepdims=True)
SIL = sorted(set(silo.tolist()))
print(f"corpus {len(X)} chunks · silos " + " · ".join(f"{s}={int((silo==s).sum())}" for s in SIL))
print()

random.seed(SEED)
filas_res = []
for D in SIL:
    idx_D = np.where(silo == D)[0]
    # consultas: titulos de chunks de D que tengan largo razonable y un hermano en D
    cands = [i for i in idx_D if 15 <= len(str(tit[i])) <= 70]
    objetivos = {}
    for i in cands:
        hermanos = [j for j in idx_D if j != i and tit[j] == tit[i] and fue[j] == fue[i]]
        if hermanos:
            objetivos[i] = set(hermanos)
    if len(objetivos) < 10:
        print(f"[{D}] solo {len(objetivos)} consultas evaluables — se omite")
        continue
    sel = random.sample(list(objetivos), min(N_CONSULTAS, len(objetivos)))

    for K in KS:
        cambio = 0; desplazo = 0; perdio = 0; intrusos = []
        for i in sel:
            obj = objetivos[i]
            # ESTADO INICIAL: solo el dominio D en el indice
            s_ini = np.where(silo == D, X @ X[i], -2.0); s_ini[i] = -2
            top_ini = np.argsort(-s_ini)[:K]
            # ESTADO FINAL: corpus COMPLETO en el mismo indice (monolitico)
            s_fin = X @ X[i]; s_fin[i] = -2
            top_fin = np.argsort(-s_fin)[:K]
            if set(top_ini.tolist()) != set(top_fin.tolist()):
                cambio += 1
            n_int = int((silo[top_fin] != D).sum())
            if n_int:
                desplazo += 1
            intrusos.append(n_int)
            # ¿el objetivo estaba y se fue?
            if (obj & set(top_ini.tolist())) and not (obj & set(top_fin.tolist())):
                perdio += 1
        n = len(sel)
        filas_res.append({"dominio": D, "k": K, "n": n,
                          "cambio_topk": cambio / n, "con_intruso": desplazo / n,
                          "perdio_objetivo": perdio / n,
                          "intrusos_medios": float(np.mean(intrusos))})

print("DAÑO POR CARGA INCREMENTAL — se agregan los otros 3 dominios al mismo indice")
print("(el brazo SEGREGADO da 0.0% en las tres columnas, por construccion)")
print()
print(f"  {'dominio':12s} {'k':>2s} {'n':>3s} {'top-k cambio':>13s} {'con intruso':>12s} "
      f"{'PERDIO objetivo':>16s} {'intrusos/k':>11s}")
for r in filas_res:
    print(f"  {r['dominio']:12s} {r['k']:2d} {r['n']:3d} {r['cambio_topk']:12.1%} "
          f"{r['con_intruso']:11.1%} {r['perdio_objetivo']:15.1%} {r['intrusos_medios']:10.2f}")

print()
for K in KS:
    g = [r for r in filas_res if r["k"] == K]
    if not g:
        continue
    tot_n = sum(r["n"] for r in g)
    cam = sum(r["cambio_topk"] * r["n"] for r in g) / tot_n
    per = sum(r["perdio_objetivo"] * r["n"] for r in g) / tot_n
    # McNemar: pares donde el segregado conserva el objetivo y el monolitico lo pierde
    b10 = int(round(per * tot_n)); b01 = 0        # el segregado no puede perder: es identico al inicial
    nd = b10 + b01
    p = min(sum(comb(nd, i) for i in range(min(b10, b01) + 1)) / 2 ** nd * 2, 1.0) if nd else 1.0
    print(f"  AGREGADO k={K} (n={tot_n}): top-k cambia en {cam:.1%} · "
          f"PIERDE el objetivo en {per:.1%}")
    print(f"     McNemar segregado vs monolitico: {b10}-{b01} · nd={nd} · "
          f"p={'%.2e' % p if p < 1e-4 else '%.4f' % p}"
          + ("  [NO CONCLUYENTE]" if nd and 2.0 ** (1 - nd) > 0.05 else ""))

(SCR / "no_interferencia.json").write_text(json.dumps(filas_res, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
print(f"\n  guardado en no_interferencia.json")
print()
print("  LECTURA: 'top-k cambia' mide INESTABILIDAD (el mismo sistema, la misma consulta,")
print("  distinta respuesta solo porque se cargaron otros dominios). 'PIERDE el objetivo'")
print("  mide DAÑO CONSUMADO: la evidencia correcta estaba y dejo de estar.")
print("  En el sistema segregado ambas son 0 por construccion, no por suerte.")
