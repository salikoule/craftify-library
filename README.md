# craftify-library (Anvil)

Shared **Craftify platform** pieces for client Anvil apps: iPac-derived theme, Tabulator + ECharts setup, reusable components, and small auth/error helpers.

Synced with Anvil cloud; consumer apps (e.g. **Cyclops**) add this repo as an **Anvil dependency**.

## What is included

| Area | Contents |
|------|----------|
| **Theme** | `theme.css`, `tabulator_styles.css`, `standard-page.html`, `kpi-card.html`, `chart-card.html`, `craftify-shell.html` (from iPac `data-sheets.html`) |
| **Client** | `Startup` (Tabulator modules + defaults), `CraftifyUtils`, `CraftifyLoginForm`, `CustomComponents` (AccountMenu, EChart, KpiCard, ChartCard, ToastyNotification) |
| **Charts** | Apache ECharts **5.5.1 via CDN** + `CraftifyUtils.echarts_theme` + `theme/assets/echarts_theme.js` |
| **Server** | `CraftifyAuth`, `CraftifyError.craftify_report_client_error` |
| **Demo** | Startup form `LibraryDemo` — KPI tiles, sample Tabulator, sample EChart |

## Run locally (optional)

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install anvil-app-server
git clone <your-anvil-git-url> craftify-library
anvil-app-server --app craftify-library
# http://localhost:3030/
```

Requires Java (Anvil runtime) and Postgres client libs per [Anvil app server docs](https://github.com/anvil-works/anvil-runtime/blob/master/doc/getting-started.md).

## Use in a new app (Cyclops)

1. In the Anvil Editor: **Settings → Dependencies → Add** → select **craftify-library** (this app).
2. In the consumer app **Theme**, either use the same Material theme or inherit roles from the library where Anvil allows.
3. In consumer **client startup** (e.g. `StartUp.py`):

```python
# In the consumer app startup module, e.g.:
import craftify_library.Startup  # Tabulator + ECharts defaults
from craftify_library.CraftifyUtils import ErrorHandling
import anvil

anvil.set_default_error_handler(ErrorHandling.error_handler)
```

4. Import UI pieces:

```python
from craftify_library.CraftifyLoginForm import CraftifyLoginForm
from craftify_library.CustomComponents.AccountMenu import AccountMenu
from craftify_library.CustomComponents.KpiCard import KpiCard
from craftify_library.CustomComponents.ChartCard import ChartCard
from craftify_library.CustomComponents.EChart import EChart
from tabulator.Tabulator import Tabulator
from craftify_library.CraftifyUtils.echarts_theme import apply_craftify_echarts_theme
```

5. **ECharts in consumer apps:** add the same scripts to the app’s **`native_deps.head_html`** (Anvil does not always merge dependency head HTML):

```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js"></script>
<script src="_/theme/echarts_theme.js"></script>
```

Copy `theme/assets/echarts_theme.js` into the consumer theme, or rely on the library theme asset path if your dependency setup exposes it.

6. Use **Standard Page** form template (`@theme:standard-page.html`) for sidebar + app bar layout.
7. For HTML-first screens (Cyclops sketch), embed `@theme:craftify-shell.html` or host static HTML in a Custom Form and match `.ds-page` / chip patterns from iPac.

## Dependencies (declared in `anvil.yaml`)

- **Anvil Extras** `v3.6.3`
- **Tabulator** `v3.3.2`

**ECharts** is not an Anvil dependency app — it is loaded from the CDN in `native_deps` (see above).

## Verify in cloud

Open **LibraryDemo** in the Anvil IDE (Run). You should see three KPI cards, a filtered Tabulator, and a bar chart with Montserrat styling.

## Source of UI patterns

Visual and structural patterns are taken from the **Neways iPac** app (`Clients/Neways/iPac`): theme CSS, Tabulator polish, ECharts theme hook, KPI/chart HTML shells, and client utility style.
