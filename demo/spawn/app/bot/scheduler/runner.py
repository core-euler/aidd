from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from datetime import timedelta

from aiogram import Bot
from sqlalchemy import update

from ..config import Config
from ..db.models import Task, TaskStatus
from ..db.session import Database
from ..services.constants import DIFFICULTY_CONFIG
from ..services.task_service import TaskService
from ..services.user_service import UserService
from ..utils.time import utc_now
from ..handlers.keyboards import notification_keyboard, back_to_menu
from ..handlers.screens import death_text, overdue_text, reminder_text


class Scheduler:
    def __init__(self, bot: Bot, db: Database, config: Config) -> None:
        self._bot = bot
        self._db = db
        self._config = config
        self._task: asyncio.Task | None = None
        self._stopped = asyncio.Event()
        self._logger = logging.getLogger("bot.scheduler")

    def start(self) -> None:
        if self._task:
            return
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._stopped.set()
        if self._task:
            await self._task

    async def _run(self) -> None:
        while not self._stopped.is_set():
            try:
                await self._process()
            except Exception:
                self._logger.exception("scheduler_error")
            await asyncio.sleep(300)

    async def _process(self) -> None:
        now = utc_now()
        remind_before = now + timedelta(hours=1)

        async with self._db.session() as session:
            task_service = TaskService(session)
            user_service = UserService(session)

            # Reminders
            remind_tasks = await task_service.due_for_reminder(now, remind_before)
            for task in remind_tasks:
                cfg = DIFFICULTY_CONFIG[task.difficulty]
                user = await user_service.get_by_id(task.user_id)
                if not user:
                    continue
                await self._bot.send_message(
                    user.telegram_id,
                    reminder_text(task, self._config.timezone, cfg.damage),
                    reply_markup=notification_keyboard(task.id),
                )
                task.reminder_sent = True
                self._logger.info(
                    "reminder_sent: user_id=%s task_id=%s deadline_utc=%s",
                    task.user_id,
                    task.id,
                    task.deadline.isoformat(),
                )

            # Overdue processing
            overdue_tasks = await task_service.overdue_tasks(now)
            grouped: dict[int, list[Task]] = defaultdict(list)
            for task in overdue_tasks:
                grouped[task.user_id].append(task)

            for user_id, tasks in grouped.items():
                user = await user_service.get_by_id(user_id)
                if not user:
                    continue

                total_damage = 0
                for task in tasks:
                    cfg = DIFFICULTY_CONFIG[task.difficulty]
                    total_damage += cfg.damage
                    await task_service.mark_failed(task)
                    user_service.record_failure(user)
                    self._logger.info(
                        "task_overdue: user_id=%s task_id=%s damage=%s deadline_utc=%s",
                        user.id,
                        task.id,
                        cfg.damage,
                        task.deadline.isoformat(),
                    )

                died = user_service.apply_damage(user, total_damage)

                for task in tasks:
                    cfg = DIFFICULTY_CONFIG[task.difficulty]
                    await self._bot.send_message(
                        user.telegram_id,
                        overdue_text(task, user, cfg.damage, self._config.timezone),
                        reply_markup=back_to_menu(),
                    )

                if died:
                    user_service.reset_on_death(user)
                    await session.execute(
                        update(Task)
                        .where(Task.user_id == user.id, Task.status == TaskStatus.active)
                        .values(status=TaskStatus.deleted)
                    )
                    self._logger.info("user_death: user_id=%s", user.id)
                    await self._bot.send_message(
                        user.telegram_id,
                        death_text(user),
                        reply_markup=back_to_menu(),
                    )

            await session.commit()
