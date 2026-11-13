"""Per-user profile photo on the app ``users`` table (optional ``profile_photo`` media column)."""

import anvil.server
from anvil.tables import app_tables

from ..CraftifyAuth import AuthError, craftify_require_user

PHOTO_COL = "profile_photo"
MAX_BYTES = 2 * 1024 * 1024
ALLOWED = ("image/jpeg", "image/png", "image/webp")


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


def _read_photo(row):
    try:
        return row[PHOTO_COL]
    except Exception:
        return None


def _photo_ok(media):
    if media is None:
        return False
    content_type = (getattr(media, "content_type", None) or "").split(";")[0].strip().lower()
    if content_type and content_type not in ALLOWED:
        raise AuthError("Use a JPEG, PNG, or WebP image.")
    try:
        size = len(media.get_bytes())
    except Exception:
        size = 0
    if size <= 0:
        raise AuthError("That file could not be read.")
    if size > MAX_BYTES:
        raise AuthError("Use an image up to 2 MB.")
    return True


def _write_photo(row, media):
    try:
        row[PHOTO_COL] = media
        return
    except Exception:
        pass
    try:
        if hasattr(row, "update"):
            row.update(**{PHOTO_COL: media})
            return
    except Exception:
        pass
    raise AuthError("This app cannot store a profile photo yet. Add a media column named profile_photo on Users.")


@anvil.server.callable
def craftify_profile_photo_get():
    user = craftify_require_user()
    row = _user_row(user)
    return _read_photo(row)


@anvil.server.callable
def craftify_profile_photo_save(media):
    user = craftify_require_user()
    if media is None:
        raise AuthError("Choose an image first.")
    _photo_ok(media)
    row = _user_row(user)
    _write_photo(row, media)
    return _read_photo(row)


@anvil.server.callable
def craftify_profile_photo_clear():
    user = craftify_require_user()
    row = _user_row(user)
    _write_photo(row, None)
    return None
