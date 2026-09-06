from dataclasses import dataclass


@dataclass
class RecomendacionTarea:
    tarea_id: int
    orden: int
    motivo: str


@dataclass
class Planificacion:
    recomendaciones: list[RecomendacionTarea]
    resumen: str
