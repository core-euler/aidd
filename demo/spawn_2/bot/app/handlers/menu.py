from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards import menu_keyboard, back_to_menu_keyboard
from app.runtime import get_session_factory, get_timezone
from app.services.users import get_or_create_user
from app.services.tasks import list_active_tasks
from app.services.stats import build_stats
from app.ui_texts import menu_text, character_text, stats_text
from app.utils.time_utils import format_deadline_local

router = Router()


@router.callback_query(lambda c: c.data == "menu")
async def menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    session_factory = get_session_factory()
    async with session_factory() as session:
        user, _ = await get_or_create_user(
            session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
        )
        tasks = await list_active_tasks(session, user.id)
        await session.commit()

    text = menu_text(user, len(tasks))
    await callback.message.edit_text(text, reply_markup=menu_keyboard(len(tasks)))
    await callback.answer()


@router.callback_query(lambda c: c.data == "character")
async def character_handler(callback: CallbackQuery, state: FSMContext):
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
        nearest = None
        if tasks:
            nearest = format_deadline_local(tasks[0].deadline, tz)
        await session.commit()

    text = character_text(user, len(tasks), nearest)
    await callback.message.edit_text(text, reply_markup=back_to_menu_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data == "stats")
async def stats_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    session_factory = get_session_factory()
    async with session_factory() as session:
        user, _ = await get_or_create_user(
            session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
        )
        stats = build_stats(user)
        await session.commit()

    text = stats_text(stats, user.created_at)
    await callback.message.edit_text(text, reply_markup=back_to_menu_keyboard())
    await callback.answer()
