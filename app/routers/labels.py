from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.routers.common import conflict_from_integrity_error

router = APIRouter()


def get_label_or_404(db: Session, label_id: int) -> models.Label:
    label = db.get(models.Label, label_id)
    if label is None:
        raise HTTPException(status_code=404, detail="Label not found")
    return label


@router.get("", response_model=list[schemas.LabelRead])
def list_labels(db: Session = Depends(get_db)):
    return db.scalars(select(models.Label).order_by(models.Label.id)).all()


@router.get("/{label_id}", response_model=schemas.LabelRead)
def get_label(label_id: int, db: Session = Depends(get_db)):
    return get_label_or_404(db, label_id)


@router.post("", response_model=schemas.LabelRead, status_code=status.HTTP_201_CREATED)
def create_label(payload: schemas.LabelCreate, db: Session = Depends(get_db)):
    label = models.Label(**payload.model_dump())
    db.add(label)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict_from_integrity_error(exc) from exc
    db.refresh(label)
    return label


@router.patch("/{label_id}", response_model=schemas.LabelRead)
def update_label(label_id: int, payload: schemas.LabelUpdate, db: Session = Depends(get_db)):
    label = get_label_or_404(db, label_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(label, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict_from_integrity_error(exc) from exc
    db.refresh(label)
    return label


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(label_id: int, db: Session = Depends(get_db)) -> None:
    label = get_label_or_404(db, label_id)
    db.delete(label)
    db.commit()
    return None