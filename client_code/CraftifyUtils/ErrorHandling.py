from routing import router
import anvil.server
from anvil import Notification, alert

from ..CustomComponents import ToastyNotification

IGNORE_ERRORS = [
    "Maximum call stack size exceeded",
    "Cannot read properties of undefined (reading 'constructor')",
    "Refused to apply style from '",
]


def _handle_client_error(err) -> bool:
    if "ShowClientError" in str(err):
        ToastyNotification(str(err).replace("ShowClientError:", ""), style="warning", timeout=5).show()
        return True
    return False


def _handle_internet_issue(err) -> bool:
    if type(err).__name__ == "AppOfflineError" or "Connection to server failed" in str(err):
        ToastyNotification(
            "Your device seems to be offline. Please try reconnecting.",
            timeout=None,
            style="info",
        ).show()
        return True
    return False


def _handle_session_expired(err) -> bool:
    if isinstance(err, anvil.server.SessionExpiredError):
        alert(
            "Your session has timed out. Please refresh the page to continue",
            title="Session Expired",
            buttons=[("Refresh Now", None)],
            dismissible=False,
        )
        anvil.server.reset_session()
        ToastyNotification("Session has been renewed.", style="success", timeout=5).show()
        return True
    return False


def _handle_timeout(err) -> bool:
    if isinstance(err, anvil.server.TimeoutError):
        alert(
            "Your query took too long to execute. Try narrowing the request.",
            title="Timeout",
        )
        return True
    return False


def _handle_prod_environment_error(err) -> bool:
    if "debug" not in anvil.app.environment.tags:
        if str(err) in IGNORE_ERRORS:
            print(str(err))
        else:
            ToastyNotification(
                "An unexpected error occurred. Refresh the page; contact support if it persists.",
                timeout=None,
                style="warning",
            ).show()
            try:
                anvil.server.call("craftify_report_client_error", str(err))
            except Exception:
                print(err)
        return True
    return False


def error_handler(err):
    """Register with ``anvil.set_default_error_handler`` in consumer app startup."""
    if _handle_client_error(err):
        return
    if _handle_internet_issue(err):
        return
    if _handle_session_expired(err):
        return
    if _handle_timeout(err):
        return
    if _handle_prod_environment_error(err):
        return
    print("Unhandled error:", err)
    raise err
