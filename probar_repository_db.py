from database.database import SessionLocal
from models.tarea import Tarea
from repository.tarea_repository_db import TareaRepositoryDB

db = SessionLocal()

try:
    repository = TareaRepositoryDB(db)

    ## 1. Prepara datos en memoria
    tareas = [
        Tarea(
        id=1,
        nombre="Estudiar Python",
        completada=False
        ),
        Tarea(
        id=2,
        nombre="Aprender FastAPI",
        completada=True
        )
    ]
    ## 2. Persiste en la base de datos
    repository.guardar_tareas(tareas)
    
    ## 3. Consulta lo guardado para verificar
    tareas_cargadas = repository.cargar_tareas()

    print("Tareas cargadas desde PostgreSQL:")

    for tarea in tareas_cargadas:
        print(
        tarea.id,
        tarea.nombre,
        tarea.completada
        )


finally:
    db.close() # Garantiza liberar recursos
