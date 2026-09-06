from datetime import date

import pytest
from fastapi.testclient import TestClient

from api.dependencies import obtener_reprogramacion_service, obtener_usuario_actual
from api.main import app
from models.reprogramacion import (
    PropuestaReprogramacion,
    PropuestasReprogramacion,
)
from models.usuario import Usuario


class ReprogramacionServiceFalso:
    def __init__(self):
        self.argumentos_recibidos = None

    def proponer_reprogramaciones(
        self,
        usuario_id: int,
        fecha_inicio: date | None,
        dias: int,
        max_tareas_por_dia: int,
    ) -> PropuestasReprogramacion:
        self.argumentos_recibidos = (
            usuario_id,
            fecha_inicio,
            dias,
            max_tareas_por_dia,
        )
        return PropuestasReprogramacion(
            fecha_inicio=fecha_inicio or date(2026, 9, 5),
            fecha_fin=date(2026, 9, 11),
            max_tareas_por_dia=max_tareas_por_dia,
            propuestas=[
                PropuestaReprogramacion(
                    tarea_id=10,
                    fecha_actual=date(2026, 9, 8),
                    fecha_sugerida=date(2026, 9, 6),
                    motivo="Tiene menor prioridad relativa ese día.",
                )
            ],
        )


@pytest.fixture
def client():
    usuario = Usuario(id=1, email="ricardo@example.com", password_hash="hash")
    service = ReprogramacionServiceFalso()
    app.dependency_overrides[obtener_usuario_actual] = lambda: usuario
    app.dependency_overrides[obtener_reprogramacion_service] = lambda: service

    yield TestClient(app), service

    app.dependency_overrides.clear()


def test_proponer_reprogramacion_devuelve_solo_una_propuesta(client):
    test_client, service = client

    response = test_client.post(
        "/ia/proponer-reprogramacion",
        json={
            "fecha_inicio": "2026-09-05",
            "dias": 7,
            "max_tareas_por_dia": 3,
        },
    )

    assert response.status_code == 200
    assert response.json()["propuestas"] == [
        {
            "tarea_id": 10,
            "fecha_sugerida": "2026-09-06",
            "motivo": "Tiene menor prioridad relativa ese día.",
            "fecha_actual": "2026-09-08",
        }
    ]
    assert service.argumentos_recibidos == (1, date(2026, 9, 5), 7, 3)
