import pytest

from api import dependencies


def test_obtener_proveedor_ia_crea_groq_con_la_configuracion(monkeypatch):
    configuracion = {
        "IA_PROVIDER": "groq",
        "GROQ_API_KEY": "clave-de-prueba",
        "GROQ_MODEL": "modelo-de-prueba",
        "GROQ_TIMEOUT_SECONDS": 12.0,
        "GROQ_MAX_TOKENS": 321,
    }
    for nombre, valor in configuracion.items():
        monkeypatch.setattr(dependencies.settings, nombre, valor)

    class GroqFalso:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(dependencies, "ProveedorGroq", GroqFalso)

    proveedor = dependencies.obtener_proveedor_ia()

    assert proveedor.kwargs == {
        "api_key": "clave-de-prueba",
        "modelo": "modelo-de-prueba",
        "timeout": 12.0,
        "max_tokens": 321,
    }


def test_obtener_proveedor_ia_exige_clave_para_groq(monkeypatch):
    monkeypatch.setattr(dependencies.settings, "IA_PROVIDER", "groq")
    monkeypatch.setattr(dependencies.settings, "GROQ_API_KEY", None)

    with pytest.raises(
        ValueError,
        match="GROQ_API_KEY es obligatoria cuando IA_PROVIDER=groq",
    ):
        dependencies.obtener_proveedor_ia()
