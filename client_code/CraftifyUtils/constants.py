"""Shared constants for Craftify client apps (iPac-aligned palette and dates)."""

import datetime

STORED_DATE_FORMAT_WITH_DAYS = "%Y%m%d"
STORED_DATE_FORMAT = "%Y%m"
DISPLAY_DATE_FORMAT_WITH_DAYS = "%b %d %Y"
DISPLAY_DATE_FORMAT = "%b %Y"
STORED_DATE_FORMAT_DASHES = "%Y-%m-%d"
DISPLAY_TIME_FORMAT = "%H:%M:%S"

COLORS_LIST = [
    "#4c6e91",
    "#5e9970",
    "#bf9000",
    "#8e7cc3",
    "#ce6f69",
    "#d09e88",
    "#6b7f76",
    "#b27c7f",
    "#8d7b6e",
    "#9b9ba3",
    "#7c9fb0",
    "#77926f",
]

TODAY = datetime.date.today()
