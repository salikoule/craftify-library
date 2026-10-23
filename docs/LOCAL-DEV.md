# Local dev & agent testing (Apple Silicon)

Cloud **Run** in the Anvil IDE is the default. Use this when you want **anvil-app-server** on your Mac (Cursor browser tools, Playwright, etc.).

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Java 21+** | `brew install openjdk@21` — the runtime JAR needs Java 21 (`SequencedCollection`). |
| **PostgreSQL** | On arm64, embedded Postgres in `.anvil-data` is x86-only. Use Homebrew Postgres: `brew install postgresql@14` && `brew services start postgresql@14`. |
| **Python venv** | `python3 -m venv .venv && pip install anvil-app-server` inside `craftify-library`. |
| **Sibling deps** | Tabulator + Anvil Extras as folders **next to** the app (see below). |

## One-command start

```bash
chmod +x scripts/dev-server.sh
./scripts/dev-server.sh
```

Open **http://localhost:3030/** — startup form **LibraryDemo** (KPI cards, Tabulator, ECharts).

## Layout (important)

The app server loads the main app from a directory whose name is a valid Python package:

```
_Craftify Works/
  craftify-library/     # git checkout (hyphen OK in git)
  craftify_library -> craftify-library   # symlink for runtime
  tabulator -> tabulator_github          # v3.3.1 from GitHub
  anvil_extras -> anvil_extras_github    # v3.6.3 from GitHub
```

You cannot `anvil checkout` the marketplace Tabulator/Extras apps without clone access; the **anvilistas** GitHub repos at matching tags work for local `--dep-id` mapping.

Pass **both** marketplace app IDs and opaque `dep_*` ids from `anvil.yaml` (see `scripts/dev-server.sh`).

## Full JAR in `~/.anvil`

`pip install anvil-app-server` may include a **truncated** JAR (~96MB). The script downloads the full **~378MB** JAR to `~/.anvil/` if needed.

## Agent interaction

With the server running, use Cursor **Browser** (or any automation) against `http://localhost:3030/`. The page exposes grid cells, pagination, and chart chrome once the downlink connects (watch the terminal for `Downlink client connected`).
