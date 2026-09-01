"""VIGENCIA — el frente donde el coseno NO manda.

Que un texto este derogado/sustituido NO esta en el vector: es un dato que el monolitico
no tiene. Un RAG sin filtro temporal recupera y cita texto sustituido con confianza total
porque semanticamente es perfecto.

PASO 1 (este script): extraer la metadata temporal con regex DETERMINISTA y medir
cuanta hay, de que tipo, y cuantos chunks del corpus quedan afectados.
Sin esto no hay experimento posible.

Formatos reales en el corpus:
  "(Artículo sustituido por art. 181 de la Ley N° 27430 ... B.O. 29/12/2017. Vigencia: ...)"
  "- Anexo VIII sustituido por art. 1° de la Resolución General N° 1810/2005 AFIP B.O. 10/1/2005"
"""
import sys, io, re, json
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "src" / "ingestion"))
from db import conectar

# --- patrones deterministas (cada uno con su rol) ---
P_ACCION = re.compile(
    r"(?P<que>Art[íi]culo|Inciso|Anexo|Ap[áa]rtado|P[áa]rrafo|Cap[íi]tulo|T[íi]tulo)?\s*"
    r"(?P<num>[IVXLC\d]+[°ºa-z\)\.]*)?\s*"
    r"(?P<accion>sustitu[íi]?d[oa]|derogad[oa]|incorporad[oa]|modificad[oa])\s+por\s+"
    r"(?P<norma>[^.;)]{5,120})", re.I)
P_BO = re.compile(r"B\.?\s?O\.?\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", re.I)
P_VIG = re.compile(r"[Vv]igencia\s*:?\s*([^.;)]{5,90})")
P_NORMA_NUM = re.compile(r"(?:Ley|Decreto|Resoluci[óo]n(?:\s+General)?|RG)\s*N?[°º]?\s*([\d\.]{3,8})", re.I)

con = conectar(); cur = con.cursor()
cur.execute("SELECT chunk_uid, silo, titulo, contenido, fuente FROM chunks")
filas = cur.fetchall(); con.close()

acciones = Counter()
por_fuente = defaultdict(int)
eventos = []
con_bo = 0
for uid, silo, tit, cont, fue in filas:
    ms = list(P_ACCION.finditer(cont))
    if not ms:
        continue
    por_fuente[fue] += 1
    for m in ms:
        acc = m.group("accion").lower()
        acc = ("sustituido" if acc.startswith("sustitu") else
               "derogado" if acc.startswith("derog") else
               "incorporado" if acc.startswith("incorp") else "modificado")
        acciones[acc] += 1
        seg = cont[m.start():m.start() + 300]
        bo = P_BO.search(seg)
        vig = P_VIG.search(seg)
        nn = P_NORMA_NUM.search(m.group("norma"))
        if bo:
            con_bo += 1
        eventos.append({"chunk_uid": uid, "silo": silo, "fuente": fue, "titulo": tit,
                        "que": (m.group("que") or "").strip(), "num": (m.group("num") or "").strip(),
                        "accion": acc, "norma_texto": m.group("norma").strip()[:90],
                        "norma_num": nn.group(1) if nn else None,
                        "bo": bo.group(1) if bo else None,
                        "vigencia": vig.group(1).strip()[:70] if vig else None})

n = len(filas)
chunks_af = len(por_fuente) and sum(por_fuente.values())
print(f"EXTRACCION DE METADATA TEMPORAL · {n} chunks · regex determinista")
print()
print(f"  eventos normativos detectados : {len(eventos)}")
print(f"  chunks afectados              : {sum(por_fuente.values())} ({sum(por_fuente.values())/n:.1%} del corpus)")
print(f"  eventos con fecha de B.O.     : {con_bo} ({con_bo/max(len(eventos),1):.0%})")
print(f"  eventos con norma identificada: {sum(1 for e in eventos if e['norma_num'])} "
      f"({sum(1 for e in eventos if e['norma_num'])/max(len(eventos),1):.0%})")
print()
print("  por tipo de acción:")
for a, c in acciones.most_common():
    print(f"     {a:14s} {c:5d}")
print()
print("  por documento:")
for f, c in sorted(por_fuente.items(), key=lambda x: -x[1]):
    print(f"     {f[:44]:44s} {c:5d} chunks")
print()
print("  MUESTRA de eventos extraidos (los que tienen norma + fecha):")
completos = [e for e in eventos if e["norma_num"] and e["bo"]]
print(f"  ({len(completos)} eventos COMPLETOS: qué + acción + norma + fecha B.O.)")
print()
for e in completos[:10]:
    q = f"{e['que']} {e['num']}".strip() or "(pieza)"
    print(f"     [{e['fuente'][:24]:24s}] {q[:22]:22s} {e['accion']:12s} por norma {e['norma_num']:8s} B.O. {e['bo']}")

out = Path(str(Path(__file__).resolve().parent.parent / "resultados") + r"\eventos_vigencia.json")
out.write_text(json.dumps(eventos, ensure_ascii=False, indent=1), encoding="utf-8")
print()
print(f"  {len(eventos)} eventos guardados en {out.name}")
