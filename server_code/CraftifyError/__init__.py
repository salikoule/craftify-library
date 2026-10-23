import anvil.server


@anvil.server.callable
def craftify_report_client_error(message: str):
    """Hook for consumer apps: log client-side failures (extend with email/Slack later)."""
    print("[craftify-library client error]", message[:2000])
