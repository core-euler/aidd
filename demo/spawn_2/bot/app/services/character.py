from __future__ import annotations

from dataclasses import dataclass
from app.constants import XP_BASE, HP_BASE, HP_PER_LEVEL
from app.models import User


@dataclass(frozen=True)
class LevelUpResult:
    levels_gained: int
    new_level: int
    new_xp: int
    new_max_hp: int


@dataclass(frozen=True)
class DamageResult:
    died: bool
    hp: int


def xp_for_next_level(level: int) -> int:
    return XP_BASE * level


def apply_xp(user: User, amount: int) -> LevelUpResult | None:
    if amount <= 0:
        return None

    user.xp += amount
    levels_gained = 0

    while user.xp >= xp_for_next_level(user.level):
        user.xp -= xp_for_next_level(user.level)
        user.level += 1
        levels_gained += 1
        user.max_hp += HP_PER_LEVEL
        user.hp = user.max_hp
        if user.level > user.max_level_reached:
            user.max_level_reached = user.level

    if levels_gained:
        return LevelUpResult(
            levels_gained=levels_gained,
            new_level=user.level,
            new_xp=user.xp,
            new_max_hp=user.max_hp,
        )
    return None


def apply_damage(user: User, amount: int) -> DamageResult:
    if amount <= 0:
        return DamageResult(died=False, hp=user.hp)

    user.hp -= amount
    if user.hp > 0:
        return DamageResult(died=False, hp=user.hp)

    user.level = 1
    user.xp = 0
    user.hp = HP_BASE
    user.max_hp = HP_BASE
    return DamageResult(died=True, hp=user.hp)
