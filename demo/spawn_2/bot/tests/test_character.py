from app.services.character import apply_xp, apply_damage, xp_for_next_level
from app.models import User


def test_level_up_single():
    user = User(telegram_id=1)
    user.level = 1
    user.xp = 90
    user.hp = 100
    user.max_hp = 100

    result = apply_xp(user, 15)
    assert result is not None
    assert user.level == 2
    assert user.xp == 5
    assert user.max_hp == 110
    assert user.hp == 110


def test_level_up_multiple():
    user = User(telegram_id=1)
    user.level = 1
    user.xp = 0
    user.hp = 100
    user.max_hp = 100

    result = apply_xp(user, 350)
    assert result is not None
    assert user.level == 3
    assert user.xp == 50
    assert user.max_hp == 120


def test_damage_death():
    user = User(telegram_id=1)
    user.level = 3
    user.xp = 40
    user.hp = 20
    user.max_hp = 120

    result = apply_damage(user, 50)
    assert result.died is True
    assert user.level == 1
    assert user.xp == 0
    assert user.hp == 100
    assert user.max_hp == 100
