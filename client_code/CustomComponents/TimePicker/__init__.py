from ._anvil_designer import TimePickerTemplate


_CSS_ID = "cf-timepicker-css"
_CSS = """
.cf-tp { position: relative; width: 100%; font: inherit; }
.cf-tp-field { position: relative; display: flex; align-items: center; }
.cf-tp-input {
  width: 100%; box-sizing: border-box; font: inherit; font-variant-numeric: tabular-nums;
  padding: 7px 34px 7px 10px; border: 1px solid var(--cf-tp-line, #d6dde8); border-radius: 8px;
  background: var(--cf-tp-surface, #fff); color: var(--cf-tp-ink, #142033); line-height: 1.3;
}
.cf-tp-input:focus { outline: none; border-color: var(--cf-tp-accent, #1e3a5f); box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.12); }
.cf-tp-input:disabled { opacity: 0.55; cursor: not-allowed; }
.cf-tp.is-invalid .cf-tp-input { border-color: #b91c1c; }
.cf-tp-icon { position: absolute; right: 10px; width: 16px; height: 16px; color: var(--cf-tp-muted, #64748b); pointer-events: none; }
.cf-tp-panel {
  display: none; position: fixed; z-index: 2000;
  grid-template-columns: 1fr 1fr; width: 168px; height: 232px; overflow: hidden; font-family: Montserrat, system-ui, sans-serif;
  background: var(--cf-tp-surface, #fff); border: 1px solid var(--cf-tp-line, #d6dde8); border-radius: 10px;
  box-shadow: 0 10px 30px rgba(20, 32, 51, 0.18);
}
.cf-tp-panel.is-open { display: grid; }
.cf-tp-col { position: relative; overflow-y: auto; padding: 4px 0; scrollbar-width: thin; }
.cf-tp-col + .cf-tp-col { border-left: 1px solid var(--cf-tp-line, #d6dde8); }
.cf-tp-panel .cf-tp-col button.cf-tp-opt {
  all: unset; box-sizing: border-box; display: block; width: 100%; padding: 5px 0; cursor: pointer;
  font-family: inherit; font-size: 13px; line-height: 1.4; font-variant-numeric: tabular-nums;
  color: var(--cf-tp-ink, #142033); text-align: center;
}
.cf-tp-panel .cf-tp-col button.cf-tp-opt:hover { background: var(--cf-tp-hover, #eef2f7); }
.cf-tp-panel .cf-tp-col button.cf-tp-opt.is-on { background: var(--cf-tp-accent, #1e3a5f); color: #fff; font-weight: 600; }
.cf-tp-panel .cf-tp-col button.cf-tp-opt:disabled { color: var(--cf-tp-off, #c3ccd8); cursor: default; background: none; }
.ipac-dark .cf-tp, .craftify-theme-dark .cf-tp, [data-theme=dark] .cf-tp,
.ipac-dark .cf-tp-panel, .craftify-theme-dark .cf-tp-panel, [data-theme=dark] .cf-tp-panel {
  --cf-tp-surface: #182233; --cf-tp-ink: #e6edf7; --cf-tp-line: #2c3a50; --cf-tp-hover: #22314a; --cf-tp-muted: #94a3b8; --cf-tp-accent: #3b82f6; --cf-tp-off: #4a5a72;
}
"""
_ICON = (
    '<svg class="cf-tp-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
    '<path d="M12 7v5l3 2"/></svg>'
)


def parse_time(text):
    """'9', '930', '9:30', '09.30' -> '09:30'. Blank -> ''. Anything else -> None."""
    raw = str(text or "").strip().replace(".", ":").replace(" ", "")
    if not raw:
        return ""
    if ":" in raw:
        hour, _, minute = raw.partition(":")
    elif raw.isdigit() and len(raw) <= 2:
        hour, minute = raw, "0"
    elif raw.isdigit() and len(raw) in (3, 4):
        hour, minute = raw[:-2], raw[-2:]
    else:
        return None
    if not (hour.isdigit() and minute.isdigit()) or len(minute) > 2:
        return None
    if int(hour) > 23 or int(minute) > 59:
        return None
    return "%02d:%02d" % (int(hour), int(minute))


def _inject_css():
    from anvil.js.window import document
    if document.getElementById(_CSS_ID) is None:
        style = document.createElement("style")
        style.id = _CSS_ID
        style.textContent = _CSS
        document.head.appendChild(style)


class TimePicker(TimePickerTemplate):
    """Time of day as 'HH:MM'. Type it (930, 9:30) or pick an hour, then a minute, from the list."""

    def __init__(self, **properties):
        time = properties.pop("time", "")
        placeholder = properties.pop("placeholder", "HH:MM")
        minute_step = properties.pop("minute_step", 5)
        min_time = properties.pop("min_time", "")
        max_time = properties.pop("max_time", "")
        enabled = properties.pop("enabled", True)
        self._time = ""
        self._step = 5
        self._min = ""
        self._max = ""
        self._listening = False
        self.init_components(**properties)
        _inject_css()
        root = self.dom_nodes["root"]
        root.innerHTML = (
            '<div class="cf-tp-field"><input class="cf-tp-input" type="text" inputmode="numeric" autocomplete="off" maxlength="5">%s</div>'
            '<div class="cf-tp-panel" role="listbox"><div class="cf-tp-col" data-col="h"></div><div class="cf-tp-col" data-col="m"></div></div>'
        ) % _ICON
        self._root = root
        self._input = root.querySelector(".cf-tp-input")
        self._panel = root.querySelector(".cf-tp-panel")
        self._input.addEventListener("focus", self._on_focus)
        self._input.addEventListener("click", self._on_focus)
        self._input.addEventListener("keydown", self._on_key)
        self._input.addEventListener("blur", self._on_blur)
        self._panel.addEventListener("mousedown", self._keep_focus)
        self._panel.addEventListener("click", self._on_pick)
        self.minute_step = minute_step
        self.min_time = min_time
        self.max_time = max_time
        self.placeholder = placeholder
        self.enabled = enabled
        self.time = time

    # Properties

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        parsed = parse_time(value)
        self._time = parsed or ""
        self._input.value = self._time
        self._root.classList.remove("is-invalid")
        self._render()

    @property
    def placeholder(self):
        return self._input.placeholder or ""

    @placeholder.setter
    def placeholder(self, value):
        self._input.placeholder = value or ""

    @property
    def minute_step(self):
        return self._step

    @minute_step.setter
    def minute_step(self, value):
        try:
            step = int(value or 5)
        except (TypeError, ValueError):
            step = 5
        self._step = step if 1 <= step <= 30 else 5
        self._render()

    @property
    def min_time(self):
        return self._min

    @min_time.setter
    def min_time(self, value):
        self._min = parse_time(value) or ""
        self._render()

    @property
    def max_time(self):
        return self._max

    @max_time.setter
    def max_time(self, value):
        self._max = parse_time(value) or ""
        self._render()

    @property
    def enabled(self):
        return not self._input.disabled

    @enabled.setter
    def enabled(self, value):
        self._input.disabled = not value
        if not value:
            self._close()

    # Lifecycle

    def form_show(self, **event_args):
        if not self._listening:
            from anvil.js.window import document
            document.addEventListener("mousedown", self._on_outside)
            self._listening = True

    def form_hide(self, **event_args):
        if self._listening:
            from anvil.js.window import document
            document.removeEventListener("mousedown", self._on_outside)
            self._listening = False
        self._close()
        self._root.appendChild(self._panel)

    # Behaviour

    def _allowed(self, stamp):
        return (not self._min or stamp >= self._min) and (not self._max or stamp <= self._max)

    def _set(self, value):
        if value == self._time:
            self._input.value = value
            return
        self._time = value
        self._input.value = value
        self._root.classList.remove("is-invalid")
        self._render()
        self.raise_event("change")

    def _commit_typed(self):
        parsed = parse_time(self._input.value)
        if parsed is None or (parsed and not self._allowed(parsed)):
            self._root.classList.add("is-invalid")
            return False
        self._set(parsed)
        return True

    def _render(self):
        panel = getattr(self, "_panel", None)
        if panel is None:
            return
        hour = self._time[:2] if self._time else ""
        minute = self._time[3:] if self._time else ""
        hours = []
        for value in range(24):
            label = "%02d" % value
            usable = any(self._allowed("%s:%02d" % (label, m)) for m in range(0, 60, self._step)) or self._allowed(label + ":59")
            hours.append('<button type="button" data-h="%s" class="cf-tp-opt %s"%s>%s</button>'
                         % (label, "is-on" if label == hour else "", "" if usable else " disabled", label))
        minutes = []
        for value in range(0, 60, self._step):
            label = "%02d" % value
            usable = not hour or self._allowed("%s:%s" % (hour, label))
            minutes.append('<button type="button" data-m="%s" class="cf-tp-opt %s"%s>%s</button>'
                           % (label, "is-on" if label == minute else "", "" if usable else " disabled", label))
        panel.querySelector('[data-col="h"]').innerHTML = "".join(hours)
        panel.querySelector('[data-col="m"]').innerHTML = "".join(minutes)

    def _open(self):
        if not self.enabled or self._panel.classList.contains("is-open"):
            return
        from anvil.js.window import document, window
        self._render()
        document.body.appendChild(self._panel)
        box = self._input.getBoundingClientRect()
        height = 232
        below = window.innerHeight - box.bottom
        top = box.bottom + 4 if (below >= height + 8 or box.top < below) else box.top - height - 4
        left = min(box.left, window.innerWidth - 176)
        self._panel.style.top = "%spx" % max(4, top)
        self._panel.style.left = "%spx" % max(4, left)
        self._panel.classList.add("is-open")
        self._root.classList.add("is-open")
        window.addEventListener("scroll", self._on_scroll, True)
        for node in self._panel.querySelectorAll("button.is-on"):
            column = node.parentElement
            column.scrollTop = max(0, node.offsetTop - column.clientHeight / 2 + node.offsetHeight / 2)

    def _close(self):
        if not self._panel.classList.contains("is-open"):
            return
        from anvil.js.window import window
        self._panel.classList.remove("is-open")
        self._root.classList.remove("is-open")
        window.removeEventListener("scroll", self._on_scroll, True)

    def _on_scroll(self, event):
        if not self._panel.contains(event.target):
            self._close()

    def _on_focus(self, event):
        self._open()

    def _keep_focus(self, event):
        event.preventDefault()

    def _on_blur(self, event):
        self._commit_typed()
        self._close()

    def _on_outside(self, event):
        if not self._root.contains(event.target) and not self._panel.contains(event.target):
            self._close()

    def _on_key(self, event):
        key = event.key
        if key == "Enter":
            event.preventDefault()
            if self._commit_typed():
                self._close()
        elif key == "Escape":
            self._input.value = self._time
            self._root.classList.remove("is-invalid")
            self._close()
        elif key == "ArrowDown":
            self._open()

    def _on_pick(self, event):
        target = event.target
        if target is None or target.tagName != "BUTTON" or target.disabled:
            return
        hour = target.getAttribute("data-h")
        minute = target.getAttribute("data-m")
        if hour:
            current = self._time[3:] if self._time else "00"
            if not self._allowed("%s:%s" % (hour, current)):
                current = next(("%02d" % m for m in range(0, 60, self._step) if self._allowed("%s:%02d" % (hour, m))), "00")
            self._set("%s:%s" % (hour, current))
        elif minute:
            hour_now = self._time[:2] if self._time else "00"
            self._set("%s:%s" % (hour_now, minute))
            self._close()
