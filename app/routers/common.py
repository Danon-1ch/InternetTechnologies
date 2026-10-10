from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


def conflict_from_integrity_error(exc: IntegrityError) -> HTTPException:
    """Превращает IntegrityError в 409 с понятным сообщением."""
    message = str(exc.orig).lower()
    if "unique" in message or "duplicate" in message:
        detail = "Duplicate value"
    elif "foreign key" in message:
        detail = "Invalid reference"
    elif "check" in message:
        detail = "Constraint violation"
    elif "restrict" in message or "violates" in message:
        detail = "Cannot delete: related records exist"
    else:
        detail = "Database conflict"
    return HTTPException(status_code=409, detail=detail)