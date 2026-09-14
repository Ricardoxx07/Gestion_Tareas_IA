from datetime import date

from ai.proveedor_ia_interface import ProveedorIAInterface
from exceptions.planificacion_exceptions import RecomendacionIAInvalidaError
from models.planificacion import Planificacion
from models.tarea import Tarea
from repository.tarea_repository_interface import TareaRepositoryInterface


class PlanificacionService:

    MAX_TAREAS_CONTEXTO = 20
    MAX_RECOMENDACIONES = 3
    PRIORIDAD_ORDEN = {"alta": 0, "media": 1, "baja": 2}

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

        tareas_contexto = self._ordenar_y_limitar_tareas(tareas_pendientes)
        planificacion = self.proveedor_ia.recomendar_tareas(
            tareas_contexto,
            fecha_actual
        )
        self._validar_recomendaciones(planificacion, tareas_contexto)

        return planificacion

    def _ordenar_y_limitar_tareas(
        self,
        tareas: list[Tarea],
    ) -> list[Tarea]:
        """Selecciona contexto relevante de forma determinista antes de usar IA."""
        return sorted(
            tareas,
            key=lambda tarea: (
                tarea.fecha_limite is None,
                tarea.fecha_limite or date.max,
                self.PRIORIDAD_ORDEN[tarea.prioridad],
                tarea.id or 0,
            ),
        )[: self.MAX_TAREAS_CONTEXTO]

    def _validar_recomendaciones(self, planificacion, tareas_pendientes) -> None:
        if len(planificacion.recomendaciones) > self.MAX_RECOMENDACIONES:
            raise RecomendacionIAInvalidaError(
                "La IA devolvió más recomendaciones de las permitidas"
            )

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
