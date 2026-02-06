from __future__ import annotations

from datetime import datetime
from app.constants import DIFFICULTY_VALUES
from app.models import User, Task
from app.services.character import xp_for_next_level
from app.services.stats import Stats
from app.utils.progress import progress_bar, percent


def welcome_text(user: User) -> str:
    xp_next = xp_for_next_level(user.level)
    return (
        "🎮 Добро пожаловать в GameTODO!\n\n"
        "Управляй задачами — прокачивай персонажа.\n\n"
        "⚔️ Выполнил вовремя — получил опыт\n"
        "💔 Просрочил — получил урон\n"
        "💀 Ноль здоровья — начинаешь сначала\n\n"
        "Твой персонаж создан:\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{xp_next}\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp}"
    )


def menu_text(user: User, active_count: int) -> str:
    return (
        "🎮 GameTODO\n\n"
        f"🎖 Уровень {user.level} | ❤️ {user.hp}/{user.max_hp}\n\n"
        f"Активных задач: {active_count}"
    )


def character_text(user: User, active_count: int, nearest_deadline: str | None) -> str:
    xp_next = xp_for_next_level(user.level)
    xp_bar = progress_bar(user.xp, xp_next)
    hp_bar = progress_bar(user.hp, user.max_hp)
    xp_pct = percent(user.xp, xp_next)
    hp_pct = percent(user.hp, user.max_hp)

    nearest = nearest_deadline or "нет"

    return (
        "👤 Твой персонаж\n\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{xp_next}\n"
        f"{xp_bar} {xp_pct}%\n\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp}\n"
        f"{hp_bar} {hp_pct}%\n\n"
        f"📋 Активных задач: {active_count}\n"
        f"⏰ Ближайший дедлайн: {nearest}"
    )


def stats_text(stats: Stats, joined_at: datetime) -> str:
    joined = joined_at.strftime("%d.%m.%Y")
    return (
        "📊 Статистика\n\n"
        f"✅ Выполнено: {stats.completed}\n"
        f"❌ Просрочено: {stats.failed}\n"
        f"📈 Успешность: {stats.success_rate}%\n\n"
        f"🏆 Макс. уровень: {stats.max_level}\n"
        f"📅 С нами с: {joined}"
    )


def tasks_list_text(tasks_count: int) -> str:
    return f"📋 Твои задачи ({tasks_count})"


def no_tasks_text() -> str:
    return "У тебя пока нет активных задач."


def task_detail_text(task: Task, deadline_str: str, remaining: str) -> str:
    diff = DIFFICULTY_VALUES.get(task.difficulty, {})
    label = diff.get("label", task.difficulty)
    xp = diff.get("xp", 0)
    return (
        f"📋 {task.title}\n\n"
        f"⚡ Сложность: {label} (+{xp} XP)\n"
        f"⏰ Дедлайн: {deadline_str}\n"
        f"⏳ Осталось: {remaining}"
    )


def task_created_text(task: Task, deadline_str: str) -> str:
    diff = DIFFICULTY_VALUES.get(task.difficulty, {})
    label = diff.get("label", task.difficulty)
    xp = diff.get("xp", 0)
    dmg = diff.get("damage", 0)
    return (
        "✅ Задача создана!\n\n"
        f"📝 {task.title}\n"
        f"⚡ {label} (+{xp} XP / -{dmg} HP)\n"
        f"⏰ Дедлайн: {deadline_str}\n\n"
        "Удачи! 💪"
    )


def task_completed_text(task: Task, user: User) -> str:
    diff = DIFFICULTY_VALUES.get(task.difficulty, {})
    xp = diff.get("xp", 0)
    xp_next = xp_for_next_level(user.level)
    xp_bar = progress_bar(user.xp, xp_next)
    xp_pct = percent(user.xp, xp_next)
    return (
        "🎉 Задача выполнена!\n\n"
        f"📝 {task.title}\n"
        f"✨ +{xp} XP\n\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{xp_next} {xp_bar} {xp_pct}%"
    )


def reminder_text(task: Task) -> str:
    diff = DIFFICULTY_VALUES.get(task.difficulty, {})
    dmg = diff.get("damage", 0)
    return (
        "⏰ Напоминание!\n\n"
        f"📝 {task.title}\n"
        "⏳ Осталось меньше часа!\n\n"
        f"Не забудь выполнить, иначе -{dmg} HP"
    )


def overdue_text(task: Task, user: User, damage: int) -> str:
    hp_bar = progress_bar(user.hp, user.max_hp)
    hp_pct = percent(user.hp, user.max_hp)
    return (
        "⚠️ Задача просрочена!\n\n"
        f"📝 {task.title}\n"
        f"💔 -{damage} HP\n\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp} {hp_bar} {hp_pct}%"
    )


def level_up_text(user: User) -> str:
    xp_next = xp_for_next_level(user.level)
    return (
        "🎉 Уровень повышен!\n\n"
        f"🎖 Новый уровень: {user.level}\n"
        f"❤️ Здоровье восстановлено: {user.max_hp}/{user.max_hp}\n"
        f"✨ До следующего: {user.xp}/{xp_next}\n\n"
        "Так держать! 💪"
    )


def death_text(user: User) -> str:
    xp_next = xp_for_next_level(user.level)
    return (
        "💀 Твой персонаж погиб!\n\n"
        "Здоровье упало до нуля.\n"
        "Прогресс сброшен.\n\n"
        "🔄 Заново:\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{xp_next}\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp}\n\n"
        "Все задачи удалены."
    )


def invalid_date_text() -> str:
    return (
        "Некорректный формат даты. Попробуй так:\n"
        "- завтра 18:00\n"
        "- 25.01 15:30\n"
        "- 25.01.2025 15:30\n"
        "- через 2 часа\n"
        "- через 1 день"
    )
