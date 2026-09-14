from datetime import date

from models.bloque_temporal import BloqueTemporal
from models.propuesta_tareas import PropuestasTareas, TareaPropuesta
from services.propuesta_tareas_service import PropuestaTareasService


class ProveedorIAEspia:
    def __init__(self, respuesta: PropuestasTareas):
        self.respuesta = respuesta
        self.texto_recibido: str | None = None
        self.fecha_recibida: date | None = None
        self.bloques_recibidos: list[BloqueTemporal] | None = None

    def proponer_tareas(
        self,
        texto: str,
        hoy: date,
        bloques_temporales: list[BloqueTemporal],
    ) -> PropuestasTareas:
        self.texto_recibido = texto
        self.fecha_recibida = hoy
        self.bloques_recibidos = bloques_temporales
        return self.respuesta


def test_devuelve_propuestas_sin_persistir_nada():
    proveedor = ProveedorIAEspia(
        PropuestasTareas(
            tareas_propuestas=[
                TareaPropuesta(
                    nombre="Preparar informe",
                    fecha_sugerida=date(2026, 9, 6),
                    prioridad_sugerida="alta",
                    motivo="El texto indica que es para mañana.",
                )
            ]
        )
    )
    service = PropuestaTareasService(proveedor)

    resultado = service.proponer_tareas(
        "Mañana preparar informe",
        hoy=date(2026, 9, 5),
    )

    assert proveedor.texto_recibido == "Mañana preparar informe"
    assert proveedor.fecha_recibida == date(2026, 9, 5)
    assert proveedor.bloques_recibidos == [
        BloqueTemporal(1, "Mañana preparar informe", date(2026, 9, 6))
    ]
    assert resultado.tareas_propuestas[0].nombre == "Preparar informe"


def test_corrige_prioridades_explicitas_sin_usar_el_orden_del_texto():
    proveedor = ProveedorIAEspia(
        PropuestasTareas(
            tareas_propuestas=[
                TareaPropuesta(
                    nombre="Llevar a mi papá al médico",
                    fecha_sugerida=date(2026, 9, 8),
                    prioridad_sugerida="baja",
                    motivo="El usuario la indicó como prioridad principal.",
                ),
                TareaPropuesta(
                    nombre="Terminar la presentación",
                    fecha_sugerida=date(2026, 9, 7),
                    prioridad_sugerida="baja",
                    motivo="Es una actividad laboral importante.",
                ),
                TareaPropuesta(
                    nombre="Llamar al proveedor",
                    fecha_sugerida=date(2026, 9, 7),
                    prioridad_sugerida="alta",
                    motivo="El usuario la indicó como prioridad principal.",
                ),
                TareaPropuesta(
                    nombre="Comprar alimentos para la semana",
                    fecha_sugerida=date(2026, 9, 8),
                    prioridad_sugerida="media",
                    motivo="Es necesaria para organizar la semana.",
                ),
                TareaPropuesta(
                    nombre="Salir a correr",
                    fecha_sugerida=date(2026, 9, 7),
                    prioridad_sugerida="alta",
                    motivo="Es importante para mantener la actividad física.",
                ),
            ]
        )
    )
    service = PropuestaTareasService(proveedor)

    resultado = service.proponer_tareas(
        "Este lunes terminar presentación y llamar al proveedor. Al día siguiente "
        "llevar a mi papá al médico y comprar alimentos. Lo más importante para mí "
        "es llevar a mi papá al médico, después terminar la presentación, luego "
        "llamar al proveedor, comprar los alimentos para la semana y por último "
        "salir a correr.",
        hoy=date(2026, 9, 5),
    )

    propuestas = {propuesta.nombre: propuesta for propuesta in resultado.tareas_propuestas}
    assert propuestas["Llevar a mi papá al médico"].prioridad_sugerida == "alta"
    assert propuestas["Terminar la presentación"].prioridad_sugerida == "alta"
    assert propuestas["Llamar al proveedor"].prioridad_sugerida == "media"
    assert propuestas["Comprar alimentos para la semana"].prioridad_sugerida == "media"
    assert propuestas["Salir a correr"].prioridad_sugerida == "baja"
    assert propuestas["Llevar a mi papá al médico"].motivo == (
        "El usuario la indicó como su prioridad principal."
    )
    assert propuestas["Llamar al proveedor"].motivo == (
        "El usuario la ubicó en el puesto 3 de sus prioridades."
    )
