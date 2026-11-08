import pytest

from tests.helpers import create_comment, create_project, create_task, create_user

pytestmark = pytest.mark.integration


def test_list_users_is_empty(client):
    assert client.get("/v1/users").json() == []


def test_create_user_defaults_to_operator(client):
    user = create_user(client, email="alice@example.com", display_name="Alice")

    assert user["id"] >= 1
    assert user["email"] == "alice@example.com"
    assert user["display_name"] == "Alice"
    assert user["role"] == "operator"
    assert user["created_at"]


def test_get_user(client):
    user = create_user(client)

    response = client.get(f"/v1/users/{user['id']}")

    assert response.status_code == 200
    assert response.json()["email"] == user["email"]


def test_list_users_ordered_by_id(client):
    first = create_user(client)
    second = create_user(client)

    users = client.get("/v1/users").json()

    assert [user["id"] for user in users] == [first["id"], second["id"]]


def test_update_user(client):
    user = create_user(client)

    response = client.patch(
        f"/v1/users/{user['id']}",
        json={"display_name": "Bob", "role": "admin"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["display_name"] == "Bob"
    assert body["role"] == "admin"
    assert body["email"] == user["email"]


def test_update_user_with_empty_payload_is_a_noop(client):
    user = create_user(client)

    response = client.patch(f"/v1/users/{user['id']}", json={})

    assert response.status_code == 200
    assert response.json()["display_name"] == user["display_name"]


def test_create_duplicate_email_returns_409(client):
    create_user(client, email="duplicate@example.com")

    response = client.post(
        "/v1/users",
        json={"email": "duplicate@example.com", "display_name": "Other"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Duplicate value"


def test_update_to_duplicate_email_returns_409(client):
    first = create_user(client, email="first@example.com")
    create_user(client, email="second@example.com")

    response = client.patch(f"/v1/users/{first['id']}", json={"email": "second@example.com"})

    assert response.status_code == 409
    assert response.json()["detail"] == "Duplicate value"


def test_delete_user(client):
    user = create_user(client)

    assert client.delete(f"/v1/users/{user['id']}").status_code == 204
    assert client.get(f"/v1/users/{user['id']}").status_code == 404


def test_delete_author_with_comments_returns_409(client):
    author = create_user(client)
    project = create_project(client)
    task = create_task(client, project["id"])
    create_comment(client, task["id"], author["id"])

    response = client.delete(f"/v1/users/{author['id']}")

    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot delete: related records exist"


def test_missing_user_returns_404(client):
    assert client.get("/v1/users/999").status_code == 404
    assert client.patch("/v1/users/999", json={"display_name": "Nobody"}).status_code == 404
    assert client.delete("/v1/users/999").status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "ab", "display_name": "Alice"},
        {"email": "alice@example.com", "display_name": ""},
        {"email": "alice@example.com", "display_name": "Alice", "role": "owner"},
    ],
)
def test_invalid_user_returns_422(client, payload):
    assert client.post("/v1/users", json=payload).status_code == 422
