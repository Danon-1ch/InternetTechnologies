import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.main import app

pytestmark = pytest.mark.integration


def test_health_reports_database_up(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "up",
        "message": "Hello community, я не хочу быть вашей частью.",
    }


def test_health_reports_database_down(client):
    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise SQLAlchemyError("database is down")

    app.dependency_overrides[get_db] = BrokenSession
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
