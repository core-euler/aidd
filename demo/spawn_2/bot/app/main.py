from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery

from app.config import load_settings
from app.db.base import Base
from app.db.session import create_engine, create_session_factory
from app.handlers import start as start_handlers
from app.handlers import menu as menu_handlers
from app.handlers import tasks as task_handlers
from app.handlers import fallback as fallback_handlers
from app.scheduler import start_scheduler
from app.runtime import set_runtime


async def on_startup(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    settings = load_settings()

    logging.basicConfig(level=settings.log_level)

    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    set_runtime(session_factory, settings.timezone)

    async def on_error(event, **kwargs):
        exception = kwargs.get("exception")
        update = kwargs.get("update") or kwargs.get("event") or event
        logging.exception("handler_error", exc_info=exception)

        message = None
        if isinstance(update, Message):
            message = update
        elif isinstance(update, CallbackQuery):
            message = update.message
            await update.answer()
        elif hasattr(update, "message"):
            message = update.message
        elif hasattr(update, "callback_query"):
            message = update.callback_query.message

        if message:
            await message.answer("Произошла ошибка. Попробуй ещё раз или вернись в меню.")
        return True

    dp.errors.register(on_error)

    dp.include_router(start_handlers.router)
    dp.include_router(menu_handlers.router)
    dp.include_router(task_handlers.router)
    dp.include_router(fallback_handlers.router)

    await on_startup(engine)
    start_scheduler(bot, session_factory, settings.timezone)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
