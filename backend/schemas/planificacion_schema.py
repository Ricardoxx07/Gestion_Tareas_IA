from pydantic import BaseModel, ConfigDict, Field


class RecomendacionTareaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tarea_id: int
    orden: int = Field(ge=1)
    motivo: str = Field(min_length=1, max_length=500)


class PlanificacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recomendaciones: list[RecomendacionTareaResponse] = Field(max_length=3)
    resumen: str = Field(min_length=1, max_length=500)
