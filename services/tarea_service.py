from models.tarea import Tarea
from repository.tarea_repository_interface import TareaRepositoryInterface

class TareaService:

    def __init__(self, repository: TareaRepositoryInterface):
        self.repository = repository

    def agregar_tarea(self, nombre: str) -> Tarea:
        nueva_tarea = Tarea(nombre=nombre)

        return self.repository.guardar_tarea(nueva_tarea)

    def listar_tareas(self) -> list[Tarea]:
        return self.repository.cargar_tareas()

    def obtener_tarea(self, id_tarea: int) -> Tarea | None:
        return self.repository.obtener_tarea(id_tarea)

    def completar_tarea(self, id_tarea: int) -> bool:
        tarea = self.obtener_tarea(id_tarea)

        if tarea is None:
            return False

        tarea.completada = True
        self.repository.actualizar_tarea(tarea)

        return True

    def actualizar_tarea(
        self,
        id_tarea: int,
        nombre: str,
        completada: bool
    ) -> Tarea | None:

        tarea = self.obtener_tarea(id_tarea)

        if tarea is None:
            return None

        tarea.nombre = nombre
        tarea.completada = completada

        self.repository.actualizar_tarea(tarea)

        return tarea

    def actualizar_parcialmente_tarea(
        self,
        id_tarea: int,
        nombre: str | None,
        completada: bool | None
    ) -> Tarea | None:

        tarea = self.obtener_tarea(id_tarea)

        if tarea is None:
            return None

        if nombre is not None:
            tarea.nombre = nombre

        if completada is not None:
            tarea.completada = completada

        self.repository.actualizar_tarea(tarea)

        return tarea

    def eliminar_tarea(self, id_tarea: int) -> bool:
        return self.repository.eliminar_tarea(id_tarea)