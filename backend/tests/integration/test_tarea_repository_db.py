from datetime import date

import pytest
from unittest.mock import Mock
from sqlalchemy.exc import SQLAlchemyError

from models.tarea import Tarea
from models.usuario_db import UsuarioDB
from repository.tarea_repository_db import TareaRepositoryDB


def test_guardar_y_obtener_tarea(tarea_repository_db, usuario_db):

    tarea = Tarea(
        nombre="Estudiar PostgreSQL",
        usuario_id=usuario_db.id,
        fecha_limite=date(2026, 9, 10),
        prioridad="alta"
    )

    guardada = tarea_repository_db.guardar_tarea(tarea)

    assert guardada.id is not None
    assert guardada.nombre == "Estudiar PostgreSQL"
    assert guardada.completada is False
    assert guardada.fecha_limite == date(2026, 9, 10)
    assert guardada.prioridad == "alta"
    assert guardada.created_at is not None

    encontrada = tarea_repository_db.obtener_tarea(guardada.id, usuario_db.id)

    assert encontrada is not None
    assert encontrada.id == guardada.id
    assert encontrada.nombre == "Estudiar PostgreSQL"
    assert encontrada.completada is False
    assert encontrada.fecha_limite == date(2026, 9, 10)
    assert encontrada.prioridad == "alta"


def test_guardar_y_listar_subtareas(tarea_repository_db, usuario_db):
    padre = tarea_repository_db.guardar_tarea(
        Tarea(nombre="Preparar presentación", usuario_id=usuario_db.id)
    )
    subtarea = tarea_repository_db.guardar_tarea(
        Tarea(
            nombre="Definir estructura",
            usuario_id=usuario_db.id,
            tarea_padre_id=padre.id,
        )
    )

    subtareas = tarea_repository_db.cargar_subtareas(padre.id, usuario_db.id)

    assert len(subtareas) == 1
    assert subtareas[0].id == subtarea.id
    assert subtareas[0].tarea_padre_id == padre.id


def test_guardar_lote_de_tareas(tarea_repository_db, usuario_db):
    tareas = tarea_repository_db.guardar_tareas(
        [
            Tarea(nombre="Primera propuesta", usuario_id=usuario_db.id),
            Tarea(nombre="Segunda propuesta", usuario_id=usuario_db.id),
        ]
    )

    assert len(tareas) == 2
    assert all(tarea.id is not None for tarea in tareas)
    assert [tarea.nombre for tarea in tareas] == [
        "Primera propuesta",
        "Segunda propuesta",
    ]


def test_cargar_tareas(tarea_repository_db, usuario_db):

    tarea1 = Tarea(nombre="Estudiar Python", usuario_id=usuario_db.id)

    tarea2 = Tarea(
        nombre="Aprender PostgreSQL",
        completada=True,
        usuario_id=usuario_db.id
    )

    tarea_repository_db.guardar_tarea(tarea1)
    tarea_repository_db.guardar_tarea(tarea2)

    tareas = tarea_repository_db.cargar_tareas(usuario_db.id)

    assert len(tareas) == 2

    assert tareas[0].nombre == "Estudiar Python"
    assert tareas[0].completada is False

    assert tareas[1].nombre == "Aprender PostgreSQL"
    assert tareas[1].completada is True


def test_obtener_tarea_inexistente(tarea_repository_db, usuario_db):

    tarea = tarea_repository_db.obtener_tarea(999, usuario_db.id)

    assert tarea is None


def test_actualizar_tarea(tarea_repository_db, usuario_db):

    tarea = Tarea(nombre="Estudiar Python", usuario_id=usuario_db.id)

    guardada = tarea_repository_db.guardar_tarea(tarea)

    guardada.nombre = "Estudiar Python avanzado"
    guardada.completada = True

    tarea_repository_db.actualizar_tarea(guardada)

    actualizada = tarea_repository_db.obtener_tarea(guardada.id, usuario_db.id)

    assert actualizada is not None
    assert actualizada.nombre == "Estudiar Python avanzado"
    assert actualizada.completada is True


def test_eliminar_tarea(tarea_repository_db, usuario_db):

    tarea = Tarea(nombre="Tarea temporal", usuario_id=usuario_db.id)

    guardada = tarea_repository_db.guardar_tarea(tarea)

    resultado = tarea_repository_db.eliminar_tarea(guardada.id, usuario_db.id)

    assert resultado is True

    eliminada = tarea_repository_db.obtener_tarea(guardada.id, usuario_db.id)

    assert eliminada is None


def test_eliminar_tarea_inexistente(tarea_repository_db, usuario_db):

    resultado = tarea_repository_db.eliminar_tarea(999, usuario_db.id)

    assert resultado is False


def test_no_obtiene_tarea_de_otro_usuario(tarea_repository_db, usuario_db, db):
    otro_usuario = UsuarioDB(
        email="otro-usuario@example.com",
        password_hash="hash-de-prueba"
    )
    db.add(otro_usuario)
    db.commit()
    db.refresh(otro_usuario)

    guardada = tarea_repository_db.guardar_tarea(
        Tarea(nombre="Tarea privada", usuario_id=usuario_db.id)
    )

    assert tarea_repository_db.obtener_tarea(guardada.id, otro_usuario.id) is None
    assert tarea_repository_db.cargar_tareas(otro_usuario.id) == []
