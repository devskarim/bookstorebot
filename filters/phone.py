import re
from typing import Tuple, Optional

UZ_PREFIXES = {
    "20","33","50","55","70","77","87","88",
    "90","91","93","94","95","97","98","99"
}

def validate_uz_phone(raw: str) -> Tuple[bool, Optional[str]]:
    """
    Qabul qiladi:
      - +998XXXXXXXXX
      - 998XXXXXXXXX
      - 0XXXXXXXXX
      - XXXXXXXXX   (9 raqam)
      - XXXXXXXXXX  (10 raqam) -> birinchi raqam olib tashlanadi va oxirgi 9 ta tekshiriladi
    Agar to'g'ri -> (True, '+998XXXXXXXXX') aks holda (False, None)
    """
    if not isinstance(raw, str):
        return False, None

    s = raw.strip()
    if not re.match(r'^[\d+\-\s()]+$', s):
        return False, None

    s = re.sub(r'[()\s\-]', '', s)

    m = re.match(r'^\+?998(\d{9})$', s)
    if m:
        national = m.group(1)
    else:
        m2 = re.match(r'^0(\d{9})$', s)
        if m2:
            national = m2.group(1)
        else:
            m3 = re.match(r'^(\d{9})$', s)
            if m3:
                national = m3.group(1)
            else:
                m4 = re.match(r'^(\d{10})$', s)
                if m4:
                    candidate = m4.group(1)[1:]  
                    prefix = candidate[:2]
                    if prefix in UZ_PREFIXES:
                        national = candidate
                    else:
                        return False, None
                else:
                    return False, None

    prefix = national[:2]
    if prefix not in UZ_PREFIXES:
        return False, None

    normalized = f'+998{national}'
    return True, normalized
