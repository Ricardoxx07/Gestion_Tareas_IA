from datetime import date, timedelta

from ai.proveedor_ia_interface import ProveedorIAInterface
from models.bloque_temporal import BloqueTemporal
from models.descomposicion_tarea import DescomposicionTarea, Subtarea
from models.planificacion import Planificacion, RecomendacionTarea
from models.plan_dia import PlanDia
from models.propuesta_tareas import PropuestasTareas, TareaPropuesta
from models.tarea import Tarea
from models.sobrecarga import CargaDiaria, ExplicacionSobrecarga
from models.reprogramacion import (
    CargaReprogramable,
    DiaDisponible,
    PropuestaReprogramacionIA,
)


class ProveedorIAFalso(ProveedorIAInterface):
    """Proveedor determinista para desarrollar y probar sin una LLM real."""

    PRIORIDAD_ORDEN = {
        "alta": 0,
        "media": 1,
        "baja": 2,
    }

    def recomendar_tareas(
        self,
        tareas: list[Tarea],
        hoy: date
    ) -> Planificacion:
        tareas_ordenadas = sorted(
            tareas,
            key=lambda tarea: (
                self._urgencia_fecha(tarea.fecha_limite, hoy),
                self.PRIORIDAD_ORDEN[tarea.prioridad],
                tarea.id
            )
        )

        recomendaciones = [
            RecomendacionTarea(
                tarea_id=tarea.id,
                orden=indice,
                motivo=self._motivo(tarea, hoy)
            )
            for indice, tarea in enumerate(tareas_ordenadas[:3], start=1)
        ]

        return Planificacion(
            recomendaciones=recomendaciones,
            resumen=self._resumen(recomendaciones)
        )

    def planificar_dia(
        self,
        tareas: list[Tarea],
        fecha: date,
    ) -> PlanDia:
        tareas_ordenadas = sorted(
            tareas,
            key=lambda tarea: (
                self._urgencia_fecha(tarea.fecha_limite, fecha),
                self.PRIORIDAD_ORDEN[tarea.prioridad],
                tarea.id or 0,
            ),
        )
        plan = [
            RecomendacionTarea(
                tarea_id=tarea.id,
                orden=indice,
                motivo=self._motivo(tarea, fecha),
            )
            for indice, tarea in enumerate(tareas_ordenadas[:5], start=1)
        ]

        return PlanDia(
            fecha=fecha,
            plan=plan,
            resumen=(
                f"Se organizaron {len(plan)} tareas relevantes para el día."
                if plan
                else "No hay tareas relevantes para esa fecha."
            ),
        )

    def explicar_sobrecargas(
        self,
        cargas: list[CargaDiaria],
    ) -> list[ExplicacionSobrecarga]:
        return [
            ExplicacionSobrecarga(
                fecha=carga.fecha,
                mensaje=(
                    f"Tienes {len(carga.tareas)} tareas pendientes concentradas "
                    "en este día."
                ),
                sugerencia=(
                    "Prioriza las tareas con fecha límite más próxima y evalúa "
                    "adelantar las restantes."
                ),
            )
            for carga in cargas
        ]

    def proponer_reprogramaciones(
        self,
        cargas: list[CargaReprogramable],
        dias_disponibles: list[DiaDisponible],
    ) -> list[PropuestaReprogramacionIA]:
        cupos_por_fecha = {
            dia.fecha: dia.cupos_disponibles for dia in dias_disponibles
        }
        prioridades = {"baja": 0, "media": 1, "alta": 2}
        propuestas = []

        for carga in cargas:
            tareas_ordenadas = sorted(
                carga.tareas,
                key=lambda tarea: (prioridades[tarea.prioridad], tarea.id or 0),
            )
            for tarea in tareas_ordenadas[: carga.max_reprogramaciones]:
                fecha_sugerida = next(
                    (
                        fecha
                        for fecha, cupos in cupos_por_fecha.items()
                        if cupos > 0
                    ),
                    None,
                )
                if fecha_sugerida is None:
                    return propuestas

                cupos_por_fecha[fecha_sugerida] -= 1
                propuestas.append(
                    PropuestaReprogramacionIA(
                        tarea_id=tarea.id,
                        motivo=(
                            "Tiene menor prioridad relativa dentro del día "
                            "sobrecargado."
                        ),
                    )
                )

        return propuestas

    def proponer_tareas(
        self,
        texto: str,
        hoy: date,
        bloques_temporales: list[BloqueTemporal],
    ) -> PropuestasTareas:
        """Implementación simple y determinista para pruebas sin LLM."""
        texto_normalizado = texto.strip()
        es_para_manana = "mañana" in texto_normalizado.lower()
        es_opcional = "si me queda tiempo" in texto_normalizado.lower()

        return PropuestasTareas(
            tareas_propuestas=[
                TareaPropuesta(
                    nombre=texto_normalizado,
                    fecha_sugerida=(
                        bloques_temporales[0].fecha
                        if bloques_temporales and bloques_temporales[0].fecha
                        else (hoy + timedelta(days=1) if es_para_manana else None)
                    ),
                    prioridad_sugerida="baja" if es_opcional else "media",
                    motivo="Propuesta generada por el proveedor de pruebas."
                )
            ]
        )

    def descomponer_tarea(self, texto: str) -> DescomposicionTarea:
        """Respuesta estable para pruebas del caso de uso de descomposición."""
        return DescomposicionTarea(
            tarea_original=texto,
            subtareas=[
                Subtarea(
                    orden=1,
                    nombre="Definir el resultado esperado",
                    motivo="Aclara el alcance antes de comenzar el trabajo.",
                ),
                Subtarea(
                    orden=2,
                    nombre="Dividir el trabajo en pasos concretos",
                    motivo="Permite avanzar con acciones pequeñas y verificables.",
                ),
                Subtarea(
                    orden=3,
                    nombre="Revisar el resultado final",
                    motivo="Confirma que el objetivo inicial quedó cubierto.",
                ),
            ],
        )

    @staticmethod
    def _urgencia_fecha(fecha_limite: date | None, hoy: date) -> int:
        if fecha_limite is None:
            return 3
        if fecha_limite < hoy:
            return 0
        if fecha_limite == hoy:
            return 1
        return 2

    @staticmethod
    def _motivo(tarea: Tarea, hoy: date) -> str:
        if tarea.fecha_limite is not None and tarea.fecha_limite < hoy:
            return "Está vencida y requiere atención inmediata."
        if tarea.fecha_limite == hoy:
            return "Vence hoy y sigue pendiente."
        if tarea.prioridad == "alta":
            return "Tiene prioridad alta y conviene adelantarla."
        return "Está pendiente y ayuda a reducir tu carga de trabajo."

    @staticmethod
    def _resumen(recomendaciones: list[RecomendacionTarea]) -> str:
        if not recomendaciones:
            return "No tienes tareas pendientes para planificar."

        return (
            f"Se priorizaron {len(recomendaciones)} tareas pendientes "
            "según vencimiento y prioridad."
        )
