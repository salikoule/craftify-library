from ..Startup import configure as configure_craftify_client
from ._anvil_designer import LibraryDemoTemplate
from anvil import *
from routing import router
from tabulator.Tabulator import Tabulator
from ..CustomComponents.EChart import EChart

from ..CustomComponents.KpiCard import KpiCard
from ..CustomComponents.ChartCard import ChartCard
from ..CustomComponents.SettingsOverlay import SettingsOverlay
from ..CraftifyUtils.echarts_theme import apply_craftify_echarts_theme
from ..CraftifyUtils import craftify_table as cf_table


class LibraryDemo(LibraryDemoTemplate):
    def __init__(self, routing_context=None, **properties):
        self.init_components(**properties)
        configure_craftify_client()
        self._build_demo()

    def _build_demo(self):
        intro = Label(
            text="Shared theme, Tabulator defaults, ECharts theme, KPI and chart shells — same patterns as iPac.",
            font_size=13,
        )
        self._settings = SettingsOverlay(
            app_name="craftify-library",
            app_version="1.0",
            app_description="Shared Craftify Anvil components.",
        )
        self.add_component(self._settings)
        open_settings = Button(text="Open settings", role="primary-color")
        open_settings.set_event_handler("click", lambda **e: self._settings.open())
        self.main_panel.add_component(intro, full_width_row=True)
        self.main_panel.add_component(open_settings)

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
        table.height = "280px"
        table.options = {
            "pagination": True,
            "pagination_size": 10,
            "pagination_counter": "rows",
            "layout": "fitColumns",
            "index": "id",
        }
        columns = cf_table.stamp_columns([
            {"title": "Order", "field": "id", "width": 112, "header_filter": True, "sorter": "string"},
            {"title": "Customer", "field": "name", "width_grow": 2, "header_filter": True},
            {"title": "Amount", "field": "amount", "width": 110, "header_filter": True, "sorter": "number", "hoz_align": "right"},
            {"title": "Placed", "field": "placed", "width": 130, "header_filter": True},
            cf_table.stamp_column({"title": "Status", "field": "status", "width": 130, "header_filter": "list"},
                                  kind="list", choices=["Active", "Draft", "Shipped"]),
        ])
        table.columns = columns
        table.data = [
            {"id": "ORD-1001", "name": "Acme Corp", "amount": 420, "placed": "12 Mar 2025", "status": "Active"},
            {"id": "ORD-1002", "name": "Beta Industries", "amount": 89, "placed": "3 Feb 2025", "status": "Draft"},
            {"id": "ORD-1003", "name": "Cyclops SA", "amount": 1280, "placed": "1 Jan 2025", "status": "Shipped"},
        ]
        cf_table.attach_toolbar(table, remote=False)
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
