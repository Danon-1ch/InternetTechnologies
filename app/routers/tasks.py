from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.routers.common import conflict_from_integrity_error

router = APIRouter()


def get_task_or_404(db: Session, task_id: int) -> models.Task:
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("", response_model=list[schemas.TaskRead])
def list_tasks(
    project_id: int | None = Query(default=None),
    status_: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    statement = select(models.Task)
    if project_id is not None:
        statement = statement.where(models.Task.project_id == project_id)
    if status_ is not None:
        statement = statement.where(models.Task.status == status_)
    return db.scalars(statement.order_by(models.Task.id)).all()


@router.get("/{task_id}", response_model=schemas.TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return get_task_or_404(db, task_id)


@router.post("", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = models.Task(**payload.model_dump())
    db.add(task)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict_from_integrity_error(exc) from exc
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=schemas.TaskRead)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = get_task_or_404(db, task_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict_from_integrity_error(exc) from exc
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    task = get_task_or_404(db, task_id)
    db.delete(task)
    db.commit()
    return None