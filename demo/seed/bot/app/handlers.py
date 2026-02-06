import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from .keyboards import (
    MENU,
    NEW_TASK,
    TASKS,
    CHARACTER,
    STATS,
    OVERDUE,
    BACK_TASKS,
    CANCEL_NEW,
    main_menu_keyboard,
    welcome_keyboard,
    back_to_menu_keyboard,
    tasks_keyboard,
    task_detail_keyboard,
    difficulty_keyboard,
    deadline_keyboard,
    after_task_created_keyboard,
    after_task_completed_keyboard,
    cancel_keyboard,
)
from .models import TaskDifficulty, TaskStatus
from .services.users import get_or_create_user, apply_xp, apply_damage, user_success_rate
from .services.tasks import (
    create_task,
    list_active_tasks,
    list_failed_tasks,
    get_task,
    mark_completed,
    mark_deleted,
    mark_failed,
    DIFFICULTY_REWARDS,
)
from .utils.text import (
    welcome_text,
    main_menu_text,
    character_text,
    stats_text,
    task_detail_text,
    overdue_list_text,
    format_deadline,
    time_left_text,
)
from .utils.timeparse import parse_deadline, quick_deadline, DeadlineParseError

logger = logging.getLogger(__name__)
router = Router()
UTC = ZoneInfo("UTC")


class NewTask(StatesGroup):
    title = State()
    difficulty = State()
    deadline = State()
    deadline_manual = State()


def _normalize_dt(dt: datetime, tz: ZoneInfo) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def _tz(timezone: ZoneInfo) -> ZoneInfo:
    return timezone


def _session(session_factory):
    return session_factory()


@router.message(CommandStart())
async def start(message: Message, session_factory, timezone: ZoneInfo) -> None:
    with _session(session_factory) as session:
        user, created = get_or_create_user(session, message.from_user.id, message.from_user.username)
        active_tasks = list_active_tasks(session, user.id)
    logger.info("start user_id=%s created=%s", message.from_user.id, created)
    if created:
        await message.answer(welcome_text(user), reply_markup=welcome_keyboard())
    else:
        await message.answer(
            main_menu_text(user, len(active_tasks)),
            reply_markup=main_menu_keyboard(len(active_tasks)),
        )


@router.callback_query(F.data == MENU)
async def open_menu(call: CallbackQuery, session_factory, timezone: ZoneInfo) -> None:
    await call.answer()
    with _session(session_factory) as session:
        user, _ = get_or_create_user(session, call.from_user.id, call.from_user.username)
        active_tasks = list_active_tasks(session, user.id)
    if call.message:
        await call.message.edit_text(
            main_menu_text(user, len(active_tasks)),
            reply_markup=main_menu_keyboard(len(active_tasks)),
        )


@router.callback_query(F.data == TASKS)
async def open_tasks(call: CallbackQuery, session_factory, timezone: ZoneInfo) -> None:
    await call.answer()
    tz = _tz(timezone)
    with _session(session_factory) as session:
        user, _ = get_or_create_user(session, call.from_user.id, call.from_user.username)
        tasks = list_active_tasks(session, user.id)
    logger.info("open_tasks user_id=%s count=%s", call.from_user.id, len(tasks))
    if call.message:
        if not tasks:
            now = datetime.now(tz)
            await call.message.edit_text("Активных задач нет.", reply_markup=tasks_keyboard([], now, tz))
            return
        now = datetime.now(tz)
        await call.message.edit_text("📋 Твои задачи:", reply_markup=tasks_keyboard(tasks, now, tz))


@router.callback_query(F.data == BACK_TASKS)
async def open_tasks_back(call: CallbackQuery, session_factory, timezone: ZoneInfo) -> None:
    await open_tasks(call, session_factory, timezone)


@router.callback_query(F.data == OVERDUE)
async def open_overdue(call: CallbackQuery, session_factory, timezone: ZoneInfo) -> None:
    await call.answer()
    tz = _tz(timezone)
    with _session(session_factory) as session:
        user, _ = get_or_create_user(session, call.from_user.id, call.from_user.username)
        tasks = list_failed_tasks(session, user.id)
    logger.info("open_overdue user_id=%s count=%s", call.from_user.id, len(tasks))
    if call.message:
        await call.message.edit_text(overdue_list_text(tasks, tz), reply_markup=back_to_menu_keyboard())


@router.callback_query(F.data == CHARACTER)
async def open_character(call: CallbackQuery, session_factory, timezone: ZoneInfo) -> None:
    await call.answer()
    tz = _tz(timezone)
    with _session(session_factory) as session:
        user, _ = get_or_create_user(session, call.from_user.id, call.from_user.username)
        tasks = list_active_tasks(session, user.id)
        nearest = None
        if tasks:
            nearest = time_left_text(tasks[0].deadline, datetime.now(tz))
    logger.info("open_character user_id=%s", call.from_user.id)
    if call.message:
        await call.message.edit_text(
            character_text(user, len(tasks), nearest), reply_markup=back_to_menu_keyboard()
        )


@router.callback_query(F.data == STATS)
async def open_stats(call: CallbackQuery, session_factory, timezone: ZoneInfo) -> None:
    await call.answer()
    with _session(session_factory) as session:
        user, _ = get_or_create_user(session, call.from_user.id, call.from_user.username)
        rate = user_success_rate(user)
    logger.info("open_stats user_id=%s", call.from_user.id)
    if call.message:
        await call.message.edit_text(stats_text(user, rate), reply_markup=back_to_menu_keyboard())


@router.callback_query(F.data.startswith("task:"))
async def open_task_detail(call: CallbackQuery, session_factory, timezone: ZoneInfo) -> None:
    await call.answer()
    tz = _tz(timezone)
    task_id = int(call.data.split(":", 1)[1])
    with _session(session_factory) as session:
        user, _ = get_or_create_user(session, call.from_user.id, call.from_user.username)
        task = get_task(session, user.id, task_id)
        if task is None:
            if call.message:
                await call.message.edit_text("Задача не найдена.", reply_markup=back_to_menu_keyboard())
            return
        now = datetime.now(tz)
    logger.info("open_task_detail user_id=%s task_id=%s", call.from_user.id, task_id)
    if call.message:
        await call.message.edit_text(task_detail_text(task, now, tz), reply_markup=task_detail_keyboard(task.id))


@router.callback_query(F.data.startswith("complete:"))
async def complete_task(call: CallbackQuery, session_factory, timezone: ZoneInfo) -> None:
    await call.answer()
    tz = _tz(timezone)
    task_id = int(call.data.split(":", 1)[1])
    with _session(session_factory) as session:
        user, _ = get_or_create_user(session, call.from_user.id, call.from_user.username)
        task = get_task(session, user.id, task_id)
        if task is None:
            if call.message:
                await call.message.edit_text("Задача не найдена.", reply_markup=back_to_menu_keyboard())
            return

        now = datetime.now(tz)
        if task.status != TaskStatus.active:
            if call.message:
                await call.message.edit_text("Эта задача уже обработана.", reply_markup=back_to_menu_keyboard())
            return

        deadline = _normalize_dt(task.deadline, tz).astimezone(UTC)
        if deadline <= datetime.now(UTC):
            reward, damage = DIFFICULTY_REWARDS[task.difficulty]
            mark_failed(task)
            user.total_failed += 1
            died = apply_damage(user, damage)
            session.commit()
            logger.info("complete_overdue user_id=%s task_id=%s died=%s", call.from_user.id, task_id, died)
            if call.message:
                if died:
                    session.query(task.__class__).filter(
                        task.__class__.user_id == user.id,
                        task.__class__.status == TaskStatus.active,
                    ).delete(synchronize_session=False)
                    session.commit()
                    await call.message.edit_text(
                        "💀 Ваш персонаж погиб! Прогресс сброшен.\nВсе активные задачи удалены.",
                        reply_markup=back_to_menu_keyboard(),
                    )
                else:
                    await call.message.edit_text(
                        "Задача просрочена. Опыт не начислен.",
                        reply_markup=back_to_menu_keyboard(),
                    )
            return

        reward, _ = DIFFICULTY_REWARDS[task.difficulty]
        mark_completed(task)
        user.total_completed += 1
        level_ups = apply_xp(user, reward)
        session.commit()
        logger.info("complete_task user_id=%s task_id=%s reward=%s level_ups=%s", call.from_user.id, task_id, reward, level_ups)

        if call.message:
            await call.message.edit_text(
                f"🎉 Задача выполнена!\n\n📝 {task.title}\n✨ +{reward} XP",
                reply_markup=after_task_completed_keyboard(),
            )

    if level_ups > 0:
        await call.bot.send_message(
            chat_id=call.from_user.id,
            text=(
                f"🎉 Уровень повышен!\n\n"
                f"🎖 Новый уровень: {user.level}\n"
                f"❤️ Здоровье восстановлено: {user.hp}/{user.max_hp}\n"
                f"✨ До следующего: {user.xp}/{user.level * 100}"
            ),
        )



@router.callback_query(F.data.startswith("delete:"))
async def delete_task(call: CallbackQuery, session_factory) -> None:
    await call.answer()
    task_id = int(call.data.split(":", 1)[1])
    with _session(session_factory) as session:
        user, _ = get_or_create_user(session, call.from_user.id, call.from_user.username)
        task = get_task(session, user.id, task_id)
        if task is None:
            if call.message:
                await call.message.edit_text("Задача не найдена.", reply_markup=back_to_menu_keyboard())
            return
        if task.status != TaskStatus.active:
            if call.message:
                await call.message.edit_text("Эта задача уже обработана.", reply_markup=back_to_menu_keyboard())
            return
        mark_deleted(task)
        session.commit()
    logger.info("delete_task user_id=%s task_id=%s", call.from_user.id, task_id)
    if call.message:
        await call.message.edit_text("Задача удалена.", reply_markup=back_to_menu_keyboard())


@router.callback_query(F.data == NEW_TASK)
async def new_task_start(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.clear()
    await state.set_state(NewTask.title)
    if call.message:
        await call.message.edit_text("Введи название задачи:", reply_markup=cancel_keyboard())


@router.message(NewTask.title)
async def new_task_title(message: Message, state: FSMContext) -> None:
    title = (message.text or "").strip()
    if not title:
        await message.answer("Название не может быть пустым. Введи ещё раз.")
        return
    truncated = False
    if len(title) > 200:
        title = title[:200]
        truncated = True
    await state.update_data(title=title)
    text = "Выбери сложность:"
    if truncated:
        text = "Название было обрезано до 200 символов.\n\n" + text
    await state.set_state(NewTask.difficulty)
    await message.answer(text, reply_markup=difficulty_keyboard())


@router.callback_query(F.data.startswith("diff:"))
async def new_task_difficulty(call: CallbackQuery, state: FSMContext) -> None:
    current = await state.get_state()
    if current != NewTask.difficulty.state:
        await call.answer("Сначала введи название задачи", show_alert=False)
        return
    await call.answer()
    difficulty_key = call.data.split(":", 1)[1]
    difficulty = TaskDifficulty(difficulty_key)
    await state.update_data(difficulty=difficulty)
    await state.set_state(NewTask.deadline)
    if call.message:
        await call.message.edit_text("Когда дедлайн?", reply_markup=deadline_keyboard())


@router.callback_query(F.data == CANCEL_NEW)
async def cancel_new_task(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.clear()
    if call.message:
        await call.message.edit_text("Создание задачи отменено.", reply_markup=back_to_menu_keyboard())


@router.callback_query(F.data.startswith("dl:"))
async def new_task_deadline_quick(call: CallbackQuery, state: FSMContext, session_factory, timezone: ZoneInfo) -> None:
    current = await state.get_state()
    if current != NewTask.deadline.state:
        await call.answer("Сначала выбери сложность", show_alert=False)
        return
    await call.answer()
    key = call.data.split(":", 1)[1]
    deadline = quick_deadline(key, timezone)
    await _finish_task_creation(call, state, session_factory, timezone, deadline)


@router.callback_query(F.data == "dl_manual")
async def new_task_deadline_manual_prompt(call: CallbackQuery, state: FSMContext) -> None:
    current = await state.get_state()
    if current != NewTask.deadline.state:
        await call.answer("Сначала выбери сложность", show_alert=False)
        return
    await call.answer()
    await state.set_state(NewTask.deadline_manual)
    if call.message:
        await call.message.edit_text(
            "Введи дату и время. Пример: 'завтра 18:00' или '25.01 15:30'",
            reply_markup=cancel_keyboard(),
        )


@router.message(NewTask.deadline_manual)
async def new_task_deadline_manual(message: Message, state: FSMContext, session_factory, timezone: ZoneInfo) -> None:
    try:
        deadline = parse_deadline(message.text or "", timezone)
    except DeadlineParseError as exc:
        await message.answer(str(exc), reply_markup=cancel_keyboard())
        return
    await _finish_task_creation(message, state, session_factory, timezone, deadline)


async def _finish_task_creation(target, state: FSMContext, session_factory, timezone: ZoneInfo, deadline: datetime) -> None:
    now = datetime.now(timezone)
    if deadline <= now:
        if isinstance(target, Message):
            await target.answer("Дедлайн в прошлом. Введи другую дату.", reply_markup=deadline_keyboard())
        else:
            if target.message:
                await target.message.edit_text("Дедлайн в прошлом. Введи другую дату.", reply_markup=deadline_keyboard())
        return

    data = await state.get_data()
    title = data.get("title")
    difficulty = data.get("difficulty")
    if not title or not difficulty:
        await state.clear()
        if isinstance(target, Message):
            await target.answer("Создание задачи прервано. Начни заново.")
        else:
            if target.message:
                await target.message.edit_text("Создание задачи прервано. Начни заново.")
        return

    deadline_utc = deadline.astimezone(UTC)
    with _session(session_factory) as session:
        username = target.from_user.username if target.from_user else None
        user, _ = get_or_create_user(session, target.from_user.id, username)
        task = create_task(session, user.id, title, difficulty, deadline_utc)

    logger.info("create_task user_id=%s task_id=%s difficulty=%s deadline=%s", target.from_user.id, task.id, difficulty.value, deadline.isoformat())

    text = (
        "✅ Задача создана!\n\n"
        f"📝 {task.title}\n"
        f"⚡ {task.difficulty.value.capitalize()}\n"
        f"⏰ Дедлайн: {format_deadline(task.deadline, timezone)}\n\n"
        "Удачи!"
    )

    await state.clear()

    if isinstance(target, Message):
        await target.answer(text, reply_markup=after_task_created_keyboard())
    else:
        if target.message:
            await target.message.edit_text(text, reply_markup=after_task_created_keyboard())


@router.message()
async def fallback_text(message: Message) -> None:
    await message.answer("Используй кнопки меню или команду /start.")
