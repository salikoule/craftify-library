from routing import router
# flake8: noqa: F401
"""Tabulator + ECharts defaults. Call ``configure()`` from a form (e.g. LibraryDemo), not at app import."""

_configured = False


def configure():
    """Idempotent: safe to call from LibraryDemo.__init__ or form_show."""
    global _configured
    if _configured:
        return
    from tabulator.Tabulator import Tabulator

    from .CraftifyUtils import tabulator_support
    from .CraftifyUtils.echarts_theme import install_craftify_echarts_theme

    Tabulator.default_options["selectable"] = False
    Tabulator.default_options["dataLoaderLoading"] = tabulator_support.CRAFTIFY_TABULATOR_LOADER_HTML
    Tabulator.default_options["dataLoaderError"] = tabulator_support.CRAFTIFY_TABULATOR_LOADER_ERROR_HTML
    Tabulator.theme = "bootstrap3"

    for name in (
        "HistoryModule",
        "AjaxModule",
        "ColumnCalcsModule",
        "DownloadModule",
        "ExportModule",
        "MoveRowsModule",
        "AccessorModule",
        "GroupRowsModule",
        "TooltipModule",
        "FilterModule",
        "PageModule",
        "MutatorModule",
        "DataTreeModule",
        "SelectRowModule",
        "KeybindingsModule",
    ):
        Tabulator.modules.add(name)

    install_craftify_echarts_theme()
    _configured = True
