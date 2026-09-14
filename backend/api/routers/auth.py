from fastapi import APIRouter, Depends, status

from api.dependencies import obtener_usuario_actual, obtener_usuario_service
from models.usuario import Usuario
from schemas.usuario_schema import (
    TokenResponse,
    UsuarioLogin,
    UsuarioRegistro,
    UsuarioResponse,
)
from security.security import create_access_token
from services.usuario_service import UsuarioService


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/registro",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED
)
def registrar_usuario(
    datos: UsuarioRegistro,
    service: UsuarioService = Depends(obtener_usuario_service)
):
    return service.registrar_usuario(datos.email, datos.password)


@router.post("/login", response_model=TokenResponse)
def iniciar_sesion(
    datos: UsuarioLogin,
    service: UsuarioService = Depends(obtener_usuario_service)
):
    usuario = service.autenticar_usuario(datos.email, datos.password)

    return TokenResponse(
        access_token=create_access_token({"sub": str(usuario.id)})
    )


@router.get("/me", response_model=UsuarioResponse)
def obtener_mi_usuario(
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    return usuario
