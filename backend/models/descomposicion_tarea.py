"""Modelos de dominio para propuestas de subtareas no persistidas."""

from dataclasses import dataclass


@dataclass
class Subtarea:
    orden: int
    nombre: str
    motivo: str


@dataclass
class DescomposicionTarea:
    tarea_original: str
    subtareas: list[Subtarea]
