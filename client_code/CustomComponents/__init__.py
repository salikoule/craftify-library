from anvil import Notification


_TOAST_STYLES = {"success", "warning", "danger", "info"}


class ToastyNotification:
    """Top-right toast aligned with iPac / Neways Spice styling (Anvil Notification under the hood)."""

    def __init__(self, message, timeout=4, style="info", **kwargs):
        if style == "error":
            style = "danger"
        if style not in _TOAST_STYLES:
            style = "info"
        self._notification = Notification(message, timeout=timeout, style=style)

    def show(self):
        self._notification.show()
