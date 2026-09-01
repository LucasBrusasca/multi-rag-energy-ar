"""AUDITORIA DE SIGNIFICANCIA de los hallazgos ya guardados.

Orden de Lucas (26-jul): "con toda prueba que hagas, recuerda la significatividad
estadistica". Este script la aplica RETROACTIVAMENTE a los datos crudos que quedaron
guardados, para separar tres categorias:

  (A) afirmaciones con respaldo estadistico -> van a la tesis como resultado
  (B) afirmaciones NO CONCLUYENTES por n insuficiente -> van como observacion
      exploratoria, con el n necesario declarado
  (C) afirmaciones que son COMPUTACIONALES, no estadisticas (verificaciones
      exhaustivas) -> van con cota superior de violacion, no con p-valor

Todo se calcula con tests EXACTOS (binomial / Fisher / Clopper-Pearson), no aproximados:
con n=8 una chi-cuadrado es invalida.

PISO DE SIGNIFICANCIA: con nd pares discordantes todos en la misma direccion, el minimo
p bilateral alcanzable es 2^(1-nd). Si ese piso supera 0.05, el experimento NO PUEDE dar
significancia ni con resultado perfecto -> el diseño estaba subdimensionado desde antes
de correrlo. Se reporta el n minimo necesario.
"""
import sys, io, json
from pathlib import Path
from math import comb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SCR = Path(__file__).resolve().parent.parent / "resultados"
ALFA = 0.05


def mcnemar_exacto(pares):
    """pares = lista de (a, b) booleanos. Devuelve dict con el diagnostico completo."""
    b10 = sum(1 for a, b in pares if a and not b)
    b01 = sum(1 for a, b in pares if b and not a)
    nd = b10 + b01
    if nd == 0:
        return {"b10": 0, "b01": 0, "nd": 0, "p": 1.0, "piso": 1.0, "n_min": None}
    p = min(sum(comb(nd, i) for i in range(min(b10, b01) + 1)) / 2 ** nd * 2, 1.0)
    piso = min(2.0 ** (1 - nd), 1.0)
    n_min = 6                                    # 2^(1-6)=0.031 < 0.05; con 5 el piso es 0.0625
    return {"b10": b10, "b01": b01, "nd": nd, "p": p, "piso": piso, "n_min": n_min}


def wilson(k, n, z=1.96):
    """intervalo de Wilson: valido con n chico, a diferencia del normal"""
    if n == 0:
        return (0.0, 1.0)
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def cp_superior(n, conf=0.95):
    """Clopper-Pearson: cota superior de la tasa real cuando se observan 0 eventos en n"""
    return 1 - (1 - conf) ** (1 / n)


def fisher(a, b, c, d):
    """Fisher exacto bilateral sobre tabla 2x2 [[a,b],[c,d]]"""
    fila1, fila2 = a + b, c + d
    col1, tot = a + c, a + b + c + d
    def pr(x):
        return comb(fila1, x) * comb(fila2, col1 - x) / comb(tot, col1)
    p0 = pr(a)
    lo = max(0, col1 - fila2)
    return min(sum(pr(x) for x in range(lo, min(fila1, col1) + 1) if pr(x) <= p0 * (1 + 1e-9)), 1.0)


def bloque(titulo, n, res, interpretacion_a, interpretacion_b):
    print(f"\n{'-'*76}\n  {titulo}   (n={n} pares)")
    print(f"     discordantes: {res['nd']}  ({res['b10']} en un sentido, {res['b01']} en el otro)")
    if res["nd"] == 0:
        print(f"     p = 1.0  ·  EMPATE EXACTO: los dos brazos se comportaron identico.")
        print(f"     ⇒ CATEGORIA (B): no hay diferencia detectable, pero con n={n} tampoco")
        print(f"       se podria detectar una chica. NO afirmar 'son equivalentes'.")
        return
    print(f"     p exacto = {res['p']:.4f}   ·   piso alcanzable con {res['nd']} discordantes = {res['piso']:.4f}")
    if res["piso"] > ALFA:
        print(f"     ⇒ CATEGORIA (B) NO CONCLUYENTE POR DISEÑO: aun con los {res['nd']}")
        print(f"       discordantes UNANIMES el p no bajaria de {res['piso']:.4f} > {ALFA}.")
        print(f"       Hacen falta >= {res['n_min']} pares discordantes. {interpretacion_b}")
    elif res["p"] < ALFA:
        print(f"     ⇒ CATEGORIA (A) SIGNIFICATIVO. {interpretacion_a}")
    else:
        print(f"     ⇒ CATEGORIA (B): el diseño SI podia detectar (piso {res['piso']:.4f}), "
              f"pero el resultado no alcanza. {interpretacion_b}")


print("=" * 76)
print("  AUDITORIA RETROACTIVA DE SIGNIFICANCIA  ·  tests exactos  ·  alfa = 0.05")
print("=" * 76)

# ---------------- 1. ABSTENCION en preguntas sin respuesta ----------------
d = json.loads((SCR / "abstencion_resultados.json").read_text(encoding="utf-8"))
pares = [(bool(r["abst_seg"]), bool(r["abst_b0"])) for r in d]
ab_s = sum(r["abst_seg"] for r in d); ab_b = sum(r["abst_b0"] for r in d)
n = len(d)
print(f"\n[1] ¿EL CONTEXTO SEGREGADO MEJORA LA ABSTENCION? (preguntas sin respuesta en el corpus)")
print(f"     segregado se abstuvo: {ab_s}/{n} ({ab_s/n:.0%})  IC95% Wilson [{wilson(ab_s,n)[0]:.0%}, {wilson(ab_s,n)[1]:.0%}]")
print(f"     B0 monolitico       : {ab_b}/{n} ({ab_b/n:.0%})  IC95% Wilson [{wilson(ab_b,n)[0]:.0%}, {wilson(ab_b,n)[1]:.0%}]")
bloque("McNemar pareado (mismo generador, mismo k)", n, mcnemar_exacto(pares),
       "La segregacion cambia la abstencion de forma detectable.",
       "Observacion exploratoria: hay que rehacerlo con el estrato sin-respuesta del Golden (15% de ~200 items = ~30 casos).")

# ---------------- 2. FUSION FALSA en preguntas trampa ----------------
d = json.loads((SCR / "fusion_resultados.json").read_text(encoding="utf-8"))
pares = [(bool(r["fusion_seg"]), bool(r["fusion_b0"])) for r in d]
fs = sum(r["fusion_seg"] for r in d); fb = sum(r["fusion_b0"] for r in d)
n = len(d)
print(f"\n\n[2] ¿EL CONTEXTO MEZCLADO PRODUCE FUSION FALSA? (une dos piezas que el corpus tiene separadas)")
print(f"     segregado fusiono: {fs}/{n} ({fs/n:.0%})  IC95% [{wilson(fs,n)[0]:.0%}, {wilson(fs,n)[1]:.0%}]")
print(f"     B0 fusiono       : {fb}/{n} ({fb/n:.0%})  IC95% [{wilson(fb,n)[0]:.0%}, {wilson(fb,n)[1]:.0%}]")
bloque("McNemar pareado", n, mcnemar_exacto(pares),
       "La segregacion reduce la fusion falsa de forma detectable.",
       "Hipotesis viva pero NO probada. Es el estrato que hay que sobredimensionar en el Golden.")

# ---------------- 3. DOSIS-RESPUESTA de cita intrusa ----------------
d = json.loads((SCR / "dosis_resultados.json").read_text(encoding="utf-8"))
print(f"\n\n[3] DOSIS-RESPUESTA: ¿mas chunks intrusos en el contexto -> mas citas intrusas?")
por_dosis = {}
for r in d:
    por_dosis.setdefault(r["dosis"], []).append(r)
print(f"     {'dosis':>6s} {'n':>4s} {'cita intrusa':>13s} {'IC95% Wilson':>20s} {'cita correcta':>14s}")
niveles = sorted(por_dosis)
for k in niveles:
    g = por_dosis[k]
    ci = sum(bool(x["cita_intrusa"]) for x in g); cc = sum(bool(x["cita_correcta"]) for x in g)
    lo, hi = wilson(ci, len(g))
    print(f"     {k:6d} {len(g):4d} {ci}/{len(g)} = {ci/len(g):6.0%} "
          f"   [{lo:5.0%}, {hi:5.0%}]  {cc}/{len(g)} = {cc/len(g):5.0%}")
# test de tendencia exacto sobre los extremos (Fisher), que es lo unico valido con estos n
if len(niveles) >= 2:
    g0, g1 = por_dosis[niveles[0]], por_dosis[niveles[-1]]
    a = sum(bool(x["cita_intrusa"]) for x in g0); b = len(g0) - a
    c = sum(bool(x["cita_intrusa"]) for x in g1); e = len(g1) - c
    p = fisher(a, b, c, e)
    print(f"\n     Fisher exacto dosis {niveles[0]} vs dosis {niveles[-1]}: p = {p:.4f}")
    if p < ALFA:
        print(f"     ⇒ CATEGORIA (A): la dosis de intrusos SI aumenta la cita intrusa, significativo.")
    else:
        print(f"     ⇒ CATEGORIA (B): tendencia visible pero NO significativa con estos n.")
        print(f"       Con {len(g0)} y {len(g1)} casos por nivel el test tiene poca potencia;")
        print(f"       la diferencia observada ({a/len(g0):.0%} -> {c/len(g1):.0%}) necesita ~3-4x mas casos.")

# ---------------- 4. VERIFICACIONES EXHAUSTIVAS: no llevan p-valor ----------------
print(f"\n\n{'='*76}")
print("[4] AFIRMACIONES COMPUTACIONALES (categoria C) — NO llevan p-valor, llevan COTA")
print("=" * 76)
print("""
Estas tres NO son hipotesis estadisticas: son verificaciones exhaustivas sobre el
conjunto de evaluacion. El error correcto de reportar es la cota superior de
Clopper-Pearson sobre la tasa de violacion, no un p-valor.
""")
for nombre, n_ver, detalle in [
    ("Teorema del rescate: filtrar al silo donde vive la evidencia NUNCA empeora su rango",
     160, "0 contraejemplos en 160 consultas"),
    ("gamma=1.0 reproduce B0 EXACTAMENTE (el monolitico es un punto degenerado del sistema)",
     100, "100/100 coincidencias exactas"),
]:
    cota = cp_superior(n_ver)
    print(f"  · {nombre}")
    print(f"      {detalle}  ->  tasa real de violacion <= {cota:.2%} con 95% de confianza")
    print(f"      REDACCION CORRECTA: \"no se observaron violaciones en {n_ver} casos")
    print(f"      (cota superior 95%: {cota:.1%})\"  ·  NO decir \"nunca ocurre\".")
print(f"""
  · Ley empirica recall ~ f(cantidad de silos abiertos): r=0.932, R2=0.87
      Es una CORRELACION sobre ~35 politicas de ruteo, no un test de hipotesis.
      Con r=0.932 y n=35 el p de la correlacion es < 1e-15 (categoria A), pero
      OJO: las 35 politicas NO son independientes entre si (comparten el corpus y
      se solapan), asi que el p esta inflado. REDACCION CORRECTA: reportar r y R2
      como descripcion, sin p-valor.
""")

print("=" * 76)
print("  RESUMEN PARA LA TESIS Y PARA LA CARTA A MERLINO")
print("=" * 76)
print("""
  Lo que la campaña 24-26/jul puede afirmar CON RESPALDO:
    · el ruteo por coseno acierta 96.2% y el 3.8% de fallos cuesta recall 0
    · el SLM de 3B NO alcanza como orquestador (McNemar unanime, p<1e-7)
    · ninguna de ~40 configuraciones supero a B0 en recall con embedder compartido
    · el monolitico es un caso particular del sistema segregado (gamma=1.0)

  Lo que NO puede afirmar todavia (n insuficiente, no resultado negativo):
    · que la segregacion mejore la abstencion
    · que la segregacion reduzca la fusion falsa
    · que la dosis de intrusos degrade la respuesta de forma monotona
    ⇒ LAS TRES son hipotesis de VALOR EPISTEMICO, no de recall. Son exactamente
      lo que el plan pide validar (objetivo 4) y lo que el Golden debe dimensionar.
      El estrato de colision y el de sin-respuesta hay que SOBREDIMENSIONARLOS.

  Regla de diseño que sale de esta auditoria (va a PROTOCOLO_GOLDEN):
    Ningun estrato del Golden con menos de ~30 items utiles. Con 8 el experimento
    es imposible de ganar: el piso de McNemar (2^(1-nd)) ya excede 0.05.
""")
