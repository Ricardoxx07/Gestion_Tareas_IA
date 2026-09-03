import pytest

from unittest.mock import Mock

from services.tarea_service import TareaService
from exceptions.tarea_exceptions import TareaNoEncontradaError


USUARIO_ID = 1
OTRO_USUARIO_ID = 2


# =========================================================
# Repository falso
# =========================================================

class RepositoryFalso:

    def __init__(self):
        self.tareas = []
        self.siguiente_id = 1

    def cargar_tareas(self, usuario_id):
        return [tarea for tarea in self.tareas if tarea.usuario_id == usuario_id]

    def guardar_tarea(self, tarea):
        tarea.id = self.siguiente_id
        self.siguiente_id += 1

        self.tareas.append(tarea)

        return tarea

    def obtener_tarea(self, id_tarea, usuario_id):
        for tarea in self.tareas:
            if tarea.id == id_tarea and tarea.usuario_id == usuario_id:
                return tarea

        return None

    def actualizar_tarea(self, tarea):
        for i, tarea_existente in enumerate(self.tareas):
            if tarea_existente.id == tarea.id:
                self.tareas[i] = tarea
                return tarea

        return None

    def eliminar_tarea(self, id_tarea, usuario_id):
        for tarea in self.tareas:
            if tarea.id == id_tarea and tarea.usuario_id == usuario_id:
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

    tarea = service.agregar_tarea("Estudiar Python", USUARIO_ID)

    assert tarea.nombre == "Estudiar Python"
    assert tarea.completada is False
    assert tarea.usuario_id == USUARIO_ID


def test_completar_tarea(service):

    tarea = service.agregar_tarea("Estudiar Python", USUARIO_ID)

    resultado = service.completar_tarea(tarea.id, USUARIO_ID)

    assert resultado is True

    tarea = service.obtener_tarea(tarea.id, USUARIO_ID)

    assert tarea is not None
    assert tarea.completada is True


def test_eliminar_tarea(service):

    tarea1 = service.agregar_tarea("Estudiar Python", USUARIO_ID)
    tarea2 = service.agregar_tarea("Ir de compras al super.", USUARIO_ID)

    resultado = service.eliminar_tarea(tarea1.id, USUARIO_ID)

    assert resultado is True
    assert service.obtener_tarea(tarea1.id, USUARIO_ID) is None

    tarea = service.obtener_tarea(tarea2.id, USUARIO_ID)

    assert tarea is not None
    assert tarea.nombre == "Ir de compras al super."


def test_completar_tarea_inexistente(service):

    service.agregar_tarea("Estudiar Python", USUARIO_ID)

    with pytest.raises(TareaNoEncontradaError) as exc_info:
        service.completar_tarea(999, USUARIO_ID)

    assert str(exc_info.value) == "Tarea con id 999 no encontrada"


def test_eliminar_tarea_inexistente(service):

    service.agregar_tarea("Estudiar Python", USUARIO_ID)

    with pytest.raises(TareaNoEncontradaError) as exc_info:
        service.eliminar_tarea(999, USUARIO_ID)

    assert str(exc_info.value) == "Tarea con id 999 no encontrada"


def test_listar_tareas_sin_tareas(service):

    tareas = service.listar_tareas(USUARIO_ID)

    assert tareas == []


def test_eliminar_tarea_por_id(service):

    tarea1 = service.agregar_tarea("Estudiar Python", USUARIO_ID)
    tarea2 = service.agregar_tarea("Aprender FastAPI", USUARIO_ID)
    tarea3 = service.agregar_tarea("Crear proyecto IA", USUARIO_ID)

    resultado = service.eliminar_tarea(tarea2.id, USUARIO_ID)

    assert resultado is True
    assert service.obtener_tarea(tarea1.id, USUARIO_ID) is not None
    assert service.obtener_tarea(tarea2.id, USUARIO_ID) is None
    assert service.obtener_tarea(tarea3.id, USUARIO_ID) is not None


def test_obtener_tarea_por_id(service):

    service.agregar_tarea("Estudiar Python", USUARIO_ID)
    tarea2 = service.agregar_tarea("Aprender FastAPI", USUARIO_ID)

    tarea = service.obtener_tarea(tarea2.id, USUARIO_ID)

    assert tarea is not None
    assert tarea.nombre == "Aprender FastAPI"


def test_actualizar_tarea(service):

    tarea = service.agregar_tarea("Estudiar Python", USUARIO_ID)

    tarea_actualizada = service.actualizar_tarea(
        tarea.id,
        USUARIO_ID,
        "Estudiar FastAPI",
        True
    )

    assert tarea_actualizada is not None
    assert tarea_actualizada.nombre == "Estudiar FastAPI"
    assert tarea_actualizada.completada is True


def test_actualizar_tarea_inexistente(service):

    service.agregar_tarea("Estudiar Python", USUARIO_ID)

    with pytest.raises(TareaNoEncontradaError) as exc_info:
        service.actualizar_tarea(
            999,
            USUARIO_ID,
            "Tarea inexistente",
            True
        )

    assert str(exc_info.value) == "Tarea con id 999 no encontrada"


def test_actualizar_parcialmente_tarea(service):

    tarea = service.agregar_tarea("Estudiar Python", USUARIO_ID)

    tarea_actualizada = service.actualizar_parcialmente_tarea(
        tarea.id,
        USUARIO_ID,
        None,
        True
    )

    assert tarea_actualizada is not None
    assert tarea_actualizada.nombre == "Estudiar Python"
    assert tarea_actualizada.completada is True


def test_actualizar_parcialmente_nombre(service):

    tarea = service.agregar_tarea("Estudiar Python", USUARIO_ID)

    tarea_actualizada = service.actualizar_parcialmente_tarea(
        tarea.id,
        USUARIO_ID,
        "Estudiar FastAPI",
        None
    )

    assert tarea_actualizada is not None
    assert tarea_actualizada.nombre == "Estudiar FastAPI"
    assert tarea_actualizada.completada is False


def test_actualizar_parcialmente_tarea_inexistente(service):

    service.agregar_tarea("Estudiar Python", USUARIO_ID)

    with pytest.raises(TareaNoEncontradaError) as exc_info:
        service.actualizar_parcialmente_tarea(
            999,
            USUARIO_ID,
            "Nueva tarea",
            True
        )

    assert str(exc_info.value) == "Tarea con id 999 no encontrada"


# =========================================================
# Tests de interacción:
# Service -> Repository
# =========================================================

def test_agregar_tarea_guarda_en_repository(service_mock):

    service, repository = service_mock

    tarea = service.agregar_tarea("Estudiar Python", USUARIO_ID)

    repository.guardar_tarea.assert_called_once_with(tarea)


def test_completar_tarea_actualiza_en_repository(service_mock):

    service, repository = service_mock

    tarea = service.agregar_tarea("Estudiar Python", USUARIO_ID)

    repository.guardar_tarea.reset_mock()

    repository.obtener_tarea.return_value = tarea

    resultado = service.completar_tarea(tarea.id, USUARIO_ID)

    assert resultado is True

    repository.actualizar_tarea.assert_called_once_with(tarea)


def test_eliminar_tarea_elimina_en_repository(service_mock):

    service, repository = service_mock

    tarea = service.agregar_tarea("Estudiar Python", USUARIO_ID)

    repository.obtener_tarea.return_value = tarea

    repository.guardar_tarea.reset_mock()

    resultado = service.eliminar_tarea(tarea.id, USUARIO_ID)

    assert resultado is True

    repository.eliminar_tarea.assert_called_once_with(tarea.id, USUARIO_ID)


def test_actualizar_tarea_actualiza_en_repository(service_mock):

    service, repository = service_mock

    tarea = service.agregar_tarea("Estudiar Python", USUARIO_ID)

    repository.obtener_tarea.return_value = tarea

    repository.guardar_tarea.reset_mock()

    tarea_actualizada = service.actualizar_tarea(
        tarea.id,
        USUARIO_ID,
        "Estudiar FastAPI",
        True
    )

    repository.actualizar_tarea.assert_called_once_with(
        tarea_actualizada
    )


def test_actualizar_parcialmente_actualiza_en_repository(service_mock):

    service, repository = service_mock

    tarea = service.agregar_tarea("Estudiar Python", USUARIO_ID)

    repository.obtener_tarea.return_value = tarea

    repository.guardar_tarea.reset_mock()

    tarea_actualizada = service.actualizar_parcialmente_tarea(
        tarea.id,
        USUARIO_ID,
        "Estudiar FastAPI",
        None
    )

    repository.actualizar_tarea.assert_called_once_with(
        tarea_actualizada
    )


def test_un_usuario_no_puede_obtener_ni_listar_tareas_de_otro(service):
    tarea = service.agregar_tarea("Tarea privada", USUARIO_ID)

    assert service.listar_tareas(OTRO_USUARIO_ID) == []
    assert service.obtener_tarea(tarea.id, OTRO_USUARIO_ID) is None
