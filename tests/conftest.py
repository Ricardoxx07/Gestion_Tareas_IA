import os
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from models.tarea_db import TareaDB
from models.usuario_db import UsuarioDB
from repository.tarea_repository_db import TareaRepositoryDB
from repository.usuario_repository_db import UsuarioRepositoryDB


load_dotenv(".env.test")


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if TEST_DATABASE_URL is None:
    raise RuntimeError("TEST_DATABASE_URL no está configurada")


test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)


@pytest.fixture(scope="session", autouse=True)
def crear_tablas():

    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():

    session = TestingSessionLocal()

    try:
        yield session

    finally:
        session.rollback()

        session.query(TareaDB).delete()
        session.query(UsuarioDB).delete()

        session.commit()
        session.close()


@pytest.fixture
def tarea_repository_db(db):
    return TareaRepositoryDB(db)


@pytest.fixture
def usuario_repository_db(db):
    return UsuarioRepositoryDB(db)


@pytest.fixture
def usuario_db(db):
    usuario = UsuarioDB(
        email=f"usuario-{uuid4()}@example.com",
        password_hash="hash-de-prueba"
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario
