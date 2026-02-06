import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .config import load_config
from .db.session import Database
from .handlers.router import router
from .scheduler.runner import Scheduler


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("/app/logs/bot.log"),
        ],
    )


async def main() -> None:
    config = load_config()
    setup_logging(config.log_level)

    db = Database(config.database_url)
    await db.create_all()

    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    dp.workflow_data.update(db=db, config=config)

    scheduler = Scheduler(bot, db, config)
    scheduler.start()

    try:
        await dp.start_polling(bot)
    finally:
        await scheduler.stop()
        await db.dispose()


if __name__ == "__main__":
    asyncio.run(main())
