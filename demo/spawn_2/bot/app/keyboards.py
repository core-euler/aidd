from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.constants import DIFFICULTY_VALUES


def menu_keyboard(active_count: int | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Новая задача", callback_data="new_task")
    if active_count is None:
        tasks_label = "📋 Мои задачи"
    else:
        tasks_label = f"📋 Мои задачи ({active_count})"
    kb.button(text=tasks_label, callback_data="tasks")
    kb.button(text="👤 Персонаж", callback_data="character")
    kb.button(text="📊 Статистика", callback_data="stats")
    kb.adjust(1)
    return kb.as_markup()


def welcome_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Создать первую задачу", callback_data="new_task")
    return kb.as_markup()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 Меню", callback_data="menu")
    return kb.as_markup()


def back_to_tasks_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ К задачам", callback_data="tasks")
    kb.button(text="🏠 Меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="menu")
    return kb.as_markup()


def tasks_list_keyboard(tasks: list[tuple[int, str, str]]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for task_id, title, remaining in tasks:
        kb.button(text=f"📌 {title} — {remaining}", callback_data=f"task:{task_id}")
    kb.adjust(1)
    kb.button(text="⛔ Просроченные", callback_data="tasks_failed")
    kb.button(text="🏠 Меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def tasks_failed_keyboard(tasks: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for task_id, title in tasks:
        kb.button(text=f"⛔ {title}", callback_data=f"task:{task_id}")
    kb.adjust(1)
    kb.button(text="◀️ К задачам", callback_data="tasks")
    kb.button(text="🏠 Меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def task_detail_keyboard(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Выполнено", callback_data=f"task_done:{task_id}")
    kb.button(text="🗑 Удалить", callback_data=f"task_del:{task_id}")
    kb.button(text="◀️ К задачам", callback_data="tasks")
    kb.adjust(2, 1)
    return kb.as_markup()


def difficulty_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key, data in DIFFICULTY_VALUES.items():
        kb.button(text=f"{data['label']} (+{data['xp']} XP)", callback_data=f"diff:{key}")
    kb.adjust(1)
    kb.button(text="❌ Отмена", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def deadline_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Через 1ч", callback_data="deadline:in1h")
    kb.button(text="Через 3ч", callback_data="deadline:in3h")
    kb.button(text="Сегодня 21:00", callback_data="deadline:today21")
    kb.button(text="Завтра 10:00", callback_data="deadline:tomorrow10")
    kb.button(text="Завтра 18:00", callback_data="deadline:tomorrow18")
    kb.button(text="✏️ Ввести", callback_data="deadline:manual")
    kb.adjust(2, 2, 2)
    kb.button(text="❌ Отмена", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def task_created_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Ещё задачу", callback_data="new_task")
    kb.button(text="🏠 Меню", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()


def task_completed_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 К задачам", callback_data="tasks")
    kb.button(text="🏠 Меню", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()


def reminder_keyboard(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Выполнено", callback_data=f"task_done:{task_id}")
    kb.button(text="📋 Открыть", callback_data=f"task:{task_id}")
    kb.adjust(2)
    return kb.as_markup()


def death_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Новая задача", callback_data="new_task")
    kb.button(text="🏠 Меню", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()
