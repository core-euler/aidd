from __future__ import annotations

from datetime import datetime

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..config import Config
from ..db.models import Difficulty, TaskStatus
from ..db.session import Database
from ..services.constants import DIFFICULTY_CONFIG
from ..services.task_service import TaskService
from ..services.user_service import UserService
from ..storage.states import CreateTask
from ..utils.formatting import format_dt, xp_to_next
from ..utils.time import parse_human_datetime, quick_deadline, to_utc, utc_now
from .keyboards import (
    Cb,
    back_to_menu,
    back_to_tasks,
    deadline_keyboard,
    difficulty_keyboard,
    main_menu,
    notification_keyboard,
    start_menu,
    task_created_keyboard,
    task_details_keyboard,
    task_list_keyboard,
)
from .screens import (
    character_text,
    main_menu_text,
    stats_text,
    task_completed_text,
    task_created_text,
    task_details_text,
    welcome_text,
)


router = Router()
logger = logging.getLogger("bot.actions")


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, db: Database, config: Config) -> None:
    await state.clear()
    async with db.session() as session:
        user_service = UserService(session)
        user = await user_service.get_or_create(message.from_user.id, message.from_user.username)
        await session.commit()

    logger.info("start: telegram_id=%s username=%s", message.from_user.id, message.from_user.username)
    if user.total_completed == 0 and user.total_failed == 0 and user.level == 1 and user.xp == 0:
        await message.answer(welcome_text(user), reply_markup=start_menu())
    else:
        await message.answer(main_menu_text(user), reply_markup=main_menu())


@router.callback_query(F.data == Cb.MENU)
async def cb_menu(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    await state.clear()
    async with db.session() as session:
        user = await UserService(session).get_or_create(query.from_user.id, query.from_user.username)
        await session.commit()
    await query.message.edit_text(main_menu_text(user), reply_markup=main_menu())
    await query.answer()


@router.callback_query(F.data == Cb.CHARACTER)
async def cb_character(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    await state.clear()
    async with db.session() as session:
        user_service = UserService(session)
        task_service = TaskService(session)
        user = await user_service.get_or_create(query.from_user.id, query.from_user.username)
        tasks = await task_service.list_active(user.id)
        next_deadline = tasks[0].deadline if tasks else None
        await session.commit()
    text = character_text(user, len(tasks), next_deadline, config.timezone)
    await query.message.edit_text(text, reply_markup=back_to_menu())
    await query.answer()


@router.callback_query(F.data == Cb.STATS)
async def cb_stats(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    await state.clear()
    async with db.session() as session:
        user = await UserService(session).get_or_create(query.from_user.id, query.from_user.username)
        await session.commit()
    await query.message.edit_text(stats_text(user), reply_markup=back_to_menu())
    await query.answer()


@router.callback_query(F.data == Cb.NEW_TASK)
async def cb_new_task(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    await state.set_state(CreateTask.title)
    await query.message.edit_text(
        "➕ Новая задача\n\nВведи название задачи:",
        reply_markup=back_to_menu(),
    )
    await query.answer()


@router.message(CreateTask.title)
async def msg_task_title(message: Message, state: FSMContext, db: Database, config: Config) -> None:
    async with db.session() as session:
        task_service = TaskService(session)
        result = task_service.normalize_title(message.text or "")
        if not result.title:
            await message.answer("Название не может быть пустым. Введи ещё раз:")
            return
        await state.update_data(title=result.title, title_truncated=result.truncated)
    await state.set_state(CreateTask.difficulty)
    await message.answer(
        f"➕ Новая задача\n\n📝 {result.title}\n\nВыбери сложность:",
        reply_markup=difficulty_keyboard(),
    )


@router.callback_query(F.data.startswith(Cb.DIFF_PREFIX))
async def cb_task_difficulty(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    data = await state.get_data()
    if "title" not in data:
        await query.answer("Сначала укажи название задачи.", show_alert=True)
        return
    diff_value = query.data.replace(Cb.DIFF_PREFIX, "")
    try:
        difficulty = Difficulty(diff_value)
    except ValueError:
        await query.answer("Неизвестная сложность.", show_alert=True)
        return

    await state.update_data(difficulty=difficulty.value)
    await state.set_state(CreateTask.deadline)
    cfg = DIFFICULTY_CONFIG[difficulty]
    await query.message.edit_text(
        f"➕ Новая задача\n\n📝 {data['title']}\n"
        f"⚡ {cfg.label} (+{cfg.xp} XP / -{cfg.damage} HP)\n\n"
        "Когда дедлайн?",
        reply_markup=deadline_keyboard(),
    )
    await query.answer()


@router.callback_query(F.data.startswith(Cb.DEADLINE_QUICK_PREFIX))
async def cb_deadline_quick(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    if await state.get_state() != CreateTask.deadline.state:
        await query.answer("Сейчас не выбирается дедлайн.", show_alert=True)
        return
    option = query.data.replace(Cb.DEADLINE_QUICK_PREFIX, "")
    local_dt = quick_deadline(option, config.timezone)
    await finalize_task_creation(query, state, db, config, local_dt)


@router.callback_query(F.data == Cb.DEADLINE_MANUAL)
async def cb_deadline_manual(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    if await state.get_state() != CreateTask.deadline.state:
        await query.answer("Сейчас не выбирается дедлайн.", show_alert=True)
        return
    await query.message.edit_text(
        "Введи дедлайн вручную. Примеры:\n"
        "- завтра 18:00\n"
        "- 25.01 15:30\n"
        "- через 2 часа",
        reply_markup=back_to_menu(),
    )
    await query.answer()


@router.message(CreateTask.deadline)
async def msg_deadline_manual(message: Message, state: FSMContext, db: Database, config: Config) -> None:
    parsed = parse_human_datetime(message.text or "", config.timezone)
    if not parsed:
        await message.answer("Не понял дату. Введи ещё раз с примерами:")
        return
    await finalize_task_creation(message, state, db, config, parsed)


async def finalize_task_creation(target, state: FSMContext, db: Database, config: Config, local_dt: datetime) -> None:
    data = await state.get_data()
    if "title" not in data or "difficulty" not in data:
        if hasattr(target, "answer"):
            await target.answer("Не хватает данных для создания задачи.", show_alert=True)
        return

    if local_dt.tzinfo is None:
        await target.answer("Некорректная дата.", show_alert=True)
        return

    deadline_utc = to_utc(local_dt)
    if deadline_utc <= utc_now():
        if hasattr(target, "message"):
            await target.message.answer("Дедлайн в прошлом. Введи другую дату:")
        else:
            await target.answer("Дедлайн в прошлом.", show_alert=True)
        return

    async with db.session() as session:
        user_service = UserService(session)
        task_service = TaskService(session)
        user = await user_service.get_or_create(target.from_user.id, target.from_user.username)
        difficulty = Difficulty(data["difficulty"])
        task = await task_service.create_task(user.id, data["title"], difficulty, deadline_utc)
        await session.commit()

    logger.info(
        "task_created: telegram_id=%s task_id=%s difficulty=%s deadline_utc=%s",
        target.from_user.id,
        task.id,
        task.difficulty.value,
        task.deadline.isoformat(),
    )
    await state.clear()
    text = task_created_text(task, config.timezone)
    if data.get("title_truncated"):
        text = "Название было обрезано до 200 символов.\n\n" + text

    if hasattr(target, "message"):
        await target.message.edit_text(text, reply_markup=task_created_keyboard())
        await target.answer()
    else:
        await target.answer(text, reply_markup=task_created_keyboard())


@router.callback_query(F.data == Cb.TASKS)
async def cb_tasks(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    await state.clear()
    async with db.session() as session:
        user_service = UserService(session)
        task_service = TaskService(session)
        user = await user_service.get_or_create(query.from_user.id, query.from_user.username)
        tasks = await task_service.list_active(user.id)
        await session.commit()

    if not tasks:
        await query.message.edit_text(
            "📋 Твои задачи\n\nУ тебя нет активных задач.",
            reply_markup=back_to_menu(),
        )
        await query.answer()
        return

    labels = [(task.id, f"📌 {task.title} — {human_short(task.deadline, config.timezone)}") for task in tasks]
    await query.message.edit_text("📋 Твои задачи", reply_markup=task_list_keyboard(labels))
    await query.answer()


def human_short(deadline: datetime, tz_name: str) -> str:
    from ..utils.formatting import human_delta_until

    return human_delta_until(deadline, tz_name)


@router.callback_query(F.data == Cb.OVERDUE)
async def cb_overdue(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    await state.clear()
    async with db.session() as session:
        user = await UserService(session).get_or_create(query.from_user.id, query.from_user.username)
        tasks = await TaskService(session).list_failed(user.id)
        await session.commit()

    if not tasks:
        await query.message.edit_text(
            "⛔ Просроченные\n\nУ тебя нет просроченных задач.",
            reply_markup=back_to_menu(),
        )
        await query.answer()
        return

    labels = [(task.id, f"💀 {task.title} — {format_dt(task.deadline, config.timezone)}") for task in tasks]
    await query.message.edit_text("⛔ Просроченные", reply_markup=task_list_keyboard(labels))
    await query.answer()


@router.callback_query(F.data.startswith(Cb.TASK_VIEW_PREFIX))
async def cb_task_view(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    await state.clear()
    task_id = int(query.data.replace(Cb.TASK_VIEW_PREFIX, ""))
    async with db.session() as session:
        user = await UserService(session).get_or_create(query.from_user.id, query.from_user.username)
        task = await TaskService(session).get_task(task_id, user.id)
        await session.commit()

    if not task:
        await query.answer("Задача не найдена.", show_alert=True)
        return

    await query.message.edit_text(task_details_text(task, config.timezone), reply_markup=task_details_keyboard(task.id))
    await query.answer()


@router.callback_query(F.data.startswith(Cb.TASK_DONE_PREFIX))
async def cb_task_done(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    await state.clear()
    task_id = int(query.data.replace(Cb.TASK_DONE_PREFIX, ""))

    async with db.session() as session:
        user_service = UserService(session)
        task_service = TaskService(session)
        user = await user_service.get_or_create(query.from_user.id, query.from_user.username)
        task = await task_service.get_task(task_id, user.id)
        if not task or task.status in {TaskStatus.deleted, TaskStatus.completed}:
            await query.answer("Задача не найдена.", show_alert=True)
            return

        xp_gain = 0
        leveled_up = False
        if task.deadline <= utc_now():
            await task_service.mark_failed(task)
            user_service.record_failure(user)
        else:
            xp_gain = DIFFICULTY_CONFIG[task.difficulty].xp
            await task_service.complete_task(task)
            user_service.record_completion(user)
            level_result = user_service.apply_xp(user, xp_gain)
            leveled_up = level_result.leveled_up

        await session.commit()

    logger.info(
        "task_completed: telegram_id=%s task_id=%s xp=%s status=%s",
        query.from_user.id,
        task_id,
        xp_gain,
        task.status.value,
    )
    if xp_gain > 0:
        await query.message.edit_text(task_completed_text(task, user, xp_gain), reply_markup=back_to_tasks())
    else:
        await query.message.edit_text(
            "Задача просрочена. Опыт не начислен.",
            reply_markup=back_to_tasks(),
        )
    await query.answer()

    if xp_gain > 0 and leveled_up:
        await query.message.answer(
            f"🎉 Уровень повышен!\n🎖 Новый уровень: {user.level}\n❤️ {user.hp}/{user.max_hp}\n✨ {user.xp}/{xp_to_next(user.level)}",
            reply_markup=back_to_menu(),
        )


@router.callback_query(F.data.startswith(Cb.TASK_DELETE_PREFIX))
async def cb_task_delete(query: CallbackQuery, state: FSMContext, db: Database, config: Config) -> None:
    await state.clear()
    task_id = int(query.data.replace(Cb.TASK_DELETE_PREFIX, ""))

    async with db.session() as session:
        user = await UserService(session).get_or_create(query.from_user.id, query.from_user.username)
        task_service = TaskService(session)
        task = await task_service.get_task(task_id, user.id)
        if not task:
            await query.answer("Задача не найдена.", show_alert=True)
            return
        await task_service.delete_task(task)
        await session.commit()

    logger.info("task_deleted: telegram_id=%s task_id=%s", query.from_user.id, task_id)
    await query.message.edit_text("Задача удалена.", reply_markup=back_to_tasks())
    await query.answer()
