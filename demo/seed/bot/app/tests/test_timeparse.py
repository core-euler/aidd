from zoneinfo import ZoneInfo
from datetime import datetime
from app.utils.timeparse import parse_deadline, quick_deadline


def test_parse_relative_hours():
    tz = ZoneInfo("Europe/Moscow")
    start = datetime.now(tz)
    deadline = parse_deadline("через 2 часа", tz)
    assert (deadline - start).total_seconds() >= 2 * 3600 - 5


def test_quick_deadline_today_evening():
    tz = ZoneInfo("Europe/Moscow")
    deadline = quick_deadline("today_evening", tz)
    assert deadline.tzinfo is not None
