from datetime import date, timedelta

from ai.proveedor_ia_interface import ProveedorIAInterface
from exceptions.planificacion_exceptions import RecomendacionIAInvalidaError
from models.sobrecarga import (
    AlertaSobrecarga,
    AnalisisSobrecarga,
    CargaDiaria,
    ExplicacionSobrecarga,
)
from repository.tarea_repository_interface import TareaRepositoryInterface
from services.calculador_carga_diaria import CalculadorCargaDiaria


class SobrecargaService:
    """Detecta carga excesiva con reglas deterministas y la IA solo la explica."""

    def __init__(
        self,
        tarea_repository: TareaRepositoryInterface,
        proveedor_ia: ProveedorIAInterface,
    ):
        self.tarea_repository = tarea_repository
        self.proveedor_ia = proveedor_ia

    def detectar_sobrecarga(
        self,
        usuario_id: int,
        fecha_inicio: date | None = None,
        dias: int = 7,
        max_tareas_por_dia: int = 3,
    ) -> AnalisisSobrecarga:
        inicio = fecha_inicio or date.today()
        fin = inicio + timedelta(days=dias - 1)
        tareas_pendientes = [
            tarea
            for tarea in self.tarea_repository.cargar_tareas(usuario_id)
            if not tarea.completada
        ]
        cargas = CalculadorCargaDiaria.obtener_cargas_sobrecargadas(
            tareas_pendientes,
            inicio,
            fin,
            max_tareas_por_dia,
        )

        if not cargas:
            return AnalisisSobrecarga(
                fecha_inicio=inicio,
                fecha_fin=fin,
                max_tareas_por_dia=max_tareas_por_dia,
                alertas=[],
            )

        explicaciones = self.proveedor_ia.explicar_sobrecargas(cargas)
        self._validar_explicaciones(explicaciones, cargas)
        explicaciones_por_fecha = {
            explicacion.fecha: explicacion for explicacion in explicaciones
        }

        return AnalisisSobrecarga(
            fecha_inicio=inicio,
            fecha_fin=fin,
            max_tareas_por_dia=max_tareas_por_dia,
            alertas=[
                AlertaSobrecarga(
                    fecha=carga.fecha,
                    cantidad_tareas=len(carga.tareas),
                    tarea_ids=[tarea.id for tarea in carga.tareas],
                    mensaje=explicaciones_por_fecha[carga.fecha].mensaje,
                    sugerencia=explicaciones_por_fecha[carga.fecha].sugerencia,
                )
                for carga in cargas
            ],
        )

    @staticmethod
    def _validar_explicaciones(
        explicaciones: list[ExplicacionSobrecarga],
        cargas: list[CargaDiaria],
    ) -> None:
        fechas_esperadas = {carga.fecha for carga in cargas}
        fechas_recibidas = [explicacion.fecha for explicacion in explicaciones]

        if len(fechas_recibidas) != len(set(fechas_recibidas)):
            raise RecomendacionIAInvalidaError(
                "La IA devolvió alertas duplicadas de sobrecarga"
            )

        if set(fechas_recibidas) != fechas_esperadas:
            raise RecomendacionIAInvalidaError(
                "La IA devolvió alertas fuera del contexto de sobrecarga"
            )
