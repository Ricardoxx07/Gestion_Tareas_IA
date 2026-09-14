from abc import ABC, abstractmethod
from models.tarea import Tarea


class TareaRepositoryInterface(ABC):

    @abstractmethod
    def cargar_tareas(self, usuario_id: int) -> list[Tarea]:
        pass

    @abstractmethod
    def cargar_subtareas(self, tarea_padre_id: int, usuario_id: int) -> list[Tarea]:
        pass

    @abstractmethod
    def obtener_tarea(self, id_tarea: int, usuario_id: int) -> Tarea | None:
        pass

    @abstractmethod
    def guardar_tarea(self, tarea: Tarea) -> Tarea:
        pass

    @abstractmethod
    def guardar_tareas(self, tareas: list[Tarea]) -> list[Tarea]:
        """Persiste un lote de tareas en una única transacción."""
        pass

    @abstractmethod
    def actualizar_tarea(self, tarea: Tarea) -> None:
        pass

    @abstractmethod
    def actualizar_tareas(self, tareas: list[Tarea]) -> list[Tarea]:
        """Actualiza un lote de tareas en una única transacción."""
        pass

    @abstractmethod
    def eliminar_tarea(self, id_tarea: int, usuario_id: int) -> bool:
        pass
