"""Confirma propuestas elegidas por el usuario y delega su persistencia."""

from models.tarea import Tarea
from services.tarea_service import TareaService


class ConfirmacionPropuestasService:
    def __init__(self, tarea_service: TareaService):
        self.tarea_service = tarea_service

    def confirmar_propuestas(
        self,
        tareas: list[Tarea],
        usuario_id: int,
    ) -> list[Tarea]:
        return self.tarea_service.agregar_tareas(tareas, usuario_id)
