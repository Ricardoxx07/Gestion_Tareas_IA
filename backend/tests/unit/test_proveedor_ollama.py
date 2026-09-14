import json
from datetime import date

import httpx
import pytest

from ai.proveedor_ollama import ProveedorOllama
from exceptions.planificacion_exceptions import (
    ProveedorIAError,
    RecomendacionIAInvalidaError,
)
from models.bloque_temporal import BloqueTemporal
from models.tarea import Tarea
from models.sobrecarga import CargaDiaria
from models.reprogramacion import CargaReprogramable, DiaDisponible


def crear_proveedor(handler) -> tuple[ProveedorOllama, httpx.Client]:
    cliente = httpx.Client(transport=httpx.MockTransport(handler))
    proveedor = ProveedorOllama(
        model="llama3.2:3b",
        url_base="http://localhost:11434/",
        timeout_seconds=10,
        max_tokens=400,
        cliente=cliente,
    )
    return proveedor, cliente


def bloque_prueba(
    identificador: int = 1,
    fecha: date | None = date(2026, 9, 6),
) -> BloqueTemporal:
    return BloqueTemporal(
        id=identificador,
        texto="Mañana debo preparar informe",
        fecha=fecha,
    )


def test_envia_contexto_y_convierte_respuesta_estructurada():
    solicitud_recibida = None

    def handler(solicitud: httpx.Request) -> httpx.Response:
        nonlocal solicitud_recibida
        solicitud_recibida = solicitud
        return httpx.Response(
            200,
            json={
                "message": {
                    "content": json.dumps(
                        {
                            "recomendaciones": [
                                {
                                    "tarea_id": 7,
                                    "orden": 1,
                                    "motivo": "Vence hoy.",
                                }
                            ],
                            "resumen": "Prioriza la tarea urgente.",
                        }
                    )
                }
            },
        )

    proveedor, cliente = crear_proveedor(handler)
    try:
        resultado = proveedor.recomendar_tareas(
            [
                Tarea(
                    id=7,
                    nombre="Enviar informe",
                    fecha_limite=date(2026, 9, 5),
                    prioridad="alta",
                )
            ],
            hoy=date(2026, 9, 5),
        )
    finally:
        cliente.close()

    assert resultado.recomendaciones[0].tarea_id == 7
    assert solicitud_recibida is not None
    assert str(solicitud_recibida.url) == "http://localhost:11434/api/chat"
    cuerpo = json.loads(solicitud_recibida.content)
    assert cuerpo["model"] == "llama3.2:3b"
    assert cuerpo["stream"] is False
    assert cuerpo["options"] == {"temperature": 0, "num_predict": 400}
    assert "format" in cuerpo
    assert "Enviar informe" in cuerpo["messages"][1]["content"]


def test_planifica_dia_con_tareas_reales_y_respuesta_estructurada():
    solicitud_recibida = None

    def handler(solicitud: httpx.Request) -> httpx.Response:
        nonlocal solicitud_recibida
        solicitud_recibida = solicitud
        return httpx.Response(
            200,
            json={
                "message": {
                    "content": json.dumps(
                        {
                            "plan": [
                                {
                                    "tarea_id": 7,
                                    "orden": 1,
                                    "motivo": "Vence en la fecha planificada.",
                                }
                            ],
                            "resumen": "Prioriza la tarea con vencimiento cercano.",
                        }
                    )
                }
            },
        )

    proveedor, cliente = crear_proveedor(handler)
    try:
        resultado = proveedor.planificar_dia(
            [
                Tarea(
                    id=7,
                    nombre="Enviar informe",
                    fecha_limite=date(2026, 9, 5),
                    prioridad="alta",
                )
            ],
            fecha=date(2026, 9, 5),
        )
    finally:
        cliente.close()

    assert resultado.plan[0].tarea_id == 7
    assert solicitud_recibida is not None
    cuerpo = json.loads(solicitud_recibida.content)
    assert "plan" in cuerpo["format"]["properties"]
    assert "2026-09-05" in cuerpo["messages"][1]["content"]
    assert "Enviar informe" in cuerpo["messages"][1]["content"]
    assert '"estado_fecha": "vence_hoy"' in cuerpo["messages"][1]["content"]
    assert "No inventes, crees, modifiques ni completes tareas" in cuerpo["messages"][0]["content"]
    assert "todavía no está vencida" in cuerpo["messages"][0]["content"]


def test_explica_sobrecargas_calculadas_por_el_backend():
    solicitud_recibida = None

    def handler(solicitud: httpx.Request) -> httpx.Response:
        nonlocal solicitud_recibida
        solicitud_recibida = solicitud
        return httpx.Response(
            200,
            json={
                "message": {
                    "content": json.dumps(
                        {
                            "alertas": [
                                {
                                    "fecha": "2026-09-07",
                                    "mensaje": "Hay varias tareas concentradas.",
                                    "sugerencia": "Prioriza las más urgentes.",
                                }
                            ]
                        }
                    )
                }
            },
        )

    proveedor, cliente = crear_proveedor(handler)
    try:
        resultado = proveedor.explicar_sobrecargas(
            [
                CargaDiaria(
                    fecha=date(2026, 9, 7),
                    tareas=[
                        Tarea(id=7, nombre="Enviar informe", prioridad="alta"),
                        Tarea(id=8, nombre="Preparar reunión", prioridad="media"),
                    ],
                )
            ]
        )
    finally:
        cliente.close()

    assert resultado[0].fecha == date(2026, 9, 7)
    assert solicitud_recibida is not None
    cuerpo = json.loads(solicitud_recibida.content)
    assert "alertas" in cuerpo["format"]["properties"]
    assert "Enviar informe" in cuerpo["messages"][1]["content"]
    assert "exactamente una alerta por cada fecha recibida" in cuerpo["messages"][0]["content"]
    assert "Solo puedes llamar vencida" in cuerpo["messages"][0]["content"]


def test_propone_reprogramaciones_solo_con_tareas_y_fechas_del_contexto():
    solicitud_recibida = None

    def handler(solicitud: httpx.Request) -> httpx.Response:
        nonlocal solicitud_recibida
        solicitud_recibida = solicitud
        return httpx.Response(
            200,
            json={
                "message": {
                    "content": json.dumps(
                        {
                            "propuestas": [
                                {
                                    "tarea_id": 7,
                                    "motivo": "Tiene menor prioridad en el día sobrecargado.",
                                }
                            ]
                        }
                    )
                }
            },
        )

    proveedor, cliente = crear_proveedor(handler)
    try:
        resultado = proveedor.proponer_reprogramaciones(
            [
                CargaReprogramable(
                    fecha=date(2026, 9, 8),
                    max_reprogramaciones=1,
                    tareas=[Tarea(id=7, nombre="Comprar materiales", prioridad="baja")],
                )
            ],
            [DiaDisponible(fecha=date(2026, 9, 9), cupos_disponibles=2)],
        )
    finally:
        cliente.close()

    assert resultado[0].tarea_id == 7
    assert solicitud_recibida is not None
    cuerpo = json.loads(solicitud_recibida.content)
    assert "propuestas" in cuerpo["format"]["properties"]
    assert "Comprar materiales" in cuerpo["messages"][1]["content"]
    assert "No devuelvas fechas" in cuerpo["messages"][0]["content"]


def test_reprogramacion_descarta_fechas_que_ollama_no_debe_decidir():
    proveedor, cliente = crear_proveedor(
        lambda solicitud: httpx.Response(
            200,
            json={
                "message": {
                    "content": json.dumps(
                        {
                            "propuestas": [
                                {
                                    "tarea_id": 7,
                                    "motivo": "Tiene menor prioridad en el día sobrecargado.",
                                    "fecha_actual": "2026-09-08",
                                    "fecha_sugerida": "2026-09-10",
                                }
                            ]
                        }
                    )
                }
            },
        )
    )
    try:
        resultado = proveedor.proponer_reprogramaciones(
            [
                CargaReprogramable(
                    fecha=date(2026, 9, 8),
                    max_reprogramaciones=1,
                    tareas=[Tarea(id=7, nombre="Comprar materiales", prioridad="baja")],
                )
            ],
            [DiaDisponible(fecha=date(2026, 9, 9), cupos_disponibles=2)],
        )
    finally:
        cliente.close()

    assert len(resultado) == 1
    assert resultado[0].tarea_id == 7
    assert resultado[0].motivo == "Tiene menor prioridad en el día sobrecargado."


@pytest.mark.parametrize(
    "respuesta_ollama",
    [
        {"message": {"content": "no es JSON"}},
        {"message": {"content": '{"recomendaciones": [], "dato_extra": true}'}},
    ],
)
def test_rechaza_una_respuesta_de_ollama_no_estructurada(respuesta_ollama):
    proveedor, cliente = crear_proveedor(
        lambda solicitud: httpx.Response(200, json=respuesta_ollama)
    )
    try:
        with pytest.raises(RecomendacionIAInvalidaError):
            proveedor.recomendar_tareas([], hoy=date(2026, 9, 5))
    finally:
        cliente.close()


@pytest.mark.parametrize(
    "handler",
    [
        lambda solicitud: httpx.Response(500, json={"error": "modelo no disponible"}),
        lambda solicitud: (_ for _ in ()).throw(httpx.ConnectError("sin conexión")),
        lambda solicitud: (_ for _ in ()).throw(httpx.ReadTimeout("tiempo agotado")),
    ],
)
def test_traduce_errores_de_conexion_o_http_a_error_de_proveedor(handler):
    proveedor, cliente = crear_proveedor(handler)
    try:
        with pytest.raises(ProveedorIAError):
            proveedor.recomendar_tareas([], hoy=date(2026, 9, 5))
    finally:
        cliente.close()


def test_interpreta_texto_y_devuelve_propuestas_estructuradas():
    solicitud_recibida = None

    def handler(solicitud: httpx.Request) -> httpx.Response:
        nonlocal solicitud_recibida
        solicitud_recibida = solicitud
        return httpx.Response(
            200,
            json={
                "message": {
                    "content": json.dumps(
                        {
                            "tareas_propuestas": [
                                {
                                    "nombre": "Preparar informe",
                                    "prioridad_sugerida": "alta",
                                    "motivo": "Se indicó que es para mañana.",
                                    "bloque_temporal_id": 1,
                                    "orden_prioridad_usuario": None,
                                }
                            ]
                        }
                    )
                }
            },
        )

    proveedor, cliente = crear_proveedor(handler)
    try:
        resultado = proveedor.proponer_tareas(
            "Mañana debo preparar informe",
            hoy=date(2026, 9, 5),
            bloques_temporales=[bloque_prueba()],
        )
    finally:
        cliente.close()

    assert resultado.tareas_propuestas[0].fecha_sugerida == date(2026, 9, 6)
    assert solicitud_recibida is not None
    cuerpo = json.loads(solicitud_recibida.content)
    assert "tareas_propuestas" in cuerpo["format"]["properties"]
    assert "2026-09-05" in cuerpo["messages"][1]["content"]
    assert "Día actual: sábado" in cuerpo["messages"][1]["content"]
    assert '"fecha_calculada": "2026-09-06"' in cuerpo["messages"][1]["content"]
    assert "Mañana debo preparar informe" in cuerpo["messages"][1]["content"]
    assert "esa preferencia tiene precedencia" in cuerpo["messages"][0]["content"]


def test_admite_una_lista_vacia_de_propuestas():
    proveedor, cliente = crear_proveedor(
        lambda solicitud: httpx.Response(
            200,
            json={"message": {"content": '{"tareas_propuestas": []}'}},
        )
    )
    try:
        resultado = proveedor.proponer_tareas(
            "No tengo nada pendiente",
            date(2026, 9, 5),
            [],
        )
    finally:
        cliente.close()

    assert resultado.tareas_propuestas == []


def test_rechaza_una_propuesta_con_prioridad_fuera_del_contrato():
    proveedor, cliente = crear_proveedor(
        lambda solicitud: httpx.Response(
            200,
            json={
                "message": {
                    "content": (
                        '{"tareas_propuestas": [{"nombre": "Tarea", '
                        '"prioridad_sugerida": "urgente", '
                        '"motivo": "Motivo", "bloque_temporal_id": 1, '
                        '"orden_prioridad_usuario": null}]}'
                    )
                }
            },
        )
    )
    try:
        with pytest.raises(RecomendacionIAInvalidaError):
            proveedor.proponer_tareas(
                "Una tarea",
                date(2026, 9, 5),
                [bloque_prueba()],
            )
    finally:
        cliente.close()


def test_rechaza_una_propuesta_sin_metadatos_para_correccion_del_backend():
    proveedor, cliente = crear_proveedor(
        lambda solicitud: httpx.Response(
            200,
            json={
                "message": {
                    "content": (
                        '{"tareas_propuestas": [{"nombre": "Ir al gym", '
                        '"prioridad_sugerida": "alta", "motivo": "Motivo"}]}'
                    )
                }
            },
        )
    )
    try:
        with pytest.raises(RecomendacionIAInvalidaError):
            proveedor.proponer_tareas(
                "El lunes ir al gym",
                date(2026, 9, 5),
                [bloque_prueba(fecha=date(2026, 9, 7))],
            )
    finally:
        cliente.close()


def test_rechaza_un_motivo_que_repite_el_nombre_de_la_tarea():
    proveedor, cliente = crear_proveedor(
        lambda solicitud: httpx.Response(
            200,
            json={
                "message": {
                    "content": (
                        '{"tareas_propuestas": [{"nombre": "Ir al gimnasio", '
                        '"prioridad_sugerida": "baja", '
                        '"motivo": "Ir al gimnasio", "bloque_temporal_id": 1, '
                        '"orden_prioridad_usuario": null}]}'
                    )
                }
            },
        )
    )
    try:
        with pytest.raises(RecomendacionIAInvalidaError):
            proveedor.proponer_tareas(
                "El lunes ir al gimnasio",
                date(2026, 9, 5),
                [bloque_prueba(fecha=date(2026, 9, 7))],
            )
    finally:
        cliente.close()


def test_corrige_fechas_relativas_y_respeta_orden_explicito_del_usuario():
    respuesta_ollama = {
        "tareas_propuestas": [
            {
                "nombre": "Visitar a mamá",
                "prioridad_sugerida": "media",
                "motivo": "El usuario la indicó como máxima prioridad.",
                "bloque_temporal_id": 2,
                "orden_prioridad_usuario": 1,
            },
            {
                "nombre": "Comprar mercadería",
                "prioridad_sugerida": "media",
                "motivo": "Se indicó para el siguiente día.",
                "bloque_temporal_id": 2,
                "orden_prioridad_usuario": None,
            },
            {
                "nombre": "Ir al gym",
                "prioridad_sugerida": "alta",
                "motivo": "Es importante para la salud.",
                "bloque_temporal_id": 1,
                "orden_prioridad_usuario": 3,
            },
            {
                "nombre": "Reunión con trabajadores del negocio",
                "prioridad_sugerida": "alta",
                "motivo": "El usuario mencionó su negocio.",
                "bloque_temporal_id": 1,
                "orden_prioridad_usuario": 2,
            },
        ]
    }
    proveedor, cliente = crear_proveedor(
        lambda solicitud: httpx.Response(
            200,
            json={"message": {"content": json.dumps(respuesta_ollama)}},
        )
    )
    try:
        resultado = proveedor.proponer_tareas(
            "El lunes gym y negocio; el siguiente día mercadería y mamá.",
            hoy=date(2026, 9, 5),
            bloques_temporales=[
                BloqueTemporal(1, "El lunes gym y negocio", date(2026, 9, 7)),
                BloqueTemporal(2, "El siguiente día mercadería y mamá", date(2026, 9, 8)),
            ],
        )
    finally:
        cliente.close()

    propuestas_por_nombre = {
        propuesta.nombre: propuesta
        for propuesta in resultado.tareas_propuestas
    }
    assert propuestas_por_nombre["Ir al gym"].fecha_sugerida == date(2026, 9, 7)
    assert propuestas_por_nombre["Reunión con trabajadores del negocio"].fecha_sugerida == date(2026, 9, 7)
    assert propuestas_por_nombre["Comprar mercadería"].fecha_sugerida == date(2026, 9, 8)
    assert propuestas_por_nombre["Visitar a mamá"].fecha_sugerida == date(2026, 9, 8)
    assert propuestas_por_nombre["Visitar a mamá"].prioridad_sugerida == "alta"
    assert propuestas_por_nombre["Reunión con trabajadores del negocio"].prioridad_sugerida == "media"
    assert propuestas_por_nombre["Ir al gym"].prioridad_sugerida == "baja"


def test_descompone_tarea_y_valida_respuesta_estructurada():
    solicitud_recibida = None

    def handler(solicitud: httpx.Request) -> httpx.Response:
        nonlocal solicitud_recibida
        solicitud_recibida = solicitud
        return httpx.Response(
            200,
            json={
                "message": {
                    "content": json.dumps(
                        {
                            "subtareas": [
                                {
                                    "orden": 1,
                                    "nombre": "Definir alcance",
                                    "motivo": "Aclara el resultado que se espera conseguir.",
                                },
                                {
                                    "orden": 2,
                                    "nombre": "Implementar solución",
                                    "motivo": "Convierte el alcance en acciones concretas.",
                                },
                            ]
                        }
                    )
                }
            },
        )

    proveedor, cliente = crear_proveedor(handler)
    try:
        resultado = proveedor.descomponer_tarea("Construir integración con IA")
    finally:
        cliente.close()

    assert resultado.tarea_original == "Construir integración con IA"
    assert [subtarea.nombre for subtarea in resultado.subtareas] == [
        "Definir alcance",
        "Implementar solución",
    ]
    assert solicitud_recibida is not None
    cuerpo = json.loads(solicitud_recibida.content)
    assert "subtareas" in cuerpo["format"]["properties"]
    assert "entre 2 y 8 subtareas" in cuerpo["messages"][0]["content"]


def test_rechaza_descomposicion_con_orden_no_consecutivo():
    proveedor, cliente = crear_proveedor(
        lambda solicitud: httpx.Response(
            200,
            json={
                "message": {
                    "content": json.dumps(
                        {
                            "subtareas": [
                                {
                                    "orden": 1,
                                    "nombre": "Definir alcance",
                                    "motivo": "Aclara el resultado que se espera conseguir.",
                                },
                                {
                                    "orden": 3,
                                    "nombre": "Implementar solución",
                                    "motivo": "Convierte el alcance en acciones concretas.",
                                },
                            ]
                        }
                    )
                }
            },
        )
    )
    try:
        with pytest.raises(RecomendacionIAInvalidaError):
            proveedor.descomponer_tarea("Construir integración con IA")
    finally:
        cliente.close()
