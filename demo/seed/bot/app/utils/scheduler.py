from datetime import datetime
import logging
from zoneinfo import ZoneInfo
from aiogram import Bot
from sqlalchemy.orm import Session
from ..services.tasks import find_due_tasks, find_remind_tasks, DIFFICULTY_REWARDS, mark_failed
from ..services.users import apply_damage
from ..models import TaskStatus
from ..utils.text import format_deadline

logger = logging.getLogger(__name__)


async def check_deadlines(bot: Bot, session: Session, tz: ZoneInfo) -> None:
    now = datetime.now(ZoneInfo("UTC"))

    due_tasks = find_due_tasks(session, now)
    tasks_by_user: dict[int, list] = {}
    for task in due_tasks:
        tasks_by_user.setdefault(task.user_id, []).append(task)

    for _, tasks in tasks_by_user.items():
        user = tasks[0].user
        total_damage = 0
        titles = []
        for task in tasks:
            if task.status != TaskStatus.active:
                continue
            _, damage = DIFFICULTY_REWARDS[task.difficulty]
            total_damage += damage
            titles.append(task.title)
            mark_failed(task)
            user.total_failed += 1

        if total_damage == 0:
            continue

        died = apply_damage(user, total_damage)
        session.commit()

        if died:
            session.query(task.__class__).filter(
                task.__class__.user_id == user.id,
                task.__class__.status == TaskStatus.active,
            ).delete(synchronize_session=False)
            session.commit()
            logger.info("death user_id=%s total_damage=%s", user.telegram_id, total_damage)
            await bot.send_message(
                chat_id=user.telegram_id,
                text=(
                    "💀 Ваш персонаж погиб! Прогресс сброшен. Начинаем заново!\n"
                    "Все активные задачи удалены."
                ),
            )
        else:
            titles_text = "\n".join(f"- {title}" for title in titles)
            logger.info("overdue user_id=%s total_damage=%s tasks=%s", user.telegram_id, total_damage, len(titles))
            await bot.send_message(
                chat_id=user.telegram_id,
                text=(
                    "⚠️ Задачи просрочены!\n\n"
                    f"{titles_text}\n\n"
                    f"Получено урона: {total_damage} HP\n"
                    f"Текущее здоровье: {user.hp}/{user.max_hp}"
                ),
            )

    remind_tasks = find_remind_tasks(session, now)
    for task in remind_tasks:
        task.reminded = True
        session.commit()
        logger.info("reminder user_id=%s task_id=%s", task.user.telegram_id, task.id)
        await bot.send_message(
            chat_id=task.user.telegram_id,
            text=(
                "⏰ Напоминание: до дедлайна осталось 1 час.\n"
                f"Задача: {task.title}\n"
                f"Дедлайн: {format_deadline(task.deadline, tz)}"
            ),
        )
