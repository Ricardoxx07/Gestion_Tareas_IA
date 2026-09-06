from datetime import date

import pytest
from fastapi.testclient import TestClient

from api.dependencies import (
    obtener_propuesta_tareas_service,
    obtener_usuario_actual,
)
from api.main import app
from models.propuesta_tareas import PropuestasTareas, TareaPropuesta
from models.usuario import Usuario


class PropuestaTareasServiceFalso:
    def __init__(self):
        self.texto_recibido: str | None = None

    def proponer_tareas(self, texto: str) -> PropuestasTareas:
        self.texto_recibido = texto
        return PropuestasTareas(
            tareas_propuestas=[
                TareaPropuesta(
                    nombre="Terminar informe para Carlos",
                    fecha_sugerida=date(2026, 9, 6),
                    prioridad_sugerida="alta",
                    motivo="El usuario indicó que debe realizarse mañana.",
                )
            ]
        )


@pytest.fixture
def client():
    service = PropuestaTareasServiceFalso()
    app.dependency_overrides[obtener_usuario_actual] = lambda: Usuario(
        id=1,
        email="ricardo@example.com",
        password_hash="hash-interno",
    )
    app.dependency_overrides[obtener_propuesta_tareas_service] = lambda: service

    yield TestClient(app), service

    app.dependency_overrides.clear()


def test_planificar_devuelve_propuestas_sin_crearlas(client):
    test_client, service = client

    response = test_client.post(
        "/ia/planificar",
        json={"texto": "Mañana tengo que terminar el informe para Carlos"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "tareas_propuestas": [
            {
                "nombre": "Terminar informe para Carlos",
                "fecha_sugerida": "2026-09-06",
                "prioridad_sugerida": "alta",
                "motivo": "El usuario indicó que debe realizarse mañana.",
            }
        ]
    }
    assert service.texto_recibido == "Mañana tengo que terminar el informe para Carlos"


@pytest.mark.parametrize("texto", ["", "   "])
def test_planificar_rechaza_texto_vacio(client, texto):
    test_client, _ = client

    response = test_client.post("/ia/planificar", json={"texto": texto})

    assert response.status_code == 422
