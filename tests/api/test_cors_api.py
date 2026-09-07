from fastapi.testclient import TestClient

from api.main import app


def test_preflight_permite_un_origen_configurado():
    client = TestClient(app)

    response = client.options(
        "/tareas",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization, Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "POST" in response.headers["access-control-allow-methods"]
