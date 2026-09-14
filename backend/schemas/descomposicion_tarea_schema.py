"""Contratos HTTP e internos para descomponer una tarea grande."""

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class DescomponerTareaRequest(BaseModel):
    texto: str = Field(min_length=1, max_length=2_000)

    @field_validator("texto")
    @classmethod
    def validar_texto(cls, valor: str) -> str:
        texto = valor.strip()
        if not texto:
            raise ValueError("El texto no puede estar vacío")
        return texto


class SubtareaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    orden: int = Field(ge=1, le=8)
    nombre: str = Field(min_length=1, max_length=255)
    motivo: str = Field(min_length=12, max_length=500)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        nombre = valor.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacío")
        return nombre


class DescomposicionTareaIAResponse(BaseModel):
    """Contrato privado: el modelo solo propone las subtareas."""

    model_config = ConfigDict(extra="forbid")

    subtareas: list[SubtareaResponse] = Field(min_length=2, max_length=8)

    @model_validator(mode="after")
    def validar_ordenes_consecutivos(self):
        ordenes = [subtarea.orden for subtarea in self.subtareas]
        if ordenes != list(range(1, len(self.subtareas) + 1)):
            raise ValueError("Las subtareas deben tener órdenes consecutivos desde 1")
        return self


class DescomposicionTareaResponse(DescomposicionTareaIAResponse):
    tarea_original: str = Field(min_length=1, max_length=2_000)
