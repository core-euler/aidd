from __future__ import annotations

import logging
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.constants import DIFFICULTY_VALUES, STATUS_ACTIVE, STATUS_FAILED, STATUS_COMPLETED, STATUS_DELETED
from app.keyboards import (
    cancel_keyboard,
    deadline_keyboard,
    difficulty_keyboard,
    menu_keyboard,
    task_created_keyboard,
    task_detail_keyboard,
    task_completed_keyboard,
    tasks_list_keyboard,
    tasks_failed_keyboard,
    back_to_menu_keyboard,
    death_keyboard,
    back_to_tasks_keyboard,
)
from app.services.users import get_or_create_user
from app.services.tasks import (
    create_task,
    list_active_tasks,
    list_failed_tasks,
    get_task,
    mark_task_completed,
    mark_task_deleted,
    mark_task_failed,
    delete_active_tasks,
)
from app.services.character import apply_xp, apply_damage
from app.states import TaskCreate
from app.ui_texts import (
    task_created_text,
    tasks_list_text,
    no_tasks_text,
    task_detail_text,
    task_completed_text,
    level_up_text,
    overdue_text,
    death_text,
    invalid_date_text,
)
from app.utils.time_utils import (
    format_deadline_local,
    format_remaining,
    parse_deadline,
    to_utc,
    now_utc,
)
from app.runtime import get_session_factory, get_timezone

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(lambda c: c.data == "new_task")
async def new_task(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(TaskCreate.waiting_title)
    await callback.message.edit_text("➕ Новая задача\n\nВведи название задачи:", reply_markup=cancel_keyboard())
    await callback.answer()


@router.message(TaskCreate.waiting_title)
async def task_title(message: Message, state: FSMContext):
    title = (message.text or "").strip()
    if not title:
        await message.answer("Название не может быть пустым. Введи ещё раз:", reply_markup=cancel_keyboard())
        return

    if len(title) > 200:
        title = title[:200]
        await message.answer("Название длиннее 200 символов. Обрезано до 200.")

    await state.update_data(title=title)
    await state.set_state(TaskCreate.waiting_difficulty)
    await message.answer(
        f"➕ Новая задача\n\n📝 {title}\n\nВыбери сложность:",
        reply_markup=difficulty_keyboard(),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("diff:"))
async def task_difficulty(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    title = data.get("title")
    if not title:
        await callback.message.answer("Сначала введи название задачи.")
        await state.set_state(TaskCreate.waiting_title)
        await callback.answer()
        return

    diff_key = callback.data.split(":", 1)[1]
    if diff_key not in DIFFICULTY_VALUES:
        await callback.message.answer("Неизвестная сложность. Выбери снова.")
        await callback.answer()
        return

    await state.update_data(difficulty=diff_key)
    await state.set_state(TaskCreate.waiting_deadline)

    diff = DIFFICULTY_VALUES[diff_key]
    await callback.message.edit_text(
        "➕ Новая задача\n\n"
        f"📝 {title}\n"
        f"⚡ {diff['label']} (+{diff['xp']} XP / -{diff['damage']} HP)\n\n"
        "Когда дедлайн?",
        reply_markup=deadline_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("deadline:"))
async def task_deadline(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    title = data.get("title")
    difficulty = data.get("difficulty")
    if not title or not difficulty:
        await callback.message.answer("Сначала заполни название и сложность.")
        await state.clear()
        await callback.answer()
        return

    option = callback.data.split(":", 1)[1]
    tz = get_timezone()
    now_local = datetime.now(tz)

    if option == "manual":
        await state.set_state(TaskCreate.waiting_deadline_manual)
        await callback.message.edit_text(
            "Введи дедлайн вручную (например, 'завтра 18:00' или '25.01 15:30'):",
            reply_markup=cancel_keyboard(),
        )
        await callback.answer()
        return

    if option == "in1h":
        deadline_local = now_local + timedelta(hours=1)
    elif option == "in3h":
        deadline_local = now_local + timedelta(hours=3)
    elif option == "today21":
        deadline_local = now_local.replace(hour=21, minute=0, second=0, microsecond=0)
    elif option == "tomorrow10":
        tomorrow = now_local + timedelta(days=1)
        deadline_local = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    elif option == "tomorrow18":
        tomorrow = now_local + timedelta(days=1)
        deadline_local = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)
    else:
        await callback.message.answer("Неизвестный дедлайн. Попробуй снова.")
        await callback.answer()
        return

    if deadline_local <= now_local:
        await callback.message.answer("Этот дедлайн уже в прошлом. Выбери другой.")
        await callback.answer()
        return

    await finalize_task_creation(callback, state, title, difficulty, deadline_local)
    await callback.answer()


@router.message(TaskCreate.waiting_deadline_manual)
async def task_deadline_manual(message: Message, state: FSMContext):
    tz = get_timezone()
    now_local = datetime.now(tz)

    parsed = parse_deadline(message.text or "", now_local, tz)
    if parsed.error or not parsed.value:
        await message.answer(invalid_date_text(), reply_markup=cancel_keyboard())
        return

    if parsed.value <= now_local:
        await message.answer("Дедлайн в прошлом. Введи другую дату:", reply_markup=cancel_keyboard())
        return

    data = await state.get_data()
    title = data.get("title")
    difficulty = data.get("difficulty")
    if not title or not difficulty:
        await message.answer("Сначала заполни название и сложность.")
        await state.clear()
        return

    await finalize_task_creation(message, state, title, difficulty, parsed.value)


async def finalize_task_creation(event, state: FSMContext, title: str, difficulty: str, deadline_local: datetime):
    session_factory = get_session_factory()
    tz = get_timezone()
    deadline_utc = to_utc(deadline_local, tz)

    async with session_factory() as session:
        user, _ = await get_or_create_user(
            session,
            telegram_id=event.from_user.id,
            username=event.from_user.username,
        )
        task = await create_task(session, user.id, title, difficulty, deadline_utc)
        await session.commit()

    await state.clear()
    deadline_str = format_deadline_local(task.deadline, tz)
    text = task_created_text(task, deadline_str)

    message = getattr(event, "message", None)
    if message:
        await message.edit_text(text, reply_markup=task_created_keyboard())
    else:
        await event.answer(text, reply_markup=task_created_keyboard())
    logger.info("task_created", extra={"user_id": user.id, "task_id": task.id})


@router.callback_query(lambda c: c.data == "tasks")
async def tasks_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    session_factory = get_session_factory()
    tz = get_timezone()
    async with session_factory() as session:
        user, _ = await get_or_create_user(
            session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
        )
        tasks = await list_active_tasks(session, user.id)
        await session.commit()

    if not tasks:
        await callback.message.edit_text(no_tasks_text(), reply_markup=menu_keyboard())
        await callback.answer()
        return

    items = []
    for task in tasks:
        remaining = format_remaining(task.deadline, tz)
        items.append((task.id, task.title, remaining))

    await callback.message.edit_text(
        tasks_list_text(len(tasks)),
        reply_markup=tasks_list_keyboard(items),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "tasks_failed")
async def tasks_failed(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    session_factory = get_session_factory()
    async with session_factory() as session:
        user, _ = await get_or_create_user(
            session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
        )
        tasks = await list_failed_tasks(session, user.id)
        await session.commit()

    if not tasks:
        await callback.message.edit_text("Нет просроченных задач.", reply_markup=back_to_tasks_keyboard())
        await callback.answer()
        return

    items = [(task.id, task.title) for task in tasks]
    await callback.message.edit_text(
        f"⛔ Просроченные задачи ({len(tasks)})",
        reply_markup=tasks_failed_keyboard(items),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("task:"))
async def task_detail(callback: CallbackQuery):
    session_factory = get_session_factory()
    tz = get_timezone()
    task_id = int(callback.data.split(":", 1)[1])

    async with session_factory() as session:
        user, _ = await get_or_create_user(
            session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
        )
        task = await get_task(session, user.id, task_id)
        await session.commit()

    if not task:
        await callback.message.answer("Задача не найдена.")
        await callback.answer()
        return

    deadline_str = format_deadline_local(task.deadline, tz)
    remaining = format_remaining(task.deadline, tz)
    text = task_detail_text(task, deadline_str, remaining)
    if task.status == STATUS_ACTIVE:
        keyboard = task_detail_keyboard(task.id)
    else:
        keyboard = back_to_menu_keyboard()
        text += "\n\nСтатус: просрочена или завершена."

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("task_done:"))
async def task_done(callback: CallbackQuery):
    session_factory = get_session_factory()
    tz = get_timezone()
    task_id = int(callback.data.split(":", 1)[1])
    now = now_utc()

    async with session_factory() as session:
        user, _ = await get_or_create_user(
            session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
        )
        task = await get_task(session, user.id, task_id)
        if not task:
            await callback.message.answer("Задача не найдена.")
            await session.commit()
            await callback.answer()
            return

        if task.status == STATUS_ACTIVE and task.deadline > now:
            await mark_task_completed(session, task, now)
            user.total_completed += 1
            level_up = apply_xp(user, DIFFICULTY_VALUES[task.difficulty]["xp"])
            await session.commit()

            await callback.message.edit_text(task_completed_text(task, user), reply_markup=task_completed_keyboard())
            logger.info("task_completed", extra={"user_id": user.id, "task_id": task.id})

            if level_up:
                await callback.message.answer(level_up_text(user), reply_markup=menu_keyboard())
            await callback.answer()
            return

        if task.status == STATUS_ACTIVE and task.deadline <= now:
            await mark_task_failed(session, task)
            user.total_failed += 1
            dmg = DIFFICULTY_VALUES[task.difficulty]["damage"]
            original_hp = user.hp
            user.hp = max(0, original_hp - dmg)
            message_text = overdue_text(task, user, dmg)
            user.hp = original_hp
            damage_result = apply_damage(user, dmg)
            if damage_result.died:
                await delete_active_tasks(session, user.id)
            await session.commit()

            await callback.message.edit_text(message_text, reply_markup=menu_keyboard())
            if damage_result.died:
                await callback.message.answer(death_text(user), reply_markup=death_keyboard())
            await callback.answer()
            return

        if task.status in {STATUS_FAILED, STATUS_COMPLETED, STATUS_DELETED}:
            await session.commit()
            await callback.message.answer("Задача уже обработана.", reply_markup=menu_keyboard())
            await callback.answer()
            return


@router.callback_query(lambda c: c.data and c.data.startswith("task_del:"))
async def task_delete(callback: CallbackQuery):
    session_factory = get_session_factory()
    task_id = int(callback.data.split(":", 1)[1])

    async with session_factory() as session:
        user, _ = await get_or_create_user(
            session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
        )
        task = await get_task(session, user.id, task_id)
        if not task:
            await callback.message.answer("Задача не найдена.")
            await session.commit()
            await callback.answer()
            return

        if task.status == STATUS_DELETED:
            await session.commit()
            await callback.message.answer("Задача уже удалена.")
            await callback.answer()
            return

        if task.status == STATUS_COMPLETED:
            await session.commit()
            await callback.message.answer("Задача уже выполнена.")
            await callback.answer()
            return

        await mark_task_deleted(session, task)
        await session.commit()

    await callback.message.edit_text("Задача удалена.", reply_markup=menu_keyboard())
    logger.info("task_deleted", extra={"user_id": user.id, "task_id": task.id})
    await callback.answer()
