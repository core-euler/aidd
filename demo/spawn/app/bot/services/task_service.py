from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Difficulty, Task, TaskStatus


@dataclass
class TitleResult:
    title: str
    truncated: bool


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def normalize_title(self, title: str) -> TitleResult:
        trimmed = title.strip()
        if len(trimmed) > 200:
            return TitleResult(title=trimmed[:200], truncated=True)
        return TitleResult(title=trimmed, truncated=False)

    async def create_task(
        self,
        user_id: int,
        title: str,
        difficulty: Difficulty,
        deadline_utc: datetime,
    ) -> Task:
        task = Task(
            user_id=user_id,
            title=title,
            difficulty=difficulty,
            deadline=deadline_utc,
            status=TaskStatus.active,
            reminder_sent=False,
        )
        self._session.add(task)
        await self._session.flush()
        return task

    async def list_active(self, user_id: int) -> list[Task]:
        result = await self._session.execute(
            select(Task)
            .where(Task.user_id == user_id, Task.status == TaskStatus.active)
            .order_by(Task.deadline.asc())
        )
        return list(result.scalars().all())

    async def list_failed(self, user_id: int) -> list[Task]:
        result = await self._session.execute(
            select(Task)
            .where(Task.user_id == user_id, Task.status == TaskStatus.failed)
            .order_by(Task.deadline.desc())
        )
        return list(result.scalars().all())

    async def get_task(self, task_id: int, user_id: int) -> Task | None:
        result = await self._session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def complete_task(self, task: Task) -> None:
        task.status = TaskStatus.completed
        task.completed_at = datetime.now(timezone.utc)

    async def delete_task(self, task: Task) -> None:
        task.status = TaskStatus.deleted

    async def mark_failed(self, task: Task) -> None:
        task.status = TaskStatus.failed

    async def due_for_reminder(self, now_utc: datetime, before_utc: datetime) -> list[Task]:
        result = await self._session.execute(
            select(Task)
            .where(
                Task.status == TaskStatus.active,
                Task.reminder_sent.is_(False),
                Task.deadline > now_utc,
                Task.deadline <= before_utc,
            )
        )
        return list(result.scalars().all())

    async def overdue_tasks(self, now_utc: datetime) -> list[Task]:
        result = await self._session.execute(
            select(Task)
            .where(Task.status == TaskStatus.active, Task.deadline <= now_utc)
        )
        return list(result.scalars().all())
