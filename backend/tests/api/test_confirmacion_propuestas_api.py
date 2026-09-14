import pytest
from fastapi.testclient import TestClient

from api.dependencies import (
    obtener_confirmacion_propuestas_service,
    obtener_usuario_actual,
)
from api.main import app
from models.tarea import Tarea
from models.usuario import Usuario


class ConfirmacionPropuestasServiceFalso:
    def __init__(self):
        self.tareas_recibidas: list[Tarea] | None = None
        self.usuario_id_recibido: int | None = None

    def confirmar_propuestas(self, tareas: list[Tarea], usuario_id: int) -> list[Tarea]:
        self.tareas_recibidas = tareas
        self.usuario_id_recibido = usuario_id
        for indice, tarea in enumerate(tareas, start=50):
            tarea.id = indice
            tarea.usuario_id = usuario_id
        return tareas


@pytest.fixture
def client():
    service = ConfirmacionPropuestasServiceFalso()
    app.dependency_overrides[obtener_usuario_actual] = lambda: Usuario(
        id=1,
        email="ricardo@example.com",
        password_hash="hash-interno",
    )
    app.dependency_overrides[obtener_confirmacion_propuestas_service] = lambda: service

    yield TestClient(app), service

    app.dependency_overrides.clear()


def test_confirma_propuestas_seleccionadas(client):
    test_client, service = client

    response = test_client.post(
        "/ia/propuestas/confirmar",
        json={
            "tareas": [
                {"nombre": "Preparar informe", "prioridad": "alta"},
                {"nombre": "Enviar correo", "prioridad": "media"},
            ]
        },
    )

    assert response.status_code == 201
    assert [tarea["id"] for tarea in response.json()["tareas_confirmadas"]] == [50, 51]
    assert service.usuario_id_recibido == 1
    assert [tarea.nombre for tarea in service.tareas_recibidas] == [
        "Preparar informe",
        "Enviar correo",
    ]


def test_confirma_subtareas_con_el_padre_elegido(client):
    test_client, service = client

    response = test_client.post(
        "/ia/propuestas/confirmar",
        json={
            "tareas": [
                {
                    "nombre": "Definir estructura",
                    "tarea_padre_id": 22,
                }
            ]
        },
    )

    assert response.status_code == 201
    assert service.tareas_recibidas[0].tarea_padre_id == 22


@pytest.mark.parametrize("tareas", [[], [{"nombre": "   "}]])
def test_rechaza_confirmacion_sin_propuestas_validas(client, tareas):
    test_client, _ = client

    response = test_client.post("/ia/propuestas/confirmar", json={"tareas": tareas})

    assert response.status_code == 422
