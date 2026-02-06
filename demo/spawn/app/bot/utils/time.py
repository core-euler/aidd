from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import dateparser


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_local(dt: datetime, tz_name: str) -> datetime:
    tz = ZoneInfo(tz_name)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return dt.astimezone(timezone.utc)


def parse_human_datetime(value: str, tz_name: str) -> datetime | None:
    tz = ZoneInfo(tz_name)
    settings = {
        "TIMEZONE": tz_name,
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future",
        "RELATIVE_BASE": datetime.now(tz),
        "DATE_ORDER": "DMY",
    }
    parsed = dateparser.parse(value, settings=settings, languages=["ru"])
    if not parsed:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)
    return parsed


def quick_deadline(option: str, tz_name: str) -> datetime:
    tz = ZoneInfo(tz_name)
    now_local = datetime.now(tz)

    if option == "1h":
        return now_local + timedelta(hours=1)
    if option == "3h":
        return now_local + timedelta(hours=3)
    if option == "today_evening":
        target = now_local.replace(hour=21, minute=0, second=0, microsecond=0)
        if target <= now_local:
            target = target + timedelta(days=1)
        return target
    if option == "tomorrow_morning":
        target = (now_local + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        return target
    if option == "tomorrow_evening":
        target = (now_local + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
        return target

    raise ValueError("Unknown quick deadline option")
