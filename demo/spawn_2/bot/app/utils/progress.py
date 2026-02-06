from __future__ import annotations


def progress_bar(current: int, total: int, length: int = 10) -> str:
    if total <= 0:
        return "[" + "░" * length + "]"
    ratio = max(0.0, min(1.0, current / total))
    filled = int(round(ratio * length))
    return "[" + "█" * filled + "░" * (length - filled) + "]"


def percent(current: int, total: int) -> int:
    if total <= 0:
        return 0
    return int(round((current / total) * 100))
