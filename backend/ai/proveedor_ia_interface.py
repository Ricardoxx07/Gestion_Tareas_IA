from abc import ABC, abstractmethod
from datetime import date

from models.bloque_temporal import BloqueTemporal
from models.descomposicion_tarea import DescomposicionTarea
from models.planificacion import Planificacion
from models.plan_dia import PlanDia
from models.propuesta_tareas import PropuestasTareas
from models.tarea import Tarea
from models.sobrecarga import CargaDiaria, ExplicacionSobrecarga
from models.reprogramacion import (
    CargaReprogramable,
    DiaDisponible,
    PropuestaReprogramacionIA,
)


class ProveedorIAInterface(ABC):
    """Contrato para proveedores de casos de uso de IA del gestor de tareas."""

    @abstractmethod
    def recomendar_tareas(
        self,
        tareas: list[Tarea],
        hoy: date
    ) -> Planificacion:
        pass

    @abstractmethod
    def planificar_dia(
        self,
        tareas: list[Tarea],
        fecha: date,
    ) -> PlanDia:
        """Ordena tareas reales para una fecha, sin persistir cambios."""
        pass

    @abstractmethod
    def explicar_sobrecargas(
        self,
        cargas: list[CargaDiaria],
    ) -> list[ExplicacionSobrecarga]:
        """Explica días sobrecargados calculados previamente por el backend."""
        pass

    @abstractmethod
    def proponer_reprogramaciones(
        self,
        cargas: list[CargaReprogramable],
        dias_disponibles: list[DiaDisponible],
    ) -> list[PropuestaReprogramacionIA]:
        """Propone cambios de fecha que el usuario debe confirmar después."""
        pass

    @abstractmethod
    def proponer_tareas(
        self,
        texto: str,
        hoy: date,
        bloques_temporales: list[BloqueTemporal],
    ) -> PropuestasTareas:
        """Interpreta texto libre, sin persistir ninguna tarea."""
        pass

    @abstractmethod
    def descomponer_tarea(self, texto: str) -> DescomposicionTarea:
        """Propone subtareas ordenadas, sin persistirlas."""
        pass
