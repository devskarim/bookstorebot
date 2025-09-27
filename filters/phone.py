import re


def validate_phone(phone: str) -> bool:

    pattern = r"^\+?\d{9,15}$"
    return bool(re.match(pattern, phone))
