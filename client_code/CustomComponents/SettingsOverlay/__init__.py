from ._anvil_designer import SettingsOverlayTemplate
from anvil import *
from anvil.js import get_dom_node, window
import anvil.server
import anvil.users
import anvil.js
from ...CraftifyUtils.theme import apply_theme, current_theme
from ...CraftifyUtils import ai_usage_view as usage_view

GLOBAL_SECTIONS = (
    ("account", "Account", False),
    ("appearance", "Appearance", False),
    ("notifications", "Notifications", False),
    ("privacy", "Privacy", False),
    ("data", "Data", True),
    ("ai", "AI", False),
    ("about", "About", False),
)
UNITS_KEY = "craftify-units"
NAME_KEY = "craftify-display-name"
TZ_KEY = "craftify-timezone"
LOCALE_KEY = "craftify-locale"
NOTIFY_KEYS = (
    ("cs_notify_product", "craftify-notify-product"),
    ("cs_notify_checkin", "craftify-notify-checkin"),
    ("cs_notify_email", "craftify-notify-email"),
)
TIMEZONES = (
    ("", "Use browser default"),
    ("UTC", "UTC"),
    ("Europe/Athens", "Europe/Athens"),
    ("Europe/London", "Europe/London"),
    ("Europe/Berlin", "Europe/Berlin"),
    ("America/New_York", "America/New_York"),
    ("America/Los_Angeles", "America/Los_Angeles"),
)
LOCALES = (
    ("", "Use browser default"),
    ("en-US", "English (US)"),
    ("en-GB", "English (UK)"),
    ("el-GR", "Greek (Greece)"),
    ("de-DE", "German (Germany)"),
)


def _node(form, name):
    nodes = getattr(form, "dom_nodes", None)
    if not nodes:
        return None
    try:
        return nodes[name]
    except Exception:
        return None


def _storage_get(key, default=""):
    try:
        value = window.localStorage.getItem(key)
        return default if value is None else value
    except Exception:
        return default


def _storage_set(key, value):
    try:
        window.localStorage.setItem(key, value)
    except Exception:
        pass


def _locale():
    locale = _storage_get(LOCALE_KEY)
    return [locale] if locale else []


def _js_date(iso):
    return anvil.js.new(window.Date, iso)


def _local_time(iso):
    """An ISO datetime in the user's timezone, e.g. 2 Nov, 14:05."""
    try:
        options = {"day": "numeric", "month": "short", "hour": "2-digit", "minute": "2-digit"}
        zone = _storage_get(TZ_KEY)
        if zone:
            options["timeZone"] = zone
        return _js_date(iso).toLocaleString(_locale(), options)
    except Exception:
        return str(iso)[:16].replace("T", " ")


def _local_day(label):
    """A chart label (YYYY-MM-DD or YYYY-MM) as 2 Nov or Nov 2026."""
    try:
        if len(label) == 7:
            return _js_date(label + "-01T12:00:00").toLocaleDateString(_locale(), {"month": "short", "year": "numeric"})
        return _js_date(label + "T12:00:00").toLocaleDateString(_locale(), {"day": "numeric", "month": "short"})
    except Exception:
        return label


def current_units():
    stored = _storage_get(UNITS_KEY, "metric")
    return stored if stored in ("metric", "imperial") else "metric"


class SettingsOverlay(SettingsOverlayTemplate):
    def __init__(self, extra_sections=None, **properties):
        self._extra = list(extra_sections or [])
        self._section = properties.get("default_section") or "account"
        self._open = False
        self._ported = False
        self._mounted_id = None
        self.init_components(**properties)
        apply_theme(current_theme())
        self._fill_static()
        self._bind()
        self._render_nav()
        self._show_section(self._section, mount=False)
        self._portal()

    def form_show(self, **event_args):
        self._fill_static()
        self._bind()
        apply_theme(current_theme())
        self._portal()

    def form_hide(self, **event_args):
        root = _node(self, "cs_root")
        host = None
        try:
            host = get_dom_node(self)
        except Exception:
            host = None
        if root is None or host is None:
            return
        try:
            host.appendChild(root)
            self._ported = False
        except Exception:
            pass

    def _portal(self):
        root = _node(self, "cs_root")
        host = None
        try:
            host = get_dom_node(self)
        except Exception:
            host = None
        if root is not None:
            try:
                window.document.body.appendChild(root)
                self._ported = True
            except Exception:
                pass
        if host is None:
            return
        host.style.position = "fixed"
        host.style.width = "0"
        host.style.height = "0"
        host.style.overflow = "visible"
        host.style.margin = "0"
        host.style.padding = "0"
        host.style.pointerEvents = "none"
        parent = getattr(host, "parentElement", None)
        while parent is not None and hasattr(parent, "className"):
            class_name = parent.className or ""
            if "anvil-panel-row" in class_name or "anvil-measure-this" in class_name:
                parent.style.height = "0"
                parent.style.minHeight = "0"
                parent.style.overflow = "visible"
                parent.style.margin = "0"
                parent.style.padding = "0"
                parent.style.pointerEvents = "none"
                break
            parent = parent.parentElement

    def _fill_static(self):
        name = _node(self, "cs_about_name")
        version = _node(self, "cs_about_version")
        desc = _node(self, "cs_about_desc")
        if name is not None:
            name.textContent = self.app_name or "Craftify"
        if version is not None:
            text = self.app_version or "—"
            version.textContent = text if str(text).startswith("v") or text == "—" else ("v%s" % text)
        if desc is not None:
            desc.textContent = self.app_description or "Built on Craftify."
        for key, url in (("cs_docs", getattr(self, "docs_url", "")), ("cs_changelog", getattr(self, "changelog_url", ""))):
            link = _node(self, key)
            if link is None:
                continue
            href = url or "#"
            link.setAttribute("href", href)
            link.style.display = "" if url else "none"

    def _bind(self):
        root = _node(self, "cs_root")
        if root is None:
            return
        if getattr(self, "_bound", False):
            self._paint_prefs()
            return
        backdrop = _node(self, "cs_backdrop")
        close_btn = _node(self, "cs_close")
        if backdrop is not None:
            backdrop.addEventListener("click", lambda e: self.close())
        if close_btn is not None:
            close_btn.addEventListener("click", lambda e: self.close())
        pairs = (
            ("cs_save_pw", self._change_password),
            ("cs_reset_pw", self._email_reset),
            ("cs_save_name", self._save_name),
            ("cs_save_regional", self._save_regional),
            ("cs_save_notify", self._save_notify),
            ("cs_save_ai", self._save_ai),
            ("cs_clear_ai", self._clear_ai),
            ("cs_ai_days", self._usage_period),
            ("cs_signout_device", self._sign_out),
            ("cs_theme_light", lambda e: self._set_theme("light")),
            ("cs_theme_dark", lambda e: self._set_theme("dark")),
            ("cs_theme_system", lambda e: self._set_theme("system")),
            ("cs_units_metric", lambda e: self._set_units("metric")),
            ("cs_units_imperial", lambda e: self._set_units("imperial")),
        )
        for name, handler in pairs:
            node = _node(self, name)
            if node is not None:
                node.addEventListener("click", handler)
        window.document.addEventListener("keydown", self._on_key)
        self._fill_selects()
        self._bound = True
        self._paint_prefs()

    def _fill_selects(self):
        self._fill_select("cs_timezone", TIMEZONES, _storage_get(TZ_KEY))
        self._fill_select("cs_locale", LOCALES, _storage_get(LOCALE_KEY))

    def _fill_select(self, name, options, selected):
        node = _node(self, name)
        if node is None:
            return
        node.innerHTML = ""
        doc = window.document
        for value, label in options:
            option = doc.createElement("option")
            option.value = value
            option.textContent = label
            if value == selected:
                option.selected = True
            node.appendChild(option)

    def _on_key(self, event):
        if not self._open:
            return
        if getattr(event, "key", "") == "Escape":
            self.close()

    def _items(self):
        extras = []
        for item in self._extra:
            extras.append((item.get("id"), item.get("label") or item.get("id"), bool(item.get("coming_soon")), True))
        globals_ = [(section_id, label, coming_soon, False) for section_id, label, coming_soon in GLOBAL_SECTIONS]
        return extras + globals_

    def _render_nav(self):
        nav = _node(self, "cs_nav")
        if nav is None:
            return
        nav.innerHTML = ""
        doc = window.document
        saw_global = False
        for section_id, label, coming_soon, is_extra in self._items():
            if not section_id:
                continue
            if not is_extra and not saw_global:
                if self._extra:
                    rule = doc.createElement("hr")
                    rule.className = "cs-nav-rule"
                    nav.appendChild(rule)
                saw_global = True
            btn = doc.createElement("button")
            btn.type = "button"
            btn.className = "cs-nav-btn"
            btn.setAttribute("data-section", section_id)
            text = doc.createElement("span")
            text.textContent = label
            btn.appendChild(text)
            if coming_soon:
                badge = doc.createElement("span")
                badge.className = "cs-soon"
                badge.textContent = "Soon"
                btn.appendChild(badge)
            btn.addEventListener("click", self._nav_click)
            nav.appendChild(btn)

    def _nav_click(self, event):
        btn = getattr(event, "currentTarget", None) or getattr(event, "target", None)
        if btn is None:
            return
        if hasattr(btn, "closest"):
            btn = btn.closest("[data-section]") or btn
        section = btn.getAttribute("data-section")
        self.open(section)

    def _extra_item(self, section):
        for item in self._extra:
            if item.get("id") == section:
                return item
        return None

    def _show_section(self, section, mount=True):
        ids = [item[0] for item in self._items()]
        if section not in ids:
            section = ids[0] if ids else "account"
        self._section = section
        extra = self._extra_item(section)
        host = _node(self, "cs_root") or get_dom_node(self)
        if host is not None and hasattr(host, "querySelectorAll"):
            for node in host.querySelectorAll(".cs-section"):
                is_app = node.getAttribute("data-section") == "app"
                if extra is not None:
                    node.classList.toggle("is-on", is_app)
                else:
                    node.classList.toggle("is-on", node.getAttribute("data-section") == section)
        nav = _node(self, "cs_nav")
        if nav is not None:
            for btn in nav.querySelectorAll(".cs-nav-btn"):
                active = btn.getAttribute("data-section") == section
                btn.classList.toggle("is-active", active)
                btn.setAttribute("aria-current", "page" if active else "false")
        if extra is not None and mount:
            self._mount_extra(extra)
        elif extra is None:
            self._mounted_id = None
        if section == "account":
            self._fill_account()
        if section == "notifications":
            self._paint_notify()
        if section == "ai":
            self._paint_ai()
            if mount:
                self._paint_usage()
        self._paint_prefs()

    def _mount_extra(self, extra):
        if self._mounted_id == extra.get("id"):
            return
        form = extra.get("form")
        builder = extra.get("build")
        try:
            self.clear(slot="section")
        except Exception:
            try:
                self.clear_slot("section")
            except Exception:
                pass
        child = None
        if builder is not None:
            child = builder()
        elif form is not None:
            child = form() if callable(form) else form
        if child is not None:
            self.add_component(child, slot="section", full_width_row=True)
            self._mounted_id = extra.get("id")

    def _user_email(self):
        try:
            user = anvil.users.get_user()
            return (user["email"] if user else "") or ""
        except Exception:
            return ""

    def _fill_account(self):
        email = self._user_email()
        name = _storage_get(NAME_KEY) or (email.split("@")[0] if email else "Signed in")
        email_box = _node(self, "cs_email")
        if email_box is not None:
            email_box.value = email
        display = _node(self, "cs_display")
        if display is not None:
            display.value = _storage_get(NAME_KEY)
        label = _node(self, "cs_display_label")
        if label is not None:
            label.textContent = name
        email_label = _node(self, "cs_email_label")
        if email_label is not None:
            email_label.textContent = email
        avatar = _node(self, "cs_avatar")
        if avatar is not None:
            avatar.textContent = (name[:1] or "?").upper()
        google = _node(self, "cs_google_status")
        if google is not None:
            connected = ""
            try:
                from anvil.google.auth import get_user_email
                connected = get_user_email() or ""
            except Exception:
                connected = ""
            if connected:
                google.textContent = "Google connected as %s." % connected
            else:
                google.textContent = "Google sign-in is available on the login page when this app enables it."
        self._fill_selects()

    def _account_msg(self, text, error=False):
        node = _node(self, "cs_account_msg")
        if node is None:
            return
        node.textContent = text or ""
        node.classList.toggle("is-error", bool(error))

    def _save_name(self, event=None):
        box = _node(self, "cs_display")
        name = getattr(box, "value", "") if box is not None else ""
        _storage_set(NAME_KEY, (name or "").strip())
        self._fill_account()
        self._account_msg("Display name saved on this device.")

    def _save_regional(self, event=None):
        tz = _node(self, "cs_timezone")
        locale = _node(self, "cs_locale")
        _storage_set(TZ_KEY, getattr(tz, "value", "") if tz is not None else "")
        _storage_set(LOCALE_KEY, getattr(locale, "value", "") if locale is not None else "")
        self._account_msg("Regional preferences saved on this device.")

    def _change_password(self, event=None):
        old_box = _node(self, "cs_old_pw")
        new_box = _node(self, "cs_new_pw")
        confirm_box = _node(self, "cs_confirm_pw")
        old_pw = getattr(old_box, "value", "") if old_box is not None else ""
        new_pw = getattr(new_box, "value", "") if new_box is not None else ""
        confirm_pw = getattr(confirm_box, "value", "") if confirm_box is not None else ""
        if not old_pw or not new_pw:
            self._account_msg("Enter your current and new password.", error=True)
            return
        if new_pw != confirm_pw:
            self._account_msg("New passwords do not match.", error=True)
            return
        if len(new_pw) < 8:
            self._account_msg("Use at least 8 characters.", error=True)
            return
        try:
            anvil.users.reset_password(old_pw, new_pw)
        except Exception as e:
            self._account_msg(str(e) or "Could not update the password.", error=True)
            return
        for box in (old_box, new_box, confirm_box):
            if box is not None:
                box.value = ""
        self._account_msg("Password updated.")

    def _email_reset(self, event=None):
        email_box = _node(self, "cs_email")
        email = getattr(email_box, "value", "") if email_box is not None else ""
        if not email:
            self._account_msg("No email on this account.", error=True)
            return
        try:
            anvil.users.send_password_reset_email(email)
        except Exception as e:
            self._account_msg(str(e) or "Could not send a reset email.", error=True)
            return
        self._account_msg("If an account exists, a reset email has been sent.")

    def _sign_out(self, event=None):
        try:
            anvil.users.logout()
        except Exception:
            pass
        self.close()
        try:
            from ..CraftifyRouting import navigate
            navigate(path="/login")
        except Exception:
            try:
                window.location.href = "/login"
            except Exception:
                pass

    def _set_theme(self, theme, event=None):
        apply_theme(theme)
        self._paint_prefs()

    def _set_units(self, units, event=None):
        _storage_set(UNITS_KEY, "imperial" if units == "imperial" else "metric")
        self._paint_prefs()

    def _paint_prefs(self):
        theme = current_theme()
        for name, value in (("cs_theme_light", "light"), ("cs_theme_dark", "dark"), ("cs_theme_system", "system")):
            node = _node(self, name)
            if node is not None:
                node.classList.toggle("is-on", theme == value)
        units = current_units()
        metric = _node(self, "cs_units_metric")
        imperial = _node(self, "cs_units_imperial")
        if metric is not None:
            metric.classList.toggle("is-on", units == "metric")
        if imperial is not None:
            imperial.classList.toggle("is-on", units == "imperial")

    def _paint_notify(self):
        for name, key in NOTIFY_KEYS:
            node = _node(self, name)
            if node is not None:
                node.checked = _storage_get(key) == "1"

    def _save_notify(self, event=None):
        for name, key in NOTIFY_KEYS:
            node = _node(self, name)
            _storage_set(key, "1" if node is not None and getattr(node, "checked", False) else "0")
        msg = _node(self, "cs_notify_msg")
        if msg is not None:
            msg.textContent = "Notification preferences saved on this device."

    def _ai_msg(self, text, error=False):
        node = _node(self, "cs_ai_msg")
        if node is None:
            return
        node.textContent = text or ""
        node.classList.toggle("is-error", bool(error))

    def _paint_ai(self, status=None):
        if status is None:
            try:
                status = anvil.server.call("craftify_ai_key_status")
            except Exception as e:
                self._ai_msg(str(e) or "Could not load the AI key.", error=True)
                status = {}
        hint = (status or {}).get("hint") or ""
        has_key = bool((status or {}).get("has_key"))
        label = _node(self, "cs_ai_status")
        if label is not None:
            if has_key:
                label.textContent = "Key saved for this account (%s)." % hint
            else:
                label.textContent = "No key saved. File reading still works from the PDF text when it can."
        box = _node(self, "cs_ai_key")
        if box is not None:
            box.value = ""
            box.placeholder = hint or "sk-…"

    def _save_ai(self, event=None):
        box = _node(self, "cs_ai_key")
        key = getattr(box, "value", "") if box is not None else ""
        try:
            status = anvil.server.call("craftify_ai_save_key", key)
        except Exception as e:
            self._ai_msg(str(e) or "Could not save the API key.", error=True)
            return
        self._paint_ai(status)
        self._ai_msg("API key saved for this account.")

    def _clear_ai(self, event=None):
        try:
            status = anvil.server.call("craftify_ai_clear_key")
        except Exception as e:
            self._ai_msg(str(e) or "Could not remove the API key.", error=True)
            return
        self._paint_ai(status)
        self._ai_msg("API key removed.")

    def _paint_usage(self, days=None):
        if days is not None:
            self._usage_days = days
        days = getattr(self, "_usage_days", 30)
        seg = _node(self, "cs_ai_days")
        if seg is not None:
            seg.innerHTML = usage_view.periods_html(days)
        box = _node(self, "cs_ai_report")
        if box is None:
            return
        try:
            report = anvil.server.call_s("craftify_ai_usage", days)
        except Exception as e:
            box.innerHTML = '<p class="cs-msg is-error">%s</p>' % usage_view.esc(str(e) or "Could not load AI usage.")
            return
        box.innerHTML = usage_view.report_html(report, _local_time, _local_day)

    def _usage_period(self, event=None):
        target = getattr(event, "target", None)
        button = target.closest("[data-days]") if target is not None and hasattr(target, "closest") else None
        if button is None:
            return
        try:
            days = int(button.getAttribute("data-days"))
        except (TypeError, ValueError):
            return
        self._paint_usage(days)

    def open(self, section=None):
        self._portal()
        if section:
            self._show_section(section)
        else:
            self._show_section(self._section or self.default_section or "account")
        root = _node(self, "cs_root")
        if root is not None:
            root.classList.remove("cs-off")
            root.setAttribute("aria-hidden", "false")
        self._open = True
        close_btn = _node(self, "cs_close")
        if close_btn is not None:
            try:
                close_btn.focus()
            except Exception:
                pass
        self.raise_event("opened", section=self._section)

    def close(self):
        root = _node(self, "cs_root")
        if root is not None:
            root.classList.add("cs-off")
            root.setAttribute("aria-hidden", "true")
        self._open = False
        self.raise_event("closed")

    def open_settings(self, section=None):
        self.open(section)
