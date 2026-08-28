import pytest
from unittest.mock import Mock

from services.tarea_service import TareaService


# =========================================================
# Repository falso
# =========================================================

class RepositoryFalso:

    def __init__(self):
        self.tareas = []
        self.siguiente_id = 1

    def cargar_tareas(self):
        return self.tareas.copy()

    def guardar_tarea(self, tarea):
        tarea.id = self.siguiente_id
        self.siguiente_id += 1

        self.tareas.append(tarea)

        return tarea

    def obtener_tarea(self, id_tarea):
        for tarea in self.tareas:
            if tarea.id == id_tarea:
                return tarea

        return None

    def actualizar_tarea(self, tarea):
        for i, tarea_existente in enumerate(self.tareas):
            if tarea_existente.id == tarea.id:
                self.tareas[i] = tarea
                return tarea

        return None

    def eliminar_tarea(self, id_tarea):
        for tarea in self.tareas:
            if tarea.id == id_tarea:
                self.tareas.remove(tarea)
                return True

        return False


# =========================================================
# Fixtures
# =========================================================

@pytest.fixture
def service():
    repository = RepositoryFalso()
    return TareaService(repository)


@pytest.fixture
def service_mock():
    repository = Mock()

    def guardar_tarea(tarea):
        tarea.id = 1
        return tarea

    repository.guardar_tarea.side_effect = guardar_tarea
    repository.eliminar_tarea.return_value = True

    return TareaService(repository), repository


# =========================================================
# Tests de comportamiento del Service
# =========================================================

def test_agregar_tarea(service):

    tarea = service.agregar_tarea("Estudiar Python")

    assert tarea.nombre == "Estudiar Python"
    assert tarea.completada is False


def test_completar_tarea(service):

    tarea = service.agregar_tarea("Estudiar Python")

    resultado = service.completar_tarea(tarea.id)

    assert resultado is True

    tarea = service.obtener_tarea(tarea.id)

    assert tarea is not None
    assert tarea.completada is True


def test_eliminar_tarea(service):

    tarea1 = service.agregar_tarea("Estudiar Python")
    tarea2 = service.agregar_tarea("Ir de compras al super.")

    resultado = service.eliminar_tarea(tarea1.id)

    assert resultado is True
    assert service.obtener_tarea(tarea1.id) is None

    tarea = service.obtener_tarea(tarea2.id)

    assert tarea is not None
    assert tarea.nombre == "Ir de compras al super."


def test_completar_tarea_inexistente(service):

    service.agregar_tarea("Estudiar Python")

    resultado = service.completar_tarea(999)

    assert resultado is False


def test_eliminar_tarea_inexistente(service):

    service.agregar_tarea("Estudiar Python")

    resultado = service.eliminar_tarea(999)

    assert resultado is False


def test_listar_tareas_sin_tareas(service):

    tareas = service.listar_tareas()

    assert tareas == []


def test_eliminar_tarea_por_id(service):

    tarea1 = service.agregar_tarea("Estudiar Python")
    tarea2 = service.agregar_tarea("Aprender FastAPI")
    tarea3 = service.agregar_tarea("Crear proyecto IA")

    resultado = service.eliminar_tarea(tarea2.id)

    assert resultado is True
    assert service.obtener_tarea(tarea1.id) is not None
    assert service.obtener_tarea(tarea2.id) is None
    assert service.obtener_tarea(tarea3.id) is not None


def test_obtener_tarea_por_id(service):

    service.agregar_tarea("Estudiar Python")
    tarea2 = service.agregar_tarea("Aprender FastAPI")

    tarea = service.obtener_tarea(tarea2.id)

    assert tarea is not None
    assert tarea.nombre == "Aprender FastAPI"


def test_actualizar_tarea(service):

    tarea = service.agregar_tarea("Estudiar Python")

    tarea_actualizada = service.actualizar_tarea(
        tarea.id,
        "Estudiar FastAPI",
        True
    )

    assert tarea_actualizada is not None
    assert tarea_actualizada.nombre == "Estudiar FastAPI"
    assert tarea_actualizada.completada is True


def test_actualizar_tarea_inexistente(service):

    service.agregar_tarea("Estudiar Python")

    tarea = service.actualizar_tarea(
        999,
        "Tarea inexistente",
        True
    )

    assert tarea is None


def test_actualizar_parcialmente_tarea(service):

    tarea = service.agregar_tarea("Estudiar Python")

    tarea_actualizada = service.actualizar_parcialmente_tarea(
        tarea.id,
        None,
        True
    )

    assert tarea_actualizada is not None
    assert tarea_actualizada.nombre == "Estudiar Python"
    assert tarea_actualizada.completada is True


def test_actualizar_parcialmente_nombre(service):

    tarea = service.agregar_tarea("Estudiar Python")

    tarea_actualizada = service.actualizar_parcialmente_tarea(
        tarea.id,
        "Estudiar FastAPI",
        None
    )

    assert tarea_actualizada is not None
    assert tarea_actualizada.nombre == "Estudiar FastAPI"
    assert tarea_actualizada.completada is False


def test_actualizar_parcialmente_tarea_inexistente(service):

    service.agregar_tarea("Estudiar Python")

    tarea = service.actualizar_parcialmente_tarea(
        999,
        "Nueva tarea",
        True
    )

    assert tarea is None


# =========================================================
# Tests de interacción:
# Service -> Repository
# =========================================================

def test_agregar_tarea_guarda_en_repository(service_mock):

    service, repository = service_mock

    tarea = service.agregar_tarea("Estudiar Python")

    repository.guardar_tarea.assert_called_once_with(tarea)


def test_completar_tarea_actualiza_en_repository(service_mock):

    service, repository = service_mock

    tarea = service.agregar_tarea("Estudiar Python")

    repository.guardar_tarea.reset_mock()

    repository.obtener_tarea.return_value = tarea

    resultado = service.completar_tarea(tarea.id)

    assert resultado is True

    repository.actualizar_tarea.assert_called_once_with(tarea)


def test_eliminar_tarea_elimina_en_repository(service_mock):

    service, repository = service_mock

    tarea = service.agregar_tarea("Estudiar Python")

    repository.obtener_tarea.return_value = tarea

    repository.guardar_tarea.reset_mock()

    resultado = service.eliminar_tarea(tarea.id)

    assert resultado is True

    repository.eliminar_tarea.assert_called_once_with(tarea.id)


def test_actualizar_tarea_actualiza_en_repository(service_mock):

    service, repository = service_mock

    tarea = service.agregar_tarea("Estudiar Python")

    repository.obtener_tarea.return_value = tarea

    repository.guardar_tarea.reset_mock()

    tarea_actualizada = service.actualizar_tarea(
        tarea.id,
        "Estudiar FastAPI",
        True
    )

    repository.actualizar_tarea.assert_called_once_with(
        tarea_actualizada
    )


def test_actualizar_parcialmente_actualiza_en_repository(service_mock):

    service, repository = service_mock

    tarea = service.agregar_tarea("Estudiar Python")

    repository.obtener_tarea.return_value = tarea

    repository.guardar_tarea.reset_mock()

    tarea_actualizada = service.actualizar_parcialmente_tarea(
        tarea.id,
        "Estudiar FastAPI",
        None
    )

    repository.actualizar_tarea.assert_called_once_with(
        tarea_actualizada
    )