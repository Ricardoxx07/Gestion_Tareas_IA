from datetime import date
import unicodedata

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from schemas.tarea_schema import PrioridadTarea


class PlanificarTextoRequest(BaseModel):
    texto: str = Field(min_length=1, max_length=2_000)

    @field_validator("texto")
    @classmethod
    def validar_texto(cls, valor: str) -> str:
        texto = valor.strip()

        if not texto:
            raise ValueError("El texto no puede estar vacío")

        return texto


class TareaPropuestaBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=255)
    prioridad_sugerida: PrioridadTarea
    motivo: str = Field(
        min_length=12,
        max_length=500,
        description=(
            "Explicación de la prioridad basada en el texto del usuario; "
            "no debe repetir el nombre de la tarea."
        ),
    )

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        nombre = valor.strip()

        if not nombre:
            raise ValueError("El nombre no puede estar vacío")

        return nombre

    @model_validator(mode="after")
    def validar_motivo(self):
        if self._normalizar(self.motivo) == self._normalizar(self.nombre):
            raise ValueError("El motivo debe explicar la propuesta, no repetir la tarea")

        return self

    @staticmethod
    def _normalizar(texto: str) -> str:
        return " ".join(
            "".join(
                caracter
                for caracter in unicodedata.normalize("NFD", texto.lower())
                if unicodedata.category(caracter) != "Mn"
            ).split()
        )


class TareaPropuestaResponse(TareaPropuestaBase):
    fecha_sugerida: date | None = None


class PropuestasTareasResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tareas_propuestas: list[TareaPropuestaResponse] = Field(max_length=8)


class TareaPropuestaIAResponse(TareaPropuestaBase):
    """Contrato interno: el modelo elige bloque, nunca una fecha."""

    bloque_temporal_id: int = Field(ge=1)
    orden_prioridad_usuario: int | None = Field(..., ge=1, le=10)


class PropuestasTareasIAResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tareas_propuestas: list[TareaPropuestaIAResponse] = Field(max_length=8)
