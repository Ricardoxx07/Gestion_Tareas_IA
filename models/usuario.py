from dataclasses import dataclass


@dataclass
class Usuario:
    """Representa un usuario dentro de las capas de dominio y persistencia.

    ``password_hash`` nunca debe enviarse en una respuesta HTTP.
    """

    email: str
    password_hash: str
    id: int | None = None
