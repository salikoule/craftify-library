"""Global visual defaults for every Apache ECharts chart in Craftify.

ECharts paints onto a canvas, so CSS cannot round bars. This module patches
EChart.__init__ once at startup (same idea as Tabulator.default_options) and
fills in styling a chart did not already set. Existing colours, stacks, and
formatters are left alone.
"""

_FONT = "Montserrat, system-ui, sans-serif"
_TITLE_COLOR = "#0f172a"
_MUTED = "#64748b"
_GRID = "#eef2f6"
_AXIS = "#e2e8f0"
_TOOLTIP_BG = "rgba(255,255,255,0.96)"
_TOOLTIP_BORDER = "#e2e8f0"
_SLICE_GAP = "#ffffff"
_TITLE_MIN_SIZE = 15
_SUBTITLE_MIN_SIZE = 13
_LABEL_MIN_SIZE = 13

_installed = False
_original_init = None


OPT_OUT_KEY = "craftify_theme"


def apply_craftify_echarts_theme(options):
    """Mutate an ECharts option dict with modern defaults. Returns the same object.

    Pass ``"craftify_theme": False`` to skip fonts, smooth lines, and animation.
    Stacked bars still follow the ECharts stack-end radius: only the outer
    segment of each column is rounded.
    """
    if not isinstance(options, dict):
        return options
    opted_out = options.get(OPT_OUT_KEY) is False
    if opted_out:
        options.pop(OPT_OUT_KEY, None)
    else:
        options.setdefault("animationDuration", 420)
        options.setdefault("animationEasing", "cubicOut")

        text_style = options.setdefault("textStyle", {})
        if isinstance(text_style, dict):
            text_style.setdefault("fontFamily", _FONT)
            text_style.setdefault("color", _TITLE_COLOR)

        _style_title(options.get("title"))
        _style_legend(options.get("legend"))
        _style_tooltip(options.get("tooltip"))
        _style_axes(options.get("xAxis"), is_value=_axis_is_value(options.get("xAxis")))
        _style_axes(options.get("yAxis"), is_value=_axis_is_value(options.get("yAxis")))

    horizontal = _is_horizontal_bar_chart(options)
    series = options.get("series")
    if isinstance(series, dict):
        if not opted_out:
            _style_series(series, horizontal)
        _round_stack_ends([series], horizontal)
    elif isinstance(series, list):
        if not opted_out:
            for item in series:
                _style_series(item, horizontal)
        _round_stack_ends(series, horizontal)

    return options


def install_craftify_echarts_theme():
    """Patch EChart so every chart picks up the theme. Safe to call more than once."""
    global _installed, _original_init
    if _installed:
        return
    from ..CustomComponents.EChart import EChart

    orig = EChart.__init__
    _original_init = orig

    def _themed_init(self, *args, **kwargs):
        if "options" in kwargs:
            kwargs["options"] = apply_craftify_echarts_theme(kwargs["options"])
        elif args and isinstance(args[0], dict):
            args = (apply_craftify_echarts_theme(args[0]),) + args[1:]
        return orig(self, *args, **kwargs)

    EChart.__init__ = _themed_init
    _inject_echarts_theme_script()
    _installed = True


def _inject_echarts_theme_script():
    """Load the canvas theme after echarts is available. Does not require anvil.yaml."""
    try:
        from anvil.js.window import document
        if document.getElementById("craftify-echarts-theme"):
            return
        script = document.createElement("script")
        script.id = "craftify-echarts-theme"
        script.src = "_/theme/echarts_theme.js"
        document.head.appendChild(script)
    except Exception:
        return


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _axis_is_value(axis):
    for item in _as_list(axis):
        if isinstance(item, dict) and item.get("type") == "value":
            return True
    return False


def _is_horizontal_bar_chart(options):
    y_is_category = False
    x_is_value = False
    for item in _as_list(options.get("yAxis")):
        if isinstance(item, dict) and item.get("type") == "category":
            y_is_category = True
    for item in _as_list(options.get("xAxis")):
        if isinstance(item, dict) and item.get("type") == "value":
            x_is_value = True
    return y_is_category and x_is_value


def _lift_font(style, minimum):
    """Raise fontSize when missing or below the readable floor. Leaves larger sizes alone."""
    if not isinstance(style, dict):
        return False
    current = style.get("fontSize")
    if current is None or (isinstance(current, (int, float)) and current < minimum):
        style["fontSize"] = minimum
        return True
    return False


def _style_title(title):
    for item in _as_list(title):
        if not isinstance(item, dict):
            continue
        text_style = item.setdefault("textStyle", {})
        if isinstance(text_style, dict):
            text_style.setdefault("fontFamily", _FONT)
            text_style.setdefault("color", _TITLE_COLOR)
            text_style.setdefault("fontWeight", 600)
            _lift_font(text_style, _TITLE_MIN_SIZE)
        sub_style = item.setdefault("subtextStyle", {})
        if isinstance(sub_style, dict):
            sub_style.setdefault("color", _MUTED)
            sub_style.setdefault("fontFamily", _FONT)
            _lift_font(sub_style, _SUBTITLE_MIN_SIZE)


def _style_legend(legend):
    for item in _as_list(legend):
        if not isinstance(item, dict):
            continue
        item.setdefault("icon", "roundRect")
        item.setdefault("itemWidth", 12)
        item.setdefault("itemHeight", 8)
        item.setdefault("itemGap", 14)
        text_style = item.setdefault("textStyle", {})
        if isinstance(text_style, dict):
            text_style.setdefault("color", _MUTED)
            text_style.setdefault("fontFamily", _FONT)
            _lift_font(text_style, _LABEL_MIN_SIZE)


def _style_tooltip(tooltip):
    for item in _as_list(tooltip):
        if not isinstance(item, dict):
            continue
        item.setdefault("backgroundColor", _TOOLTIP_BG)
        item.setdefault("borderColor", _TOOLTIP_BORDER)
        item.setdefault("borderWidth", 1)
        item.setdefault("extraCssText", "border-radius:10px;box-shadow:0 8px 24px rgba(15,23,42,0.12);")
        text_style = item.setdefault("textStyle", {})
        if isinstance(text_style, dict):
            text_style.setdefault("color", "#334155")
            text_style.setdefault("fontFamily", _FONT)
            _lift_font(text_style, _LABEL_MIN_SIZE)


def _style_axes(axis, is_value=False):
    for item in _as_list(axis):
        if not isinstance(item, dict):
            continue
        item.setdefault("axisTick", {}).setdefault("show", False)
        axis_line = item.setdefault("axisLine", {})
        if isinstance(axis_line, dict):
            axis_line.setdefault("show", False)
            line_style = axis_line.setdefault("lineStyle", {})
            if isinstance(line_style, dict):
                line_style.setdefault("color", _AXIS)
        split_line = item.setdefault("splitLine", {})
        if isinstance(split_line, dict):
            if is_value:
                split_line.setdefault("show", True)
            line_style = split_line.setdefault("lineStyle", {})
            if isinstance(line_style, dict):
                line_style.setdefault("color", _GRID)
                line_style.setdefault("type", "solid")
        axis_label = item.setdefault("axisLabel", {})
        if isinstance(axis_label, dict):
            axis_label.setdefault("color", _MUTED)
            axis_label.setdefault("fontFamily", _FONT)
            lifted = _lift_font(axis_label, _LABEL_MIN_SIZE)
            if lifted and axis_label.get("rotate"):
                axis_label.setdefault("hideOverlap", True)
                axis_label.setdefault("overflow", "truncate")
                axis_label.setdefault("ellipsis", "...")
                axis_label.setdefault("width", 72)
        name_style = item.setdefault("nameTextStyle", {})
        if isinstance(name_style, dict):
            name_style.setdefault("color", _MUTED)
            name_style.setdefault("fontFamily", _FONT)
            _lift_font(name_style, _LABEL_MIN_SIZE)


def _style_series(series, horizontal):
    if not isinstance(series, dict):
        return
    stype = series.get("type")
    if stype == "bar":
        _style_bar(series, horizontal)
    elif stype == "line":
        _style_line(series)
    elif stype == "pie":
        _style_pie(series)
    elif stype == "treemap":
        _style_treemap(series)
    elif stype == "scatter":
        _style_scatter(series)
    if stype != "gauge" and isinstance(series.get("label"), dict):
        _lift_font(series["label"], _LABEL_MIN_SIZE)


def _numeric_values(data):
    values = []
    for item in data or []:
        if isinstance(item, bool):
            continue
        if isinstance(item, (int, float)):
            values.append(item)
        elif isinstance(item, dict):
            raw = item.get("value", item.get("y"))
            if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                values.append(raw)
            elif isinstance(raw, list) and raw:
                last = raw[-1]
                if isinstance(last, (int, float)) and not isinstance(last, bool):
                    values.append(last)
    return values


def _series_grows_negative(series):
    """True when most non-zero values sit below / left of the origin."""
    values = [v for v in _numeric_values(series.get("data")) if v != 0]
    if not values:
        return False
    negatives = 0
    for value in values:
        if value < 0:
            negatives += 1
    return negatives > len(values) / 2.0


def _bar_end_radius(series, horizontal):
    """Round the free end of the bar, including negative series that grow away from zero."""
    return _free_end_radius(_series_grows_negative(series), horizontal)


def _free_end_radius(negative, horizontal):
    if horizontal:
        return [4, 0, 0, 4] if negative else [0, 6, 6, 0]
    return [0, 0, 4, 4] if negative else [6, 6, 0, 0]


def _as_number(item):
    if isinstance(item, bool) or item is None:
        return None
    if isinstance(item, (int, float)):
        if item != item:
            return None
        return item
    if isinstance(item, str):
        try:
            return float(item)
        except ValueError:
            return None
    if isinstance(item, dict):
        if "value" in item:
            return _as_number(item.get("value"))
        return None
    if isinstance(item, (list, tuple)) and item:
        return _as_number(item[-1])
    return None


_STACK_SQUARE = [0, 0, 0, 0]


def _point_value(series, index):
    data = series.get("data")
    if not isinstance(data, list) or index >= len(data):
        return None
    return _as_number(data[index])


def _paint_point_radius(series, index, radius):
    """Write ``borderRadius`` on one data item, keeping any existing fields."""
    data = series.get("data")
    if not isinstance(data, list) or index >= len(data):
        return
    item = data[index]
    if isinstance(item, dict):
        style = item.get("itemStyle")
        if not isinstance(style, dict):
            style = {}
            item["itemStyle"] = style
        style["borderRadius"] = radius
        return
    data[index] = {"value": item, "itemStyle": {"borderRadius": radius}}


def _round_stack_ends(series_list, horizontal):
    """Round only the outer segment of a stack, as in ECharts' bar-stack-borderRadius example.

    Each category remembers the last positive segment and the last negative
    segment. Those two points get the free-end radius. Every other segment is
    written as square so a canvas theme cannot round the joins.
    """
    groups = {}
    for series in series_list:
        if not isinstance(series, dict) or series.get("type") != "bar":
            continue
        stack = series.get("stack")
        if not stack:
            continue
        groups.setdefault(stack, []).append(series)

    for group in groups.values():
        length = 0
        for series in group:
            data = series.get("data")
            if isinstance(data, list):
                length = max(length, len(data))
            item = series.setdefault("itemStyle", {})
            if isinstance(item, dict):
                item["borderRadius"] = 0
        for index in range(length):
            positive_end = None
            negative_end = None
            for series in group:
                value = _point_value(series, index)
                if value is None or value == 0:
                    continue
                if value > 0:
                    positive_end = series
                else:
                    negative_end = series
            for series in group:
                if _point_value(series, index) is None:
                    continue
                if series is positive_end:
                    radius = _free_end_radius(False, horizontal)
                elif series is negative_end:
                    radius = _free_end_radius(True, horizontal)
                else:
                    radius = _STACK_SQUARE
                _paint_point_radius(series, index, radius)


def _style_bar(series, horizontal):
    negative = _series_grows_negative(series)
    if not horizontal and not negative:
        series.setdefault("barMaxWidth", 36)
    item = series.setdefault("itemStyle", {})
    if isinstance(item, dict) and not series.get("stack"):
        item.setdefault("borderRadius", _bar_end_radius(series, horizontal))
    emphasis = series.setdefault("emphasis", {})
    if isinstance(emphasis, dict):
        emphasis_item = emphasis.setdefault("itemStyle", {})
        if isinstance(emphasis_item, dict):
            emphasis_item.setdefault("shadowBlur", 8)
            emphasis_item.setdefault("shadowColor", "rgba(15,23,42,0.16)")


def _style_line(series):
    series.setdefault("smooth", 0.4)
    series.setdefault("symbol", "circle")
    series.setdefault("symbolSize", 6)
    line_style = series.setdefault("lineStyle", {})
    if isinstance(line_style, dict):
        line_style.setdefault("width", 2.5)
        line_style.setdefault("cap", "round")
        line_style.setdefault("join", "round")


def _style_pie(series):
    item = series.setdefault("itemStyle", {})
    if isinstance(item, dict):
        item.setdefault("borderRadius", 6)
        item.setdefault("borderColor", _SLICE_GAP)
        item.setdefault("borderWidth", 2)


def _style_treemap(series):
    item = series.setdefault("itemStyle", {})
    if isinstance(item, dict):
        item.setdefault("borderRadius", 6)
        item.setdefault("borderColor", _SLICE_GAP)
        item.setdefault("borderWidth", 2)
        item.setdefault("gapWidth", 4)


def _style_scatter(series):
    series.setdefault("symbol", "circle")
    item = series.setdefault("itemStyle", {})
    if isinstance(item, dict):
        item.setdefault("opacity", 0.78)
        item.setdefault("borderWidth", 1)
        item.setdefault("borderColor", "rgba(255,255,255,0.7)")
