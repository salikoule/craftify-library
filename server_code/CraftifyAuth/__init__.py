import anvil.server
import anvil.users


class AuthError(Exception):
    pass


def _user_roles(user) -> set:
    if user is None:
        return set()
    roles = user.get("roles") or []
    return {str(r["name"]).lower() for r in roles if r.get("name")}


@anvil.server.callable
def craftify_user_has_role(role_name: str) -> bool:
    user = anvil.users.get_user()
    if user is None:
        return False
    roles = _user_roles(user)
    if "admin" in roles or "super admin" in roles:
        return True
    return role_name.lower() in roles


@anvil.server.callable
def craftify_require_role(role_name: str):
    if not craftify_user_has_role(role_name):
        raise AuthError(f"{role_name.title()} role required.")
