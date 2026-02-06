from __future__ import annotations

from dataclasses import dataclass
from app.models import User


@dataclass(frozen=True)
class Stats:
    completed: int
    failed: int
    success_rate: int
    max_level: int


def build_stats(user: User) -> Stats:
    completed = user.total_completed
    failed = user.total_failed
    total = completed + failed
    success_rate = int(round((completed / total) * 100)) if total else 0
    return Stats(
        completed=completed,
        failed=failed,
        success_rate=success_rate,
        max_level=user.max_level_reached,
    )
