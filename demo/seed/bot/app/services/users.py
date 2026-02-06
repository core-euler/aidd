from sqlalchemy.orm import Session
from ..models import User


def get_or_create_user(session: Session, telegram_id: int, username: str | None) -> tuple[User, bool]:
    user = session.query(User).filter(User.telegram_id == telegram_id).one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user, True

    if username and user.username != username:
        user.username = username
        session.commit()
    return user, False


def reset_user_progress(user: User) -> None:
    user.level = 1
    user.xp = 0
    user.hp = 100
    user.max_hp = 100
    user.max_level_reached = max(user.max_level_reached, 1)


def apply_damage(user: User, damage: int) -> bool:
    user.hp -= damage
    if user.hp <= 0:
        reset_user_progress(user)
        return True
    return False


def apply_xp(user: User, xp_gain: int) -> int:
    level_ups = 0
    user.xp += xp_gain
    while user.xp >= user.level * 100:
        user.xp -= user.level * 100
        user.level += 1
        user.max_hp += 10
        user.hp = user.max_hp
        level_ups += 1
        user.max_level_reached = max(user.max_level_reached, user.level)
    return level_ups


def user_success_rate(user: User) -> float:
    total = user.total_completed + user.total_failed
    if total == 0:
        return 0.0
    return (user.total_completed / total) * 100.0
