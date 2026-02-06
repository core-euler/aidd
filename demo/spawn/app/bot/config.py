from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Config:
    bot_token: str
    database_url: str
    timezone: str
    log_level: str


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN")
    database_url = os.getenv("DATABASE_URL")
    timezone = os.getenv("TIMEZONE", "Europe/Moscow")
    log_level = os.getenv("LOG_LEVEL", "INFO")

    if not bot_token:
        raise RuntimeError("BOT_TOKEN is required")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    return Config(
        bot_token=bot_token,
        database_url=database_url,
        timezone=timezone,
        log_level=log_level,
    )
