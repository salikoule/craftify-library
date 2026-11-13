"""Device-local display name (shared by settings and account menu)."""

from anvil.js import window

NAME_KEY = "craftify-display-name"


def read():
    try:
        value = window.localStorage.getItem(NAME_KEY)
        return (value or "").strip()
    except Exception:
        return ""


def write(value):
    try:
        window.localStorage.setItem(NAME_KEY, (value or "").strip())
    except Exception:
        pass


def chip_label(email):
    name = read()
    if name:
        return name
    return (email or "").strip()


def initials(email):
    name = read()
    text = name or (email or "").strip()
    return text[:1].upper() if text else "?"
