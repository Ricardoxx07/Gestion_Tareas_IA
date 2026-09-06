"""Contrato de confirmación explícita de propuestas generadas por IA."""

from pydantic import BaseModel, ConfigDict, Field

from schemas.tarea_schema import TareaRequest, TareaResponse


class ConfirmarPropuestasRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tareas: list[TareaRequest] = Field(min_length=1, max_length=8)


class PropuestasConfirmadasResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tareas_confirmadas: list[TareaResponse]
