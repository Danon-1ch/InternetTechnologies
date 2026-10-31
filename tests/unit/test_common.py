import pytest
from sqlalchemy.exc import IntegrityError

from app.routers.common import conflict_from_integrity_error

pytestmark = pytest.mark.unit


def _integrity_error(message: str) -> IntegrityError:
    return IntegrityError("INSERT", {}, Exception(message))


@pytest.mark.parametrize(
    ("message", "detail"),
    [
        ("duplicate key value violates unique constraint", "Duplicate value"),
        ("unique constraint failed", "Duplicate value"),
        ("insert violates foreign key constraint", "Invalid reference"),
        ("new row violates check constraint", "Constraint violation"),
        ("cannot delete because of restrict", "Cannot delete: related records exist"),
        ("statement violates something else", "Cannot delete: related records exist"),
        ("connection lost", "Database conflict"),
    ],
)
def test_maps_integrity_errors_to_409(message, detail):
    error = conflict_from_integrity_error(_integrity_error(message))
    assert error.status_code == 409
    assert error.detail == detail
