from exceptions.usuario_exceptions import (
    CredencialesInvalidasError,
    UsuarioYaExisteError,
)
from models.usuario import Usuario
from repository.usuario_repository_interface import UsuarioRepositoryInterface
from security.security import hash_password, verify_password


class UsuarioService:

    def __init__(self, repository: UsuarioRepositoryInterface):
        self.repository = repository

    def registrar_usuario(self, email: str, password: str) -> Usuario:
        email_normalizado = email.strip().lower()

        if self.repository.obtener_por_email(email_normalizado) is not None:
            raise UsuarioYaExisteError(
                "Ya existe un usuario registrado con ese email"
            )

        usuario = Usuario(
            email=email_normalizado,
            password_hash=hash_password(password)
        )

        return self.repository.guardar_usuario(usuario)

    def autenticar_usuario(self, email: str, password: str) -> Usuario:
        email_normalizado = email.strip().lower()
        usuario = self.repository.obtener_por_email(email_normalizado)

        if usuario is None or not verify_password(
            password,
            usuario.password_hash
        ):
            raise CredencialesInvalidasError("Email o contraseña incorrectos")

        return usuario

    def obtener_usuario_por_id(self, id_usuario: int) -> Usuario | None:
        return self.repository.obtener_por_id(id_usuario)
