# ECharts (native CDN)

craftify-library does **not** use the `_D Apache ECharts` dependency app (cross-account). Charts use:

1. **[Apache ECharts 5.5.1](https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js)** in `native_deps.head_html`
2. **`theme/assets/echarts_theme.js`** — registers the `craftify` canvas theme and default `echarts.init` behaviour
3. **`CustomComponents.EChart`** — Anvil custom component (`craftifyDefineChart` + `set_option`)
4. **`CraftifyUtils.echarts_theme.apply_craftify_echarts_theme`** — Python-side option defaults (fonts, rounded bars, tooltips)

## Usage

```python
from craftify_library.CustomComponents.EChart import EChart
from craftify_library.CraftifyUtils.echarts_theme import apply_craftify_echarts_theme

chart = EChart(
    options=apply_craftify_echarts_theme({
        "xAxis": {"type": "category", "data": ["A", "B"]},
        "yAxis": {"type": "value"},
        "series": [{"type": "bar", "data": [1, 2]}],
    }),
    height="320px",
)
```

Call `craftify_library.Startup` (or `import craftify_library`) once so `install_craftify_echarts_theme()` patches `EChart` automatically.

## Consumer apps (Cyclops)

Duplicate the two `<script>` tags from craftify-library `anvil.yaml` → `native_deps.head_html`, and ship `echarts_theme.js` in the app theme (copy from this repo).

Optional: use ECharts directly in Custom HTML with `echarts.init(dom)` after the CDN scripts load — same as cyclops/sketch if you embed charts in static HTML.
