from datetime import date, timedelta

from ai.proveedor_ia_interface import ProveedorIAInterface
from exceptions.planificacion_exceptions import RecomendacionIAInvalidaError
from models.plan_dia import PlanDia
from models.planificacion import RecomendacionTarea
from models.tarea import Tarea
from repository.tarea_repository_interface import TareaRepositoryInterface


class PlanDiaService:
    """Prepara un plan diario sin modificar tareas persistidas."""

    MAX_TAREAS_CONTEXTO = 10
    MAX_TAREAS_PLAN = 5
    DIAS_PROXIMOS = 7
    PRIORIDAD_ORDEN = {"alta": 0, "media": 1, "baja": 2}

    def __init__(
        self,
        tarea_repository: TareaRepositoryInterface,
        proveedor_ia: ProveedorIAInterface,
    ):
        self.tarea_repository = tarea_repository
        self.proveedor_ia = proveedor_ia

    def planificar_dia(
        self,
        usuario_id: int,
        fecha: date | None = None,
    ) -> PlanDia:
        fecha_plan = fecha or date.today()
        tareas_pendientes = [
            tarea
            for tarea in self.tarea_repository.cargar_tareas(usuario_id)
            if not tarea.completada
        ]

        if not tareas_pendientes:
            return PlanDia(
                fecha=fecha_plan,
                plan=[],
                resumen="No tienes tareas pendientes para planificar.",
            )

        tareas_relevantes = self._seleccionar_tareas_relevantes(
            tareas_pendientes,
            fecha_plan,
        )
        plan = self.proveedor_ia.planificar_dia(tareas_relevantes, fecha_plan)
        self._validar_plan(plan, tareas_relevantes)

        return PlanDia(
            fecha=fecha_plan,
            plan=plan.plan,
            resumen=plan.resumen,
        )

    def _seleccionar_tareas_relevantes(
        self,
        tareas: list[Tarea],
        fecha_plan: date,
    ) -> list[Tarea]:
        vencidas_o_del_dia = [
            tarea
            for tarea in tareas
            if tarea.fecha_limite is not None and tarea.fecha_limite <= fecha_plan
        ]
        if vencidas_o_del_dia:
            return self._ordenar_y_limitar(vencidas_o_del_dia)

        fecha_maxima = fecha_plan + timedelta(days=self.DIAS_PROXIMOS)
        proximas = [
            tarea
            for tarea in tareas
            if tarea.fecha_limite is not None
            and fecha_plan < tarea.fecha_limite <= fecha_maxima
        ]
        if proximas:
            return self._ordenar_y_limitar(proximas)

        sin_fecha = [tarea for tarea in tareas if tarea.fecha_limite is None]
        return self._ordenar_y_limitar(sin_fecha)

    def _ordenar_y_limitar(self, tareas: list[Tarea]) -> list[Tarea]:
        return sorted(
            tareas,
            key=lambda tarea: (
                tarea.fecha_limite is None,
                tarea.fecha_limite or date.max,
                self.PRIORIDAD_ORDEN[tarea.prioridad],
                tarea.id or 0,
            ),
        )[: self.MAX_TAREAS_CONTEXTO]

    def _validar_plan(self, plan: PlanDia, tareas_relevantes: list[Tarea]) -> None:
        if len(plan.plan) > self.MAX_TAREAS_PLAN:
            raise RecomendacionIAInvalidaError(
                "La IA devolvió más tareas de las permitidas para el plan diario"
            )

        ids_permitidos = {tarea.id for tarea in tareas_relevantes}
        ids_planificados = [recomendacion.tarea_id for recomendacion in plan.plan]
        ordenes = [recomendacion.orden for recomendacion in plan.plan]

        if len(ids_planificados) != len(set(ids_planificados)):
            raise RecomendacionIAInvalidaError(
                "La IA devolvió tareas duplicadas en el plan diario"
            )

        if not set(ids_planificados).issubset(ids_permitidos):
            raise RecomendacionIAInvalidaError(
                "La IA incluyó una tarea fuera del contexto permitido"
            )

        if ordenes != list(range(1, len(ordenes) + 1)):
            raise RecomendacionIAInvalidaError(
                "La IA devolvió un orden inválido para el plan diario"
            )
