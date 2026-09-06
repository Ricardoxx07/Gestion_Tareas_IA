from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from schemas.planificacion_schema import RecomendacionTareaResponse


class PlanDiaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha: date | None = None


class PlanDiaIAResponse(BaseModel):
    """Contrato que debe cumplir el proveedor de IA."""

    model_config = ConfigDict(extra="forbid")

    plan: list[RecomendacionTareaResponse] = Field(max_length=5)
    resumen: str = Field(min_length=1, max_length=500)


class PlanDiaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha: date
    plan: list[RecomendacionTareaResponse]
    resumen: str
