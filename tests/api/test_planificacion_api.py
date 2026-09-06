import pytest
from fastapi.testclient import TestClient

from api.dependencies import obtener_planificacion_service, obtener_usuario_actual
from api.main import app
from exceptions.planificacion_exceptions import (
    ProveedorIAError,
    RecomendacionIAInvalidaError,
)
from models.planificacion import Planificacion, RecomendacionTarea
from models.usuario import Usuario


class PlanificacionServiceFalso:

    def __init__(self, respuesta: Planificacion | Exception):
        self.respuesta = respuesta
        self.usuario_id_recibido: int | None = None

    def recomendar_tareas(self, usuario_id: int) -> Planificacion:
        self.usuario_id_recibido = usuario_id

        if isinstance(self.respuesta, Exception):
            raise self.respuesta

        return self.respuesta


@pytest.fixture
def usuario_actual():
    return Usuario(
        id=1,
        email="ricardo@example.com",
        password_hash="hash-interno"
    )


@pytest.fixture
def client(usuario_actual):
    service = PlanificacionServiceFalso(
        Planificacion(
            recomendaciones=[
                RecomendacionTarea(
                    tarea_id=10,
                    orden=1,
                    motivo="Vence hoy y sigue pendiente."
                )
            ],
            resumen="Se priorizó 1 tarea pendiente."
        )
    )
    app.dependency_overrides[obtener_usuario_actual] = lambda: usuario_actual
    app.dependency_overrides[obtener_planificacion_service] = lambda: service

    yield TestClient(app), service

    app.dependency_overrides.clear()


def test_recomendar_tareas_devuelve_planificacion_del_usuario(client):
    test_client, service = client

    response = test_client.post("/ia/recomendar-tareas")

    assert response.status_code == 200
    assert response.json() == {
        "recomendaciones": [
            {
                "tarea_id": 10,
                "orden": 1,
                "motivo": "Vence hoy y sigue pendiente."
            }
        ],
        "resumen": "Se priorizó 1 tarea pendiente."
    }
    assert service.usuario_id_recibido == 1


def test_recomendar_tareas_oculta_respuesta_invalida_del_proveedor(usuario_actual):
    service = PlanificacionServiceFalso(
        RecomendacionIAInvalidaError("ID interno no permitido")
    )
    app.dependency_overrides[obtener_usuario_actual] = lambda: usuario_actual
    app.dependency_overrides[obtener_planificacion_service] = lambda: service

    client = TestClient(app)
    response = client.post("/ia/recomendar-tareas")

    app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json() == {
        "detail": "La IA devolvió una respuesta inválida: ID interno no permitido"
    }


def test_recomendar_tareas_informa_proveedor_no_disponible(usuario_actual):
    service = PlanificacionServiceFalso(ProveedorIAError("Timeout interno"))
    app.dependency_overrides[obtener_usuario_actual] = lambda: usuario_actual
    app.dependency_overrides[obtener_planificacion_service] = lambda: service

    client = TestClient(app)
    response = client.post("/ia/recomendar-tareas")

    app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "detail": "No fue posible obtener una recomendación en este momento"
    }
