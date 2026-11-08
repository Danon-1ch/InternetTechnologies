import os
from collections.abc import Iterator

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

# Must be set before the app imports its settings/engine.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://taskflow:taskflow@localhost:5432/taskflow_test",
)

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def clean_tables(database):
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE users, projects, labels, tasks, comments RESTART IDENTITY CASCADE"))


@pytest.fixture
def client(clean_tables) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def session(clean_tables) -> Iterator[Session]:
    with Session(engine) as db_session:
        yield db_session
