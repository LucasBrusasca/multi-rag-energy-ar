import sys
import numpy as np
from multirag.config import CLASIFICADOR_TEMP, SILOS
from multirag.ingestion.embedder import embed_query
import json


_prototipos = None

def _centroides_db() -> dict:
    """Centroid per silo = L2-normalized centroid of that silo's real chunk embeddings (the ONE formula).
    Returns {} if the DB is unreachable (cold start / Docker off).
    [ES] Centroide por silo = centroide L2-normalizado de los embeddings reales del silo (la ÚNICA fórmula).
    Devuelve {} si no hay base (arranque en frío / Docker apagado)."""
    from multirag.db import conectar
    from collections import defaultdict
    try:
        conexion = conectar()
    except Exception:
        return {}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT silo, embedding::text FROM chunks")
            filas = cursor.fetchall()
    finally:
        conexion.close()
    por_silo = defaultdict(list)
    for silo, vector in filas:
        por_silo[silo].append(json.loads(vector))
    return {silo: _centroide_l2(embs) for silo, embs in por_silo.items()}


def _get_prototipos() -> dict:
    """Prototype per silo. HOMOGENEOUS by design: real-chunk centroids ONLY when every silo has data;
    otherwise the embedded descriptions for ALL silos (cold start).
    [ES] Prototipo por silo. HOMOGÉNEO por diseño: centroides SOLO cuando todos los silos tienen
    datos; si no, descripciones para TODOS (arranque en frío). Mezclar rompe la clasificación (A.2)."""
    global _prototipos
    if _prototipos is None:
        centroides = _centroides_db()
        if set(centroides) >= set(SILOS):
            _prototipos = {silo: centroides[silo] for silo in SILOS}
            print("[clasificador] prototipos: centroides (todos los silos poblados)")
        else:
            _prototipos = {silo: embed_query(desc) for silo, desc in SILOS.items()}
            print("[clasificador] prototipos: descripciones (cold start homogéneo)")
    return _prototipos


def _coseno(a, b) -> float:
    """Similitud coseno entre dos vectores (1 = idénticos, ~0 = sin relación))"""
    a, b = np.array(a), np.array(b)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na==0 or nb == 0 else float(np.dot(a,b) / (na * nb))


def _centroide_l2(embeddings) -> list:
    """L2-normalized centroid: mean of UNIT vectors, so a long chunk (larger norm) doesn't dominate
    THE single centroid formula - used by both ingestion routing and self-training.
    [ES] Centroide L2-normalizado: promedio de vectores UNITARIOS, para que un chunk largo no domine.
    La única fórmula de centroide - la usan el ruteo de ingesta y el self-training."""
    unit = [np.array(v) / (np.linalg.norm(v) or 1) for v in embeddings]
    c = np.mean(unit, axis = 0)
    return (c / (np.linalg.norm(c) or 1)).tolist()


def _softmax(cosenos: dict, t: float) -> dict:
    """Convierte los cosenos en una distribución (probabilidad que suman 1), con temperatura T."""
    vals = np.array(list(cosenos.values())) / t
    exp = np.exp(vals - vals.max())
    probs = exp / exp.sum()
    return {silo: float(p) for silo, p in zip(cosenos.keys(),probs)}

def clasificar_vector(vec, t: float = CLASIFICADOR_TEMP) -> dict:
    """Classify an ALREADY-computed embedding. DETERMINISTIC (no LLM).
    returns {'silo': dominant, 'silo_scores': full distributions}.
    [ES] Clasifica un embedding YA calculado. Determinístico (sin LLM)."""
    cosenos = {silo: _coseno(vec, proto) for silo, proto in _get_prototipos().items()}
    distribucion = _softmax(cosenos, t)
    silo_dominante= max(distribucion, key= distribucion.get)
    return {"silo": silo_dominante, "silo_scores": distribucion}

def clasificar(texto: str, t: float = CLASIFICADOR_TEMP) -> dict:
    """Classify a TEXT (embeds it and delegates to clasificar_vector).
    [ES] Clasifica un TEXTO  (lo embebe y delega en clasificar_vector)."""
    return clasificar_vector(embed_query(texto), t)

if __name__ == "__main__":
    texto = " ".join(sys.argv[1:]) 
    if not texto:
        print('Uso: python -m multirag.orchestration.clasificador "<texto a clasificar>"')
        sys.exit(1)
    r = clasificar(texto)
    print(f"\nSilo dominante: {r['silo']}\n")
    for silo, score in sorted(r["silo_scores"].items(), key=lambda x: -x[1]):
        print(f" {silo:12} {score:.3f}")

def clasificar_knn(embedding, k: int = 10) -> dict:
    """Classify a chunk by its k nearest labeled neighbors in the DB (KNN / semantic router).
    Deterministic, per-chunk, reuses pgvector.
    Returns {'silo': dominant, 'silo_scores': distribution}.
    [ES] Clasifica un chunk por sus k vecinos más cercanos etiquetados en la base.
    Determinístico, por-chunk, reusa pgvector."""
    from multirag.db import conectar
    from collections import Counter
    vector_literal = "[" + ",".join(map(str,embedding)) + "]"
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT silo FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s",
                (vector_literal, k),
             )
            vecinos = [fila[0] for fila in cursor.fetchall()]

    finally:
        conexion.close()
    
    total = len(vecinos) or 1
    conteo = Counter(vecinos)
    distribucion = {silo: conteo.get(silo,0) / total for silo in SILOS}
    silo_dominante = max(distribucion, key= distribucion.get)
    return {"silo": silo_dominante, "silo_scores": distribucion}
