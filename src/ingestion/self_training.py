import json
import numpy as np
from collections import Counter
from db import conectar
from embedder import embed_query
from config import SILOS, CLASIFICADOR_TEMP
from clasificador import _coseno, _softmax


def _leer_chunks() -> list[dict]:
    """id + embedding of every chunk. 
    [ES] id + embedding de cada chunk."""
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id, embedding::text FROM chunks")
            filas = cursor.fetchall()
    finally:
        conexion.close()
    return [{"id": i, "emb": np.array(json.loads(e))} for i, e in filas]

def _centroide_12(embeddings: list) -> np.ndarray:
    """L2-normalized centroid: mean of the UNIT vectors, so a longer chunk with a larger-norm vector doesn't dominate the centroid.
    [ES] Centroide L2-normalizado: promedio de vectores UNITARIOS, para que un chunk largo (vector de mayor norma) no domine el centroide."""
    unit = [v / (np.linalg.norm(v) or 1) for v in embeddings]
    c = np.mean(unit, axis=0)
    return c / (np.linalg.norm(c) or 1)

def self_training(max_iter: int = 8, t: float = CLASIFICADOR_TEMP) -> dict:
    """Descriptions -> centroids -> iterate until stable. Returns {id: silo}.
    [ES] Descripciones -> centroides -> itera hasta estabilizar. Devuelve {id: silo}."""
    chunks = _leer_chunks()
    prototipos ={silo: embed_query(desc) for silo, desc in SILOS.items()}

    asignacion_prev = None
    for it in range(1, max_iter+1):
        asignacion, embs_por_silo = {}, {s: [] for s in SILOS}
        for ch in chunks:
            dist = _softmax({s: _coseno(ch["emb"],p) for s, p in prototipos.items()}, t)
            silo = max(dist, key=dist.get)
            asignacion[ch["id"]] = silo
            embs_por_silo[silo].append(ch["emb"])

        print(f"iter {it}: { {s: len(e) for s, e in embs_por_silo.items()} }")
        for silo, embs in embs_por_silo.items():
            if embs:
                prototipos[silo] = _centroide_12(embs)

        
        if asignacion == asignacion_prev:
            print(f"estable en la iteracion {it}")
            break
        asignacion_prev = asignacion

    return asignacion

def persistir(asignacion: dict) -> int:
    """Write the self-trained silo assignment back to the DB (chunks.silo).
    [ES] Escribe la asignación del self-training en la base (chunks.silo)."""
    conexion = conectar()
    try:
        with conexion:
            with conexion.cursor() as cursor:
                for cid, silo in asignacion.items():
                    cursor.execute("UPDATE chunks SET silo = %s WHERE id = %s", (silo, cid))
    finally:
        conexion.close()
    return len(asignacion)

if __name__ == "__main__":
    asignacion = self_training()

    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id, fuente, contenido FROM chunks")
            filas = {i: (f, c) for i, f, c in cursor.fetchall()}
    finally:
        conexion.close()


    por_silo = {}
    for cid, silo in asignacion.items():
        por_silo.setdefault(silo, Counter())[filas[cid][0]] += 1
    print("\n--- source document behind each silo's chunks ---")
    for silo, c in sorted(por_silo.items()):
        print(f"{silo:12}: {dict(c)}")


    for target in ("contable","financiero"):
        ids = [cid for cid, s in asignacion.items() if s == target][:3]
        print(f"\n=== sample: {target} ===")
        for cid in ids:
            print(f" [{cid}] {filas[cid][1][:130]}")
    
    n = persistir(asignacion)
    print(f"\npersistidas {n} etiquetas en la base")

