from models.tarea import Tarea
from services.confirmacion_propuestas_service import ConfirmacionPropuestasService


class TareaServiceEspia:
    def __init__(self):
        self.tareas_recibidas: list[Tarea] | None = None
        self.usuario_id_recibido: int | None = None

    def agregar_tareas(self, tareas: list[Tarea], usuario_id: int) -> list[Tarea]:
        self.tareas_recibidas = tareas
        self.usuario_id_recibido = usuario_id
        for indice, tarea in enumerate(tareas, start=1):
            tarea.id = indice
            tarea.usuario_id = usuario_id
        return tareas


def test_confirma_solo_las_propuestas_seleccionadas_por_el_usuario():
    tarea_service = TareaServiceEspia()
    service = ConfirmacionPropuestasService(tarea_service)
    propuestas = [
        Tarea(nombre="Preparar informe", prioridad="alta"),
        Tarea(nombre="Enviar correo", prioridad="media"),
    ]

    resultado = service.confirmar_propuestas(propuestas, usuario_id=7)

    assert tarea_service.tareas_recibidas == propuestas
    assert tarea_service.usuario_id_recibido == 7
    assert [tarea.id for tarea in resultado] == [1, 2]
