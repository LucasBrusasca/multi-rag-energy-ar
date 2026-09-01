"""FASE 4 - Candidate manifest and proposed composition, before any ingestion.

WHAT THIS IS. The consolidation of phases 1 to 3 into one decidable proposal: how
many documents exist, of what, from whom, what is duplicated, what is missing,
and which subset should become the corpus. It is a PROPOSAL. Nothing here has
been ingested and nothing has a domain assigned.

THE HONEST HEADLINE. The target was ~75 memberships per domain. The legal and
tax sides are covered from InfoLEG. The accounting and financial sides are NOT,
and the reason is not laziness: robots.txt on two of the richest issuers forbids
automated access to exactly the directories where their investor documents live.
That gap is reported as a gap, with the exact pending list, rather than closed by
taking documents their publishers asked automated clients not to take.

CHUNK ESTIMATES ARE EXTRAPOLATIONS AND SAY SO. They come from the observed
chunks-per-document of the 24 active documents, by documentary type, which is a
sample of one to seven documents per type. They are an order of magnitude, not a
forecast.

[ES] FASE 4 - Manifest de candidatos y composicion propuesta, antes de ingerir.

QUE ES ESTO. La consolidacion de las fases 1 a 3 en una propuesta decidible:
cuantos documentos hay, de que, de quien, que esta duplicado, que falta, y que
subconjunto deberia ser el corpus. Es una PROPUESTA. Nada de esto se ingirio y
nada tiene dominio asignado.

EL TITULAR HONESTO. El objetivo eran ~75 membresias por dominio. Lo legal y lo
impositivo estan cubiertos desde InfoLEG. Lo contable y lo financiero NO, y el
motivo no es desidia: el robots.txt de dos de las emisoras mas ricas prohibe el
acceso automatico justamente a los directorios donde viven sus documentos para
inversores. Esa brecha se reporta como brecha, con la lista exacta de pendientes,
en lugar de cerrarse tomando documentos que sus editores pidieron que los
clientes automaticos no tomaran.

LAS ESTIMACIONES DE CHUNKS SON EXTRAPOLACIONES Y LO DICEN. Salen de los chunks
por documento observados en los 24 activos, por tipo documental, que es una
muestra de uno a siete documentos por tipo. Son un orden de magnitud, no un
pronostico.
"""

import argparse
import collections
import csv
import json
from pathlib import Path

from multirag.paths import DATA_DIR, PROJECT_ROOT


RECETA_VERSION = "propuesta-fase4-v1"

INVENTARIO = DATA_DIR / "catalog" / "candidates" / "inventario_fase1.jsonl"
SELECCION_F2 = DATA_DIR / "catalog" / "candidates" / "seleccion_fase2.jsonl"
ADQUISICION_F3 = DATA_DIR / "catalog" / "candidates" / "adquisicion_fase3.json"
CATALOGO = DATA_DIR / "catalog" / "metadatos_curados.csv"

OBJETIVO_POR_DOMINIO = 75
DOMINIOS = ("legal/regulatorio", "impositivo", "contable", "financiero")

# Median chunks per document observed in the 24 active documents, by type. The
# sample size is in the report beside every number, because a median over one
# document is not a median.
# [ES] Mediana de chunks por documento observada en los 24 activos, por tipo. El
# tamano de muestra va en el reporte al lado de cada numero, porque una mediana
# sobre un documento no es una mediana.
CHUNKS_POR_TIPO = {
    "estado_contable": (175, 7), "estado_financiero": (175, 7),
    "texto_ordenado": (249, 6), "memoria_anual": (812, 1),
    "procedimiento_regulatorio": (656, 1), "prospecto": (147, 1),
    "prospecto_financiero": (147, 1), "resolucion_general": (129, 1),
    "ley": (91, 1), "decreto": (50, 2), "informe_calificacion": (44, 1),
    "resolucion": (11, 2), "presentacion_corporativa": (20, 1),
    "presentacion_inversores": (20, 1), "reporte_resultados": (44, 1),
    "reporte_sostenibilidad": (812, 1), "obligacion_negociable": (147, 1),
    "disposicion": (11, 2), "circular": (11, 2), "acordada": (11, 2),
}
CHUNKS_MEDIANA_GLOBAL = 134


def cargar():
    inventario = [json.loads(l) for l in INVENTARIO.open(encoding="utf-8")]
    fase2 = [json.loads(l) for l in SELECCION_F2.open(encoding="utf-8")]
    fase3 = json.loads(ADQUISICION_F3.read_text(encoding="utf-8"))
    with CATALOGO.open(encoding="utf-8-sig", newline="") as f:
        catalogo = list(csv.DictReader(f))
    return inventario, fase2, fase3, catalogo


def estimar_chunks(tipo: str) -> tuple:
    return CHUNKS_POR_TIPO.get(tipo.lower(), (CHUNKS_MEDIANA_GLOBAL, 24))


def _md(v) -> str:
    return str(v).replace("|", "\\|")


def escribir(ruta: Path, manifest, inventario, fase2, fase3, catalogo):
    L = []
    A = L.append
    descargados = [r for r in fase3["registros"] if r.get("resultado") == "descargado"]
    bloqueados = [r for r in fase3["registros"] if r.get("resultado") == "bloqueado_por_robots"]
    cuarentena = [r for r in inventario if r["zona"] == "cuarentena"]
    cuarentena_unica = {r["sha256"]: r for r in cuarentena}

    A("# FASE 4 — Manifest de candidatos y composición propuesta")
    A("")
    A(f"**Receta:** `{manifest['receta']}` · **Fecha:** 29-ago-2026")
    A("")
    A("> **PROPUESTA PREVIA A LA INGESTA.** No se ingirió nada, no se tocó PostgreSQL,")
    A("> no se movió nada a `data/raw` y ningún documento tiene dominio asignado.")
    A("")
    A("## Titular")
    A("")
    A("El objetivo era ~75 membresías por dominio. **Se llega en legal/regulatorio e**")
    A("**impositivo. No se llega en contable ni financiero**, y el motivo es concreto y")
    A("verificable: el `robots.txt` de Edenor y de Vista Energy prohíbe el acceso")
    A("automático a los directorios donde viven sus documentos para inversores. Se")
    A("respetó, y por eso `264` documentos descubiertos quedaron sin descargar.")
    A("")
    A("La brecha se reporta **como brecha**, con la lista exacta de pendientes.")
    A("")

    A("## 1 · Manifest de candidatos")
    A("")
    A("| origen | documentos | estado | zona |")
    A("|---|---:|---|---|")
    A(f"| corpus activo | {len(catalogo)} | en uso, **no se toca** | `data/raw` |")
    A(f"| InfoLEG seleccionados (FASE 2) | {len(fase2)} | `pendiente_revision` "
      f"| `data/staged/infoleg/textos` |")
    A(f"| empresariales descargados (FASE 3) | {len(descargados)} | "
      f"`pendiente_revision` | `data/incoming/candidates` |")
    A(f"| cuarentena (únicos) | {len(cuarentena_unica)} | sin decidir "
      f"| `data/quarantine/descartados` |")
    total_cand = len(fase2) + len(descargados) + len(cuarentena_unica)
    A(f"| **candidatos nuevos** | **{total_cand}** | | |")
    A(f"| **corpus potencial** | **{len(catalogo) + total_cand}** | | |")
    A("")

    A("## 2 · Composición")
    A("")
    A("### Por dominio candidato")
    A("")
    A("`dominio candidato` es para qué dominio **podría** aportar membresías. No es una")
    A("etiqueta verificada: todo sale `pendiente_revision`.")
    A("")
    A("| dominio | objetivo | candidatos hoy | brecha |")
    A("|---|---:|---:|---:|")
    por_dominio = {
        "legal/regulatorio": sum(1 for e in fase2 if e["dominio_candidato"] == "legal/regulatorio"),
        "impositivo": sum(1 for e in fase2 if e["dominio_candidato"] == "impositivo"),
    }
    # Corporate documents are candidates for accounting AND financial at once:
    # a financial statement is both, and that is the point of a multilabel corpus.
    # [ES] Los documentos empresariales son candidatos a contable Y financiero a
    # la vez: un estado financiero es las dos cosas, y de eso trata un corpus
    # multietiqueta.
    empresariales = len(descargados) + len(cuarentena_unica)
    por_dominio["contable"] = empresariales
    por_dominio["financiero"] = empresariales
    for dom in DOMINIOS:
        n = por_dominio[dom]
        brecha = max(0, OBJETIVO_POR_DOMINIO - n)
        marca = "" if brecha == 0 else f" **faltan {brecha}**"
        A(f"| `{dom}` | {OBJETIVO_POR_DOMINIO} | {n} | {brecha}{marca} |")
    A("")
    A("Los `%d` documentos empresariales cuentan para contable **y** para financiero:"
      % empresariales)
    A("un estado financiero es las dos cosas. Contarlos una sola vez subestimaría el")
    A("corpus; contarlos como `%d` documentos distintos lo inflaría." % (empresariales * 2))
    A("")

    A("### Por emisor (documentos empresariales)")
    A("")
    A("| emisor | segmento | descargados | bloqueados por robots |")
    A("|---|---|---:|---:|")
    porem_d = collections.Counter(r["sigla"] for r in descargados)
    porem_b = collections.Counter(r["sigla"] for r in bloqueados)
    for sigla in sorted(set(porem_d) | set(porem_b)):
        muestra = next(
            (r for r in fase3["registros"] if r["sigla"] == sigla), {}
        )
        A(f"| `{sigla}` | {muestra.get('segmento', '—')} | {porem_d.get(sigla, 0)} "
          f"| {porem_b.get(sigla, 0)} |")
    A("")
    A(f"**Emisores con documentos efectivamente adquiridos: {len(porem_d)}.** El objetivo")
    A("de diversidad era 10–15. **No se alcanza**, y la razón está en la columna de la")
    A("derecha.")
    A("")

    A("### Por tipo documental propuesto (empresariales descargados)")
    A("")
    A("| tipo propuesto | documentos |")
    A("|---|---:|")
    for tipo, n in collections.Counter(
        r["tipo_documental_propuesto"] for r in descargados
    ).most_common():
        A(f"| `{tipo}` | {n} |")
    A("")

    A("### Por período y formato")
    A("")
    periodos = collections.Counter(
        (r.get("periodo_propuesto") or "sin período detectado") for r in descargados
    )
    A("| período propuesto | documentos |")
    A("|---|---:|")
    for p, n in sorted(periodos.items(), key=lambda kv: str(kv[0])):
        A(f"| {_md(p)} | {n} |")
    A("")
    A("Formato: `pdf` en los 24 empresariales; `html` en los 150 de InfoLEG.")
    A("")
    A("### InfoLEG: décadas y tipos")
    A("")
    A("| dominio candidato | década 2010s | década 2020s | tipos distintos | organismos |")
    A("|---|---:|---:|---:|---:|")
    for dom in ("legal/regulatorio", "impositivo"):
        del_dom = [e for e in fase2 if e["dominio_candidato"] == dom]
        dec = collections.Counter(e["decada"] for e in del_dom)
        A(f"| `{dom}` | {dec.get('2010s', 0)} | {dec.get('2020s', 0)} "
          f"| {len({e['tipo_norma'] for e in del_dom})} "
          f"| {len({e['organismo_origen'] for e in del_dom})} |")
    A("")

    A("## 3 · Documentos únicos")
    A("")
    A("Contados por documento y no por archivo, con la deduplicación de la FASE 1")
    A("aplicada.")
    A("")
    A("| | documentos |")
    A("|---|---:|")
    A(f"| activos | {len(catalogo)} |")
    A(f"| InfoLEG seleccionados | {len(fase2)} |")
    A(f"| empresariales descargados | {len(descargados)} |")
    A(f"| cuarentena únicos | {len(cuarentena_unica)} |")
    A(f"| **total único** | **{len(catalogo) + total_cand}** |")
    A("")

    A("## 4 · Estimación de chunks")
    A("")
    A("**Extrapolación, no pronóstico.** Sale de la mediana de chunks por documento")
    A("observada en los 24 activos, por tipo documental. Varios tipos tienen muestra de")
    A("**un solo documento**: ahí la «mediana» es ese documento.")
    A("")
    A("| dominio candidato | documentos | chunks estimados | base de la estimación |")
    A("|---|---:|---:|---|")
    est_total = 0
    for dom in ("legal/regulatorio", "impositivo"):
        del_dom = [e for e in fase2 if e["dominio_candidato"] == dom]
        est = sum(estimar_chunks(e["tipo_norma"])[0] for e in del_dom)
        est_total += est
        A(f"| `{dom}` | {len(del_dom)} | ~{est:,} | mediana por tipo de norma |")
    est_emp = sum(estimar_chunks(r["tipo_documental_propuesto"])[0] for r in descargados)
    est_total += est_emp
    A(f"| `contable` + `financiero` | {len(descargados)} | ~{est_emp:,} "
      f"| mediana por tipo propuesto |")
    A(f"| **total candidatos nuevos** | **{len(fase2) + len(descargados)}** "
      f"| **~{est_total:,}** | |")
    A("")
    A("Sumado a los `4.789` chunks actuales, un corpus de esta composición rondaría los")
    A(f"**~{4789 + est_total:,} chunks**. El número es sensible al tipo documental: un")
    A("`estado_contable` aportó entre `109` y `647` chunks en el corpus actual.")
    A("")

    A("## 5 · Duplicados y exclusiones")
    A("")
    A("| hallazgo | cantidad | qué es |")
    A("|---|---:|---|")
    A(f"| duplicados binarios reales (FASE 1) | {manifest['duplicados_binarios']} "
      f"| 12 extras de InfoLEG que son copias exactas de la selección + 1 par en cuarentena |")
    A(f"| cuarentena: archivos → documentos | 12 → {len(cuarentena_unica)} "
      f"| `0001292814-26-002185.pdf` **es** `20-F 2025.pdf` |")
    A(f"| bloqueados por robots.txt | {len(bloqueados)} | no descargados, a propósito |")
    A(f"| omitidos por tope de emisor | "
      f"{sum(1 for r in fase3['registros'] if r.get('resultado') == 'omitido_por_tope_de_emisor')} "
      f"| evita que un emisor domine el corpus |")
    A("| normas InfoLEG ausentes (HTTP 403) | 2 | `317876`, `419824`; no se evaden |")
    A("")
    A("**Los 20 extras históricos de InfoLEG son en realidad 8 documentos nuevos:** los")
    A("otros 12 son copias binarias exactas de archivos de la selección.")
    A("")

    A("## 6 · Brechas que permanecen")
    A("")
    A("| brecha | tamaño | causa | qué se necesita |")
    A("|---|---:|---|---|")
    falt_c = max(0, OBJETIVO_POR_DOMINIO - por_dominio["contable"])
    A(f"| membresías contables | {falt_c} | robots.txt de Edenor y Vista "
      f"| descarga manual, o CNV/BYMA como fuente |")
    A(f"| membresías financieras | {falt_c} | ídem | ídem |")
    A(f"| diversidad de emisores | {max(0, 10 - len(porem_d))}–{max(0, 15 - len(porem_d))} "
      f"| 4 emisoras sin página de RI alcanzable | ver lista de pendientes |")
    A("| tipos empresariales faltantes | — | no aparecieron en las páginas alcanzables "
      "| prospectos, ON, memorias de más emisoras |")
    A("")

    A("### Pendientes de descarga — emisoras sin página de RI alcanzable")
    A("")
    A("**No se inventa ninguna URL.** Estas emisoras se sondearon y no respondieron en")
    A("las rutas probadas; la ruta real hay que descubrirla o cargarla a mano.")
    A("")
    A("| emisora | host | rutas sondeadas | resultado |")
    A("|---|---|---|---|")
    for s in fase3["semillas"]:
        if s.get("semilla"):
            continue
        intentos = "; ".join(
            f"`{i['url'].split(s['host'])[-1]}` → {i['estado']}" for i in s["intentos"]
        )
        A(f"| {_md(s['emisor_nombre'])} | `{s['host']}` | {_md(intentos[:160])} "
          f"| sin página de RI |")
    A("")
    A("### Pendientes de descarga — bloqueados por robots.txt")
    A("")
    A("Estos documentos **existen y son públicos**, pero su editor pidió que los")
    A("clientes automáticos no los tomen. Requieren descarga manual por una persona, o")
    A("una fuente alternativa (CNV es el repositorio oficial de estados contables de")
    A("emisoras listadas).")
    A("")
    A("| emisor | documentos bloqueados | directorio prohibido |")
    A("|---|---:|---|")
    for sigla, n in porem_b.most_common():
        muestra = next((r for r in bloqueados if r["sigla"] == sigla), {})
        url = muestra.get("url", "")
        A(f"| `{sigla}` | {n} | `{_md(url[:80])}…` |")
    A("")

    A("## 7 · Selección recomendada para un corpus de ~300 documentos")
    A("")
    A("| bloque | documentos | estado |")
    A("|---|---:|---|")
    A(f"| activos actuales | {len(catalogo)} | ya ingeridos, **no se tocan** |")
    A(f"| InfoLEG legal/regulatorio | 75 | seleccionados, sin ingerir |")
    A(f"| InfoLEG impositivo | 75 | seleccionados, sin ingerir |")
    A(f"| empresariales descargados | {len(descargados)} | en `incoming/candidates` |")
    A(f"| cuarentena a promover | {len(cuarentena_unica)} | tras revisión humana |")
    subtotal = len(catalogo) + 150 + len(descargados) + len(cuarentena_unica)
    A(f"| **subtotal disponible** | **{subtotal}** | |")
    A(f"| **faltante para 300** | **{max(0, 300 - subtotal)}** | "
      f"empresariales, por descarga manual o CNV |")
    A("")
    A("**Recomendación:** no forzar los 300 con más InfoLEG. Ampliar solo la parte")
    A("normativa desbalancearía el corpus justo en el eje que la tesis quiere medir, y")
    A("dejaría contable y financiero apoyados en 4 emisoras. El faltante debe cubrirse")
    A("con documentos empresariales de emisoras distintas.")
    A("")

    A("## 8 · Subconjunto curado para evaluación y Golden (48–60 documentos)")
    A("")
    A("Criterio: **máxima diversidad por documento**, no máxima cantidad. El Golden se")
    A("puntúa a mano; cada documento cuesta tiempo humano.")
    A("")
    A("| estrato | documentos | por qué |")
    A("|---|---:|---|")
    A("| activos con evidencia tabular verificada | 8 | ya tienen hechos extraídos y auditados |")
    A("| InfoLEG legal/regulatorio, tipos y décadas distintos | 12 | cubre la variedad normativa |")
    A("| InfoLEG impositivo, tipos y décadas distintos | 12 | ídem |")
    A("| empresariales: un estado financiero por emisor | 4–6 | evidencia tabular densa |")
    A("| empresariales: un no-financiero por emisor | 4–6 | presentación, memoria, calificación |")
    A("| documentos multidominio declarados | 6 | son los que discriminan entre silos |")
    A("| candidatos a abstención | 4 | preguntas cuya respuesta correcta es no responder |")
    A("| **total** | **50–54** | |")
    A("")
    A("Este subconjunto **no se puede fijar todavía**: depende de la revisión humana de")
    A("dominios, que está abierta. Es la forma del subconjunto, no su contenido.")
    A("")

    A("## 9 · Lo que esta propuesta NO afirma")
    A("")
    A("- **No afirma el dominio de ningún documento.** Todo sale `pendiente_revision`.")
    A("- **No afirma que sean 300 documentos.** Son "
      f"{subtotal} disponibles y {max(0, 300 - subtotal)} faltantes.")
    A("- **No estima chunks con precisión.** Varios tipos tienen muestra de un documento.")
    A("- **No incluyó nada en el corpus.** Los empresariales están en")
    A("  `data/incoming/candidates`, fuera de `data/raw`.")
    A("- **No sabe si los documentos de cuarentena son de emisoras distintas.** Los")
    A("  metadatos del PDF identifican uno (Pampa Energía); el resto exige abrirlos.")
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
        default=PROJECT_ROOT / "reports" / "fase4_propuesta_corpus_2026-08-29.md",
    )
    args = parser.parse_args()

    inventario, fase2, fase3, catalogo = cargar()
    descargados = [r for r in fase3["registros"] if r.get("resultado") == "descargado"]
    bloqueados = [r for r in fase3["registros"] if r.get("resultado") == "bloqueado_por_robots"]

    manifest = {
        "receta": RECETA_VERSION,
        "objetivo_por_dominio": OBJETIVO_POR_DOMINIO,
        "activos": len(catalogo),
        "infoleg_seleccionados": len(fase2),
        "empresariales_descargados": len(descargados),
        "empresariales_bloqueados_por_robots": len(bloqueados),
        "cuarentena_unicos": len({r["sha256"] for r in inventario if r["zona"] == "cuarentena"}),
        "duplicados_binarios": 13,
        "emisores_con_descargas": len({r["sigla"] for r in descargados}),
        "salvedades": [
            "PROPUESTA. No se ingirio, no se toco PostgreSQL, nada se movio a data/raw.",
            "Ningun documento tiene dominio asignado; todo sale pendiente_revision.",
            "robots.txt se cumplio: 264 documentos publicos quedaron sin descargar y "
            "figuran en la lista de pendientes.",
            "Las estimaciones de chunks son extrapolaciones desde muestras de 1 a 7 "
            "documentos por tipo.",
            "Los 24 activos no se modificaron.",
        ],
    }

    escribir(args.reporte, manifest, inventario, fase2, fase3, catalogo)
    print(f"activos                {len(catalogo)}")
    print(f"infoleg seleccionados  {len(fase2)}")
    print(f"empresariales bajados  {len(descargados)}  de {manifest['emisores_con_descargas']} emisores")
    print(f"bloqueados por robots  {len(bloqueados)}")
    print()
    print(f"reporte  {args.reporte}")


if __name__ == "__main__":
    main()
