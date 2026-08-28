#Importa los tipos de datos que tendrá la tabla SQL.
from sqlalchemy import Boolean, Integer, String

#La forma moderna en SQLAlchemy 2.0 para definir columnas vinculando tipos de Python con tipos SQL.
from sqlalchemy.orm import Mapped, mapped_column

#Clase base de la cual deben heredar todos los modelos ORM para ser reconocidos.
from database.database import Base


class TareaDB(Base):
    #Define el nombre exacto que tendrá la tabla en PostgreSQL.
    __tablename__ = "tareas"

    #Llave primaria (primary_key=True) e indexada para búsquedas rápidas (index=True).
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    #Cadena de texto de máximo 255 caracteres, obligatoria (nullable=False).
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    
    #Booleano obligatorio que inicia por defecto en False.
    completada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    