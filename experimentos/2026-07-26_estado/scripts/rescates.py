"""¿SE PUEDE SUPERAR A B0? — verificacion del error de C.43.

C.43 afirmo "recall(cualquier seleccion) <= recall(B0) SIEMPRE". ESO ERA FALSO:
solo vale para abrir TODOS los silos y fusionar. Filtrar a UN silo puede superar a B0,
porque dentro del silo el chunk correcto SUBE de puesto (se le quitan de encima los
parecidos de OTROS dominios = la colision).

TEOREMA (a verificar 0 contraejemplos): el puesto del chunk dentro de su propio silo
es SIEMPRE <= su puesto global (filtrar solo puede sacarle competidores de arriba).

RESCATES: casos donde B0 pierde el chunk (fuera del top-3 global) pero el silo
correcto lo encuentra (dentro del top-3 del silo). Nota: la FUGA del silver empuja
el origen al puesto 1 global -> juega EN CONTRA de encontrar rescates -> el conteo
es CONSERVADOR (los rescates reales con preguntas parafraseadas serian mas).
"""
import sys, io, json, random
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
from db import conectar
from embedder import embed_query

DOM = {"Ley_24065_Energia_Electrica_TO": "legal", "Ley_24076_Gas_Natural_TO": "legal",
       "Decreto_1738_1992_Reglamentario_Gas": "legal", "Decreto_1398_1992_Reglamentario_Electrico": "legal",
       "Res_SE_61_1992_Los_Procedimientos": "legal", "Res_SE_137_1992": "legal", "ENRE_Resolucion_544_2024": "legal",
       "Ley_11683_Procedimiento_Fiscal_TO": "impositivo", "Decreto_821_1998_TO_Ley_11683": "impositivo",
       "RG_AFIP_830": "impositivo",
       "Estados_Contables_Neuquen": "contable", "EEFF-ind-31-03-2019": "contable", "FS-31-03-2019": "contable",
       "TR-consolidado-03-2026_VF-Clean": "contable",
       "MSU_ON_ClaseIV": "financiero", "Transener_Calificacion_FIX": "financiero",
       "Transener-Company-Presentation-April-2026": "financiero"}
K = 3
con = conectar()
cur = con.cursor()
cur.execute("SELECT DISTINCT fuente, titulo FROM chunks WHERE LENGTH(titulo) BETWEEN 15 AND 70")
todo = [(f, t) for f, t in cur.fetchall() if f in DOM]
random.seed(7)
por_dom = {}
for f, t in todo:
    por_dom.setdefault(DOM[f], []).append((f, t))
consultas = []
for d, l in por_dom.items():
    consultas += [(f, t, d) for f, t in random.sample(l, min(40, len(l)))]

rescates = []
contraejemplos_teorema = 0
mejoras_puesto = []

for f, t, dom in consultas:
    cur.execute("SELECT chunk_uid, silo FROM chunks WHERE fuente = %s AND titulo = %s", (f, t))
    origen = cur.fetchall()
    uids = {u for u, _ in origen}
    q = embed_query(t)
    vec = "[" + ",".join(map(str, q)) + "]"

    # puesto GLOBAL del chunk de origen (hasta 50)
    cur.execute("SELECT chunk_uid FROM chunks ORDER BY embedding <=> %s::vector LIMIT 50", (vec,))
    glob = [r[0] for r in cur.fetchall()]
    pos_g = next((i for i, u in enumerate(glob, 1) if u in uids), 99)

    # puesto DENTRO del silo donde quedo guardado (el mejor entre los silos de origen)
    mejor_pos_s = 99
    for silo_o in {s for _, s in origen}:
        cur.execute("SELECT chunk_uid FROM chunks WHERE silo = %s "
                    "ORDER BY embedding <=> %s::vector LIMIT 50", (silo_o, vec))
        dentro = [r[0] for r in cur.fetchall()]
        pos_s = next((i for i, u in enumerate(dentro, 1) if u in uids), 99)
        mejor_pos_s = min(mejor_pos_s, pos_s)

    if mejor_pos_s > pos_g:
        contraejemplos_teorema += 1
    if pos_g < 99 and mejor_pos_s < 99:
        mejoras_puesto.append(pos_g - mejor_pos_s)
    if pos_g > K and mejor_pos_s <= K:
        rescates.append((t, f, pos_g, mejor_pos_s))

con.close()
n = len(consultas)
print(f"VERIFICACION — {n} consultas")
print()
print(f"  TEOREMA 'filtrar al silo correcto nunca empeora el puesto':")
print(f"     contraejemplos: {contraejemplos_teorema}   <- debe ser 0")
print()
print(f"  RESCATES (B0 lo pierde del top-{K}, el silo correcto lo encuentra): {len(rescates)}/{n}  ({len(rescates)/n:.1%})")
print(f"  (conteo CONSERVADOR: la fuga del silver empuja el origen al puesto 1 global,")
print(f"   o sea juega EN CONTRA de que aparezcan rescates)")
print()
print("  ejemplos de rescate (consulta | puesto global -> puesto en su silo):")
for t, f, pg, ps in rescates[:6]:
    print(f'     "{t[:45]:45s}" {f[:24]:24s}  #{pg} -> #{ps}')
