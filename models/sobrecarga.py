from dataclasses import dataclass
from datetime import date

from models.tarea import Tarea


@dataclass
class CargaDiaria:
    """Grupo de tareas que vencen en un mismo día del período analizado."""

    fecha: date
    tareas: list[Tarea]
    incluye_tareas_vencidas: bool = False


@dataclass
class ExplicacionSobrecarga:
    """Parte interpretativa aportada por el proveedor de IA."""

    fecha: date
    mensaje: str
    sugerencia: str


@dataclass
class AlertaSobrecarga:
    fecha: date
    cantidad_tareas: int
    tarea_ids: list[int]
    mensaje: str
    sugerencia: str


@dataclass
class AnalisisSobrecarga:
    fecha_inicio: date
    fecha_fin: date
    max_tareas_por_dia: int
    alertas: list[AlertaSobrecarga]
