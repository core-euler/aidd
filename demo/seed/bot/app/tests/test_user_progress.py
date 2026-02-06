from app.services.users import apply_xp
from app.models import User


def test_apply_xp_single_level():
    user = User(level=1, xp=0, hp=100, max_hp=100, max_level_reached=1)
    level_ups = apply_xp(user, 100)
    assert level_ups == 1
    assert user.level == 2
    assert user.xp == 0
    assert user.max_hp == 110
    assert user.hp == 110


def test_apply_xp_multiple_levels():
    user = User(level=1, xp=0, hp=100, max_hp=100, max_level_reached=1)
    level_ups = apply_xp(user, 350)
    assert level_ups == 2
    assert user.level == 3
    assert user.xp == 50
    assert user.max_hp == 120
    assert user.hp == 120
