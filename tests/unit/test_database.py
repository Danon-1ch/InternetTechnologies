import pytest

from app import database

pytestmark = pytest.mark.unit


def test_get_db_yields_a_session_and_closes_it(monkeypatch):
    class FakeSession:
        closed = False

        def close(self):
            self.closed = True

    fake = FakeSession()
    monkeypatch.setattr(database, "SessionLocal", lambda: fake)

    generator = database.get_db()
    assert next(generator) is fake
    assert fake.closed is False

    with pytest.raises(StopIteration):
        next(generator)
    assert fake.closed is True
