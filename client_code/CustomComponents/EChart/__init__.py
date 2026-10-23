"""Apache ECharts host — loads from CDN via app native_deps (no Anvil dependency app)."""

import uuid

from anvil.js import window

from ._anvil_designer import EChartTemplate


def _apply_theme(option):
    from ...CraftifyUtils.echarts_theme import apply_craftify_echarts_theme

    return apply_craftify_echarts_theme(option or {})


class EChart(EChartTemplate):
    def __init__(self, options: dict = None, **properties):
        self.chart_id = str(uuid.uuid4())
        self.dom_nodes["echart_div"].setAttribute("id", self.chart_id)
        self.init_components(**properties)
        self._first_load = True
        self.option = _apply_theme(options) if options else {}
        self.chart = None

    @property
    def height(self):
        return getattr(self, "_height", "300px")

    @height.setter
    def height(self, value):
        self._height = value or "300px"
        v = self._height
        if isinstance(v, str) and v.endswith("%"):
            v = f"{v[:-1]}dvh"
        self.dom_nodes["echart_div"].style.height = v

    @property
    def width(self):
        return getattr(self, "_width", "100%")

    @width.setter
    def width(self, value):
        self._width = value or "100%"
        self.dom_nodes["echart_div"].style.width = self._width

    @property
    def resize(self):
        return getattr(self, "_resize", True)

    @resize.setter
    def resize(self, value):
        self._resize = bool(value)

    def form_show(self, **event_args):
        if not self._first_load:
            return
        self._first_load = False
        self.chart = self.call_js("craftifyDefineChart", self.chart_id)
        if self.option:
            self.set_option(self.option)
        self._watch_resize()

    def set_option(self, option: dict, not_merge: bool = True):
        self.option = _apply_theme(option)
        if self.chart is None:
            return
        self.chart.setOption(self.option, not_merge)

    def _watch_resize(self):
        if not self.resize or self.chart is None:
            return
        if not getattr(window, "ResizeObserver", None):
            return
        observer = window.ResizeObserver(lambda entries, obs: self.chart.resize())
        observer.observe(self.dom_nodes["echart_div"])
