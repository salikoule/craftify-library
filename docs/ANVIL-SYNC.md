# Anvil git sync (500 errors)

If `anvil watch` fails with **500 Internal server error** on a large batch:

## Common causes (craftify-library)

1. **Deleting the startup form** — The cloud app still had **Form1** as startup while the batch tried to **unlink Form1** and add **LibraryDemo** without updating `anvil.yaml` on the server. **Fix:** keep **Form1** in the repo until a sync succeeds; then set startup to **LibraryDemo** and remove Form1 in a second commit.

2. **`client_code/__init__.py`** — Anvil mapped this to a client module named `""` (empty), which can break saves. **Fix:** do not add a root `client_code/__init__.py`; import `Startup` from forms/modules that need it (`from .. import Startup`).

3. **Huge single batch** — Many new forms + theme assets at once. **Fix:** sync in two steps (theme assets first, then client_code), or pause watch, push smaller commits.

## After a successful sync

1. In the IDE, open **LibraryDemo** and confirm it runs.
2. Set **Startup form** to **LibraryDemo** (App Settings or `anvil.yaml`: `startup: {module: LibraryDemo, type: form}`).
3. Sync again, then delete **Form1** if you no longer need it.

## “An internal error occurred: …” when you Run

1. **Dependencies** — In the Anvil IDE: **Settings → Dependencies**. Confirm **Anvil Extras** and **Tabulator** are installed (green). If missing, add them from the link in `anvil.yaml` or the Anvil dependency search.
2. **`startup_form: null`** — Remove from `anvil.yaml` if present (conflicts with `startup:`).
3. **Heavy import on startup** — Startup form must not import `Startup` / Tabulator at import time. Use plain **Form1**, then open **LibraryDemo** after sync.
4. Retry **Run** after `anvil watch` finishes syncing.

## If 500 persists

- Retry (transient Anvil outage).
- Open the app in the Anvil IDE and apply the same change manually once; then let git pull.
- Contact Anvil support with the error id from the JSON (e.g. `5eaeaccf9289`).
