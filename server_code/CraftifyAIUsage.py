"""AI usage accounting: token prices, call records, and the report summary. No Anvil imports."""

from datetime import date, datetime, timedelta, timezone

# USD per 1M tokens: (input, cached input, output). OpenAI list prices; the OpenAI bill is the source of truth.
PRICES = {
    "gpt-5": (1.25, 0.125, 10.00),
    "gpt-5-mini": (0.25, 0.025, 2.00),
    "gpt-5-nano": (0.05, 0.005, 0.40),
    "gpt-4.1": (2.00, 0.50, 8.00),
    "gpt-4.1-mini": (0.40, 0.10, 1.60),
    "gpt-4.1-nano": (0.10, 0.025, 0.40),
    "gpt-4o": (2.50, 1.25, 10.00),
    "gpt-4o-mini": (0.15, 0.075, 0.60),
    "o3": (2.00, 0.50, 8.00),
    "o4-mini": (1.10, 0.275, 4.40),
}
RECENT_LIMIT = 50
MAX_DAY_BARS = 90


def price_for(model):
    """The price row for a model name, matching dated names like gpt-4.1-2025-04-14 by the longest prefix."""
    name = (model or "").lower()
    best = None
    for key in PRICES:
        if (name == key or name.startswith(key + "-")) and (best is None or len(key) > len(best)):
            best = key
    return PRICES.get(best)


def cost_usd(model, input_tokens, cached_tokens, output_tokens):
    """Estimated cost of one call, or None when the model has no known price."""
    price = price_for(model)
    if price is None:
        return None
    fresh = max(0, (input_tokens or 0) - (cached_tokens or 0))
    return (fresh * price[0] + (cached_tokens or 0) * price[1] + (output_tokens or 0) * price[2]) / 1e6


def record_from_usage(feature, model, usage, latency_ms, status="ok", error="", request_id="", at=None):
    """One usage row from an OpenAI chat completion ``usage`` block."""
    usage = usage or {}
    prompt = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
    output = usage.get("completion_tokens") or usage.get("output_tokens") or 0
    cached = ((usage.get("prompt_tokens_details") or usage.get("input_tokens_details") or {}).get("cached_tokens")) or 0
    reasoning = ((usage.get("completion_tokens_details") or usage.get("output_tokens_details") or {})
                 .get("reasoning_tokens")) or 0
    return {
        "at": at or datetime.now(timezone.utc),
        "feature": feature or "Other",
        "model": model or "",
        "input_tokens": int(prompt),
        "cached_tokens": int(cached),
        "output_tokens": int(output),
        "reasoning_tokens": int(reasoning),
        "cost_usd": cost_usd(model, prompt, cached, output) if status == "ok" else 0.0,
        "latency_ms": int(latency_ms or 0),
        "status": status,
        "error": (error or "")[:300],
        "request_id": request_id or "",
    }


def _aware(value):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    return None


def _totals(records):
    calls = len(records)
    errors = sum(1 for r in records if r.get("status") != "ok")
    priced = [r["cost_usd"] for r in records if r.get("cost_usd") is not None]
    latencies = [r.get("latency_ms") or 0 for r in records if r.get("status") == "ok"]
    inp = sum(r.get("input_tokens") or 0 for r in records)
    out = sum(r.get("output_tokens") or 0 for r in records)
    return {
        "calls": calls,
        "errors": errors,
        "input_tokens": inp,
        "cached_tokens": sum(r.get("cached_tokens") or 0 for r in records),
        "output_tokens": out,
        "reasoning_tokens": sum(r.get("reasoning_tokens") or 0 for r in records),
        "tokens": inp + out,
        "cost_usd": round(sum(priced), 6),
        "unpriced_calls": sum(1 for r in records if r.get("cost_usd") is None and r.get("status") == "ok"),
        "avg_latency_ms": int(sum(latencies) / len(latencies)) if latencies else None,
        "avg_cost_usd": round(sum(priced) / len(priced), 6) if priced else None,
    }


def _group(records, key):
    groups = {}
    for r in records:
        groups.setdefault(r.get(key) or "—", []).append(r)
    rows = [dict(_totals(items), name=name) for name, items in groups.items()]
    return sorted(rows, key=lambda row: (-(row["cost_usd"] or 0), -row["calls"]))


def _bars(records, since, now):
    if since is None:
        months = {}
        for r in records:
            key = r["at"].strftime("%Y-%m")
            months.setdefault(key, [0.0, 0])
            months[key][0] += r.get("cost_usd") or 0
            months[key][1] += 1
        return {"unit": "month", "bars": [{"label": k, "cost_usd": round(v[0], 6), "calls": v[1]} for k, v in sorted(months.items())]}
    days = {}
    for r in records:
        key = r["at"].date().isoformat()
        days.setdefault(key, [0.0, 0])
        days[key][0] += r.get("cost_usd") or 0
        days[key][1] += 1
    bars = []
    day = since.date()
    while day <= now.date() and len(bars) < MAX_DAY_BARS:
        cost, calls = days.get(day.isoformat(), (0.0, 0))
        bars.append({"label": day.isoformat(), "cost_usd": round(cost, 6), "calls": calls})
        day += timedelta(days=1)
    return {"unit": "day", "bars": bars}


def summarize(records, days=30, now=None):
    """The usage report for the last ``days`` days (0 = all time), newest calls first."""
    now = _aware(now) or datetime.now(timezone.utc)
    rows = []
    for r in records or []:
        at = _aware(r.get("at"))
        if at is not None:
            rows.append(dict(r, at=at))
    rows.sort(key=lambda r: r["at"], reverse=True)
    since = (now - timedelta(days=int(days) - 1)).replace(hour=0, minute=0, second=0, microsecond=0) if days else None
    period = [r for r in rows if since is None or r["at"] >= since]
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return {
        "ready": True,
        "days": int(days or 0),
        "since": since.isoformat() if since else None,
        "totals": _totals(period),
        "month_cost_usd": round(sum(r.get("cost_usd") or 0 for r in rows if r["at"] >= month_start), 6),
        "all_time_cost_usd": round(sum(r.get("cost_usd") or 0 for r in rows), 6),
        "by_feature": _group(period, "feature"),
        "by_model": _group(period, "model"),
        "chart": _bars(period, since, now),
        "recent": [dict(r, at=r["at"].isoformat()) for r in period[:RECENT_LIMIT]],
    }
