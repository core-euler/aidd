from __future__ import annotations

from datetime import datetime
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Task
from app.constants import STATUS_ACTIVE, STATUS_COMPLETED, STATUS_DELETED, STATUS_FAILED
from app.utils.time_utils import ensure_aware


async def create_task(
    session: AsyncSession,
    user_id: int,
    title: str,
    difficulty: str,
    deadline_utc: datetime,
) -> Task:
    task = Task(
        user_id=user_id,
        title=title,
        difficulty=difficulty,
        deadline=ensure_aware(deadline_utc),
        status=STATUS_ACTIVE,
    )
    session.add(task)
    await session.flush()
    return task


async def list_active_tasks(session: AsyncSession, user_id: int) -> list[Task]:
    result = await session.execute(
        select(Task)
        .where(and_(Task.user_id == user_id, Task.status == STATUS_ACTIVE))
        .order_by(Task.deadline.asc())
    )
    return list(result.scalars().all())


async def list_failed_tasks(session: AsyncSession, user_id: int) -> list[Task]:
    result = await session.execute(
        select(Task)
        .where(and_(Task.user_id == user_id, Task.status == STATUS_FAILED))
        .order_by(Task.deadline.desc())
    )
    return list(result.scalars().all())


async def get_task(session: AsyncSession, user_id: int, task_id: int) -> Task | None:
    result = await session.execute(
        select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
    )
    return result.scalar_one_or_none()


async def mark_task_deleted(session: AsyncSession, task: Task) -> None:
    task.status = STATUS_DELETED


async def mark_task_completed(session: AsyncSession, task: Task, completed_at: datetime) -> None:
    task.status = STATUS_COMPLETED
    task.completed_at = ensure_aware(completed_at)


async def mark_task_failed(session: AsyncSession, task: Task) -> None:
    task.status = STATUS_FAILED


async def delete_active_tasks(session: AsyncSession, user_id: int) -> int:
    result = await session.execute(
        update(Task)
        .where(and_(Task.user_id == user_id, Task.status == STATUS_ACTIVE))
        .values(status=STATUS_DELETED)
        .execution_options(synchronize_session="fetch")
    )
    return result.rowcount or 0


async def find_due_for_reminder(session: AsyncSession, now_utc: datetime, in_one_hour: datetime) -> list[Task]:
    result = await session.execute(
        select(Task).options(selectinload(Task.user))
        .where(
            and_(
                Task.status == STATUS_ACTIVE,
                Task.reminder_sent.is_(False),
                Task.deadline > now_utc,
                Task.deadline <= in_one_hour,
            )
        )
    )
    return list(result.scalars().all())


async def mark_reminder_sent(session: AsyncSession, task: Task) -> None:
    task.reminder_sent = True


async def find_overdue_tasks(session: AsyncSession, now_utc: datetime) -> list[Task]:
    result = await session.execute(
        select(Task).options(selectinload(Task.user))
        .where(
            and_(Task.status == STATUS_ACTIVE, Task.deadline <= now_utc)
        )
    )
    return list(result.scalars().all())
