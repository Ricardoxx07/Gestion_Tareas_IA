from dataclasses import dataclass
from datetime import date, datetime

#Este @dataclass lo que hace es facilitar y optimizar el código, haciendo que el constructor  __init__ y el __repr__ ya exista.

@dataclass
class Tarea:
    nombre: str
    completada: bool = False
    id: int | None = None
    usuario_id: int | None = None
    fecha_limite: date | None = None
    prioridad: str = "media"
    created_at: datetime | None = None
    tarea_padre_id: int | None = None
