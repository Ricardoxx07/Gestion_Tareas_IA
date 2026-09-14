from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from schemas.sobrecarga_schema import DetectarSobrecargaRequest


class ProponerReprogramacionRequest(DetectarSobrecargaRequest):
    """Parámetros compartidos con el análisis de sobrecarga."""

    pass


class PropuestaReprogramacionIAResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tarea_id: int
    motivo: str = Field(min_length=1, max_length=500)


class PropuestasReprogramacionIAResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    propuestas: list[PropuestaReprogramacionIAResponse] = Field(max_length=8)


class PropuestaReprogramacionResponse(PropuestaReprogramacionIAResponse):
    fecha_actual: date
    fecha_sugerida: date


class PropuestasReprogramacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha_inicio: date
    fecha_fin: date
    max_tareas_por_dia: int
    propuestas: list[PropuestaReprogramacionResponse] = Field(max_length=8)
