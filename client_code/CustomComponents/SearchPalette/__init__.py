from ._anvil_designer import SearchPaletteTemplate
import json

from anvil import HtmlTemplate
from anvil.js.window import clearTimeout, document, localStorage, navigator, setTimeout


_CSS_ID = "cf-searchpalette-css"
_CSS = """
.cf-sp, .cf-sp-trigger {
  --cf-sp-surface: #fff; --cf-sp-panel: #f4f6fa; --cf-sp-ink: #0f172a; --cf-sp-muted: #64748b; --cf-sp-line: #e2e8f0;
  --cf-sp-hover: #eef2f7; --cf-sp-accent: #2563eb; --cf-sp-accent-ink: #fff; --cf-sp-ring: rgba(37, 99, 235, 0.16); --cf-sp-kbd: #fff;
}
.ipac-dark .cf-sp, .craftify-theme-dark .cf-sp, [data-theme=dark] .cf-sp,
.ipac-dark .cf-sp-trigger, .craftify-theme-dark .cf-sp-trigger, [data-theme=dark] .cf-sp-trigger {
  --cf-sp-surface: #1b2638; --cf-sp-panel: #111927; --cf-sp-ink: #e6edf7; --cf-sp-muted: #94a3b8; --cf-sp-line: #2c3a50;
  --cf-sp-hover: #22314a; --cf-sp-accent: #3b82f6; --cf-sp-ring: rgba(59, 130, 246, 0.22); --cf-sp-kbd: #22314a;
}
.cf-sp { display: none; }
.cf-sp.is-open { display: block; }
.cf-sp *, .cf-sp-trigger * { box-sizing: border-box; }
.cf-sp-backdrop {
  position: fixed; inset: 0; z-index: 2000; display: flex; justify-content: center; align-items: flex-start;
  padding: 10vh 16px 16px; background: rgba(2, 6, 23, 0.55); backdrop-filter: blur(3px);
  font-family: Montserrat, system-ui, sans-serif; animation: cf-sp-fade 0.12s ease-out;
}
.cf-sp-card {
  width: min(620px, 100%); max-height: 78vh; display: flex; flex-direction: column; overflow: hidden;
  background: var(--cf-sp-panel); color: var(--cf-sp-ink); border: 1px solid var(--cf-sp-line); border-radius: 16px;
  box-shadow: 0 30px 70px rgba(2, 6, 23, 0.4); animation: cf-sp-rise 0.14s ease-out;
}
.cf-sp-field {
  display: flex; align-items: center; gap: 12px; margin: 14px 14px 4px; padding: 0 12px 0 14px; height: 54px; cursor: text;
  background: var(--cf-sp-surface); border: 2px solid var(--cf-sp-accent); border-radius: 12px; box-shadow: 0 0 0 4px var(--cf-sp-ring);
}
.cf-sp-field svg { width: 21px; height: 21px; flex: 0 0 auto; color: var(--cf-sp-accent); }
html body .cf-sp .cf-sp-field input.cf-sp-input {
  all: unset; flex: 1; min-width: 0; height: 100%; font-family: inherit; font-size: 17px; font-weight: 500; line-height: 1.3;
  color: var(--cf-sp-ink) !important; -webkit-text-fill-color: var(--cf-sp-ink) !important; caret-color: var(--cf-sp-accent);
  background: transparent !important; border: 0 !important; box-shadow: none !important; padding: 0 !important; margin: 0 !important; outline: none !important;
}
html body .cf-sp .cf-sp-field input.cf-sp-input::placeholder { -webkit-text-fill-color: var(--cf-sp-muted) !important; }
.cf-sp input.cf-sp-input::placeholder { color: var(--cf-sp-muted); opacity: 1; font-weight: 400; }
.cf-sp button.cf-sp-clear {
  all: unset; display: none; padding: 2px 7px; border-radius: 6px; cursor: pointer; font-size: 20px; line-height: 1; color: var(--cf-sp-muted);
  background: transparent !important; border: 0 !important; box-shadow: none !important;
}
.cf-sp-field.has-text button.cf-sp-clear { display: block; }
.cf-sp kbd svg { width: 11px; height: 11px; }
.cf-sp button.cf-sp-clear:hover { color: var(--cf-sp-ink); background: var(--cf-sp-hover); }
.cf-sp-body { flex: 1; overflow-y: auto; padding: 4px 14px 14px; scrollbar-width: thin; }
.cf-sp-head { margin: 12px 2px 8px; font-size: 12px; font-weight: 700; letter-spacing: 0.02em; color: var(--cf-sp-accent); }
.cf-sp-list { display: flex; flex-direction: column; gap: 6px; }
.cf-sp a.cf-sp-hit {
  display: flex; align-items: center; gap: 12px; min-height: 50px; margin: 0; padding: 8px 12px; cursor: pointer;
  background: var(--cf-sp-surface); color: var(--cf-sp-ink); border: 1px solid var(--cf-sp-line); border-radius: 10px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06); text-decoration: none; line-height: 1.3;
}
.cf-sp a.cf-sp-hit:hover, .cf-sp a.cf-sp-hit:focus { color: var(--cf-sp-ink); text-decoration: none; }
.cf-sp a.cf-sp-hit.is-active { background: var(--cf-sp-accent); border-color: var(--cf-sp-accent); color: var(--cf-sp-accent-ink); }
.cf-sp-lead { flex: 0 0 auto; display: inline-flex; align-items: center; color: var(--cf-sp-muted); }
.cf-sp-lead svg { width: 18px; height: 18px; }
.cf-sp-text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.cf-sp-title { font-size: 14px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cf-sp-sub { font-size: 12px; color: var(--cf-sp-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cf-sp-kind { flex: 0 0 auto; font-size: 12px; color: var(--cf-sp-muted); }
.cf-sp a.cf-sp-hit.is-active .cf-sp-sub, .cf-sp a.cf-sp-hit.is-active .cf-sp-kind, .cf-sp a.cf-sp-hit.is-active .cf-sp-lead { color: rgba(255, 255, 255, 0.85); }
.cf-sp button.cf-sp-remove {
  all: unset; flex: 0 0 auto; width: 26px; height: 26px; display: inline-flex; align-items: center; justify-content: center;
  border-radius: 6px; cursor: pointer; font-size: 18px; color: var(--cf-sp-muted);
}
.cf-sp button.cf-sp-remove { background: transparent !important; border: 0 !important; box-shadow: none !important; }
.cf-sp button.cf-sp-remove:hover { background: var(--cf-sp-hover); color: var(--cf-sp-ink); }
.cf-sp a.cf-sp-hit.is-active button.cf-sp-remove { color: #fff; }
.cf-sp a.cf-sp-hit.is-active button.cf-sp-remove:hover { background: rgba(255, 255, 255, 0.18); }
.cf-sp-empty { padding: 30px 8px; text-align: center; font-size: 14px; color: var(--cf-sp-muted); }
.cf-sp-empty strong { color: var(--cf-sp-ink); }
.cf-sp-foot {
  display: flex; align-items: center; gap: 18px; padding: 10px 16px; font-size: 12px; color: var(--cf-sp-muted);
  background: var(--cf-sp-surface); border-top: 1px solid var(--cf-sp-line);
}
.cf-sp-foot span { display: inline-flex; align-items: center; gap: 4px; }
.cf-sp kbd, .cf-sp-trigger kbd {
  display: inline-flex; align-items: center; justify-content: center; min-width: 20px; height: 19px; padding: 0 5px; margin-right: 2px;
  font-family: inherit; font-size: 11px; font-weight: 600; line-height: 1; color: var(--cf-sp-muted);
  background: var(--cf-sp-kbd); border: 1px solid var(--cf-sp-line); border-radius: 5px; box-shadow: inset 0 -1px 0 var(--cf-sp-line);
}
a.cf-sp-trigger {
  display: flex !important; align-items: center; gap: 10px; margin: 0 12px 10px !important; padding: 7px 10px !important;
  font-size: 13px; color: var(--cf-sp-muted) !important; text-decoration: none !important; cursor: pointer;
  background: var(--cf-sp-surface); border: 1px solid var(--cf-sp-line); border-radius: 8px;
}
a.cf-sp-trigger:hover { color: var(--cf-sp-ink) !important; border-color: var(--cf-sp-muted); }
a.cf-sp-trigger svg { width: 15px; height: 15px; flex: 0 0 auto; }
a.cf-sp-trigger kbd { margin-left: auto; }
.structure.nav-collapsed a.cf-sp-trigger { margin: 0 8px 8px !important; background: transparent; border-color: transparent; }
.structure.nav-collapsed a.cf-sp-trigger kbd { display: none; }
@keyframes cf-sp-fade { from { opacity: 0; } }
@keyframes cf-sp-rise { from { opacity: 0; transform: translateY(-8px) scale(0.98); } }
@media (max-width: 600px) {
  .cf-sp-backdrop { padding: 0; }
  .cf-sp-card { height: 100vh; max-height: 100vh; border-radius: 0; }
  .cf-sp-foot { display: none; }
}
"""

_SEARCH_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true">'
    '<circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.5-3.5"></path></svg>'
)
_RECENT_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"></path><path d="M3 3v5h5"></path><path d="M12 7v5l3 2"></path></svg>'
)

_ENTER = "M20 5v7a3 3 0 0 1-3 3H5M9 11l-4 4 4 4"
_DOWN = "M12 5v14M6 13l6 6 6-6"
_UP = "M12 19V5M6 11l6-6 6 6"


def _key_icon(path):
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><path d="%s"></path></svg>' % path
    )


_SHORTCUT_OWNER = [None]
_LISTENING = [False]


def shortcut_label():
    """"⌘K" on a Mac, "Ctrl K" elsewhere."""
    return "⌘K" if "Mac" in str(navigator.platform or "") else "Ctrl K"


def _esc(value):
    return str(value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _install_css():
    if document.getElementById(_CSS_ID):
        return
    style = document.createElement("style")
    style.id = _CSS_ID
    style.textContent = _CSS
    document.head.appendChild(style)


def _on_document_key(event):
    owner = _SHORTCUT_OWNER[0]
    if owner is None:
        return
    if (event.metaKey or event.ctrlKey) and str(event.key or "").lower() == "k":
        event.preventDefault()
        owner.toggle()


def _identity(hit):
    return json.dumps([hit.get("id"), hit.get("kind"), hit.get("badge"), hit.get("title")])


class SearchPalette(SearchPaletteTemplate):
    """A search pop-up over the page. `search(text)` returns hits; picking one raises `select` with `hit`.

    A hit is a dict: title, and optionally subtitle, badge, badge_class, kind, id, plus any keys the app needs back.
    With `recent_key` set, picked hits are kept in the browser and shown as Recent while the box is empty.
    """

    def __init__(self, search=None, **properties):
        self.search = search
        self.placeholder = properties.pop("placeholder", "Search") or "Search"
        self.recent_key = properties.pop("recent_key", "") or ""
        self.recent_limit = int(properties.pop("recent_limit", 6) or 6)
        self.min_chars = int(properties.pop("min_chars", 2) or 1)
        self.delay_ms = int(properties.pop("delay_ms", 250) or 0)
        self.shortcut = bool(properties.pop("shortcut", True))
        self._shown = []
        self._active = -1
        self._timer = None
        self._seq = 0
        self.init_components(**properties)
        _install_css()
        self._build()
        if self.shortcut:
            _SHORTCUT_OWNER[0] = self
            if not _LISTENING[0]:
                document.addEventListener("keydown", _on_document_key)
                _LISTENING[0] = True

    def _build(self):
        root = self.dom_nodes["root"]
        root.innerHTML = (
            '<div class="cf-sp-backdrop"><div class="cf-sp-card" role="dialog" aria-modal="true" aria-label="Search">'
            '<label class="cf-sp-field">%s<input class="cf-sp-input" type="text" autocomplete="off" spellcheck="false" placeholder="%s">'
            '<button type="button" class="cf-sp-clear" aria-label="Clear">&times;</button></label>'
            '<div class="cf-sp-body"></div>'
            '<div class="cf-sp-foot"><span><kbd>%s</kbd> to select</span><span><kbd>%s</kbd><kbd>%s</kbd> to navigate</span>'
            "<span><kbd>esc</kbd> to close</span></div>"
            "</div></div>" % (_SEARCH_ICON, _esc(self.placeholder), _key_icon(_ENTER), _key_icon(_DOWN), _key_icon(_UP))
        )
        self._backdrop = root.querySelector(".cf-sp-backdrop")
        self._field = root.querySelector(".cf-sp-field")
        self._input = root.querySelector(".cf-sp-input")
        self._body = root.querySelector(".cf-sp-body")
        root.addEventListener("click", self._on_click)
        root.addEventListener("mousemove", self._on_hover)
        self._input.addEventListener("input", self._on_input)
        self._input.addEventListener("keydown", self._on_key)

    def open(self, *args):
        self._input.value = ""
        self._field.classList.remove("has-text")
        self._render_idle()
        self.dom_nodes["root"].classList.add("is-open")
        setTimeout(lambda: self._input.focus(), 0)

    def close(self, *args):
        self._seq += 1
        self.dom_nodes["root"].classList.remove("is-open")

    def toggle(self, *args):
        if self.dom_nodes["root"].classList.contains("is-open"):
            self.close()
        else:
            self.open()

    def trigger(self, label="Search"):
        """A sidebar button that opens the palette, showing the keyboard shortcut."""
        button = HtmlTemplate(
            html='<a class="cf-sp-trigger" anvil-name="root" href="javascript:void(0)" data-nav-label="%s" aria-label="%s">'
            '%s<span class="link-text">%s</span><kbd>%s</kbd></a>'
            % (_esc(label), _esc(label), _SEARCH_ICON, _esc(label), shortcut_label() if self.shortcut else "")
        )
        button.dom_nodes["root"].addEventListener("click", self.open)
        return button

    def _on_input(self, event):
        text = self._input.value.strip()
        self._field.classList.toggle("has-text", bool(self._input.value))
        if self._timer is not None:
            clearTimeout(self._timer)
            self._timer = None
        self._seq += 1
        if not text:
            self._render_idle()
        elif len(text) < self.min_chars:
            self._render_message("Keep typing…")
        else:
            seq = self._seq
            self._timer = setTimeout(lambda: self._run(seq), self.delay_ms)

    def _run(self, seq):
        self._timer = None
        if seq != self._seq:
            return
        text = self._input.value.strip()
        if not self._shown:
            self._render_message("Searching…")
        try:
            hits = list(self.search(text) or []) if self.search else []
        except Exception:
            if seq == self._seq:
                self._render_message("The search did not work. Try again.")
            return
        if seq != self._seq:
            return
        if hits:
            self._render_list("Results", hits, removable=False)
        else:
            self._render_message('No results for <strong>"%s"</strong>' % _esc(text), html=True)

    def _on_key(self, event):
        key = event.key
        if key == "Escape":
            event.preventDefault()
            self.close()
        elif key in ("ArrowDown", "ArrowUp"):
            event.preventDefault()
            self._move(1 if key == "ArrowDown" else -1)
        elif key == "Enter":
            event.preventDefault()
            if 0 <= self._active < len(self._shown):
                self._select(self._active)
            elif self._input.value.strip():
                self._seq += 1
                self._run(self._seq)

    def _on_click(self, event):
        target = event.target
        if target == self._backdrop:
            self.close()
            return
        remove = target.closest("[data-sp-remove]")
        if remove:
            event.preventDefault()
            event.stopPropagation()
            self._forget(int(remove.getAttribute("data-sp-remove")))
            return
        if target.closest(".cf-sp-clear"):
            event.preventDefault()
            self._input.value = ""
            self._on_input(None)
            self._input.focus()
            return
        hit = target.closest("[data-sp-hit]")
        if hit:
            event.preventDefault()
            self._select(int(hit.getAttribute("data-sp-hit")))

    def _on_hover(self, event):
        hit = event.target.closest("[data-sp-hit]")
        if hit:
            index = int(hit.getAttribute("data-sp-hit"))
            if index != self._active:
                self._set_active(index, scroll=False)

    def _render_idle(self):
        recent = self._recent()
        if recent:
            self._render_list("Recent", recent, removable=True)
        else:
            self._render_message("Type to search.")

    def _render_message(self, text, html=False):
        self._shown = []
        self._active = -1
        self._body.innerHTML = '<div class="cf-sp-empty">%s</div>' % (text if html else _esc(text))

    def _render_list(self, heading, hits, removable):
        self._shown = hits
        rows = []
        for index, hit in enumerate(hits):
            if removable:
                lead = _RECENT_ICON
            elif hit.get("badge"):
                lead = '<span class="%s">%s</span>' % (_esc(hit.get("badge_class") or "cf-sp-badge"), _esc(hit.get("badge")))
            else:
                lead = ""
            sub = hit.get("subtitle")
            if removable and hit.get("badge"):
                sub = " · ".join(part for part in (hit.get("badge"), sub) if part)
            rows.append(
                '<a class="cf-sp-hit" href="javascript:void(0)" data-sp-hit="%d">%s'
                '<span class="cf-sp-text"><span class="cf-sp-title">%s</span>%s</span>%s%s</a>'
                % (
                    index,
                    '<span class="cf-sp-lead">%s</span>' % lead if lead else "",
                    _esc(hit.get("title")),
                    '<span class="cf-sp-sub">%s</span>' % _esc(sub) if sub else "",
                    '<span class="cf-sp-kind">%s</span>' % _esc(hit.get("kind")) if hit.get("kind") else "",
                    '<button type="button" class="cf-sp-remove" data-sp-remove="%d" aria-label="Remove from recent">&times;</button>' % index if removable else "",
                )
            )
        self._body.innerHTML = '<div class="cf-sp-head">%s</div><div class="cf-sp-list">%s</div>' % (_esc(heading), "".join(rows))
        self._active = -1
        self._set_active(0)

    def _move(self, step):
        if self._shown:
            self._set_active((self._active + step) % len(self._shown))

    def _set_active(self, index, scroll=True):
        self._active = index
        for node in self._body.querySelectorAll("[data-sp-hit]"):
            on = int(node.getAttribute("data-sp-hit")) == index
            node.classList.toggle("is-active", on)
            if on and scroll:
                node.scrollIntoView({"block": "nearest"})

    def _select(self, index):
        hit = self._shown[index]
        self._remember(hit)
        self.close()
        self.raise_event("select", hit=hit)

    def _storage_key(self):
        return "cf-sp:" + self.recent_key

    def _recent(self):
        if not self.recent_key:
            return []
        try:
            saved = json.loads(localStorage.getItem(self._storage_key()) or "[]")
        except Exception:
            return []
        return [hit for hit in saved if isinstance(hit, dict)][: self.recent_limit]

    def _save_recent(self, hits):
        try:
            localStorage.setItem(self._storage_key(), json.dumps(hits[: self.recent_limit]))
        except Exception:
            pass

    def _remember(self, hit):
        if not self.recent_key:
            return
        try:
            json.dumps(hit)
        except Exception:
            return
        key = _identity(hit)
        self._save_recent([hit] + [old for old in self._recent() if _identity(old) != key])

    def _forget(self, index):
        recent = self._recent()
        if 0 <= index < len(recent):
            del recent[index]
            self._save_recent(recent)
        self._render_idle()
        self._input.focus()
