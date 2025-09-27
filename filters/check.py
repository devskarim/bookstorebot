import re

COMMON_NAMES = {
    "Ali", "Ahmad", "Muhammad", "Javohir", "Dilnoza", "Lola", "Sanjar",
    "Sardor", "Bek", "Oybek", "Gulnora", "Feruza", "Umida", "Aziz"
}

VOWELS = set("aeiouyAEIOUY" + "аеёиоуыэюяАЕËИОУЫЭЮЯ" + "ўЎoO")

BASIC_PATTERN = r"^[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ'‘ʼ` \-]{2,30}$"

def validate_name(name: str) -> bool:
    if not name or not isinstance(name, str):
        return False

    name = name.strip()
    if not re.match(BASIC_PATTERN, name):
        return False

    normalized = " ".join(w.capitalize() for w in name.split())
    if normalized in COMMON_NAMES:
        return True

    if not any(ch in VOWELS for ch in name):
        return False

    compact = re.sub(r"[ '\-`‘ʼ]", "", name)
    if len(compact) < 2:
        return False

    if re.search(r"[^aeiouyAEIOUYаеёиоуыэюяАЕЁИОУЫЭЮЯўЎ]{3,}", compact):
        return False

    if re.search(r"(.)\1{3,}", compact):
        return False

    return True


