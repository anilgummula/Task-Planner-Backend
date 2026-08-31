from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/timer", tags=["timer"])


def _get_owned_task(db: Session, task_id: str, user_id: str) -> models.Task:
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == user_id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def _find_running_session(db: Session, user_id: str) -> models.TaskSession | None:
    return (
        db.query(models.TaskSession)
        .join(models.Task)
        .filter(models.Task.user_id == user_id, models.TaskSession.end_time.is_(None))
        .first()
    )


@router.post("/start/{task_id}", response_model=schemas.TaskSessionOut)
def start_timer(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = _get_owned_task(db, task_id, current_user.id)

    running = _find_running_session(db, current_user.id)
    if running:
        raise HTTPException(
            status_code=409,
            detail=f"Task '{running.task.title}' is already running. Stop it first.",
        )

    session = models.TaskSession(task_id=task.id, start_time=datetime.utcnow())
    db.add(session)

    if task.status == models.TaskStatus.todo:
        task.status = models.TaskStatus.in_progress

    db.commit()
    db.refresh(session)
    return session


@router.post("/stop/{task_id}", response_model=schemas.TaskSessionOut)
def stop_timer(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = _get_owned_task(db, task_id, current_user.id)

    session = (
        db.query(models.TaskSession)
        .filter(models.TaskSession.task_id == task.id, models.TaskSession.end_time.is_(None))
        .first()
    )
    if not session:
        raise HTTPException(status_code=400, detail="No running session for this task")

    session.end_time = datetime.utcnow()
    delta = session.end_time - session.start_time
    session.duration_minutes = max(1, round(delta.total_seconds() / 60))

    db.commit()
    db.refresh(session)
    return session


@router.get("/history/{task_id}", response_model=list[schemas.TaskSessionOut])
def timer_history(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_owned_task(db, task_id, current_user.id)
    return (
        db.query(models.TaskSession)
        .filter(models.TaskSession.task_id == task_id)
        .order_by(models.TaskSession.start_time.desc())
        .all()
    )
