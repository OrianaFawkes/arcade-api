import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.models import Base

from fastapi.testclient import TestClient

from main import app
from app.core.database import get_db

from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def test_engine():
    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        pytest.fail(
            "TEST_DATABASE_URL must be configured "
            "to run database integration tests."
        )

    url = make_url(database_url)

    # Safety check: never let integration tests run
    # against the development or production database.
    if url.database != "arcade_test":
        pytest.fail(
            "Integration tests must use the arcade_test database."
        )

    if url.host not in {"localhost", "127.0.0.1", "::1"}:
        pytest.fail(
            "Integration tests must use a local database."
        )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    # Create the tables from our SQLAlchemy models.
    Base.metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    original_overrides = app.dependency_overrides.copy()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
