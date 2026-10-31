import pytest
from pydantic import ValidationError

from app import schemas

pytestmark = pytest.mark.unit


def test_user_create_defaults_role_to_operator():
    user = schemas.UserCreate(email="alice@example.com", display_name="Alice")
    assert user.role == "operator"


def test_user_update_is_fully_optional():
    assert schemas.UserUpdate().model_dump() == {
        "email": None,
        "display_name": None,
        "role": None,
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "ab", "display_name": "Alice"},
        {"email": "alice@example.com", "display_name": ""},
        {"email": "alice@example.com", "display_name": "Alice", "role": "owner"},
    ],
)
def test_user_create_rejects_invalid_payload(payload):
    with pytest.raises(ValidationError):
        schemas.UserCreate(**payload)


def test_user_update_rejects_invalid_role():
    with pytest.raises(ValidationError):
        schemas.UserUpdate(role="owner")


def test_project_create_and_update():
    project = schemas.ProjectCreate(name="TaskFlow")
    assert project.description is None
    assert schemas.ProjectUpdate().model_dump() == {"name": None, "description": None}


def test_project_rejects_empty_name():
    with pytest.raises(ValidationError):
        schemas.ProjectCreate(name="")


def test_label_create_defaults_color():
    label = schemas.LabelCreate(name="bug")
    assert label.color == "#6b7280"


@pytest.mark.parametrize("color", ["6b7280", "#xyzxyz", "#12345"])
def test_label_rejects_invalid_color(color):
    with pytest.raises(ValidationError):
        schemas.LabelCreate(name="bug", color=color)
    with pytest.raises(ValidationError):
        schemas.LabelUpdate(color=color)


def test_task_create_defaults():
    task = schemas.TaskCreate(project_id=1, title="Ship it")
    assert task.status == "open"
    assert task.priority == "medium"
    assert task.assignee_id is None
    assert task.label_id is None


@pytest.mark.parametrize(
    "payload",
    [
        {"project_id": 1, "title": ""},
        {"project_id": 1, "title": "Ship it", "status": "blocked"},
        {"project_id": 1, "title": "Ship it", "priority": "urgent"},
    ],
)
def test_task_create_rejects_invalid_payload(payload):
    with pytest.raises(ValidationError):
        schemas.TaskCreate(**payload)


def test_task_update_accepts_partial_payload():
    update = schemas.TaskUpdate(status="done")
    assert update.model_dump(exclude_unset=True) == {"status": "done"}


def test_comment_payloads():
    comment = schemas.CommentCreate(task_id=1, author_id=2, body="Hi")
    assert comment.body == "Hi"
    assert schemas.CommentUpdate().model_dump() == {"body": None}
    with pytest.raises(ValidationError):
        schemas.CommentCreate(task_id=1, author_id=2, body="")
    with pytest.raises(ValidationError):
        schemas.CommentUpdate(body="")
