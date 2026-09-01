"""Generate a self-contained HTML page to label chunks comfortably.

One fragment at a time on the left; a fixed reference panel on the right
holds the operational criterion of every label, read from config so the page
never keeps its own copy of the vocabulary.

[ES] Genera una página HTML autocontenida para etiquetar chunks.

Un fragmento por vez a la izquierda; un panel fijo a la derecha con el
criterio operativo de cada etiqueta, leído desde config para que la página no
tenga su propia copia del vocabulario.
"""

import argparse
import csv
import json
from pathlib import Path

from multirag.config import MATERIALIDADES, SILOS


PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Etiquetado de chunks</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: system-ui, sans-serif; margin: 0; padding: 24px;
         padding-right: 380px; background: #f5f5f4; color: #1c1917; }
  .principal { max-width: 900px; margin: 0 auto; }
  header { display: flex; justify-content: space-between; align-items: baseline; }
  h1 { font-size: 18px; margin: 0; }
  .barra { height: 6px; background: #e7e5e4; border-radius: 3px; margin: 12px 0 20px; }
  .barra div { height: 100%; background: #0f766e; border-radius: 3px; }
  .titulo { font-weight: 600; margin-bottom: 6px; color: #44403c; }
  .meta { font-size: 13px; color: #78716c; margin-bottom: 8px; }
  .texto { background: #fff; border: 1px solid #d6d3d1; border-radius: 8px;
           padding: 20px; font-size: 17px; line-height: 1.7; white-space: pre-wrap;
           max-height: 45vh; overflow-y: auto; }
  fieldset { border: 1px solid #d6d3d1; border-radius: 8px; margin: 16px 0;
             padding: 12px 14px; background: #fff; }
  legend { font-weight: 600; font-size: 14px; padding: 0 6px; }
  button { font: inherit; padding: 9px 15px; margin: 3px 6px 3px 0; cursor: pointer;
           border: 1px solid #a8a29e; border-radius: 6px; background: #fff; }
  button.sel { background: #0f766e; color: #fff; border-color: #0f766e; }
  button:disabled { opacity: .4; cursor: not-allowed; }
  textarea { width: 100%; min-height: 55px; font: inherit; padding: 8px;
             border: 1px solid #d6d3d1; border-radius: 6px; }
  nav { display: flex; gap: 10px; margin-top: 18px; }
  nav button { flex: 1; }
  .exportar { background: #1c1917; color: #fff; border-color: #1c1917; }
  .aviso { color: #b45309; font-size: 14px; margin-top: 10px; }

  aside { position: fixed; top: 0; right: 0; bottom: 0; width: 360px;
          background: #fff; border-left: 1px solid #d6d3d1; padding: 20px;
          overflow-y: auto; font-size: 13px; line-height: 1.55; }
  aside h2 { font-size: 13px; text-transform: uppercase; letter-spacing: .04em;
             color: #78716c; margin: 18px 0 8px; }
  aside h2:first-child { margin-top: 0; }
  aside p { margin: 0 0 10px; color: #44403c; }
  aside b { color: #0f766e; }
  .regla { color: #b45309; font-weight: 600; border-top: 1px solid #e7e5e4;
           padding-top: 10px; }
</style>
</head>
<body>

<div class="principal">
  <header>
    <h1>Etiquetado de chunks</h1>
    <div><span id="pos"></span> · <span id="hechas"></span> completados</div>
  </header>
  <div class="barra"><div id="barra"></div></div>

  <div class="titulo" id="titulo"></div>
  <div class="meta" id="meta"></div>
  <div class="texto" id="texto"></div>

  <fieldset>
    <legend>1 · ¿Tiene materia propia, o es trámite?</legend>
    <div id="mat"></div>
  </fieldset>

  <fieldset>
    <legend>2 · ¿Qué materia? — solo si es sustantivo, podés marcar varias</legend>
    <div id="dom"></div>
  </fieldset>

  <fieldset>
    <legend>Observaciones — anotá acá si dudás</legend>
    <textarea id="obs"></textarea>
  </fieldset>

  <nav>
    <button id="ant">&larr; Anterior</button>
    <button id="sig">Siguiente &rarr;</button>
    <button id="exp" class="exportar">Descargar CSV</button>
  </nav>
  <div class="aviso" id="aviso"></div>
</div>

<aside>
  <h2>Materialidad</h2>
  <div id="critMat"></div>
  <h2>Dominios</h2>
  <div id="critDom"></div>
</aside>

<script>
const FILAS = __DATOS__;
const MATERIALIDADES = __MATERIALIDADES__;
const DOMINIOS = __DOMINIOS__;
const COLUMNAS = __COLUMNAS__;
const NOMBRE_SALIDA = __NOMBRE_SALIDA__;
let i = 0;
const $ = id => document.getElementById(id);

$('critMat').innerHTML =
  Object.entries(MATERIALIDADES)
    .map(([k, v]) => `<p><b>${k}</b> — ${v}</p>`).join('')
  + '<p class="regla">Clasificá por MATERIA, no por la forma del documento. '
  + 'Una ley o un decreto no son automáticamente «legal».</p>';

$('critDom').innerHTML =
  Object.entries(DOMINIOS)
    .map(([k, v]) => `<p><b>${k}</b> — ${v}</p>`).join('');

function pintar() {
  const f = FILAS[i];
  const claves = Object.keys(DOMINIOS);
  $('pos').textContent = `${i + 1} / ${FILAS.length}`;
  $('hechas').textContent = FILAS.filter(x => x.materialidad_humana).length;
  $('barra').style.width = ((i + 1) / FILAS.length * 100) + '%';
  $('titulo').textContent = f.titulo || '(sin título)';
  $('meta').textContent = `${(f.contenido || '').length} caracteres`;
  $('texto').textContent = f.contenido || '';
  $('obs').value = f.observaciones || '';

  $('mat').innerHTML = '';
  Object.keys(MATERIALIDADES).forEach(m => {
    const b = document.createElement('button');
    b.textContent = m;
    if (f.materialidad_humana === m) b.className = 'sel';
    b.onclick = () => {
      f.materialidad_humana = m;
      if (m !== 'sustantivo') f.dominios_humano = '';
      pintar();
    };
    $('mat').appendChild(b);
  });

  const activo = f.materialidad_humana === 'sustantivo';
  const puestos = (f.dominios_humano || '').split(',')
                    .map(s => s.trim()).filter(Boolean);
  $('dom').innerHTML = '';
  claves.forEach(d => {
    const b = document.createElement('button');
    b.textContent = d;
    b.disabled = !activo;
    if (puestos.includes(d)) b.className = 'sel';
    b.onclick = () => {
      const s = new Set(puestos);
      s.has(d) ? s.delete(d) : s.add(d);
      f.dominios_humano = claves.filter(x => s.has(x)).join(',');
      pintar();
    };
    $('dom').appendChild(b);
  });

  $('ant').disabled = i === 0;
  $('sig').disabled = i === FILAS.length - 1;
}

$('obs').oninput = e => { FILAS[i].observaciones = e.target.value; };
$('ant').onclick = () => { if (i > 0) { i--; pintar(); } };
$('sig').onclick = () => { if (i < FILAS.length - 1) { i++; pintar(); } };

$('exp').onclick = () => {
  const esc = v => '"' + String(v ?? '').replace(/"/g, '""') + '"';
  const lineas = [COLUMNAS.join(',')];
  FILAS.forEach(f => lineas.push(COLUMNAS.map(c => esc(f[c])).join(',')));
  const blob = new Blob(['\\ufeff' + lineas.join('\\r\\n')],
                        {type: 'text/csv;charset=utf-8'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = NOMBRE_SALIDA;
  a.click();
  $('aviso').textContent = 'CSV descargado. Guardalo aparte, no pises el original.';
};

document.onkeydown = e => {
  if (e.target.tagName === 'TEXTAREA') return;
  if (e.key === 'ArrowRight') $('sig').click();
  if (e.key === 'ArrowLeft') $('ant').click();
};

pintar();
</script>
</body>
</html>
"""


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.

    [ES] Construye la interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Genera una página HTML autocontenida para etiquetar la "
            "planilla de chunks."
        )
    )
    parser.add_argument(
        "--planilla",
        type=Path,
        required=True,
        help="CSV de etiquetado producido por la selección.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        required=True,
        help="Archivo HTML nuevo.",
    )
    return parser


def main() -> None:
    """Read the sheet and write the offline labelling page.

    [ES] Lee la planilla y escribe la página de etiquetado offline.
    """
    argumentos = construir_parser().parse_args()
    salida = argumentos.salida.resolve()

    if salida.exists():
        raise SystemExit(f"ERROR: la salida ya existe: {salida}")

    with argumentos.planilla.resolve().open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as archivo:
        lector = csv.DictReader(archivo)
        columnas = list(lector.fieldnames or [])
        filas = list(lector)

    if not filas:
        raise SystemExit("ERROR: la planilla no tiene filas.")

    html = (
        PLANTILLA
        .replace("__DATOS__", json.dumps(filas, ensure_ascii=False))
        .replace(
            "__MATERIALIDADES__",
            json.dumps(MATERIALIDADES, ensure_ascii=False),
        )
        .replace("__DOMINIOS__", json.dumps(SILOS, ensure_ascii=False))
        .replace("__COLUMNAS__", json.dumps(columnas))
        .replace(
            "__NOMBRE_SALIDA__",
            json.dumps(f"{argumentos.planilla.stem}_completada.csv"),
        )
    )

    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(html, encoding="utf-8")

    print(f"Filas embebidas : {len(filas)}")
    print(f"Dominios        : {list(SILOS)}")
    print(f"Materialidades  : {list(MATERIALIDADES)}")
    print(f"Página          : {salida}")
    print("Abrila con doble clic. No necesita internet.")


if __name__ == "__main__":
    main()