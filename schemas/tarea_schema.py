
from pydantic import BaseModel, Field, field_validator


class TareaRequest(BaseModel):

    nombre: str = Field(
        min_length=1,
        max_length=255
    )

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:

        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre no puede estar vacío")

        return valor


class TareaResponse(BaseModel):

    id: int
    nombre: str
    completada: bool


class TareaUpdate(BaseModel):

    nombre: str = Field(
        min_length=1,
        max_length=255
    )

    completada: bool

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

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str | None) -> str | None:

        if valor is None:
            return None

        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre no puede estar vacío")

        return valor
