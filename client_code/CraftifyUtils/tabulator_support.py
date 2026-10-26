from routing import router
"""Shared Tabulator loader markup (styled in theme.css)."""

CRAFTIFY_TABULATOR_LOADER_HTML = (
    '<div class="ipac-tabulator-loader">'
    '<div class="ipac-tabulator-loader-spinner" aria-hidden="true"></div>'
    '<span class="ipac-tabulator-loader-label">Loading data…</span>'
    "</div>"
)

CRAFTIFY_TABULATOR_LOADER_ERROR_HTML = (
    '<div class="ipac-tabulator-loader ipac-tabulator-loader--error">'
    '<i class="fa fa-exclamation-circle ipac-tabulator-loader-icon" aria-hidden="true"></i>'
    '<span class="ipac-tabulator-loader-label">Unable to load data</span>'
    "</div>"
)
