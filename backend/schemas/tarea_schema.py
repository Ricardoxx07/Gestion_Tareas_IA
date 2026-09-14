
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


PrioridadTarea = Literal["baja", "media", "alta"]


class TareaBaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(
        min_length=1,
        max_length=255
    )
    fecha_limite: date | None = None
    prioridad: PrioridadTarea = "media"

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:

        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre no puede estar vacío")

        return valor


class TareaRequest(TareaBaseRequest):
    tarea_padre_id: int | None = Field(default=None, ge=1)


class SubtareaRequest(TareaBaseRequest):
    """Datos de una subtarea cuyo padre viene definido por la ruta."""

    pass


class TareaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    completada: bool
    fecha_limite: date | None = None
    prioridad: PrioridadTarea = "media"
    created_at: datetime | None = None
    tarea_padre_id: int | None = None


class TareaUpdate(BaseModel):

    nombre: str = Field(
        min_length=1,
        max_length=255
    )

    completada: bool
    fecha_limite: date | None = None
    prioridad: PrioridadTarea | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:

        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre no puede estar vacío")

        return valor


class TareaPatch(BaseModel):

    nombre: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    completada: bool | None = None
    fecha_limite: date | None = None
    prioridad: PrioridadTarea | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str | None) -> str | None:

        if valor is None:
            return None

        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre no puede estar vacío")

        return valor
