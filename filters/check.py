import re

def validate_name(name: str) -> bool:
  
    pattern = r"^[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ ]{2,30}$"
    return bool(re.match(pattern, name))
