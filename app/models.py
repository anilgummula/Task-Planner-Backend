import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, ForeignKey, DateTime, Text, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    google_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
    chats = relationship("AIChat", back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(SAEnum(TaskPriority), default=TaskPriority.medium)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.todo)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="tasks")
    sessions = relationship("TaskSession", back_populates="task", cascade="all, delete-orphan")


class TaskSession(Base):
    __tablename__ = "task_sessions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    task_id = Column(UUID(as_uuid=False), ForeignKey("tasks.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    task = relationship("Task", back_populates="sessions")


class AIChat(Base):
    __tablename__ = "ai_chats"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")
