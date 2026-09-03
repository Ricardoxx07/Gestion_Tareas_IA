from models.usuario import Usuario


def test_guardar_y_obtener_usuario_por_email(usuario_repository_db):
    usuario = Usuario(
        email="ricardo@example.com",
        password_hash="hash-de-prueba"
    )

    guardado = usuario_repository_db.guardar_usuario(usuario)
    encontrado = usuario_repository_db.obtener_por_email("ricardo@example.com")

    assert guardado.id is not None
    assert encontrado is not None
    assert encontrado.id == guardado.id
    assert encontrado.email == "ricardo@example.com"
    assert encontrado.password_hash == "hash-de-prueba"


def test_obtener_usuario_por_id(usuario_repository_db):
    guardado = usuario_repository_db.guardar_usuario(
        Usuario(
            email="ricardo@example.com",
            password_hash="hash-de-prueba"
        )
    )

    encontrado = usuario_repository_db.obtener_por_id(guardado.id)

    assert encontrado == guardado


def test_obtener_usuario_inexistente_retorna_none(usuario_repository_db):
    assert usuario_repository_db.obtener_por_email("noexiste@example.com") is None
    assert usuario_repository_db.obtener_por_id(999) is None
