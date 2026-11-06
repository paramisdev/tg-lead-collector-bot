import re

_NON_DIGITS = re.compile(r"\D")
_RU_COUNTRY_CODE = "7"
_RU_NUMBER_LENGTH = 11


def normalize_phone(raw: str) -> str | None:
    """Return an E.164 phone number or None if the input is not a valid RU number."""
    digits = _NON_DIGITS.sub("", raw)

    if len(digits) == _RU_NUMBER_LENGTH and digits.startswith("8"):
        digits = _RU_COUNTRY_CODE + digits[1:]
    elif len(digits) == 10:
        digits = _RU_COUNTRY_CODE + digits

    if len(digits) != _RU_NUMBER_LENGTH or not digits.startswith(_RU_COUNTRY_CODE):
        return None

    return f"+{digits}"
