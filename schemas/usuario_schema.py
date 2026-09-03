import re

from pydantic import BaseModel, Field, field_validator


class UsuarioRegistro(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str) -> str:
        email = valor.strip().lower()

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("El email no tiene un formato válido")

        return email


class UsuarioResponse(BaseModel):
    id: int
    email: str


class UsuarioLogin(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str) -> str:
        return UsuarioRegistro.validar_email(valor)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
