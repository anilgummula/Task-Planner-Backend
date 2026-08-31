from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.models import TaskPriority, TaskStatus


# ---------- Auth ----------
class GoogleLoginRequest(BaseModel):
    id_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    email: str
    avatar_url: Optional[str] = None
    created_at: datetime


# ---------- Tasks ----------
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.todo


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    total_minutes: int = 0
    is_running: bool = False
    running_since: Optional[datetime] = None


# ---------- Timer ----------
class TaskSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    task_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[int]


# ---------- Dashboard ----------
class DashboardStats(BaseModel):
    total_tasks: int
    active_tasks: int
    completed_tasks: int
    minutes_today: int


class DailyPoint(BaseModel):
    date: str
    minutes: int


class DashboardCharts(BaseModel):
    daily: List[DailyPoint]
    by_priority: dict


# ---------- AI ----------
class AIChatRequest(BaseModel):
    prompt: str


class AIChatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    prompt: str
    response: str
    created_at: datetime
