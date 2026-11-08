import pytest

from tests.helpers import create_comment, create_project, create_task, create_user

pytestmark = pytest.mark.integration


def test_list_comments_is_empty(client):
    assert client.get("/v1/comments").json() == []


def test_create_comment(client):
    author = create_user(client)
    project = create_project(client)
    task = create_task(client, project["id"])

    comment = create_comment(client, task["id"], author["id"], body="On it")

    assert comment["task_id"] == task["id"]
    assert comment["author_id"] == author["id"]
    assert comment["body"] == "On it"
    assert comment["created_at"]


def test_get_comment(client):
    author = create_user(client)
    project = create_project(client)
    task = create_task(client, project["id"])
    comment = create_comment(client, task["id"], author["id"])

    response = client.get(f"/v1/comments/{comment['id']}")

    assert response.status_code == 200
    assert response.json()["body"] == comment["body"]


def test_list_comments_ordered_by_id(client):
    author = create_user(client)
    project = create_project(client)
    task = create_task(client, project["id"])
    first = create_comment(client, task["id"], author["id"])
    second = create_comment(client, task["id"], author["id"])

    comments = client.get("/v1/comments").json()

    assert [comment["id"] for comment in comments] == [first["id"], second["id"]]


def test_filter_comments_by_task(client):
    author = create_user(client)
    project = create_project(client)
    first_task = create_task(client, project["id"])
    second_task = create_task(client, project["id"])
    expected = create_comment(client, first_task["id"], author["id"])
    create_comment(client, second_task["id"], author["id"])

    comments = client.get(f"/v1/comments?task_id={first_task['id']}").json()

    assert [comment["id"] for comment in comments] == [expected["id"]]


def test_update_comment(client):
    author = create_user(client)
    project = create_project(client)
    task = create_task(client, project["id"])
    comment = create_comment(client, task["id"], author["id"])

    response = client.patch(f"/v1/comments/{comment['id']}", json={"body": "Edited"})

    assert response.status_code == 200
    assert response.json()["body"] == "Edited"


def test_update_comment_with_empty_payload_is_a_noop(client):
    author = create_user(client)
    project = create_project(client)
    task = create_task(client, project["id"])
    comment = create_comment(client, task["id"], author["id"])

    response = client.patch(f"/v1/comments/{comment['id']}", json={})

    assert response.status_code == 200
    assert response.json()["body"] == comment["body"]


def test_create_comment_with_unknown_task_returns_409(client):
    author = create_user(client)

    response = client.post(
        "/v1/comments",
        json={"task_id": 999, "author_id": author["id"], "body": "Orphan"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Invalid reference"


def test_create_comment_with_unknown_author_returns_409(client):
    project = create_project(client)
    task = create_task(client, project["id"])

    response = client.post(
        "/v1/comments",
        json={"task_id": task["id"], "author_id": 999, "body": "Orphan"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Invalid reference"


def test_delete_comment(client):
    author = create_user(client)
    project = create_project(client)
    task = create_task(client, project["id"])
    comment = create_comment(client, task["id"], author["id"])

    assert client.delete(f"/v1/comments/{comment['id']}").status_code == 204
    assert client.get(f"/v1/comments/{comment['id']}").status_code == 404


def test_missing_comment_returns_404(client):
    assert client.get("/v1/comments/999").status_code == 404
    assert client.patch("/v1/comments/999", json={"body": "Nobody"}).status_code == 404
    assert client.delete("/v1/comments/999").status_code == 404


@pytest.mark.parametrize("body", ["", None])
def test_invalid_comment_returns_422(client, body):
    response = client.post(
        "/v1/comments",
        json={"task_id": 1, "author_id": 1, "body": body},
    )

    assert response.status_code == 422
