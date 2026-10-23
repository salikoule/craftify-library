# BodyCoach (server module)

Reusable **pure Python** coach for body-composition apps (no Anvil imports inside `BodyCoach/`).

## Location

`server_code/BodyCoach/` — import as `craftify_library.BodyCoach` from consumer apps.

## Tests

```bash
cd craftify-library
.venv/bin/pip install pytest  # once
.venv/bin/python -m pytest tests/test_body_coach.py tests/test_body_coach_extended.py -q
```

## Consumer example

**body-comp-tracker** calls `propose_plan`, `build_schedule`, and `adapt_calories` via `server_code/BodyCompService/`.

## Auth UI

- `CraftifyLoginForm` — optional `redirect_form=` after sign-in.
- `CraftifyAuth.craftify_require_user()` — server-side guard for `@anvil.server.callable` endpoints.
