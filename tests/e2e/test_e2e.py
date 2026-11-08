import socket
import threading
import time

import httpx
import pytest
import uvicorn

from app.main import app
from tests.helpers import (
    create_comment,
    create_label,
    create_project,
    create_task,
    create_user,
)

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="session")
def live_server(database):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="error",
        log_config=None,
        access_log=False,
        lifespan="off",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.01)
    assert server.started, "uvicorn did not start"

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=10)


@pytest.fixture
def http(live_server, clean_tables):
    with httpx.Client(base_url=live_server, timeout=10) as client:
        yield client


def test_full_task_lifecycle_over_http(http):
    health = http.get("/health")
    assert health.status_code == 200
    assert health.json()["database"] == "up"

    author = create_user(http, email="e2e@example.com", display_name="E2E")
    project = create_project(http, name="E2E project")
    label = create_label(http, name="e2e-label", color="#123abc")
    task = create_task(
        http,
        project["id"],
        assignee_id=author["id"],
        label_id=label["id"],
        title="Ship it",
        priority="high",
    )
    comment = create_comment(http, task["id"], author["id"], body="On it")

    filtered = http.get(f"/v1/tasks?project_id={project['id']}&status=open").json()
    assert [item["id"] for item in filtered] == [task["id"]]

    updated = http.patch(f"/v1/tasks/{task['id']}", json={"status": "done"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "done"

    comments = http.get(f"/v1/comments?task_id={task['id']}").json()
    assert [item["id"] for item in comments] == [comment["id"]]

    assert http.delete(f"/v1/projects/{project['id']}").status_code == 204
    assert http.get(f"/v1/tasks/{task['id']}").status_code == 404
    assert http.get(f"/v1/comments/{comment['id']}").status_code == 404


def test_openapi_and_docs_are_served(http):
    schema = http.get("/openapi.json")
    assert schema.status_code == 200
    assert "/health" in schema.json()["paths"]
    assert http.get("/docs").status_code == 200


def test_error_contract_over_http(http):
    assert http.get("/v1/tasks/999").status_code == 404

    create_user(http, email="duplicate-e2e@example.com")
    duplicate = http.post(
        "/v1/users",
        json={"email": "duplicate-e2e@example.com", "display_name": "Duplicate"},
    )
    assert duplicate.status_code == 409

    assert http.post("/v1/tasks", json={"title": "No project"}).status_code == 422
    assert http.post("/v1/projects", json={"name": ""}).status_code == 422
