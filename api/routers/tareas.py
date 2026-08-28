from fastapi import APIRouter, Depends, HTTPException, status

from schemas.tarea_schema import (
    TareaRequest,
    TareaResponse,
    TareaUpdate,
    TareaPatch
)

from services.tarea_service import TareaService
from api.dependencies import obtener_service


router = APIRouter(
    prefix="/tareas",
    tags=["Tareas"]
)


@router.get(
    "",
    response_model=list[TareaResponse]
)
def listar_tareas(
    service: TareaService = Depends(obtener_service)
):
    return service.listar_tareas()


@router.post(
    "",
    response_model=TareaResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_tarea(
    tarea: TareaRequest,
    service: TareaService = Depends(obtener_service)
):
    return service.agregar_tarea(tarea.nombre)


@router.get(
    "/{id_tarea}",
    response_model=TareaResponse
)
def obtener_tarea_por_id(
    id_tarea: int,
    service: TareaService = Depends(obtener_service)
):
    tarea = service.obtener_tarea(id_tarea)

    if tarea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    return tarea


@router.put(
    "/{id_tarea}",
    response_model=TareaResponse
)
def actualizar_tarea(
    id_tarea: int,
    datos: TareaUpdate,
    service: TareaService = Depends(obtener_service)
):
    tarea = service.actualizar_tarea(
        id_tarea,
        datos.nombre,
        datos.completada
    )

    if tarea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    return tarea


@router.patch(
    "/{id_tarea}",
    response_model=TareaResponse
)
def actualizar_parcialmente_tarea(
    id_tarea: int,
    datos: TareaPatch,
    service: TareaService = Depends(obtener_service)
):
    tarea = service.actualizar_parcialmente_tarea(
        id_tarea,
        datos.nombre,
        datos.completada
    )

    if tarea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    return tarea


@router.delete(
    "/{id_tarea}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_tarea(
    id_tarea: int,
    service: TareaService = Depends(obtener_service)
):
    eliminado = service.eliminar_tarea(id_tarea)

    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
