"""Craftify-styled alert and confirm dialogs.

The styles are injected at runtime, so every app that depends on the library
gets them without copying theme CSS.
"""

import anvil

_STYLE_ID = "craftify-dialogs"

_CSS = """
.anvil-alert-modal {
  --cfd-panel: #ffffff;
  --cfd-ink: #0f172a;
  --cfd-title: #1e3a5f;
  --cfd-muted: #475569;
  --cfd-line: #e2e8f0;
  --cfd-soft: #f1f5f9;
  --cfd-primary: #1e3a5f;
  --cfd-primary-hover: #0f2744;
  --cfd-danger: #dc2626;
  --cfd-danger-hover: #b91c1c;
  --cfd-on-strong: #ffffff;
}
html.craftify-theme-dark .anvil-alert-modal,
html.ipac-dark .anvil-alert-modal,
html[data-theme="dark"] .anvil-alert-modal {
  --cfd-panel: #151e2e;
  --cfd-ink: #e7eef7;
  --cfd-title: #e7eef7;
  --cfd-muted: #94a3b8;
  --cfd-line: #2a3a52;
  --cfd-soft: #1a2740;
  --cfd-primary: #93c5fd;
  --cfd-primary-hover: #bfdbfe;
  --cfd-danger: #dc2626;
  --cfd-danger-hover: #ef4444;
  --cfd-on-strong: #0b1220;
}
.anvil-modal-backdrop.anvil-in {
  opacity: 1 !important;
  background: rgba(15, 23, 42, 0.42) !important;
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
}
.anvil-alert-modal .anvil-modal-dialog.anvil-modal-sm {
  width: min(420px, calc(100vw - 32px));
  margin: 18vh auto 0;
}
.anvil-alert-modal.anvil-in .anvil-modal-dialog {
  animation: cfd-in 160ms cubic-bezier(0.2, 0.8, 0.2, 1);
}
@keyframes cfd-in {
  from { opacity: 0; transform: translateY(8px) scale(0.98); }
  to { opacity: 1; transform: none; }
}
.anvil-alert-modal .anvil-modal-content {
  background: var(--cfd-panel);
  border: 1px solid var(--cfd-line);
  border-radius: 16px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.22), 0 2px 6px rgba(15, 23, 42, 0.06);
  overflow: hidden;
  font-family: Montserrat, system-ui, sans-serif;
}
.anvil-alert-modal .anvil-modal-header {
  padding: 22px 24px 0;
  border: 0;
}
.anvil-alert-modal .anvil-modal-title {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  line-height: 1.35;
  color: var(--cfd-title);
}
.anvil-alert-modal .anvil-modal-header .anvil-close {
  color: var(--cfd-muted);
  opacity: 0.7;
  text-shadow: none;
}
.anvil-alert-modal .anvil-modal-body {
  padding: 22px 24px 4px;
  font-size: 14px;
  line-height: 1.55;
  color: var(--cfd-muted);
  white-space: pre-line;
}
.anvil-alert-modal .anvil-modal-header:not([style*="display: none"]) + .anvil-modal-body {
  padding-top: 8px;
}
.anvil-alert-modal .anvil-modal-footer {
  padding: 18px 24px 20px;
  border: 0;
  text-align: right;
}
.anvil-alert-modal .anvil-alert-footer-button-panel {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}
.anvil-alert-modal .anvil-modal-footer .anvil-button {
  margin: 0;
}
.anvil-alert-modal .anvil-modal-footer .anvil-button > .anvil-btn {
  min-width: 80px;
  border-color: var(--cfd-line) !important;
  background: var(--cfd-panel) !important;
  color: var(--cfd-title) !important;
  transition: background 120ms ease, border-color 120ms ease;
}
.anvil-alert-modal .anvil-modal-footer .anvil-button > .anvil-btn:hover {
  background: var(--cfd-soft) !important;
}
.anvil-alert-modal .anvil-modal-footer .anvil-button > .anvil-btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.18) !important;
}
.anvil-alert-modal .anvil-modal-footer .anvil-btn .anvil-component-icon:empty {
  display: none;
}
.anvil-alert-modal .anvil-modal-footer .anvil-role-success > .anvil-btn,
.anvil-alert-modal .anvil-modal-footer .anvil-role-cf-primary > .anvil-btn {
  background: var(--cfd-primary) !important;
  border-color: var(--cfd-primary) !important;
  color: var(--cfd-on-strong) !important;
}
.anvil-alert-modal .anvil-modal-footer .anvil-role-success > .anvil-btn:hover,
.anvil-alert-modal .anvil-modal-footer .anvil-role-cf-primary > .anvil-btn:hover {
  background: var(--cfd-primary-hover) !important;
  border-color: var(--cfd-primary-hover) !important;
}
.anvil-alert-modal .anvil-modal-footer .anvil-role-cf-danger > .anvil-btn {
  background: var(--cfd-danger) !important;
  border-color: var(--cfd-danger) !important;
  color: #ffffff !important;
}
.anvil-alert-modal .anvil-modal-footer .anvil-role-cf-danger > .anvil-btn:hover {
  background: var(--cfd-danger-hover) !important;
  border-color: var(--cfd-danger-hover) !important;
}
"""


def install():
    """Add the dialog styles to the page once."""
    try:
        from anvil.js.window import document
    except Exception:
        return
    if document.getElementById(_STYLE_ID):
        return
    style = document.createElement("style")
    style.id = _STYLE_ID
    style.textContent = _CSS
    document.head.appendChild(style)


def confirm(message, title=None, confirm_text="OK", cancel_text="Cancel", danger=False):
    """Ask a yes/no question. Returns True when the user confirms.

    ``danger=True`` paints the confirm button red for destructive actions.
    """
    install()
    role = "cf-danger" if danger else "cf-primary"
    return anvil.alert(
        message,
        title=title or "",
        buttons=[(cancel_text, False, ""), (confirm_text, True, role)],
        dismissible=True,
    ) is True


def alert(message, title=None, button_text="OK"):
    """Show a message with a single button."""
    install()
    return anvil.alert(
        message,
        title=title or "",
        buttons=[(button_text, True, "cf-primary")],
        dismissible=True,
    )
