from models.tarea import Tarea
from repository.tarea_repository_interface import TareaRepositoryInterface
from exceptions.tarea_exceptions import TareaNoEncontradaError


class TareaService:

    def __init__(self, repository: TareaRepositoryInterface):
        self.repository = repository

    def agregar_tarea(self, nombre: str, usuario_id: int) -> Tarea:
        nueva_tarea = Tarea(nombre=nombre, usuario_id=usuario_id)

        return self.repository.guardar_tarea(nueva_tarea)

    def listar_tareas(self, usuario_id: int) -> list[Tarea]:
        return self.repository.cargar_tareas(usuario_id)

    def obtener_tarea(self, id_tarea: int, usuario_id: int) -> Tarea | None:
        return self.repository.obtener_tarea(id_tarea, usuario_id)

    def obtener_tarea_o_error(self, id_tarea: int, usuario_id: int) -> Tarea:
        tarea = self.repository.obtener_tarea(id_tarea, usuario_id)

        if tarea is None:
            raise TareaNoEncontradaError(
                f"Tarea con id {id_tarea} no encontrada"
            )

        return tarea

    def completar_tarea(self, id_tarea: int, usuario_id: int) -> bool:
        tarea = self.obtener_tarea_o_error(id_tarea, usuario_id)

        tarea.completada = True
        self.repository.actualizar_tarea(tarea)

        return True

    def actualizar_tarea(
        self,
        id_tarea: int,
        usuario_id: int,
        nombre: str,
        completada: bool
    ) -> Tarea:

        tarea = self.obtener_tarea_o_error(id_tarea, usuario_id)

        tarea.nombre = nombre
        tarea.completada = completada

        self.repository.actualizar_tarea(tarea)

        return tarea

    def actualizar_parcialmente_tarea(
        self,
        id_tarea: int,
        usuario_id: int,
        nombre: str | None,
        completada: bool | None
    ) -> Tarea:

        tarea = self.obtener_tarea_o_error(id_tarea, usuario_id)

        if nombre is not None:
            tarea.nombre = nombre

        if completada is not None:
            tarea.completada = completada

        self.repository.actualizar_tarea(tarea)

        return tarea

    def eliminar_tarea(self, id_tarea: int, usuario_id: int) -> bool:
        tarea = self.obtener_tarea_o_error(id_tarea, usuario_id)

        self.repository.eliminar_tarea(tarea.id, usuario_id)

        return True
