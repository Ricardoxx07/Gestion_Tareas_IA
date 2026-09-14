from datetime import timedelta

from security.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_no_guarda_la_contrasena_en_texto_plano():
    password = "password-segura"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True


def test_verify_password_rechaza_contrasena_incorrecta():
    password_hash = hash_password("password-segura")

    assert verify_password("password-incorrecta", password_hash) is False


def test_decode_access_token_recupera_el_subject():
    token = create_access_token({"sub": "123"})

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "123"
    assert "exp" in payload


def test_decode_access_token_rechaza_un_token_expirado():
    token = create_access_token(
        {"sub": "123"},
        expires_delta=timedelta(seconds=-1)
    )

    assert decode_access_token(token) is None


def test_decode_access_token_rechaza_un_token_malformado():
    assert decode_access_token("token-invalido") is None
