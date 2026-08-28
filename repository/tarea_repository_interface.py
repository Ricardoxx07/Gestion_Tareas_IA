from abc import ABC, abstractmethod
from models.tarea import Tarea


class TareaRepositoryInterface(ABC):

    @abstractmethod
    def cargar_tareas(self) -> list[Tarea]:
        pass

    @abstractmethod
    def obtener_tarea(self, id_tarea: int) -> Tarea | None:
        pass

    @abstractmethod
    def guardar_tarea(self, tarea: Tarea) -> Tarea:
        pass

    @abstractmethod
    def actualizar_tarea(self, tarea: Tarea) -> None:
        pass

    @abstractmethod
    def eliminar_tarea(self, id_tarea: int) -> bool:
        pass