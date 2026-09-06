from datetime import date

import pytest

from exceptions.planificacion_exceptions import RecomendacionIAInvalidaError
from models.reprogramacion import PropuestaReprogramacionIA
from models.tarea import Tarea
from services.reprogramacion_service import ReprogramacionService


class TareaRepositoryFalso:
    def __init__(self, tareas: list[Tarea]):
        self.tareas = tareas

    def cargar_tareas(self, usuario_id: int) -> list[Tarea]:
        return [tarea for tarea in self.tareas if tarea.usuario_id == usuario_id]


class ProveedorIAEspia:
    def __init__(self, propuestas: list[PropuestaReprogramacionIA]):
        self.propuestas = propuestas
        self.cargas_recibidas = None
        self.dias_disponibles_recibidos = None

    def proponer_reprogramaciones(self, cargas, dias_disponibles):
        self.cargas_recibidas = cargas
        self.dias_disponibles_recibidos = dias_disponibles
        return self.propuestas


def test_propone_mover_tareas_del_usuario_hacia_un_dia_con_cupo():
    inicio = date(2026, 9, 5)
    proveedor = ProveedorIAEspia(
        [
            PropuestaReprogramacionIA(
                tarea_id=3,
                motivo="Tiene prioridad baja dentro del día sobrecargado.",
            )
        ]
    )
    service = ReprogramacionService(
        TareaRepositoryFalso(
            [
                Tarea(id=1, usuario_id=1, nombre="Alta", prioridad="alta", fecha_limite=date(2026, 9, 8)),
                Tarea(id=2, usuario_id=1, nombre="Media", prioridad="media", fecha_limite=date(2026, 9, 8)),
                Tarea(id=3, usuario_id=1, nombre="Baja", prioridad="baja", fecha_limite=date(2026, 9, 8)),
                Tarea(id=4, usuario_id=1, nombre="Otra", prioridad="baja", fecha_limite=date(2026, 9, 8)),
                Tarea(id=5, usuario_id=1, nombre="Después", fecha_limite=date(2026, 9, 9)),
                Tarea(id=6, usuario_id=2, nombre="Otro usuario", fecha_limite=date(2026, 9, 8)),
            ]
        ),
        proveedor,
    )

    resultado = service.proponer_reprogramaciones(
        usuario_id=1,
        fecha_inicio=inicio,
        dias=7,
        max_tareas_por_dia=3,
    )

    assert [tarea.id for tarea in proveedor.cargas_recibidas[0].tareas] == [1, 2, 3, 4]
    assert proveedor.cargas_recibidas[0].max_reprogramaciones == 1
    assert date(2026, 9, 8) not in {
        dia.fecha for dia in proveedor.dias_disponibles_recibidos
    }
    assert resultado.propuestas[0].tarea_id == 3
    assert resultado.propuestas[0].fecha_actual == date(2026, 9, 8)
    assert resultado.propuestas[0].fecha_sugerida == inicio


def test_no_propone_mover_tareas_vencidas():
    proveedor = ProveedorIAEspia([])
    service = ReprogramacionService(
        TareaRepositoryFalso(
            [
                Tarea(id=1, usuario_id=1, nombre="Vencida A", fecha_limite=date(2026, 9, 3)),
                Tarea(id=2, usuario_id=1, nombre="Vencida B", fecha_limite=date(2026, 9, 3)),
            ]
        ),
        proveedor,
    )

    resultado = service.proponer_reprogramaciones(
        usuario_id=1,
        fecha_inicio=date(2026, 9, 5),
        max_tareas_por_dia=1,
    )

    assert resultado.propuestas == []
    assert proveedor.cargas_recibidas is None


def test_descarta_el_exceso_de_propuestas_del_mismo_dia_sobrecargado():
    proveedor = ProveedorIAEspia(
        [
            PropuestaReprogramacionIA(tarea_id=1, motivo="Primera propuesta."),
            PropuestaReprogramacionIA(tarea_id=2, motivo="Exceso."),
        ]
    )
    service = ReprogramacionService(
        TareaRepositoryFalso(
            [
                Tarea(id=1, usuario_id=1, nombre="A", fecha_limite=date(2026, 9, 8)),
                Tarea(id=2, usuario_id=1, nombre="B", fecha_limite=date(2026, 9, 8)),
            ]
        ),
        proveedor,
    )

    resultado = service.proponer_reprogramaciones(
        usuario_id=1,
        fecha_inicio=date(2026, 9, 5),
        max_tareas_por_dia=1,
    )

    assert [propuesta.tarea_id for propuesta in resultado.propuestas] == [1]


@pytest.mark.parametrize(
    "propuestas",
    [
        [
            PropuestaReprogramacionIA(
                tarea_id=999,
                motivo="No pertenece al contexto.",
            )
        ],
        [
            PropuestaReprogramacionIA(
                tarea_id=1,
                motivo="Primera propuesta.",
            ),
            PropuestaReprogramacionIA(
                tarea_id=1,
                motivo="Propuesta duplicada.",
            ),
        ],
    ],
)
def test_rechaza_propuestas_fuera_del_contexto(propuestas):
    service = ReprogramacionService(
        TareaRepositoryFalso(
            [
                Tarea(id=1, usuario_id=1, nombre="A", fecha_limite=date(2026, 9, 8)),
                Tarea(id=2, usuario_id=1, nombre="B", fecha_limite=date(2026, 9, 8)),
            ]
        ),
        ProveedorIAEspia(propuestas),
    )

    with pytest.raises(RecomendacionIAInvalidaError):
        service.proponer_reprogramaciones(
            usuario_id=1,
            fecha_inicio=date(2026, 9, 5),
            max_tareas_por_dia=1,
        )
