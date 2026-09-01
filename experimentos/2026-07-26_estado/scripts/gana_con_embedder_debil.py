"""¿LA SEGREGACION GANA CUANDO EL EMBEDDER ES MAS DEBIL? — el test que decide.

POR QUE ESTE Y NO LA PUREZA:
  Medir que MiniLM tiene mas contaminacion (13.8% vs 7.6%) NO dice si la arquitectura
  gana. Solo dice que hay mas basura. La pregunta que importa es si el sistema segregado
  APROVECHA esa diferencia. Los dos desenlaces son informativos:
    - si con MiniLM la segregacion GANA -> la ventaja arquitectonica existe pero queda
      TAPADA por la calidad del embedder. Consecuencia metodologica fuerte: una
      conclusion arquitectonica NO es portable entre embedders, y los papers que
      afirman "multi-indice gana" sin declarar su embedder estan confundidos.
    - si con MiniLM tambien empata -> el embedder no explica nada y la linea se cierra.

DISEÑO: se repite EXACTAMENTE la medicion de C.30-C.69 (protocolo silver: el titulo de
un chunk como consulta, los chunks hermanos como objetivo), pero cambiando el embedder.
Asi el resultado es directamente comparable con lo ya medido en bge-m3.

BRAZOS (P4: ninguno degradado, misma k):
  B0            top-k GLOBAL (monolitico)
  MULTI-oraculo top-k dentro del silo donde vive la evidencia (techo de la arquitectura)
  MULTI-router  top-k dentro del silo que elige el router por coseno a prototipos
                (el sistema REAL, sin oraculo)
  B0+MMR        monolitico con diversificacion estandar (el baseline fuerte, P4)

METRICAS: recall@k del objetivo · contaminacion del contexto · McNemar pareado con
piso de significancia.

Los vectores se guardan en .npy para no re-embeber si hay que repetir.
"""
import sys, io, json, random, time
from pathlib import Path
from math import comb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar

K = 3
N_POR_SILO = 40
SEED = 7
MODELOS = [
    ("sentence-transformers/all-MiniLM-L6-v2", None),
    ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", None),
    ("BAAI/bge-m3", None),
]

con = conectar(); cur = con.cursor()
cur.execute("SELECT id, silo, titulo, contenido, fuente FROM chunks")
filas = cur.fetchall(); con.close()
silo = np.array([r[1] for r in filas]); tit = np.array([r[2] for r in filas])
fue = np.array([r[4] for r in filas])
textos = [f"{r[2]}\n{r[3]}" for r in filas]
SIL = sorted(set(silo.tolist()))
n = len(filas)

# conjunto de evaluacion IDENTICO al de C.30-C.69 (mismo seed, misma construccion)
random.seed(SEED)
por_dom = {}
for i in range(n):
    if 15 <= len(str(tit[i])) <= 70:
        por_dom.setdefault(silo[i], []).append(i)
consultas = []
for s in SIL:
    consultas += random.sample(por_dom[s], min(N_POR_SILO, len(por_dom[s])))
objetivos = {}
for i in consultas:
    h = {j for j in range(n) if j != i and tit[j] == tit[i] and fue[j] == fue[i]}
    if h:
        objetivos[i] = h
print(f"corpus {n} chunks · {len(objetivos)} consultas evaluables · k={K}\n", flush=True)


def mmr(s, X, Kk, lam=0.5, pool=40):
    cand = list(np.argsort(-s)[:pool]); sel = []
    while len(sel) < Kk and cand:
        mejor, mv = None, -9.0
        for j in cand:
            red = max((float(X[j] @ X[k]) for k in sel), default=0.0)
            v = lam * float(s[j]) - (1 - lam) * red
            if v > mv:
                mv, mejor = v, j
        sel.append(mejor); cand.remove(mejor)
    return sel


def mcnemar(a, b):
    """a, b = listas de booleanos pareadas. Devuelve (pro_a, pro_b, nd, p, piso)."""
    b10 = sum(1 for x, y in zip(a, b) if x and not y)
    b01 = sum(1 for x, y in zip(a, b) if y and not x)
    nd = b10 + b01
    if nd == 0:
        return b10, b01, 0, 1.0, 1.0
    p = min(sum(comb(nd, i) for i in range(min(b10, b01) + 1)) / 2 ** nd * 2, 1.0)
    return b10, b01, nd, p, min(2.0 ** (1 - nd), 1.0)


from sentence_transformers import SentenceTransformer
from clasificador import _centroide_l2

tabla = []
for nombre, prefijo in MODELOS:
    cache = SCR / f"vec_{nombre.split('/')[-1]}.npy"
    if cache.exists():
        X = np.load(cache)
        print(f"=== {nombre}  (vectores desde cache)", flush=True)
    else:
        print(f"=== {nombre}  (embebiendo {n} chunks...)", flush=True)
        try:
            m = SentenceTransformer(nombre)
        except Exception as e:
            print(f"    NO DISPONIBLE: {type(e).__name__}\n", flush=True)
            continue
        t0 = time.time()
        txt = [prefijo + t for t in textos] if prefijo else textos
        X = np.asarray(m.encode(txt, batch_size=32, show_progress_bar=False,
                                normalize_embeddings=True), dtype=np.float32)
        np.save(cache, X)
        print(f"    listo en {(time.time()-t0)/60:.1f} min · dim {X.shape[1]}", flush=True)
        del m
    proto = {s: np.array(_centroide_l2([X[i] for i in range(n) if silo[i] == s])) for s in SIL}
    P = np.array([proto[s] for s in SIL]); P = P / np.linalg.norm(P, axis=1, keepdims=True)

    BR = ["B0", "B0+MMR", "MULTI-router", "MULTI-oraculo"]
    hit = {b: [] for b in BR}; cont = {b: [] for b in BR}
    ruteo_ok = []
    for i, obj in objetivos.items():
        s = X @ X[i]; s[i] = -2
        dom_i = silo[i]
        sel = {"B0": list(np.argsort(-s)[:K]), "B0+MMR": mmr(s, X, K)}
        # router real: coseno a prototipos
        top_r = SIL[int(np.argmax(X[i] @ P.T))]
        ruteo_ok.append(top_r == dom_i)
        sel["MULTI-router"] = list(np.argsort(-np.where(silo == top_r, s, -2))[:K])
        silos_obj = list({silo[j] for j in obj})
        sel["MULTI-oraculo"] = list(np.argsort(-np.where(np.isin(silo, silos_obj), s, -2))[:K])
        for b in BR:
            hit[b].append(bool(obj & set(sel[b])))
            cont[b].append(float((silo[sel[b]] != dom_i).mean()))

    m_ = len(objetivos)
    print(f"    acierto de ruteo del router: {sum(ruteo_ok)}/{m_} = {sum(ruteo_ok)/m_:.1%}")
    print(f"    {'brazo':16s} {'recall@3':>9s} {'contamin':>9s} {'vs B0':>8s}  McNemar vs B0")
    for b in BR:
        r = sum(hit[b]) / m_
        d = (r - sum(hit['B0']) / m_) * 100
        if b == "B0":
            print(f"    {b:16s} {r:8.1%} {np.mean(cont[b]):8.1%} {'—':>8s}")
        else:
            b10, b01, nd, p, piso = mcnemar(hit[b], hit["B0"])
            aviso = "  [NO CONCLUYENTE]" if nd and piso > 0.05 else ""
            print(f"    {b:16s} {r:8.1%} {np.mean(cont[b]):8.1%} {d:+7.1f}  "
                  f"{b10}-{b01} nd={nd} p={p:.4f}{aviso}")
        tabla.append({"embedder": nombre, "dim": int(X.shape[1]), "brazo": b,
                      "recall": r, "contaminacion": float(np.mean(cont[b])),
                      "ruteo": sum(ruteo_ok) / m_})
    print(flush=True)
    del X

(SCR / "gana_con_embedder_debil.json").write_text(json.dumps(tabla, ensure_ascii=False, indent=1),
                                                 encoding="utf-8")
print("=" * 90)
print("  ¿GANA LA SEGREGACION CON EL EMBEDDER DEBIL?")
print("=" * 90)
print(f"  {'embedder':44s} {'brazo':16s} {'recall':>8s} {'contam':>8s}")
for t in tabla:
    print(f"  {t['embedder'][:44]:44s} {t['brazo']:16s} {t['recall']:7.1%} {t['contaminacion']:7.1%}")
print()
emb = sorted({t["embedder"] for t in tabla})
for e in emb:
    g = {t["brazo"]: t for t in tabla if t["embedder"] == e}
    if "B0" in g and "MULTI-router" in g:
        d = (g["MULTI-router"]["recall"] - g["B0"]["recall"]) * 100
        print(f"  {e.split('/')[-1]:44s} MULTI-router vs B0: {d:+.1f} pp "
              f"(ruteo {g['MULTI-router']['ruteo']:.0%})")
print()
print("  LECTURA: si el delta MULTI-router vs B0 es POSITIVO con los MiniLM y ~0 con bge-m3,")
print("  la ventaja arquitectonica EXISTE y la tapa la calidad del embedder. Si es ~0 o")
print("  negativo en los tres, el embedder no explica nada y la linea se cierra.")
