import pytest
from unittest.mock import Mock
from services.tarea_service import TareaService

class Repository_Falso:
    def cargar_tareas(self):
        return []
    

    def guardar_tareas(self, tareas):
        pass

#Un @pytest.fixture es una función que prepara el entorno o los objetos necesarios antes de ejecutar un test.
# Sirve para reutilizar la configuración inicial (setup) y evitar duplicar código en cada prueba.
@pytest.fixture
def service():
    repository = Repository_Falso()
    return TareaService(repository)

def test_agregar_tarea(service):

    #Se crea una variable repository y service que hacen referencia de objeto a las clases Repository_Falso
    #y service a TareaService

    """ Con pytest.fixture esto ya se podría abreviar:
    repository = Repository_Falso()

    service = TareaService(repository)
    """

    service.agregar_tarea("Estudiar Python")

    assert len(service.tareas) == 1
    assert service.tareas[0].nombre == "Estudiar Python"
    assert service.tareas[0].completada is False

def test_completar_tarea(service):
    

    service.agregar_tarea("Estudiar Python")

    service.completar_tarea(1)

    assert service.tareas[0].completada is True


def test_eliminar_tarea(service):

    service.agregar_tarea("Estudiar Python")
    service.agregar_tarea("Ir de compras al super.")

    
    service.eliminar_tarea(1)

    assert len(service.tareas) == 1
    assert service.tareas[0].nombre == "Ir de compras al super."


def test_completar_tarea_inexistente(service):

    service.agregar_tarea("Estudiar Python")

    service.completar_tarea(5)

    assert service.tareas[0].completada is False

def test_eliminar_tarea_inexistente(service):

    service.agregar_tarea("Estudiar Python")

    service.eliminar_tarea(5)

    assert len(service.tareas) == 1
    assert service.tareas[0].nombre == "Estudiar Python"

def test_listar_tareas_sin_tareas(service):

    service.listar_tareas()

    assert service.tareas == []

def test_agregar_tarea_guarda_en_repository():

    #Crea un repositorio falso, pero esta vez no se tiene que incializar.
    #Mock se encarga de simular métodos.Es un lienzo en blanco.
    repository = Mock()

    #Aquí ocurre la magia de Python. Al escribir .cargar_tareas, el objeto Mock dice: "Ah, ¿me estás pidiendo este método?
    #  No lo tenía, pero lo acabo de crear ahora mismo". Al agregarle .return_value = [],
    #  le estás dando el guion: "Y cuando alguien te llame, devuelve una lista vacía".
    repository.cargar_tareas.return_value = []

    #El Service recibe este "actor" creyendo que es un repositorio real.
    #  Cuando el constructor del Service ejecuta internamente self.repositorio.cargar_tareas(),
    #  el Mock actúa su papel y le entrega la lista vacía []. El Service ni se entera de que es un impostor.
    service = TareaService(repository)

    #El Service ejecuta su lógica real (agrega la tarea a la RAM)
    #  y luego llama internamente a self.repositorio.guardar_tareas(self.tareas).
    #  Nuevamente, el Mock dice: "¿Me llamas a guardar_tareas? Lo creo en este instante
    #  y anoto en mi libreta que me llamaste y con qué datos me llamaste".
    service.agregar_tarea("Estudiar Python")

    #Esta es la función del Mock como "espía".
    #Como el Mock anotó todo lo que le hicieron, tú puedes preguntarle al final de la prueba:
    #  "Oye, ¿el Service te llamó exactamente una vez usando este método y pasándote exactamente esta lista?". 
    # Si es verdad, el test pasa. Si el Service nunca lo llamó, el test falla.
    repository.guardar_tareas.assert_called_once_with(service.tareas)


def test_completar_tarea_guarda_en_repository():

    repository = Mock()
    repository.cargar_tareas.return_value = []

    service = TareaService(repository)

    service.agregar_tarea("Estudiar Python")

    repository.guardar_tareas.reset_mock()

    service.completar_tarea(1)

    repository.guardar_tareas.assert_called_once_with(service.tareas)

def test_eliminar_tarea_guarda_en_repository():

    repository = Mock()
    repository.cargar_tareas.return_value = []

    service = TareaService(repository)

    service.agregar_tarea("Estudiar Python")

    repository.reset_mock()

    service.eliminar_tarea(1)

    repository.guardar_tareas.assert_called_once_with(service.tareas)







    """
Diferencia clave: Mock vs. Repositorio Falso

El Falso (Repository_Falso): Tienes que escribir una clase entera tú mismo, definir def cargar_tareas(self): 
 y escribir código para simular la RAM.

El Mock (Mock()): No escribes ninguna clase. Es un espía dinámico que se adapta a lo que le pidas
 y memoriza cómo interactuaron con él.

(Si recuerdas Java, esto es exactamente lo que hace la librería Mockito, solo que en Python es aún más flexible
 porque no te obliga a amarrarlo a una interfaz previa).


    """
