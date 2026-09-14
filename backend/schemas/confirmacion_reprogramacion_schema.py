from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from schemas.tarea_schema import TareaResponse


class ReprogramacionConfirmarItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tarea_id: int = Field(ge=1)
    fecha_actual: date
    fecha_sugerida: date


class ConfirmarReprogramacionesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reprogramaciones: list[ReprogramacionConfirmarItem] = Field(min_length=1, max_length=8)


class ReprogramacionesConfirmadasResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tareas_actualizadas: list[TareaResponse]
