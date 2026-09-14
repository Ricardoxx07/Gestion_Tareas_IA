from database.database import engine, Base

#Es imprescindible importar el modelo aquí para que Base conozca su existencia.
from models.tarea_db import TareaDB

#Lee todos los modelos registrados en Base y genera en PostgreSQL la sentencia CREATE TABLE IF NOT EXISTS tareas (...).
Base.metadata.create_all(bind=engine)

print("Tabla creada correctamente")