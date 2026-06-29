import sys
import numpy as np
from embedder import embed_query
from config import SILOS, CLASIFICADOR_TEMP


_prototipos = None

def _get_prototipos() -> dict:
    """Embebe la DESCRIPCIÓN de cada silo una vez. Ese vector es el 'prototipo' del silo."""
    global _prototipos
    if _prototipos is None:
        _prototipos = {silo: embed_query(desc) for silo, desc in SILOS.items()}
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

def clasificar(texto: str, t: float = CLASIFICADOR_TEMP) -> dict:
    """Clasifica un texto en los silos. DETERMINÍSTICO (sin LLM).
    Devuelve {'silo': dominante, 'silo_scores': distribución completa}."""
    vec = embed_query(texto)
    cosenos = {silo: _coseno(vec, proto) for silo, proto in _get_prototipos().items()}
    distribucion = _softmax(cosenos, t)
    silo_dominante = max(distribucion, key=distribucion.get)
    return {"silo": silo_dominante, "silo_scores": distribucion}
    
if __name__ == "__main__":
    texto = " ".join(sys.argv[1:]) 
    if not texto:
        print('Uso: python src/ingestion/clasificador.py "<texto a clasificar>"')
        sys.exit(1)
    r = clasificar(texto)
    print(f"\nSilo dominante: {r['silo']}\n")
    for silo, score in sorted(r["silo_scores"].items(), key=lambda x: -x[1]):
        print(f" {silo:12} {score:.3f}")
