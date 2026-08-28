from sqlalchemy.orm import Session

from models.tarea import Tarea
from models.tarea_db import TareaDB
from repository.tarea_repository_interface import TareaRepositoryInterface


class TareaRepositoryDB(TareaRepositoryInterface):


    def __init__(self, db: Session):
        self.db = db

    def cargar_tareas(self) -> list[Tarea]:

        tareas_db = self.db.query(TareaDB).all()

        return [
            Tarea(
                id=tarea.id,
                nombre=tarea.nombre,
                completada=tarea.completada
            )
            for tarea in tareas_db
        ]

    def obtener_tarea(self, id_tarea: int) -> Tarea | None:

        tarea_db = self.db.get(TareaDB, id_tarea)

        if tarea_db is None:
            return None

        return Tarea(
            id=tarea_db.id,
            nombre=tarea_db.nombre,
            completada=tarea_db.completada
        )

    def guardar_tarea(self, tarea: Tarea) -> Tarea:

        tarea_db = TareaDB(
        nombre=tarea.nombre,
        completada=tarea.completada
        )

        self.db.add(tarea_db)

        self.db.commit()

        self.db.refresh(tarea_db)

        return Tarea(
        id=tarea_db.id,
        nombre=tarea_db.nombre,
        completada=tarea_db.completada
        )

    def actualizar_tarea(self, tarea: Tarea) -> None:

        tarea_db = self.db.get(TareaDB, tarea.id)

        if tarea_db is None:
            return

        tarea_db.nombre = tarea.nombre
        tarea_db.completada = tarea.completada

        self.db.commit()

    def eliminar_tarea(self, id_tarea: int) -> bool:

        tarea_db = self.db.get(TareaDB, id_tarea)

        if tarea_db is None:
            return False

        self.db.delete(tarea_db)
        self.db.commit()

        return True