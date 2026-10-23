from ._anvil_designer import ChartCardTemplate


class ChartCard(ChartCardTemplate):
    """Standalone chart shell: left title + subtitle, chart mounted below."""

    def __init__(self, **properties):
        title = properties.pop("title", "")
        subtitle = properties.pop("subtitle", "")
        self.init_components(**properties)
        self.title = title
        self.subtitle = subtitle

    def _node(self, name):
        nodes = getattr(self, "dom_nodes", None)
        if not nodes:
            return None
        try:
            return nodes[name]
        except Exception:
            return None

    @property
    def title(self):
        node = self._node("title")
        return (node.textContent or "") if node is not None else ""

    @title.setter
    def title(self, value):
        node = self._node("title")
        if node is not None:
            node.textContent = value or ""

    @property
    def subtitle(self):
        node = self._node("subtitle")
        return (node.textContent or "") if node is not None else ""

    @subtitle.setter
    def subtitle(self, value):
        node = self._node("subtitle")
        if node is None:
            return
        text = value or ""
        node.textContent = text
        if text:
            node.classList.remove("is-empty")
        else:
            node.classList.add("is-empty")

    def clear(self):
        host = getattr(self, "chart_host", None)
        if host is None:
            return super().clear()
        host.clear()

    def add_component(self, component, **kwargs):
        host = getattr(self, "chart_host", None)
        if host is None or component is host:
            return super().add_component(component, **kwargs)
        kwargs.setdefault("full_width_row", True)
        return host.add_component(component, **kwargs)

    def mount(self, component, **kwargs):
        self.clear()
        return self.add_component(component, **kwargs)
