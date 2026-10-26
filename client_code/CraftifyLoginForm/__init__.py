from ._anvil_designer import CraftifyLoginFormTemplate
from anvil import *
import anvil.js
import anvil.users
from anvil.js import get_dom_node


class CraftifyLoginForm(CraftifyLoginFormTemplate):
    def __init__(self, redirect_form=None, brand_text="Craftify", brand_sub="Sign in to continue",
                 copyright="© Craftify", allow_signup=True, **properties):
        self._redirect_form = redirect_form
        self.init_components(**properties)
        self.brand_title.text = brand_text or "Craftify"
        self.brand_subtitle.text = brand_sub or ""
        self.brand_subtitle.visible = False
        self.site_link.text = brand_sub or (brand_text or "craftify")
        self.copyright_link.text = copyright or ""
        self.signup_btn.visible = allow_signup
        self.or_divider.visible = allow_signup
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
