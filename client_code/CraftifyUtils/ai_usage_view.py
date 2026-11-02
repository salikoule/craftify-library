"""HTML for the Settings → AI usage report. Pure: no Anvil imports, times formatted by the caller."""

PERIODS = ((7, "7 days"), (30, "30 days"), (90, "90 days"), (0, "All time"))
BILLING_URL = "https://platform.openai.com/usage"


def esc(value):
    text = "" if value is None else str(value)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def usd(value):
    if value is None:
        return "—"
    value = float(value)
    if value == 0:
        return "$0.00"
    if value < 0.01:
        return "$%.4f" % value
    if value < 1:
        return "$%.3f" % value
    return "$%.2f" % value


def count(value):
    number = int(value or 0)
    text = str(abs(number))
    groups = []
    while len(text) > 3:
        groups.insert(0, text[-3:])
        text = text[:-3]
    groups.insert(0, text)
    return ("-" if number < 0 else "") + ",".join(groups)


def compact(value):
    number = int(value or 0)
    if number >= 1000000:
        return "%.1fM" % (number / 1000000.0)
    if number >= 10000:
        return "%.0fk" % (number / 1000.0)
    if number >= 1000:
        return "%.1fk" % (number / 1000.0)
    return str(number)


def seconds(ms):
    return "—" if ms is None else "%.1f s" % (ms / 1000.0)


def periods_html(days):
    return "".join(
        '<button type="button" data-days="%s" class="%s">%s</button>' % (value, "is-on" if value == days else "", label)
        for value, label in PERIODS
    )


def _tile(label, value, note=""):
    return ('<div class="cs-u-tile"><span>%s</span><strong>%s</strong><small>%s</small></div>'
            % (esc(label), esc(value), esc(note)))


def _tiles(report):
    t = report["totals"]
    calls_note = "%s failed" % t["errors"] if t["errors"] else "All succeeded" if t["calls"] else ""
    tokens_note = "%s in · %s cached · %s out" % (compact(t["input_tokens"]), compact(t["cached_tokens"]),
                                                 compact(t["output_tokens"]))
    return '<div class="cs-u-tiles">%s</div>' % "".join((
        _tile("Spend", usd(t["cost_usd"]), "This month %s · all time %s" % (usd(report.get("month_cost_usd")),
                                                                            usd(report.get("all_time_cost_usd")))),
        _tile("Calls", count(t["calls"]), calls_note),
        _tile("Tokens", compact(t["tokens"]), tokens_note),
        _tile("Per call", usd(t["avg_cost_usd"]), "Average reply in %s" % seconds(t["avg_latency_ms"])),
    ))


def _chart(report, fmt_label):
    bars = (report.get("chart") or {}).get("bars") or []
    if not bars:
        return ""
    top = max([bar["cost_usd"] for bar in bars] + [0])
    cols = []
    for bar in bars:
        height = 0 if not top else max(4, int(round(bar["cost_usd"] / top * 100)))
        tip = "%s · %s · %s call%s" % (fmt_label(bar["label"]), usd(bar["cost_usd"]), bar["calls"],
                                        "" if bar["calls"] == 1 else "s")
        cols.append('<i title="%s" class="%s"><b style="height:%s%%"></b></i>' % (
            esc(tip), "is-empty" if not bar["calls"] else "", height))
    return (
        '<div class="cs-u-chart"><div class="cs-u-bars">%s</div>'
        '<div class="cs-u-axis"><span>%s</span><span>Peak %s</span><span>%s</span></div></div>'
        % ("".join(cols), esc(fmt_label(bars[0]["label"])), esc(usd(top)), esc(fmt_label(bars[-1]["label"])))
    )


def _group_table(title, rows, total_cost):
    if not rows:
        return ""
    body = []
    for row in rows:
        share = "%d%%" % round(row["cost_usd"] / total_cost * 100) if total_cost else "—"
        body.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            esc(row["name"]), count(row["calls"]), compact(row["tokens"]), usd(row["cost_usd"]), share))
    return (
        '<div class="cs-u-block"><h4>%s</h4><div class="cs-u-scroll"><table class="cs-u-table">'
        "<thead><tr><th>%s</th><th>Calls</th><th>Tokens</th><th>Cost</th><th>Share</th></tr></thead>"
        "<tbody>%s</tbody></table></div></div>" % (esc(title), "Feature" if title == "By feature" else "Model", "".join(body))
    )


def _recent(report, fmt_time):
    rows = report.get("recent") or []
    if not rows:
        return ""
    body = []
    for row in rows:
        ok = row.get("status") == "ok"
        status = '<span class="cs-u-ok">OK</span>' if ok else '<span class="cs-u-err" title="%s">Failed</span>' % esc(row.get("error"))
        cached = row.get("cached_tokens") or 0
        tokens = "%s in · %s out" % (count(row.get("input_tokens")), count(row.get("output_tokens")))
        if cached:
            tokens += "<em>%s cached</em>" % count(cached)
        body.append(
            '<tr title="%s"><td>%s</td><td>%s<em>%s</em></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                esc("Request %s" % row["request_id"]) if row.get("request_id") else "",
                esc(fmt_time(row["at"])), esc(row.get("feature")), esc(row.get("model")), tokens,
                usd(row.get("cost_usd")) if ok else "—", seconds(row.get("latency_ms")), status))
    more = report["totals"]["calls"] - len(rows)
    return (
        '<div class="cs-u-block"><h4>Calls</h4><div class="cs-u-scroll"><table class="cs-u-table cs-u-calls">'
        "<thead><tr><th>When</th><th>Feature</th><th>Tokens</th><th>Cost</th><th>Time</th><th>Status</th></tr></thead>"
        "<tbody>%s</tbody></table></div>%s</div>"
        % ("".join(body), '<p class="cs-u-note">Showing the latest %s. %s older call%s in this period.</p>' % (
            len(rows), more, "" if more == 1 else "s") if more > 0 else "")
    )


def _footnote():
    return ('<p class="cs-u-note">Costs are estimates from OpenAI list prices for each model. Your OpenAI bill is final: '
            '<a href="%s" target="_blank" rel="noopener noreferrer">open OpenAI usage</a>.</p>' % BILLING_URL)


def report_html(report, fmt_time=str, fmt_label=str):
    """The full report. ``fmt_time`` formats ISO datetimes; ``fmt_label`` formats chart bar labels."""
    if not report or not report.get("ready"):
        return ('<div class="cs-u-empty"><strong>Usage logging is not set up in this app yet.</strong>'
                "<p>Add a data table named <code>ai_usage</code> to the app. Calls are logged from then on.</p></div>")
    totals = report["totals"]
    if not totals["calls"]:
        return ('<div class="cs-u-empty"><strong>No AI calls in this period.</strong>'
                "<p>Reading a scan or asking the coach shows up here, with tokens and cost.</p></div>%s" % _footnote())
    return "".join((
        _tiles(report),
        _chart(report, fmt_label),
        _group_table("By feature", report.get("by_feature"), totals["cost_usd"]),
        _group_table("By model", report.get("by_model"), totals["cost_usd"]) if len(report.get("by_model") or []) > 1 else "",
        _recent(report, fmt_time),
        _footnote(),
    ))
