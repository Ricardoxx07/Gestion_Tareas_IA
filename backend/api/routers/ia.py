from fastapi import APIRouter, Depends

from api.dependencies import (
    obtener_planificacion_service,
    obtener_plan_dia_service,
    obtener_sobrecarga_service,
    obtener_reprogramacion_service,
    obtener_confirmacion_reprogramacion_service,
    obtener_confirmacion_propuestas_service,
    obtener_descomposicion_tarea_service,
    obtener_propuesta_tareas_service,
    obtener_usuario_actual,
)
from models.usuario import Usuario
from models.tarea import Tarea
from schemas.planificacion_schema import PlanificacionResponse
from schemas.plan_dia_schema import PlanDiaRequest, PlanDiaResponse
from schemas.sobrecarga_schema import (
    AnalisisSobrecargaResponse,
    DetectarSobrecargaRequest,
)
from schemas.reprogramacion_schema import (
    ProponerReprogramacionRequest,
    PropuestasReprogramacionResponse,
)
from schemas.confirmacion_reprogramacion_schema import (
    ConfirmarReprogramacionesRequest,
    ReprogramacionesConfirmadasResponse,
)
from schemas.propuesta_tareas_schema import (
    PlanificarTextoRequest,
    PropuestasTareasResponse,
)
from schemas.descomposicion_tarea_schema import (
    DescomponerTareaRequest,
    DescomposicionTareaResponse,
)
from schemas.confirmacion_propuestas_schema import (
    ConfirmarPropuestasRequest,
    PropuestasConfirmadasResponse,
)
from services.confirmacion_propuestas_service import ConfirmacionPropuestasService
from services.descomposicion_tarea_service import DescomposicionTareaService
from services.planificacion_service import PlanificacionService
from services.plan_dia_service import PlanDiaService
from services.sobrecarga_service import SobrecargaService
from services.reprogramacion_service import ReprogramacionService
from services.confirmacion_reprogramacion_service import ConfirmacionReprogramacionService
from services.propuesta_tareas_service import PropuestaTareasService


router = APIRouter(prefix="/ia", tags=["Inteligencia artificial"])


@router.post("/recomendar-tareas", response_model=PlanificacionResponse)
def recomendar_tareas(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: PlanificacionService = Depends(obtener_planificacion_service)
):
    return service.recomendar_tareas(usuario_actual.id)


@router.post("/plan-dia", response_model=PlanDiaResponse)
def planificar_dia(
    datos: PlanDiaRequest,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: PlanDiaService = Depends(obtener_plan_dia_service),
):
    """Organiza tareas existentes para una fecha, sin modificar ninguna."""
    return service.planificar_dia(usuario_actual.id, datos.fecha)


@router.post("/detectar-sobrecarga", response_model=AnalisisSobrecargaResponse)
def detectar_sobrecarga(
    datos: DetectarSobrecargaRequest,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: SobrecargaService = Depends(obtener_sobrecarga_service),
):
    """Detecta concentración de tareas; no reprograma ni modifica datos."""
    return service.detectar_sobrecarga(
        usuario_id=usuario_actual.id,
        fecha_inicio=datos.fecha_inicio,
        dias=datos.dias,
        max_tareas_por_dia=datos.max_tareas_por_dia,
    )


@router.post(
    "/proponer-reprogramacion",
    response_model=PropuestasReprogramacionResponse,
)
def proponer_reprogramacion(
    datos: ProponerReprogramacionRequest,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: ReprogramacionService = Depends(obtener_reprogramacion_service),
):
    """Propone nuevas fechas; el usuario debe decidir si las aplica."""
    return service.proponer_reprogramaciones(
        usuario_id=usuario_actual.id,
        fecha_inicio=datos.fecha_inicio,
        dias=datos.dias,
        max_tareas_por_dia=datos.max_tareas_por_dia,
    )


@router.post(
    "/reprogramaciones/confirmar",
    response_model=ReprogramacionesConfirmadasResponse,
)
def confirmar_reprogramaciones(
    datos: ConfirmarReprogramacionesRequest,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: ConfirmacionReprogramacionService = Depends(
        obtener_confirmacion_reprogramacion_service
    ),
):
    tareas = service.confirmar(
        [
            (item.tarea_id, item.fecha_actual, item.fecha_sugerida)
            for item in datos.reprogramaciones
        ],
        usuario_actual.id,
    )
    return ReprogramacionesConfirmadasResponse(tareas_actualizadas=tareas)


@router.post("/planificar", response_model=PropuestasTareasResponse)
def planificar_desde_texto(
    datos: PlanificarTextoRequest,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: PropuestaTareasService = Depends(obtener_propuesta_tareas_service),
):
    """Devuelve propuestas; no crea tareas ni accede a PostgreSQL."""
    return service.proponer_tareas(datos.texto)


@router.post("/descomponer", response_model=DescomposicionTareaResponse)
def descomponer_tarea(
    datos: DescomponerTareaRequest,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: DescomposicionTareaService = Depends(
        obtener_descomposicion_tarea_service
    ),
):
    """Propone subtareas; no crea ni modifica tareas existentes."""
    return service.descomponer_tarea(datos.texto)


@router.post(
    "/propuestas/confirmar",
    response_model=PropuestasConfirmadasResponse,
    status_code=201,
)
def confirmar_propuestas(
    datos: ConfirmarPropuestasRequest,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    service: ConfirmacionPropuestasService = Depends(
        obtener_confirmacion_propuestas_service
    ),
):
    """Persiste únicamente las propuestas que el usuario eligió confirmar."""
    tareas_confirmadas = service.confirmar_propuestas(
        [
            Tarea(
                nombre=tarea.nombre,
                fecha_limite=tarea.fecha_limite,
                prioridad=tarea.prioridad,
                tarea_padre_id=tarea.tarea_padre_id,
            )
            for tarea in datos.tareas
        ],
        usuario_actual.id,
    )
    return PropuestasConfirmadasResponse(tareas_confirmadas=tareas_confirmadas)
