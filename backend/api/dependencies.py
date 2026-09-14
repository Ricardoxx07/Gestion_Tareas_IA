from ai.proveedor_ia_falso import ProveedorIAFalso
from ai.proveedor_ia_interface import ProveedorIAInterface
from ai.proveedor_groq import ProveedorGroq
from ai.proveedor_ollama import ProveedorOllama
from config.settings import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database.database import SessionLocal
from models.usuario import Usuario
from repository.tarea_repository_db import TareaRepositoryDB
from repository.usuario_repository_db import UsuarioRepositoryDB
from services.tarea_service import TareaService
from services.planificacion_service import PlanificacionService
from services.plan_dia_service import PlanDiaService
from services.sobrecarga_service import SobrecargaService
from services.reprogramacion_service import ReprogramacionService
from services.confirmacion_reprogramacion_service import ConfirmacionReprogramacionService
from services.descomposicion_tarea_service import DescomposicionTareaService
from services.confirmacion_propuestas_service import ConfirmacionPropuestasService
from services.propuesta_tareas_service import PropuestaTareasService
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


def obtener_planificacion_service() -> PlanificacionService:
    db = SessionLocal()

    try:
        tarea_repository = TareaRepositoryDB(db)
        proveedor_ia = obtener_proveedor_ia()
        yield PlanificacionService(tarea_repository, proveedor_ia)
    finally:
        db.close()


def obtener_plan_dia_service() -> PlanDiaService:
    db = SessionLocal()

    try:
        tarea_repository = TareaRepositoryDB(db)
        proveedor_ia = obtener_proveedor_ia()
        yield PlanDiaService(tarea_repository, proveedor_ia)
    finally:
        db.close()


def obtener_sobrecarga_service() -> SobrecargaService:
    db = SessionLocal()

    try:
        tarea_repository = TareaRepositoryDB(db)
        proveedor_ia = obtener_proveedor_ia()
        yield SobrecargaService(tarea_repository, proveedor_ia)
    finally:
        db.close()


def obtener_reprogramacion_service() -> ReprogramacionService:
    db = SessionLocal()

    try:
        tarea_repository = TareaRepositoryDB(db)
        proveedor_ia = obtener_proveedor_ia()
        yield ReprogramacionService(tarea_repository, proveedor_ia)
    finally:
        db.close()


def obtener_confirmacion_reprogramacion_service() -> ConfirmacionReprogramacionService:
    db = SessionLocal()
    try:
        yield ConfirmacionReprogramacionService(TareaService(TareaRepositoryDB(db)))
    finally:
        db.close()


def obtener_proveedor_ia() -> ProveedorIAInterface:
    """Construye el proveedor configurado sin exponerlo al router o service."""
    if settings.IA_PROVIDER == "ollama":
        return ProveedorOllama(
            model=settings.OLLAMA_MODEL,
            url_base=settings.OLLAMA_URL,
            timeout_seconds=settings.OLLAMA_TIMEOUT_SECONDS,
            max_tokens=settings.OLLAMA_MAX_TOKENS,
        )

    if settings.IA_PROVIDER == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY es obligatoria cuando IA_PROVIDER=groq")

        return ProveedorGroq(
            api_key=settings.GROQ_API_KEY,
            modelo=settings.GROQ_MODEL,
            timeout=settings.GROQ_TIMEOUT_SECONDS,
            max_tokens=settings.GROQ_MAX_TOKENS,
        )

    return ProveedorIAFalso()


def obtener_propuesta_tareas_service() -> PropuestaTareasService:
    """Este caso de uso no requiere repositorio ni abre una sesión de base de datos."""
    return PropuestaTareasService(obtener_proveedor_ia())


def obtener_descomposicion_tarea_service() -> DescomposicionTareaService:
    """Este caso de uso genera propuestas y no requiere acceso a PostgreSQL."""
    return DescomposicionTareaService(obtener_proveedor_ia())


def obtener_confirmacion_propuestas_service() -> ConfirmacionPropuestasService:
    db = SessionLocal()

    try:
        tarea_service = TareaService(TareaRepositoryDB(db))
        yield ConfirmacionPropuestasService(tarea_service)
    finally:
        db.close()
