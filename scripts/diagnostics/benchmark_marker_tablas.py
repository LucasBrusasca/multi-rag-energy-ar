"""Benchmark estructural y reproducible de Docling contra Marker en PDFs.

El benchmark no evalua si el Markdown "se ve bien". Evalua si una relacion
tabular verificable sobrevive al parseo:

    concepto -> valor -> encabezados de columna -> unidad -> paginas fuente

Docling se lee desde los JSON de ``auditar_tablas.py``. Marker se consume en
formato ``chunks`` porque conserva bloque, pagina, bounding box y HTML. Tambien
puede ejecutarse en un interprete aislado mediante ``--run-marker``.

No modifica la base, no reingiere documentos y rechaza planillas: los XLSX se
auditan por sus celdas nativas con ``auditar_excel.py``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
import unicodedata
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
AUDIT_ROOT = ROOT / "experimentos" / "auditoria_tablas"
DEFAULT_MANIFEST = AUDIT_ROOT / "casos_semilla_parsers.json"
DEFAULT_DOCLING = AUDIT_ROOT / "docling"
DEFAULT_MARKER = AUDIT_ROOT / "marker"
DEFAULT_OUTPUT = AUDIT_ROOT / "comparacion_parsers"
MARKER_PAGE_POLICY = (
    "Marker 2.0.0 chunks puede emitir page=374 para IDs /page/0/...; "
    "se usa el segmento /page/N del ID como procedencia canonica y solo se "
    "recurre al campo page cuando el ID no la contiene."
)


def normalizar(texto: str) -> str:
    """Normaliza para comparar texto, sin alterar cifras ni signos."""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(texto.casefold().split())


def coincide(texto: str, variantes: Iterable[str]) -> bool:
    base = normalizar(texto)
    return any(normalizar(variante) in base for variante in variantes)


@dataclass(frozen=True)
class Celda:
    texto: str
    fila: int
    fila_fin: int
    columna: int
    columna_fin: int

    def comparte_fila(self, otra: "Celda") -> bool:
        return self.fila < otra.fila_fin and otra.fila < self.fila_fin

    def comparte_columna(self, otra: "Celda") -> bool:
        return self.columna < otra.columna_fin and otra.columna < self.columna_fin


@dataclass(frozen=True)
class Tabla:
    parser: str
    documento: str
    identificador: str
    paginas: tuple[int, ...]
    celdas: tuple[Celda, ...]


class _ParserTablasHTML(HTMLParser):
    """Convierte tablas HTML simples, incluidos rowspan/colspan, a una grilla."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tablas: list[list[Celda]] = []
        self._profundidad = 0
        self._celdas: list[Celda] = []
        self._ocupadas: set[tuple[int, int]] = set()
        self._fila = -1
        self._columna = 0
        self._activa: dict | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        atributos = dict(attrs)
        if tag == "table":
            if self._profundidad == 0:
                self._celdas = []
                self._ocupadas = set()
                self._fila = -1
            self._profundidad += 1
            return

        if self._profundidad != 1:
            return

        if tag == "tr":
            self._fila += 1
            self._columna = 0
        elif tag in {"td", "th"}:
            while (self._fila, self._columna) in self._ocupadas:
                self._columna += 1
            rowspan = max(1, int(atributos.get("rowspan", "1") or "1"))
            colspan = max(1, int(atributos.get("colspan", "1") or "1"))
            self._activa = {
                "partes": [],
                "fila": self._fila,
                "fila_fin": self._fila + rowspan,
                "columna": self._columna,
                "columna_fin": self._columna + colspan,
            }
            for fila in range(self._fila, self._fila + rowspan):
                for columna in range(self._columna, self._columna + colspan):
                    self._ocupadas.add((fila, columna))
            self._columna += colspan
        elif tag == "br" and self._activa is not None:
            self._activa["partes"].append(" ")

    def handle_data(self, data: str) -> None:
        if self._profundidad == 1 and self._activa is not None:
            self._activa["partes"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._profundidad == 1 and self._activa:
            self._celdas.append(
                Celda(
                    texto=" ".join("".join(self._activa["partes"]).split()),
                    fila=self._activa["fila"],
                    fila_fin=self._activa["fila_fin"],
                    columna=self._activa["columna"],
                    columna_fin=self._activa["columna_fin"],
                )
            )
            self._activa = None
        elif tag == "table" and self._profundidad:
            self._profundidad -= 1
            if self._profundidad == 0:
                self.tablas.append(list(self._celdas))


def tablas_desde_html(html: str) -> list[list[Celda]]:
    parser = _ParserTablasHTML()
    parser.feed(html or "")
    parser.close()
    return parser.tablas


def cargar_docling(directorio: Path) -> dict[str, list[Tabla]]:
    """Carga la salida estructurada ya cacheada por la auditoria Docling."""
    documentos: dict[str, list[Tabla]] = {}
    for ruta in sorted(directorio.glob("*.json")):
        data = json.loads(ruta.read_text(encoding="utf-8"))
        nombre = data.get("archivo", f"{ruta.stem}.pdf")
        tablas = []
        for tabla in data.get("tablas", []):
            celdas = tuple(
                Celda(
                    texto=c.get("texto", ""),
                    fila=int(c["fila"]),
                    fila_fin=int(c["fila_fin"]),
                    columna=int(c["col"]),
                    columna_fin=int(c["col_fin"]),
                )
                for c in tabla.get("celdas", [])
            )
            tablas.append(
                Tabla(
                    parser="docling-current",
                    documento=nombre,
                    identificador=tabla.get("self_ref", ""),
                    paginas=tuple(int(p) for p in tabla.get("paginas", [])),
                    celdas=celdas,
                )
            )
        documentos[nombre] = tablas
    return documentos


def cargar_marker_archivo(
    ruta: Path, documento: str, parser_id: str, page_base: int = 0
) -> list[Tabla]:
    """Carga un JSON de Marker generado con ``--output_format chunks``."""
    data = json.loads(ruta.read_text(encoding="utf-8"))
    if not isinstance(data.get("blocks"), list):
        raise ValueError(
            f"{ruta} no es salida Marker chunks: falta la lista 'blocks'"
        )

    resultado = []
    for bloque in data["blocks"]:
        tipo = str(bloque.get("block_type", "")).split(".")[-1].casefold()
        if tipo != "table":
            continue
        # Marker 2.0.0 has a provenance bug in ChunkRenderer: it derives
        # ``page`` from the final numeric segment of the Page block ID. In the
        # observed output that yielded page=374 for /page/0/Table/11. Every
        # child block still carries the real page in its stable ID, so that is
        # the canonical source here. [ES] El ID conserva la pagina correcta.
        coincidencia_pagina = re.search(
            r"(?:^|/)page/(\d+)(?:/|$)",
            str(bloque.get("id", "")),
            flags=re.IGNORECASE,
        )
        pagina_cruda = (
            int(coincidencia_pagina.group(1))
            if coincidencia_pagina
            else int(bloque.get("page", page_base))
        )
        pagina = pagina_cruda - page_base + 1
        for indice, celdas in enumerate(tablas_desde_html(bloque.get("html", ""))):
            resultado.append(
                Tabla(
                    parser=parser_id,
                    documento=documento,
                    identificador=f"{bloque.get('id', '')}#{indice}",
                    paginas=(pagina,),
                    celdas=tuple(celdas),
                )
            )
    return resultado


def descubrir_corridas_marker(
    directorio: Path, page_base: int = 0
) -> dict[str, dict[str, list[Tabla]]]:
    """Descubre una o mas corridas Marker bajo un directorio de resultados."""
    corridas: dict[str, dict[str, list[Tabla]]] = {}
    if not directorio.is_dir():
        return corridas

    for ruta in sorted(directorio.rglob("*.json")):
        if ruta.name.endswith("_meta.json") or ruta.name == "run_metadata.json":
            continue
        try:
            data = json.loads(ruta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict) or not isinstance(data.get("blocks"), list):
            continue

        relativo = ruta.relative_to(directorio)
        partes_corrida = relativo.parts[:-2]
        etiqueta = "/".join(partes_corrida) or "importada"
        parser_id = f"marker:{etiqueta}"
        documento = f"{ruta.stem}.pdf"
        corridas.setdefault(parser_id, {})[documento] = cargar_marker_archivo(
            ruta, documento, parser_id, page_base=page_base
        )
    return corridas


def _grupos_requeridos(caso: dict) -> list[list[str]]:
    grupos = [caso["concepto"], caso["valor"]]
    grupos.extend(caso.get("encabezados", []))
    if caso.get("unidad"):
        grupos.append(caso["unidad"])
    return grupos


def _tabla_contiene_grupos(tabla: Tabla, grupos: list[list[str]]) -> bool:
    return all(
        any(coincide(celda.texto, variantes) for celda in tabla.celdas)
        for variantes in grupos
    )


def evaluar_caso(caso: dict, tablas: list[Tabla] | None) -> dict:
    """Puntua contenido, localidad, asociacion y procedencia por separado."""
    if tablas is None:
        return {
            "case_id": caso["case_id"],
            "documento": caso["documento"],
            "disponible": False,
            "componentes": False,
            "misma_tabla": False,
            "asociacion": False,
            "procedencia": False,
            "respondible": False,
            "tabla": None,
            "paginas_observadas": [],
        }

    grupos = _grupos_requeridos(caso)
    todas = [celda for tabla in tablas for celda in tabla.celdas]
    componentes = all(
        any(coincide(celda.texto, variantes) for celda in todas)
        for variantes in grupos
    )
    misma_tabla = any(_tabla_contiene_grupos(tabla, grupos) for tabla in tablas)

    candidatas: list[Tabla] = []
    for tabla in tablas:
        valores = [c for c in tabla.celdas if coincide(c.texto, caso["valor"])]
        conceptos = [c for c in tabla.celdas if coincide(c.texto, caso["concepto"])]
        for valor in valores:
            fila_correcta = any(concepto.comparte_fila(valor) for concepto in conceptos)
            columnas_correctas = all(
                any(
                    coincide(encabezado.texto, variantes)
                    and encabezado.comparte_columna(valor)
                    for encabezado in tabla.celdas
                )
                for variantes in caso.get("encabezados", [])
            )
            unidad_presente = not caso.get("unidad") or any(
                coincide(celda.texto, caso["unidad"]) for celda in tabla.celdas
            )
            if fila_correcta and columnas_correctas and unidad_presente:
                candidatas.append(tabla)
                break

    asociacion = bool(candidatas)
    paginas_esperadas = set(int(p) for p in caso.get("paginas", []))
    candidata_procedente = next(
        (
            tabla
            for tabla in candidatas
            if paginas_esperadas.issubset(set(tabla.paginas))
        ),
        None,
    )
    procedencia = candidata_procedente is not None
    muestra = candidata_procedente or (candidatas[0] if candidatas else None)

    return {
        "case_id": caso["case_id"],
        "documento": caso["documento"],
        "disponible": True,
        "componentes": componentes,
        "misma_tabla": misma_tabla,
        "asociacion": asociacion,
        "procedencia": procedencia,
        "respondible": asociacion and procedencia,
        "tabla": muestra.identificador if muestra else None,
        "paginas_observadas": list(muestra.paginas) if muestra else [],
    }


def resumir(resultados: list[dict]) -> dict:
    total = len(resultados)
    return {
        "casos": total,
        "disponibles": sum(r["disponible"] for r in resultados),
        "componentes": sum(r["componentes"] for r in resultados),
        "misma_tabla": sum(r["misma_tabla"] for r in resultados),
        "asociacion": sum(r["asociacion"] for r in resultados),
        "procedencia": sum(r["procedencia"] for r in resultados),
        "respondibles": sum(r["respondible"] for r in resultados),
    }


def validar_manifest(manifest: dict) -> None:
    if not isinstance(manifest.get("cases"), list) or not manifest["cases"]:
        raise ValueError("El manifest debe contener una lista no vacia 'cases'")
    requeridas = {"case_id", "documento", "concepto", "valor", "paginas"}
    ids = set()
    for caso in manifest["cases"]:
        faltantes = requeridas - set(caso)
        if faltantes:
            raise ValueError(f"Caso incompleto {caso}: faltan {sorted(faltantes)}")
        if caso["case_id"] in ids:
            raise ValueError(f"case_id duplicado: {caso['case_id']}")
        ids.add(caso["case_id"])
        if Path(caso["documento"]).suffix.casefold() not in {".pdf"}:
            raise ValueError(
                f"{caso['documento']}: Marker se limita a PDF; "
                "use auditar_excel.py para XLSX"
            )


def _hash_archivo(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def _version_marker(python_marker: Path) -> str:
    comando = [
        str(python_marker),
        "-c",
        "import importlib.metadata as m; print(m.version('marker-pdf'))",
    ]
    proceso = subprocess.run(comando, capture_output=True, text=True, check=False)
    if proceso.returncode:
        raise RuntimeError(
            "El interprete indicado no tiene marker-pdf instalado: "
            + (proceso.stderr or proceso.stdout).strip()
        )
    return proceso.stdout.strip()


def ejecutar_marker(
    python_marker: Path,
    documentos: list[Path],
    destino: Path,
    modo: str,
    repeticiones: int,
    llama_cpp_binary: Path | None = None,
    repeticion_inicial: int = 1,
) -> list[dict]:
    """Ejecuta Marker aislado; no importa sus dependencias en este proceso."""
    version = _version_marker(python_marker)
    metadatos = []
    entrada_cli = (
        "from marker.scripts.convert_single import convert_single_cli; "
        "convert_single_cli()"
    )
    entorno = os.environ.copy()
    if llama_cpp_binary is not None:
        if not llama_cpp_binary.is_file():
            raise FileNotFoundError(f"No existe llama-server: {llama_cpp_binary}")
        entorno["LLAMA_CPP_BINARY"] = str(llama_cpp_binary.resolve())

    try:
        import psutil
    except ImportError:  # pragma: no cover - la corrida sigue sin esta metrica
        psutil = None

    for repeticion in range(
        repeticion_inicial, repeticion_inicial + repeticiones
    ):
        corrida = destino / modo / f"run_{repeticion:02d}"
        for documento in documentos:
            inicio = time.perf_counter()
            comando = [
                str(python_marker),
                "-c",
                entrada_cli,
                str(documento),
                "--output_dir",
                str(corrida),
                "--output_format",
                "chunks",
                "--mode",
                modo,
                "--disable_image_extraction",
            ]
            logs = destino / "logs" / modo
            logs.mkdir(parents=True, exist_ok=True)
            log_path = logs / f"run_{repeticion:02d}_{documento.stem}.log"
            pico_rss = None
            with log_path.open("w", encoding="utf-8", errors="replace") as log:
                proceso = subprocess.Popen(
                    comando,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=entorno,
                )
                while proceso.poll() is None:
                    if psutil is not None:
                        try:
                            raiz = psutil.Process(proceso.pid)
                            procesos = [raiz, *raiz.children(recursive=True)]
                            rss = sum(
                                p.memory_info().rss
                                for p in procesos
                                if p.is_running()
                            )
                            pico_rss = max(pico_rss or 0, rss)
                        except (psutil.Error, OSError):
                            pass
                    time.sleep(0.5)
                retorno = proceso.wait()
            segundos = time.perf_counter() - inicio
            salida = corrida / documento.stem / f"{documento.stem}.json"
            if retorno or not salida.is_file():
                detalle = log_path.read_text(
                    encoding="utf-8", errors="replace"
                )[-3000:]
                raise RuntimeError(
                    f"Marker fallo para {documento.name} (codigo "
                    f"{retorno}):\n{detalle}"
                )
            metadatos.append(
                {
                    "documento": documento.name,
                    "modo": modo,
                    "repeticion": repeticion,
                    "marker_version": version,
                    "llama_cpp_binary": entorno.get("LLAMA_CPP_BINARY"),
                    "segundos": round(segundos, 3),
                    "peak_process_tree_rss_bytes": pico_rss,
                    "sha256_salida": _hash_archivo(salida),
                    "salida": str(salida.relative_to(ROOT)),
                    "log": str(log_path.relative_to(ROOT)),
                }
            )

    destino.mkdir(parents=True, exist_ok=True)
    (destino / "run_metadata.json").write_text(
        json.dumps(metadatos, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    return metadatos


def redactar_informe(payload: dict) -> str:
    manifest = payload["manifest"]
    lineas = [
        "# Benchmark estructural Docling–Marker",
        "",
        "Este informe es exploratorio y de solo lectura. No modifica la ingesta ni la base.",
        "",
        f"**Estado de la verdad:** `{manifest.get('truth_status', 'no declarado')}`. ",
        "Los casos deben verificarse visualmente y congelarse antes de usarlos como Golden confirmatorio.",
        "",
        f"**Política de página Marker:** {payload['marker_page_policy']}",
        "",
        "## Resultado agregado",
        "",
        "| parser/corrida | disponibles | componentes | misma tabla | asociación fila/columna | procedencia | respondibles |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for parser_id, datos in payload["parsers"].items():
        r = datos["resumen"]
        total = r["casos"]
        evaluables = r["disponibles"]
        denominador = evaluables if evaluables else 0
        lineas.append(
            f"| {parser_id} | {r['disponibles']}/{total} | "
            f"{r['componentes']}/{denominador} | {r['misma_tabla']}/{denominador} | "
            f"{r['asociacion']}/{denominador} | {r['procedencia']}/{denominador} | "
            f"**{r['respondibles']}/{denominador}** |"
        )

    lineas.extend(
        [
            "",
            "`componentes` solo exige que los datos aparezcan en alguna tabla. "
            "`respondibles` exige además asociación estructural correcta y todas las páginas fuente. "
            "Las métricas de calidad usan como denominador solo los casos disponibles para esa corrida.",
            "",
            "## Comparación pareada contra Docling",
            "",
            "| corrida Marker | casos compartidos | Docling respondibles | Marker respondibles | diferencia |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for comparacion in payload["comparaciones_pareadas"]:
        lineas.append(
            f"| {comparacion['marker']} | {comparacion['casos_compartidos']} | "
            f"{comparacion['docling_respondibles']} | "
            f"{comparacion['marker_respondibles']} | "
            f"{comparacion['diferencia']:+d} |"
        )

    lineas.extend(
        [
            "",
            "## Detalle por caso",
            "",
            "| parser | caso | componentes | misma tabla | asociación | procedencia | respondible | páginas observadas |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for parser_id, datos in payload["parsers"].items():
        for caso in datos["casos"]:
            marca = lambda valor: "sí" if valor else "no"
            lineas.append(
                f"| {parser_id} | {caso['case_id']} | {marca(caso['componentes'])} | "
                f"{marca(caso['misma_tabla'])} | {marca(caso['asociacion'])} | "
                f"{marca(caso['procedencia'])} | **{marca(caso['respondible'])}** | "
                f"{caso['paginas_observadas'] or '—'} |"
            )

    lineas.extend(
        [
            "",
            "## Regla de decisión",
            "",
            "Marker no reemplaza a Docling por velocidad, marketing ni apariencia. Solo se promueve "
            "si mejora relaciones respondibles en los casos congelados, conserva procedencia y su costo "
            "operativo es aceptable. Excel permanece en lectura nativa con openpyxl.",
            "",
        ]
    )
    return "\n".join(lineas)


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark estructural Docling–Marker, sin reingesta."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--docling-dir", type=Path, default=DEFAULT_DOCLING)
    parser.add_argument("--marker-dir", type=Path, default=DEFAULT_MARKER)
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--marker-page-base",
        type=int,
        choices=(0, 1),
        default=0,
        help="Base de pagina en Marker chunks; la version 2.0.0 usa 0.",
    )
    parser.add_argument("--run-marker", action="store_true")
    parser.add_argument("--marker-python", type=Path)
    parser.add_argument(
        "--llama-cpp-binary",
        type=Path,
        help="Ruta a llama-server(.exe), requerido por Surya 0.22.1 en CPU.",
    )
    parser.add_argument("--modo-marker", choices=("fast", "balanced"), default="fast")
    parser.add_argument("--repeticiones", type=int, default=1)
    parser.add_argument(
        "--repeticion-inicial",
        type=int,
        default=1,
        help="Numero inicial: permite agregar run_02 sin pisar run_01.",
    )
    parser.add_argument(
        "--documentos-marker",
        nargs="*",
        help=(
            "Subconjunto de PDFs a convertir con Marker. La evaluacion conserva "
            "todos los casos y marca como no disponibles los documentos ausentes."
        ),
    )
    return parser


def main() -> None:
    args = construir_parser().parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    validar_manifest(manifest)

    if args.run_marker:
        if args.marker_python is None:
            raise SystemExit("--run-marker requiere --marker-python aislado")
        nombres_manifest = {caso["documento"] for caso in manifest["cases"]}
        nombres = set(args.documentos_marker or nombres_manifest)
        desconocidos = nombres - nombres_manifest
        if desconocidos:
            raise ValueError(
                "--documentos-marker fuera del manifest: "
                + ", ".join(sorted(desconocidos))
            )
        documentos = sorted(ROOT / "data" / "raw" / nombre for nombre in nombres)
        faltantes = [str(ruta) for ruta in documentos if not ruta.is_file()]
        if faltantes:
            raise FileNotFoundError("Documentos ausentes: " + ", ".join(faltantes))
        ejecutar_marker(
            args.marker_python,
            documentos,
            args.marker_dir,
            args.modo_marker,
            max(1, args.repeticiones),
            llama_cpp_binary=args.llama_cpp_binary,
            repeticion_inicial=max(1, args.repeticion_inicial),
        )

    fuentes: dict[str, dict[str, list[Tabla]]] = {
        "docling-current": cargar_docling(args.docling_dir)
    }
    fuentes.update(
        descubrir_corridas_marker(args.marker_dir, page_base=args.marker_page_base)
    )

    parsers = {}
    for parser_id, documentos in fuentes.items():
        resultados = [
            evaluar_caso(caso, documentos.get(caso["documento"]))
            for caso in manifest["cases"]
        ]
        parsers[parser_id] = {"resumen": resumir(resultados), "casos": resultados}

    docling_por_caso = {
        caso["case_id"]: caso for caso in parsers["docling-current"]["casos"]
    }
    comparaciones_pareadas = []
    for parser_id, datos in parsers.items():
        if parser_id == "docling-current":
            continue
        compartidos = [
            caso
            for caso in datos["casos"]
            if caso["disponible"]
            and docling_por_caso[caso["case_id"]]["disponible"]
        ]
        docling_respondibles = sum(
            docling_por_caso[caso["case_id"]]["respondible"] for caso in compartidos
        )
        marker_respondibles = sum(caso["respondible"] for caso in compartidos)
        comparaciones_pareadas.append(
            {
                "marker": parser_id,
                "casos_compartidos": len(compartidos),
                "docling_respondibles": docling_respondibles,
                "marker_respondibles": marker_respondibles,
                "diferencia": marker_respondibles - docling_respondibles,
            }
        )

    payload = {
        "schema_version": "parser-table-benchmark-v1",
        "marker_page_policy": MARKER_PAGE_POLICY,
        "manifest": {
            "path": str(args.manifest.resolve()),
            "truth_status": manifest.get("truth_status"),
            "cases": len(manifest["cases"]),
        },
        "parsers": parsers,
        "comparaciones_pareadas": comparaciones_pareadas,
    }
    args.salida.mkdir(parents=True, exist_ok=True)
    json_path = args.salida / "resultados.json"
    md_path = args.salida / "informe.md"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(redactar_informe(payload), encoding="utf-8", newline="\n")

    print(f"parsers: {', '.join(parsers)}")
    print(f"resultados: {json_path.resolve()}")
    print(f"informe: {md_path.resolve()}")


if __name__ == "__main__":
    main()
