"""Build a working sheet for writing Golden items, with everything derivable
already filled in.

Writing a Golden item means filling ~25 fields (`PROTOCOLO_GOLDEN.md` §5). Doing
that by hand for 60 questions is unsustainable, and most of those fields are not
a human decision: `document_id`, `artifact_id`, `sha256`, `emisor_id`,
`chunk_uid_snapshot`, the persisted silo and every derived field come from the
catalog and the database.

This sheet separates the two things:

- what ONLY a person can decide — the question, which domains it needs, the
  reference answer, the domain of the evidence fragment, whether the distractor
  really is one;
- everything else, which is generated afterwards from the catalog and the
  snapshot.

That reduces the human work to five fields per item instead of twenty-five.

⚠️ It does NOT write questions. Proximity is computed by the embedding and is a
search aid; whether a pair is a real collision is decided by reading, as
`PROTOCOLO_GOLDEN.md` requires. The domain of the distractor must come from
human review of its content — never from the automatic `silo`, `silo_scores` or
the router output.

STRICTLY READ-ONLY over the database.

[ES] Arma una planilla de trabajo para escribir ítems del Golden, con todo lo
derivable ya completado.

Escribir un ítem del Golden implica llenar ~25 campos (`PROTOCOLO_GOLDEN.md`
§5). Hacerlo a mano para 60 preguntas es insostenible, y la mayoría de esos
campos no son una decisión humana: `document_id`, `artifact_id`, `sha256`,
`emisor_id`, `chunk_uid_snapshot`, el silo persistido y todos los campos
derivados salen del catálogo y de la base.

Esta planilla separa las dos cosas:

- lo que SOLO puede decidir una persona: la pregunta, qué dominios necesita, la
  respuesta de referencia, el dominio del fragmento de evidencia, si el
  distractor lo es de verdad;
- todo lo demás, que se genera después desde el catálogo y el snapshot.

Eso baja el trabajo humano a cinco campos por ítem en lugar de veinticinco.

⚠️ NO escribe preguntas. La cercanía la calcula el embedding y es una ayuda de
búsqueda; que un par sea una colisión real se decide leyendo, como exige
`PROTOCOLO_GOLDEN.md`. El dominio del distractor debe salir de revisión humana
de su contenido, nunca del `silo` automático, de `silo_scores` ni de la salida
del router.

ESTRICTAMENTE DE SOLO LECTURA sobre la base.
"""

import argparse
import csv
import random
import re
from pathlib import Path

from multirag.config import SILOS
from multirag.db import conectar
from multirag.paths import DATA_DIR, EXPERIMENTS_DIR
from scripts.diagnostics.plantilla_golden import PLANTILLA_HTML


CATALOGO = DATA_DIR / "catalog" / "metadatos_curados.csv"

SALIDA_PREDETERMINADA = EXPERIMENTS_DIR / "planilla_golden_v1.html"

LARGO_MINIMO = 400

PATRON_ADMINISTRATIVO = re.compile(
    r"arch[ií]vese|comun[ií]quese|publ[ií]quese|reg[ií]strese",
    re.IGNORECASE,
)

# Docling's table serializer emits "row, column = value".
# [ES] El serializador de tablas de Docling emite "fila, columna = valor".
PATRON_TABLA = re.compile(r"=\s")

SEMILLA = 17


def cargar_catalogo() -> dict:
    """document_id -> catalog data, including its human domains.

    [ES] document_id -> datos del catálogo, incluidos sus dominios humanos.
    """
    catalogo = {}

    with CATALOGO.open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            documento = (fila.get("document_id") or "").strip()

            if not documento:
                continue

            crudos = {
                valor.strip()
                for valor in (
                    fila.get("dominios_documentales") or ""
                ).split("|")
                if valor.strip()
            }

            catalogo[documento] = {
                "fuente": fila.get("fuente", ""),
                "titulo": fila.get("titulo_oficial", ""),
                "emisor": fila.get("emisor_nombre", ""),
                "tipo": fila.get("tipo_documento", ""),
                "humanos": crudos,
                "silos": crudos & set(SILOS),
            }

    return catalogo


def es_sustantivo(contenido: str) -> bool:
    """Rough filter for fragments with matter of their own.

    [ES] Filtro grueso de fragmentos con materia propia.
    """
    if not contenido or len(contenido) < LARGO_MINIMO:
        return False

    return not PATRON_ADMINISTRATIVO.search(contenido[:400])


def leer_chunks(cursor) -> list[dict]:
    """Read every chunk with its document. Read-only.

    [ES] Lee cada chunk con su documento. Solo lectura.
    """
    cursor.execute(
        """
        SELECT chunk_uid, document_id, fuente, titulo, contenido, hierarchy
        FROM chunks
        WHERE chunk_uid IS NOT NULL AND document_id IS NOT NULL
        ORDER BY chunk_uid
        """
    )

    return [
        {
            "chunk_uid": uid,
            "document_id": documento,
            "fuente": fuente,
            "titulo": titulo or "",
            "contenido": contenido or "",
            "hierarchy": hierarchy or [],
        }
        for uid, documento, fuente, titulo, contenido, hierarchy in cursor.fetchall()
    ]


def vecino_de_otro_dominio(cursor, chunk_uid: str, documentos_ajenos: list[str]):
    """The nearest fragment from documents of other domains.

    [ES] El fragmento más cercano entre documentos de otros dominios.
    """
    cursor.execute(
        """
        SELECT c.chunk_uid, c.document_id, c.titulo, c.contenido,
               1 - (c.embedding <=> a.embedding) AS similitud
        FROM chunks AS c
        CROSS JOIN (
            SELECT embedding FROM chunks WHERE chunk_uid = %s
        ) AS a
        WHERE c.document_id = ANY(%s)
          AND c.chunk_uid <> %s
          AND length(c.contenido) >= %s
        ORDER BY c.embedding <=> a.embedding
        LIMIT 1
        """,
        (chunk_uid, documentos_ajenos, chunk_uid, LARGO_MINIMO),
    )

    return cursor.fetchone()


def limpiar(texto: str, largo: int) -> str:
    """Collapse whitespace and cut.

    [ES] Colapsa espacios y recorta.
    """
    plano = " ".join((texto or "").split())

    return plano[:largo] + ("..." if len(plano) > largo else "")


def _escapar(texto: str) -> str:
    """Escape text for safe HTML interpolation.

    [ES] Escapa el texto para interpolarlo en HTML de forma segura.
    """
    return (
        str(texto)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def renderizar_html(items) -> str:
    """Render the sheet as a self-contained interactive HTML page.

    The real gain over markdown is not the styling: it is that the fields can
    be typed into, the work survives closing the tab, and everything written
    comes back out with one button. A sheet that has to be transcribed by hand
    does not get filled.

    [ES] Representa la planilla como una pagina HTML interactiva y autonoma.

    La ganancia real sobre markdown no es el estilo: es que los campos se
    pueden tipear, que el trabajo sobrevive a cerrar la pestana, y que todo lo
    escrito sale con un boton. Una planilla que hay que transcribir a mano no
    se completa.
    """
    tarjetas = []

    for item in items:
        marca = (
            '<p class="marca-tabla">La evidencia es una tabla. '
            "Estos ítems son los que demuestran la parte multimodal "
            "de la tesis: priorizálos.</p>"
            if item["es_tabla"]
            else ""
        )

        tarjetas.append(f"""
<article class="item" id="item-{item['numero']}" data-item="{item['numero']}">
  <header class="item-cabecera">
    <span class="numero">Ítem {item['numero']}</span>
    <span class="estado" data-estado>sin empezar</span>
  </header>
  {marca}

  <section class="fragmento evidencia">
    <div class="rol">Evidencia <span class="dominio">{_escapar(item['dominio'])}</span></div>
    <p class="procedencia">
      <strong>{_escapar(item['fuente'])}</strong>
      <span>{_escapar(item['tipo'])}</span>
      <span>{_escapar(item['emisor'])}</span>
    </p>
    <p class="ubicacion">{_escapar(item['document_id'])} &middot; {_escapar(item['ruta'] or 'sin ruta de sección')}</p>
    <div class="texto" data-texto>{_escapar(item['evidencia'])}</div>
    <button class="ver-mas" type="button" data-vermas>Ver todo</button>
  </section>

  <section class="fragmento distractor">
    <div class="rol">Distractor candidato
      <span class="dominio">{_escapar(item['dominio_distractor'])}</span>
      <span class="similitud">parecido {item['similitud']:.2f}</span>
    </div>
    <p class="procedencia"><strong>{_escapar(item['fuente_distractor'])}</strong></p>
    <div class="texto" data-texto>{_escapar(item['distractor'])}</div>
    <button class="ver-mas" type="button" data-vermas>Ver todo</button>
  </section>

  <section class="completar">
    <label>
      <span>Pregunta</span>
      <textarea rows="2" data-campo="pregunta"
        placeholder="La consulta, como la haría alguien que trabaja en el sector"></textarea>
    </label>
    <label>
      <span>Respuesta de referencia</span>
      <textarea rows="2" data-campo="respuesta_referencia"
        placeholder="La respuesta correcta, en una o dos oraciones"></textarea>
    </label>
    <div class="fila">
      <label>
        <span>Silos necesarios</span>
        <input type="text" data-campo="silos_necesarios" value="{_escapar(item['dominio'])}">
      </label>
      <label>
        <span>Dominio de la evidencia</span>
        <input type="text" data-campo="dominios_evidencia" value="{_escapar(item['dominio'])}">
      </label>
      <label>
        <span>El distractor sirve</span>
        <select data-campo="distractor_valido">
          <option value="">elegir</option>
          <option value="si">Sí, se parece pero no responde</option>
          <option value="no">No, también responde</option>
        </select>
      </label>
    </div>
    <p class="identidad">
      evidencia <code>{item['chunk_evidencia'][:16]}...</code> &middot;
      distractor <code>{item['chunk_distractor'][:16]}...</code>
    </p>
  </section>
</article>""")

    identidad = ",\n".join(
        '    {{numero: "{n}", evidencia: "{e}", distractor: "{d}"}}'.format(
            n=item["numero"],
            e=item["chunk_evidencia"],
            d=item["chunk_distractor"],
        )
        for item in items
    )

    return (
        PLANTILLA_HTML
        .replace("__TARJETAS__", "\n".join(tarjetas))
        .replace("__IDENTIDAD__", identidad)
        .replace("__TOTAL__", str(len(items)))
    )


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.

    [ES] Construye la interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Arma la planilla de trabajo para escribir ítems del Golden. "
            "Solo lectura."
        )
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=SALIDA_PREDETERMINADA,
        help="Archivo markdown a generar. No sobrescribe.",
    )
    parser.add_argument(
        "--items",
        type=int,
        default=15,
        help="Cuántos bloques preparar. Por defecto 15.",
    )
    parser.add_argument(
        "--similitud-minima",
        type=float,
        default=0.60,
        help="Un distractor por debajo de esto no es plausible.",
    )
    return parser


def main() -> None:
    """Generate the sheet.

    [ES] Genera la planilla.
    """
    argumentos = construir_parser().parse_args()
    salida = Path(argumentos.salida).resolve()

    if salida.exists():
        raise SystemExit(
            f"La salida ya existe y no será sobrescrita: {salida}"
        )

    catalogo = cargar_catalogo()

    claros = {
        documento: next(iter(datos["silos"]))
        for documento, datos in catalogo.items()
        if len(datos["silos"]) == 1
    }

    conexion = conectar()
    items = []

    try:
        with conexion.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            chunks = leer_chunks(cursor)

            candidatos = [
                chunk
                for chunk in chunks
                if chunk["document_id"] in claros
                and es_sustantivo(chunk["contenido"])
            ]

            sorteador = random.Random(SEMILLA)
            por_dominio: dict[str, list] = {}

            for chunk in candidatos:
                por_dominio.setdefault(
                    claros[chunk["document_id"]], []
                ).append(chunk)

            cupo = max(1, argumentos.items // max(1, len(por_dominio)))
            elegidas = []

            for dominio in sorted(por_dominio):
                elegidas += sorteador.sample(
                    por_dominio[dominio],
                    min(cupo, len(por_dominio[dominio])),
                )

            for ancla in sorted(elegidas, key=lambda c: c["chunk_uid"]):
                dominio = claros[ancla["document_id"]]
                datos = catalogo[ancla["document_id"]]

                ajenos = [
                    documento
                    for documento, entrada in catalogo.items()
                    if dominio not in entrada["silos"]
                ]

                vecino = (
                    vecino_de_otro_dominio(
                        cursor, ancla["chunk_uid"], ajenos
                    )
                    if ajenos
                    else None
                )

                if not vecino or float(vecino[4]) < argumentos.similitud_minima:
                    continue

                uid_d, doc_d, _titulo_d, texto_d, similitud = vecino
                datos_d = catalogo.get(doc_d, {})

                items.append(
                    {
                        "numero": len(items) + 1,
                        "dominio": dominio,
                        "es_tabla": bool(
                            PATRON_TABLA.search(ancla["contenido"])
                        ),
                        "fuente": datos["fuente"],
                        "tipo": datos["tipo"],
                        "emisor": datos["emisor"],
                        "document_id": ancla["document_id"],
                        "ruta": " > ".join(
                            p for p in ancla["hierarchy"] if p
                        ),
                        "evidencia": " ".join(ancla["contenido"].split()),
                        "chunk_evidencia": ancla["chunk_uid"],
                        "fuente_distractor": datos_d.get("fuente", doc_d),
                        "dominio_distractor": "|".join(
                            sorted(datos_d.get("silos", []))
                        ) or "?",
                        "distractor": " ".join((texto_d or "").split()),
                        "chunk_distractor": uid_d,
                        "similitud": float(similitud),
                    }
                )

        conexion.rollback()
    finally:
        conexion.close()

    if not items:
        raise SystemExit("Ningún par superó el umbral de similitud.")

    salida.parent.mkdir(parents=True, exist_ok=True)
    temporal = salida.with_name(f".{salida.name}.tmp")
    temporal.write_text(
        renderizar_html(items),
        encoding="utf-8",
        newline="\n",
    )
    temporal.replace(salida)

    print(f"bloques preparados: {len(items)}")
    print(f"con evidencia en tabla: {sum(i['es_tabla'] for i in items)}")
    print(f"planilla: {salida}")


if __name__ == "__main__":
    main()
