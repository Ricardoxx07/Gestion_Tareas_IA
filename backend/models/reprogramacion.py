from dataclasses import dataclass
from datetime import date

from models.tarea import Tarea


@dataclass
class CargaReprogramable:
    """Tareas de un día sobrecargado que pueden evaluarse para mover."""

    fecha: date
    tareas: list[Tarea]
    max_reprogramaciones: int


@dataclass
class DiaDisponible:
    fecha: date
    cupos_disponibles: int


@dataclass
class PropuestaReprogramacionIA:
    tarea_id: int
    motivo: str


@dataclass
class PropuestaReprogramacion(PropuestaReprogramacionIA):
    fecha_actual: date
    fecha_sugerida: date


@dataclass
class PropuestasReprogramacion:
    fecha_inicio: date
    fecha_fin: date
    max_tareas_por_dia: int
    propuestas: list[PropuestaReprogramacion]
