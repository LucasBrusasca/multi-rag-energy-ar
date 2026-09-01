"""Freeze the classifier recipe and detect any later change to it.

The recipe is everything that determines what the classifier answers: the
prompt template, the silo descriptions embedded in it, the model and the
temperature. Its fingerprint is written once, BEFORE observing the results of
the run it governs, and verified from then on.

Why it matters: the prompt contains rules written after an exploratory finding
of Aug 2026 (the confusion between accounting statements and financial
instruments). Using an exploratory finding to design is legitimate; retouching
the prompt after seeing each measurement is not, and from the outside the two
are indistinguishable unless the recipe was frozen with a date. The frozen
fingerprint is what makes them distinguishable.

Freezing does not forbid changing the recipe. It forbids changing it SILENTLY:
a change makes the verification fail, and then a new version must be declared
with its reason.

[ES] Congela la receta del clasificador y detecta cualquier cambio posterior.

La receta es todo lo que determina qué responde el clasificador: la plantilla
del prompt, las descripciones de silo incrustadas en ella, el modelo y la
temperatura. Su huella se escribe una vez, ANTES de observar los resultados de
la corrida que gobierna, y desde entonces se verifica.

Por qué importa: el prompt contiene reglas escritas después de un hallazgo
exploratorio de agosto de 2026 (la confusión entre estados contables e
instrumentos financieros). Usar un hallazgo exploratorio para diseñar es
legítimo; retocar el prompt después de ver cada medición no lo es, y desde
afuera ambas cosas son indistinguibles salvo que la receta se haya congelado
con fecha. La huella congelada es lo que las vuelve distinguibles.

Congelar no prohíbe cambiar la receta. Prohíbe cambiarla EN SILENCIO: un cambio
hace fallar la verificación, y entonces hay que declarar una versión nueva con
su motivo.
"""

import argparse
import hashlib
import json
from pathlib import Path

from multirag.config import LLM_MODELS, SILOS
from multirag.paths import DATA_DIR
from multirag.research.clasificador_llm import _construir_prompt


RUTA_RECETA = DATA_DIR / "receta_clasificador_congelada.json"


# Temperature used by multirag.generation.llm.llamar_llm. It is part of the
# recipe: the same prompt at another temperature is another classifier.
# [ES] Temperatura que usa multirag.generation.llm.llamar_llm. Es parte de la
# receta: el mismo prompt a otra temperatura es otro clasificador.
TEMPERATURA = 0

ROL = "router"


# Placeholders so the fingerprint covers the TEMPLATE and not the content of
# any particular chunk.
# [ES] Marcadores para que la huella cubra la PLANTILLA y no el contenido de
# ningún chunk en particular.
TEXTO_TESTIGO = "<<FRAGMENTO>>"
TITULO_TESTIGO = "<<TITULO>>"
RUTA_TESTIGO = ["<<SECCION>>"]


class RecetaAlterada(RuntimeError):
    """The recipe changed after being frozen.

    [ES] La receta cambió después de haber sido congelada.
    """


def plantilla() -> str:
    """The exact prompt template, with the silo descriptions inside it.

    [ES] La plantilla exacta del prompt, con las descripciones de silo dentro.
    """
    return _construir_prompt(
        TEXTO_TESTIGO,
        titulo=TITULO_TESTIGO,
        hierarchy=list(RUTA_TESTIGO),
    )


def receta() -> dict:
    """Everything that determines the classifier's answer.

    [ES] Todo lo que determina la respuesta del clasificador.
    """
    return {
        "rol": ROL,
        "modelo": LLM_MODELS[ROL],
        "temperatura": TEMPERATURA,
        "silos": dict(sorted(SILOS.items())),
        "plantilla_prompt": plantilla(),
    }


def huella(datos: dict | None = None) -> str:
    """SHA-256 of the recipe, serialised deterministically.

    [ES] SHA-256 de la receta, serializada de forma determinista.
    """
    contenido = json.dumps(
        datos if datos is not None else receta(),
        ensure_ascii=False,
        sort_keys=True,
    )

    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()


def congelar(
    ruta: Path = RUTA_RECETA,
    *,
    version: str,
    fecha: str,
    motivo: str = "",
) -> dict:
    """Write the frozen recipe. Refuses to overwrite an existing one.

    The date is received, never taken from the clock: a manifest must be able
    to be regenerated identically.

    [ES] Escribe la receta congelada. Se niega a pisar una existente.

    La fecha se recibe, nunca se toma del reloj: un manifiesto tiene que poder
    regenerarse idéntico.
    """
    ruta = Path(ruta)

    if ruta.exists():
        raise RecetaAlterada(
            f"Ya existe una receta congelada en {ruta}. Congelar de nuevo "
            "borraría la evidencia de qué gobernaba la corrida anterior. "
            "Para declarar una versión nueva, renombrá la anterior a mano y "
            "dejá escrito el motivo del cambio."
        )

    datos = receta()

    manifiesto = {
        "version": version,
        "fecha_congelamiento": fecha,
        "motivo": motivo,
        "huella_sha256": huella(datos),
        "receta": datos,
    }

    ruta.parent.mkdir(parents=True, exist_ok=True)

    temporal = ruta.with_name(f".{ruta.name}.tmp")
    temporal.write_text(
        json.dumps(manifiesto, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    temporal.replace(ruta)

    return manifiesto


def verificar(ruta: Path = RUTA_RECETA) -> dict:
    """Check that the current recipe still matches the frozen one.

    Raises with a readable diff when it does not: what changed matters more
    than the fact that something did.

    [ES] Verifica que la receta actual siga coincidiendo con la congelada.

    Falla con una diferencia legible cuando no: qué cambió importa más que el
    hecho de que algo cambió.
    """
    ruta = Path(ruta)

    if not ruta.is_file():
        raise RecetaAlterada(
            f"No hay receta congelada en {ruta}. Congelala ANTES de observar "
            "los resultados que va a gobernar; congelarla después no protege "
            "de nada."
        )

    manifiesto = json.loads(ruta.read_text(encoding="utf-8"))
    actual = receta()
    huella_actual = huella(actual)

    if huella_actual == manifiesto["huella_sha256"]:
        return manifiesto

    diferencias = []

    congelada = manifiesto["receta"]

    for clave in ("modelo", "temperatura", "rol"):
        if congelada.get(clave) != actual.get(clave):
            diferencias.append(
                f"{clave}: congelado={congelada.get(clave)!r} "
                f"actual={actual.get(clave)!r}"
            )

    silos_congelados = congelada.get("silos", {})

    for silo in sorted(set(silos_congelados) | set(actual["silos"])):
        if silos_congelados.get(silo) != actual["silos"].get(silo):
            diferencias.append(
                f"descripción del silo {silo!r} cambió"
            )

    if congelada.get("plantilla_prompt") != actual["plantilla_prompt"]:
        diferencias.append("la plantilla del prompt cambió")

    raise RecetaAlterada(
        "La receta del clasificador cambió después de congelarse "
        f"(versión {manifiesto.get('version')}, "
        f"{manifiesto.get('fecha_congelamiento')}).\n"
        + "\n".join(f"  - {d}" for d in diferencias)
        + "\n\nSi el cambio es deliberado, declaralo como versión nueva y "
        "dejá escrito el motivo. Si no lo es, revertilo: la corrida "
        "clasificada con la receta anterior ya no describe a este código."
    )


def construir_parser() -> argparse.ArgumentParser:
    """Build the command-line interface.

    [ES] Construye la interfaz de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Congela o verifica la receta del clasificador (prompt, "
            "descripciones de silo, modelo y temperatura)."
        )
    )
    parser.add_argument(
        "--congelar",
        action="store_true",
        help="Escribe la receta congelada. No pisa una existente.",
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Nombre de la versión, por ejemplo 'receta-llm-v1'.",
    )
    parser.add_argument(
        "--fecha",
        default=None,
        help="Fecha del congelamiento, en formato AAAA-MM-DD.",
    )
    parser.add_argument(
        "--motivo",
        default="",
        help="Por qué se congela ahora.",
    )
    return parser


def main() -> None:
    """Freeze or verify from the command line.

    [ES] Congela o verifica desde la línea de comandos.
    """
    argumentos = construir_parser().parse_args()

    if argumentos.congelar:
        if not argumentos.version or not argumentos.fecha:
            raise SystemExit(
                "Para congelar hace falta --version y --fecha explícitas."
            )

        manifiesto = congelar(
            version=argumentos.version,
            fecha=argumentos.fecha,
            motivo=argumentos.motivo,
        )

        print(f"Receta congelada: {RUTA_RECETA}")
        print(f"  versión : {manifiesto['version']}")
        print(f"  fecha   : {manifiesto['fecha_congelamiento']}")
        print(f"  modelo  : {manifiesto['receta']['modelo']}")
        print(f"  huella  : {manifiesto['huella_sha256']}")
        print(
            "\nDesde ahora, cualquier cambio del prompt, de las descripciones "
            "de silo, del modelo o de la temperatura hace fallar la "
            "verificación."
        )
        return

    manifiesto = verificar()

    print("La receta coincide con la congelada.")
    print(f"  versión : {manifiesto['version']}")
    print(f"  fecha   : {manifiesto['fecha_congelamiento']}")
    print(f"  huella  : {manifiesto['huella_sha256']}")


if __name__ == "__main__":
    main()
