from ._anvil_designer import KpiCardTemplate


TONES = ("good", "warn", "bad")


class KpiCard(KpiCardTemplate):
    """Compact metric tile: uppercase title, large value, optional subtitle."""

    def __init__(self, **properties):
        title = properties.pop("title", "")
        value = properties.pop("value", "—")
        subtitle = properties.pop("subtitle", "")
        tone = properties.pop("tone", "")
        selected = properties.pop("selected", False)
        enabled = properties.pop("enabled", True)
        clickable = properties.pop("clickable", False)
        icon = properties.pop("icon", "")
        icon_color = properties.pop("icon_color", "")
        self.init_components(**properties)
        self._wired = False
        self._icon = ""
        self._icon_color = ""
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.tone = tone
        self.selected = selected
        self.enabled = enabled
        self.clickable = clickable
        self.icon_color = icon_color
        self.icon = icon
        self._wire_click()

    def _node(self, name):
        nodes = getattr(self, "dom_nodes", None)
        if not nodes:
            return None
        try:
            return nodes[name]
        except Exception:
            return None

    def _wire_click(self):
        if self._wired:
            return
        card = self._node("card")
        if card is None:
            return
        card.addEventListener("click", self._on_click)
        self._wired = True

    def _on_click(self, *_args):
        if not self.enabled:
            return
        self.raise_event("click")
        self.raise_event("metrics_click")

    def _set_class(self, name, on):
        card = self._node("card")
        if card is None:
            return
        if on:
            card.classList.add(name)
        else:
            card.classList.remove(name)

    @property
    def title(self):
        node = self._node("title")
        return (node.textContent or "") if node is not None else ""

    @title.setter
    def title(self, value):
        node = self._node("title")
        if node is None:
            return
        text = value or ""
        node.textContent = text
        if text:
            node.classList.remove("is-empty")
        else:
            node.classList.add("is-empty")

    @property
    def value(self):
        node = self._node("value")
        return (node.textContent or "") if node is not None else ""

    @value.setter
    def value(self, value):
        node = self._node("value")
        if node is not None:
            node.textContent = "—" if value in (None, "") else str(value)

    @property
    def subtitle(self):
        node = self._node("subtitle")
        return (node.textContent or "") if node is not None else ""

    @subtitle.setter
    def subtitle(self, value):
        node = self._node("subtitle")
        if node is None:
            return
        text = "" if value in (None, "") else str(value)
        node.textContent = text
        if text:
            node.classList.remove("is-empty")
        else:
            node.classList.add("is-empty")

    @property
    def tone(self):
        return getattr(self, "_tone", "")

    @tone.setter
    def tone(self, value):
        tone = (value or "").replace("is-", "")
        if tone not in TONES:
            tone = ""
        self._tone = tone
        for name in TONES:
            self._set_class(f"is-{name}", name == tone)

    @property
    def selected(self):
        return getattr(self, "_selected", False)

    @selected.setter
    def selected(self, value):
        self._selected = bool(value)
        self._set_class("is-selected", self._selected)

    @property
    def enabled(self):
        return getattr(self, "_enabled", True)

    @enabled.setter
    def enabled(self, value):
        self._enabled = bool(value)
        self._set_class("is-disabled", not self._enabled)

    @property
    def clickable(self):
        return getattr(self, "_clickable", False)

    @clickable.setter
    def clickable(self, value):
        self._clickable = bool(value)
        self._set_class("is-clickable", self._clickable)

    @property
    def icon(self):
        return getattr(self, "_icon", "")

    @icon.setter
    def icon(self, value):
        self._icon = value or ""
        self._paint_icon()

    @property
    def icon_color(self):
        return getattr(self, "_icon_color", "")

    @icon_color.setter
    def icon_color(self, value):
        self._icon_color = value or ""
        self._paint_icon()

    def _paint_icon(self):
        node = self._node("icon")
        if node is None:
            return
        html = _icon_html(self._icon, self._icon_color)
        node.innerHTML = html
        if html:
            node.classList.remove("is-empty")
        else:
            node.classList.add("is-empty")


def _icon_html(icon, color=""):
    if not icon:
        return ""
    kind, name = _split_icon(icon)
    if not name:
        return ""
    style = f' style="color:{color}"' if color else ""
    if kind == "fa":
        css_name = name if name.startswith("fa-") else f"fa-{name}"
        return f'<i class="fa-solid {css_name} fa {css_name}"{style}></i>'
    return f'<span class="material-symbols-outlined"{style}>{name}</span>'


def _split_icon(icon):
    text = str(icon).strip()
    if ":" in text:
        prefix, name = text.split(":", 1)
        prefix = prefix.strip().lower()
        name = name.strip()
        if prefix in ("fa", "fas", "far", "fab"):
            return "fa", name
        return "mi", name
    return "mi", text
