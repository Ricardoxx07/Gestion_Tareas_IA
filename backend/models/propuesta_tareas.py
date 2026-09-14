from dataclasses import dataclass
from datetime import date


@dataclass
class TareaPropuesta:
    """Una sugerencia que aún no representa una tarea persistida."""

    nombre: str
    fecha_sugerida: date | None
    prioridad_sugerida: str
    motivo: str


@dataclass
class PropuestasTareas:
    tareas_propuestas: list[TareaPropuesta]
