import pytest
from pydantic import ValidationError

from schemas.usuario_schema import UsuarioLogin, UsuarioRegistro, UsuarioResponse


def test_usuario_registro_normaliza_email():
    datos = UsuarioRegistro(
        email="  RICARDO@EXAMPLE.COM  ",
        password="password-segura"
    )

    assert datos.email == "ricardo@example.com"


@pytest.mark.parametrize("email", ["invalido", "usuario@", "@example.com"])
def test_usuario_registro_rechaza_email_invalido(email):
    with pytest.raises(ValidationError):
        UsuarioRegistro(email=email, password="password-segura")


def test_usuario_registro_rechaza_contrasena_corta():
    with pytest.raises(ValidationError):
        UsuarioRegistro(email="ricardo@example.com", password="corta")


def test_usuario_login_normaliza_email():
    datos = UsuarioLogin(
        email="  RICARDO@EXAMPLE.COM  ",
        password="password-segura"
    )

    assert datos.email == "ricardo@example.com"


def test_usuario_response_no_expone_password_hash():
    response = UsuarioResponse(id=1, email="ricardo@example.com")

    assert response.model_dump() == {"id": 1, "email": "ricardo@example.com"}
