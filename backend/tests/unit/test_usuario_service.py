import pytest

from exceptions.usuario_exceptions import (
    CredencialesInvalidasError,
    UsuarioYaExisteError,
)
from models.usuario import Usuario
from services.usuario_service import UsuarioService


class UsuarioRepositoryFalso:

    def __init__(self):
        self.usuarios: list[Usuario] = []
        self.siguiente_id = 1

    def obtener_por_email(self, email: str) -> Usuario | None:
        return next(
            (usuario for usuario in self.usuarios if usuario.email == email),
            None
        )

    def obtener_por_id(self, id_usuario: int) -> Usuario | None:
        return next(
            (usuario for usuario in self.usuarios if usuario.id == id_usuario),
            None
        )

    def guardar_usuario(self, usuario: Usuario) -> Usuario:
        usuario.id = self.siguiente_id
        self.siguiente_id += 1
        self.usuarios.append(usuario)
        return usuario


@pytest.fixture
def service(monkeypatch):
    monkeypatch.setattr(
        "services.usuario_service.hash_password",
        lambda password: f"hash-de-{password}"
    )
    monkeypatch.setattr(
        "services.usuario_service.verify_password",
        lambda password, password_hash: password_hash == f"hash-de-{password}"
    )
    return UsuarioService(UsuarioRepositoryFalso())


def test_registrar_usuario_guarda_email_normalizado_y_password_hasheada(service):
    usuario = service.registrar_usuario("  RICARDO@EXAMPLE.COM  ", "password-segura")

    assert usuario.id == 1
    assert usuario.email == "ricardo@example.com"
    assert usuario.password_hash == "hash-de-password-segura"


def test_registrar_usuario_con_email_duplicado_lanza_error(service):
    service.registrar_usuario("ricardo@example.com", "password-segura")

    with pytest.raises(UsuarioYaExisteError) as exc_info:
        service.registrar_usuario("RICARDO@example.com", "otra-password")

    assert str(exc_info.value) == "Ya existe un usuario registrado con ese email"


def test_autenticar_usuario_con_credenciales_validas(service):
    registrado = service.registrar_usuario("ricardo@example.com", "password-segura")

    usuario = service.autenticar_usuario("RICARDO@example.com", "password-segura")

    assert usuario == registrado


def test_autenticar_usuario_con_credenciales_invalidas_lanza_error(service):
    service.registrar_usuario("ricardo@example.com", "password-segura")

    with pytest.raises(CredencialesInvalidasError) as exc_info:
        service.autenticar_usuario("ricardo@example.com", "password-incorrecta")

    assert str(exc_info.value) == "Email o contraseña incorrectos"


def test_obtener_usuario_por_id(service):
    registrado = service.registrar_usuario("ricardo@example.com", "password-segura")

    assert service.obtener_usuario_por_id(registrado.id) == registrado
