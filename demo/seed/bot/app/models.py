from enum import Enum
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Enum as SAEnum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base


class TaskStatus(str, Enum):
    active = "active"
    completed = "completed"
    failed = "failed"
    deleted = "deleted"


class TaskDifficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    epic = "epic"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    level = Column(Integer, default=1, nullable=False)
    xp = Column(Integer, default=0, nullable=False)
    hp = Column(Integer, default=100, nullable=False)
    max_hp = Column(Integer, default=100, nullable=False)
    total_completed = Column(Integer, default=0, nullable=False)
    total_failed = Column(Integer, default=0, nullable=False)
    max_level_reached = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    difficulty = Column(SAEnum(TaskDifficulty), nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=False)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.active, nullable=False)
    reminded = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="tasks")
