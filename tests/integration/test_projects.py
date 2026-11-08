import pytest

from tests.helpers import create_comment, create_project, create_task, create_user

pytestmark = pytest.mark.integration


def test_list_projects_is_empty(client):
    assert client.get("/v1/projects").json() == []


def test_create_project(client):
    project = create_project(client, name="TaskFlow", description="Team work")

    assert project["id"] >= 1
    assert project["name"] == "TaskFlow"
    assert project["description"] == "Team work"
    assert project["created_at"]


def test_create_project_without_description(client):
    project = create_project(client)

    assert project["description"] is None


def test_get_project(client):
    project = create_project(client)

    response = client.get(f"/v1/projects/{project['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == project["name"]


def test_list_projects_ordered_by_id(client):
    first = create_project(client)
    second = create_project(client)

    projects = client.get("/v1/projects").json()

    assert [project["id"] for project in projects] == [first["id"], second["id"]]


def test_update_project(client):
    project = create_project(client)

    response = client.patch(
        f"/v1/projects/{project['id']}",
        json={"name": "Renamed", "description": "New description"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"
    assert response.json()["description"] == "New description"


def test_update_project_with_empty_payload_is_a_noop(client):
    project = create_project(client)

    response = client.patch(f"/v1/projects/{project['id']}", json={})

    assert response.status_code == 200
    assert response.json()["name"] == project["name"]


def test_delete_project_cascades_tasks_and_comments(client):
    author = create_user(client)
    project = create_project(client)
    task = create_task(client, project["id"])
    comment = create_comment(client, task["id"], author["id"])

    assert client.delete(f"/v1/projects/{project['id']}").status_code == 204

    assert client.get(f"/v1/projects/{project['id']}").status_code == 404
    assert client.get(f"/v1/tasks/{task['id']}").status_code == 404
    assert client.get(f"/v1/comments/{comment['id']}").status_code == 404


def test_missing_project_returns_404(client):
    assert client.get("/v1/projects/999").status_code == 404
    assert client.patch("/v1/projects/999", json={"name": "Nobody"}).status_code == 404
    assert client.delete("/v1/projects/999").status_code == 404


def test_invalid_project_returns_422(client):
    assert client.post("/v1/projects", json={"name": ""}).status_code == 422
