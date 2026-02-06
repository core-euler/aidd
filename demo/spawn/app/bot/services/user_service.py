from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import User
from ..utils.formatting import xp_to_next


@dataclass
class LevelUpResult:
    leveled_up: bool
    new_level: int
    new_xp: int
    new_hp: int
    new_max_hp: int


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self._session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_or_create(self, telegram_id: int, username: str | None) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            return user

        user = User(
            telegram_id=telegram_id,
            username=username,
            level=1,
            xp=0,
            hp=100,
            max_hp=100,
            total_completed=0,
            total_failed=0,
            max_level_reached=1,
        )
        self._session.add(user)
        await self._session.flush()
        return user

    def apply_xp(self, user: User, xp_gain: int) -> LevelUpResult:
        level = user.level
        xp = user.xp + xp_gain
        max_hp = user.max_hp
        hp = user.hp
        leveled_up = False

        while xp >= xp_to_next(level):
            xp -= xp_to_next(level)
            level += 1
            max_hp += 10
            hp = max_hp
            leveled_up = True

        user.level = level
        user.xp = xp
        user.max_hp = max_hp
        user.hp = hp
        if level > user.max_level_reached:
            user.max_level_reached = level

        return LevelUpResult(
            leveled_up=leveled_up,
            new_level=level,
            new_xp=xp,
            new_hp=hp,
            new_max_hp=max_hp,
        )

    def apply_damage(self, user: User, damage: int) -> bool:
        user.hp -= damage
        if user.hp <= 0:
            user.hp = 0
            return True
        return False

    def reset_on_death(self, user: User) -> None:
        user.level = 1
        user.xp = 0
        user.hp = 100
        user.max_hp = 100
        user.max_level_reached = max(user.max_level_reached, 1)

    def record_completion(self, user: User) -> None:
        user.total_completed += 1
        if user.level > user.max_level_reached:
            user.max_level_reached = user.level

    def record_failure(self, user: User) -> None:
        user.total_failed += 1
