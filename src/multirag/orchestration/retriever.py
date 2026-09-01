import sys
from multirag.config import RETRIEVAL_TOP_K
from multirag.db import conectar
from multirag.orchestration.alcance import (
    ORIGEN_DOMINIO,
    VARIANTE_ASIGNACION_PREDETERMINADA,
    VARIANTE_EXPANSION_PREDETERMINADA,
    construir_consulta_vectorial,
    construir_filtro_asignacion,
    expandir_por_documento,
    recuperar,
    recuperar_multidominio,
)


def _vector_de_consulta(pregunta: str) -> list[float]:
    """Embed the question. Imported inside the function so that importing this
    module does not load the embedding stack.

    [ES] Embebe la pregunta. Se importa dentro de la función para que importar
    este módulo no cargue la pila de embeddings."""
    from multirag.ingestion.embedder import embed_query

    return embed_query(pregunta)


def buscar(pregunta: str, silo: str = None, k: int = RETRIEVAL_TOP_K,
           documentos: list[str] = None,
           *,
           variante_asignacion: str = VARIANTE_ASIGNACION_PREDETERMINADA,
           assignment_version: str = None,
           taxonomy_version: str = None,
           materiality_version: str = None,
           consulta_procedimental: bool = False) -> list[dict]:
    """Retrieve the top-k chunks most similar to the question (cosine similarity).
        'silo' restricts to one domain (segregated retrieval);
        'documentos' restricts to specific document_id values (diagnostic oracle);
        neither = monolithic baseline. The three arms share THIS function.

        The default is A0: 'silo' is matched against the legacy column
        chunks.silo, exactly as before. Under A1/A2 the same 'silo' argument is
        matched against the versioned membership table instead, and an explicit
        assignment_version is mandatory.

        [ES] El valor predeterminado es A0: 'silo' se compara contra la columna
        heredada chunks.silo, exactamente como antes. Con A1/A2 ese mismo
        argumento se compara contra la tabla versionada de membresías, y la
        assignment_version explícita es obligatoria."""
    vector = _vector_de_consulta(pregunta)
    vector_literal = "[" + ",".join(map(str,vector)) + "]"

    condiciones, params_filtro = construir_filtro_asignacion(
        variante_asignacion=variante_asignacion,
        dominio=silo,
        assignment_version=assignment_version,
        taxonomy_version=taxonomy_version,
        materiality_version=materiality_version,
        consulta_procedimental=consulta_procedimental,
    )

    consulta, params = construir_consulta_vectorial(
        vector_literal=vector_literal,
        k=k,
        condiciones=condiciones,
        parametros_filtro=params_filtro,
        documentos=documentos,
    )

    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, params)
            filas = cursor.fetchall()
    finally:
            conexion.close()

    return [
        {
            "chunk_uid": uid,
            # Inherited physical silo. Its historical meaning does not change:
            # it is the exclusive label of the snapshot, NOT the set of domains
            # the chunk was retrieved through.
            # [ES] Silo físico heredado. Su significado histórico no cambia: es
            # la etiqueta exclusiva del snapshot, NO el conjunto de dominios por
            # los que el chunk fue recuperado.
            "silo": silo_del_chunk,
            "titulo": titulo,
            "contenido": contenido,
            "fuente": fuente,
            "document_id": document_id,
            "instrument_id": instrument_id,
            "artifact_id": artifact_id,
            "similitud": similitud,
            "dominios_recuperacion": [silo] if silo else [],
            "origen_recuperacion": ORIGEN_DOMINIO,
        }
        for (
            uid,
            silo_del_chunk,
            titulo,
            contenido,
            fuente,
            document_id,
            instrument_id,
            artifact_id,
            similitud,
        ) in filas
    ]


def buscar_multidominio(pregunta: str, dominios, k: int = RETRIEVAL_TOP_K,
                        **asignacion) -> list[dict]:
    """Retrieve from a set of domains: validate, union, dedupe by chunk_uid,
    keep the best similarity, record every retrieval domain, rerank and return
    exactly the requested final k.

    [ES] Recupera desde un conjunto de dominios: valida, une, deduplica por
    chunk_uid, conserva la mejor similitud, registra todos los dominios de
    recuperación, rerankea y devuelve exactamente el k final pedido."""
    return recuperar_multidominio(
        pregunta=pregunta,
        dominios=dominios,
        buscar_fn=buscar,
        k=k,
        **asignacion,
    )


def buscar_con_expansion_documental(pregunta: str, semillas,
                                    k: int = RETRIEVAL_TOP_K,
                                    k_hermanos: int = None,
                                    **asignacion) -> list[dict]:
    """E1 over already retrieved seeds: enable siblings of their document_id,
    dedupe, rerank with the same question and trim to the same final k.

    [ES] E1 sobre semillas ya recuperadas: habilita hermanos de su document_id,
    deduplica, rerankea con la misma pregunta y recorta al mismo k final."""
    return expandir_por_documento(
        pregunta=pregunta,
        semillas=semillas,
        buscar_fn=buscar,
        k=k,
        k_hermanos=k_hermanos,
        **asignacion,
    )


def recuperar_declarando_variantes(
        pregunta: str,
        dominios=None,
        k: int = RETRIEVAL_TOP_K,
        variante_asignacion: str = VARIANTE_ASIGNACION_PREDETERMINADA,
        variante_expansion: str = VARIANTE_EXPANSION_PREDETERMINADA,
        **opciones) -> list[dict]:
    """Retrieve declaring both dimensions: assignment (A0/A1/A2) and
    documentary expansion (E0/E1). They are independent.

    [ES] Recupera declarando ambas dimensiones: asignación (A0/A1/A2) y
    expansión documental (E0/E1). Son independientes."""
    return recuperar(
        pregunta=pregunta,
        buscar_fn=buscar,
        dominios=dominios,
        k=k,
        variante_asignacion=variante_asignacion,
        variante_expansion=variante_expansion,
        **opciones,
    )


def _evidencia_por_silo(vector) -> dict:
     """ Best real similarity available in each silo, in ONE query (evidence probe).
     [ES] Mejor similitud REAL disponible en cada silo, en UNA sola consulta (sonda de evidencia)."""
     literal = "[" + ",".join(map(str,vector)) + "]"
     conexion = conectar()
     try:
          with conexion.cursor() as cursor:
               cursor.execute(
                    """SELECT DISTINCT ON (silo) silo, 1 - (embedding <=> %s::vector)
                    FROM chunks ORDER BY silo, embedding <=> %s::vector""",
                    (literal,literal))
               return dict(cursor.fetchall())
     finally:
          conexion.close()


def buscar_ruteado(pregunta: str, k: int = RETRIEVAL_TOP_K) -> list[dict]:
     """Governed router: classify the QUESTION, then retrieve only within the right silo(s).
     Low uncertainty -> hard-route to the top silo (System 1). High uncertainty -> broaden to
     the top-2 silos (System 2), so a cross-domain question isn't lost by a wrong hard route.
     Deterministic. This is S1/S2; buscar() with no silo = S0 (monolithic).
     [ES] Router gobernado: clasifica la PREGUNTA y recupera solo en el/los silo(s) correcto(s).
     Baja incertidumbre -> ruteo duro al silo top (S1). Alta -> abre a los 2 silos top (S2), para
     que una pregunta cross-dominio no se pierda. Determinístico."""
     from multirag.orchestration.clasificador import clasificar
     from multirag.orchestration.gate import evaluar_incertidumbre
     dist = clasificar(pregunta)["silo_scores"]
     gate = evaluar_incertidumbre(dist)
     orden = sorted(dist, key=dist.get, reverse=True)
     silos = orden[:2] if gate["ambiguo"] else orden[:1]
     print(f"[router] {'S2' if gate['ambiguo'] else 'S1'} silos={silos} "
           f"(H={gate['entropia']}, margen={gate['margen']})")
     resultados= []
     for s in silos:
          resultados += buscar(pregunta, silo=s, k=k)
     resultados.sort(key=lambda r: r["similitud"], reverse=True)
     return resultados[:k]


if __name__ == "__main__":
    from multirag.config import SILOS
    args = sys.argv[1:]
    if not args:
         print('Uso: python -m multirag.orchestration.retriever [<silo>] "<pregunta>"')
         sys.exit(1)
    if args[0] in SILOS:
         silo, pregunta = args[0], " ".join(args[1:])
    else:
         silo, pregunta = None, " ".join(args)
    modo = f"silo: {silo}" if silo else "MONOLÍTICO (todos los silos)"
    print(f"[{modo}] Pregunta: {pregunta}\n")
    for r in buscar(pregunta, silo):
         print(f"[sim {r['similitud']:.3f}] ({r['silo']}) {r['titulo']} ({r['fuente']})")
         print(r["contenido"][:200]); print("-" * 40)
