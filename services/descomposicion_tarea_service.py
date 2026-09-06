"""Caso de uso para descomponer trabajo grande sin persistir subtareas."""

from ai.proveedor_ia_interface import ProveedorIAInterface
from models.descomposicion_tarea import DescomposicionTarea


class DescomposicionTareaService:
    def __init__(self, proveedor_ia: ProveedorIAInterface):
        self.proveedor_ia = proveedor_ia

    def descomponer_tarea(self, texto: str) -> DescomposicionTarea:
        descomposicion = self.proveedor_ia.descomponer_tarea(texto)
        return DescomposicionTarea(
            tarea_original=texto,
            subtareas=descomposicion.subtareas,
        )
