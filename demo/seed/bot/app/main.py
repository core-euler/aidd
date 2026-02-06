import asyncio
import logging
from zoneinfo import ZoneInfo
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramNetworkError

from .config import load_settings
from .db import create_engine_and_session, init_db
from .handlers import router
from .utils.scheduler import check_deadlines


async def scheduler_loop(bot: Bot, session_factory, tz: ZoneInfo) -> None:
    while True:
        try:
            with session_factory() as session:
                await check_deadlines(bot, session, tz)
        except Exception:
            logging.exception("Scheduler loop error")
        await asyncio.sleep(300)


def main() -> None:
    settings = load_settings()
    logging.basicConfig(level=settings.log_level)

    engine, session_factory = create_engine_and_session(settings.database_url)
    init_db(engine)

    tz = ZoneInfo(settings.timezone)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp["session_factory"] = session_factory
    dp["timezone"] = tz

    dp.include_router(router)

    async def on_startup() -> None:
        dp["scheduler_task"] = asyncio.create_task(scheduler_loop(bot, session_factory, tz))

    async def on_shutdown() -> None:
        task = dp.get("scheduler_task")
        if task:
            task.cancel()
        await bot.session.close()

    @dp.errors()
    async def on_error(event, **kwargs):
        exception = kwargs.get("exception")
        logging.exception("Unhandled exception in update handler", exc_info=exception)
        if isinstance(exception, TelegramNetworkError):
            return True
        return True

    async def run() -> None:
        await on_startup()
        try:
            await dp.start_polling(bot)
        finally:
            await on_shutdown()

    asyncio.run(run())


if __name__ == "__main__":
    main()
