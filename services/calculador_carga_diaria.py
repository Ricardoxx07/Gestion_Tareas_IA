from collections import defaultdict
from datetime import date

from models.sobrecarga import CargaDiaria
from models.tarea import Tarea


class CalculadorCargaDiaria:
    """Reglas deterministas para agrupar carga pendiente por fecha."""

    @staticmethod
    def calcular_cargas(
        tareas: list[Tarea],
        inicio: date,
        fin: date,
    ) -> list[CargaDiaria]:
        tareas_por_fecha: dict[date, list[Tarea]] = defaultdict(list)
        fechas_con_vencidas: set[date] = set()

        for tarea in tareas:
            if tarea.fecha_limite is None or tarea.fecha_limite > fin:
                continue

            fecha_carga = tarea.fecha_limite
            if tarea.fecha_limite < inicio:
                fecha_carga = inicio
                fechas_con_vencidas.add(inicio)

            tareas_por_fecha[fecha_carga].append(tarea)

        return [
            CargaDiaria(
                fecha=fecha,
                tareas=sorted(tareas_dia, key=lambda tarea: tarea.id or 0),
                incluye_tareas_vencidas=fecha in fechas_con_vencidas,
            )
            for fecha, tareas_dia in sorted(tareas_por_fecha.items())
        ]

    @classmethod
    def obtener_cargas_sobrecargadas(
        cls,
        tareas: list[Tarea],
        inicio: date,
        fin: date,
        max_tareas_por_dia: int,
    ) -> list[CargaDiaria]:
        return [
            carga
            for carga in cls.calcular_cargas(tareas, inicio, fin)
            if len(carga.tareas) > max_tareas_por_dia
        ]
