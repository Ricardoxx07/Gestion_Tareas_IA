from datetime import date

import pytest
from fastapi.testclient import TestClient

from api.dependencies import obtener_sobrecarga_service, obtener_usuario_actual
from api.main import app
from models.sobrecarga import AlertaSobrecarga, AnalisisSobrecarga
from models.usuario import Usuario


class SobrecargaServiceFalso:
    def __init__(self):
        self.argumentos_recibidos = None

    def detectar_sobrecarga(
        self,
        usuario_id: int,
        fecha_inicio: date | None,
        dias: int,
        max_tareas_por_dia: int,
    ) -> AnalisisSobrecarga:
        self.argumentos_recibidos = (
            usuario_id,
            fecha_inicio,
            dias,
            max_tareas_por_dia,
        )
        return AnalisisSobrecarga(
            fecha_inicio=fecha_inicio or date(2026, 9, 5),
            fecha_fin=date(2026, 9, 11),
            max_tareas_por_dia=max_tareas_por_dia,
            alertas=[
                AlertaSobrecarga(
                    fecha=date(2026, 9, 7),
                    cantidad_tareas=4,
                    tarea_ids=[10, 11, 12, 13],
                    mensaje="Hay tareas concentradas en ese día.",
                    sugerencia="Adelanta una tarea si es posible.",
                )
            ],
        )


@pytest.fixture
def client():
    usuario = Usuario(id=1, email="ricardo@example.com", password_hash="hash")
    service = SobrecargaServiceFalso()
    app.dependency_overrides[obtener_usuario_actual] = lambda: usuario
    app.dependency_overrides[obtener_sobrecarga_service] = lambda: service

    yield TestClient(app), service

    app.dependency_overrides.clear()


def test_detectar_sobrecarga_devuelve_alertas_del_usuario(client):
    test_client, service = client

    response = test_client.post(
        "/ia/detectar-sobrecarga",
        json={
            "fecha_inicio": "2026-09-05",
            "dias": 7,
            "max_tareas_por_dia": 3,
        },
    )

    assert response.status_code == 200
    assert response.json()["alertas"][0] == {
        "fecha": "2026-09-07",
        "mensaje": "Hay tareas concentradas en ese día.",
        "sugerencia": "Adelanta una tarea si es posible.",
        "cantidad_tareas": 4,
        "tarea_ids": [10, 11, 12, 13],
    }
    assert service.argumentos_recibidos == (1, date(2026, 9, 5), 7, 3)
