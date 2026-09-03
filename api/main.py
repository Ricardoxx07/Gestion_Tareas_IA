from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.routers.auth import router as auth_router
from api.routers.tareas import router as tareas_router
from exceptions.tarea_exceptions import TareaNoEncontradaError
from exceptions.usuario_exceptions import (
    CredencialesInvalidasError,
    UsuarioYaExisteError,
)


app = FastAPI(
    title="API Gestor de Tareas",
    description="API REST para gestionar tareas",
    version="1.0.0"
)


app.include_router(tareas_router)
app.include_router(auth_router)


@app.get("/")
def inicio():
    return {
        "mensaje": "API del gestor de tareas funcionando"
    }

@app.get("/prueba-async")
async def prueba_async():
    return {
        "tipo": "async",
        "ok": True
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
