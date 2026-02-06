from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .time import utc_now, to_local


def progress_bar(current: int, total: int, length: int = 10) -> str:
    if total <= 0:
        return "[" + "░" * length + "]"
    ratio = max(0.0, min(1.0, current / total))
    filled = int(round(ratio * length))
    return "[" + "█" * filled + "░" * (length - filled) + "]"


def format_dt(dt: datetime, tz_name: str) -> str:
    local = to_local(dt, tz_name)
    return local.strftime("%d.%m, %H:%M")


def human_delta_until(dt: datetime, tz_name: str) -> str:
    now_local = datetime.now(ZoneInfo(tz_name))
    local = to_local(dt, tz_name)
    delta = local - now_local
    if delta.total_seconds() <= 0:
        return "просрочено"
    return humanize_timedelta(delta)


def humanize_timedelta(delta: timedelta) -> str:
    seconds = int(delta.total_seconds())
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}д")
    if hours > 0:
        parts.append(f"{hours}ч")
    if minutes > 0 and days == 0:
        parts.append(f"{minutes}мин")
    if not parts:
        return "меньше минуты"
    return " ".join(parts)


def xp_to_next(level: int) -> int:
    return 100 * level


def is_overdue(deadline: datetime) -> bool:
    return deadline <= utc_now()
