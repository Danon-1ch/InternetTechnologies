import pytest

pytestmark = pytest.mark.integration


def test_health_reports_database_up(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "up",
        "message": "Hello community, я не хочу быть вашей частью.",
    }
