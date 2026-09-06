from pydantic import BaseModel, ConfigDict, Field


class RecomendacionTareaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tarea_id: int
    orden: int = Field(ge=1)
    motivo: str


class PlanificacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recomendaciones: list[RecomendacionTareaResponse]
    resumen: str
