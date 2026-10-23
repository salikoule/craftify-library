from ..Startup import configure as configure_craftify_client
from ._anvil_designer import LibraryDemoTemplate
from anvil import *
from tabulator.Tabulator import Tabulator
from ..CustomComponents.EChart import EChart

from ..CustomComponents.KpiCard import KpiCard
from ..CustomComponents.ChartCard import ChartCard
from ..CraftifyUtils.echarts_theme import apply_craftify_echarts_theme


class LibraryDemo(LibraryDemoTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        configure_craftify_client()
        self._build_demo()

    def _build_demo(self):
        intro = Label(
            text="Shared theme, Tabulator defaults, ECharts theme, KPI and chart shells — same patterns as iPac.",
            font_size=13,
        )
        self.main_panel.add_component(intro, full_width_row=True)

        kpi_row = FlowPanel(align="left", spacing=12)
        for title, value, subtitle, tone in (
            ("Active users", "128", "Last 7 days", "good"),
            ("Open tasks", "14", "Needs review", "warn"),
            ("Failed jobs", "2", "Since midnight", "bad"),
        ):
            kpi_row.add_component(
                KpiCard(title=title, value=value, subtitle=subtitle, tone=tone, clickable=True),
                width=220,
            )
        self.main_panel.add_component(kpi_row, full_width_row=True)

        table = Tabulator()
        table.height = "220px"
        table.columns = [
            {"title": "ID", "field": "id", "width": 90},
            {"title": "Name", "field": "name", "header_filter": True},
            {"title": "Status", "field": "status", "width": 120},
        ]
        table.data = [
            {"id": "PRD-001", "name": "Sample product", "status": "Active"},
            {"id": "PRD-002", "name": "Second row", "status": "Draft"},
            {"id": "PRD-003", "name": "Third row", "status": "Active"},
        ]
        self.main_panel.add_component(table, full_width_row=True)

        chart_card = ChartCard(
            title="Weekly output",
            subtitle="ECharts with Craftify theme defaults",
        )
        options = apply_craftify_echarts_theme(
            {
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": [120, 200, 150, 80, 190], "name": "Units"}],
            }
        )
        chart_card.mount(EChart(options=options, height="280px"))
        self.main_panel.add_component(chart_card, full_width_row=True)
