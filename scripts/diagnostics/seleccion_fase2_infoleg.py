"""FASE 2 - Reproducible selection of ~75 legal/regulatory + ~75 tax norms.

DETERMINISTIC, NOT RANDOM. The selection is stratified by acquisition criterion,
norm type and decade, allocated proportionally with largest remainders, and
ordered inside each stratum by norm id. Same pool, same output, on any machine,
with no seed to lose. A random draw would be defensible too; a draw nobody can
reproduce would not.

THE ACQUISITION CRITERION IS NOT A DOMAIN LABEL. These norms were found by
searching InfoLEG for `energia` and `impositivo`. That is how they were located,
not what they are about. Every record carries `dominio_adquisicion` and
`estado = pendiente_revision`, and nothing here promotes a search filter to
human truth. A norm found under `energia` that turns out to be purely procedural
is a finding for the reviewer, not an error to hide.

THE TWO HTTP 403 ARE NOT EVADED. Norms `317876` and `419824` answered 403 during
acquisition. They are absent from the pool, they are named in the report, and
the quota is completed by the SAME rule from the remaining pool - not by hand
picking two replacements.

NOTHING IS INGESTED. This writes a proposal.

[ES] FASE 2 - Seleccion reproducible de ~75 normas legal/regulatorias + ~75
impositivas.

DETERMINISTICA, NO ALEATORIA. La seleccion se estratifica por criterio de
adquisicion, tipo de norma y decada, se asigna proporcionalmente por restos
mayores, y se ordena dentro de cada estrato por id de norma. Mismo pool, misma
salida, en cualquier maquina, sin semilla que perder. Un sorteo aleatorio tambien
seria defendible; un sorteo que nadie puede reproducir, no.

EL CRITERIO DE ADQUISICION NO ES UNA ETIQUETA DE DOMINIO. Estas normas se
encontraron buscando en InfoLEG por `energia` e `impositivo`. Asi se las ubico,
no de que tratan. Cada registro lleva `dominio_adquisicion` y
`estado = pendiente_revision`, y aca nada promueve un filtro de busqueda a verdad
humana. Una norma encontrada bajo `energia` que resulte puramente procedimental
es un hallazgo para el revisor, no un error que ocultar.

LOS DOS HTTP 403 NO SE EVADEN. Las normas `317876` y `419824` respondieron 403 en
la adquisicion. Estan ausentes del pool, se nombran en el reporte, y el cupo se
completa con la MISMA regla desde el pool restante, no eligiendo dos reemplazos a
mano.

NO SE INGIERE NADA. Esto escribe una propuesta.
"""

import argparse
import collections
import csv
import json
from pathlib import Path

from multirag.paths import DATA_DIR, PROJECT_ROOT


RECETA_VERSION = "seleccion-fase2-v1"

SELECCION = DATA_DIR / "incoming" / "infoleg" / "seleccion.csv"
INVENTARIO = DATA_DIR / "catalog" / "candidates" / "inventario_fase1.jsonl"

CUPO = {"energia": 75, "impositivo": 75}

# What each acquisition domain is a candidate for. Candidate: the reviewer
# decides, not this table.
# [ES] Para que dominio es candidato cada dominio de adquisicion. Candidato: lo
# decide el revisor, no esta tabla.
DOMINIO_CANDIDATO = {
    "energia": "legal/regulatorio",
    "impositivo": "impositivo",
}


def decada(fecha: str) -> str:
    return (fecha or "????")[:3] + "0s"


def cargar_pool():
    """Norms that were selected, downloaded AND normalised, with their text hash.

    A norm that is in the selection but never arrived cannot be selected again
    by wishing. The pool is what exists.

    [ES] Normas que fueron seleccionadas, descargadas Y normalizadas, con su
    huella de texto.

    Una norma que esta en la seleccion pero nunca llego no se puede seleccionar
    de nuevo por voluntad. El pool es lo que existe.
    """
    with SELECCION.open(encoding="utf-8-sig", newline="") as f:
        seleccion = list(csv.DictReader(f))

    inventario = [json.loads(l) for l in INVENTARIO.open(encoding="utf-8")]
    normalizados = {
        r["id_norma"]: r for r in inventario if r["zona"] == "infoleg_normalizado"
    }

    pool, ausentes = [], []
    for fila in seleccion:
        registro = normalizados.get(fila["id_norma"])
        if registro is None:
            ausentes.append(fila)
            continue
        pool.append(
            {
                "id_norma": fila["id_norma"],
                "dominio_adquisicion": fila["dominio"],
                "criterio_adquisicion": fila["criterio"],
                "tipo_norma": fila["tipo_norma"],
                "numero_norma": fila["numero_norma"],
                "organismo_origen": fila["organismo_origen"],
                "fecha_sancion": fila["fecha_sancion"],
                "decada": decada(fila["fecha_sancion"]),
                "titulo_resumido": fila["titulo_resumido"],
                "url_origen": fila["url"],
                "ruta_normalizada": registro["ruta"],
                "sha256_archivo": registro["sha256"],
                "sha256_texto": registro["texto_sha256"],
                "caracteres_texto": registro.get("caracteres_texto"),
            }
        )
    return pool, ausentes


def reparto_por_restos_mayores(conteos: dict, cupo: int) -> dict:
    """Proportional allocation that adds up EXACTLY to the quota.

    Rounding each stratum on its own gives 73 or 78, never 75. Largest
    remainders close the gap deterministically, and ties break by stratum name
    so the result does not depend on dictionary order.

    [ES] Reparto proporcional que suma EXACTAMENTE el cupo.

    Redondear cada estrato por su cuenta da 73 o 78, nunca 75. Los restos
    mayores cierran la diferencia de forma deterministica, y los empates se
    rompen por nombre de estrato para que el resultado no dependa del orden de
    un diccionario.
    """
    total = sum(conteos.values())
    if total == 0:
        return {}
    exactos = {k: v * cupo / total for k, v in conteos.items()}
    base = {k: int(v) for k, v in exactos.items()}
    faltan = cupo - sum(base.values())
    orden = sorted(conteos, key=lambda k: (-(exactos[k] - base[k]), k))
    for k in orden[:faltan]:
        base[k] += 1
    # Never allocate more than the stratum holds.
    # [ES] Nunca asignar mas de lo que el estrato tiene.
    for k in base:
        base[k] = min(base[k], conteos[k])
    return base


def seleccionar(pool, dominio: str, cupo: int):
    """Stratified, deterministic, and deduplicated by normalised text.

    [ES] Estratificada, deterministica, y deduplicada por texto normalizado.
    """
    candidatos = [p for p in pool if p["dominio_adquisicion"] == dominio]

    estratos = collections.defaultdict(list)
    for p in candidatos:
        clave = f"{p['criterio_adquisicion']}|{p['tipo_norma']}|{p['decada']}"
        estratos[clave].append(p)
    for clave in estratos:
        estratos[clave].sort(key=lambda p: int(p["id_norma"]))

    asignacion = reparto_por_restos_mayores(
        {k: len(v) for k, v in estratos.items()}, cupo
    )

    elegidos, vistos_texto, descartados = [], set(), []
    for clave in sorted(estratos):
        tomados = 0
        objetivo = asignacion.get(clave, 0)
        for p in estratos[clave]:
            if tomados >= objetivo:
                break
            if p["sha256_texto"] in vistos_texto:
                descartados.append(dict(p, motivo="texto duplicado de otro elegido"))
                continue
            vistos_texto.add(p["sha256_texto"])
            elegidos.append(dict(p, estrato=clave))
            tomados += 1

    # The quota may fall short when a stratum ran out or lost members to
    # deduplication. It is completed by the SAME rule over the remaining pool,
    # never by hand.
    # [ES] El cupo puede quedar corto si un estrato se agoto o perdio miembros
    # por deduplicacion. Se completa con la MISMA regla sobre el pool restante,
    # nunca a mano.
    if len(elegidos) < cupo:
        ya = {p["id_norma"] for p in elegidos}
        resto = sorted(
            (p for p in candidatos if p["id_norma"] not in ya),
            key=lambda p: (p["criterio_adquisicion"], p["tipo_norma"],
                           p["decada"], int(p["id_norma"])),
        )
        for p in resto:
            if len(elegidos) >= cupo:
                break
            if p["sha256_texto"] in vistos_texto:
                continue
            vistos_texto.add(p["sha256_texto"])
            elegidos.append(dict(p, estrato="completado_por_la_misma_regla"))

    return elegidos, asignacion, descartados


def _md(v) -> str:
    return str(v).replace("|", "\\|")


def tabla_conteo(titulo, contador, total, A):
    A(f"**{titulo}**")
    A("")
    A("| valor | documentos | % |")
    A("|---|---:|---:|")
    for k, n in contador.most_common():
        A(f"| {_md(k)} | {n} | {n / total * 100:.0f} % |")
    A("")


def escribir_reporte(ruta: Path, manifest, elegidos, ausentes, descartados, asignaciones):
    L = []
    A = L.append
    A("# FASE 2 — Selección reproducible de normas InfoLEG")
    A("")
    A(f"**Receta:** `{manifest['receta']}` · **Fecha:** 29-ago-2026")
    A("")
    A("**Propuesta. No se ingirió nada.**")
    A("")
    A("## Salvedades, antes de los números")
    A("")
    for aviso in manifest["salvedades"]:
        A(f"- {aviso}")
    A("")

    A("## 1 · Resultado")
    A("")
    A("| dominio de adquisición | candidato a | seleccionados | pool disponible |")
    A("|---|---|---:|---:|")
    for dom, cupo in CUPO.items():
        n = sum(1 for e in elegidos if e["dominio_adquisicion"] == dom)
        A(f"| `{dom}` | {DOMINIO_CANDIDATO[dom]} | **{n}** / {cupo} "
          f"| {manifest['pool_por_dominio'][dom]} |")
    A(f"| **total** | | **{len(elegidos)}** | |")
    A("")

    A("## 2 · Los dos HTTP 403 — documentados, no evadidos")
    A("")
    if ausentes:
        A("| id_norma | dominio | tipo | organismo | título |")
        A("|---|---|---|---|---|")
        for a in ausentes:
            A(f"| `{a['id_norma']}` | {a['dominio']} | {a['tipo_norma']} "
              f"| {_md(a['organismo_origen'])} | {_md(a['titulo_resumido'][:60])} |")
        A("")
        A("No se intentó ningún rodeo. Estas normas quedan **fuera del pool**, y el cupo")
        A("se completó con la misma regla estratificada sobre las normas que sí están.")
        A("Sustituir a mano dos documentos elegidos por una persona rompería la")
        A("reproducibilidad de toda la selección para ganar dos documentos.")
    else:
        A("Ninguna norma de la selección quedó ausente.")
    A("")

    A("## 3 · Composición de lo seleccionado")
    A("")
    for dom in CUPO:
        del_dom = [e for e in elegidos if e["dominio_adquisicion"] == dom]
        if not del_dom:
            continue
        A(f"### `{dom}` — {len(del_dom)} documentos")
        A("")
        for campo, titulo in (
            ("tipo_norma", "Tipo de norma"),
            ("decada", "Década"),
            ("criterio_adquisicion", "Criterio de adquisición"),
            ("organismo_origen", "Organismo emisor"),
        ):
            tabla_conteo(titulo, collections.Counter(e[campo] for e in del_dom),
                         len(del_dom), A)

    A("## 4 · Concentración por organismo — limitación, no defecto corregido")
    A("")
    A("El Poder Ejecutivo Nacional concentra buena parte de las normas porque **así se**")
    A("**dicta la normativa argentina**: los decretos salen del PEN. La estratificación")
    A("es por tipo de norma y década, que reparte organismos de forma indirecta, y **no**")
    A("se impuso un tope artificial por organismo: hacerlo distorsionaría la composición")
    A("real del corpus normativo para que una tabla se vea más pareja.")
    A("")
    A("| dominio | organismos distintos | organismo más frecuente | su participación |")
    A("|---|---:|---|---:|")
    for dom in CUPO:
        del_dom = [e for e in elegidos if e["dominio_adquisicion"] == dom]
        if not del_dom:
            continue
        c = collections.Counter(e["organismo_origen"] for e in del_dom)
        top, n = c.most_common(1)[0]
        A(f"| `{dom}` | {len(c)} | {_md(top)} | {n / len(del_dom) * 100:.0f} % |")
    A("")

    A("## 5 · Deduplicación aplicada dentro de la selección")
    A("")
    if descartados:
        A(f"{len(descartados)} norma(s) descartada(s) por tener el mismo texto")
        A("normalizado que otra ya elegida:")
        A("")
        A("| id_norma | motivo |")
        A("|---|---|")
        for d in descartados[:20]:
            A(f"| `{d['id_norma']}` | {d['motivo']} |")
    else:
        A("Ninguna. Ningún par de normas seleccionadas comparte texto normalizado.")
    A("")

    A("## 6 · Lo que esta selección NO afirma")
    A("")
    A("- **No afirma el dominio de ninguna norma.** `energia` e `impositivo` son")
    A("  criterios de búsqueda en InfoLEG. Cada registro sale con")
    A("  `estado = pendiente_revision` y su dominio queda por decidir con el mismo")
    A("  instrumento de revisión humana que los 24 actuales.")
    A("- **No afirma que sean 75 documentos de dominio legal.** Son 75 normas")
    A("  *candidatas* a aportar membresías legal/regulatorias.")
    A("- **No incluye nada en el corpus.** Es una propuesta previa a la ingesta.")
    A("")

    A("## Manifest")
    A("")
    A("```json")
    A(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    A("```")
    A("")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(L), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--reporte", type=Path,
        default=PROJECT_ROOT / "reports" / "fase2_seleccion_infoleg_2026-08-29.md",
    )
    parser.add_argument(
        "--jsonl", type=Path,
        default=DATA_DIR / "catalog" / "candidates" / "seleccion_fase2.jsonl",
    )
    args = parser.parse_args()

    pool, ausentes = cargar_pool()
    pool_por_dominio = collections.Counter(p["dominio_adquisicion"] for p in pool)

    elegidos, descartados, asignaciones = [], [], {}
    for dominio, cupo in CUPO.items():
        sel, asign, desc = seleccionar(pool, dominio, cupo)
        elegidos.extend(sel)
        descartados.extend(desc)
        asignaciones[dominio] = asign

    for e in elegidos:
        e["dominio_candidato"] = DOMINIO_CANDIDATO[e["dominio_adquisicion"]]
        e["estado"] = "pendiente_revision"
        e["fase"] = "fase2_infoleg"

    manifest = {
        "receta": RECETA_VERSION,
        "cupo": dict(CUPO),
        "seleccionados": len(elegidos),
        "pool_por_dominio": dict(pool_por_dominio),
        "estratificacion": "criterio_adquisicion x tipo_norma x decada",
        "reparto": "proporcional por restos mayores; orden por id_norma",
        "deduplicacion": "texto normalizado; ninguna norma repetida",
        "ausentes_http_403": [a["id_norma"] for a in ausentes],
        "descartados_por_duplicado": len(descartados),
        "salvedades": [
            "PROPUESTA. No se ingirio nada y no se toco PostgreSQL.",
            "`energia`/`impositivo` son CRITERIOS DE BUSQUEDA en InfoLEG, no "
            "etiquetas de dominio verificadas. Todo sale pendiente_revision.",
            "Los dos HTTP 403 no se evaden: se documentan y el cupo se completa con "
            "la misma regla sobre el pool restante.",
            "No se impuso tope por organismo: el PEN concentra decretos porque asi se "
            "dicta la normativa, y forzar una tabla pareja distorsionaria el corpus.",
            "Seleccion deterministica: mismo pool, misma salida, sin semilla.",
        ],
    }

    args.jsonl.parent.mkdir(parents=True, exist_ok=True)
    with args.jsonl.open("w", encoding="utf-8") as f:
        for e in elegidos:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    escribir_reporte(args.reporte, manifest, elegidos, ausentes, descartados, asignaciones)

    for dom in CUPO:
        n = sum(1 for e in elegidos if e["dominio_adquisicion"] == dom)
        orgs = len({e["organismo_origen"] for e in elegidos
                    if e["dominio_adquisicion"] == dom})
        print(f"{dom:12} {n:3}/{CUPO[dom]}  organismos distintos: {orgs}")
    print(f"ausentes 403 {[a['id_norma'] for a in ausentes]}")
    print()
    print(f"reporte  {args.reporte}")
    print(f"jsonl    {args.jsonl}")


if __name__ == "__main__":
    main()
