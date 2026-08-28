import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from models.tarea_db import TareaDB
from repository.tarea_repository_db import TareaRepositoryDB


load_dotenv()


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

    #Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():

    session = TestingSessionLocal()

    try:
        yield session

    finally:
        session.rollback()

        session.query(TareaDB).delete()

        session.commit()
        session.close()


@pytest.fixture
def tarea_repository_db(db):

    return TareaRepositoryDB(db)