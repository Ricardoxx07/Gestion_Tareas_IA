from datetime import date

import pytest

from ai.proveedor_ia_falso import ProveedorIAFalso
from exceptions.planificacion_exceptions import RecomendacionIAInvalidaError
from models.planificacion import Planificacion, RecomendacionTarea
from models.tarea import Tarea
from services.planificacion_service import PlanificacionService


class TareaRepositoryFalso:

    def __init__(self, tareas: list[Tarea]):
        self.tareas = tareas

    def cargar_tareas(self, usuario_id: int) -> list[Tarea]:
        return [tarea for tarea in self.tareas if tarea.usuario_id == usuario_id]


class ProveedorIAEspia:

    def __init__(self, respuesta: Planificacion):
        self.respuesta = respuesta
        self.tareas_recibidas: list[Tarea] | None = None

    def recomendar_tareas(self, tareas: list[Tarea], hoy: date) -> Planificacion:
        self.tareas_recibidas = tareas
        return self.respuesta


def test_recomienda_primero_tarea_vencida_y_de_prioridad_alta():
    tareas = [
        Tarea(id=1, usuario_id=1, nombre="Estudiar AWS", prioridad="alta"),
        Tarea(
            id=2,
            usuario_id=1,
            nombre="Enviar informe",
            fecha_limite=date(2026, 9, 2),
            prioridad="media"
        ),
        Tarea(
            id=3,
            usuario_id=1,
            nombre="Comprar materiales",
            fecha_limite=date(2026, 9, 3),
            prioridad="alta"
        ),
    ]
    service = PlanificacionService(TareaRepositoryFalso(tareas), ProveedorIAFalso())

    planificacion = service.recomendar_tareas(1, hoy=date(2026, 9, 3))

    assert [item.tarea_id for item in planificacion.recomendaciones] == [2, 3, 1]
    assert planificacion.recomendaciones[0].orden == 1
    assert "vencida" in planificacion.recomendaciones[0].motivo


def test_solo_entrega_tareas_pendientes_del_usuario_al_proveedor():
    tareas = [
        Tarea(id=1, usuario_id=1, nombre="Pendiente"),
        Tarea(id=2, usuario_id=1, nombre="Completada", completada=True),
        Tarea(id=3, usuario_id=2, nombre="De otro usuario"),
    ]
    proveedor = ProveedorIAEspia(
        Planificacion(
            recomendaciones=[RecomendacionTarea(1, 1, "Motivo")],
            resumen="Resumen"
        )
    )
    service = PlanificacionService(TareaRepositoryFalso(tareas), proveedor)

    service.recomendar_tareas(1, hoy=date(2026, 9, 3))

    assert proveedor.tareas_recibidas is not None
    assert [tarea.id for tarea in proveedor.tareas_recibidas] == [1]


def test_no_llama_al_proveedor_si_no_hay_tareas_pendientes():
    proveedor = ProveedorIAEspia(Planificacion([], "No debería usarse"))
    service = PlanificacionService(
        TareaRepositoryFalso([Tarea(id=1, usuario_id=1, nombre="Lista", completada=True)]),
        proveedor
    )

    planificacion = service.recomendar_tareas(1, hoy=date(2026, 9, 3))

    assert planificacion.recomendaciones == []
    assert proveedor.tareas_recibidas is None


@pytest.mark.parametrize(
    "recomendaciones",
    [
        [RecomendacionTarea(999, 1, "No existe")],
        [RecomendacionTarea(1, 1, "Primera"), RecomendacionTarea(1, 2, "Duplicada")],
    ]
)
def test_rechaza_recomendaciones_fuera_del_contexto_o_duplicadas(recomendaciones):
    proveedor = ProveedorIAEspia(Planificacion(recomendaciones, "Resumen"))
    service = PlanificacionService(
        TareaRepositoryFalso([Tarea(id=1, usuario_id=1, nombre="Pendiente")]),
        proveedor
    )

    with pytest.raises(RecomendacionIAInvalidaError):
        service.recomendar_tareas(1, hoy=date(2026, 9, 3))
