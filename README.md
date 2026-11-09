# craftify-library (Anvil)

Shared **Craftify platform** pieces for client Anvil apps: iPac-derived theme, Tabulator + ECharts setup, reusable components, and small auth/error helpers.

Synced with Anvil cloud; consumer apps (e.g. **Cyclops**) add this repo as an **Anvil dependency**.

## What is included

| Area | Contents |
|------|----------|
| **Theme** | `theme.css`, `tabulator_styles.css`, `standard-page.html`, `kpi-card.html`, `chart-card.html`, `craftify-shell.html` (from iPac `data-sheets.html`) |
| **Client** | `Startup` (Tabulator modules + defaults), `CraftifyUtils`, `CraftifyLoginForm`, `CustomComponents` (AccountMenu, EChart, KpiCard, ChartCard, TimePicker, SearchPalette, ToastyNotification) |
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
from craftify_library.CustomComponents.TimePicker import TimePicker  # TimePicker(time="09:30", minute_step=5, min_time="06:00"); event: change
from craftify_library.CustomComponents.SearchPalette import SearchPalette  # see "Search pop-up" below
from tabulator.Tabulator import Tabulator
from craftify_library.CraftifyUtils.echarts_theme import apply_craftify_echarts_theme
```

**Search pop-up.** `SearchPalette` opens over the page from a sidebar button or Ctrl/⌘+K. Arrow keys move, Enter picks, and Esc closes. Picked hits show as Recent (kept in the browser under `recent_key`).

```python
def find(text):  # a list of hits: title, plus optional subtitle, badge, badge_class, kind, id, and any keys you need back
    return [{"id": r["code"], "title": r["name"], "badge": r["code"], "kind": "Item", "path": "/items/" + r["code"]}
            for r in anvil.server.call_s("search", text)]

palette = SearchPalette(search=find, placeholder="Find a record", recent_key="myapp")
palette.set_event_handler("select", lambda hit, **e: navigate(path=hit["path"]))
self.add_component(palette)                                        # the pop-up itself (fixed over the page)
self.menu_panel.add_component(palette.trigger(), full_width_row=True)  # "Search  ⌘K" button for the sidebar
```

Call `palette.close()` from the router's `navigate` handler. Override the colours with the `--cf-sp-*` CSS variables. Dark mode follows `ipac-dark`, `craftify-theme-dark` or `data-theme="dark"`.

5. **ECharts in consumer apps:** add the same scripts to the app’s **`native_deps.head_html`** (Anvil does not always merge dependency head HTML):

```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js"></script>
<script src="_/theme/echarts_theme.js"></script>
```

Copy `theme/assets/echarts_theme.js` into the consumer theme, or rely on the library theme asset path if your dependency setup exposes it.

6. Use **Standard Page** form template (`@theme:standard-page.html`) for sidebar + app bar layout. Sidebar links are `NavLink(text=, path=, icon="fa:...")` in the `left-nav` slot. Common `fa:` names (`box`, `industry`, `chart-line`, `users`, `gear` and others listed in `craftify-full-theme.css`) are drawn as Lucide line icons; any other `fa:` name keeps its Font Awesome glyph. Put a group label between links with `<div class="cf-nav-group">Records</div>`. Colours are the `--cf-nav-*` CSS variables. The theme files are copied into each app's `theme/assets`, so copy `craftify-full-theme.css` and `craftify-theme.css` again after changing them here.
7. For HTML-first screens (Cyclops sketch), embed `@theme:craftify-shell.html` or host static HTML in a Custom Form and match `.ds-page` / chip patterns from iPac.

## Dependencies (declared in `anvil.yaml`)

- **Anvil Extras** `v3.6.3`
- **Tabulator** `v3.3.2`

**ECharts** is not an Anvil dependency app — it is loaded from the CDN in `native_deps` (see above).

## Verify in cloud

Open **LibraryDemo** in the Anvil IDE (Run). You should see three KPI cards, a filtered Tabulator, and a bar chart with Montserrat styling.

## Source of UI patterns

Visual and structural patterns are taken from the **Neways iPac** app (`Clients/Neways/iPac`): theme CSS, Tabulator polish, ECharts theme hook, KPI/chart HTML shells, and client utility style.
