"""Craftify side drawer: a panel that slides in from the right over the page.

    handle = drawer.open(content, host=self, title="Week 3", footer=(save_button,))
    handle.close()

The drawer is added to ``host`` (default: the open form) so its components stay
in the Anvil tree, and its root element moves to ``document.body`` to sit over
everything. Styles are injected at runtime, like the dialogs.
"""

import anvil
from anvil.js import get_dom_node

from . import dialogs

_STYLE_ID = "craftify-drawer"

_HTML = """
<div anvil-name="root" class="cf-drawer" aria-hidden="true">
  <div anvil-name="backdrop" class="cf-drawer-backdrop"></div>
  <aside anvil-name="panel" class="cf-drawer-panel" role="dialog" aria-modal="true" tabindex="-1">
    <header class="cf-drawer-head">
      <div class="cf-drawer-heading">
        <p anvil-name="eyebrow" class="cf-drawer-eyebrow"></p>
        <h2 anvil-name="title" class="cf-drawer-title"></h2>
        <p anvil-name="subtitle" class="cf-drawer-subtitle"></p>
      </div>
      <button anvil-name="close" type="button" class="cf-drawer-close" aria-label="Close">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      </button>
    </header>
    <div anvil-slot="body" class="cf-drawer-body"></div>
    <footer anvil-name="footer" class="cf-drawer-foot"><div anvil-slot="footer" class="cf-drawer-actions"></div></footer>
  </aside>
</div>
"""

_CSS = """
.cf-drawer {
  --cfw-panel: #ffffff;
  --cfw-ink: #0f172a;
  --cfw-title: #1e3a5f;
  --cfw-muted: #64748b;
  --cfw-line: #e2e8f0;
  --cfw-soft: #f1f5f9;
  position: fixed;
  inset: 0;
  z-index: 1035;
  pointer-events: none;
  font-family: Montserrat, system-ui, sans-serif;
}
html.craftify-theme-dark .cf-drawer,
html.ipac-dark .cf-drawer,
html[data-theme="dark"] .cf-drawer {
  --cfw-panel: #151e2e;
  --cfw-ink: #e7eef7;
  --cfw-title: #e7eef7;
  --cfw-muted: #94a3b8;
  --cfw-line: #2a3a52;
  --cfw-soft: #1a2740;
}
.cf-drawer.is-open { pointer-events: auto; }
.cf-drawer-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.42);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
  opacity: 0;
  transition: opacity 200ms ease;
}
.cf-drawer.is-open .cf-drawer-backdrop { opacity: 1; }
.cf-drawer-panel {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: min(var(--cfw-width, 480px), 100vw);
  display: flex;
  flex-direction: column;
  background: var(--cfw-panel);
  color: var(--cfw-ink);
  border-left: 1px solid var(--cfw-line);
  box-shadow: -24px 0 60px rgba(15, 23, 42, 0.18);
  transform: translateX(100%);
  transition: transform 240ms cubic-bezier(0.2, 0.8, 0.2, 1);
  outline: none;
}
.cf-drawer.is-open .cf-drawer-panel { transform: none; }
.cf-drawer-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 22px 24px 16px;
  border-bottom: 1px solid var(--cfw-line);
}
.cf-drawer-eyebrow {
  margin: 0 0 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--cfw-muted);
}
.cf-drawer-title {
  margin: 0;
  font-size: 19px;
  font-weight: 700;
  line-height: 1.3;
  color: var(--cfw-title);
}
.cf-drawer-subtitle {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--cfw-muted);
}
.cf-drawer-eyebrow:empty, .cf-drawer-subtitle:empty { display: none; }
.cf-drawer-close {
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid var(--cfw-line);
  border-radius: 10px;
  background: var(--cfw-panel);
  color: var(--cfw-muted);
  cursor: pointer;
  transition: background 120ms ease, color 120ms ease;
}
.cf-drawer-close:hover { background: var(--cfw-soft); color: var(--cfw-title); }
.cf-drawer-close:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.18); }
.cf-drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px 24px;
  overscroll-behavior: contain;
}
.cf-drawer-foot {
  padding: 14px 24px 18px;
  border-top: 1px solid var(--cfw-line);
  background: var(--cfw-panel);
}
.cf-drawer-foot.is-empty { display: none; }
.cf-drawer-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.cf-drawer-actions > * { margin: 0 !important; }
html.cf-drawer-lock, html.cf-drawer-lock body { overflow: hidden; }
@media (max-width: 640px) {
  .cf-drawer-panel { width: 100vw; border-left: 0; }
  .cf-drawer-head { padding: 18px 18px 14px; }
  .cf-drawer-body { padding: 16px 18px 20px; }
  .cf-drawer-foot { padding: 12px 18px 16px; }
  .cf-drawer-actions > * { flex: 1; }
}
@media (prefers-reduced-motion: reduce) {
  .cf-drawer-panel, .cf-drawer-backdrop { transition: none; }
}
"""

_CLOSE_MS = 240


def install():
    """Add the drawer styles to the page once."""
    try:
        from anvil.js.window import document
    except Exception:
        return
    if document.getElementById(_STYLE_ID):
        return
    style = document.createElement("style")
    style.id = _STYLE_ID
    style.textContent = _CSS
    document.head.appendChild(style)


class Drawer:
    """One open drawer. Use ``open()`` to create it."""

    def __init__(self, content, host=None, title="", subtitle="", eyebrow="", footer=(), width=480,
                 on_close=None, confirm_close=None):
        install()
        self._on_close = on_close
        self._confirm_close = confirm_close
        self._open = False
        self._footer = []
        self.template = anvil.HtmlTemplate(html=_HTML)
        nodes = self.template.dom_nodes
        self._root = nodes["root"]
        self._panel = nodes["panel"]
        self._root.style.setProperty("--cfw-width", "%spx" % int(width))
        self.set_title(title, subtitle, eyebrow)
        self.template.add_component(content, slot="body")
        self.set_footer(footer)
        nodes["close"].addEventListener("click", self._close_click)
        nodes["backdrop"].addEventListener("click", self._close_click)
        self._panel.addEventListener("keydown", self._on_key)
        self._host = host or anvil.get_open_form()
        self._host.add_component(self.template)
        host_node = get_dom_node(self.template)
        host_node.style.display = "contents"

    def set_title(self, title="", subtitle="", eyebrow=""):
        nodes = self.template.dom_nodes
        nodes["title"].textContent = title or ""
        nodes["subtitle"].textContent = subtitle or ""
        nodes["eyebrow"].textContent = eyebrow or ""

    def set_footer(self, components=()):
        for component in self._footer:
            component.remove_from_parent()
        self._footer = list(components or ())
        for component in self._footer:
            self.template.add_component(component, slot="footer")
        self.template.dom_nodes["footer"].classList.toggle("is-empty", not self._footer)

    @property
    def is_open(self):
        return self._open

    def show(self):
        from anvil.js.window import document, requestAnimationFrame

        document.body.appendChild(self._root)
        document.documentElement.classList.add("cf-drawer-lock")
        self._root.setAttribute("aria-hidden", "false")
        self._open = True

        def reveal(*args):
            self._root.classList.add("is-open")
            self._focus_first()

        requestAnimationFrame(lambda *a: requestAnimationFrame(reveal))
        return self

    def _focus_first(self):
        target = self._panel.querySelector(
            ".cf-drawer-body input:not([type=hidden]), .cf-drawer-body textarea, .cf-drawer-body select")
        try:
            (target or self._panel).focus()
        except Exception:
            pass

    def close(self, force=True):
        """Close the drawer. With ``force=False`` the ``confirm_close`` check runs first."""
        if not self._open:
            return True
        if not force and self._confirm_close is not None and not self._confirm_close():
            return False
        self._open = False
        self._root.classList.remove("is-open")
        self._root.setAttribute("aria-hidden", "true")
        from anvil.js.window import document, setTimeout

        if not document.querySelector(".cf-drawer.is-open"):
            document.documentElement.classList.remove("cf-drawer-lock")
        setTimeout(self._dispose, _CLOSE_MS)
        if self._on_close is not None:
            self._on_close()
        return True

    def _dispose(self, *args):
        try:
            self._root.remove()
        except Exception:
            pass
        try:
            self.template.remove_from_parent()
        except Exception:
            pass

    def _close_click(self, event=None):
        self.close(force=False)

    def _on_key(self, event):
        if getattr(event, "key", "") == "Escape":
            event.stopPropagation()
            self.close(force=False)


def open(content, host=None, title="", subtitle="", eyebrow="", footer=(), width=480,
         on_close=None, confirm_close=None):
    """Slide ``content`` in from the right and return the ``Drawer``.

    ``footer`` holds buttons pinned to the bottom. ``confirm_close`` is a callable
    that returns True when it is fine to close (Escape, backdrop, or the close
    button); ``discard_check`` builds a typical one.
    """
    return Drawer(content, host=host, title=title, subtitle=subtitle, eyebrow=eyebrow, footer=footer,
                  width=width, on_close=on_close, confirm_close=confirm_close).show()


def discard_check(is_dirty, message="Your changes in this panel will be lost.", title="Discard changes?"):
    """A ``confirm_close`` that asks before throwing away unsaved changes."""

    def check():
        if not is_dirty():
            return True
        return dialogs.confirm(message, title=title, confirm_text="Discard", cancel_text="Keep editing", danger=True)

    return check
