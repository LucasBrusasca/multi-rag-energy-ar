"""Calibrate the final `k` of retrieval against the development questions.

`RETRIEVAL_TOP_K = 3` is declared provisional in `config.py` and was never
calibrated. Choosing it by eye is exactly what the protocol forbids, and
choosing it after seeing the confirmatory test would be worse.

The calibration reads two curves at once over the SAME questions:

- **recall of the evidence**: does the reference fragment appear among the k
  delivered? It grows with k and flattens out. That elbow is where more context
  stops buying anything.
- **contamination**: the more fragments are brought, the higher the chance of
  including material from the wrong regime. It also grows with k.

The good `k` is where recall has already flattened and contamination has not yet
taken off. It is a trade-off, so the criterion must be declared BEFORE looking
at the numbers, and the value frozen before opening the test.

Three rules that cannot be skipped, and the code enforces the first two:

1. It is calibrated ONLY with development questions. `etapa` must be
   `desarrollo`; a confirmatory item makes it fail.
2. It is IDENTICAL across arms. If one arm received a larger k it would win by
   budget and not by architecture.
3. It is frozen before opening the test, like the classifier recipe.

⚠️ `k` is not only a count of fragments, it is a CONTEXT BUDGET. A dense
accounting chunk can be three times the size of a legal one, so `k = 3` does not
mean the same thing in every arm. The delivered characters are reported
alongside, because that is the quantity the protocol demands be comparable.

⚠️ The contamination measured here is a PROXY: a fragment whose retrieval
domains do not intersect the domains the question needs. The normative
definition is human (`PROTOCOLO_EXPERIMENTAL.md` §3, `regimen_chunk`). It serves
to choose a hyperparameter on development; it does not replace human scoring.

[ES] Calibra el `k` final de la recuperación contra las preguntas de desarrollo.

`RETRIEVAL_TOP_K = 3` está declarado como provisorio en `config.py` y nunca se
calibró. Elegirlo a ojo es exactamente lo que el protocolo prohíbe, y elegirlo
después de ver el test confirmatorio sería peor.

La calibración lee dos curvas a la vez sobre las MISMAS preguntas:

- **recall de la evidencia**: ¿aparece el fragmento de referencia entre los k
  entregados? Sube con k y se aplana. Ese codo es donde más contexto deja de
  comprar algo.
- **contaminación**: cuantos más fragmentos se traen, más chance de incluir
  material del régimen equivocado. También sube con k.

El `k` bueno es donde el recall ya se aplanó y la contaminación todavía no se
disparó. Es un compromiso, así que el criterio debe declararse ANTES de mirar
los números, y el valor congelarse antes de abrir el test.

Tres reglas que no se pueden saltear, y el código hace cumplir las dos primeras:

1. Se calibra SOLO con preguntas de desarrollo. `etapa` tiene que ser
   `desarrollo`; un ítem confirmatorio la hace fallar.
2. Es IDÉNTICO entre brazos. Si un brazo recibiera un k mayor ganaría por
   presupuesto y no por arquitectura.
3. Se congela antes de abrir el test, igual que la receta del clasificador.

⚠️ `k` no es solo una cantidad de fragmentos, es un PRESUPUESTO DE CONTEXTO. Un
chunk contable denso puede ocupar el triple que uno legal, así que `k = 3` no
significa lo mismo en cada brazo. Se reportan al lado los caracteres entregados,
porque esa es la magnitud que el protocolo exige comparable.

⚠️ La contaminación que se mide acá es un PROXY: un fragmento cuyos dominios de
recuperación no intersectan los dominios que la pregunta necesita. La definición
normativa es humana (`PROTOCOLO_EXPERIMENTAL.md` §3, `regimen_chunk`). Sirve
para elegir un hiperparámetro sobre desarrollo; no reemplaza la puntuación
humana.
"""

VALORES_K_PREDETERMINADOS = (1, 3, 5, 10)


class ErrorDeCalibracion(ValueError):
    """The calibration cannot be run as requested.

    [ES] La calibración no se puede correr como se pidió.
    """


def validar_items(items) -> list[dict]:
    """Check that every item is usable and belongs to development.

    [ES] Verifica que cada ítem sea utilizable y sea de desarrollo.
    """
    items = list(items or [])

    if not items:
        raise ErrorDeCalibracion(
            "No hay ítems para calibrar. La calibración necesita preguntas de "
            "desarrollo con evidencia marcada: sin ellas no hay recall que "
            "medir."
        )

    for numero, item in enumerate(items, start=1):
        etapa = item.get("split") or item.get("etapa")

        if etapa is not None and etapa not in ("desarrollo", "dev", "pilot", "piloto"):
            raise ErrorDeCalibracion(
                f"El ítem {item.get('id', numero)!r} declara etapa {etapa!r}. "
                "El `k` se calibra SOLO con desarrollo: usar el test "
                "confirmatorio para elegir un hiperparámetro lo invalida."
            )

        if not item.get("pregunta"):
            raise ErrorDeCalibracion(
                f"El ítem {item.get('id', numero)!r} no tiene pregunta."
            )

        if not _uids_de_evidencia(item):
            raise ErrorDeCalibracion(
                f"El ítem {item.get('id', numero)!r} no tiene evidencia con "
                "chunk_uid. Sin evidencia marcada no se puede medir si fue "
                "recuperada."
            )

    return items


def _uids_de_evidencia(item: dict) -> set:
    """The chunk_uid values of the item's reference evidence.

    [ES] Los chunk_uid de la evidencia de referencia del ítem.
    """
    uids = set()

    for evidencia in item.get("evidencia") or []:
        uid = (
            evidencia.get("chunk_uid_snapshot")
            or evidencia.get("chunk_uid")
        )

        if uid:
            uids.add(uid)

    return uids


def _dominios_necesarios(item: dict) -> set:
    """The domains the question needs, from the human reference.

    [ES] Los dominios que la pregunta necesita, según la referencia humana.
    """
    return {
        str(silo).strip()
        for silo in (item.get("silos_necesarios") or [])
        if str(silo).strip()
    }


def _dominios_del_resultado(registro: dict) -> set:
    """The domains a delivered fragment was retrieved through.

    Falls back to the inherited physical silo when the retrieval did not record
    domains, which is the A0 case.

    [ES] Los dominios por los que un fragmento entregado fue recuperado.

    Cae al silo físico heredado cuando la recuperación no registró dominios,
    que es el caso A0.
    """
    dominios = {
        str(dominio).strip()
        for dominio in (registro.get("dominios_recuperacion") or [])
        if str(dominio).strip()
    }

    if dominios:
        return dominios

    silo = registro.get("silo")

    return {str(silo).strip()} if silo else set()


def medir_item(item: dict, resultados, k: int) -> dict:
    """Measure one question at one value of k.

    [ES] Mide una pregunta con un valor de k.
    """
    entregados = list(resultados)[:k]
    esperados = _uids_de_evidencia(item)
    necesarios = _dominios_necesarios(item)

    recuperados = {
        registro.get("chunk_uid")
        for registro in entregados
        if registro.get("chunk_uid")
    }

    encontrados = esperados & recuperados

    contaminados = 0

    if necesarios:
        for registro in entregados:
            dominios = _dominios_del_resultado(registro)

            if dominios and not (dominios & necesarios):
                contaminados += 1

    caracteres = sum(
        len(str(registro.get("contenido") or ""))
        for registro in entregados
    )

    return {
        # The item counts as a hit when AT LEAST ONE reference fragment was
        # delivered: that is what lets the generator answer.
        # [ES] El ítem cuenta como acierto cuando se entregó AL MENOS UN
        # fragmento de referencia: eso es lo que permite responder.
        "acierto": bool(encontrados),
        "evidencia_esperada": len(esperados),
        "evidencia_recuperada": len(encontrados),
        "entregados": len(entregados),
        "contaminados": contaminados,
        # Declared apart from contamination: an item without
        # `silos_necesarios` cannot be scored, and averaging it in as zero
        # would understate contamination.
        # [ES] Se declara aparte de la contaminación: un ítem sin
        # `silos_necesarios` no se puede puntuar, y promediarlo como cero
        # subestimaría la contaminación.
        "puntuable_contaminacion": bool(necesarios),
        "caracteres": caracteres,
    }


def calibrar(
    items,
    buscar_fn,
    valores_k=VALORES_K_PREDETERMINADOS,
    **opciones_busqueda,
) -> list[dict]:
    """Run the whole grid and return one row per value of k.

    Retrieval is requested ONCE per question, with the largest k, and each
    value is measured over a prefix of that same list. Beyond saving calls, it
    guarantees that the curves come from the same ranking and that a difference
    between two k values is not an artifact of two separate runs.

    [ES] Corre la grilla completa y devuelve una fila por valor de k.

    La recuperación se pide UNA vez por pregunta, con el k más grande, y cada
    valor se mide sobre un prefijo de esa misma lista. Además de ahorrar
    llamadas, garantiza que las curvas salgan del mismo ranking y que una
    diferencia entre dos k no sea un artefacto de dos corridas distintas.
    """
    items = validar_items(items)

    valores = sorted({int(k) for k in valores_k})

    if not valores or valores[0] < 1:
        raise ErrorDeCalibracion(
            f"Los valores de k deben ser enteros mayores que cero; se "
            f"recibió {valores_k!r}."
        )

    k_maximo = valores[-1]

    recuperado_por_item = {}

    for item in items:
        recuperado_por_item[id(item)] = list(
            buscar_fn(
                item["pregunta"],
                k=k_maximo,
                **opciones_busqueda,
            )
        )

    informe = []

    for k in valores:
        mediciones = [
            medir_item(item, recuperado_por_item[id(item)], k)
            for item in items
        ]

        puntuables = [m for m in mediciones if m["puntuable_contaminacion"]]

        entregados = sum(m["entregados"] for m in puntuables)
        contaminados = sum(m["contaminados"] for m in puntuables)

        esperada = sum(m["evidencia_esperada"] for m in mediciones)
        recuperada = sum(m["evidencia_recuperada"] for m in mediciones)

        informe.append(
            {
                "k": k,
                "items": len(mediciones),
                # Fraction of questions with at least one reference fragment.
                # [ES] Proporción de preguntas con al menos un fragmento de
                # referencia.
                "recall_item": (
                    sum(m["acierto"] for m in mediciones) / len(mediciones)
                ),
                # Fraction of reference fragments delivered. Stricter than the
                # previous one when a question has several.
                # [ES] Proporción de fragmentos de referencia entregados. Más
                # exigente que el anterior cuando una pregunta tiene varios.
                "recall_evidencia": (
                    recuperada / esperada if esperada else 0.0
                ),
                "contaminacion": (
                    contaminados / entregados if entregados else 0.0
                ),
                "items_puntuables": len(puntuables),
                "caracteres_promedio": (
                    sum(m["caracteres"] for m in mediciones) / len(mediciones)
                ),
            }
        )

    return informe


def formatear(informe) -> str:
    """Render the report as a readable table.

    [ES] Presenta el informe como una tabla legible.
    """
    lineas = [
        f"{'k':>4} {'recall ítem':>12} {'recall evid.':>13} "
        f"{'contaminación':>14} {'caracteres':>11}",
    ]

    for fila in informe:
        lineas.append(
            f"{fila['k']:>4} "
            f"{fila['recall_item']:>11.0%} "
            f"{fila['recall_evidencia']:>12.0%} "
            f"{fila['contaminacion']:>13.0%} "
            f"{fila['caracteres_promedio']:>11,.0f}"
        )

    if informe and informe[0]["items_puntuables"] < informe[0]["items"]:
        lineas.append("")
        lineas.append(
            f"⚠️ {informe[0]['items'] - informe[0]['items_puntuables']} "
            f"de {informe[0]['items']} ítems no declaran silos_necesarios y "
            "quedan fuera de la contaminación."
        )

    lineas.append("")
    lineas.append(
        "El k bueno es donde el recall ya se aplanó y la contaminación "
        "todavía no se disparó."
    )
    lineas.append(
        "Declarar el criterio ANTES de mirar, y congelar el valor antes de "
        "abrir el test."
    )

    return "\n".join(lineas)
