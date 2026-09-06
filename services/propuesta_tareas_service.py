from datetime import date

from ai.proveedor_ia_interface import ProveedorIAInterface
from models.propuesta_tareas import PropuestasTareas, TareaPropuesta
from services.interpretador_prioridad import InterpretadorPrioridad, PrioridadExplicita
from services.interpretador_temporal import InterpretadorTemporal


class PropuestaTareasService:
    """Orquesta propuestas de IA sin acceso a persistencia."""

    def __init__(
        self,
        proveedor_ia: ProveedorIAInterface,
        interpretador_temporal: InterpretadorTemporal | None = None,
        interpretador_prioridad: InterpretadorPrioridad | None = None,
    ):
        self.proveedor_ia = proveedor_ia
        self.interpretador_temporal = interpretador_temporal or InterpretadorTemporal()
        self.interpretador_prioridad = interpretador_prioridad or InterpretadorPrioridad()

    def proponer_tareas(
        self,
        texto: str,
        hoy: date | None = None,
    ) -> PropuestasTareas:
        fecha_actual = hoy or date.today()
        bloques_temporales = self.interpretador_temporal.extraer_bloques(
            texto,
            fecha_actual,
        )
        propuestas = self.proveedor_ia.proponer_tareas(
            texto,
            fecha_actual,
            bloques_temporales,
        )
        prioridades_explicitas = self.interpretador_prioridad.interpretar(
            texto,
            [propuesta.nombre for propuesta in propuestas.tareas_propuestas],
        )

        return PropuestasTareas(
            tareas_propuestas=[
                self._aplicar_prioridad_explicita(
                    propuesta,
                    prioridades_explicitas.get(propuesta.nombre),
                )
                for propuesta in propuestas.tareas_propuestas
            ]
        )

    @staticmethod
    def _aplicar_prioridad_explicita(
        propuesta: TareaPropuesta,
        prioridad_explicita: PrioridadExplicita | None,
    ) -> TareaPropuesta:
        if prioridad_explicita is None:
            return propuesta

        orden = prioridad_explicita.orden
        total = prioridad_explicita.total

        if orden == 1 or (total >= 4 and orden == 2):
            prioridad = "alta"
        elif orden == total and total > 1:
            prioridad = "baja"
        else:
            prioridad = "media"

        if orden == 1:
            motivo = "El usuario la indicó como su prioridad principal."
        elif orden == total:
            motivo = "El usuario la dejó en último lugar de prioridad."
        else:
            motivo = f"El usuario la ubicó en el puesto {orden} de sus prioridades."

        return TareaPropuesta(
            nombre=propuesta.nombre,
            fecha_sugerida=propuesta.fecha_sugerida,
            prioridad_sugerida=prioridad,
            motivo=motivo,
        )
