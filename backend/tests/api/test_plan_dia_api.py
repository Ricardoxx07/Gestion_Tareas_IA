from datetime import date

import pytest
from fastapi.testclient import TestClient

from api.dependencies import obtener_plan_dia_service, obtener_usuario_actual
from api.main import app
from models.plan_dia import PlanDia
from models.planificacion import RecomendacionTarea
from models.usuario import Usuario


class PlanDiaServiceFalso:
    def __init__(self):
        self.usuario_id_recibido: int | None = None
        self.fecha_recibida: date | None = None

    def planificar_dia(self, usuario_id: int, fecha: date | None) -> PlanDia:
        self.usuario_id_recibido = usuario_id
        self.fecha_recibida = fecha
        return PlanDia(
            fecha=fecha or date(2026, 9, 5),
            plan=[
                RecomendacionTarea(
                    tarea_id=10,
                    orden=1,
                    motivo="Vence en la fecha planificada.",
                )
            ],
            resumen="Se organizó 1 tarea relevante para el día.",
        )


@pytest.fixture
def client():
    usuario = Usuario(id=1, email="ricardo@example.com", password_hash="hash")
    service = PlanDiaServiceFalso()
    app.dependency_overrides[obtener_usuario_actual] = lambda: usuario
    app.dependency_overrides[obtener_plan_dia_service] = lambda: service

    yield TestClient(app), service

    app.dependency_overrides.clear()


def test_plan_dia_devuelve_plan_del_usuario_para_la_fecha_solicitada(client):
    test_client, service = client

    response = test_client.post("/ia/plan-dia", json={"fecha": "2026-09-07"})

    assert response.status_code == 200
    assert response.json() == {
        "fecha": "2026-09-07",
        "plan": [
            {
                "tarea_id": 10,
                "orden": 1,
                "motivo": "Vence en la fecha planificada.",
            }
        ],
        "resumen": "Se organizó 1 tarea relevante para el día.",
    }
    assert service.usuario_id_recibido == 1
    assert service.fecha_recibida == date(2026, 9, 7)


def test_plan_dia_acepta_una_fecha_omitida(client):
    test_client, service = client

    response = test_client.post("/ia/plan-dia", json={})

    assert response.status_code == 200
    assert service.fecha_recibida is None
