import sys
import numpy as np
from embedder import embed_query
from config import SILOS, CLASIFICADOR_TEMP
import json


_prototipos = None

def _centroides_db() -> dict:
    """Centroid per silo: the MEAN of the real chunk embeddings stored in that silo.
    Returns {} if the DB is unreachable (cold start / Docker off).
    [ES] Centroide por silo = promedio de los embeddings reales guardados; {} si no hay base.   
    """
    from db import conectar
    try:
        conexion = conectar()
    except Exception:
        return {}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT silo, AVG(embedding)::text FROM chunks GROUP BY silo")
            filas = cursor.fetchall()
    finally:
        conexion.close()
    return {silo: json.loads(vector) for silo, vector in filas}

def _get_prototipos() -> dict:
    """Prototype per silo: the CENTROID of its real chunks when the silo has data;
    otherwise the embedded description (cold-start fallback).
    [ES] Prototipo = centroide si el silo tiene chunks; si no, la descripción embebida."""
    global _prototipos
    if _prototipos is None:
        centroides = _centroides_db()
        _prototipos = {}
        for silo, desc in SILOS.items():
            if silo in centroides:
                _prototipos[silo] = centroides[silo]
                print(f"[clasificador] prototipo '{silo}': centroide (chunks reales)")
            else:
                _prototipos[silo] = embed_query(desc)
                print(f"[clasificador] prototipo '{silo}': descripción (silo vacío)")
    return _prototipos


def _coseno(a, b) -> float:
    """Similitud coseno entre dos vectores (1 = idénticos, ~0 = sin relación))"""
    a, b = np.array(a), np.array(b)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na==0 or nb == 0 else float(np.dot(a,b) / (na * nb))

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
        print('Uso: python src/ingestion/clasificador.py "<texto a clasificar>"')
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
    from db import conectar
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