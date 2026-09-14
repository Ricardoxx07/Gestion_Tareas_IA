import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from api.dependencies import obtener_usuario_service
from api.main import app
from config.settings import settings
from exceptions.usuario_exceptions import (
    CredencialesInvalidasError,
    UsuarioYaExisteError,
)
from models.usuario import Usuario


class UsuarioServiceFalso:

    def __init__(self):
        self.usuario = Usuario(
            id=1,
            email="ricardo@example.com",
            password_hash="hash-interno"
        )

    def registrar_usuario(self, email: str, password: str) -> Usuario:
        if email == "existente@example.com":
            raise UsuarioYaExisteError(
                "Ya existe un usuario registrado con ese email"
            )

        return Usuario(id=1, email=email, password_hash="hash-interno")

    def autenticar_usuario(self, email: str, password: str) -> Usuario:
        if email != self.usuario.email or password != "password-segura":
            raise CredencialesInvalidasError("Email o contraseña incorrectos")

        return self.usuario

    def obtener_usuario_por_id(self, id_usuario: int) -> Usuario | None:
        if id_usuario == self.usuario.id:
            return self.usuario

        return None


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    app.dependency_overrides[obtener_usuario_service] = UsuarioServiceFalso
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver"
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_registrar_usuario(client):
    response = await client.post(
        "/auth/registro",
        json={"email": "nuevo@example.com", "password": "password-segura"}
    )

    assert response.status_code == 201
    assert response.json() == {"id": 1, "email": "nuevo@example.com"}


@pytest.mark.anyio
async def test_registrar_usuario_duplicado(client):
    response = await client.post(
        "/auth/registro",
        json={"email": "existente@example.com", "password": "password-segura"}
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Ya existe un usuario registrado con ese email"
    }


@pytest.mark.anyio
async def test_login_devuelve_jwt(client):
    response = await client.post(
        "/auth/login",
        json={"email": "ricardo@example.com", "password": "password-segura"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    payload = jwt.decode(
        body["access_token"],
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["sub"] == "1"


@pytest.mark.anyio
async def test_login_con_credenciales_invalidas(client):
    response = await client.post(
        "/auth/login",
        json={"email": "ricardo@example.com", "password": "otra-password"}
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {"detail": "Email o contraseña incorrectos"}


@pytest.mark.anyio
async def test_obtener_usuario_actual(client):
    login = await client.post(
        "/auth/login",
        json={"email": "ricardo@example.com", "password": "password-segura"}
    )

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )

    assert response.status_code == 200
    assert response.json() == {"id": 1, "email": "ricardo@example.com"}


@pytest.mark.anyio
async def test_obtener_usuario_actual_sin_token(client):
    response = await client.get("/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {
        "detail": "No se pudieron validar las credenciales"
    }


@pytest.mark.anyio
async def test_obtener_usuario_actual_con_token_invalido(client):
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer token-invalido"}
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "No se pudieron validar las credenciales"
    }
