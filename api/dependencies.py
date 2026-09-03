from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database.database import SessionLocal
from models.usuario import Usuario
from repository.tarea_repository_db import TareaRepositoryDB
from repository.usuario_repository_db import UsuarioRepositoryDB
from services.tarea_service import TareaService
from services.usuario_service import UsuarioService
from security.security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def obtener_service() -> TareaService:
    db = SessionLocal()

    try:
        repository = TareaRepositoryDB(db)

        yield TareaService(repository)

    finally:
        db.close()


def obtener_usuario_service() -> UsuarioService:
    db = SessionLocal()

    try:
        repository = UsuarioRepositoryDB(db)
        yield UsuarioService(repository)
    finally:
        db.close()


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    service: UsuarioService = Depends(obtener_usuario_service)
) -> Usuario:
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if credenciales is None or credenciales.scheme.lower() != "bearer":
        raise credenciales_invalidas

    payload = decode_access_token(credenciales.credentials)
    subject = payload.get("sub") if payload else None

    try:
        id_usuario = int(subject)
    except (TypeError, ValueError):
        raise credenciales_invalidas

    usuario = service.obtener_usuario_por_id(id_usuario)

    if usuario is None:
        raise credenciales_invalidas

    return usuario
