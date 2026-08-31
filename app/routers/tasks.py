from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _serialize(task: models.Task) -> schemas.TaskOut:
    total = sum(s.duration_minutes or 0 for s in task.sessions)
    running_session = next((s for s in task.sessions if s.end_time is None), None)
    out = schemas.TaskOut.model_validate(task)
    out.total_minutes = total
    out.is_running = running_session is not None
    out.running_since = running_session.start_time if running_session else None
    return out


@router.get("", response_model=list[schemas.TaskOut])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tasks = (
        db.query(models.Task)
        .filter(models.Task.user_id == current_user.id)
        .order_by(models.Task.created_at.desc())
        .all()
    )
    return [_serialize(t) for t in tasks]


@router.post("", response_model=schemas.TaskOut)
def create_task(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = models.Task(user_id=current_user.id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return _serialize(task)


@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: str,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return _serialize(task)


@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}
