from models.tarea import Tarea
from services.tarea_service import TareaService


class ConfirmacionReprogramacionService:
    def __init__(self, tarea_service: TareaService):
        self.tarea_service = tarea_service

    def confirmar(self, cambios, usuario_id: int) -> list[Tarea]:
        return self.tarea_service.reprogramar_tareas(cambios, usuario_id)
