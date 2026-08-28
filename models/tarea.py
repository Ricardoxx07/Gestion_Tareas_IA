from dataclasses import dataclass

#Este @dataclass lo que hace es facilitar y optimizar el código, haciendo que el constructor  __init__ y el __repr__ ya exista.

@dataclass
class Tarea:
    nombre: str
    completada: bool= False

    def __init__(
        self,
        nombre: str,
        completada: bool = False,
        id: int | None = None
    ):
        self.id = id
        self.nombre = nombre
        self.completada = completada
        