import anvil.server
from ..CraftifyAuth import AuthError, craftify_require_user

KEY_COL = "openai_api_key"


def key_hint(key):
    text = (key or "").strip()
    if not text:
        return ""
    if len(text) <= 8:
        return "••••"
    return "%s…%s" % (text[:3], text[-4:])


def user_openai_key(user=None):
    """Server-only. Never send the raw key to the browser."""
    if user is None:
        user = craftify_require_user()
    try:
        return (user[KEY_COL] or "").strip()
    except Exception:
        return ""


def _write_key(user, value):
    try:
        user[KEY_COL] = value
        if hasattr(user, "update"):
            user.update()
    except Exception:
        raise AuthError("This app cannot store a personal API key yet.")


@anvil.server.callable
def craftify_ai_key_status():
    user = craftify_require_user()
    key = user_openai_key(user)
    return {"has_key": bool(key), "hint": key_hint(key)}


@anvil.server.callable
def craftify_ai_save_key(key):
    user = craftify_require_user()
    text = (key or "").strip()
    if not text:
        raise AuthError("Paste an API key first.")
    _write_key(user, text)
    return {"has_key": True, "hint": key_hint(text)}


@anvil.server.callable
def craftify_ai_clear_key():
    user = craftify_require_user()
    _write_key(user, "")
    return {"has_key": False, "hint": ""}
