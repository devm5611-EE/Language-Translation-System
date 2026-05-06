import re


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_password(password: str):
    """Returns (is_valid: bool, error: str)"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    return True, ""


def validate_text_length(text: str, max_len: int = 5000):
    if not text or not text.strip():
        return False, "Text cannot be empty."
    if len(text) > max_len:
        return False, f"Text exceeds {max_len} characters."
    return True, ""


def validate_name(name: str):
    name = name.strip()
    if len(name) < 2:
        return False, "Name must be at least 2 characters."
    if len(name) > 100:
        return False, "Name must be under 100 characters."
    return True, ""


def sanitize_text(text: str) -> str:
    return text.strip().replace("\r\n", "\n").replace("\r", "\n")
