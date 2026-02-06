from __future__ import annotations

from datetime import datetime

from ..db.models import Task, User
from ..services.constants import DIFFICULTY_CONFIG
from ..utils.formatting import format_dt, human_delta_until, progress_bar, xp_to_next


def welcome_text(user: User) -> str:
    return (
        "🎮 Добро пожаловать в GameTODO!\n\n"
        "Управляй задачами — прокачивай персонажа.\n\n"
        "⚔️ Выполнил вовремя — получил опыт\n"
        "💔 Просрочил — получил урон\n"
        "💀 Ноль здоровья — начинаешь сначала\n\n"
        "Твой персонаж создан:\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{xp_to_next(user.level)}\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp}"
    )


def main_menu_text(user: User) -> str:
    return (
        "🎮 GameTODO\n\n"
        f"🎖 Уровень {user.level} | ❤️ {user.hp}/{user.max_hp}"
    )


def character_text(user: User, active_tasks: int, next_deadline: datetime | None, tz_name: str) -> str:
    xp_bar = progress_bar(user.xp, xp_to_next(user.level))
    hp_bar = progress_bar(user.hp, user.max_hp)
    next_deadline_text = "нет"
    if next_deadline:
        next_deadline_text = human_delta_until(next_deadline, tz_name)

    return (
        "👤 Твой персонаж\n\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{xp_to_next(user.level)}\n"
        f"{xp_bar}\n\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp}\n"
        f"{hp_bar}\n\n"
        f"📋 Активных задач: {active_tasks}\n"
        f"⏰ Ближайший дедлайн: {next_deadline_text}"
    )


def stats_text(user: User) -> str:
    total = user.total_completed + user.total_failed
    success = int((user.total_completed / total) * 100) if total > 0 else 0
    return (
        "📊 Статистика\n\n"
        f"✅ Выполнено: {user.total_completed}\n"
        f"❌ Просрочено: {user.total_failed}\n"
        f"📈 Успешность: {success}%\n\n"
        f"🏆 Макс. уровень: {user.max_level_reached}"
    )


def task_details_text(task: Task, tz_name: str) -> str:
    cfg = DIFFICULTY_CONFIG[task.difficulty]
    return (
        f"📋 {task.title}\n\n"
        f"⚡ Сложность: {cfg.label} (+{cfg.xp} XP)\n"
        f"⏰ Дедлайн: {format_dt(task.deadline, tz_name)}\n"
        f"⏳ Осталось: {human_delta_until(task.deadline, tz_name)}"
    )


def task_created_text(task: Task, tz_name: str) -> str:
    cfg = DIFFICULTY_CONFIG[task.difficulty]
    return (
        "✅ Задача создана!\n\n"
        f"📝 {task.title}\n"
        f"⚡ {cfg.label} (+{cfg.xp} XP / -{cfg.damage} HP)\n"
        f"⏰ Дедлайн: {format_dt(task.deadline, tz_name)}\n\n"
        "Удачи! 💪"
    )


def task_completed_text(task: Task, user: User, xp_gain: int) -> str:
    xp_bar = progress_bar(user.xp, xp_to_next(user.level))
    return (
        "🎉 Задача выполнена!\n\n"
        f"📝 {task.title}\n"
        f"✨ +{xp_gain} XP\n\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{xp_to_next(user.level)} {xp_bar}"
    )


def reminder_text(task: Task, tz_name: str, damage: int) -> str:
    return (
        "⏰ Напоминание!\n\n"
        f"📝 {task.title}\n"
        "⏳ Осталось меньше часа!\n\n"
        f"Не забудь выполнить, иначе -{damage} HP"
    )


def overdue_text(task: Task, user: User, damage: int, tz_name: str) -> str:
    hp_bar = progress_bar(user.hp, user.max_hp)
    return (
        "⚠️ Задача просрочена!\n\n"
        f"📝 {task.title}\n"
        f"💔 -{damage} HP\n\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp} {hp_bar}"
    )


def level_up_text(user: User) -> str:
    return (
        "🎉 Уровень повышен!\n\n"
        f"🎖 Новый уровень: {user.level}\n"
        f"❤️ Здоровье восстановлено: {user.hp}/{user.max_hp}\n"
        f"✨ До следующего: {user.xp}/{xp_to_next(user.level)}\n\n"
        "Так держать! 💪"
    )


def death_text(user: User) -> str:
    return (
        "💀 Твой персонаж погиб!\n\n"
        "Здоровье упало до нуля.\n"
        "Прогресс сброшен.\n\n"
        "🔄 Заново:\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{xp_to_next(user.level)}\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp}\n\n"
        "Все задачи удалены."
    )
