from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tasks = db.query(models.Task).filter(models.Task.user_id == current_user.id).all()
    total_tasks = len(tasks)
    active_tasks = sum(1 for t in tasks if t.status != models.TaskStatus.done)
    completed_tasks = sum(1 for t in tasks if t.status == models.TaskStatus.done)

    today = datetime.utcnow().date()
    minutes_today = 0
    for t in tasks:
        for s in t.sessions:
            if s.start_time.date() == today and s.duration_minutes:
                minutes_today += s.duration_minutes

    return schemas.DashboardStats(
        total_tasks=total_tasks,
        active_tasks=active_tasks,
        completed_tasks=completed_tasks,
        minutes_today=minutes_today,
    )


@router.get("/charts", response_model=schemas.DashboardCharts)
def charts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tasks = db.query(models.Task).filter(models.Task.user_id == current_user.id).all()

    daily_minutes: dict[str, int] = {}
    today = datetime.utcnow().date()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        daily_minutes[day.isoformat()] = 0

    by_priority = {"low": 0, "medium": 0, "high": 0}

    for t in tasks:
        by_priority[t.priority.value] += 1
        for s in t.sessions:
            key = s.start_time.date().isoformat()
            if key in daily_minutes and s.duration_minutes:
                daily_minutes[key] += s.duration_minutes

    daily = [
        schemas.DailyPoint(date=d, minutes=m) for d, m in daily_minutes.items()
    ]

    return schemas.DashboardCharts(daily=daily, by_priority=by_priority)
