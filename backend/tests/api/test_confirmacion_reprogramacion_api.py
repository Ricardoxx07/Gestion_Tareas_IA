from datetime import date

import pytest
from fastapi.testclient import TestClient

from api.dependencies import (
    obtener_confirmacion_reprogramacion_service,
    obtener_usuario_actual,
)
from api.main import app
from exceptions.tarea_exceptions import PropuestaDesactualizadaError
from models.tarea import Tarea
from models.usuario import Usuario


class ConfirmacionReprogramacionServiceFalso:
    def __init__(self, error=None):
        self.error = error
        self.cambios_recibidos = None
        self.usuario_id_recibido = None

    def confirmar(self, cambios, usuario_id):
        self.cambios_recibidos = cambios
        self.usuario_id_recibido = usuario_id
        if self.error:
            raise self.error
        return [
            Tarea(
                id=tarea_id,
                nombre="Tarea reprogramada",
                usuario_id=usuario_id,
                fecha_limite=fecha_sugerida,
            )
            for tarea_id, _, fecha_sugerida in cambios
        ]


@pytest.fixture
def usuario():
    return Usuario(id=1, email="ricardo@example.com", password_hash="hash")


def test_confirma_reprogramacion_seleccionada(usuario):
    service = ConfirmacionReprogramacionServiceFalso()
    app.dependency_overrides[obtener_usuario_actual] = lambda: usuario
    app.dependency_overrides[obtener_confirmacion_reprogramacion_service] = lambda: service

    response = TestClient(app).post(
        "/ia/reprogramaciones/confirmar",
        json={"reprogramaciones": [{"tarea_id": 10, "fecha_actual": "2026-09-08", "fecha_sugerida": "2026-09-06"}]},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["tareas_actualizadas"][0]["fecha_limite"] == "2026-09-06"
    assert service.usuario_id_recibido == 1
    assert service.cambios_recibidos == [(10, date(2026, 9, 8), date(2026, 9, 6))]


def test_rechaza_propuesta_desactualizada(usuario):
    service = ConfirmacionReprogramacionServiceFalso(
        PropuestaDesactualizadaError("La tarea con id 10 cambió desde la propuesta")
    )
    app.dependency_overrides[obtener_usuario_actual] = lambda: usuario
    app.dependency_overrides[obtener_confirmacion_reprogramacion_service] = lambda: service

    response = TestClient(app).post(
        "/ia/reprogramaciones/confirmar",
        json={"reprogramaciones": [{"tarea_id": 10, "fecha_actual": "2026-09-08", "fecha_sugerida": "2026-09-06"}]},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 409
