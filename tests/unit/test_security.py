import pytest

from app.security import (
    check_requirements_for_password,
    get_password_hash,
    verify_password,
)


@pytest.mark.parametrize(
    ("password", "is_valid"),
    [
        ("abc1!", False),
        ("abcdef!", False),
        ("abcdef1", False),
        ("secure1!", True),
        ("A-longer-password9$", True),
    ],
)
def test_password_requirements(password: str, is_valid: bool):
    assert check_requirements_for_password(password) is is_valid


def test_password_hash_verifies_only_the_original_password():
    encoded = get_password_hash("secure1!")

    assert encoded != "secure1!"
    assert verify_password("secure1!", encoded)
    assert not verify_password("different1!", encoded)
