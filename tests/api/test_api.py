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

    def cargar_subtareas(tarea_padre_id, usuario_id):
        return [
            tarea
            for tarea in tareas.values()
            if tarea.usuario_id == usuario_id
            and tarea.tarea_padre_id == tarea_padre_id
        ]

    repository.cargar_subtareas.side_effect = cargar_subtareas

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
            "completada": False,
            "fecha_limite": None,
            "prioridad": "media",
            "created_at": None,
            "tarea_padre_id": None,
        },
        {
            "id": 2,
            "nombre": "Aprender FastAPI",
            "completada": True,
            "fecha_limite": None,
            "prioridad": "media",
            "created_at": None,
            "tarea_padre_id": None,
        }
    ]


def test_obtener_tarea_por_id(client):
    response = client.get("/tareas/1")

    assert response.status_code == 200

    assert response.json() == {
        "id": 1,
        "nombre": "Estudiar Python",
        "completada": False,
        "fecha_limite": None,
        "prioridad": "media",
        "created_at": None,
        "tarea_padre_id": None,
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
            "nombre": "Crear proyecto de IA",
            "fecha_limite": "2026-09-10",
            "prioridad": "alta"
        }
    )

    assert response.status_code == 201

    datos = response.json()

    assert datos["id"] == 3
    assert datos["nombre"] == "Crear proyecto de IA"
    assert datos["completada"] is False
    assert datos["fecha_limite"] == "2026-09-10"
    assert datos["prioridad"] == "alta"


def test_crear_y_listar_subtareas(client):
    response = client.post(
        "/tareas/1/subtareas",
        json={
            "nombre": "Definir estructura de diapositivas",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 3
    assert response.json()["tarea_padre_id"] == 1

    subtareas = client.get("/tareas/1/subtareas")

    assert subtareas.status_code == 200
    assert subtareas.json()[0]["id"] == 3
    assert subtareas.json()[0]["tarea_padre_id"] == 1


def test_crear_subtarea_rechaza_un_padre_inexistente(client):
    response = client.post(
        "/tareas/999/subtareas",
        json={
            "nombre": "Subtarea sin padre válido",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Tarea padre con id 999 no encontrada"}


def test_crear_subtarea_no_acepta_un_padre_en_el_cuerpo(client):
    response = client.post(
        "/tareas/1/subtareas",
        json={
            "nombre": "Subtarea con padre en el cuerpo",
            "tarea_padre_id": 999,
        },
    )

    assert response.status_code == 422


def test_obtener_subtarea_desde_su_padre(client):
    creada = client.post(
        "/tareas/1/subtareas",
        json={"nombre": "Definir estructura"},
    )

    response = client.get("/tareas/1/subtareas/3")

    assert creada.status_code == 201
    assert response.status_code == 200
    assert response.json()["nombre"] == "Definir estructura"
    assert response.json()["tarea_padre_id"] == 1


def test_no_obtiene_subtarea_bajo_otro_padre(client):
    client.post("/tareas/1/subtareas", json={"nombre": "Definir estructura"})

    response = client.get("/tareas/2/subtareas/3")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Subtarea con id 3 no encontrada para la tarea padre"
    }


def test_actualizar_subtarea_con_put_y_patch(client):
    client.post("/tareas/1/subtareas", json={"nombre": "Definir estructura"})

    actualizada = client.put(
        "/tareas/1/subtareas/3",
        json={"nombre": "Definir contenido", "completada": True},
    )
    parcial = client.patch(
        "/tareas/1/subtareas/3",
        json={"prioridad": "alta"},
    )

    assert actualizada.status_code == 200
    assert actualizada.json()["nombre"] == "Definir contenido"
    assert actualizada.json()["completada"] is True
    assert parcial.status_code == 200
    assert parcial.json()["prioridad"] == "alta"
    assert parcial.json()["tarea_padre_id"] == 1


def test_eliminar_subtarea_desde_su_padre(client):
    client.post("/tareas/1/subtareas", json={"nombre": "Definir estructura"})

    eliminada = client.delete("/tareas/1/subtareas/3")
    subtareas = client.get("/tareas/1/subtareas")

    assert eliminada.status_code == 204
    assert subtareas.status_code == 200
    assert subtareas.json() == []


def test_crear_tarea_rechaza_prioridad_invalida(client):
    response = client.post(
        "/tareas",
        json={
            "nombre": "Crear proyecto de IA",
            "prioridad": "urgente"
        }
    )

    assert response.status_code == 422


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
        "completada": True,
        "fecha_limite": None,
        "prioridad": "media",
        "created_at": None,
        "tarea_padre_id": None,
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
        "completada": False,
        "fecha_limite": None,
        "prioridad": "media",
        "created_at": None,
        "tarea_padre_id": None,
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
