"""Validate metadata and its governing configuration.

[ES] Valida los metadatos y la configuración que los gobierna.
"""

import json
import re
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path


RUTA_CONFIGURACION_CATALOGO = Path(__file__).with_name(
    "catalogo_vocabularios.json"
)

CLAVES_RAIZ_CONFIGURACION = (
    "schema_version",
    "taxonomia_version",
    "separador_multivalor",
    "alcance_experimental",
    "politica_clasificacion",
    "patrones_identidad",
    "formatos_fecha_permitidos",
    "campos_multivalor",
    "tipos_documento_por_familia",
    "vocabularios",
    "campos_objetivos_requeridos",
    "campos_propuesta_automatica",
    "campos_canonicos_requeridos_si_incluido",
    "reglas_condicionales",
)


def cargar_configuracion_catalogo(
        ruta_configuracion: Path
) -> dict[str, object]:
    """Load the catalog configuration from a JSON file.

    [ES] Carga la configuración del catálogo desde un archivo JSON.
    """
    ruta_resuelta = ruta_configuracion.resolve()

    if not ruta_resuelta.is_file():
        raise FileNotFoundError(
            f"No existe la configuración: {ruta_resuelta}"
        )

    try:
        with ruta_resuelta.open(
                "r",
                encoding="utf-8-sig"
        ) as archivo:
            configuracion = json.load(archivo)
    except json.JSONDecodeError as error:
        raise ValueError(
            "La configuración contiene JSON inválido "
            f"en la línea {error.lineno}."
        ) from error

    if not isinstance(configuracion, dict):
        raise ValueError(
            "La raíz de la configuración debe ser un objeto JSON."
        )

    return configuracion


def _obtener_objeto_configuracion(
        configuracion: dict[str, object],
        clave: str
) -> dict[str, object]:
    """Return a required nested configuration object.

    [ES] Devuelve un objeto interno obligatorio de la configuración.
    """
    valor = configuracion.get(clave)

    if not isinstance(valor, dict):
        raise ValueError(
            f"La clave {clave} debe contener un objeto JSON."
        )

    return valor


def _validar_lista_textos_unicos(
        valor: object,
        nombre: str
) -> list[str]:
    """Validate a non-empty list of unique text values.

    [ES] Valida una lista no vacía de textos únicos.
    """
    if not isinstance(valor, list) or not valor:
        raise ValueError(
            f"{nombre} debe ser una lista no vacía."
        )

    valores_texto: list[str] = []

    for elemento in valor:
        if not isinstance(elemento, str) or not elemento.strip():
            raise ValueError(
                f"{nombre} solo puede contener textos no vacíos."
            )

        valores_texto.append(elemento)

    if len(valores_texto) != len(set(valores_texto)):
        raise ValueError(
            f"{nombre} contiene valores duplicados."
        )

    return valores_texto


def validar_estructura_configuracion(
        configuracion: dict[str, object]
) -> None:
    """Validate the internal structure of the catalog configuration.

    [ES] Valida la estructura interna de la configuración del catálogo.
    """

    for clave in CLAVES_RAIZ_CONFIGURACION:
        if clave not in configuracion:
            raise ValueError(
                f"Falta la clave obligatoria: {clave}."
            )

    alcance = _obtener_objeto_configuracion(
        configuracion,
        "alcance_experimental",
    )
    vocabularios = _obtener_objeto_configuracion(
        configuracion,
        "vocabularios",
    )

    silos = _validar_lista_textos_unicos(
        alcance.get("silos_evaluados_en_la_tesis"),
        "silos_evaluados_en_la_tesis",
    )

    for nombre_vocabulario, valores in vocabularios.items():
        _validar_lista_textos_unicos(
            valores,
            nombre_vocabulario,
        )

    dominios = _validar_lista_textos_unicos(
            vocabularios.get("dominios_documentales"),
            "dominios_documentales",
        )

    conjunto_dominios = set(dominios)

    for silo in silos:
        if silo not in conjunto_dominios:
            raise ValueError(
                f"El silo experimental {silo} no está registrado "
                "en dominios_documentales."
            )

def validar_registro_metadatos(
        registro: Mapping[str, object],
        configuracion: dict[str, object]
) -> dict[str, list[str]]:
    """Validate required metadata field acording to record status.

    [ES] Valida los metadatos obligatorios según el estado del registro.
    """

    errores: list[str] = []
    advertencias: list[str] = []

    campos_objetivos = _validar_lista_textos_unicos(
        configuracion.get("campos_objetivos_requeridos"),
        "campos_objetivos_requeridos",
    )

    campos_canonicos = _validar_lista_textos_unicos(
        configuracion.get(
            "campos_canonicos_requeridos_si_incluido"
        ),
        "campos_canonicos_requeridos_si_incluido",
    )
    reglas = _obtener_objeto_configuracion(
        configuracion,
        "reglas_condicionales",
    )

    for campo in campos_objetivos:
        valor = registro.get(campo)

        if not isinstance(valor, str) or not valor.strip():
            errores.append(
                f"El campo objetivo {campo} es obligatorio."
            )

    estado = registro.get("estado_inclusion")

    if not isinstance(estado, str) or not estado.strip():
        advertencias.append(
            "El campo estado_inclusion está pendiente."
        )
        estado = ""
    else:
        estado = estado.strip()

    if estado == "incluido":
        for campo in campos_canonicos:
            valor = registro.get(campo)

            if not isinstance(valor, str) or not valor.strip():
                errores.append(
                    f"El campo canónico {campo} es obligatorio "
                    "para un documento incluido."
                )

    estado_que_requiere_motivo = reglas.get(
        "motivo_exclusion_requerido_si_estado"
    )

    if estado == estado_que_requiere_motivo:
        motivo = registro.get("motivo_exclusion")

        if not isinstance(motivo, str) or not motivo.strip():
            errores.append(
                "El campo motivo_exclusion es obligatorio "
                "para un documento excluido."
            )

    patrones_identidad = _obtener_objeto_configuracion(
        configuracion,
        "patrones_identidad",
    )

    for campo, patron in patrones_identidad.items():
        if not isinstance(patron, str):
            raise ValueError(
                f"El patrón de {campo} debe ser texto."
            )

        valor = registro.get(campo)

        if (
            isinstance(valor, str)
            and valor.strip()
            and re.fullmatch(patron, valor.strip()) is None
        ):
            errores.append(
                f"El campo {campo} no respeta su formato."
            )

    valor_fecha = registro.get("fecha_documento")

    if isinstance(valor_fecha, str) and valor_fecha.strip():
        formatos_fecha = _validar_lista_textos_unicos(
            configuracion.get("formatos_fecha_permitidos"),
            "formatos_fecha_permitidos",
        )
        especificaciones_fecha: dict[
            str,
            tuple[str, str],
        ] = {
            "AAAA": (
                r"[0-9]{4}",
                "%Y",
            ),
            "AAAA-MM": (
                r"[0-9]{4}-[0-9]{2}",
                "%Y-%m",
            ),
            "AAAA-MM-DD": (
                r"[0-9]{4}-[0-9]{2}-[0-9]{2}",
                "%Y-%m-%d",
            ),
        }
        fecha_valida = False

        for formato_fecha in formatos_fecha:
            especificacion = especificaciones_fecha.get(
                formato_fecha
            )

            if especificacion is None:
                raise ValueError(
                    "Formato de fecha no implementado: "
                    f"{formato_fecha}."
                )

            patron_fecha, formato_python = especificacion

            if re.fullmatch(
                    patron_fecha,
                    valor_fecha.strip()
            ) is None:
                continue

            try:
                datetime.strptime(
                    valor_fecha.strip(),
                    formato_python,
                )
            except ValueError:
                continue

            fecha_valida = True
            break

        if not fecha_valida:
            errores.append(
                "El campo fecha_documento no contiene "
                "una fecha válida."
            )

    separador = configuracion.get("separador_multivalor")

    if not isinstance(separador, str) or not separador:
        raise ValueError(
            "separador_multivalor debe ser texto no vacío."
        )

    campos_multivalor = _validar_lista_textos_unicos(
        configuracion.get("campos_multivalor"),
        "campos_multivalor",
    )
    valores_multivalor: dict[str, list[str]] = {}

    for campo in campos_multivalor:
        valor = registro.get(campo)

        if not isinstance(valor, str) or not valor.strip():
            continue

        valores = [
            elemento.strip()
            for elemento in valor.split(separador)
        ]

        if any(not elemento for elemento in valores):
            errores.append(
                f"El campo {campo} contiene un valor vacío."
            )
            continue

        if len(valores) != len(set(valores)):
            errores.append(
                f"El campo {campo} contiene un valor duplicado."
            )

        valores_multivalor[campo] = valores

    vocabularios = _obtener_objeto_configuracion(
        configuracion,
        "vocabularios",
    )

    for campo, valores_permitidos in vocabularios.items():
        if campo not in registro:
            continue

        permitidos = set(
            _validar_lista_textos_unicos(
                valores_permitidos,
                campo,
            )
        )
        valor = registro.get(campo)

        if not isinstance(valor, str) or not valor.strip():
            continue

        valores_registro = valores_multivalor.get(
            campo,
            [valor.strip()],
        )

        for valor_registro in valores_registro:
            if valor_registro in permitidos:
                continue

            mensaje = (
                f"El valor {valor_registro} de {campo} "
                "no está registrado en el vocabulario."
            )

            if estado == "incluido":
                errores.append(mensaje)
            else:
                advertencias.append(mensaje)

    familias_documentales = _obtener_objeto_configuracion(
        configuracion,
        "tipos_documento_por_familia",
    )
    tipos_documento: set[str] = set()

    for familia, tipos in familias_documentales.items():
        tipos_documento.update(
            _validar_lista_textos_unicos(
                tipos,
                familia,
            )
        )

    tipo_documento = registro.get("tipo_documento")

    if (
        isinstance(tipo_documento, str)
        and tipo_documento.strip()
        and tipo_documento not in tipos_documento
    ):
        mensaje = (
            f"El tipo_documento {tipo_documento} "
            "no está registrado."
        )

        if estado == "incluido":
            errores.append(mensaje)
        else:
            advertencias.append(mensaje)


    return {
        "errores": errores,
        "advertencias": advertencias,
    }
