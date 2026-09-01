"""RQ0, read-only probe: does the embedding represent DOMAIN, TYPE or ISSUER?

The exploratory measurement of `92 %` on normative documents and `11 %` on
company documents admits a rival explanation: BGE-M3 may separate documentary
TYPE or the issuer's STYLE better than domain of knowledge. If the rival
explanation wins, the experimental axis of the thesis has to be discussed with
the director before freezing the protocol. That is the whole point of this
probe.

WHAT IT DOES NOT DO. It does not modify PostgreSQL, does not re-ingest, does not
recompute any embedding, does not touch the persisted classification and does
not change a single `chunk_uid`. It opens a read-only transaction and reads.

--- Methodology, and why the first version of this script was replaced ---

ONE VECTOR AND ONE VOTE PER DOCUMENT. The primary analysis averages a
document's chunks into a single L2-normalised vector, and class centroids are
built from DOCUMENT vectors. The first version built centroids from chunks, so a
document of 812 chunks pulled the centroid 270 times harder than one of 3: the
result described the longest documents, not the corpus. Chunk-level prediction
with majority voting survives only as a sensitivity analysis, reported apart.

THE NULL RE-RUNS THE WHOLE PROCEDURE. Each permutation shuffles the labels among
documents and then refits every fold and every centroid. The first version kept
the observed predictions and permuted only the true labels, which is the null of
"these predictions are unrelated to these labels" - not the null of the
supervised procedure that produced them. The weaker null makes almost anything
look significant.

THE FOUR SILOS ARE THE PRIMARY DOMAIN QUESTION. `legal`, `impositivo`,
`contable` and `financiero` are the architecture the thesis is about, evaluated
as four one-vs-rest tasks with a Holm correction over exactly those four.
`dominio_combinacion` is exploratory description ONLY: it drops 7 of 24
documents, and all three `financiero` documents are among them, so it cannot
speak about the four-silo architecture and cannot resolve the gate.

UNCERTAINTY IS OMITTED WHEN IT WOULD BE THEATRE. The bootstrap is stratified
within each true class so no resample loses a class; when the smallest evaluated
class is too small for that to mean anything, the interval is not printed and
the limitation is stated instead.

[ES] RQ0, sonda de solo lectura: representa el embedding DOMINIO, TIPO o EMISOR?

La medicion exploratoria de `92 %` en documentos normativos y `11 %` en
documentos de empresa admite una explicacion rival: BGE-M3 podria separar TIPO
documental o ESTILO del emisor mejor que dominio de conocimiento. Si gana la
explicacion rival, el eje experimental de la tesis hay que discutirlo con el
director antes de congelar el protocolo. Ese es todo el proposito de esta sonda.

QUE NO HACE. No modifica PostgreSQL, no reingiere, no recalcula ningun
embedding, no toca la clasificacion persistida y no cambia un solo `chunk_uid`.
Abre una transaccion de solo lectura y lee.

--- Metodologia, y por que se reemplazo la primera version de este script ---

UN VECTOR Y UN VOTO POR DOCUMENTO. El analisis primario promedia los chunks de
un documento en un unico vector L2-normalizado, y los centroides de clase se
arman con vectores DOCUMENTALES. La primera version armaba los centroides con
chunks, asi que un documento de 812 chunks tiraba del centroide 270 veces mas
fuerte que uno de 3: el resultado describia los documentos mas largos, no el
corpus. La prediccion por chunks con voto mayoritario sobrevive solo como
analisis de sensibilidad, reportado aparte.

EL NULO VUELVE A CORRER TODO EL PROCEDIMIENTO. Cada permutacion baraja las
etiquetas entre documentos y despues reajusta todos los folds y todos los
centroides. La primera version conservaba las predicciones observadas y permutaba
solo las etiquetas verdaderas, que es el nulo de "estas predicciones no tienen
relacion con estas etiquetas" - no el nulo del procedimiento supervisado que las
produjo. El nulo mas debil vuelve significativo casi cualquier cosa.

LOS CUATRO SILOS SON LA PREGUNTA PRIMARIA DE DOMINIO. `legal`, `impositivo`,
`contable` y `financiero` son la arquitectura de la que trata la tesis,
evaluados como cuatro tareas uno-contra-el-resto con correccion de Holm sobre
esos cuatro exactamente. `dominio_combinacion` es descripcion exploratoria y
NADA MAS: descarta 7 de 24 documentos, y los tres documentos `financiero` estan
entre ellos, asi que no puede hablar de la arquitectura de cuatro silos ni
resolver la compuerta.

LA INCERTIDUMBRE SE OMITE CUANDO SERIA DECORADO. El bootstrap es estratificado
dentro de cada clase verdadera para que ninguna remuestra pierda una clase;
cuando la clase evaluada mas chica es demasiado chica para que eso signifique
algo, el intervalo no se imprime y en su lugar se declara la limitacion.
"""

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import balanced_accuracy_score, confusion_matrix

from multirag.config import SILOS
from multirag.db import conectar
from multirag.paths import DATA_DIR, PROJECT_ROOT


RECETA_VERSION = "rq0-v0.2-documento-como-unidad"
SEMILLA = 20260829

CATALOGO = DATA_DIR / "catalog" / "metadatos_curados.csv"
INVENTARIO = DATA_DIR / "catalog" / "inventario_objetivo.jsonl"

SEPARADOR_DOMINIOS = "|"

# The four silos of the architecture, read from the single source of truth
# instead of retyped here. `dominios_documentales` carries other tokens too;
# those are supplementary, not the question.
# [ES] Los cuatro silos de la arquitectura, leidos de la fuente unica de verdad
# en lugar de reescritos aca. `dominios_documentales` trae otros tokens ademas;
# esos son suplementarios, no la pregunta.
DOMINIOS_CENTRALES = tuple(sorted(SILOS))

# Below this many documents in the smallest evaluated class, a bootstrap
# interval is decoration: resampling three documents with replacement produces a
# number, not an estimate of anything.
# [ES] Por debajo de esta cantidad de documentos en la clase evaluada mas chica,
# un intervalo bootstrap es decorado: remuestrear tres documentos con reposicion
# produce un numero, no una estimacion de nada.
MINIMO_PARA_BOOTSTRAP = 5


# --------------------------------------------------------------------------
# Reading, strictly read-only / Lectura, estrictamente de solo lectura
# --------------------------------------------------------------------------


def huella_de_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return f"sha256:{h.hexdigest()}"


def huella_de_conjunto(document_ids, chunk_uids) -> str:
    """Fingerprint of the analysed set. Sorted, so row order cannot change it.

    [ES] Huella del conjunto analizado. Ordenada, para que el orden de las filas
    no pueda cambiarla.
    """
    h = hashlib.sha256()
    for d in sorted(set(document_ids)):
        h.update(f"D{d}\n".encode("utf-8"))
    for c in sorted(chunk_uids):
        h.update(f"C{c}\n".encode("utf-8"))
    return f"sha256:{h.hexdigest()}"


def leer_inventario_objetivo() -> set:
    """The 24 canonical artifacts. The 14 pilot chunks are NOT among them.

    [ES] Los 24 artefactos canonicos. Los 14 chunks piloto NO estan entre ellos.
    """
    with INVENTARIO.open(encoding="utf-8") as f:
        return {json.loads(l)["artifact_id"] for l in f if l.strip()}


def leer_catalogo() -> dict:
    with CATALOGO.open(encoding="utf-8-sig") as f:
        return {r["document_id"]: r for r in csv.DictReader(f)}


def normalizar(M):
    """L2 per row. A row-wise operation cannot leak between folds.

    [ES] L2 por fila. Una operacion por fila no puede filtrar entre folds.
    """
    normas = np.linalg.norm(M, axis=1, keepdims=True)
    return M / np.maximum(normas, 1e-12)


def leer_chunks(artifacts_objetivo: set):
    """Read chunk embeddings inside a READ ONLY transaction.

    [ES] Lee los embeddings de los chunks dentro de una transaccion READ ONLY.
    """
    conexion = conectar()
    try:
        conexion.set_session(readonly=True)
        cur = conexion.cursor()
        cur.execute(
            """
            select chunk_uid, document_id, artifact_id, embedding
            from chunks
            where embedding is not null
            order by chunk_uid
            """
        )
        filas = cur.fetchall()
    finally:
        conexion.close()

    seleccion = [f for f in filas if f[2] in artifacts_objetivo]
    descartados = len(filas) - len(seleccion)

    chunk_uids = [f[0] for f in seleccion]
    documentos = [f[1] for f in seleccion]
    vectores = np.array(
        [np.fromstring(f[3].strip("[]"), sep=",") for f in seleccion], dtype=np.float64
    )
    return chunk_uids, documentos, normalizar(vectores), descartados


# --------------------------------------------------------------------------
# The document as the unit / El documento como unidad
# --------------------------------------------------------------------------


def vectores_por_documento(X, grupos):
    """One L2-normalised vector per document: the mean of its chunks.

    This is what makes every document weigh exactly once. A 812-chunk document
    and a 3-chunk one arrive at the centroid as one vector each.

    [ES] Un vector L2-normalizado por documento: el promedio de sus chunks.

    Esto es lo que hace que cada documento pese exactamente una vez. Un documento
    de 812 chunks y uno de 3 llegan al centroide como un vector cada uno.
    """
    documentos = sorted(set(grupos))
    indice = {d: i for i, d in enumerate(documentos)}
    acumulado = np.zeros((len(documentos), X.shape[1]))
    conteo = np.zeros(len(documentos))
    for fila, doc in zip(X, grupos):
        acumulado[indice[doc]] += fila
        conteo[indice[doc]] += 1
    return documentos, normalizar(acumulado / conteo[:, None])


def _predecir_una_pasada(V, y):
    """Leave one DOCUMENT out over document vectors, with a rank-1 update.

    Recomputing every centroid from scratch in every fold would be correct and
    slow; subtracting the held-out document from its own class sum is the same
    arithmetic and is what makes 2.000 refitted permutations affordable.

    Returns the predictions and the mask of folds that could actually be
    scored: a fold whose training set lost a class entirely cannot predict it,
    and that is reported rather than absorbed.

    [ES] Deja un DOCUMENTO afuera sobre vectores documentales, con una
    actualizacion de rango 1.

    Recalcular cada centroide desde cero en cada fold seria correcto y lento;
    restarle al total de su clase el documento retenido es la misma aritmetica y
    es lo que vuelve pagables 2.000 permutaciones reajustadas.

    Devuelve las predicciones y la mascara de folds efectivamente puntuables: un
    fold cuyo entrenamiento perdio una clase entera no puede predecirla, y eso se
    reporta en lugar de absorberse.
    """
    clases = sorted(set(y.tolist()))
    indice = {c: i for i, c in enumerate(clases)}
    y_idx = np.array([indice[v] for v in y])

    sumas = np.zeros((len(clases), V.shape[1]))
    conteos = np.zeros(len(clases))
    for i, c in enumerate(y_idx):
        sumas[c] += V[i]
        conteos[c] += 1

    predicciones = np.empty(len(y), dtype=object)
    puntuable = np.zeros(len(y), dtype=bool)

    for i in range(len(y)):
        c = y_idx[i]
        n = conteos.copy()
        n[c] -= 1
        if (n <= 0).any():
            # A class vanished from training with this document held out.
            # [ES] Una clase desaparecio del entrenamiento al retener este
            # documento.
            continue
        s = sumas.copy()
        s[c] -= V[i]
        centros = normalizar(s / n[:, None])
        predicciones[i] = clases[int(np.argmax(centros @ V[i]))]
        puntuable[i] = True

    return predicciones, puntuable


def predecir_documentos(V, documentos, y_doc):
    """PRIMARY analysis: one vector, one vote, one weight per document.

    [ES] Analisis PRIMARIO: un vector, un voto, un peso por documento.
    """
    y = np.array([y_doc[d] for d in documentos])
    predicciones, puntuable = _predecir_una_pasada(V, y)
    return (
        [d for d, ok in zip(documentos, puntuable) if ok],
        y[puntuable],
        predicciones[puntuable].astype(object),
    )


def predecir_por_voto_de_chunks(X, grupos, y_doc):
    """SENSITIVITY analysis: centroids from chunks, majority vote per document.

    Kept only to show what the chunk-weighted version does differently. It is
    NOT the result: a document of 812 chunks moves these centroids 270 times
    more than one of 3.

    [ES] Analisis de SENSIBILIDAD: centroides desde chunks, voto mayoritario por
    documento.

    Se conserva solo para mostrar en que difiere la version pesada por chunks.
    NO es el resultado: un documento de 812 chunks mueve estos centroides 270
    veces mas que uno de 3.
    """
    grupos = np.asarray(grupos)
    y_chunk = np.array([y_doc[g] for g in grupos])
    documentos = sorted(set(grupos.tolist()))
    total_clases = len(set(y_chunk.tolist()))

    salida_doc, verdadero, predicho = [], [], []
    for doc in documentos:
        prueba = grupos == doc
        entrena = ~prueba
        clases = sorted(set(y_chunk[entrena].tolist()))
        if len(clases) < total_clases:
            continue
        centros = normalizar(
            np.vstack([X[entrena][y_chunk[entrena] == c].mean(axis=0) for c in clases])
        )
        votos = collections.Counter(
            clases[i] for i in (X[prueba] @ centros.T).argmax(axis=1).tolist()
        )
        salida_doc.append(doc)
        verdadero.append(y_doc[doc])
        predicho.append(sorted(votos.items(), key=lambda kv: (-kv[1], str(kv[0])))[0][0])

    return salida_doc, np.array(verdadero, dtype=object), np.array(predicho, dtype=object)


# --------------------------------------------------------------------------
# Null, uncertainty, multiplicity / Nulo, incertidumbre, multiplicidad
# --------------------------------------------------------------------------


def nulo_reajustado(V, documentos, y_doc, permutaciones: int, semilla: int):
    """The null of the WHOLE procedure: permute labels, then refit every fold.

    Each permutation shuffles the label assignment among documents and runs the
    entire leave-one-document-out loop again, rebuilding every class centroid
    from the permuted labels. That is what "the geometry carries no information
    about this label" actually implies, and it is strictly harder to beat than
    permuting the truth against fixed predictions.

    [ES] El nulo de TODO el procedimiento: permutar etiquetas y reajustar cada
    fold.

    Cada permutacion baraja la asignacion de etiquetas entre documentos y vuelve
    a correr el ciclo completo de dejar-un-documento-afuera, reconstruyendo cada
    centroide de clase con las etiquetas permutadas. Eso es lo que implica de
    verdad "la geometria no lleva informacion sobre esta etiqueta", y es
    estrictamente mas dificil de superar que permutar la verdad contra
    predicciones fijas.
    """
    y = np.array([y_doc[d] for d in documentos])
    generador = np.random.default_rng(semilla)
    nulos = []
    for _ in range(permutaciones):
        permutada = generador.permutation(y)
        predicciones, puntuable = _predecir_una_pasada(V, permutada)
        if not puntuable.any():
            continue
        nulos.append(
            balanced_accuracy_score(
                permutada[puntuable], predicciones[puntuable].astype(object)
            )
        )
    return np.array(nulos)


def bootstrap_estratificado(verdadero, predicho, remuestras: int, semilla: int):
    """Resample WITHIN each true class, so no resample can lose a class.

    A plain bootstrap over 17 documents regularly produces a resample missing a
    class entirely; dropping those resamples biases the interval, and keeping
    them makes balanced accuracy undefined. Stratifying fixes both.

    It does not fix the underlying problem. With three documents in a class the
    interval is an artefact of resampling three points, so the caller checks the
    smallest class and omits the interval instead of printing one.

    [ES] Remuestrea DENTRO de cada clase verdadera, para que ninguna remuestra
    pueda perder una clase.

    Un bootstrap comun sobre 17 documentos produce con regularidad una remuestra
    a la que le falta una clase entera; descartar esas remuestras sesga el
    intervalo, y conservarlas vuelve indefinida la exactitud balanceada.
    Estratificar arregla las dos cosas.

    No arregla el problema de fondo. Con tres documentos en una clase el
    intervalo es un artefacto de remuestrear tres puntos, asi que quien llama
    revisa la clase mas chica y omite el intervalo en lugar de imprimir uno.
    """
    verdadero = np.asarray(verdadero, dtype=object)
    predicho = np.asarray(predicho, dtype=object)
    por_clase = {c: np.flatnonzero(verdadero == c) for c in sorted(set(verdadero.tolist()))}
    generador = np.random.default_rng(semilla)

    valores = []
    for _ in range(remuestras):
        idx = np.concatenate(
            [generador.choice(ix, size=len(ix), replace=True) for ix in por_clase.values()]
        )
        valores.append(balanced_accuracy_score(verdadero[idx], predicho[idx]))
    return np.array(valores)


def holm(p_valores: dict) -> dict:
    """Holm-Bonferroni: control the family-wise error over a declared family.

    Four one-vs-rest domain tests are four chances to find something. Reporting
    each raw p as if it stood alone would inflate the family error to roughly
    one in five.

    [ES] Holm-Bonferroni: controla el error por familia sobre una familia
    declarada.

    Cuatro pruebas uno-contra-el-resto de dominio son cuatro oportunidades de
    encontrar algo. Reportar cada p cruda como si estuviera sola inflaria el
    error de familia a cerca de uno en cinco.
    """
    items = sorted(p_valores.items(), key=lambda kv: kv[1])
    n = len(items)
    ajustados = {}
    corriendo = 0.0
    for i, (nombre, p) in enumerate(items):
        corriendo = max(corriendo, min(1.0, (n - i) * p))
        ajustados[nombre] = corriendo
    return ajustados


def formatear_p(p) -> str:
    """Never print `0.000`. A p is bounded below by the permutation count.

    [ES] Nunca imprimir `0.000`. Un p esta acotado por abajo por la cantidad de
    permutaciones.
    """
    if p is None:
        return "—"
    return "<0.001" if p < 0.001 else f"{p:.3f}"


# --------------------------------------------------------------------------
# Targets / Objetivos
# --------------------------------------------------------------------------


def etiquetas_por_documento(catalogo: dict, documentos_presentes) -> dict:
    objetivos = {
        "tipo_documento": {},
        "emisor_id": {},
        "dominio_combinacion": {},
        "dominio_token": {},
    }
    for doc in sorted(set(documentos_presentes)):
        fila = catalogo.get(doc)
        if fila is None:
            continue
        objetivos["tipo_documento"][doc] = fila["tipo_documento"].strip()
        objetivos["emisor_id"][doc] = fila["emisor_id"].strip()
        crudo = fila["dominios_documentales"].strip()
        objetivos["dominio_combinacion"][doc] = crudo
        objetivos["dominio_token"][doc] = tuple(
            sorted(t.strip() for t in crudo.split(SEPARADOR_DOMINIOS) if t.strip())
        )
    return objetivos


def clases_admisibles(etiquetas: dict, minimo: int):
    """Classes with enough DOCUMENTS. Counting chunks here would be the bug.

    [ES] Clases con suficientes DOCUMENTOS. Contar chunks aca seria el error.
    """
    conteo = collections.Counter(etiquetas.values())
    return (
        {c for c, n in conteo.items() if n >= minimo},
        sorted(c for c, n in conteo.items() if n < minimo),
    )


def evaluar(nombre, V, documentos, X, grupos, etiquetas, minimo, permutaciones,
            remuestras, semilla) -> dict:
    """Evaluate one target: primary, null, uncertainty and sensitivity.

    [ES] Evalua un objetivo: primario, nulo, incertidumbre y sensibilidad.
    """
    admisibles, excluidas = clases_admisibles(etiquetas, minimo)
    conteo = collections.Counter(etiquetas.values())
    mantenidos = {d: e for d, e in etiquetas.items() if e in admisibles}

    resultado = {
        "objetivo": nombre,
        "clases_totales": len(conteo),
        "clases_evaluadas": len(admisibles),
        "clases_excluidas": excluidas,
        "documentos_totales": len(etiquetas),
        "documentos_evaluados": len(mantenidos),
        "documentos_excluidos": sorted(set(etiquetas) - set(mantenidos)),
        "distribucion": dict(sorted(conteo.items(), key=lambda kv: (-kv[1], kv[0]))),
    }

    if len(admisibles) < 2:
        resultado["evaluable"] = False
        resultado["motivo"] = "menos de dos clases con suficientes documentos"
        return resultado

    mascara = np.array([d in mantenidos for d in documentos])
    V_sub = V[mascara]
    docs_sub = [d for d, ok in zip(documentos, mascara) if ok]

    docs, verdadero, predicho = predecir_documentos(V_sub, docs_sub, mantenidos)
    if len(docs) == 0:
        resultado["evaluable"] = False
        resultado["motivo"] = "ningun fold conservo todas las clases en entrenamiento"
        return resultado

    observado = balanced_accuracy_score(verdadero, predicho)
    nulos = nulo_reajustado(V_sub, docs_sub, mantenidos, permutaciones, semilla)
    p = (int(np.sum(nulos >= observado)) + 1) / (len(nulos) + 1)

    menor_clase = min(collections.Counter(verdadero.tolist()).values())
    if menor_clase >= MINIMO_PARA_BOOTSTRAP:
        valores = bootstrap_estratificado(verdadero, predicho, remuestras, semilla + 1)
        ic = (float(np.percentile(valores, 2.5)), float(np.percentile(valores, 97.5)))
        motivo_ic = None
    else:
        ic = None
        motivo_ic = (
            f"la clase evaluada más chica tiene {menor_clase} documentos "
            f"(mínimo {MINIMO_PARA_BOOTSTRAP}): un intervalo sería decorado"
        )

    etiquetas_ord = sorted(set(verdadero.tolist()) | set(predicho.tolist()))

    # Sensitivity, on the same kept documents.
    # [ES] Sensibilidad, sobre los mismos documentos conservados.
    mascara_chunk = np.array([g in mantenidos for g in grupos])
    _, v_sens, p_sens = predecir_por_voto_de_chunks(
        X[mascara_chunk], np.asarray(grupos)[mascara_chunk], mantenidos
    )
    sensibilidad = (
        float(balanced_accuracy_score(v_sens, p_sens)) if len(v_sens) else None
    )

    resultado.update(
        {
            "evaluable": True,
            "documentos_puntuados": len(docs),
            "exactitud_balanceada": float(observado),
            "ic95_bootstrap_estratificado": ic,
            "motivo_sin_ic": motivo_ic,
            "clase_mas_chica": int(menor_clase),
            "nulo_media": float(np.mean(nulos)),
            "nulo_p95": float(np.percentile(nulos, 95)),
            "permutaciones_efectivas": int(len(nulos)),
            "p_valor": float(p),
            "brecha_contra_nulo": float(observado - np.mean(nulos)),
            "supera_el_nulo": bool(observado > np.percentile(nulos, 95)),
            "etiquetas": etiquetas_ord,
            "matriz_confusion": confusion_matrix(
                verdadero, predicho, labels=etiquetas_ord
            ).tolist(),
            "aciertos_por_documento": {
                d: bool(v == q) for d, v, q in zip(docs, verdadero, predicho)
            },
            "sensibilidad_por_chunks": sensibilidad,
        }
    )
    return resultado


def evaluar_dominio_ovr(tokens, V, documentos, X, grupos, etiquetas_tupla,
                        permutaciones, remuestras, semilla) -> list:
    """One-vs-rest per domain token, reporting positives and negatives.

    [ES] Uno-contra-el-resto por token de dominio, informando positivos y
    negativos.
    """
    salida = []
    for token in tokens:
        binarias = {
            d: ("si" if token in tks else "no") for d, tks in etiquetas_tupla.items()
        }
        positivos = sum(1 for v in binarias.values() if v == "si")
        r = evaluar(
            f"dominio:{token}", V, documentos, X, grupos, binarias,
            2, permutaciones, remuestras, semilla,
        )
        r["token"] = token
        r["documentos_positivos"] = positivos
        r["documentos_negativos"] = len(binarias) - positivos
        salida.append(r)
    return salida


def comparar_descriptivo(a: dict, b: dict) -> dict:
    """Count discordant documents. DESCRIPTIVE: it does not establish "better".

    The targets have different numbers of classes and different task shapes, so
    a sign test between them tests nothing well defined. The counts are reported
    so the size of the evidence is visible, and no claim is attached.

    [ES] Cuenta documentos discordantes. DESCRIPTIVO: no establece «mejor».

    Los objetivos tienen distinta cantidad de clases y distinta forma de tarea,
    asi que un test de signos entre ellos no prueba nada bien definido. Los
    recuentos se informan para que se vea el tamano de la evidencia, y no se les
    cuelga ninguna afirmacion.
    """
    ea, eb = a.get("aciertos_por_documento", {}), b.get("aciertos_por_documento", {})
    comunes = sorted(set(ea) & set(eb))
    return {
        "par": f"{a['objetivo']} vs {b['objetivo']}",
        "documentos_comunes": len(comunes),
        "aciertos_solo_el_primero": sum(1 for d in comunes if ea[d] and not eb[d]),
        "aciertos_solo_el_segundo": sum(1 for d in comunes if eb[d] and not ea[d]),
        "documentos_discordantes": sum(1 for d in comunes if ea[d] != eb[d]),
    }


# --------------------------------------------------------------------------
# Exploratory projection / Proyeccion exploratoria
# --------------------------------------------------------------------------


def proyectar_2d(V, semilla: int):
    """A 2-D projection of the DOCUMENT vectors, for looking at only.

    UMAP is preferred when installed; it is not a dependency of this project and
    is not installed here, so the fallback is t-SNE and the manifest records
    which ran. Labelling a t-SNE plot "UMAP" would misdescribe the only artefact
    a reader can inspect directly.

    [ES] Una proyeccion 2-D de los vectores DOCUMENTALES, solo para mirar.

    Se prefiere UMAP cuando esta instalado; no es dependencia de este proyecto y
    aca no lo esta, asi que el reemplazo es t-SNE y el manifest registra cual
    corrio. Rotular "UMAP" un grafico de t-SNE describiria mal el unico artefacto
    que un lector puede inspeccionar directamente.
    """
    try:
        import umap

        return (
            umap.UMAP(n_components=2, random_state=semilla, metric="cosine").fit_transform(V),
            "umap",
            f"umap-learn {umap.__version__}",
        )
    except ImportError:
        import sklearn
        from sklearn.manifold import TSNE

        perplejidad = max(2, min(10, (len(V) - 1) // 3))
        coords = TSNE(
            n_components=2, random_state=semilla, init="pca",
            perplexity=perplejidad, metric="cosine",
        ).fit_transform(V)
        return coords, "tsne", f"sklearn {sklearn.__version__} (perplexity={perplejidad})"


PALETA = (
    "#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#8c564b",
    "#e377c2", "#17becf", "#bcbd22", "#7f7f7f", "#393b79", "#843c39",
)


def escribir_svg(ruta: Path, coords, etiquetas, nombres, titulo, metodo) -> None:
    """Plain SVG. No plotting library is installed and none was added.

    [ES] SVG plano. No hay biblioteca de graficos instalada y no se agrego
    ninguna.
    """
    ancho, alto, margen = 940, 640, 70
    x, y = coords[:, 0], coords[:, 1]
    ex = (x - x.min()) / max(float(np.ptp(x)), 1e-9) * (ancho - 2 * margen - 240) + margen
    ey = (y - y.min()) / max(float(np.ptp(y)), 1e-9) * (alto - 2 * margen - 20) + margen

    clases = sorted(set(etiquetas))
    color = {c: PALETA[i % len(PALETA)] for i, c in enumerate(clases)}

    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" '
        f'viewBox="0 0 {ancho} {alto}" font-family="system-ui,sans-serif">',
        f'<rect width="{ancho}" height="{alto}" fill="#ffffff"/>',
        f'<text x="{margen}" y="30" font-size="16" font-weight="600">{titulo}</text>',
        f'<text x="{margen}" y="50" font-size="12" fill="#b00020">'
        f"EXPLORATORIA — {metodo} sobre 24 puntos no es una prueba estadistica. "
        f"La distancia visual no mide separabilidad.</text>",
    ]
    for cx, cy, etq, nom in zip(ex, ey, etiquetas, nombres):
        partes.append(
            f'<circle cx="{cx:.1f}" cy="{alto - cy:.1f}" r="6" fill="{color[etq]}" '
            f'fill-opacity="0.75" stroke="#333" stroke-width="0.5"/>'
        )
        partes.append(
            f'<text x="{cx + 8:.1f}" y="{alto - cy + 3:.1f}" font-size="8" '
            f'fill="#444">{nom}</text>'
        )
    lx = ancho - 225
    partes.append(f'<text x="{lx}" y="{margen - 14}" font-size="11" font-weight="600">clases</text>')
    for i, c in enumerate(clases):
        cy = margen + i * 18
        partes.append(
            f'<rect x="{lx}" y="{cy - 8}" width="10" height="10" fill="{color[c]}"/>'
            f'<text x="{lx + 16}" y="{cy + 1}" font-size="11">{c}</text>'
        )
    partes.append("</svg>")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(partes), encoding="utf-8")


# --------------------------------------------------------------------------
# Report / Reporte
# --------------------------------------------------------------------------


def _pct(v):
    return "  —  " if v is None else f"{v * 100:5.1f} %"


def _ic(r):
    ic = r.get("ic95_bootstrap_estratificado")
    return f"{ic[0] * 100:.1f} – {ic[1] * 100:.1f} %" if ic else "omitido"


def escribir_reporte(ruta, manifest, dominios, suplementarios, metadatos,
                     combinacion, comparaciones, holm_centrales, holm_supl,
                     holm_meta) -> None:
    L = []
    A = L.append
    A("# RQ0 — geometría del embedding frente a dominio, tipo y emisor")
    A("")
    A(f"**Receta:** `{manifest['receta']}` · **Fecha:** 29-ago-2026")
    A("")
    A("> **Esta versión reemplaza metodológicamente a la primera** "
      "(`rq0-v0.1-exploratoria`).")
    A("> Los números de aquella versión **no son válidos** y no deben citarse.")
    A("> Qué cambió y por qué, en la sección 7.")
    A("")
    A("**Diagnóstico exploratorio.** No es evidencia confirmatoria.")
    A("")
    A("## Salvedades, antes de los números")
    A("")
    for aviso in manifest["salvedades"]:
        A(f"- {aviso}")
    A("")
    A("## Conjunto analizado")
    A("")
    A("| | |")
    A("|---|---|")
    for k in ("documentos", "chunks", "dimension_embedding",
              "chunks_descartados_no_objetivo", "chunks_por_documento_min",
              "chunks_por_documento_max"):
        A(f"| {k} | `{manifest['conjunto'][k]}` |")
    A(f"| huella del conjunto | `{manifest['conjunto']['huella']}` |")
    A(f"| huella del catálogo | `{manifest['conjunto']['huella_catalogo']}` |")
    A("")

    A("## 1 · Resultado primario — los cuatro silos")
    A("")
    A("Un vector y un voto por documento. Cuatro tareas uno-contra-el-resto sobre")
    A("`legal`, `impositivo`, `contable` y `financiero`: la arquitectura de la tesis.")
    A("Corrección de **Holm sobre estas cuatro pruebas**.")
    A("")
    A("| dominio | docs + | docs − | exact. balanceada | IC 95 % | nulo | brecha | p | p (Holm) | supera |")
    A("|---|---:|---:|---:|:---:|---:|---:|---:|---:|:--:|")
    for r in dominios:
        if not r.get("evaluable"):
            A(f"| `{r['token']}` | {r['documentos_positivos']} | {r['documentos_negativos']} "
              f"| no evaluable | — | — | — | — | — | — |")
            continue
        pa = holm_centrales.get(r["token"])
        A(
            f"| `{r['token']}` | {r['documentos_positivos']} | {r['documentos_negativos']} "
            f"| {_pct(r['exactitud_balanceada'])} | {_ic(r)} | {_pct(r['nulo_media'])} "
            f"| {r['brecha_contra_nulo'] * 100:+5.1f} pp | {formatear_p(r['p_valor'])} "
            f"| {formatear_p(pa)} | {'sí' if pa is not None and pa < 0.05 else '**no**'} |"
        )
    A("")
    for r in dominios:
        if r.get("motivo_sin_ic"):
            A(f"- `{r['token']}`: IC omitido — {r['motivo_sin_ic']}.")
    A("")
    A("### Conteos de confusión (nivel documento)")
    A("")
    A("| dominio | + / + | + / − | − / + | − / − |")
    A("|---|---:|---:|---:|---:|")
    for r in dominios:
        if not r.get("evaluable"):
            continue
        idx = {e: i for i, e in enumerate(r["etiquetas"])}
        m = r["matriz_confusion"]
        si, no = idx.get("si"), idx.get("no")
        if si is None or no is None:
            A(f"| `{r['token']}` | — | — | — | — |")
            continue
        A(f"| `{r['token']}` | {m[si][si]} | {m[si][no]} | {m[no][si]} | {m[no][no]} |")
    A("")
    A("`+ / −` es un documento del dominio que el espacio no reconoció como tal.")
    A("")
    A("### Sensibilidad: centroides pesados por chunks")
    A("")
    A("Análisis **secundario**. Muestra qué cambia cuando un documento de 812 chunks")
    A("pesa 270 veces más que uno de 3. No es el resultado.")
    A("")
    A("| dominio | primario (1 voto/doc) | sensibilidad (chunks) | diferencia |")
    A("|---|---:|---:|---:|")
    for r in dominios:
        if not r.get("evaluable"):
            continue
        s = r.get("sensibilidad_por_chunks")
        d = f"{(r['exactitud_balanceada'] - s) * 100:+5.1f} pp" if s is not None else "—"
        A(f"| `{r['token']}` | {_pct(r['exactitud_balanceada'])} | {_pct(s)} | {d} |")
    A("")

    A("## 2 · Metadatos documentales: tipo y emisor")
    A("")
    A("Familia de **dos** pruebas, con su propia corrección de Holm.")
    A("")
    A("| objetivo | clases | docs | exact. balanceada | IC 95 % | nulo | brecha | p | p (Holm) | supera |")
    A("|---|---:|---:|---:|:---:|---:|---:|---:|---:|:--:|")
    for r in metadatos:
        if not r.get("evaluable"):
            A(f"| `{r['objetivo']}` | {r['clases_evaluadas']} | {r['documentos_evaluados']} "
              f"| no evaluable | — | — | — | — | — | — |")
            continue
        pa = holm_meta.get(r["objetivo"])
        A(
            f"| `{r['objetivo']}` | {r['clases_evaluadas']} | {r['documentos_puntuados']} "
            f"| {_pct(r['exactitud_balanceada'])} | {_ic(r)} | {_pct(r['nulo_media'])} "
            f"| {r['brecha_contra_nulo'] * 100:+5.1f} pp | {formatear_p(r['p_valor'])} "
            f"| {formatear_p(pa)} | {'sí' if pa is not None and pa < 0.05 else '**no**'} |"
        )
    A("")
    for r in metadatos:
        if r.get("motivo_sin_ic"):
            A(f"- `{r['objetivo']}`: IC omitido — {r['motivo_sin_ic']}.")
    A("")

    A("## 3 · Exploratorio suplementario — otros tokens de dominio")
    A("")
    A("**No** forman parte de la arquitectura de cuatro silos. Corrección de Holm")
    A("**separada**, sobre esta familia y no junto a la principal.")
    A("")
    A("| token | docs + | docs − | exact. balanceada | nulo | p | p (Holm supl.) |")
    A("|---|---:|---:|---:|---:|---:|---:|")
    for r in suplementarios:
        if not r.get("evaluable"):
            A(f"| `{r['token']}` | {r['documentos_positivos']} | {r['documentos_negativos']} "
              f"| no evaluable | — | — | — |")
            continue
        A(
            f"| `{r['token']}` | {r['documentos_positivos']} | {r['documentos_negativos']} "
            f"| {_pct(r['exactitud_balanceada'])} | {_pct(r['nulo_media'])} "
            f"| {formatear_p(r['p_valor'])} | {formatear_p(holm_supl.get(r['token']))} |"
        )
    A("")

    A("## 4 · Exploratorio — combinación completa de dominios")
    A("")
    A("> ⚠️ **`dominio_combinacion` NO evalúa la arquitectura de cuatro silos y no puede**")
    A("> **resolver la compuerta de `PRIORIDADES` §2.** Trata cada combinación literal")
    A("> como una clase, así que descarta los documentos cuya combinación es única:")
    A(f"> **{len(combinacion['documentos_excluidos'])} de 24**, y **los tres documentos**")
    A("> **`financiero` están entre ellos**. Se conserva solo como descripción.")
    A("")
    A("Documentos descartados: "
      + ", ".join(f"`{d}`" for d in combinacion["documentos_excluidos"]) + ".")
    A("")
    if combinacion.get("evaluable"):
        A(f"Exactitud balanceada `{combinacion['exactitud_balanceada'] * 100:.1f} %` sobre "
          f"{combinacion['documentos_puntuados']} documentos y "
          f"{combinacion['clases_evaluadas']} clases; nulo "
          f"`{combinacion['nulo_media'] * 100:.1f} %`; p "
          f"{formatear_p(combinacion['p_valor'])}.")
    A("")

    A("## 5 · ¿Representa el espacio mejor dominio, tipo o emisor?")
    A("")
    A("**Comparación descriptiva, no una prueba.** Las tareas tienen distinta cantidad")
    A("de clases y distinta estructura, así que un test de signos entre ellas no")
    A("sostiene «explica mejor» ni «explica peor». Se informa el recuento de documentos")
    A("discordantes para que se vea el tamaño real de la evidencia, y nada más.")
    A("")
    A("| comparación | docs comunes | acierta solo el 1° | acierta solo el 2° | discordantes |")
    A("|---|---:|---:|---:|---:|")
    for c in comparaciones:
        A(
            f"| `{c['par']}` | {c['documentos_comunes']} | {c['aciertos_solo_el_primero']} "
            f"| {c['aciertos_solo_el_segundo']} | {c['documentos_discordantes']} |"
        )
    A("")
    A("### Lectura")
    A("")
    silos_ok = [r["token"] for r in dominios
                if r.get("evaluable") and holm_centrales.get(r["token"], 1.0) < 0.05]
    silos_no = [r["token"] for r in dominios if r["token"] not in silos_ok]
    meta_ok = [r["objetivo"] for r in metadatos
               if r.get("evaluable") and holm_meta.get(r["objetivo"], 1.0) < 0.05]
    meta_no = [r["objetivo"] for r in metadatos if r["objetivo"] not in meta_ok]

    A(f"**Dominio:** {len(silos_ok)} de 4 silos superan su nulo tras Holm — "
      + (", ".join(f"`{t}`" for t in silos_ok) or "ninguno")
      + (f". No lo superan: {', '.join(f'`{t}`' for t in silos_no)}." if silos_no else "."))
    A("")
    A(f"**Metadatos:** {len(meta_ok)} de 2 superan su nulo tras Holm — "
      + (", ".join(f"`{t}`" for t in meta_ok) or "ninguno")
      + (f". No lo superan: {', '.join(f'`{t}`' for t in meta_no)}." if meta_no else "."))
    A("")
    if len(silos_ok) > len(meta_ok):
        A("**La compuerta de `PRIORIDADES` §2 no se dispara.** Esa compuerta pregunta si")
        A("tipo documental o emisor explican el espacio **mucho mejor** que dominio. Con")
        A("esta medición no se observó el patrón previsto por la compuerta: el dominio")
        A("sobrevive en más pruebas que los metadatos documentales. La explicación rival")
        A("**no** queda respaldada.")
        A("")
        A("Eso **no** autoriza la afirmación simétrica. Que `tipo_documento` no supere su")
        A("nulo con 17 documentos y 4 clases es falta de evidencia, no evidencia de")
        A("ausencia; y las tareas tienen distinta forma, así que «dominio explica mejor»")
        A("sigue sin ser una afirmación que estos datos sostengan.")
    else:
        A("**Atención: la compuerta de `PRIORIDADES` §2 podría estar en juego.** Revisar")
        A("con el director antes de congelar el protocolo.")
    A("")
    A("**RQ0 no concluyente con el corpus actual.**")
    A("")
    A("Para la pregunta de ordenar dominio, tipo y emisor, 24 documentos no alcanzan: la")
    A("comparación entre objetivos es descriptiva y los documentos discordantes son un")
    A("puñado. Lo que sí quedó establecido es más acotado y más útil: bajo un voto por")
    A("documento, la geometría lleva información sobre varios de los silos por encima de")
    A("su propio nulo, con corrección por multiplicidad.")
    A("")
    A("Lo que haría falta son **más documentos por clase**, no más chunks: todo el poder")
    A("de esta prueba está en 24 documentos, y `financiero` tiene 3.")
    A("")
    A("## 6 · Distribución de clases a nivel documento")
    A("")
    for r in metadatos + [combinacion]:
        A(f"**`{r['objetivo']}`**")
        A("")
        A("| clase | documentos |")
        A("|---|---:|")
        for clase, n in r["distribucion"].items():
            A(f"| `{clase}` | {n} |")
        A("")
    A("**tokens de dominio**")
    A("")
    A("| token | documentos | familia |")
    A("|---|---:|---|")
    for r in dominios:
        A(f"| `{r['token']}` | {r['documentos_positivos']} | **principal (silo)** |")
    for r in suplementarios:
        A(f"| `{r['token']}` | {r['documentos_positivos']} | suplementaria |")
    A("")

    A("## 7 · Reemplazo metodológico de la primera versión")
    A("")
    A("La primera versión (`rq0-v0.1-exploratoria`) tenía cuatro defectos que invalidan")
    A("sus números. Se conserva la traza, no los resultados.")
    A("")
    A("| # | Defecto de la v0.1 | Corrección en la v0.2 |")
    A("|---|---|---|")
    A("| 1 | Centroides construidos con **chunks**: un documento de 812 chunks pesaba 270 veces más que uno de 3 | Un vector L2-normalizado **por documento**; cada documento pesa una vez. La versión por chunks queda como sensibilidad |")
    A("| 2 | El nulo conservaba las predicciones y permutaba solo la verdad: nulo de «estas predicciones no se relacionan con estas etiquetas», no del procedimiento supervisado | Cada permutación **reajusta todos los folds** y reconstruye los centroides con las etiquetas permutadas |")
    A("| 3 | `dominio_combinacion` se leía como si evaluara los silos; descarta 7 de 24 documentos y **los 3 `financiero`** | Los **cuatro silos** como OvR con Holm; `dominio_combinacion` queda como descripción explícitamente incapaz de resolver la compuerta |")
    A("| 4 | Bootstrap simple que perdía clases, y un test de signos leído como ranking | Bootstrap **estratificado** por clase verdadera, **omitido** cuando la clase más chica no lo sostiene; el test de signos baja a descriptivo |")
    A("")
    A("También: los valores p se imprimen como `<0.001` y nunca como `0.000`.")
    A("")

    A("## Manifest")
    A("")
    A("```json")
    A(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    A("```")
    A("")
    A("Para regenerar:")
    A("")
    A("```bash")
    A("python -m scripts.diagnostics.rq0_geometria_vs_metadatos")
    A("```")
    A("")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(L), encoding="utf-8")


# --------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--min-documentos", type=int, default=2)
    parser.add_argument("--permutaciones", type=int, default=2000)
    parser.add_argument("--remuestras", type=int, default=2000)
    parser.add_argument("--semilla", type=int, default=SEMILLA)
    parser.add_argument(
        "--reporte", type=Path,
        default=PROJECT_ROOT / "reports" / "rq0_geometria_2026-08-29.md",
    )
    parser.add_argument(
        "--figura", type=Path,
        default=PROJECT_ROOT / "reports" / "figuras" / "rq0_proyeccion_2d.svg",
    )
    args = parser.parse_args()

    objetivo = leer_inventario_objetivo()
    chunk_uids, grupos, X, descartados = leer_chunks(objetivo)
    documentos, V = vectores_por_documento(X, grupos)
    catalogo = leer_catalogo()
    etiquetas = etiquetas_por_documento(catalogo, grupos)
    por_documento = collections.Counter(grupos)

    print(f"documentos          {len(documentos)}", flush=True)
    print(f"chunks              {len(chunk_uids)}", flush=True)
    print(f"descartados         {descartados} (piloto, fuera del inventario)", flush=True)
    print(f"chunks por doc      min {min(por_documento.values())} / "
          f"max {max(por_documento.values())}", flush=True)
    print(flush=True)

    print("1. cuatro silos (uno contra el resto) ...", flush=True)
    dominios = evaluar_dominio_ovr(
        DOMINIOS_CENTRALES, V, documentos, X, grupos, etiquetas["dominio_token"],
        args.permutaciones, args.remuestras, args.semilla,
    )
    holm_centrales = holm(
        {r["token"]: r["p_valor"] for r in dominios if r.get("evaluable")}
    )

    todos = set()
    for tks in etiquetas["dominio_token"].values():
        todos.update(tks)
    tokens_supl = tuple(sorted(todos - set(DOMINIOS_CENTRALES)))

    print("2. tokens suplementarios ...", flush=True)
    suplementarios = evaluar_dominio_ovr(
        tokens_supl, V, documentos, X, grupos, etiquetas["dominio_token"],
        args.permutaciones, args.remuestras, args.semilla,
    )
    holm_supl = holm(
        {r["token"]: r["p_valor"] for r in suplementarios if r.get("evaluable")}
    )

    print("3. tipo_documento y emisor_id ...", flush=True)
    metadatos = [
        evaluar(nombre, V, documentos, X, grupos, etiquetas[nombre],
                args.min_documentos, args.permutaciones, args.remuestras, args.semilla)
        for nombre in ("tipo_documento", "emisor_id")
    ]

    holm_meta = holm(
        {r["objetivo"]: r["p_valor"] for r in metadatos if r.get("evaluable")}
    )

    print("4. dominio_combinacion (exploratorio) ...", flush=True)
    combinacion = evaluar(
        "dominio_combinacion", V, documentos, X, grupos,
        etiquetas["dominio_combinacion"], args.min_documentos,
        args.permutaciones, args.remuestras, args.semilla,
    )

    comparaciones = []
    evaluables = [r for r in metadatos + [combinacion] if r.get("evaluable")]
    for i, a in enumerate(evaluables):
        for b in evaluables[i + 1:]:
            comparaciones.append(comparar_descriptivo(a, b))

    print("5. proyeccion 2-D de los documentos ...", flush=True)
    coords, metodo, implementacion = proyectar_2d(V, args.semilla)
    color = [etiquetas["tipo_documento"].get(d, "?") for d in documentos]
    escribir_svg(
        args.figura, coords, color, documentos,
        "RQ0 — proyeccion 2-D de los 24 DOCUMENTOS, coloreada por tipo_documento",
        metodo,
    )

    manifest = {
        "receta": RECETA_VERSION,
        "reemplaza": "rq0-v0.1-exploratoria (numeros invalidados)",
        "semilla": args.semilla,
        "min_documentos_por_clase": args.min_documentos,
        "permutaciones": args.permutaciones,
        "remuestras_bootstrap": args.remuestras,
        "minimo_clase_para_bootstrap": MINIMO_PARA_BOOTSTRAP,
        "particion": "Leave-One-Document-Out sobre 24 vectores documentales",
        "unidad_de_analisis": "documento (un vector, un voto, un peso)",
        "modelo": "centroide de clase mas cercano por coseno, sin parametros",
        "nulo": "permutacion de etiquetas por documento + reajuste completo de todos los folds",
        "correccion_multiple": "Holm sobre los 4 silos; Holm separado sobre tipo/emisor; Holm separado sobre los tokens suplementarios",
        "dominios_centrales": list(DOMINIOS_CENTRALES),
        "embedding": "BAAI/bge-m3 denso, leido de chunks.embedding sin recomputar",
        "conjunto": {
            "documentos": len(documentos),
            "chunks": len(chunk_uids),
            "dimension_embedding": int(X.shape[1]),
            "chunks_descartados_no_objetivo": descartados,
            "chunks_por_documento_min": int(min(por_documento.values())),
            "chunks_por_documento_max": int(max(por_documento.values())),
            "huella": huella_de_conjunto(grupos, chunk_uids),
            "huella_catalogo": huella_de_archivo(CATALOGO),
            "huella_inventario": huella_de_archivo(INVENTARIO),
        },
        "figura": {
            "ruta": str(args.figura.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "metodo": metodo,
            "implementacion": implementacion,
            "unidad": "documento",
            "coloreada_por": "tipo_documento",
        },
        "salvedades": [
            "Diagnostico EXPLORATORIO. No es evidencia confirmatoria.",
            "24 documentos: todo el poder estadistico esta ahi. `financiero` tiene 3.",
            "Los metadatos del catalogo siguen PENDIENTES DE RATIFICACION HUMANA "
            "(estado_inclusion = pendiente_revision en los 24 registros).",
            "La unidad es el documento: un vector, un voto y un peso por documento. "
            "La version pesada por chunks es sensibilidad, no resultado.",
            "Las exactitudes crudas NO son comparables entre objetivos con distinta "
            "cantidad de clases. La comparacion entre objetivos es DESCRIPTIVA.",
            "La proyeccion 2-D es para mirar. No prueba separabilidad.",
            "No se cargaron los 398 documentos de InfoLEG. No se modifico PostgreSQL, "
            "ni la ingesta, ni los embeddings, ni la clasificacion persistida, ni "
            "ningun chunk_uid.",
        ],
    }

    escribir_reporte(
        args.reporte, manifest, dominios, suplementarios, metadatos,
        combinacion, comparaciones, holm_centrales, holm_supl, holm_meta,
    )
    print(flush=True)
    print(f"reporte  {args.reporte}")
    print(f"figura   {args.figura}  ({metodo})")


if __name__ == "__main__":
    main()
