from models.tarea import Tarea
from repository.tarea_repository import TareaRepository
from services.tarea_service import TareaService

import pytest


#Lo sabe porque en la fixture estás sobrescribiendo la ruta predeterminada del archivo
#  y reemplazándola por una ruta generada dentro de una carpeta temporal.
@pytest.fixture
def repository(tmp_path):
    archivo = tmp_path / "tareas.json"
    return TareaRepository(archivo)

def test_guardar_y_cargar_tareas(repository):

    #tmp_path te da una carpeta temporal exclusiva para ese test.
    #"Dentro de esa carpeta temporal, quiero trabajar con un archivo llamado tareas.json."

    """ Con pytest esto se abrevia:
    archivo = tmp_path / "tareas.json"

    repository = TareaRepository(archivo)
    """

    tareas = [
        Tarea("Estudiar Python"),
        Tarea("Aprender FastAPI", True)
    ]

    repository.guardar_tareas(tareas)

    tareas_cargadas = repository.cargar_tareas()

    assert len(tareas_cargadas) == 2
    assert tareas_cargadas[0].nombre == "Estudiar Python"
    assert tareas_cargadas[0].completada is False

    assert tareas_cargadas[1].nombre == "Aprender FastAPI"
    assert tareas_cargadas[1].completada is True

def test_cargar_tareas_archivo_inexistente(repository):

    tareas = repository.cargar_tareas()

    assert tareas == []


def test_cargar_tareas_json_invalido(tmp_path):

    archivo = tmp_path / "tareas.json"

    archivo.write_text("Esto no es un JSON válido")

    repository = TareaRepository(archivo)

    tareas = repository.cargar_tareas()

    assert tareas == []

def test_guardar_tareas_preserva_datos(tmp_path):

    archivo = tmp_path / "tareas.json"

    repository = TareaRepository(archivo)

    tareas = [
        Tarea("Estudiar Python", False),
        Tarea("Aprender FastAPI", True),
        Tarea("Crear proyecto de IA", False)
    ]

    repository.guardar_tareas(tareas)

    tareas_cargadas = repository.cargar_tareas()

    assert len(tareas_cargadas) == 3

    assert tareas_cargadas[0].nombre == "Estudiar Python"
    assert tareas_cargadas[0].completada is False

    assert tareas_cargadas[1].nombre == "Aprender FastAPI"
    assert tareas_cargadas[1].completada is True

    assert tareas_cargadas[2].nombre == "Crear proyecto de IA"
    assert tareas_cargadas[2].completada is False

