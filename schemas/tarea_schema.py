from pydantic import BaseModel


class TareaRequest(BaseModel):
    nombre: str

class TareaResponse(BaseModel):
    id: int
    nombre: str
    completada: bool

class TareaUpdate(BaseModel):
    nombre: str
    completada: bool

class TareaPatch(BaseModel):
    nombre: str | None = None
    completada: bool | None = None
