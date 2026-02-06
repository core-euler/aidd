from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str
    timezone: str
    log_level: str


def load_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://bot:bot@db:5432/bot"
    ).strip()
    timezone = os.getenv("TIMEZONE", "Europe/Moscow").strip()
    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is required")
    return Settings(
        bot_token=bot_token,
        database_url=database_url,
        timezone=timezone,
        log_level=log_level,
    )
