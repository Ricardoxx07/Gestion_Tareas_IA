from datetime import date

from services.confirmacion_reprogramacion_service import (
    ConfirmacionReprogramacionService,
)


class TareaServiceEspia:
    def __init__(self):
        self.cambios_recibidos = None
        self.usuario_id_recibido = None

    def reprogramar_tareas(self, cambios, usuario_id):
        self.cambios_recibidos = cambios
        self.usuario_id_recibido = usuario_id
        return []


def test_confirma_solo_las_reprogramaciones_seleccionadas():
    tarea_service = TareaServiceEspia()
    service = ConfirmacionReprogramacionService(tarea_service)
    cambios = [(10, date(2026, 9, 8), date(2026, 9, 6))]

    resultado = service.confirmar(cambios, usuario_id=7)

    assert resultado == []
    assert tarea_service.cambios_recibidos == cambios
    assert tarea_service.usuario_id_recibido == 7
