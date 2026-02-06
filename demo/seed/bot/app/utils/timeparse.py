from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


RELATIVE_RE = re.compile(r"^через\s+(\d+)\s+(час|часа|часов|день|дня|дней)$", re.IGNORECASE)
DATE_RE = re.compile(r"^(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?\s+(\d{1,2}):(\d{2})$")
TOMORROW_RE = re.compile(r"^завтра\s+(\d{1,2}):(\d{2})$", re.IGNORECASE)


class DeadlineParseError(ValueError):
    pass


def parse_deadline(text: str, tz: ZoneInfo) -> datetime:
    raw = text.strip().lower()

    match = RELATIVE_RE.match(raw)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        now = datetime.now(tz)
        if "час" in unit:
            return now + timedelta(hours=amount)
        return now + timedelta(days=amount)

    match = TOMORROW_RE.match(raw)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        now = datetime.now(tz)
        target = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        return target

    match = DATE_RE.match(raw)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3)) if match.group(3) else datetime.now(tz).year
        hour = int(match.group(4))
        minute = int(match.group(5))
        return datetime(year, month, day, hour, minute, tzinfo=tz)

    raise DeadlineParseError(
        "Некорректный формат даты. Примеры: 'завтра 18:00', '25.01 15:30', '25.01.2025 15:30', 'через 2 часа'"
    )


def quick_deadline(key: str, tz: ZoneInfo) -> datetime:
    now = datetime.now(tz)
    if key == "1h":
        return now + timedelta(hours=1)
    if key == "3h":
        return now + timedelta(hours=3)
    if key == "today_evening":
        target = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if target <= now:
            target = target + timedelta(days=1)
        return target
    if key == "tomorrow_morning":
        return (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    if key == "tomorrow_evening":
        return (now + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
    raise DeadlineParseError("Неизвестный быстрый дедлайн")
