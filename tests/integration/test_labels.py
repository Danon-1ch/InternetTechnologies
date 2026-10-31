import pytest

from tests.helpers import create_label

pytestmark = pytest.mark.integration


def test_list_labels_is_empty(client):
    assert client.get("/v1/labels").json() == []


def test_create_label(client):
    label = create_label(client, name="bug", color="#ff0000")

    assert label["id"] >= 1
    assert label["name"] == "bug"
    assert label["color"] == "#ff0000"


def test_create_label_defaults_color(client):
    label = create_label(client)

    assert label["color"] == "#6b7280"


def test_get_label(client):
    label = create_label(client)

    response = client.get(f"/v1/labels/{label['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == label["name"]


def test_list_labels_ordered_by_id(client):
    first = create_label(client)
    second = create_label(client)

    labels = client.get("/v1/labels").json()

    assert [label["id"] for label in labels] == [first["id"], second["id"]]


def test_update_label(client):
    label = create_label(client)

    response = client.patch(
        f"/v1/labels/{label['id']}",
        json={"name": "feature", "color": "#00ff00"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "feature"
    assert response.json()["color"] == "#00ff00"


def test_update_label_with_empty_payload_is_a_noop(client):
    label = create_label(client)

    response = client.patch(f"/v1/labels/{label['id']}", json={})

    assert response.status_code == 200
    assert response.json()["name"] == label["name"]


def test_create_duplicate_label_returns_409(client):
    create_label(client, name="duplicate")

    response = client.post("/v1/labels", json={"name": "duplicate", "color": "#123456"})

    assert response.status_code == 409
    assert response.json()["detail"] == "Duplicate value"


def test_update_to_duplicate_label_returns_409(client):
    first = create_label(client, name="first")
    create_label(client, name="second")

    response = client.patch(f"/v1/labels/{first['id']}", json={"name": "second"})

    assert response.status_code == 409
    assert response.json()["detail"] == "Duplicate value"


def test_delete_label(client):
    label = create_label(client)

    assert client.delete(f"/v1/labels/{label['id']}").status_code == 204
    assert client.get(f"/v1/labels/{label['id']}").status_code == 404


def test_missing_label_returns_404(client):
    assert client.get("/v1/labels/999").status_code == 404
    assert client.patch("/v1/labels/999", json={"name": "Nobody"}).status_code == 404
    assert client.delete("/v1/labels/999").status_code == 404


@pytest.mark.parametrize("color", ["6b7280", "#xyzxyz"])
def test_invalid_label_returns_422(client, color):
    assert client.post("/v1/labels", json={"name": "bad", "color": color}).status_code == 422
