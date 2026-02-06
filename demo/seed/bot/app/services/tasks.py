from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models import Task, TaskStatus, TaskDifficulty

DIFFICULTY_REWARDS = {
    TaskDifficulty.easy: (10, 5),
    TaskDifficulty.medium: (25, 15),
    TaskDifficulty.hard: (50, 30),
    TaskDifficulty.epic: (100, 50),
}


def create_task(session: Session, user_id: int, title: str, difficulty: TaskDifficulty, deadline: datetime) -> Task:
    task = Task(user_id=user_id, title=title, difficulty=difficulty, deadline=deadline)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def list_active_tasks(session: Session, user_id: int) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user_id, Task.status == TaskStatus.active).order_by(Task.deadline.asc())
    return list(session.execute(stmt).scalars())


def list_failed_tasks(session: Session, user_id: int) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user_id, Task.status == TaskStatus.failed).order_by(Task.deadline.desc())
    return list(session.execute(stmt).scalars())


def get_task(session: Session, user_id: int, task_id: int) -> Task | None:
    stmt = select(Task).where(Task.user_id == user_id, Task.id == task_id)
    return session.execute(stmt).scalars().one_or_none()


def mark_completed(task: Task) -> None:
    task.status = TaskStatus.completed
    task.completed_at = datetime.utcnow()


def mark_deleted(task: Task) -> None:
    task.status = TaskStatus.deleted


def mark_failed(task: Task) -> None:
    task.status = TaskStatus.failed


def find_due_tasks(session: Session, now: datetime) -> list[Task]:
    stmt = select(Task).where(Task.status == TaskStatus.active, Task.deadline <= now)
    return list(session.execute(stmt).scalars())


def find_remind_tasks(session: Session, now: datetime) -> list[Task]:
    reminder_point = now + timedelta(hours=1)
    stmt = select(Task).where(
        Task.status == TaskStatus.active,
        Task.reminded.is_(False),
        Task.deadline <= reminder_point,
        Task.deadline > now,
    )
    return list(session.execute(stmt).scalars())
