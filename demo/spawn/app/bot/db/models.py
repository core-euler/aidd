import enum
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .base import Base


class Difficulty(enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    epic = "epic"


class TaskStatus(enum.Enum):
    active = "active"
    completed = "completed"
    failed = "failed"
    deleted = "deleted"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)

    level = Column(Integer, nullable=False, default=1)
    xp = Column(Integer, nullable=False, default=0)
    hp = Column(Integer, nullable=False, default=100)
    max_hp = Column(Integer, nullable=False, default=100)

    total_completed = Column(Integer, nullable=False, default=0)
    total_failed = Column(Integer, nullable=False, default=0)
    max_level_reached = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String(200), nullable=False)
    difficulty = Column(Enum(Difficulty), nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.active)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    reminder_sent = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="tasks")
