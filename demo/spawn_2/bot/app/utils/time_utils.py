from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import re
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class ParseResult:
    value: datetime | None
    error: str | None


RELATIVE_RE = re.compile(r"^через\s+(\d+)\s+(час|часа|часов|день|дня|дней)$", re.IGNORECASE)
DATE_RE_SHORT = re.compile(r"^(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})$")
DATE_RE_FULL = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2})$")
TOMORROW_RE = re.compile(r"^завтра\s+(\d{2}):(\d{2})$", re.IGNORECASE)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def ensure_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def to_utc(local_dt: datetime, tz: ZoneInfo) -> datetime:
    if local_dt.tzinfo is None:
        local_dt = local_dt.replace(tzinfo=tz)
    return local_dt.astimezone(timezone.utc)


def from_utc(utc_dt: datetime, tz: ZoneInfo) -> datetime:
    utc_dt = ensure_aware(utc_dt)
    return utc_dt.astimezone(tz)


def format_deadline_local(utc_dt: datetime, tz: ZoneInfo) -> str:
    local_dt = from_utc(utc_dt, tz)
    fmt = "%d.%m, %H:%M" if local_dt.year == datetime.now(tz).year else "%d.%m.%Y, %H:%M"
    return local_dt.strftime(fmt)


def format_remaining(utc_dt: datetime, tz: ZoneInfo) -> str:
    local_dt = from_utc(utc_dt, tz)
    now_local = datetime.now(tz)
    delta = local_dt - now_local
    if delta.total_seconds() <= 0:
        return "0мин"
    total_minutes = int(delta.total_seconds() // 60)
    days, rem_minutes = divmod(total_minutes, 1440)
    hours, minutes = divmod(rem_minutes, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days}д")
    if hours:
        parts.append(f"{hours}ч")
    if minutes or not parts:
        parts.append(f"{minutes}мин")
    return " ".join(parts)


def parse_deadline(text: str, now_local: datetime, tz: ZoneInfo) -> ParseResult:
    raw = text.strip().lower()
    if not raw:
        return ParseResult(None, "Пустой ввод даты")

    match = RELATIVE_RE.match(raw)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if unit.startswith("час"):
            return ParseResult(now_local + timedelta(hours=value), None)
        return ParseResult(now_local + timedelta(days=value), None)

    match = TOMORROW_RE.match(raw)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        date = (now_local + timedelta(days=1)).date()
        return ParseResult(datetime(date.year, date.month, date.day, hour, minute, tzinfo=tz), None)

    match = DATE_RE_FULL.match(raw)
    if match:
        day, month, year, hour, minute = map(int, match.groups())
        try:
            return ParseResult(datetime(year, month, day, hour, minute, tzinfo=tz), None)
        except ValueError:
            return ParseResult(None, "Некорректная дата")

    match = DATE_RE_SHORT.match(raw)
    if match:
        day, month, hour, minute = map(int, match.groups())
        year = now_local.year
        try:
            return ParseResult(datetime(year, month, day, hour, minute, tzinfo=tz), None)
        except ValueError:
            return ParseResult(None, "Некорректная дата")

    return ParseResult(None, "Неверный формат даты")
