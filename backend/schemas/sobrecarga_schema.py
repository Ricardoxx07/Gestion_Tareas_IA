from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class DetectarSobrecargaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha_inicio: date | None = None
    dias: int = Field(default=7, ge=1, le=31)
    max_tareas_por_dia: int = Field(default=3, ge=1, le=20)


class ExplicacionSobrecargaIAResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha: date
    mensaje: str = Field(min_length=1, max_length=500)
    sugerencia: str = Field(min_length=1, max_length=500)


class SobrecargasIAResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alertas: list[ExplicacionSobrecargaIAResponse] = Field(max_length=31)


class AlertaSobrecargaResponse(ExplicacionSobrecargaIAResponse):
    cantidad_tareas: int = Field(ge=1)
    tarea_ids: list[int] = Field(min_length=1)


class AnalisisSobrecargaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha_inicio: date
    fecha_fin: date
    max_tareas_por_dia: int
    alertas: list[AlertaSobrecargaResponse] = Field(max_length=31)
