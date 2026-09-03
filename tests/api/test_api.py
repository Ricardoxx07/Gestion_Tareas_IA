import pytest
from unittest.mock import Mock

from fastapi.testclient import TestClient

from api.main import app
from api.dependencies import obtener_service, obtener_usuario_actual
from models.tarea import Tarea
from models.usuario import Usuario
from services.tarea_service import TareaService



@pytest.fixture
def service_falso():

    repository = Mock()

    tarea1 = Tarea(
        id=1,
        nombre="Estudiar Python",
        completada=False,
        usuario_id=1
    )

    tarea2 = Tarea(
        id=2,
        nombre="Aprender FastAPI",
        completada=True,
        usuario_id=1
    )

    tareas = {
        1: tarea1,
        2: tarea2
    }

    def cargar_tareas(usuario_id):
        return [tarea for tarea in tareas.values() if tarea.usuario_id == usuario_id]

    repository.cargar_tareas.side_effect = cargar_tareas

    def obtener_tarea(id_tarea, usuario_id):
        tarea = tareas.get(id_tarea)
        return tarea if tarea and tarea.usuario_id == usuario_id else None

    repository.obtener_tarea.side_effect = obtener_tarea

    def guardar_tarea(tarea):
        tarea.id = max(tareas.keys(), default=0) + 1
        tareas[tarea.id] = tarea
        return tarea

    repository.guardar_tarea.side_effect = guardar_tarea

    def actualizar_tarea(tarea):
        if tarea.id not in tareas:
            return

        tareas[tarea.id] = tarea

    repository.actualizar_tarea.side_effect = actualizar_tarea

    def eliminar_tarea(id_tarea, usuario_id):
        tarea = tareas.get(id_tarea)
        if tarea is None or tarea.usuario_id != usuario_id:
            return False

        del tareas[id_tarea]
        return True

    repository.eliminar_tarea.side_effect = eliminar_tarea

    return TareaService(repository)




@pytest.fixture
def client(service_falso):
    app.dependency_overrides[obtener_service] = lambda: service_falso
    app.dependency_overrides[obtener_usuario_actual] = lambda: Usuario(
        id=1,
        email="ricardo@example.com",
        password_hash="hash-interno"
    )

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def test_listar_tareas(client):
    response = client.get("/tareas")

    assert response.status_code == 200

    assert response.json() == [
        {
            "id": 1,
            "nombre": "Estudiar Python",
            "completada": False
        },
        {
            "id": 2,
            "nombre": "Aprender FastAPI",
            "completada": True
        }
    ]


def test_obtener_tarea_por_id(client):
    response = client.get("/tareas/1")

    assert response.status_code == 200

    assert response.json() == {
        "id": 1,
        "nombre": "Estudiar Python",
        "completada": False
    }


def test_obtener_tarea_inexistente(client):
    response = client.get("/tareas/999")

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Tarea no encontrada"
    }


def test_crear_tarea(client):
    response = client.post(
        "/tareas",
        json={
            "nombre": "Crear proyecto de IA"
        }
    )

    assert response.status_code == 201

    datos = response.json()

    assert datos["id"] == 3
    assert datos["nombre"] == "Crear proyecto de IA"
    assert datos["completada"] is False


def test_actualizar_tarea(client):
    response = client.put(
        "/tareas/1",
        json={
            "nombre": "Estudiar Python avanzado",
            "completada": True
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "id": 1,
        "nombre": "Estudiar Python avanzado",
        "completada": True
    }


def test_actualizar_tarea_inexistente(client):
    response = client.put(
        "/tareas/999",
        json={
            "nombre": "Tarea inexistente",
            "completada": True
        }
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Tarea con id 999 no encontrada"
    }


def test_actualizar_parcialmente_tarea(client):
    response = client.patch(
        "/tareas/1",
        json={
            "nombre": "Estudiar Python avanzado"
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "id": 1,
        "nombre": "Estudiar Python avanzado",
        "completada": False
    }


def test_actualizar_parcialmente_tarea_inexistente(client):
    response = client.patch(
        "/tareas/999",
        json={
            "nombre": "Tarea inexistente"
        }
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Tarea con id 999 no encontrada"
    }


def test_eliminar_tarea(client):
    response = client.delete("/tareas/1")

    assert response.status_code == 204


def test_eliminar_tarea_inexistente(client):
    response = client.delete("/tareas/999")

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Tarea con id 999 no encontrada"
    }
