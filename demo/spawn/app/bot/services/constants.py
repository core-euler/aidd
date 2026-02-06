from dataclasses import dataclass

from ..db.models import Difficulty


@dataclass(frozen=True)
class DifficultyConfig:
    xp: int
    damage: int
    label: str


DIFFICULTY_CONFIG = {
    Difficulty.easy: DifficultyConfig(xp=10, damage=5, label="Лёгкая"),
    Difficulty.medium: DifficultyConfig(xp=25, damage=15, label="Средняя"),
    Difficulty.hard: DifficultyConfig(xp=50, damage=30, label="Сложная"),
    Difficulty.epic: DifficultyConfig(xp=100, damage=50, label="Эпическая"),
}
