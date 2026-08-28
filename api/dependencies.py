from database.database import SessionLocal
from repository.tarea_repository_db import TareaRepositoryDB
from services.tarea_service import TareaService


def obtener_service() -> TareaService:
    db = SessionLocal()

    try:
        repository = TareaRepositoryDB(db)

        yield TareaService(repository)

    finally:
        db.close()