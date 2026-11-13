"""Craftify Tabulator: labeled column filters, toolbar, and footer export."""

from anvil.js import get_dom_node, window

TABLE_ROLE = "craftify-table"
NO_AUTOFILL = {"elementAttributes": {"autocomplete": "off", "name": "cf-table-filter"}}
SEARCH_DELAY_MS = 400
DATE_FIELDS = frozenset({"start", "end", "received", "due", "stopped", "restarted"})
COMPARE_FIELDS = frozenset({"hours"})
DATE_FILTER_HINT = "Any date"
COMPARE_OPS = (("≥", ">="), ("≤", "<="), (">", ">"), ("<", "<"), ("=", "="))
FILTER_DELAY_MS = 450
MONTH_LABELS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _at_least(header_val, row_val, row_data, **params):
    if header_val is None or str(header_val).strip() == "":
        return True
    try:
        return float(row_val) >= float(header_val)
    except (TypeError, ValueError):
        return False


def filter_params(placeholder=""):
    attrs = dict(NO_AUTOFILL.get("elementAttributes") or {})
    if placeholder:
        attrs["placeholder"] = placeholder
    return {"elementAttributes": attrs}


def stamp_column(column, *, kind="text", choices=None):
    """Craftify filter row: placeholder text and ``cf-filter-col`` styling."""
    column = dict(column)
    if column.get("header_filter") is False or column.get("field") == "edit":
        return column
    classes = [token for token in (column.get("css_class") or "").split() if token]
    if "cf-filter-col" not in classes:
        classes.append("cf-filter-col")
    column["css_class"] = " ".join(classes)

    existing = column.get("header_filter")
    if existing is False:
        return column

    if kind == "list" or existing == "list":
        column["header_filter"] = "list"
        params = dict(NO_AUTOFILL)
        params.update({"values": choices if choices is not None else True, "clearable": True, "sort": "asc"})
        column["header_filter_params"] = column.get("header_filter_params") or params
        return column

    if kind == "compare":
        column["header_filter"] = "input"
        column["header_filter_params"] = filter_params("")
        if "cf-filter-compare" not in classes:
            classes.append("cf-filter-compare")
        column["css_class"] = " ".join(classes)
        return column

    if kind == "number":
        column["header_filter"] = "input"
        column["header_filter_params"] = filter_params("At least...")
        if not column.get("header_filter_func"):
            column["header_filter_func"] = _at_least
        return column

    if kind == "date":
        column["header_filter"] = "input"
        column["header_filter_placeholder"] = DATE_FILTER_HINT
        column["header_filter_params"] = filter_params(DATE_FILTER_HINT)
        if "cf-filter-date" not in classes:
            classes.append("cf-filter-date")
        column["css_class"] = " ".join(classes)
        return column

    column["header_filter"] = existing if existing not in (None, True) else "input"
    if column["header_filter"] is True:
        column["header_filter"] = "input"
    column["header_filter_params"] = filter_params("Contains...")
    return column


def stamp_columns(columns, field_hints=None):
    """Apply :func:`stamp_column` using list ``capabilities`` (filter, sort, choices)."""
    hints = field_hints or {}
    choices = hints.get("choices") or {}
    filterable = set(hints.get("filter") or [])

    stamped = []
    for column in columns:
        field = column.get("field")
        if column.get("header_filter") is False or field in ("edit", "_row"):
            stamped.append(column)
            continue
        if field not in filterable and column.get("header_filter") not in (True, "input", "list"):
            if column.get("header_filter"):
                stamped.append(stamp_column(column, kind="text"))
            else:
                stamped.append(column)
            continue
        if field in choices:
            kind = "list"
        elif field in DATE_FIELDS or column.get("header_filter_placeholder"):
            kind = "date"
        elif field in COMPARE_FIELDS or column.get("filter_kind") == "compare":
            kind = "compare"
        elif column.get("sorter") == "number":
            kind = "number"
        else:
            kind = "text"
        stamped.append(stamp_column(column, kind=kind, choices=choices.get(field)))
    return stamped


def apply_table_theme(table):
    """Tabulator ``cssClass`` so filter-row chrome applies before ``table_built``."""
    opts = dict(getattr(table, "options", None) or {})
    role = opts.get("css_class") or ""
    tokens = [token for token in (role.split() if isinstance(role, str) else list(role or [])) if token]
    if TABLE_ROLE not in tokens:
        tokens.append(TABLE_ROLE)
    opts["css_class"] = " ".join(tokens)
    table.options = opts


def _table_built_hooks(table):
    hooks = getattr(table, "_cf_table_built_hooks", None)
    if hooks is None:
        hooks = []
        table._cf_table_built_hooks = hooks

        def on_built(**event_args):
            for hook in list(hooks):
                try:
                    hook(**event_args)
                except Exception:
                    pass

        table.set_event_handler("table_built", on_built)
        try:
            if table.initialized:
                on_built()
        except Exception:
            pass
    return hooks


def _register_table_built(table, hook):
    _table_built_hooks(table).append(hook)
    try:
        if table.initialized:
            hook()
    except Exception:
        pass


def _short_iso(iso):
    if not iso or len(iso) < 10:
        return ""
    try:
        year, month, day = iso.split("-", 2)
        return "%d %s %s" % (int(day), MONTH_LABELS[int(month) - 1], year)
    except Exception:
        return iso


_PUSH_HEADER_FILTER = None


def _notify_header_filter(inp):
    """Tabulator applies a header filter on ``keyup`` / ``search`` of its own input."""
    global _PUSH_HEADER_FILTER
    if _PUSH_HEADER_FILTER is None:
        _PUSH_HEADER_FILTER = window.Function(
            "input",
            """
            input.dispatchEvent(new Event("keyup", {bubbles: true}));
            input.dispatchEvent(new Event("search", {bubbles: true}));
            input.dispatchEvent(new Event("change", {bubbles: true}));
            """,
        )
    try:
        _PUSH_HEADER_FILTER(inp)
    except Exception:
        pass


def _date_range_label(start_iso, end_iso):
    if start_iso and end_iso:
        return "%s – %s" % (_short_iso(start_iso), _short_iso(end_iso))
    if start_iso:
        return "From %s" % _short_iso(start_iso)
    if end_iso:
        return "Until %s" % _short_iso(end_iso)
    return DATE_FILTER_HINT


def reset_date_range_ui(root):
    if root is None:
        return
    try:
        blocks = root.querySelectorAll(".cf-date-range")
    except Exception:
        return
    for block in blocks:
        try:
            token = block.getAttribute("data-cf-range")
            panel = window.document.querySelector('.cf-date-range-panel[data-cf-range="%s"]' % token) if token else None
            if panel is not None:
                for sel in (".cf-date-range-from", ".cf-date-range-to"):
                    field = panel.querySelector(sel)
                    if field is not None:
                        field.value = ""
                panel.setAttribute("hidden", "")
            hidden = block.parentElement.querySelector(".cf-date-range-value") if block.parentElement is not None else None
            if hidden is not None:
                hidden.value = ""
            label = block.querySelector(".cf-date-range-label")
            if label is not None:
                label.textContent = DATE_FILTER_HINT
        except Exception:
            pass


def _build_date_range_filter(wrapper, hidden_input):
    doc = window.document
    if wrapper.querySelector(".cf-date-range"):
        return
    hidden_input.classList.add("cf-date-range-value")
    try:
        hidden_input.tabIndex = -1
    except Exception:
        pass

    block = doc.createElement("div")
    block.className = "cf-date-range"

    trigger = doc.createElement("button")
    trigger.type = "button"
    trigger.className = "cf-date-range-trigger"
    trigger.innerHTML = '<i class="fa-regular fa-calendar" aria-hidden="true"></i><span class="cf-date-range-label">%s</span>' % DATE_FILTER_HINT

    panel = doc.createElement("div")
    panel.className = "cf-date-range-panel"
    panel.setAttribute("hidden", "")
    token = "cf-%s" % id(block)
    block.setAttribute("data-cf-range", token)
    panel.setAttribute("data-cf-range", token)

    def row(caption, css_class):
        row_el = doc.createElement("label")
        row_el.className = "cf-date-range-row"
        cap = doc.createElement("span")
        cap.className = "cf-date-range-caption"
        cap.textContent = caption
        field = doc.createElement("input")
        field.type = "date"
        field.className = css_class
        row_el.appendChild(cap)
        row_el.appendChild(field)
        return row_el, field

    from_row, from_input = row("From", "cf-date-range-from")
    to_row, to_input = row("To", "cf-date-range-to")
    panel.appendChild(from_row)
    panel.appendChild(to_row)

    actions = doc.createElement("div")
    actions.className = "cf-date-range-actions"
    clear = doc.createElement("button")
    clear.type = "button"
    clear.className = "cf-date-range-clear"
    clear.textContent = "Clear"
    actions.appendChild(clear)
    panel.appendChild(actions)

    def place_panel():
        rect = trigger.getBoundingClientRect()
        width = max(260, rect.width)
        left = rect.left
        if left + width > window.innerWidth - 8:
            left = max(8, window.innerWidth - width - 8)
        top = rect.bottom + 6
        if top + 180 > window.innerHeight:
            top = max(8, rect.top - 186)
        panel.style.left = "%dpx" % int(left)
        panel.style.top = "%dpx" % int(top)
        panel.style.width = "%dpx" % int(width)

    def close_panel():
        panel.setAttribute("hidden", "")

    def toggle(event=None):
        if event is not None:
            event.preventDefault()
            event.stopPropagation()
        opening = panel.hasAttribute("hidden")
        if opening:
            doc.body.appendChild(panel)
            panel.removeAttribute("hidden")
            place_panel()
        else:
            close_panel()

    def on_outside(event):
        if panel.hasAttribute("hidden"):
            return
        try:
            target = event.target
            if block.contains(target) or panel.contains(target):
                return
            close_panel()
        except Exception:
            pass

    def keep_open(event):
        try:
            event.stopPropagation()
        except Exception:
            pass

    def clear_range(event):
        event.preventDefault()
        event.stopPropagation()
        from_input.value = ""
        to_input.value = ""
        _apply_date_range_block(block)

    clear.addEventListener("click", clear_range)
    trigger.addEventListener("click", toggle)
    panel.addEventListener("click", keep_open)
    doc.addEventListener("click", on_outside)
    window.addEventListener("resize", lambda event: place_panel() if not panel.hasAttribute("hidden") else None)

    clear = doc.createElement("button")
    clear.type = "button"
    clear.className = "cf-filter-x"
    clear.setAttribute("hidden", "")
    clear.setAttribute("aria-label", "Clear")
    clear.textContent = "\u00d7"

    def clear_range_x(event):
        event.preventDefault()
        event.stopPropagation()
        from_input.value = ""
        to_input.value = ""
        _apply_date_range_block(block)

    clear.addEventListener("click", clear_range_x)
    block.appendChild(trigger)
    block.appendChild(clear)
    wrapper.insertBefore(block, hidden_input)


def _apply_date_range_block(block):
    try:
        token = block.getAttribute("data-cf-range")
        panel = window.document.querySelector('.cf-date-range-panel[data-cf-range="%s"]' % token) if token else None
        from_input = panel.querySelector(".cf-date-range-from") if panel is not None else None
        to_input = panel.querySelector(".cf-date-range-to") if panel is not None else None
        wrapper = block.parentElement
        hidden = wrapper.querySelector("input.cf-date-range-value") if wrapper is not None else None
        if hidden is None or from_input is None or to_input is None:
            return
        start_iso = (from_input.value or "").strip()
        end_iso = (to_input.value or "").strip()
        if start_iso and end_iso:
            hidden.value = "%s..%s" % (start_iso, end_iso)
        elif start_iso:
            hidden.value = start_iso
        elif end_iso:
            hidden.value = end_iso
        else:
            hidden.value = ""
        label = block.querySelector(".cf-date-range-label")
        if label is not None:
            label.textContent = _date_range_label(start_iso, end_iso)
        clear = block.querySelector(".cf-filter-x")
        if clear is not None:
            if hidden.value:
                clear.removeAttribute("hidden")
            else:
                clear.setAttribute("hidden", "")
        _notify_header_filter(hidden)
    except Exception:
        pass


def _on_date_field_change(event):
    target = event.target
    try:
        classes = target.classList
    except Exception:
        return
    if classes is None or not (classes.contains("cf-date-range-from") or classes.contains("cf-date-range-to")):
        return
    block = target.closest(".cf-date-range")
    if block is None:
        panel = target.closest(".cf-date-range-panel")
        token = panel.getAttribute("data-cf-range") if panel is not None else None
        block = window.document.querySelector('.cf-date-range[data-cf-range="%s"]' % token) if token else None
    if block is None:
        return
    _apply_date_range_block(block)


_DATE_RANGE_LISTENING = False


def _listen_for_date_ranges():
    """The popover lives on ``document.body``, so the table never sees its ``change`` events."""
    global _DATE_RANGE_LISTENING
    if _DATE_RANGE_LISTENING:
        return
    _DATE_RANGE_LISTENING = True
    doc = window.document
    doc.addEventListener("change", _on_date_field_change, True)
    doc.addEventListener("input", _on_date_field_change, True)


def attach_date_range_filters(table):
    _listen_for_date_ranges()

    def on_built(**event_args):
        _, root = _tabulator_root(table)
        if root is None:
            return
        try:
            wrappers = root.querySelectorAll(".tabulator-col.cf-filter-date .tabulator-header-filter")
        except Exception:
            return
        for wrapper in wrappers:
            try:
                hidden = wrapper.querySelector("input")
                if hidden is None:
                    continue
                _build_date_range_filter(wrapper, hidden)
            except Exception:
                pass

    _register_table_built(table, on_built)


def _tabulator_root(table):
    try:
        host = get_dom_node(table)
    except Exception:
        return None, None
    if host is None:
        return None, None
    root = host
    if hasattr(host, "querySelector") and not host.classList.contains("tabulator"):
        found = host.querySelector(".tabulator")
        if found is not None:
            root = found
    return host, root


def attach_excel_download(table, on_click, title="Download Excel"):
    def on_built(**event_args):
        _, root = _tabulator_root(table)
        if root is None:
            return
        footer = root.querySelector(".tabulator-footer .tabulator-footer-contents")
        if footer is None:
            footer = root.querySelector(".tabulator-footer")
        if footer is None or footer.querySelector(".cy-export-excel"):
            return
        doc = window.document
        wrap = doc.createElement("div")
        wrap.className = "ipac-tabulator-footer-actions"
        button = doc.createElement("button")
        button.type = "button"
        button.className = "ipac-footer-btn cy-export-excel"
        button.setAttribute("title", title)
        button.setAttribute("aria-label", title)
        button.innerHTML = '<i class="fa-solid fa-download" aria-hidden="true"></i>'

        def clicked(event):
            event.preventDefault()
            event.stopPropagation()
            on_click()

        button.addEventListener("click", clicked)
        wrap.appendChild(button)
        footer.insertBefore(wrap, footer.firstChild)

    _register_table_built(table, on_built)


def _build_compare_filter(wrapper, hidden_input):
    doc = window.document
    if wrapper.querySelector(".cf-compare"):
        return
    hidden_input.classList.add("cf-compare-value")
    try:
        hidden_input.tabIndex = -1
    except Exception:
        pass
    block = doc.createElement("div")
    block.className = "cf-compare"
    select = doc.createElement("select")
    select.className = "cf-compare-op"
    for label, op in COMPARE_OPS:
        option = doc.createElement("option")
        option.value = op
        option.textContent = label
        select.appendChild(option)
    number = doc.createElement("input")
    number.type = "number"
    number.step = "any"
    number.className = "cf-compare-num"
    number.setAttribute("placeholder", "")
    number.setAttribute("autocomplete", "off")

    def sync(_event=None):
        raw = (number.value or "").strip()
        hidden_input.value = ("%s %s" % (select.value, raw)) if raw else ""
        _notify_header_filter(hidden_input)

    select.addEventListener("change", sync)
    number.addEventListener("input", sync)
    block.appendChild(select)
    block.appendChild(number)
    wrapper.insertBefore(block, hidden_input)


def attach_compare_filters(table):
    def on_built(**event_args):
        _, root = _tabulator_root(table)
        if root is None:
            return
        try:
            wrappers = root.querySelectorAll(".tabulator-col.cf-filter-compare .tabulator-header-filter")
        except Exception:
            return
        for wrapper in wrappers:
            try:
                hidden = wrapper.querySelector("input")
                if hidden is None:
                    continue
                _build_compare_filter(wrapper, hidden)
            except Exception:
                pass

    _register_table_built(table, on_built)


def attach_filter_clears(table):
    """An × at the right of each text or number filter."""

    def on_built(**event_args):
        _, root = _tabulator_root(table)
        if root is None:
            return
        try:
            inputs = root.querySelectorAll(".tabulator-header-filter input, .tabulator-header-filter select")
        except Exception:
            return
        doc = window.document
        for field in inputs:
            try:
                if (field.tagName or "").lower() == "select":
                    continue
                kind = (field.getAttribute("type") or "").lower()
                if kind in ("hidden",) or field.classList.contains("cf-date-range-value") or field.classList.contains("cf-compare-value"):
                    continue
                if field.classList.contains("cf-compare-op") or field.classList.contains("cf-date-range-from") or field.classList.contains("cf-date-range-to"):
                    continue
                host = field.parentElement
                if host is None or host.querySelector(".cf-filter-x"):
                    continue
                button = doc.createElement("button")
                button.type = "button"
                button.className = "cf-filter-x"
                button.setAttribute("aria-label", "Clear")
                button.textContent = "\u00d7"
                if not (field.value or "").strip():
                    button.setAttribute("hidden", "")

                def toggle(event, control=field, mark=button):
                    if (control.value or "").strip():
                        mark.removeAttribute("hidden")
                    else:
                        mark.setAttribute("hidden", "")

                def clear(event, control=field, mark=button):
                    event.preventDefault()
                    event.stopPropagation()
                    control.value = ""
                    mark.setAttribute("hidden", "")
                    _notify_header_filter(control)

                field.addEventListener("input", toggle)
                field.addEventListener("keyup", toggle)
                field.addEventListener("change", toggle)
                button.addEventListener("click", clear)
                host.appendChild(button)
            except Exception:
                pass

    _register_table_built(table, on_built)


def attach_toolbar(table, *, remote=False, on_clear=None, search_placeholder="Search rows…"):
    """Toolbar above the grid for local search. Each filter clears itself."""

    def on_built(**event_args):
        host, root = _tabulator_root(table)
        if root is None:
            return
        if root.querySelector(".cf-table-toolbar"):
            return
        root.classList.add("craftify-table")
        try:
            table.role = TABLE_ROLE
        except Exception:
            pass
        if remote:
            return

        doc = window.document
        toolbar = doc.createElement("div")
        toolbar.className = "cf-table-toolbar"
        state = {"timer": None}

        search = doc.createElement("input")
        search.type = "search"
        search.className = "cf-table-search"
        search.setAttribute("placeholder", search_placeholder)
        search.setAttribute("autocomplete", "off")
        toolbar.appendChild(search)

        def row_matches(data):
            query = (search.value or "").strip().lower()
            if not query:
                return True
            for value in (data or {}).values():
                if value is None:
                    continue
                if query in str(value).lower():
                    return True
            return False

        def apply_search():
            query = (search.value or "").strip()
            try:
                if not query:
                    table.clearFilter()
                else:
                    table.setFilter(row_matches)
            except Exception:
                pass

        def on_input(event=None):
            timer = state.get("timer")
            if timer is not None:
                try:
                    window.clearTimeout(timer)
                except Exception:
                    pass
            state["timer"] = window.setTimeout(apply_search, SEARCH_DELAY_MS)

        search.addEventListener("input", on_input)

        holder = root.querySelector(".tabulator-tableholder")
        if holder is not None and holder.parentElement is not None:
            holder.parentElement.insertBefore(toolbar, holder)
        else:
            root.insertBefore(toolbar, root.firstChild)

    _register_table_built(table, on_built)
    attach_date_range_filters(table)
    attach_compare_filters(table)
    attach_filter_clears(table)


def prepare_remote_table(table, columns, field_hints, on_excel=None):
    table.columns = stamp_columns(columns, field_hints)
    attach_toolbar(table, remote=True)
    if on_excel is not None:
        attach_excel_download(table, on_excel)


def prepare_local_table(table, columns, field_hints=None, on_excel=None, remote=False):
    table.columns = stamp_columns(columns, field_hints)
    attach_toolbar(table, remote=remote)
    if on_excel is not None:
        attach_excel_download(table, on_excel)
