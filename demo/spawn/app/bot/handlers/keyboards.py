from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..db.models import Difficulty
from ..services.constants import DIFFICULTY_CONFIG


class Cb:
    MENU = "menu"
    NEW_TASK = "new_task"
    TASKS = "tasks"
    CHARACTER = "character"
    STATS = "stats"
    BACK = "back"
    OVERDUE = "overdue"

    TASK_VIEW_PREFIX = "task:"
    TASK_DONE_PREFIX = "done:"
    TASK_DELETE_PREFIX = "delete:"

    DEADLINE_QUICK_PREFIX = "deadline:"
    DEADLINE_MANUAL = "deadline:manual"

    DIFF_PREFIX = "diff:"


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Новая задача", callback_data=Cb.NEW_TASK)
    kb.button(text="📋 Мои задачи", callback_data=Cb.TASKS)
    kb.button(text="👤 Персонаж", callback_data=Cb.CHARACTER)
    kb.button(text="📊 Статистика", callback_data=Cb.STATS)
    kb.adjust(1)
    return kb.as_markup()


def start_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Создать первую задачу", callback_data=Cb.NEW_TASK)
    return kb.as_markup()


def back_to_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 Меню", callback_data=Cb.MENU)
    return kb.as_markup()


def back_to_tasks() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ К задачам", callback_data=Cb.TASKS)
    return kb.as_markup()


def task_list_keyboard(tasks: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for task_id, label in tasks:
        kb.button(text=label, callback_data=f"{Cb.TASK_VIEW_PREFIX}{task_id}")
    kb.button(text="⛔ Просроченные", callback_data=Cb.OVERDUE)
    kb.button(text="🏠 Меню", callback_data=Cb.MENU)
    kb.adjust(1)
    return kb.as_markup()


def task_details_keyboard(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Выполнено", callback_data=f"{Cb.TASK_DONE_PREFIX}{task_id}")
    kb.button(text="🗑 Удалить", callback_data=f"{Cb.TASK_DELETE_PREFIX}{task_id}")
    kb.button(text="◀️ К задачам", callback_data=Cb.TASKS)
    kb.adjust(2, 1)
    return kb.as_markup()


def difficulty_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for diff in [Difficulty.easy, Difficulty.medium, Difficulty.hard, Difficulty.epic]:
        cfg = DIFFICULTY_CONFIG[diff]
        kb.button(text=f"{cfg.label} (+{cfg.xp} XP)", callback_data=f"{Cb.DIFF_PREFIX}{diff.value}")
    kb.button(text="❌ Отмена", callback_data=Cb.MENU)
    kb.adjust(1)
    return kb.as_markup()


def deadline_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Через 1ч", callback_data=f"{Cb.DEADLINE_QUICK_PREFIX}1h")
    kb.button(text="Через 3ч", callback_data=f"{Cb.DEADLINE_QUICK_PREFIX}3h")
    kb.button(text="Сегодня 21:00", callback_data=f"{Cb.DEADLINE_QUICK_PREFIX}today_evening")
    kb.button(text="Завтра 10:00", callback_data=f"{Cb.DEADLINE_QUICK_PREFIX}tomorrow_morning")
    kb.button(text="Завтра 18:00", callback_data=f"{Cb.DEADLINE_QUICK_PREFIX}tomorrow_evening")
    kb.button(text="✏️ Ввести", callback_data=Cb.DEADLINE_MANUAL)
    kb.button(text="❌ Отмена", callback_data=Cb.MENU)
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup()


def task_created_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Ещё задачу", callback_data=Cb.NEW_TASK)
    kb.button(text="🏠 Меню", callback_data=Cb.MENU)
    kb.adjust(2)
    return kb.as_markup()


def notification_keyboard(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Выполнено", callback_data=f"{Cb.TASK_DONE_PREFIX}{task_id}")
    kb.button(text="📋 Открыть", callback_data=f"{Cb.TASK_VIEW_PREFIX}{task_id}")
    kb.adjust(2)
    return kb.as_markup()
