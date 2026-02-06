from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from datetime import timedelta

from aiogram import Bot

from app.constants import DIFFICULTY_VALUES, STATUS_FAILED
from app.services.tasks import find_due_for_reminder, mark_reminder_sent, find_overdue_tasks, delete_active_tasks
from app.services.character import apply_damage
from app.ui_texts import reminder_text, overdue_text, death_text
from app.keyboards import reminder_keyboard, menu_keyboard, death_keyboard
from app.utils.time_utils import now_utc

logger = logging.getLogger(__name__)


async def scheduler_loop(bot: Bot, session_factory, tz):
    while True:
        try:
            await run_checks(bot, session_factory, tz)
        except Exception:
            logger.exception("scheduler_error")
        await asyncio.sleep(300)


async def run_checks(bot: Bot, session_factory, tz):
    now = now_utc()
    in_one_hour = now + timedelta(hours=1)

    async with session_factory() as session:
        reminders = await find_due_for_reminder(session, now, in_one_hour)
        for task in reminders:
            await bot.send_message(
                task.user.telegram_id,
                reminder_text(task),
                reply_markup=reminder_keyboard(task.id),
            )
            await mark_reminder_sent(session, task)
            logger.info("reminder_sent", extra={"user_id": task.user_id, "task_id": task.id})

        overdue_tasks = await find_overdue_tasks(session, now)
        by_user: dict[int, list] = defaultdict(list)
        for task in overdue_tasks:
            by_user[task.user_id].append(task)

        for user_id, tasks in by_user.items():
            user = tasks[0].user
            total_damage = sum(DIFFICULTY_VALUES[t.difficulty]["damage"] for t in tasks)
            original_hp = user.hp
            cumulative = 0

            for task in tasks:
                task.status = STATUS_FAILED
                user.total_failed += 1
                damage = DIFFICULTY_VALUES[task.difficulty]["damage"]
                cumulative += damage
                user.hp = max(0, original_hp - cumulative)
                await bot.send_message(
                    user.telegram_id,
                    overdue_text(task, user, damage),
                    reply_markup=menu_keyboard(),
                )
                logger.info("task_overdue", extra={"user_id": user.id, "task_id": task.id})

            user.hp = original_hp
            damage_result = apply_damage(user, total_damage)
            if damage_result.died:
                await delete_active_tasks(session, user.id)
                await bot.send_message(
                    user.telegram_id,
                    death_text(user),
                    reply_markup=death_keyboard(),
                )
                logger.info("user_died", extra={"user_id": user.id})

        await session.commit()


def start_scheduler(bot: Bot, session_factory, tz):
    asyncio.create_task(scheduler_loop(bot, session_factory, tz))
