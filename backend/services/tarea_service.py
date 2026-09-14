from models.tarea import Tarea
from repository.tarea_repository_interface import TareaRepositoryInterface
from exceptions.tarea_exceptions import TareaNoEncontradaError
from exceptions.tarea_exceptions import PropuestaDesactualizadaError


class TareaService:

    def __init__(self, repository: TareaRepositoryInterface):
        self.repository = repository

    def agregar_tarea(
        self,
        nombre: str,
        usuario_id: int,
        fecha_limite=None,
        prioridad: str = "media",
        tarea_padre_id: int | None = None,
    ) -> Tarea:
        if tarea_padre_id is not None:
            tarea_padre = self.repository.obtener_tarea(tarea_padre_id, usuario_id)
            if tarea_padre is None:
                raise TareaNoEncontradaError(
                    f"Tarea padre con id {tarea_padre_id} no encontrada"
                )

        nueva_tarea = Tarea(
            nombre=nombre,
            usuario_id=usuario_id,
            fecha_limite=fecha_limite,
            prioridad=prioridad,
            tarea_padre_id=tarea_padre_id,
        )

        return self.repository.guardar_tarea(nueva_tarea)

    def listar_tareas(self, usuario_id: int) -> list[Tarea]:
        return self.repository.cargar_tareas(usuario_id)

    def agregar_tareas(self, tareas: list[Tarea], usuario_id: int) -> list[Tarea]:
        for tarea in tareas:
            if tarea.tarea_padre_id is not None:
                tarea_padre = self.repository.obtener_tarea(
                    tarea.tarea_padre_id,
                    usuario_id,
                )
                if tarea_padre is None:
                    raise TareaNoEncontradaError(
                        f"Tarea padre con id {tarea.tarea_padre_id} no encontrada"
                    )

        tareas_para_guardar = [
            Tarea(
                nombre=tarea.nombre,
                usuario_id=usuario_id,
                fecha_limite=tarea.fecha_limite,
                prioridad=tarea.prioridad,
                tarea_padre_id=tarea.tarea_padre_id,
            )
            for tarea in tareas
        ]
        return self.repository.guardar_tareas(tareas_para_guardar)

    def listar_subtareas(self, tarea_padre_id: int, usuario_id: int) -> list[Tarea]:
        self.obtener_tarea_o_error(tarea_padre_id, usuario_id)
        return self.repository.cargar_subtareas(tarea_padre_id, usuario_id)

    def obtener_subtarea_o_error(
        self,
        tarea_padre_id: int,
        id_subtarea: int,
        usuario_id: int,
    ) -> Tarea:
        subtarea = self.obtener_tarea_o_error(id_subtarea, usuario_id)

        if subtarea.tarea_padre_id != tarea_padre_id:
            raise TareaNoEncontradaError(
                f"Subtarea con id {id_subtarea} no encontrada para la tarea padre"
            )

        return subtarea

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
        completada: bool,
        fecha_limite=None,
        prioridad: str | None = None,
        actualizar_fecha_limite: bool = False
    ) -> Tarea:

        tarea = self.obtener_tarea_o_error(id_tarea, usuario_id)

        tarea.nombre = nombre
        tarea.completada = completada

        if actualizar_fecha_limite:
            tarea.fecha_limite = fecha_limite

        if prioridad is not None:
            tarea.prioridad = prioridad

        self.repository.actualizar_tarea(tarea)

        return tarea

    def actualizar_parcialmente_tarea(
        self,
        id_tarea: int,
        usuario_id: int,
        nombre: str | None,
        completada: bool | None,
        fecha_limite=None,
        prioridad: str | None = None,
        actualizar_fecha_limite: bool = False
    ) -> Tarea:

        tarea = self.obtener_tarea_o_error(id_tarea, usuario_id)

        if nombre is not None:
            tarea.nombre = nombre

        if completada is not None:
            tarea.completada = completada

        if actualizar_fecha_limite:
            tarea.fecha_limite = fecha_limite

        if prioridad is not None:
            tarea.prioridad = prioridad

        self.repository.actualizar_tarea(tarea)

        return tarea

    def eliminar_tarea(self, id_tarea: int, usuario_id: int) -> bool:
        tarea = self.obtener_tarea_o_error(id_tarea, usuario_id)

        self.repository.eliminar_tarea(tarea.id, usuario_id)

        return True

    def reprogramar_tareas(
        self,
        cambios: list[tuple[int, object, object]],
        usuario_id: int,
    ) -> list[Tarea]:
        tareas = []
        for tarea_id, fecha_actual, fecha_sugerida in cambios:
            tarea = self.obtener_tarea_o_error(tarea_id, usuario_id)
            if tarea.fecha_limite != fecha_actual:
                raise PropuestaDesactualizadaError(
                    f"La tarea con id {tarea_id} cambió desde la propuesta"
                )
            tarea.fecha_limite = fecha_sugerida
            tareas.append(tarea)
        return self.repository.actualizar_tareas(tareas)
