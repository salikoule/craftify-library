from ._anvil_designer import CraftifyLoginFormTemplate
from anvil import *
import anvil.users


class CraftifyLoginForm(CraftifyLoginFormTemplate):
    def __init__(self, redirect_form=None, **properties):
        self._redirect_form = redirect_form
        self.init_components(**properties)

    def _go_next(self):
        if self._redirect_form:
            open_form(self._redirect_form)

    def login_btn_click(self, **event_args):
        self.error_label.visible = False
        try:
            anvil.users.login_with_email(self.email_box.text.strip(), self.password_box.text)
        except anvil.users.AuthenticationFailed as e:
            self.error_label.text = str(e)
            self.error_label.visible = True
            return
        self._go_next()

    def signup_btn_click(self, **event_args):
        self.error_label.visible = False
        try:
            anvil.users.signup_with_email(
                self.email_box.text.strip(), self.password_box.text, remember=True
            )
        except anvil.users.AuthenticationFailed as e:
            self.error_label.text = str(e)
            self.error_label.visible = True
            return
        self._go_next()
