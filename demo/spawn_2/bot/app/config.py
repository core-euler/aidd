from dataclasses import dataclass
import os
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str
    timezone: ZoneInfo
    log_level: str


def load_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    database_url = os.getenv("DATABASE_URL", "").strip()
    tz_name = os.getenv("TIMEZONE", "Europe/Moscow").strip()
    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    if not bot_token:
        raise RuntimeError("BOT_TOKEN is required")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")

    return Settings(
        bot_token=bot_token,
        database_url=database_url,
        timezone=tz,
        log_level=log_level,
    )
