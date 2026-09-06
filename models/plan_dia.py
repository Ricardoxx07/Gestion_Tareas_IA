from dataclasses import dataclass
from datetime import date

from models.planificacion import RecomendacionTarea


@dataclass
class PlanDia:
    """Plan de solo lectura para una fecha concreta."""

    fecha: date
    plan: list[RecomendacionTarea]
    resumen: str
