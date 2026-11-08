import pytest

from tests.helpers import create_comment, create_label, create_project, create_task, create_user

pytestmark = pytest.mark.integration


def test_list_tasks_is_empty(client):
    assert client.get("/v1/tasks").json() == []


def test_create_task_defaults(client):
    project = create_project(client)

    task = create_task(client, project["id"], title="Ship it")

    assert task["project_id"] == project["id"]
    assert task["title"] == "Ship it"
    assert task["status"] == "open"
    assert task["priority"] == "medium"
    assert task["assignee_id"] is None
    assert task["label_id"] is None
    assert task["created_at"]
    assert task["updated_at"]


def test_create_task_with_relations(client):
    project = create_project(client)
    assignee = create_user(client)
    label = create_label(client)

    task = create_task(
        client,
        project["id"],
        assignee_id=assignee["id"],
        label_id=label["id"],
    )

    assert task["assignee_id"] == assignee["id"]
    assert task["label_id"] == label["id"]


def test_get_task(client):
    project = create_project(client)
    task = create_task(client, project["id"])

    response = client.get(f"/v1/tasks/{task['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == task["title"]


def test_list_tasks_ordered_by_id(client):
    project = create_project(client)
    first = create_task(client, project["id"])
    second = create_task(client, project["id"])

    tasks = client.get("/v1/tasks").json()

    assert [task["id"] for task in tasks] == [first["id"], second["id"]]


def test_filter_tasks_by_project(client):
    first_project = create_project(client)
    second_project = create_project(client)
    first = create_task(client, first_project["id"])
    create_task(client, second_project["id"])

    tasks = client.get(f"/v1/tasks?project_id={first_project['id']}").json()

    assert [task["id"] for task in tasks] == [first["id"]]


def test_filter_tasks_by_status(client):
    project = create_project(client)
    open_task = create_task(client, project["id"])
    done_task = create_task(client, project["id"], status="done")

    tasks = client.get("/v1/tasks?status=done").json()

    assert [task["id"] for task in tasks] == [done_task["id"]]
    assert open_task["status"] == "open"


def test_filter_tasks_by_project_and_status(client):
    project = create_project(client)
    other_project = create_project(client)
    create_task(client, project["id"], status="done")
    expected = create_task(client, project["id"], status="in_progress")
    create_task(client, other_project["id"], status="in_progress")

    tasks = client.get(f"/v1/tasks?project_id={project['id']}&status=in_progress").json()

    assert [task["id"] for task in tasks] == [expected["id"]]


def test_filter_tasks_by_unknown_status_returns_empty_list(client):
    project = create_project(client)
    create_task(client, project["id"])

    assert client.get("/v1/tasks?status=blocked").json() == []


def test_update_task(client):
    project = create_project(client)
    assignee = create_user(client)
    label = create_label(client)
    task = create_task(client, project["id"])

    response = client.patch(
        f"/v1/tasks/{task['id']}",
        json={
            "title": "Renamed",
            "description": "Details",
            "status": "done",
            "priority": "high",
            "assignee_id": assignee["id"],
            "label_id": label["id"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Renamed"
    assert body["description"] == "Details"
    assert body["status"] == "done"
    assert body["priority"] == "high"
    assert body["assignee_id"] == assignee["id"]
    assert body["label_id"] == label["id"]


def test_update_task_with_empty_payload_is_a_noop(client):
    project = create_project(client)
    task = create_task(client, project["id"])

    response = client.patch(f"/v1/tasks/{task['id']}", json={})

    assert response.status_code == 200
    assert response.json()["title"] == task["title"]


def test_delete_task_cascades_comments(client):
    author = create_user(client)
    project = create_project(client)
    task = create_task(client, project["id"])
    comment = create_comment(client, task["id"], author["id"])

    assert client.delete(f"/v1/tasks/{task['id']}").status_code == 204

    assert client.get(f"/v1/tasks/{task['id']}").status_code == 404
    assert client.get(f"/v1/comments/{comment['id']}").status_code == 404


def test_create_task_with_unknown_project_returns_409(client):
    response = client.post(
        "/v1/tasks",
        json={"project_id": 999, "title": "Orphan"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Invalid reference"


def test_create_task_with_unknown_assignee_returns_409(client):
    project = create_project(client)

    response = client.post(
        "/v1/tasks",
        json={"project_id": project["id"], "title": "Orphan", "assignee_id": 999},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Invalid reference"


def test_create_task_with_unknown_label_returns_409(client):
    project = create_project(client)

    response = client.post(
        "/v1/tasks",
        json={"project_id": project["id"], "title": "Orphan", "label_id": 999},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Invalid reference"


def test_update_task_with_unknown_assignee_returns_409(client):
    project = create_project(client)
    task = create_task(client, project["id"])

    response = client.patch(f"/v1/tasks/{task['id']}", json={"assignee_id": 999})

    assert response.status_code == 409
    assert response.json()["detail"] == "Invalid reference"


def test_missing_task_returns_404(client):
    assert client.get("/v1/tasks/999").status_code == 404
    assert client.patch("/v1/tasks/999", json={"title": "Nobody"}).status_code == 404
    assert client.delete("/v1/tasks/999").status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"project_id": 1, "title": ""},
        {"project_id": 1, "title": "Ship it", "status": "blocked"},
        {"project_id": 1, "title": "Ship it", "priority": "urgent"},
    ],
)
def test_invalid_task_returns_422(client, payload):
    assert client.post("/v1/tasks", json=payload).status_code == 422
