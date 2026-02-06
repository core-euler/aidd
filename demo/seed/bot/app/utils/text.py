from datetime import datetime
from zoneinfo import ZoneInfo
from ..models import User, Task
from ..services.tasks import DIFFICULTY_REWARDS


def progress_bar(current: int, total: int, size: int = 10) -> str:
    if total <= 0:
        return "[" + "░" * size + "]"
    filled = int((current / total) * size)
    filled = max(0, min(size, filled))
    return "[" + "█" * filled + "░" * (size - filled) + "]"


def _ensure_tz(dt: datetime, tz: ZoneInfo) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt


def format_deadline(dt: datetime, tz: ZoneInfo) -> str:
    local_dt = _ensure_tz(dt, tz).astimezone(tz)
    return local_dt.strftime("%d.%m.%Y %H:%M")


def time_left_text(dt: datetime, now: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    if now.tzinfo is None:
        now = now.replace(tzinfo=ZoneInfo("UTC"))
    dt_local = dt.astimezone(now.tzinfo)
    delta = dt_local - now
    seconds = int(delta.total_seconds())
    if seconds <= 0:
        return "0мин"
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    if days > 0:
        return f"{days}д {hours % 24}ч"
    if hours > 0:
        return f"{hours}ч {minutes % 60}мин"
    return f"{minutes}мин"


def welcome_text(user: User) -> str:
    return (
        "🎮 Добро пожаловать в GameTODO!\n\n"
        "Управляй задачами — прокачивай персонажа.\n\n"
        "⚔️ Выполнил вовремя — получил опыт\n"
        "💔 Просрочил — получил урон\n"
        "💀 Ноль здоровья — начинаешь сначала\n\n"
        "Твой персонаж создан:\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{user.level * 100}\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp}"
    )


def main_menu_text(user: User, active_tasks: int) -> str:
    return (
        "🎮 GameTODO\n\n"
        f"🎖 Уровень {user.level} | ❤️ {user.hp}/{user.max_hp}\n\n"
        f"Активных задач: {active_tasks}"
    )


def character_text(user: User, active_tasks: int, nearest_deadline: str | None) -> str:
    xp_bar = progress_bar(user.xp, user.level * 100)
    hp_bar = progress_bar(user.hp, user.max_hp)
    nearest = nearest_deadline or "нет"
    return (
        "👤 Твой персонаж\n\n"
        f"🎖 Уровень: {user.level}\n"
        f"✨ Опыт: {user.xp}/{user.level * 100}\n"
        f"{xp_bar}\n\n"
        f"❤️ Здоровье: {user.hp}/{user.max_hp}\n"
        f"{hp_bar}\n\n"
        f"📋 Активных задач: {active_tasks}\n"
        f"⏰ Ближайший дедлайн: {nearest}"
    )


def stats_text(user: User, success_rate: float) -> str:
    return (
        "📊 Статистика\n\n"
        f"✅ Выполнено задач: {user.total_completed}\n"
        f"❌ Просрочено задач: {user.total_failed}\n"
        f"🎯 Успешность: {success_rate:.1f}%\n"
        f"🏆 Максимальный уровень: {user.max_level_reached}"
    )


def task_detail_text(task: Task, now: datetime, tz: ZoneInfo) -> str:
    reward, damage = DIFFICULTY_REWARDS[task.difficulty]
    deadline_text = format_deadline(task.deadline, tz)
    left = time_left_text(task.deadline, now)
    return (
        f"📋 {task.title}\n"
        f"⚡ Сложность: {task.difficulty.value.capitalize()}\n"
        f"⏰ Дедлайн: {deadline_text}\n"
        f"⏳ Осталось: {left}\n\n"
        f"Награда: {reward} XP | Урон: {damage} HP"
    )


def overdue_list_text(tasks: list[Task], tz: ZoneInfo) -> str:
    if not tasks:
        return "Просроченных задач нет."
    lines = ["⛔ Просроченные задачи:"]
    for task in tasks:
        lines.append(f"- {task.title} ({format_deadline(task.deadline, tz)})")
    return "\n".join(lines)
