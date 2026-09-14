#Permite escribir consultas SQL puras en formato de texto dentro de SQLAlchemy.
from sqlalchemy import text

#Importa el engine (motor de conexión), que administra el grupo de conexiones físicas a PostgreSQL.
from database.database import engine  # ===== Motor de conexión.

#Abre una conexión directa, la cual se cierra automáticamente al salir del bloque with.
with engine.connect() as connection:
    #Ejecuta una consulta SQL nativa para pedir la versión de PostgreSQL.
    resultado = connection.execute(text("SELECT version()"))

    print("Conexión exitosa")
    #Extrae el primer valor de la primera fila obtenida (el texto de la versión).
    print(resultado.scalar())