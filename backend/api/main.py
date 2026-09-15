import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers.auth import router as auth_router
from api.routers.ia import router as ia_router
from api.routers.tareas import router as tareas_router
from config.settings import settings
from exceptions.planificacion_exceptions import (
    ProveedorIAError,
    RecomendacionIAInvalidaError,
)
from exceptions.tarea_exceptions import TareaNoEncontradaError, PropuestaDesactualizadaError
from exceptions.usuario_exceptions import (
    CredencialesInvalidasError,
    UsuarioYaExisteError,
)


logger = logging.getLogger(__name__)


app = FastAPI(
    title="API Gestor de Tareas",
    description="API REST para gestionar tareas",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


app.include_router(tareas_router)
app.include_router(auth_router)
app.include_router(ia_router)


@app.get("/")
def inicio():
    return {
        "mensaje": "API del gestor de tareas funcionando"
    }

@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "service": "gestor-tareas-api"
    }

@app.exception_handler(TareaNoEncontradaError)
async def tarea_no_encontrada_handler(
    request: Request,
    exc: TareaNoEncontradaError
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc)
        }
    )


@app.exception_handler(PropuestaDesactualizadaError)
async def propuesta_desactualizada_handler(request: Request, exc: PropuestaDesactualizadaError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(UsuarioYaExisteError)
async def usuario_ya_existe_handler(
    request: Request,
    exc: UsuarioYaExisteError
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )


@app.exception_handler(CredencialesInvalidasError)
async def credenciales_invalidas_handler(
    request: Request,
    exc: CredencialesInvalidasError
):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.exception_handler(RecomendacionIAInvalidaError)
async def recomendacion_ia_invalida_handler(
    request: Request,
    exc: RecomendacionIAInvalidaError
):
    logger.warning(
        "Se rechazó una respuesta inválida del proveedor IA (%s)",
        type(exc).__name__,
    )
    return JSONResponse(
        status_code=502,
        content={"detail": "La respuesta de la IA no tiene un formato válido"},
    )


@app.exception_handler(ProveedorIAError)
async def proveedor_ia_error_handler(
    request: Request,
    exc: ProveedorIAError
):
    logger.warning(
        "El proveedor IA no estuvo disponible (%s)",
        type(exc).__name__,
    )
    return JSONResponse(
        status_code=503,
        content={
            "detail": "El proveedor de IA no está disponible. Intenta nuevamente más tarde"
        },
    )
