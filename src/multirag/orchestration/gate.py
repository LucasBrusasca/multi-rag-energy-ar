import math
from multirag.config import SILOS


def evaluar_incertidumbre(silo_scores: dict, umbral_entropia: float = 0.5, umbral_margen: float = 0.15)-> dict:
    """Return the distribution's entropy (normalized 0-1), the top1-top2 margin, and whether it is AMBIGUOUS. Thresholds are PROVISIONAL - calibrated vs the Golden Dataset later.
    [ES] Devuelve entropía (normalizada 0-1), margen top1-top2, y si es AMBIGUO.
    Umbrales PROVISORIOS - se calibran contra el Golden Dataset."""

    probs = [p for p in silo_scores.values() if p>0]

    h = -sum(p * math.log(p) for p in probs)

    h_norm = h / math.log(len(SILOS)) if len(SILOS) > 1 else 0

    ordenados = sorted(silo_scores.values(), reverse=True)

    margen = ordenados[0] - (ordenados[1] if len(ordenados) > 1 else 0)

    ambiguo = (h_norm > umbral_entropia) or (margen < umbral_margen)

    return {"entropia": round(h_norm, 3), "margen": round(margen,3), "ambiguo": ambiguo}


if __name__ == "__main__":
    import sys
    from multirag.orchestration.clasificador import clasificar
    texto = " ".join(sys.argv[1:])
    if not texto:
        print('Uso: python -m multirag.orchestration.gate "<texto>"'); sys.exit(1)
    r = clasificar(texto)
    g = evaluar_incertidumbre(r["silo_scores"])
    scores = {s: round(v, 2) for s, v in r["silo_scores"].items()}
    ruta = "S2 (ambiguo)" if g["ambiguo"] else "S1 (claro)"
    print(f"silo: {r['silo']} scores: {scores}")
    print(f"entropia= {g['entropia']} margen= {g['margen']} -> {ruta}")
