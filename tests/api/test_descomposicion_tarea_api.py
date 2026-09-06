import pytest
from fastapi.testclient import TestClient

from api.dependencies import (
    obtener_descomposicion_tarea_service,
    obtener_usuario_actual,
)
from api.main import app
from models.descomposicion_tarea import DescomposicionTarea, Subtarea
from models.usuario import Usuario


class DescomposicionTareaServiceFalso:
    def __init__(self):
        self.texto_recibido: str | None = None

    def descomponer_tarea(self, texto: str) -> DescomposicionTarea:
        self.texto_recibido = texto
        return DescomposicionTarea(
            tarea_original=texto,
            subtareas=[
                Subtarea(1, "Definir requisitos", "Aclara el alcance del resultado esperado."),
                Subtarea(2, "Implementar solución", "Permite convertir el alcance en trabajo."),
            ],
        )


@pytest.fixture
def client():
    service = DescomposicionTareaServiceFalso()
    app.dependency_overrides[obtener_usuario_actual] = lambda: Usuario(
        id=1,
        email="ricardo@example.com",
        password_hash="hash-interno",
    )
    app.dependency_overrides[obtener_descomposicion_tarea_service] = lambda: service

    yield TestClient(app), service

    app.dependency_overrides.clear()


def test_descomponer_devuelve_subtareas_sin_persistir(client):
    test_client, service = client

    response = test_client.post(
        "/ia/descomponer",
        json={"texto": "Construir integración con IA"},
    )

    assert response.status_code == 200
    assert response.json()["tarea_original"] == "Construir integración con IA"
    assert response.json()["subtareas"][0]["orden"] == 1
    assert service.texto_recibido == "Construir integración con IA"


@pytest.mark.parametrize("texto", ["", "   "])
def test_descomponer_rechaza_texto_vacio(client, texto):
    test_client, _ = client

    response = test_client.post("/ia/descomponer", json={"texto": texto})

    assert response.status_code == 422
