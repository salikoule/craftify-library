from routing import router
# flake8: noqa: F401
"""Official Anvil URL routing for every Craftify app.

Use a startup module that calls ``launch()`` and a ``routes`` module that
defines Route subclasses. Do not swap pages with ``anvil.open_form``.
"""

from routing.router import (
    CACHE_FIRST,
    NETWORK_FIRST,
    NO_CACHE,
    STALE_WHILE_REVALIDATE,
    NotFound,
    Redirect,
    Route,
    RoutingContext,
    TemplateWithContainerRoute,
    add_event_handler,
    back,
    forward,
    get_routing_context,
    get_url,
    launch as router_launch,
    navigate as router_navigate,
    open_form as router_open_form,
    reload,
    remove_event_handler,
)


def __getattr__(name):
    if name == "NavLink":
        from routing.router.NavLink import NavLink
        return NavLink
    raise AttributeError(name)


def launch():
    router_launch()


def navigate(*args, **kwargs):
    return router_navigate(*args, **kwargs)


def open_form(form, **properties):
    return router_open_form(form, **properties)


class ShellRoute(TemplateWithContainerRoute):
    """Keep a chrome form open and load pages into its container."""

    template = None
    template_container = "content_panel"
    template_container_properties = {"full_width_row": True}


class AuthenticatedShellRoute(ShellRoute):
    """Shell page that sends signed-out visitors to ``login_path``."""

    login_path = "/login"

    def before_load(self, **loader_args):
        import anvil.users

        if anvil.users.get_user() is None:
            raise Redirect(path=self.login_path)
