from datetime import date

import pytest

from exceptions.planificacion_exceptions import RecomendacionIAInvalidaError
from models.plan_dia import PlanDia
from models.planificacion import RecomendacionTarea
from models.tarea import Tarea
from services.plan_dia_service import PlanDiaService


class TareaRepositoryFalso:
    def __init__(self, tareas: list[Tarea]):
        self.tareas = tareas

    def cargar_tareas(self, usuario_id: int) -> list[Tarea]:
        return [tarea for tarea in self.tareas if tarea.usuario_id == usuario_id]


class ProveedorIAEspia:
    def __init__(self, respuesta: PlanDia):
        self.respuesta = respuesta
        self.tareas_recibidas: list[Tarea] | None = None
        self.fecha_recibida: date | None = None

    def planificar_dia(self, tareas: list[Tarea], fecha: date) -> PlanDia:
        self.tareas_recibidas = tareas
        self.fecha_recibida = fecha
        return self.respuesta


def crear_plan(fecha: date, ids: list[int]) -> PlanDia:
    return PlanDia(
        fecha=fecha,
        plan=[
            RecomendacionTarea(tarea_id=tarea_id, orden=orden, motivo="Motivo")
            for orden, tarea_id in enumerate(ids, start=1)
        ],
        resumen="Plan diario de prueba.",
    )


def test_entrega_solo_vencidas_o_que_vencen_en_la_fecha_planificada():
    fecha = date(2026, 9, 5)
    proveedor = ProveedorIAEspia(crear_plan(fecha, [1, 2]))
    service = PlanDiaService(
        TareaRepositoryFalso(
            [
                Tarea(id=1, usuario_id=1, nombre="Vencida", fecha_limite=date(2026, 9, 4)),
                Tarea(id=2, usuario_id=1, nombre="Para hoy", fecha_limite=fecha),
                Tarea(id=3, usuario_id=1, nombre="Mañana", fecha_limite=date(2026, 9, 6)),
                Tarea(id=4, usuario_id=2, nombre="Otro usuario", fecha_limite=fecha),
                Tarea(id=5, usuario_id=1, nombre="Completada", completada=True, fecha_limite=fecha),
            ]
        ),
        proveedor,
    )

    plan = service.planificar_dia(usuario_id=1, fecha=fecha)

    assert [tarea.id for tarea in proveedor.tareas_recibidas] == [1, 2]
    assert proveedor.fecha_recibida == fecha
    assert [recomendacion.tarea_id for recomendacion in plan.plan] == [1, 2]


def test_si_no_hay_tareas_para_el_dia_usa_las_proximas_relevantes():
    fecha = date(2026, 9, 5)
    proveedor = ProveedorIAEspia(crear_plan(fecha, [1]))
    service = PlanDiaService(
        TareaRepositoryFalso(
            [
                Tarea(id=1, usuario_id=1, nombre="Mañana", fecha_limite=date(2026, 9, 6)),
                Tarea(id=2, usuario_id=1, nombre="Lejana", fecha_limite=date(2026, 9, 13)),
                Tarea(id=3, usuario_id=1, nombre="Sin fecha"),
            ]
        ),
        proveedor,
    )

    service.planificar_dia(usuario_id=1, fecha=fecha)

    assert [tarea.id for tarea in proveedor.tareas_recibidas] == [1]


def test_no_llama_al_proveedor_si_no_hay_tareas_pendientes():
    fecha = date(2026, 9, 5)
    proveedor = ProveedorIAEspia(crear_plan(fecha, []))
    service = PlanDiaService(
        TareaRepositoryFalso(
            [Tarea(id=1, usuario_id=1, nombre="Lista", completada=True)]
        ),
        proveedor,
    )

    plan = service.planificar_dia(usuario_id=1, fecha=fecha)

    assert plan.plan == []
    assert proveedor.tareas_recibidas is None


@pytest.mark.parametrize(
    "plan",
    [
        crear_plan(date(2026, 9, 5), [999]),
        PlanDia(
            fecha=date(2026, 9, 5),
            plan=[
                RecomendacionTarea(1, 1, "Primera"),
                RecomendacionTarea(1, 2, "Duplicada"),
            ],
            resumen="Resumen",
        ),
        PlanDia(
            fecha=date(2026, 9, 5),
            plan=[RecomendacionTarea(1, 2, "Orden incorrecto")],
            resumen="Resumen",
        ),
    ],
)
def test_rechaza_planes_con_ids_u_orden_invalidos(plan):
    proveedor = ProveedorIAEspia(plan)
    service = PlanDiaService(
        TareaRepositoryFalso([Tarea(id=1, usuario_id=1, nombre="Pendiente")]),
        proveedor,
    )

    with pytest.raises(RecomendacionIAInvalidaError):
        service.planificar_dia(usuario_id=1, fecha=date(2026, 9, 5))
