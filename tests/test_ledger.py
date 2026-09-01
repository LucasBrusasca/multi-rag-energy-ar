"""Tests for the execution ledger.

No PostgreSQL: the cursor is faked. What is under test is that a run cannot be
recorded without the data that makes it reconstructible.

[ES] Pruebas del ledger de ejecución.

Sin PostgreSQL: el cursor se simula. Lo que se prueba es que una corrida no
pueda registrarse sin los datos que la vuelven reconstruible.
"""

import json
import unittest


from multirag.evaluation.ledger import (
    ErrorDeLedger,
    construir_consulta,
    construir_corrida,
    construir_evidencia,
    registrar_consulta,
    registrar_corrida,
)


CORRIDA = {
    "corrida_id": "corrida-2026-08-23-piloto",
    "brazos": ["B0", "B1", "B2"],
    "k_final": 3,
    "etapa": "piloto",
}


class CursorFalso:
    """Record the executed statements and their parameters.

    [ES] Registra las sentencias ejecutadas y sus parámetros.
    """

    def __init__(self, id_devuelto: int = 77):
        self.ejecutadas = []
        self.id_devuelto = id_devuelto

    def execute(self, sql, params):
        self.ejecutadas.append((" ".join(sql.split()), params))

    def fetchone(self):
        return (self.id_devuelto,)


def resultado(uid: str, similitud: float, **extra) -> dict:
    base = {
        "chunk_uid": uid,
        "silo": "legal",
        "titulo": "",
        "contenido": "",
        "fuente": "Ley_24065",
        "document_id": "DOC-0013",
        "instrument_id": "INS-0013",
        "artifact_id": "ART-SHA256-AAAA",
        "similitud": similitud,
        "dominios_recuperacion": ["legal"],
        "origen_recuperacion": "dominio",
    }
    base.update(extra)
    return base


class CorridaTestCase(unittest.TestCase):
    """A run without its configuration is not reproducible.

    [ES] Una corrida sin su configuración no es reproducible.
    """

    def test_construye_una_corrida_valida(self) -> None:
        corrida = construir_corrida(**CORRIDA)

        self.assertEqual(corrida["etapa"], "piloto")
        self.assertEqual(corrida["variante_asignacion"], "A0")
        self.assertEqual(corrida["variante_expansion"], "E0")

    def test_rechaza_etapa_desconocida(self) -> None:
        with self.assertRaises(ErrorDeLedger) as contexto:
            construir_corrida(**{**CORRIDA, "etapa": "prueba"})

        self.assertIn("confirmatorio", str(contexto.exception))

    def test_rechaza_brazo_desconocido(self) -> None:
        with self.assertRaises(ErrorDeLedger):
            construir_corrida(**{**CORRIDA, "brazos": ["B0", "B7"]})

    def test_a1_exige_registrar_la_version_de_membresias(self) -> None:
        """Without it, nobody knows which memberships governed the run.

        [ES] Sin eso, nadie sabe qué membresías gobernaron la corrida.
        """
        with self.assertRaises(ErrorDeLedger) as contexto:
            construir_corrida(
                **{**CORRIDA, "variante_asignacion": "A1"}
            )

        self.assertIn("assignment_version", str(contexto.exception))

    def test_a1_con_version_se_acepta(self) -> None:
        corrida = construir_corrida(
            **{
                **CORRIDA,
                "variante_asignacion": "A1",
                "assignment_version": "coseno-margen-0.05",
            }
        )

        self.assertEqual(
            corrida["assignment_version"],
            "coseno-margen-0.05",
        )

    def test_rechaza_k_invalido(self) -> None:
        with self.assertRaises(ErrorDeLedger):
            construir_corrida(**{**CORRIDA, "k_final": 0})

    def test_conserva_la_huella_de_la_receta(self) -> None:
        corrida = construir_corrida(
            **{**CORRIDA, "receta_clasificador_sha256": "903ccb71"}
        )

        self.assertEqual(
            corrida["receta_clasificador_sha256"],
            "903ccb71",
        )


class ConsultaTestCase(unittest.TestCase):
    """The routing decision is recorded as it was made.

    [ES] La decisión de ruteo se registra tal como se tomó.
    """

    def test_construye_una_consulta_valida(self) -> None:
        consulta = construir_consulta(
            corrida_id="c1",
            pregunta="¿Qué sanciones corresponden?",
            brazo="B2",
            silos_abiertos=["legal", "impositivo"],
            router_scores={"legal": 0.6, "impositivo": 0.3},
            router_modo="S2",
        )

        self.assertEqual(
            consulta["silos_abiertos"],
            ["legal", "impositivo"],
        )
        self.assertEqual(consulta["router_modo"], "S2")

    def test_rechaza_pregunta_vacia(self) -> None:
        with self.assertRaises(ErrorDeLedger):
            construir_consulta(
                corrida_id="c1",
                pregunta="   ",
                brazo="B0",
            )

    def test_rechaza_brazo_desconocido(self) -> None:
        with self.assertRaises(ErrorDeLedger):
            construir_consulta(
                corrida_id="c1",
                pregunta="¿Qué dice?",
                brazo="B9",
            )

    def test_conserva_los_tramos_del_veto(self) -> None:
        """A veto that cannot be inspected cannot be defended.

        [ES] Un veto que no se puede inspeccionar no se puede defender.
        """
        spans = [{"start": 10, "end": 25, "confidence": 0.9}]

        consulta = construir_consulta(
            corrida_id="c1",
            pregunta="¿Qué dice?",
            brazo="B0",
            veto_activado=True,
            veto_spans=spans,
        )

        self.assertEqual(consulta["veto_spans"], spans)


class EvidenciaTestCase(unittest.TestCase):
    """The delivered order is preserved, and the identity is copied.

    [ES] Se conserva el orden de entrega y se copia la identidad.
    """

    def test_conserva_el_orden_de_entrega(self) -> None:
        filas = construir_evidencia(
            [
                resultado("a" * 64, 0.9),
                resultado("b" * 64, 0.8),
                resultado("c" * 64, 0.7),
            ]
        )

        self.assertEqual(
            [f["posicion"] for f in filas],
            [1, 2, 3],
        )
        self.assertEqual(filas[0]["chunk_uid"], "a" * 64)

    def test_copia_la_identidad_documental(self) -> None:
        filas = construir_evidencia([resultado("a" * 64, 0.9)])

        self.assertEqual(filas[0]["document_id"], "DOC-0013")
        self.assertEqual(filas[0]["instrument_id"], "INS-0013")
        self.assertEqual(filas[0]["artifact_id"], "ART-SHA256-AAAA")

    def test_distingue_silo_de_dominios_de_recuperacion(self) -> None:
        """They are different things and both are needed for contamination.

        [ES] Son cosas distintas y las dos hacen falta para contaminación.
        """
        filas = construir_evidencia(
            [
                resultado(
                    "a" * 64,
                    0.9,
                    silo="contable",
                    dominios_recuperacion=["legal", "impositivo"],
                    origen_recuperacion="ambos",
                )
            ]
        )

        self.assertEqual(filas[0]["silo"], "contable")
        self.assertEqual(
            filas[0]["dominios_recuperacion"],
            ["legal", "impositivo"],
        )
        self.assertEqual(filas[0]["origen_recuperacion"], "ambos")

    def test_rechaza_evidencia_sin_chunk_uid(self) -> None:
        with self.assertRaises(ErrorDeLedger) as contexto:
            construir_evidencia([resultado("", 0.9)])

        self.assertIn("chunk_uid", str(contexto.exception))

    def test_sin_evidencia_no_falla(self) -> None:
        self.assertEqual(construir_evidencia([]), [])


class PersistenciaTestCase(unittest.TestCase):
    """The INSERT carries the values in the declared order.

    [ES] El INSERT lleva los valores en el orden declarado.
    """

    def test_registra_la_corrida(self) -> None:
        cursor = CursorFalso()
        registrar_corrida(cursor, construir_corrida(**CORRIDA))

        sql, params = cursor.ejecutadas[0]

        self.assertIn("INSERT INTO ledger_corrida", sql)
        self.assertEqual(sql.count("%s"), len(params))
        self.assertIn("corrida-2026-08-23-piloto", params)

    def test_registra_consulta_y_su_evidencia(self) -> None:
        cursor = CursorFalso(id_devuelto=42)

        consulta = construir_consulta(
            corrida_id="c1",
            pregunta="¿Qué dice?",
            brazo="B1",
            router_scores={"legal": 0.7},
        )
        evidencia = construir_evidencia(
            [resultado("a" * 64, 0.9), resultado("b" * 64, 0.8)]
        )

        consulta_id = registrar_consulta(cursor, consulta, evidencia)

        self.assertEqual(consulta_id, 42)
        self.assertEqual(len(cursor.ejecutadas), 3)

        sql_consulta, _ = cursor.ejecutadas[0]

        self.assertIn("INSERT INTO ledger_consulta", sql_consulta)
        self.assertIn("RETURNING id", sql_consulta)

        for sql_evidencia, params in cursor.ejecutadas[1:]:
            self.assertIn("INSERT INTO ledger_evidencia", sql_evidencia)
            self.assertIn(42, params)
            self.assertEqual(sql_evidencia.count("%s"), len(params))

    def test_serializa_los_campos_json(self) -> None:
        cursor = CursorFalso()

        consulta = construir_consulta(
            corrida_id="c1",
            pregunta="¿Qué dice?",
            brazo="B0",
            router_scores={"legal": 0.7},
            veto_spans=[{"start": 1, "end": 5}],
        )

        registrar_consulta(cursor, consulta, [])

        sql, params = cursor.ejecutadas[0]

        self.assertIn("%s::jsonb", sql)

        serializados = [p for p in params if isinstance(p, str) and p.startswith(("{", "["))]

        self.assertEqual(len(serializados), 2)
        self.assertEqual(
            json.loads(serializados[0]),
            {"legal": 0.7},
        )

    def test_los_campos_json_nulos_no_se_serializan(self) -> None:
        cursor = CursorFalso()

        consulta = construir_consulta(
            corrida_id="c1",
            pregunta="¿Qué dice?",
            brazo="B0",
        )

        registrar_consulta(cursor, consulta, [])

        _, params = cursor.ejecutadas[0]

        self.assertIn(None, params)


if __name__ == "__main__":
    unittest.main()
