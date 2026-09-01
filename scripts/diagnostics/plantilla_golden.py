"""HTML template for the Golden worksheet.

Kept apart from the generator because it is presentation, not logic, and mixing
a long template into the module that queries the database makes both harder to
read.

The page is self-contained on purpose: it has to open from a file, from a
shared link or from a phone, without a server and without network access beyond
the font stylesheet.

[ES] Plantilla HTML de la planilla del Golden.

Se mantiene aparte del generador porque es presentación, no lógica, y mezclar
una plantilla larga dentro del módulo que consulta la base vuelve ilegibles a
los dos.

La página es autónoma a propósito: tiene que abrirse desde un archivo, desde un
enlace compartido o desde un teléfono, sin servidor y sin más red que la hoja de
estilos de las tipografías.
"""

PLANTILLA_HTML = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Planilla del Golden</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>
:root {
  --papel: #f7f8fa;
  --superficie: #ffffff;
  --tinta: #16202e;
  --tinta-suave: #5a6675;
  --borde: #dde2ea;
  --evidencia: #1f3d6b;
  --evidencia-fondo: #eef2f8;
  --distractor: #a8641b;
  --distractor-fondo: #fbf3e8;
  --tabla: #0f6b5c;
  --tabla-fondo: #e9f4f1;
  --foco: #1f3d6b;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --papel: #12161c;
    --superficie: #1a1f27;
    --tinta: #e6eaf0;
    --tinta-suave: #9aa5b4;
    --borde: #2c333e;
    --evidencia: #8fb3e8;
    --evidencia-fondo: #1b2534;
    --distractor: #e0a259;
    --distractor-fondo: #2a2118;
    --tabla: #5fc7b2;
    --tabla-fondo: #162926;
    --foco: #8fb3e8;
  }
}
:root[data-theme="dark"] {
  --papel: #12161c;
  --superficie: #1a1f27;
  --tinta: #e6eaf0;
  --tinta-suave: #9aa5b4;
  --borde: #2c333e;
  --evidencia: #8fb3e8;
  --evidencia-fondo: #1b2534;
  --distractor: #e0a259;
  --distractor-fondo: #2a2118;
  --tabla: #5fc7b2;
  --tabla-fondo: #162926;
  --foco: #8fb3e8;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--papel);
  color: var(--tinta);
  font-family: "IBM Plex Sans", system-ui, -apple-system, sans-serif;
  font-size: 16px;
  line-height: 1.6;
}
.barra {
  position: sticky; top: 0; z-index: 10;
  display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
  padding: .7rem clamp(1rem, 4vw, 2.5rem);
  background: var(--superficie);
  border-bottom: 1px solid var(--borde);
}
.barra strong { font-size: .95rem; font-weight: 600; }
.progreso { flex: 1 1 8rem; height: 6px; background: var(--borde); border-radius: 3px; overflow: hidden; min-width: 6rem; }
.progreso > i { display: block; height: 100%; width: 0; background: var(--evidencia); transition: width .3s; }
.contador { font-variant-numeric: tabular-nums; font-size: .85rem; color: var(--tinta-suave); }
button {
  font: inherit; font-size: .85rem; font-weight: 500;
  padding: .45rem .9rem; border-radius: 6px; cursor: pointer;
  border: 1px solid var(--evidencia); background: var(--evidencia); color: var(--papel);
}
button.secundario { background: transparent; color: var(--evidencia); }
button:focus-visible, textarea:focus-visible, input:focus-visible, select:focus-visible {
  outline: 2px solid var(--foco); outline-offset: 2px;
}
main { max-width: 54rem; margin: 0 auto; padding: 0 clamp(1rem, 4vw, 2.5rem) 5rem; }
.intro { padding: 2.5rem 0 1rem; }
h1 {
  font-family: "Source Serif 4", Georgia, serif;
  font-size: clamp(1.9rem, 5vw, 2.6rem); font-weight: 600;
  line-height: 1.15; margin: 0 0 .6rem; text-wrap: balance;
}
h2 {
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 1.3rem; font-weight: 600; margin: 2.2rem 0 .6rem; text-wrap: balance;
}
.bajada { font-size: 1.05rem; color: var(--tinta-suave); margin: 0 0 1.5rem; max-width: 40rem; }
.intro p, .intro li { max-width: 40rem; }
.intro ol, .intro ul { padding-left: 1.2rem; }
.intro li { margin-bottom: .4rem; }
.cita {
  border-left: 3px solid var(--evidencia);
  padding: .2rem 0 .2rem 1rem; margin: 1rem 0;
  font-family: "Source Serif 4", Georgia, serif; color: var(--tinta-suave);
}
table.campos { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: .92rem; }
table.campos th, table.campos td { text-align: left; padding: .5rem .6rem; border-bottom: 1px solid var(--borde); vertical-align: top; }
table.campos th { font-weight: 600; white-space: nowrap; }
table.campos code { font-family: "IBM Plex Mono", monospace; font-size: .85em; }
.aviso {
  background: var(--distractor-fondo); border: 1px solid var(--distractor);
  border-radius: 8px; padding: .9rem 1.1rem; margin: 1.5rem 0; font-size: .93rem;
}
.aviso.guardado { background: var(--evidencia-fondo); border-color: var(--evidencia); }
.item {
  background: var(--superficie); border: 1px solid var(--borde);
  border-radius: 10px; padding: 1.4rem; margin-bottom: 1.6rem;
  display: flex; flex-direction: column; gap: 1rem;
}
.item-cabecera { display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; }
.numero { font-family: "Source Serif 4", Georgia, serif; font-size: 1.15rem; font-weight: 600; }
.estado { font-size: .78rem; color: var(--tinta-suave); text-transform: uppercase; letter-spacing: .06em; }
.estado[data-listo] { color: var(--tabla); font-weight: 600; }
.marca-tabla {
  margin: 0; padding: .6rem .9rem; font-size: .88rem;
  background: var(--tabla-fondo); border-left: 3px solid var(--tabla); border-radius: 0 6px 6px 0;
}
.fragmento { border-left: 3px solid; padding-left: 1rem; }
.fragmento.evidencia { border-color: var(--evidencia); }
.fragmento.distractor { border-color: var(--distractor); }
.rol {
  font-size: .78rem; text-transform: uppercase; letter-spacing: .07em; font-weight: 600;
  display: flex; gap: .5rem; align-items: center; flex-wrap: wrap; margin-bottom: .35rem;
}
.evidencia .rol { color: var(--evidencia); }
.distractor .rol { color: var(--distractor); }
.dominio, .similitud {
  font-family: "IBM Plex Mono", monospace; font-size: .72rem;
  text-transform: none; letter-spacing: 0; font-weight: 400;
  padding: .1rem .4rem; border-radius: 4px; border: 1px solid currentColor;
}
.procedencia { margin: 0; font-size: .9rem; display: flex; gap: .6rem; flex-wrap: wrap; }
.procedencia span { color: var(--tinta-suave); }
.ubicacion { margin: .1rem 0 .5rem; font-size: .82rem; color: var(--tinta-suave); font-family: "IBM Plex Mono", monospace; }
.texto {
  font-family: "Source Serif 4", Georgia, serif; font-size: 1rem; line-height: 1.65;
  max-height: 11rem; overflow: hidden; position: relative;
  background: var(--evidencia-fondo); padding: .8rem 1rem; border-radius: 6px;
}
.distractor .texto { background: var(--distractor-fondo); }
.texto.abierto { max-height: none; }
.texto:not(.abierto)::after {
  content: ""; position: absolute; inset: auto 0 0 0; height: 3rem;
  background: linear-gradient(transparent, var(--evidencia-fondo));
}
.distractor .texto:not(.abierto)::after { background: linear-gradient(transparent, var(--distractor-fondo)); }
.ver-mas { margin-top: .4rem; background: transparent; border: none; color: var(--tinta-suave); padding: .2rem 0; text-decoration: underline; }
.completar { display: flex; flex-direction: column; gap: .8rem; border-top: 1px solid var(--borde); padding-top: 1rem; }
.completar label { display: flex; flex-direction: column; gap: .3rem; flex: 1 1 10rem; }
.completar label > span { font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; color: var(--tinta-suave); font-weight: 600; }
.fila { display: flex; gap: .8rem; flex-wrap: wrap; }
textarea, input, select {
  font: inherit; font-size: .95rem; color: var(--tinta);
  background: var(--papel); border: 1px solid var(--borde);
  border-radius: 6px; padding: .5rem .6rem; width: 100%; resize: vertical;
}
.identidad { margin: 0; font-size: .75rem; color: var(--tinta-suave); }
.identidad code { font-family: "IBM Plex Mono", monospace; }
.aviso-copia { position: fixed; bottom: 1.5rem; left: 50%; transform: translateX(-50%);
  background: var(--tinta); color: var(--papel); padding: .6rem 1.2rem; border-radius: 6px;
  font-size: .9rem; opacity: 0; pointer-events: none; transition: opacity .25s; }
.aviso-copia.visible { opacity: 1; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
</head>
<body>

<nav class="barra">
  <strong>Planilla del Golden</strong>
  <span class="progreso"><i id="barra-progreso"></i></span>
  <span class="contador" id="contador">0 de __TOTAL__</span>
  <button type="button" id="copiar">Copiar lo escrito</button>
  <button type="button" class="secundario" id="borrar">Borrar todo</button>
</nav>

<main>
<div class="intro">
<h1>Planilla del Golden</h1>
<p class="bajada">El Golden es el instrumento de medición de la tesis: preguntas con la respuesta
correcta ya conocida y verificada. Sin él no se puede saber si B1 recupera mejor que B0, porque no
habría contra qué comparar. Es lo único del experimento que no puede hacer una máquina.</p>

<h2>Qué necesita cada pregunta</h2>
<ol>
<li><strong>Una pregunta realista</strong>, del tipo que haría alguien que trabaja en el sector.</li>
<li><strong>La evidencia</strong>: el fragmento concreto que la responde. No «está en la Ley 24.065»,
sino el artículo exacto.</li>
<li><strong>Los dominios que hacen falta</strong> para responderla: legal, impositivo, contable o financiero.</li>
</ol>

<h2>Por qué las preguntas de colisión son las importantes</h2>
<p>La hipótesis dice que segregar por dominio reduce la contaminación entre dominios. Una pregunta
solo puede confirmarla o refutarla si <strong>hay algo que pueda contaminar</strong>.</p>
<p>Un ítem de colisión tiene esa forma: la respuesta está en el dominio A, y existe otro fragmento del
dominio B que se le parece mucho por vocabulario pero <strong>no sirve para responder</strong>. Si el
sistema monolítico trae el equivocado y el segregado no, eso es exactamente lo que la tesis afirma.</p>
<p>Lo difícil de escribir un ítem de colisión no es la pregunta: es encontrar un distractor plausible.
Eso ya está hecho en esta planilla.</p>

<h2>Cómo trabajar</h2>
<ol>
<li><strong>Leé la evidencia.</strong> Preguntate: qué consulta real se respondería con esto.</li>
<li><strong>Mirá el distractor.</strong> ¿Podría un buscador traerlo por parecido de palabras, aunque
no sirva para responder?
<ul>
<li>Si <strong>sí</strong>, tenés un ítem de colisión. Escribí la pregunta.</li>
<li>Si el distractor <strong>también responde</strong>, no es colisión. Marcalo y seguí de largo.
Vas a descartar varios, es normal.</li>
</ul></li>
<li><strong>Completá los cinco campos.</strong> Dos ya vienen sugeridos.</li>
</ol>
<p>No busques que la pregunta salga perfecta. Salen mejores escribiendo diez que pensando una.</p>

<h2>Un ejemplo, de un ítem que ya escribiste</h2>
<div class="cita">
<strong>pregunta:</strong> ¿Qué sanciones corresponden por violar la ley del sector eléctrico,
cometidas por terceros no concesionarios?<br>
<strong>evidencia:</strong> Ley 24.065, artículo 63<br>
<strong>silos_necesarios:</strong> legal
</div>
<p>Funciona como colisión porque «sanciones» también aparece en materia impositiva —multas fiscales,
intereses resarcitorios— y un buscador sin gobierno puede traer el régimen sancionatorio equivocado.</p>

<h2>Los cinco campos</h2>
<table class="campos">
<tr><th>Pregunta</th><td>La consulta, redactada como la haría una persona real.</td></tr>
<tr><th>Respuesta de referencia</th><td>La respuesta correcta, breve. Una o dos oraciones.</td></tr>
<tr><th>Silos necesarios</th><td>Qué dominios hacen falta para responder. Casi siempre uno. Viene sugerido.</td></tr>
<tr><th>Dominio de la evidencia</th><td>De qué dominio es <em>el fragmento</em>. Suele coincidir con el anterior, pero no siempre.</td></tr>
<tr><th>El distractor sirve</th><td>Si se parece pero no responde, o si también responde.</td></tr>
</table>
<p>Todo lo demás —<code>document_id</code>, <code>artifact_id</code>, <code>sha256</code>,
<code>chunk_uid</code>, <code>emisor_id</code>, el silo persistido y los campos derivados— se completa
solo después, desde el catálogo y la base. Son veinte campos que no hace falta que escribas.</p>

<div class="aviso">
<strong>Un aviso metodológico.</strong> El parecido entre evidencia y distractor lo calculó el
embedding, y es solo una ayuda para buscar. Que un par aparezca acá <strong>no</strong> lo convierte
en colisión: eso lo decidís leyendo. Y el dominio del distractor tiene que salir de tu lectura de su
contenido, nunca del silo automático ni de la salida del router.
</div>

<div class="aviso guardado">
<strong>Lo que escribas se guarda en este navegador</strong> mientras no borres los datos del sitio,
así que podés cerrar y seguir después. Igual, cuando termines una tanda, usá
<strong>Copiar lo escrito</strong> y pegalo en el chat: ahí queda a salvo y se convierte al formato
YAML del protocolo.
</div>
</div>

__TARJETAS__
</main>

<div class="aviso-copia" id="aviso-copia">Copiado</div>

<script>
const IDENTIDAD = [
__IDENTIDAD__
];
const CLAVE = "planilla-golden-v1";

function cargar() {
  try { return JSON.parse(localStorage.getItem(CLAVE) || "{}"); }
  catch (e) { return {}; }
}
function guardar(datos) {
  try { localStorage.setItem(CLAVE, JSON.stringify(datos)); } catch (e) {}
}

const datos = cargar();

function refrescar() {
  let listos = 0;
  document.querySelectorAll(".item").forEach(function (tarjeta) {
    const numero = tarjeta.dataset.item;
    const estado = tarjeta.querySelector("[data-estado]");
    const d = datos[numero] || {};
    if (d.distractor_valido === "no") {
      estado.textContent = "descartado";
      estado.setAttribute("data-listo", "");
      listos++;
    } else if ((d.pregunta || "").trim()) {
      estado.textContent = "escrito";
      estado.setAttribute("data-listo", "");
      listos++;
    } else {
      estado.textContent = "sin empezar";
      estado.removeAttribute("data-listo");
    }
  });
  const total = IDENTIDAD.length;
  document.getElementById("contador").textContent = listos + " de " + total;
  document.getElementById("barra-progreso").style.width = (100 * listos / total) + "%";
}

document.querySelectorAll(".item").forEach(function (tarjeta) {
  const numero = tarjeta.dataset.item;
  tarjeta.querySelectorAll("[data-campo]").forEach(function (campo) {
    const nombre = campo.dataset.campo;
    if (datos[numero] && datos[numero][nombre] !== undefined) {
      campo.value = datos[numero][nombre];
    }
    campo.addEventListener("input", function () {
      datos[numero] = datos[numero] || {};
      datos[numero][nombre] = campo.value;
      guardar(datos);
      refrescar();
    });
  });
  tarjeta.querySelectorAll("[data-vermas]").forEach(function (boton) {
    boton.addEventListener("click", function () {
      const texto = boton.previousElementSibling;
      texto.classList.toggle("abierto");
      boton.textContent = texto.classList.contains("abierto") ? "Ver menos" : "Ver todo";
    });
  });
});

function avisar(mensaje) {
  const aviso = document.getElementById("aviso-copia");
  aviso.textContent = mensaje;
  aviso.classList.add("visible");
  setTimeout(function () { aviso.classList.remove("visible"); }, 1800);
}

document.getElementById("copiar").addEventListener("click", function () {
  const lineas = [];
  IDENTIDAD.forEach(function (ref) {
    const d = datos[ref.numero];
    if (!d) return;
    if (!(d.pregunta || "").trim() && d.distractor_valido !== "no") return;
    lineas.push("- item: " + ref.numero);
    lineas.push('  pregunta: "' + (d.pregunta || "").replace(/"/g, "'") + '"');
    lineas.push('  respuesta_referencia: "' + (d.respuesta_referencia || "").replace(/"/g, "'") + '"');
    lineas.push("  silos_necesarios: [" + (d.silos_necesarios || "") + "]");
    lineas.push("  dominios_evidencia: [" + (d.dominios_evidencia || "") + "]");
    lineas.push("  distractor_valido: " + (d.distractor_valido || ""));
    lineas.push("  chunk_evidencia: " + ref.evidencia);
    lineas.push("  chunk_distractor: " + ref.distractor);
  });
  if (!lineas.length) { avisar("Todavía no hay nada escrito"); return; }
  const texto = lineas.join("\\n");
  navigator.clipboard.writeText(texto).then(
    function () { avisar("Copiado: pegalo en el chat"); },
    function () { window.prompt("Copiá esto:", texto); }
  );
});

document.getElementById("borrar").addEventListener("click", function () {
  if (!window.confirm("Esto borra todo lo escrito en esta planilla. ¿Seguro?")) return;
  Object.keys(datos).forEach(function (k) { delete datos[k]; });
  guardar(datos);
  document.querySelectorAll("[data-campo]").forEach(function (campo) {
    campo.value = campo.defaultValue || "";
  });
  refrescar();
  avisar("Planilla vaciada");
});

refrescar();
</script>
</body>
</html>
"""
