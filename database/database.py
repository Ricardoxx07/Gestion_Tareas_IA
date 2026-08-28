import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# Carga las variables del archivo .env
load_dotenv()


# Obtiene la URL de conexión desde la variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL no está configurada")


# Engine: conexión/configuración que SQLAlchemy utiliza
# para comunicarse con PostgreSQL.
engine = create_engine(DATABASE_URL)


# Fábrica de sesiones.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# Clase base de los modelos SQLAlchemy.
class Base(DeclarativeBase):
    pass


# Dependencia que posteriormente utilizaremos con FastAPI.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
