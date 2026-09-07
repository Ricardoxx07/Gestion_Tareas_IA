from collections import Counter
from datetime import date, timedelta

from ai.proveedor_ia_interface import ProveedorIAInterface
from exceptions.planificacion_exceptions import RecomendacionIAInvalidaError
from models.reprogramacion import (
    CargaReprogramable,
    DiaDisponible,
    PropuestaReprogramacion,
    PropuestaReprogramacionIA,
    PropuestasReprogramacion,
)
from models.sobrecarga import CargaDiaria
from models.tarea import Tarea
from repository.tarea_repository_interface import TareaRepositoryInterface
from services.calculador_carga_diaria import CalculadorCargaDiaria


class ReprogramacionService:
    """Propone cambios de fecha; nunca persiste cambios automáticamente."""

    MAX_TAREAS_CONTEXTO_IA = 20
    PRIORIDAD_ORDEN = {"baja": 0, "media": 1, "alta": 2}

    def __init__(
        self,
        tarea_repository: TareaRepositoryInterface,
        proveedor_ia: ProveedorIAInterface,
    ):
        self.tarea_repository = tarea_repository
        self.proveedor_ia = proveedor_ia

    def proponer_reprogramaciones(
        self,
        usuario_id: int,
        fecha_inicio: date | None = None,
        dias: int = 7,
        max_tareas_por_dia: int = 3,
    ) -> PropuestasReprogramacion:
        inicio = fecha_inicio or date.today()
        fin = inicio + timedelta(days=dias - 1)
        tareas_pendientes = [
            tarea
            for tarea in self.tarea_repository.cargar_tareas(usuario_id)
            if not tarea.completada
        ]
        cargas = CalculadorCargaDiaria.calcular_cargas(
            tareas_pendientes,
            inicio,
            fin,
        )
        cargas_sobrecargadas = [
            carga
            for carga in cargas
            if len(carga.tareas) > max_tareas_por_dia
        ]
        cargas_reprogramables = self._obtener_cargas_reprogramables(
            cargas_sobrecargadas,
            inicio,
            max_tareas_por_dia,
        )
        dias_disponibles = self._obtener_dias_disponibles(
            cargas,
            cargas_sobrecargadas,
            inicio,
            fin,
            max_tareas_por_dia,
        )

        if not cargas_reprogramables or not dias_disponibles:
            return PropuestasReprogramacion(
                fecha_inicio=inicio,
                fecha_fin=fin,
                max_tareas_por_dia=max_tareas_por_dia,
                propuestas=[],
            )

        cargas_contexto = self._limitar_cargas_para_ia(cargas_reprogramables)
        propuestas = self.proveedor_ia.proponer_reprogramaciones(
            cargas_contexto,
            dias_disponibles,
        )
        propuestas = self._normalizar_propuestas(
            propuestas,
            cargas_contexto,
            dias_disponibles,
        )
        fechas_sugeridas = self._asignar_fechas_disponibles(
            propuestas,
            dias_disponibles,
        )

        fechas_actuales = {
            tarea.id: carga.fecha
            for carga in cargas_contexto
            for tarea in carga.tareas
        }
        return PropuestasReprogramacion(
            fecha_inicio=inicio,
            fecha_fin=fin,
            max_tareas_por_dia=max_tareas_por_dia,
            propuestas=[
                PropuestaReprogramacion(
                    tarea_id=propuesta.tarea_id,
                    fecha_actual=fechas_actuales[propuesta.tarea_id],
                    fecha_sugerida=fechas_sugeridas[propuesta.tarea_id],
                    motivo=propuesta.motivo,
                )
                for propuesta in propuestas
            ],
        )

    @staticmethod
    def _obtener_cargas_reprogramables(
        cargas: list[CargaDiaria],
        inicio: date,
        max_tareas_por_dia: int,
    ) -> list[CargaReprogramable]:
        cargas_reprogramables = []
        for carga in cargas:
            tareas_reprogramables = [
                tarea
                for tarea in carga.tareas
                if tarea.fecha_limite == carga.fecha and tarea.fecha_limite >= inicio
            ]
            max_reprogramaciones = min(
                len(carga.tareas) - max_tareas_por_dia,
                len(tareas_reprogramables),
            )
            if max_reprogramaciones:
                cargas_reprogramables.append(
                    CargaReprogramable(
                        fecha=carga.fecha,
                        tareas=tareas_reprogramables,
                        max_reprogramaciones=max_reprogramaciones,
                    )
                )
        return cargas_reprogramables

    def _limitar_cargas_para_ia(
        self,
        cargas: list[CargaReprogramable],
    ) -> list[CargaReprogramable]:
        """Distribuye un contexto acotado entre los días sobrecargados."""
        cantidad_total = sum(len(carga.tareas) for carga in cargas)
        if cantidad_total <= self.MAX_TAREAS_CONTEXTO_IA:
            return cargas

        tareas_ordenadas = {
            carga.fecha: sorted(
                carga.tareas,
                key=lambda tarea: (
                    self.PRIORIDAD_ORDEN[tarea.prioridad],
                    tarea.id or 0,
                ),
            )
            for carga in cargas
        }
        seleccionadas = {carga.fecha: [] for carga in cargas}
        restantes = self.MAX_TAREAS_CONTEXTO_IA

        for carga in cargas:
            if restantes and tareas_ordenadas[carga.fecha]:
                seleccionadas[carga.fecha].append(
                    tareas_ordenadas[carga.fecha].pop(0)
                )
                restantes -= 1

        for carga in cargas:
            while restantes and tareas_ordenadas[carga.fecha]:
                seleccionadas[carga.fecha].append(
                    tareas_ordenadas[carga.fecha].pop(0)
                )
                restantes -= 1

        return [
            CargaReprogramable(
                fecha=carga.fecha,
                tareas=seleccionadas[carga.fecha],
                max_reprogramaciones=min(
                    carga.max_reprogramaciones,
                    len(seleccionadas[carga.fecha]),
                ),
            )
            for carga in cargas
            if seleccionadas[carga.fecha]
        ]

    @staticmethod
    def _obtener_dias_disponibles(
        cargas: list[CargaDiaria],
        cargas_sobrecargadas: list[CargaDiaria],
        inicio: date,
        fin: date,
        max_tareas_por_dia: int,
    ) -> list[DiaDisponible]:
        cantidad_por_fecha = {
            carga.fecha: len(carga.tareas) for carga in cargas
        }
        fechas_sobrecargadas = {carga.fecha for carga in cargas_sobrecargadas}
        dias_disponibles = []

        for desplazamiento in range((fin - inicio).days + 1):
            fecha = inicio + timedelta(days=desplazamiento)
            if fecha in fechas_sobrecargadas:
                continue

            cupos = max_tareas_por_dia - cantidad_por_fecha.get(fecha, 0)
            if cupos > 0:
                dias_disponibles.append(DiaDisponible(fecha, cupos))

        return dias_disponibles

    @staticmethod
    def _normalizar_propuestas(
        propuestas: list[PropuestaReprogramacionIA],
        cargas: list[CargaReprogramable],
        dias_disponibles: list[DiaDisponible],
    ) -> list[PropuestaReprogramacionIA]:
        ids_permitidos = {
            tarea.id for carga in cargas for tarea in carga.tareas
        }
        ids_propuestos = [propuesta.tarea_id for propuesta in propuestas]
        fecha_origen_por_id = {
            tarea.id: carga.fecha for carga in cargas for tarea in carga.tareas
        }
        maximos_por_fecha_origen = {
            carga.fecha: carga.max_reprogramaciones for carga in cargas
        }
        if len(ids_propuestos) != len(set(ids_propuestos)):
            raise RecomendacionIAInvalidaError(
                "La IA propuso reprogramar una tarea más de una vez"
            )

        if not set(ids_propuestos).issubset(ids_permitidos):
            raise RecomendacionIAInvalidaError(
                "La IA propuso una tarea fuera del contexto permitido"
            )

        propuestas_limitadas = []
        cantidad_por_origen = Counter()
        for propuesta in propuestas:
            fecha_origen = fecha_origen_por_id[propuesta.tarea_id]
            if cantidad_por_origen[fecha_origen] >= maximos_por_fecha_origen[
                fecha_origen
            ]:
                continue

            propuestas_limitadas.append(propuesta)
            cantidad_por_origen[fecha_origen] += 1

        cupos_totales = sum(dia.cupos_disponibles for dia in dias_disponibles)
        return propuestas_limitadas[:cupos_totales]

    @staticmethod
    def _asignar_fechas_disponibles(
        propuestas: list[PropuestaReprogramacionIA],
        dias_disponibles: list[DiaDisponible],
    ) -> dict[int, date]:
        cupos_por_fecha = {
            dia.fecha: dia.cupos_disponibles for dia in dias_disponibles
        }
        fechas_sugeridas = {}

        for propuesta in propuestas:
            fecha_sugerida = next(
                fecha for fecha, cupos in cupos_por_fecha.items() if cupos > 0
            )
            cupos_por_fecha[fecha_sugerida] -= 1
            fechas_sugeridas[propuesta.tarea_id] = fecha_sugerida

        return fechas_sugeridas
