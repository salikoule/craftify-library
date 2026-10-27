import anvil.server
from anvil.tables import app_tables
from ..CraftifyAuth import AuthError, craftify_require_user

KEY_COL = "openai_api_key"


def key_hint(key):
    text = (key or "").strip()
    if not text:
        return ""
    if len(text) <= 8:
        return "••••"
    return "%s…%s" % (text[:3], text[-4:])


def _users_table():
    return getattr(app_tables, "users", None)


def _user_row(user):
    table = _users_table()
    if table is not None:
        try:
            row = table.get_by_id(user.get_id())
            if row is not None:
                return row
        except Exception:
            pass
        try:
            email = ((user["email"] or "") if user is not None else "").strip()
            if email:
                matches = list(table.search(email=email))
                if matches:
                    return matches[0]
        except Exception:
            pass
    return user


def user_openai_key(user=None):
    """Server-only. Never send the raw key to the browser."""
    if user is None:
        user = craftify_require_user()
    row = _user_row(user)
    try:
        return (row[KEY_COL] or "").strip()
    except Exception:
        return ""


def _write_key(user, value):
    row = _user_row(user)
    try:
        row[KEY_COL] = value
        return
    except Exception:
        pass
    try:
        row[KEY_COL] = value
        if hasattr(row, "update"):
            row.update()
        return
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
