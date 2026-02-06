from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import Task
from .utils.text import time_left_text

MENU = "menu"
NEW_TASK = "new_task"
TASKS = "tasks"
CHARACTER = "character"
STATS = "stats"
OVERDUE = "overdue"
BACK_TASKS = "back_tasks"
CANCEL_NEW = "cancel_new"


def _row(*buttons: InlineKeyboardButton) -> list[InlineKeyboardButton]:
    return list(buttons)


def main_menu_keyboard(active_tasks: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            _row(InlineKeyboardButton(text="➕ Новая задача", callback_data=NEW_TASK)),
            _row(InlineKeyboardButton(text=f"📋 Мои задачи ({active_tasks})", callback_data=TASKS)),
            _row(InlineKeyboardButton(text="👤 Персонаж", callback_data=CHARACTER)),
            _row(InlineKeyboardButton(text="📊 Статистика", callback_data=STATS)),
        ]
    )


def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[_row(InlineKeyboardButton(text="➕ Создать первую задачу", callback_data=NEW_TASK))]
    )


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[_row(InlineKeyboardButton(text="🏠 Меню", callback_data=MENU))]
    )


def tasks_keyboard(tasks: list[Task], now: datetime, tz: ZoneInfo) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for task in tasks:
        left = time_left_text(task.deadline, now)
        rows.append(_row(InlineKeyboardButton(text=f"📌 {task.title} — {left}", callback_data=f"task:{task.id}")))
    rows.append(_row(InlineKeyboardButton(text="⛔ Просроченные", callback_data=OVERDUE)))
    rows.append(_row(InlineKeyboardButton(text="🏠 Меню", callback_data=MENU)))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def task_detail_keyboard(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            _row(InlineKeyboardButton(text="✅ Выполнено", callback_data=f"complete:{task_id}")),
            _row(InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{task_id}")),
            _row(InlineKeyboardButton(text="◀️ К задачам", callback_data=BACK_TASKS)),
        ]
    )


def difficulty_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            _row(InlineKeyboardButton(text="🟢 Лёгкая", callback_data="diff:easy")),
            _row(InlineKeyboardButton(text="🟡 Средняя", callback_data="diff:medium")),
            _row(InlineKeyboardButton(text="🔴 Сложная", callback_data="diff:hard")),
            _row(InlineKeyboardButton(text="🟣 Эпическая", callback_data="diff:epic")),
            _row(InlineKeyboardButton(text="❌ Отмена", callback_data=CANCEL_NEW)),
        ]
    )


def deadline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            _row(
                InlineKeyboardButton(text="Через 1 час", callback_data="dl:1h"),
                InlineKeyboardButton(text="Через 3 часа", callback_data="dl:3h"),
            ),
            _row(
                InlineKeyboardButton(text="Сегодня вечером", callback_data="dl:today_evening"),
                InlineKeyboardButton(text="Завтра утром", callback_data="dl:tomorrow_morning"),
            ),
            _row(
                InlineKeyboardButton(text="Завтра вечером", callback_data="dl:tomorrow_evening"),
                InlineKeyboardButton(text="Ввести вручную", callback_data="dl_manual"),
            ),
            _row(InlineKeyboardButton(text="❌ Отмена", callback_data=CANCEL_NEW)),
        ]
    )


def after_task_created_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            _row(InlineKeyboardButton(text="➕ Ещё задачу", callback_data=NEW_TASK)),
            _row(InlineKeyboardButton(text="🏠 Меню", callback_data=MENU)),
        ]
    )


def after_task_completed_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            _row(InlineKeyboardButton(text="📋 К задачам", callback_data=TASKS)),
            _row(InlineKeyboardButton(text="🏠 Меню", callback_data=MENU)),
        ]
    )


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[_row(InlineKeyboardButton(text="❌ Отмена", callback_data=CANCEL_NEW))]
    )
