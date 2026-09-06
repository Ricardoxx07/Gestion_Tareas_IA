from datetime import date

import pytest

from exceptions.planificacion_exceptions import RecomendacionIAInvalidaError
from models.sobrecarga import ExplicacionSobrecarga
from models.tarea import Tarea
from services.sobrecarga_service import SobrecargaService


class TareaRepositoryFalso:
    def __init__(self, tareas: list[Tarea]):
        self.tareas = tareas

    def cargar_tareas(self, usuario_id: int) -> list[Tarea]:
        return [tarea for tarea in self.tareas if tarea.usuario_id == usuario_id]


class ProveedorIAEspia:
    def __init__(self, explicaciones: list[ExplicacionSobrecarga]):
        self.explicaciones = explicaciones
        self.cargas_recibidas = None

    def explicar_sobrecargas(self, cargas):
        self.cargas_recibidas = cargas
        return self.explicaciones


def test_detecta_sobrecarga_solo_con_tareas_pendientes_del_usuario():
    inicio = date(2026, 9, 5)
    proveedor = ProveedorIAEspia(
        [
            ExplicacionSobrecarga(
                fecha=inicio,
                mensaje="Hay varias tareas acumuladas.",
                sugerencia="Empieza por las tareas vencidas.",
            )
        ]
    )
    service = SobrecargaService(
        TareaRepositoryFalso(
            [
                Tarea(id=1, usuario_id=1, nombre="Vencida", fecha_limite=date(2026, 9, 4)),
                Tarea(id=2, usuario_id=1, nombre="Para hoy A", fecha_limite=inicio),
                Tarea(id=3, usuario_id=1, nombre="Para hoy B", fecha_limite=inicio),
                Tarea(id=4, usuario_id=1, nombre="Para hoy C", fecha_limite=inicio),
                Tarea(id=5, usuario_id=1, nombre="Completada", completada=True, fecha_limite=inicio),
                Tarea(id=6, usuario_id=2, nombre="Otro usuario", fecha_limite=inicio),
            ]
        ),
        proveedor,
    )

    analisis = service.detectar_sobrecarga(
        usuario_id=1,
        fecha_inicio=inicio,
        dias=7,
        max_tareas_por_dia=3,
    )

    assert len(proveedor.cargas_recibidas) == 1
    assert [tarea.id for tarea in proveedor.cargas_recibidas[0].tareas] == [1, 2, 3, 4]
    assert proveedor.cargas_recibidas[0].incluye_tareas_vencidas is True
    assert analisis.alertas[0].cantidad_tareas == 4
    assert analisis.alertas[0].tarea_ids == [1, 2, 3, 4]


def test_no_llama_al_proveedor_si_no_hay_sobrecarga():
    proveedor = ProveedorIAEspia([])
    service = SobrecargaService(
        TareaRepositoryFalso(
            [
                Tarea(id=1, usuario_id=1, nombre="Una", fecha_limite=date(2026, 9, 5)),
                Tarea(id=2, usuario_id=1, nombre="Dos", fecha_limite=date(2026, 9, 5)),
            ]
        ),
        proveedor,
    )

    analisis = service.detectar_sobrecarga(
        usuario_id=1,
        fecha_inicio=date(2026, 9, 5),
        max_tareas_por_dia=3,
    )

    assert analisis.alertas == []
    assert proveedor.cargas_recibidas is None


@pytest.mark.parametrize(
    "explicaciones",
    [
        [
            ExplicacionSobrecarga(
                fecha=date(2026, 9, 6),
                mensaje="Fecha ajena.",
                sugerencia="Sugerencia.",
            )
        ],
        [
            ExplicacionSobrecarga(
                fecha=date(2026, 9, 5),
                mensaje="Primera.",
                sugerencia="Sugerencia.",
            ),
            ExplicacionSobrecarga(
                fecha=date(2026, 9, 5),
                mensaje="Duplicada.",
                sugerencia="Sugerencia.",
            ),
        ],
    ],
)
def test_rechaza_explicaciones_fuera_del_contexto_o_duplicadas(explicaciones):
    service = SobrecargaService(
        TareaRepositoryFalso(
            [
                Tarea(id=1, usuario_id=1, nombre="A", fecha_limite=date(2026, 9, 5)),
                Tarea(id=2, usuario_id=1, nombre="B", fecha_limite=date(2026, 9, 5)),
            ]
        ),
        ProveedorIAEspia(explicaciones),
    )

    with pytest.raises(RecomendacionIAInvalidaError):
        service.detectar_sobrecarga(
            usuario_id=1,
            fecha_inicio=date(2026, 9, 5),
            max_tareas_por_dia=1,
        )
