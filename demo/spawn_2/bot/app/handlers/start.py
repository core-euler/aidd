from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards import menu_keyboard, welcome_keyboard
from app.runtime import get_session_factory
from app.services.users import get_or_create_user
from app.services.tasks import list_active_tasks
from app.ui_texts import welcome_text, menu_text

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    session_factory = get_session_factory()
    async with session_factory() as session:
        user, created = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
        )
        await session.commit()

        if created:
            text = welcome_text(user)
            await message.answer(text, reply_markup=welcome_keyboard())
            return

        tasks = await list_active_tasks(session, user.id)
        await session.commit()
        text = menu_text(user, len(tasks))
        await message.answer(text, reply_markup=menu_keyboard(len(tasks)))
