from __future__ import annotations

from typing import Optional
from zoneinfo import ZoneInfo

_session_factory = None
_timezone: Optional[ZoneInfo] = None


def set_runtime(session_factory, timezone: ZoneInfo):
    global _session_factory, _timezone
    _session_factory = session_factory
    _timezone = timezone


def get_session_factory():
    if _session_factory is None:
        raise RuntimeError("Session factory is not initialized")
    return _session_factory


def get_timezone() -> ZoneInfo:
    if _timezone is None:
        raise RuntimeError("Timezone is not initialized")
    return _timezone
