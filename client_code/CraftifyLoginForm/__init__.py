from ._anvil_designer import CraftifyLoginFormTemplate
from anvil import *
import anvil.js
import anvil.users
from anvil.js import get_dom_node

_GOOGLE_ICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E"
    "%3Cpath fill='%23FFC107' d='M43.6 20.5H42V20H24v8h11.3C33.7 33.7 29.3 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.3 0 6.3 1.2 8.6 3.3l5.7-5.7C34.6 5.1 29.6 3 24 3 12.4 3 3 12.4 3 24s9.4 21 21 21 21-9.4 21-21c0-1.2-.1-2.3-.4-3.5z'/%3E"
    "%3Cpath fill='%23FF3D00' d='M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.3 0 6.3 1.2 8.6 3.3l5.7-5.7C34.6 5.1 29.6 3 24 3 16.3 3 9.7 7.3 6.3 14.7z'/%3E"
    "%3Cpath fill='%234CAF50' d='M24 45c5.4 0 10.3-2.1 14-5.4l-6.5-5.5C29.3 35.7 26.8 37 24 37c-5.3 0-9.7-3.3-11.3-8l-6.5 5C9.6 40.6 16.2 45 24 45z'/%3E"
    "%3Cpath fill='%231976D2' d='M43.6 20.5H42V20H24v8h11.3c-1.1 3.2-3.5 5.7-6.6 7.1l.1.1 6.5 5.5C39.1 38.6 45 33 45 24c0-1.2-.1-2.3-.4-3.5z'/%3E"
    "%3C/svg%3E"
)


class CraftifyLoginForm(CraftifyLoginFormTemplate):
    def __init__(self, redirect_form=None, brand_text="Craftify", brand_sub="Sign in to continue",
                 copyright="© Craftify", allow_signup=True, allow_google=True, **properties):
        self._redirect_form = redirect_form
        self.init_components(**properties)
        self.brand_title.text = brand_text or "Craftify"
        self.brand_subtitle.text = brand_sub or ""
        self.brand_subtitle.visible = False
        self.site_link.text = brand_sub or (brand_text or "craftify")
        self.copyright_link.text = copyright or ""
        self.signup_btn.visible = allow_signup
        self.google_login_btn.visible = allow_google
        self.google_login_btn.icon = _GOOGLE_ICON
        self.or_divider.visible = allow_signup or allow_google
        self.or_divider.text = "or continue with" if allow_google else "or"
        self._resize_handler = None

    def _go_next(self):
        target = self._redirect_form or "AppStartup"
        if callable(target):
            target()
        else:
            open_form(target)

    def _show_error(self, message):
        self.error_label.text = message
        self.error_label.visible = True

    def _pin_bottom_strip(self, component, parent, strip_h):
        parent_node = get_dom_node(parent)
        parent_node.style.position = "relative"
        node = get_dom_node(component)
        target = node
        current = node.parentElement
        while current and current is not parent_node:
            class_name = current.className or ""
            if "anvil-panel-row" in class_name:
                target = current
                break
            current = current.parentElement
        target.style.position = "absolute"
        target.style.left = "0"
        target.style.right = "0"
        target.style.bottom = "0"
        target.style.width = "100%"
        target.style.height = "%spx" % strip_h
        target.style.zIndex = "5"
        target.style.margin = "0"
        node.style.height = "%spx" % strip_h

    def _fit_login_layout(self, *_args):
        is_narrow = anvil.js.window.innerWidth < 768
        full_h = max(int(anvil.js.window.innerHeight), 400)
        strip_h = 44
        height_px = "" if is_narrow else "%spx" % full_h
        for component in (self.left_panel, self.home_header_card, self.login_panel):
            node = get_dom_node(component)
            node.style.minHeight = height_px
            node.style.height = height_px
            node.style.marginBottom = "0"
            node.style.boxSizing = "border-box"
        get_dom_node(self.left_panel).style.backgroundColor = "transparent"
        get_dom_node(self.home_header_card).style.backgroundColor = "transparent"
        get_dom_node(self.left_panel).style.overflow = "hidden"
        self._pin_bottom_strip(self.footer_row, self.left_panel, strip_h)
        self._pin_bottom_strip(self.copyright_link, self.login_panel, strip_h)

    def login_btn_click(self, **event_args):
        self.error_label.visible = False
        email = (self.email_textbox.text or "").strip()
        password = self.password_textbox.text or ""
        if not email or not password:
            self._show_error("Enter your email and password.")
            return
        try:
            anvil.users.login_with_email(email, password, remember=True)
        except Exception as e:
            self._show_error(str(e) or "Login failed.")
            return
        self._go_next()

    def signup_btn_click(self, **event_args):
        self.error_label.visible = False
        email = (self.email_textbox.text or "").strip()
        password = self.password_textbox.text or ""
        if not email or not password:
            self._show_error("Enter an email and password to create an account.")
            return
        try:
            anvil.users.signup_with_email(email, password, remember=True)
        except Exception as e:
            self._show_error(str(e) or "Could not create the account.")
            return
        self._go_next()

    def google_login_btn_click(self, **event_args):
        self.error_label.visible = False
        try:
            user = anvil.users.login_with_google(remember=True)
        except anvil.users.AuthenticationFailed:
            if not self.signup_btn.visible:
                self._show_error("Google sign-in failed.")
                return
            try:
                user = anvil.users.signup_with_google(remember=True)
            except Exception as e:
                self._show_error(str(e) or "Could not create an account with Google.")
                return
        except Exception as e:
            self._show_error(str(e) or "Google sign-in failed.")
            return
        if user:
            self._go_next()

    def forgot_password_link_click(self, **event_args):
        email = (self.email_textbox.text or "").strip()
        if not email:
            self._show_error("Enter your email address first.")
            return
        try:
            anvil.users.send_password_reset_email(email)
        except Exception as e:
            self._show_error(str(e) or "Could not send a reset email.")
            return
        alert("If an account exists for %s, a reset email has been sent." % email, title="Forgot password")

    def form_show(self, **event_args):
        self._fit_login_layout()
        anvil.js.window.setTimeout(self._fit_login_layout, 0)
        if self._resize_handler is None:
            self._resize_handler = self._fit_login_layout
            anvil.js.window.addEventListener("resize", self._resize_handler)
        if anvil.users.get_user():
            self._go_next()
