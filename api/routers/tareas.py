from fastapi import APIRouter, Depends, HTTPException, status

from schemas.tarea_schema import (
    TareaRequest,
    SubtareaRequest,
    TareaResponse,
    TareaUpdate,
    TareaPatch
)

from services.tarea_service import TareaService
from api.dependencies import obtener_service, obtener_usuario_actual
from models.usuario import Usuario


router = APIRouter(
    prefix="/tareas",
    tags=["Tareas"]
)


@router.get(
    "",
    response_model=list[TareaResponse]
)
def listar_tareas(
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return service.listar_tareas(usuario_actual.id)


@router.post(
    "",
    response_model=TareaResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_tarea(
    tarea: TareaRequest,
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return service.agregar_tarea(
        tarea.nombre,
        usuario_actual.id,
        tarea.fecha_limite,
        tarea.prioridad,
        tarea.tarea_padre_id,
    )


@router.get(
    "/{id_tarea}",
    response_model=TareaResponse
)
def obtener_tarea_por_id(
    id_tarea: int,
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    tarea = service.obtener_tarea(id_tarea, usuario_actual.id)

    if tarea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    return tarea


@router.get(
    "/{id_tarea}/subtareas",
    response_model=list[TareaResponse],
)
def listar_subtareas(
    id_tarea: int,
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    return service.listar_subtareas(id_tarea, usuario_actual.id)


@router.post(
    "/{id_tarea}/subtareas",
    response_model=TareaResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_subtarea(
    id_tarea: int,
    subtarea: SubtareaRequest,
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """Crea una hija de la tarea indicada por la URL."""
    return service.agregar_tarea(
        subtarea.nombre,
        usuario_actual.id,
        subtarea.fecha_limite,
        subtarea.prioridad,
        id_tarea,
    )


@router.get(
    "/{id_tarea}/subtareas/{id_subtarea}",
    response_model=TareaResponse,
)
def obtener_subtarea(
    id_tarea: int,
    id_subtarea: int,
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    return service.obtener_subtarea_o_error(
        id_tarea,
        id_subtarea,
        usuario_actual.id,
    )


@router.put(
    "/{id_tarea}/subtareas/{id_subtarea}",
    response_model=TareaResponse,
)
def actualizar_subtarea(
    id_tarea: int,
    id_subtarea: int,
    datos: TareaUpdate,
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    service.obtener_subtarea_o_error(id_tarea, id_subtarea, usuario_actual.id)
    return service.actualizar_tarea(
        id_subtarea,
        usuario_actual.id,
        datos.nombre,
        datos.completada,
        datos.fecha_limite,
        datos.prioridad,
        "fecha_limite" in datos.model_fields_set,
    )


@router.patch(
    "/{id_tarea}/subtareas/{id_subtarea}",
    response_model=TareaResponse,
)
def actualizar_parcialmente_subtarea(
    id_tarea: int,
    id_subtarea: int,
    datos: TareaPatch,
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    service.obtener_subtarea_o_error(id_tarea, id_subtarea, usuario_actual.id)
    return service.actualizar_parcialmente_tarea(
        id_subtarea,
        usuario_actual.id,
        datos.nombre,
        datos.completada,
        datos.fecha_limite,
        datos.prioridad,
        "fecha_limite" in datos.model_fields_set,
    )


@router.delete(
    "/{id_tarea}/subtareas/{id_subtarea}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_subtarea(
    id_tarea: int,
    id_subtarea: int,
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    service.obtener_subtarea_o_error(id_tarea, id_subtarea, usuario_actual.id)
    service.eliminar_tarea(id_subtarea, usuario_actual.id)


@router.put(
    "/{id_tarea}",
    response_model=TareaResponse
)
def actualizar_tarea(
    id_tarea: int,
    datos: TareaUpdate,
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    tarea = service.actualizar_tarea(
        id_tarea,
        usuario_actual.id,
        datos.nombre,
        datos.completada,
        datos.fecha_limite,
        datos.prioridad,
        "fecha_limite" in datos.model_fields_set
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
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    tarea = service.actualizar_parcialmente_tarea(
        id_tarea,
        usuario_actual.id,
        datos.nombre,
        datos.completada,
        datos.fecha_limite,
        datos.prioridad,
        "fecha_limite" in datos.model_fields_set
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
    service: TareaService = Depends(obtener_service),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    eliminado = service.eliminar_tarea(id_tarea, usuario_actual.id)

    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
