import json
import time

import anvil.server
from anvil.tables import app_tables
from ..CraftifyAuth import AuthError, craftify_require_user
from ..CraftifyAIUsage import record_from_usage, summarize

KEY_COL = "openai_api_key"
CHAT_URL = "https://api.openai.com/v1/chat/completions"
USAGE_TABLE = "ai_usage"
REPORT_DAYS = (7, 30, 90, 0)


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


def chat_completion(body, feature, key=None, timeout=25):
    """Send a chat completion with the user's key and log its usage. Raises what urllib raises."""
    import urllib.error
    import urllib.request

    user = _current_user()
    if key is None:
        key = user_openai_key(user) if user is not None else ""
    req = urllib.request.Request(
        CHAT_URL,
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer %s" % key, "Content-Type": "application/json"},
        method="POST",
    )
    model = body.get("model") or ""
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            request_id = resp.headers.get("x-request-id") or ""
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as err:
        _log(user, record_from_usage(feature, model, None, _ms(started), status="error",
                                     error="HTTP %s" % err.code, request_id=(err.headers or {}).get("x-request-id") or ""))
        raise
    except Exception as err:
        _log(user, record_from_usage(feature, model, None, _ms(started), status="error",
                                     error=type(err).__name__))
        raise
    _log(user, record_from_usage(feature, model or payload.get("model"), payload.get("usage"), _ms(started),
                                 request_id=request_id))
    return payload


def _ms(started):
    return (time.time() - started) * 1000


def _current_user():
    try:
        import anvil.users

        user = anvil.users.get_user()
    except Exception:
        return None
    return _user_row(user) if user is not None else None


def _usage_table():
    return getattr(app_tables, USAGE_TABLE, None)


def _log(user, record):
    """Store one call. Usage logging never breaks the AI feature itself."""
    table = _usage_table()
    if table is None or user is None:
        return
    try:
        table.add_row(user=user, **record)
    except Exception as err:
        print("AI usage not logged: %s" % err)


@anvil.server.callable
def craftify_ai_usage(days=30):
    """The signed-in user's AI usage report for the last ``days`` days (0 = all time)."""
    user = _user_row(craftify_require_user())
    table = _usage_table()
    if table is None:
        return {"ready": False, "days": days}
    days = days if days in REPORT_DAYS else 30
    fields = ("at", "feature", "model", "input_tokens", "cached_tokens", "output_tokens", "reasoning_tokens",
              "cost_usd", "latency_ms", "status", "error", "request_id")
    records = []
    for row in table.search(user=user):
        item = {}
        for name in fields:
            try:
                item[name] = row[name]
            except Exception:
                item[name] = None
        records.append(item)
    return summarize(records, days)
