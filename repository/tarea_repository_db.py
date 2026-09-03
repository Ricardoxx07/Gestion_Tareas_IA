from sqlalchemy.orm import Session

from models.tarea import Tarea
from models.tarea_db import TareaDB
from repository.tarea_repository_interface import TareaRepositoryInterface
from sqlalchemy.exc import SQLAlchemyError


class TareaRepositoryDB(TareaRepositoryInterface):


    def __init__(self, db: Session):
        self.db = db

    def cargar_tareas(self, usuario_id: int) -> list[Tarea]:

        tareas_db = (
            self.db.query(TareaDB)
            .filter(TareaDB.usuario_id == usuario_id)
            .all()
        )

        return [
            Tarea(
                id=tarea.id,
                nombre=tarea.nombre,
                completada=tarea.completada,
                usuario_id=tarea.usuario_id
            )
            for tarea in tareas_db
        ]

    def obtener_tarea(self, id_tarea: int, usuario_id: int) -> Tarea | None:

        tarea_db = (
            self.db.query(TareaDB)
            .filter(
                TareaDB.id == id_tarea,
                TareaDB.usuario_id == usuario_id
            )
            .first()
        )

        if tarea_db is None:
            return None

        return Tarea(
            id=tarea_db.id,
            nombre=tarea_db.nombre,
            completada=tarea_db.completada,
            usuario_id=tarea_db.usuario_id
        )

    def guardar_tarea(self, tarea: Tarea) -> Tarea:

        tarea_db = TareaDB(
            nombre=tarea.nombre,
            completada=tarea.completada,
            usuario_id=tarea.usuario_id
            )

        try:
            self.db.add(tarea_db)
            self.db.commit()
            self.db.refresh(tarea_db)

        except SQLAlchemyError:
            self.db.rollback()
            raise

        return Tarea(
            id=tarea_db.id,
            nombre=tarea_db.nombre,
            completada=tarea_db.completada,
            usuario_id=tarea_db.usuario_id
            )

    def actualizar_tarea(self, tarea: Tarea) -> None:

        tarea_db = (
            self.db.query(TareaDB)
            .filter(
                TareaDB.id == tarea.id,
                TareaDB.usuario_id == tarea.usuario_id
            )
            .first()
        )

        if tarea_db is None:
            return

        tarea_db.nombre = tarea.nombre
        tarea_db.completada = tarea.completada

        try:
            self.db.commit()

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def eliminar_tarea(self, id_tarea: int, usuario_id: int) -> bool:

        tarea_db = (
            self.db.query(TareaDB)
            .filter(
                TareaDB.id == id_tarea,
                TareaDB.usuario_id == usuario_id
            )
            .first()
        )

        if tarea_db is None:
            return False

        self.db.delete(tarea_db)

        try:
            self.db.commit()

        except SQLAlchemyError:
            self.db.rollback()
            raise

        return True
