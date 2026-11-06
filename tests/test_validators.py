import pytest

from bot.utils.validators import normalize_phone


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+7 999 123-45-67", "+79991234567"),
        ("8 (999) 123-45-67", "+79991234567"),
        ("9991234567", "+79991234567"),
        ("+79991234567", "+79991234567"),
        ("7 999 123 45 67", "+79991234567"),
    ],
)
def test_normalize_phone_valid(raw: str, expected: str) -> None:
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "123",
        "abc",
        "+1 202 555 0147",
        "799912345678",
    ],
)
def test_normalize_phone_invalid(raw: str) -> None:
    assert normalize_phone(raw) is None
