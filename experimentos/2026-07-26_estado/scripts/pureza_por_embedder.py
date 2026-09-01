"""¿LA COLISION SEMANTICA DEPENDE DEL EMBEDDER? — la pregunta que puede dar vuelta todo.

LOS 6 RESULTADOS NEGATIVOS DEPENDEN DE UNA SOLA PREMISA: que bge-m3 ya separa los
dominios de hecho (pureza de vecindario 89-91%). Si un embedder distinto los separa
PEOR, la colision semantica existe para ese embedder y segregar SI paga.

CONTEXTO DEL PROYECTO: el ADR A4 dice que el sistema arranco con MiniLM-384d y se
subio a bge-m3 con la nota "MiniLM-384d es 2021, bajo SOTA". Y la premisa del plan
aprobado (PDF pag. 3) es que "los modelos de embeddings genericos agrupan vectores
basandose en similitudes lexicas superficiales" — eso puede ser CIERTO para MiniLM y
FALSO para bge-m3. Nunca se verifico.

SE MIDE, para cada embedder, sobre el MISMO corpus y las MISMAS consultas:
  · PUREZA DE VECINDARIO (k=5): de los 5 vecinos mas cercanos, cuantos son del mismo
    silo. Es la metrica correcta en alta dimension (el silhouette engaña: dio 0.123
    cuando la pureza era 89.2%).
  · CONTAMINACION del top-3 global: fraccion de los chunks entregados que son de otro
    dominio. Es el daño directo que la segregacion elimina.
  · SEPARACION DE SENTIDOS en el termino polisemico "agentes": distancia media entre
    los chunks de "agentes" del silo legal y los del silo impositivo. Si el embedder
    los pone cerca, la colision es real.

Los embedders se prueban en orden de "cuan comun es en RAG". Si alguno no esta
descargado, se descarga (son chicos salvo bge-m3, que ya esta).
NO ESCRIBE NADA EN LA BASE.
"""
import sys, io, json, random, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
SCR = Path(__file__).resolve().parent.parent / "resultados"
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
import numpy as np
from db import conectar

K_VEC = 5
K_CTX = 3
MUESTRA = 150          # puntos de medicion por silo
SEED = 7

# (nombre, cuan usado en RAG, prefijo que exige el modelo para pasajes/consultas)
EMBEDDERS = [
    ("sentence-transformers/all-MiniLM-L6-v2", "el default de LangChain y de la mitad de los tutoriales (2021, 384d, solo ingles)", None),
    ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "el MiniLM multilingue: el default cuando el corpus no es ingles (384d)", None),
    ("intfloat/multilingual-e5-small", "muy usado para RAG multilingue (384d, 2024)", "passage: "),
    ("BAAI/bge-m3", "el que usa el proyecto (1024d, SOTA multilingue)", None),
]

con = conectar(); cur = con.cursor()
cur.execute("SELECT id, silo, titulo, contenido, fuente FROM chunks")
filas = cur.fetchall(); con.close()
silo = np.array([r[1] for r in filas])
textos_base = [f"{r[2]}\n{r[3]}" for r in filas]
cont_low = [r[3].lower() for r in filas]
SIL = sorted(set(silo.tolist()))
n = len(filas)
print(f"corpus {n} chunks · silos {SIL}\n", flush=True)

random.seed(SEED)
consultas = []
for s in SIL:
    idx = [i for i in range(n) if silo[i] == s]
    consultas += random.sample(idx, min(MUESTRA, len(idx)))
print(f"puntos de medicion: {len(consultas)} ({MUESTRA} por silo, seed={SEED})\n", flush=True)

# chunks donde "agentes" es central, por silo (para medir separacion de sentidos)
AG = {s: [i for i in range(n) if silo[i] == s and cont_low[i].count("agentes") >= 2] for s in SIL}
print("chunks con «agentes» central: " + " · ".join(f"{s}={len(v)}" for s, v in AG.items()) + "\n", flush=True)

from sentence_transformers import SentenceTransformer

resultados = []
for nombre, comentario, prefijo in EMBEDDERS:
    print(f"=== {nombre}")
    print(f"    ({comentario})", flush=True)
    try:
        modelo = SentenceTransformer(nombre)
    except Exception as e:
        print(f"    NO DISPONIBLE: {type(e).__name__}: {str(e)[:110]}\n", flush=True)
        continue
    txt = [prefijo + t for t in textos_base] if prefijo else textos_base
    import time
    t0 = time.time()
    V = modelo.encode(txt, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
    X = np.asarray(V, dtype=np.float32)
    print(f"    embebido en {(time.time()-t0)/60:.1f} min · dim {X.shape[1]}", flush=True)

    pur, cont = [], []
    for i in consultas:
        sims = X @ X[i]; sims[i] = -2
        vec = np.argpartition(-sims, K_VEC)[:K_VEC]
        pur.append(float((silo[vec] == silo[i]).mean()))
        t3 = np.argpartition(-sims, K_CTX)[:K_CTX]
        cont.append(float((silo[t3] != silo[i]).mean()))
    pureza = float(np.mean(pur)); contam = float(np.mean(cont))
    por_silo = {s: float(np.mean([p for p, i in zip(pur, consultas) if silo[i] == s])) for s in SIL}

    # separacion de sentidos de «agentes»: coseno medio ENTRE silos vs DENTRO del silo
    sep = None
    if len(AG["legal"]) >= 3 and len(AG["impositivo"]) >= 3:
        A = X[AG["legal"]]; B = X[AG["impositivo"]]
        entre = float((A @ B.T).mean())
        dentro = float((np.triu(A @ A.T, 1).sum() + np.triu(B @ B.T, 1).sum()) /
                       (len(A) * (len(A) - 1) / 2 + len(B) * (len(B) - 1) / 2))
        sep = {"entre_silos": round(entre, 4), "dentro_silo": round(dentro, 4),
               "brecha": round(dentro - entre, 4)}

    resultados.append({"embedder": nombre, "dim": int(X.shape[1]), "comentario": comentario,
                       "pureza": pureza, "contaminacion": contam,
                       "pureza_por_silo": por_silo, "agentes": sep})
    print(f"    PUREZA {pureza:.1%} · CONTAMINACION {contam:.1%}"
          + (f" · «agentes» brecha dentro-entre {sep['brecha']:+.3f}" if sep else ""), flush=True)
    print(flush=True)
    del X, V, modelo

print("=" * 96)
print(f"  ¿LA COLISION DEPENDE DEL EMBEDDER?  ·  pureza k={K_VEC} · contaminacion top-{K_CTX}")
print("=" * 96)
print(f"  {'embedder':46s} {'dim':>5s} {'PUREZA':>8s} {'CONTAM':>8s} {'brecha agentes':>15s}")
for r in sorted(resultados, key=lambda x: x["pureza"]):
    b = f"{r['agentes']['brecha']:+.3f}" if r["agentes"] else "-"
    print(f"  {r['embedder'][:46]:46s} {r['dim']:5d} {r['pureza']:7.1%} {r['contaminacion']:7.1%} {b:>15s}")

if len(resultados) >= 2:
    peor = min(resultados, key=lambda x: x["pureza"]); mejor = max(resultados, key=lambda x: x["pureza"])
    d = (mejor["pureza"] - peor["pureza"]) * 100
    print()
    print(f"  RANGO DE PUREZA entre embedders: {d:.1f} puntos")
    print(f"     peor : {peor['embedder']} -> {peor['pureza']:.1%} · contaminacion {peor['contaminacion']:.1%}")
    print(f"     mejor: {mejor['embedder']} -> {mejor['pureza']:.1%} · contaminacion {mejor['contaminacion']:.1%}")
    print()
    if d >= 5:
        print(f"  ⇒ LA COLISION SI DEPENDE DEL EMBEDDER. Con el peor, la contaminacion del")
        print(f"    monolitico es {peor['contaminacion']:.1%} (vs {mejor['contaminacion']:.1%} con el mejor):")
        print(f"    la segregacion tiene MUCHO mas que eliminar. El resultado negativo de las 6")
        print(f"    mediciones es CONDICIONAL al embedder, no universal — y eso es el hallazgo.")
    else:
        print(f"  ⇒ NO depende del embedder ({d:.1f} pp de rango). Los 4 separan parecido, asi que")
        print(f"    el resultado negativo NO se explica por haber elegido un embedder demasiado bueno.")

(SCR / "pureza_por_embedder.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1),
                                             encoding="utf-8")
print(f"\n  guardado en pureza_por_embedder.json")
