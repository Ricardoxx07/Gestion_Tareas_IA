from datetime import date

from ai.proveedor_ia_interface import ProveedorIAInterface
from exceptions.planificacion_exceptions import RecomendacionIAInvalidaError
from models.planificacion import Planificacion
from repository.tarea_repository_interface import TareaRepositoryInterface


class PlanificacionService:

    def __init__(
        self,
        tarea_repository: TareaRepositoryInterface,
        proveedor_ia: ProveedorIAInterface
    ):
        self.tarea_repository = tarea_repository
        self.proveedor_ia = proveedor_ia

    def recomendar_tareas(
        self,
        usuario_id: int,
        hoy: date | None = None
    ) -> Planificacion:
        fecha_actual = hoy or date.today()
        tareas_pendientes = [
            tarea
            for tarea in self.tarea_repository.cargar_tareas(usuario_id)
            if not tarea.completada
        ]

        if not tareas_pendientes:
            return Planificacion(
                recomendaciones=[],
                resumen="No tienes tareas pendientes para planificar."
            )

        planificacion = self.proveedor_ia.recomendar_tareas(
            tareas_pendientes,
            fecha_actual
        )
        self._validar_recomendaciones(planificacion, tareas_pendientes)

        return planificacion

    @staticmethod
    def _validar_recomendaciones(planificacion, tareas_pendientes) -> None:
        ids_permitidos = {tarea.id for tarea in tareas_pendientes}
        ids_recomendados = [
            recomendacion.tarea_id
            for recomendacion in planificacion.recomendaciones
        ]

        if len(ids_recomendados) != len(set(ids_recomendados)):
            raise RecomendacionIAInvalidaError(
                "La IA devolvió tareas duplicadas"
            )

        if not set(ids_recomendados).issubset(ids_permitidos):
            raise RecomendacionIAInvalidaError(
                "La IA recomendó una tarea fuera del contexto permitido"
            )
