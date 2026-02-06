from datetime import datetime
from zoneinfo import ZoneInfo

from app.utils.time_utils import parse_deadline


def test_parse_relative_hours():
    tz = ZoneInfo("Europe/Moscow")
    now = datetime(2025, 1, 1, 12, 0, tzinfo=tz)
    result = parse_deadline("через 2 часа", now, tz)
    assert result.error is None
    assert result.value.hour == 14


def test_parse_tomorrow():
    tz = ZoneInfo("Europe/Moscow")
    now = datetime(2025, 1, 1, 12, 0, tzinfo=tz)
    result = parse_deadline("завтра 18:00", now, tz)
    assert result.error is None
    assert result.value.day == 2
    assert result.value.hour == 18


def test_parse_full_date():
    tz = ZoneInfo("Europe/Moscow")
    now = datetime(2025, 1, 1, 12, 0, tzinfo=tz)
    result = parse_deadline("25.01.2025 15:30", now, tz)
    assert result.error is None
    assert result.value.year == 2025
    assert result.value.day == 25
