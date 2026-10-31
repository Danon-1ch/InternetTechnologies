import itertools

_counter = itertools.count(1)


def _post(client, url, payload):
    response = client.post(url, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def create_user(client, **overrides):
    n = next(_counter)
    payload = {"email": f"user{n}@example.com", "display_name": f"User {n}"}
    payload.update(overrides)
    return _post(client, "/v1/users", payload)


def create_project(client, **overrides):
    n = next(_counter)
    payload = {"name": f"Project {n}"}
    payload.update(overrides)
    return _post(client, "/v1/projects", payload)


def create_label(client, **overrides):
    n = next(_counter)
    payload = {"name": f"label-{n}", "color": "#6b7280"}
    payload.update(overrides)
    return _post(client, "/v1/labels", payload)


def create_task(client, project_id, **overrides):
    n = next(_counter)
    payload = {"project_id": project_id, "title": f"Task {n}"}
    payload.update(overrides)
    return _post(client, "/v1/tasks", payload)


def create_comment(client, task_id, author_id, **overrides):
    payload = {"task_id": task_id, "author_id": author_id, "body": "Looks good"}
    payload.update(overrides)
    return _post(client, "/v1/comments", payload)
