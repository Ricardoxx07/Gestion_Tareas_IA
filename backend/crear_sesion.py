from sqlalchemy import text
#Importa la fábrica de sesiones. Una Session gestiona la transacción (hacer consultas, añadir o borrar objetos).
from database.database import SessionLocal


db = SessionLocal()
#Garantiza que la sesión se cierre y devuelva su conexión al pool, incluso si ocurre un error.
try:
    resultado = db.execute(text("SELECT 1"))

    print("Sesión creada correctamente")
    print("Resultado:", resultado.scalar())

finally:
    db.close()