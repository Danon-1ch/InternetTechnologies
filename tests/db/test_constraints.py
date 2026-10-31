import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from app import models

pytestmark = pytest.mark.db


def _graph(session):
    author = models.User(email="author@example.com", display_name="Author")
    assignee = models.User(email="assignee@example.com", display_name="Assignee")
    project = models.Project(name="Project")
    label = models.Label(name="bug")
    session.add_all([author, assignee, project, label])
    session.flush()

    task = models.Task(
        project_id=project.id,
        assignee_id=assignee.id,
        label_id=label.id,
        title="Task",
    )
    session.add(task)
    session.flush()

    comment = models.Comment(task_id=task.id, author_id=author.id, body="Hi")
    session.add(comment)
    session.commit()
    return author, assignee, project, label, task, comment


def test_server_defaults_are_applied(session):
    user = models.User(email="default@example.com", display_name="Default")
    project = models.Project(name="Project")
    session.add_all([user, project])
    session.flush()
    task = models.Task(project_id=project.id, title="Task")
    session.add(task)
    session.commit()
    session.refresh(user)
    session.refresh(task)

    assert user.role == "operator"
    assert user.created_at is not None
    assert task.status == "open"
    assert task.priority == "medium"
    assert task.created_at is not None
    assert task.updated_at is not None


def test_invalid_role_is_rejected(session):
    session.add(models.User(email="owner@example.com", display_name="Owner", role="owner"))

    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


@pytest.mark.parametrize(
    "overrides",
    [
        {"status": "blocked"},
        {"priority": "urgent"},
    ],
)
def test_invalid_task_enums_are_rejected(session, overrides):
    project = models.Project(name="Project")
    session.add(project)
    session.flush()
    session.add(models.Task(project_id=project.id, title="Task", **overrides))

    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_duplicate_email_is_rejected(session):
    session.add(models.User(email="dup@example.com", display_name="One"))
    session.commit()
    session.add(models.User(email="dup@example.com", display_name="Two"))

    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_duplicate_label_name_is_rejected(session):
    session.add(models.Label(name="dup"))
    session.commit()
    session.add(models.Label(name="dup"))

    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_task_requires_existing_project(session):
    session.add(models.Task(project_id=999, title="Orphan"))

    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_deleting_project_cascades_to_tasks_and_comments(session):
    _, _, project, _, _, _ = _graph(session)

    session.delete(project)
    session.commit()

    assert session.scalar(select(func.count()).select_from(models.Task)) == 0
    assert session.scalar(select(func.count()).select_from(models.Comment)) == 0


def test_deleting_task_cascades_to_comments(session):
    _, _, _, _, task, _ = _graph(session)

    session.delete(task)
    session.commit()

    assert session.scalar(select(func.count()).select_from(models.Comment)) == 0


def test_deleting_label_nulls_task_label(session):
    _, _, _, label, task, _ = _graph(session)
    task_id = task.id

    session.delete(label)
    session.commit()
    session.expire_all()

    assert session.get(models.Task, task_id).label_id is None


def test_deleting_assignee_nulls_task_assignee(session):
    _, assignee, _, _, task, _ = _graph(session)
    task_id = task.id

    session.delete(assignee)
    session.commit()
    session.expire_all()

    assert session.get(models.Task, task_id).assignee_id is None


def test_deleting_author_with_comments_is_restricted(session):
    author, _, _, _, _, _ = _graph(session)

    with pytest.raises(IntegrityError):
        session.execute(text("DELETE FROM users WHERE id = :id"), {"id": author.id})
    session.rollback()
