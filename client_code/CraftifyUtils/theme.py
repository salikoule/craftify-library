from anvil.js import window

THEME_KEY = "craftify-theme"
_listening = False


def _storage_get(key, default=""):
    try:
        value = window.localStorage.getItem(key)
        return default if value is None else value
    except Exception:
        return default


def _storage_set(key, value):
    try:
        window.localStorage.setItem(key, value)
    except Exception:
        pass


def current_theme():
    stored = _storage_get(THEME_KEY, "light")
    return stored if stored in ("light", "dark", "system") else "light"


def resolved_theme(theme=None):
    value = theme or current_theme()
    if value == "system":
        try:
            if window.matchMedia("(prefers-color-scheme: dark)").matches:
                return "dark"
        except Exception:
            pass
        return "light"
    return "dark" if value == "dark" else "light"


def apply_theme(theme=None):
    stored = theme or current_theme()
    if stored not in ("light", "dark", "system"):
        stored = "light"
    _storage_set(THEME_KEY, stored)
    value = resolved_theme(stored)
    dark = value == "dark"
    try:
        root = window.document.documentElement
        root.classList.toggle("ipac-dark", dark)
        root.classList.toggle("craftify-theme-dark", dark)
        root.setAttribute("data-theme", value)
        root.style.colorScheme = value
    except Exception:
        pass
    return stored


def listen_for_system_theme():
    global _listening
    if _listening:
        return
    try:
        media = window.matchMedia("(prefers-color-scheme: dark)")
    except Exception:
        return

    def _on_change(event=None):
        if current_theme() == "system":
            apply_theme("system")

    try:
        media.addEventListener("change", _on_change)
    except Exception:
        try:
            media.addListener(_on_change)
        except Exception:
            return
    _listening = True
