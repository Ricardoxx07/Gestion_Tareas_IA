from abc import ABC, abstractmethod

from models.usuario import Usuario


class UsuarioRepositoryInterface(ABC):

    @abstractmethod
    def obtener_por_id(self, id_usuario: int) -> Usuario | None:
        pass

    @abstractmethod
    def obtener_por_email(self, email: str) -> Usuario | None:
        pass

    @abstractmethod
    def guardar_usuario(self, usuario: Usuario) -> Usuario:
        pass
