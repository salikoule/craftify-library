from ._anvil_designer import AccountMenuTemplate
from routing import router
from anvil.js import get_dom_node
from anvil.js.window import setTimeout
import anvil.users


def _initials(email):
    text = (email or "").strip()
    return text[:1].upper() if text else "?"


def _closest(node, selector):
    if node is None:
        return None
    if getattr(node, "nodeType", None) == 3:
        node = getattr(node, "parentElement", None)
    if node is None or not hasattr(node, "closest"):
        return None
    return node.closest(selector)


class AccountMenu(AccountMenuTemplate):
    def __init__(self, **properties):
        self._email = properties.pop("email", "") or ""
        self._show_profile = bool(properties.pop("show_profile", True))
        self._show_logout = bool(properties.pop("show_logout", True))
        self._bound = False
        self._open = False
        self._root_el = None
        self.init_components(**properties)
        self._bind()
        self._render()

    def form_show(self, **event_args):
        self._bind()
        self._render()

    def _node(self, name):
        nodes = getattr(self, "dom_nodes", None)
        if not nodes:
            return None
        try:
            return nodes[name]
        except Exception:
            return None

    def _host(self):
        try:
            return get_dom_node(self)
        except Exception:
            return None

    def _root(self):
        if self._root_el is not None:
            return self._root_el
        node = self._node("am_root")
        if node is not None:
            return node
        host = self._host()
        if host is None:
            return None
        if hasattr(host, "querySelector"):
            found = host.querySelector(".am-wrap")
            if found is not None:
                return found
        return None

    def _bind(self):
        if self._bound:
            return
        root = self._root()
        if root is None:
            setTimeout(self._bind, 50)
            return
        self._root_el = root
        root.addEventListener("click", self._on_root)
        self._bound = True
        setTimeout(self._listen_document, 0)

    def _listen_document(self):
        root = self._root()
        if root is None:
            return
        root.ownerDocument.addEventListener("click", self._close_if_outside)

    def _render(self):
        email_node = self._node("am_email")
        initials_node = self._node("am_initials")
        host = self._host()
        if email_node is None and host is not None and hasattr(host, "querySelector"):
            email_node = host.querySelector(".am-email")
            initials_node = host.querySelector(".am-ava")
        if email_node is not None:
            email_node.textContent = self._email
            email_node.title = self._email
        if initials_node is not None:
            initials_node.textContent = _initials(self._email)
        profile = self._node("am_profile_item")
        logout = self._node("am_logout_item")
        if profile is not None:
            profile.classList.toggle("am-off", not self._show_profile)
        if logout is not None:
            logout.classList.toggle("am-off", not self._show_logout)
        if not self._bound:
            self._bind()

    def _set_open(self, open_):
        self._open = bool(open_)
        root = self._root()
        menu = self._node("am_menu")
        if menu is None and root is not None and hasattr(root, "querySelector"):
            menu = root.querySelector(".am-menu")
        if root is not None:
            root.classList.toggle("am-open", self._open)
        if menu is not None:
            menu.classList.toggle("am-off", not self._open)

    def _on_root(self, event):
        action_btn = _closest(getattr(event, "target", None), "[data-action]")
        if action_btn is None:
            return
        event.stopPropagation()
        self._set_open(False)
        action = action_btn.getAttribute("data-action")
        if action == "profile":
            self.raise_event("profile_click")
        elif action == "reload":
            self.raise_event("reload_click")
            try:
                from anvil.js import window
                window.location.reload()
            except Exception:
                pass
        elif action == "logout":
            self.raise_event("logout_click")
            try:
                anvil.users.logout()
            except Exception:
                pass

    def _close_if_outside(self, event):
        if not self._open:
            return
        root = self._root()
        target = getattr(event, "target", None)
        if root is None or target is None:
            return
        try:
            if root.contains(target):
                return
        except Exception:
            pass
        self._set_open(False)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value or ""
        self._render()
