from routing import router
"""Client helpers shared across Craftify Anvil apps (subset of iPac ClientUtils)."""

import datetime
import math
import re
import time
from collections import defaultdict

import anvil.js
import anvil.server
from anvil import Notification

from . import constants

STORED_DATE_FORMAT_WITH_DAYS = constants.STORED_DATE_FORMAT_WITH_DAYS
STORED_DATE_FORMAT = constants.STORED_DATE_FORMAT
DISPLAY_DATE_FORMAT_WITH_DAYS = constants.DISPLAY_DATE_FORMAT_WITH_DAYS
DISPLAY_DATE_FORMAT = constants.DISPLAY_DATE_FORMAT
COLORS_LIST = constants.COLORS_LIST


def escape_html(value) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def build_chip_style(
    bg: str,
    fg: str,
    height_px: int = 22,
    pad_y_px: int = 2,
    pad_x_px: int = 10,
    justify: str = "center",
) -> str:
    return (
        "display:inline-flex;"
        f"align-items:center;justify-content:{justify};gap:6px;"
        f"padding:{pad_y_px}px {pad_x_px}px;height:{height_px}px;line-height:{height_px}px;"
        "border-radius:9999px;"
        "font-size:12px;font-weight:600;letter-spacing:.2px;"
        "font-variant-numeric:tabular-nums;"
        f"--ink:{fg};background:{bg};color:{fg};"
        f"border:1px solid color-mix(in srgb, {fg} 18%, transparent);"
        "box-shadow:0 1px 0 rgba(0,0,0,.04);"
        "white-space:nowrap;"
    )


def build_chip_html(
    label,
    bg: str,
    fg: str,
    icon: str = None,
    height_px: int = 22,
    pad_y_px: int = 2,
    pad_x_px: int = 10,
    justify: str = "center",
) -> str:
    icon_html = (
        f'<i class="fa {icon}" style="font-size:11px;opacity:.85;"></i>' if icon else ""
    )
    style = build_chip_style(
        bg=bg,
        fg=fg,
        height_px=height_px,
        pad_y_px=pad_y_px,
        pad_x_px=pad_x_px,
        justify=justify,
    )
    return f'<span class="craftify-chip" style="{style}">{icon_html}{escape_html(label)}</span>'


def beautify_digit(value, decimal_places=None, min_value_for_suffix=1, use_space=False):
    if isinstance(value, str):
        value = value.replace(".", "")
        value = float(value)
    num = float(value)
    suffixes = [("T", 1e12), ("B", 1e9), ("M", 1e6), ("k", 1e3)]
    if num == 0:
        return "0"
    sign = "-" if num < 0 else ""
    num = abs(num)
    separator = " " if use_space else ""
    for suffix, threshold in suffixes:
        if num >= threshold and num >= min_value_for_suffix:
            formatted_num = num / threshold
            if decimal_places is None:
                if formatted_num.is_integer():
                    return f"{sign}{int(formatted_num)}{separator}{suffix}"
                formatted = f"{sign}{formatted_num:.1f}{separator}{suffix}"
                return formatted.rstrip("0").rstrip(".")
            if decimal_places == 0:
                return f"{sign}{round(formatted_num)}{separator}{suffix}"
            formatted = f"{sign}{formatted_num:.{decimal_places}f}{separator}{suffix}"
            return formatted.rstrip("0").rstrip(".") if "." in formatted else formatted
    if decimal_places is None:
        if num.is_integer() or num < min_value_for_suffix:
            return f"{sign}{int(round(num))}"
        formatted = f"{sign}{num:.2f}"
        return formatted.rstrip("0").rstrip(".")
    if decimal_places == 0:
        return f"{sign}{round(num)}"
    formatted = f"{sign}{num:.{decimal_places}f}"
    return formatted.rstrip("0").rstrip(".") if "." in formatted else formatted


def wait_background_task(task, show_msg: bool = True, raise_exception: bool = True, sleep: int = 5) -> bool:
    with anvil.server.no_loading_indicator:
        while task.is_running():
            time.sleep(sleep)
        if task.get_termination_status() == "failed":
            if show_msg:
                Notification(
                    "There was an error running the background task. Please contact admin.",
                    timeout=10,
                ).show()
                print(task.get_error())
            if raise_exception:
                raise task.get_error()
            return False
    return True


def monitor_background_task(
    task,
    on_complete=None,
    on_error=None,
    show_msg: bool = True,
    success_message: str = None,
    poll_ms: int = 2000,
):
    def finish():
        if task.get_termination_status() == "failed":
            if show_msg:
                Notification(
                    "There was an error running the background task. Please contact admin.",
                    timeout=10,
                ).show()
                print(task.get_error())
            if on_error:
                on_error(task)
            return
        if success_message:
            Notification(success_message, style="success", timeout=5).show()
        if on_complete:
            on_complete(task)

    def poll():
        with anvil.server.no_loading_indicator:
            if task.is_running():
                anvil.js.window.setTimeout(poll, poll_ms)
                return
        finish()

    anvil.js.window.setTimeout(poll, 0)


def sum_dictionaries_by_keys(dict_list: list) -> dict:
    sum_dict = defaultdict(int)
    for d in dict_list:
        for k in dict(d):
            sum_dict[k] += d[k]
    return sum_dict


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+'+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def sort_dict_by_date(unsorted_dictionary, date_format, strftime_format=None, reverse=False) -> dict:
    strftime_format = date_format if not strftime_format else strftime_format
    sorted_dictionary = sorted(
        {
            datetime.datetime.strptime(key, date_format): value
            for key, value in unsorted_dictionary.items()
        },
        reverse=reverse,
    )
    return {
        key.strftime(strftime_format): unsorted_dictionary[key.strftime(strftime_format)]
        for key in sorted_dictionary
    }
