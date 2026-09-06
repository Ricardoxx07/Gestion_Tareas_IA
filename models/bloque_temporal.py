from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class BloqueTemporal:
    """Fragmento del texto asociado a una fecha calculada por el backend."""

    id: int
    texto: str
    fecha: date | None
