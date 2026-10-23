import anvil
from anvil.js.window import jQuery as _S


def maintain_scroll_position():
    """Decorator: preserve .content or .nav-holder scroll across UI refresh."""

    def wrap(func):
        def wrapped_func(*args, **kwargs):
            scroll_pos, selector = get_scroll_position()
            res = func(*args, **kwargs)
            set_scroll_position(selector, scroll_pos)
            return res

        return wrapped_func

    return wrap


def get_scroll_position():
    selector = ".nav-holder" if _S(".nav-holder").css("display") == "block" else ".content"
    scroll_pos = anvil.get_open_form().call_js("getScrollPosition", selector)
    return scroll_pos, selector


def set_scroll_position(selector, scroll_position):
    anvil.get_open_form().call_js("restoreScrollPosition", selector, scroll_position)
