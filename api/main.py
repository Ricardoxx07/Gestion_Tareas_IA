from fastapi import FastAPI

from api.routers.tareas import router as tareas_router


app = FastAPI(
    title="API Gestor de Tareas",
    description="API REST para gestionar tareas",
    version="1.0.0"
)


app.include_router(tareas_router)


@app.get("/")
def inicio():
    return {
        "mensaje": "API del gestor de tareas funcionando"
    }