"""Read-only probe: run the evidence contract and verifier over the isolated facts.

It answers three questions that cannot be answered by reading the code:

1. Under an explicit, versioned requirement recipe, how complete is each
   component of a fact, and how many facts are exactly complete? Reported per
   document, because facts from the same document are not independent
   observations.
2. How many facts the extractor reports with high confidence are nonetheless
   incomplete? That gap is the point: confidence and completeness are different
   things, and the number says how far apart they are here.
3. What does the bounded cycle decide, and with which reasons, if no retrieval
   backend is attached?

STRICTLY READ-ONLY. It opens no database connection, calls no model, writes
nothing to `hechos.jsonl` and recomputes no uid. It verifies the fingerprint of
its input before reporting anything: if the input is not the file the numbers
were computed on, the numbers are not these.

WHAT IT DOES NOT MEASURE. Accuracy. A populated field can be wrong, and the
extractor cannot be its own ground truth. Nothing printed here says a value is
correct.

[ES] Sonda de solo lectura: corre el contrato de evidencia y el verificador
sobre los hechos aislados.

Responde tres preguntas que no se pueden responder leyendo el codigo:

1. Bajo una receta de obligatoriedad explicita y versionada, que tan completo
   esta cada componente de un hecho, y cuantos hechos estan exactamente
   completos? Se reporta por documento, porque los hechos del mismo documento no
   son observaciones independientes.
2. Cuantos hechos que el extractor informa con confianza alta estan igualmente
   incompletos? Ese hueco es el punto: confianza y completitud son cosas
   distintas, y el numero dice que tan lejos estan una de otra aca.
3. Que decide el ciclo acotado, y con que motivos, si no se le conecta ningun
   backend de recuperacion?

ESTRICTAMENTE DE SOLO LECTURA. No abre ninguna conexion a la base, no llama a
ningun modelo, no escribe nada en `hechos.jsonl` y no recalcula ningun uid.
Verifica la huella de su insumo antes de reportar nada: si el insumo no es el
archivo sobre el que se calcularon los numeros, los numeros no son estos.

QUE NO MIDE. Exactitud. Un campo poblado puede estar mal, y el extractor no
puede ser su propia verdad de referencia. Nada de lo que se imprime aca dice que
un valor sea correcto.
"""

import argparse
import hashlib
import json
from pathlib import Path

from multirag.evidencia.contrato import Afirmacion, evidencia_de_hecho_tabular
from multirag.evidencia.metricas import I1, observar, resumir
from multirag.evidencia.verificador import (
    COMPONENTES_SEMANTICOS,
    MOTIVOS,
    RECETAS,
    RECETA_REPORTE_V0,
    RECETA_TESIS,
    verificar,
)
from multirag.paths import EXPERIMENTS_DIR


HECHOS_PREDETERMINADOS = EXPERIMENTS_DIR / "prototipo_tablas" / "hechos.jsonl"


def huella(ruta: Path) -> str:
    """SHA-256 of the input. Without it a number cannot be traced to its source.

    [ES] SHA-256 del insumo. Sin ella un numero no se puede rastrear hasta su
    origen.
    """
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return f"sha256:{h.hexdigest()}"


def leer_hechos(ruta: Path):
    """[ES] Lee el jsonl sin modificarlo."""
    with ruta.open("r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                yield json.loads(linea)


def _pct(valor):
    return "  -  " if valor is None else f"{valor * 100:5.1f} %"


def informar(ruta: Path, receta_nombre: str) -> None:
    receta = RECETAS[receta_nombre]
    evidencias = [evidencia_de_hecho_tabular(h) for h in leer_hechos(ruta)]

    # ONE FACT = ONE CLAIM, here and only here. There are no questions yet: the
    # Golden does not exist, so there is nothing that groups several facts into
    # one item. It is a descriptive choice of this probe, and it has a
    # consequence worth stating: no fact can donate a component to another,
    # because composition happens inside a claim. Real claims will group the
    # facts a question needs, and their completeness can only go UP from here.
    #
    # [ES] UN HECHO = UNA AFIRMACION, aca y solo aca. Todavia no hay preguntas:
    # el Golden no existe, asi que no hay nada que agrupe varios hechos en un
    # item. Es una eleccion descriptiva de este sondeo, y tiene una consecuencia
    # que conviene decir: ningun hecho puede donarle un componente a otro, porque
    # la composicion ocurre dentro de una afirmacion. Las afirmaciones reales van
    # a agrupar los hechos que una pregunta necesite, y su completitud solo puede
    # SUBIR respecto de esto.
    afirmaciones = [
        Afirmacion(item_id=f"hecho-{i:05d}", evidencias=(e,))
        for i, e in enumerate(evidencias)
    ]

    print(f"insumo            {ruta}")
    print(f"huella del insumo {huella(ruta)}")
    print(f"hechos            {len(evidencias)}")
    print(f"receta            {receta.nombre}")
    print(f"tipologia         {receta.tipologia_version}")
    print("unidad            un hecho = una afirmacion (eleccion del sondeo:")
    print("                  todavia no hay preguntas que agrupen hechos, asi")
    print("                  que NO hay composicion entre hechos en esta corrida)")
    print("especificacion    NINGUNA: no hay Golden, asi que ninguna afirmacion")
    print("                  declara de que trata. Por eso NINGUNA decision puede")
    print("                  ser `responder`: es una propiedad del sondeo, no del")
    print("                  brazo. Lo que si mide esta corrida es completitud.")
    print()

    observaciones = observar(afirmaciones, I1, receta=receta)
    resumen = resumir(observaciones, receta=receta)

    print("SALVEDADES (van adelante, no al final)")
    for aviso in resumen.advertencias():
        print(f"  - {aviso}")
    print()

    print("DISTRIBUCION POR TIPO DE HECHO")
    for tipo, n in sorted(resumen.distribucion_por_tipo.items(), key=lambda kv: -kv[1]):
        print(f"  {tipo:22} {n:6}  {n / resumen.n_items * 100:5.1f} %")
    print()

    print("SOPORTE (distinto de completitud y de localizabilidad)")
    for soporte, n in sorted(resumen.distribucion_por_soporte.items(), key=lambda kv: -kv[1]):
        print(f"  {soporte:22} {n:6}  {n / resumen.n_items * 100:5.1f} %")
    print()

    print("COMPLETITUD POR COMPONENTE (sobre los hechos que lo exigen)")
    for componente in COMPONENTES_SEMANTICOS:
        print(f"  {componente:12} {_pct(resumen.integridad_por_componente.get(componente))}")
    print()

    print("INTEGRIDAD EXACTA")
    glob = resumen.global_agrupado_no_inferencial
    print(f"  agrupado (NO inferencial)   {_pct(glob['integridad_exacta'])}")
    print(f"  mediana entre documentos    {_pct(resumen.mediana_entre_documentos['integridad_exacta'])}")
    rango = resumen.rango_entre_documentos["integridad_exacta"]
    if rango:
        print(f"  rango entre documentos      {_pct(rango[0])} .. {_pct(rango[1])}")
    print(f"  presencia de evidencia      {_pct(glob['presencia_evidencia'])}")
    print(f"  tupla (entidad, periodo, unidad, moneda, valor), solo monetarios"
          f"  {_pct(resumen.integridad_exacta_del_hecho)}")
    print()

    print(f"POR DOCUMENTO (unidad de analisis; n={resumen.n_documentos})")
    print(
        f"  {'document_id':14} {'items':>7} {'exacta':>8} {'presencia':>10} "
        f"{'abstuvo':>9} {'indet.':>8}"
    )
    for d in sorted(resumen.por_documento, key=lambda x: -x.n):
        print(
            f"  {str(d.document_id):14} {d.n:7} {_pct(d.integridad_exacta):>8} "
            f"{_pct(d.presencia_evidencia):>10} {d.abstenciones:9} {d.indeterminados:8}"
        )
    print()

    print("CONFIANZA DECLARADA CONTRA INTEGRIDAD")
    print("  La confianza se copia del extractor y NO se recalcula. Bajarla para")
    print("  que los numeros cierren ocultaria el hallazgo en lugar de reportarlo.")
    cruce = {}
    for evidencia in evidencias:
        v = verificar(evidencia, receta)
        clave = (v.confianza_declarada, v.integridad_exacta)
        cruce[clave] = cruce.get(clave, 0) + 1
    for (confianza, exacta), n in sorted(cruce.items(), key=lambda kv: str(kv[0])):
        marca = "" if exacta else "   <- incompleto"
        print(f"  confianza={str(confianza):6} integridad_exacta={str(exacta):5} {n:6}{marca}")
    print(
        f"  casos de confianza alta con integridad incompleta: "
        f"{resumen.confianza_alta_con_integridad_incompleta}"
    )
    print()

    print("MOTIVOS DE INSUFICIENCIA (un hecho puede acumular varios)")
    conteo = {m: 0 for m in MOTIVOS}
    for o in observaciones:
        for m in o.motivos:
            conteo[m] = conteo.get(m, 0) + 1
    for motivo, n in sorted(conteo.items(), key=lambda kv: -kv[1]):
        if n:
            print(f"  {motivo:28} {n:6}  {n / resumen.n_items * 100:5.1f} %")
    print()

    print("CONDUCTA DEL CICLO SIN BACKEND DE RECUPERACION")
    print("  Conducta, no calidad: dice lo que hizo el brazo, nunca si acerto.")
    print("  Sin adaptador no hay reintento: esto es el comportamiento de I1,")
    print("  no una falla. I2 exige conectar un adaptador real.")
    print(f"  responder      {_pct(glob['tasa_de_respuesta'])}")
    print(f"  abstener       {_pct(glob['tasa_de_abstencion'])}")
    print(f"  indeterminado  {_pct(glob['tasa_de_indeterminado'])}")
    print(f"  reintentos     {glob['reintentos_usados']}")
    print()
    print("  Precision de abstencion, tasa de abstencion correcta, falso veto y")
    print("  cobertura NO se calculan: exigen referencia humana y no hay Golden.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--hechos",
        type=Path,
        default=HECHOS_PREDETERMINADOS,
        help="jsonl de hechos del extractor table-aware (solo se lee)",
    )
    parser.add_argument(
        "--receta",
        choices=sorted(RECETAS),
        default=RECETA_TESIS.nombre,
        help=(
            f"{RECETA_TESIS.nombre} exige entidad (PRIORIDADES 7.1); "
            f"{RECETA_REPORTE_V0.nombre} no la exige (reports/completitud_hechos.md)"
        ),
    )
    args = parser.parse_args()

    if not args.hechos.exists():
        raise SystemExit(f"no existe el insumo: {args.hechos}")

    informar(args.hechos, args.receta)


if __name__ == "__main__":
    main()
