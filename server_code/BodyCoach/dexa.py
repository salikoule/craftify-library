"""DEXA baseline, milestones, and measured RMR integration."""

from __future__ import annotations

from datetime import date, timedelta

MALE_BF_LADDER = (25.0, 22.0, 18.0, 15.0, 12.0, 10.0)
FEMALE_BF_LADDER = (30.0, 27.0, 24.0, 22.0, 18.0)


def weight_kg_at_bf(*, ffm_kg: float, bf_percent: float) -> float:
    if bf_percent >= 100:
        raise ValueError("bf_percent must be below 100")
    return round(ffm_kg / (1 - bf_percent / 100), 1)


def navy_dexa_offset(*, dexa_bf_percent: float, navy_bf_percent: float) -> float:
    """Add this to raw Navy % so tape at baseline matches DEXA truth."""
    return round(dexa_bf_percent - navy_bf_percent, 2)


def calibrated_navy_bf(*, navy_bf_percent: float, offset: float | None) -> float:
    if offset is None:
        return round(navy_bf_percent, 1)
    return round(navy_bf_percent + offset, 1)


def resolve_body_composition(
    *,
    weight_kg: float,
    navy_bf: float | None,
    dexa_bf_percent: float | None,
    dexa_ffm_kg: float | None,
) -> tuple[float | None, float | None, str]:
    """Return (body_fat %, fat-free mass kg, source label)."""
    if dexa_bf_percent is not None and dexa_ffm_kg is not None:
        return round(dexa_bf_percent, 1), round(dexa_ffm_kg, 2), "dexa"
    if dexa_bf_percent is not None:
        ffm = weight_kg * (1 - dexa_bf_percent / 100)
        return round(dexa_bf_percent, 1), round(ffm, 2), "dexa_bf"
    if dexa_ffm_kg is not None:
        bf = 100 * (1 - dexa_ffm_kg / weight_kg) if weight_kg > 0 else None
        return (round(bf, 1) if bf is not None else None), round(dexa_ffm_kg, 2), "dexa_ffm"
    if navy_bf is not None:
        ffm = weight_kg * (1 - navy_bf / 100)
        return round(navy_bf, 1), round(ffm, 2), "navy"
    return None, None, "none"


def build_bf_milestones(
    *,
    sex: str,
    start_bf: float,
    goal_bf: float,
    ffm_kg: float,
    start_weight_kg: float,
    weekly_rate_kg: float,
    start_date: date,
) -> list[dict]:
    """Stepping stones between current DEXA/truth BF and the phase goal (e.g. 25 → 22 → 18 → 12)."""
    ladder = MALE_BF_LADDER if sex == "male" else FEMALE_BF_LADDER
    steps = [b for b in ladder if b < start_bf - 0.05 and b >= goal_bf - 0.05]
    if not any(abs(b - goal_bf) < 0.05 for b in steps):
        steps.append(goal_bf)
    steps = sorted(set(steps), reverse=True)

    milestones: list[dict] = []
    for bf in steps:
        target_w = weight_kg_at_bf(ffm_kg=ffm_kg, bf_percent=bf)
        kg_to_lose = max(0.0, start_weight_kg - target_w)
        weeks = max(0, round(kg_to_lose / weekly_rate_kg)) if weekly_rate_kg > 0 else 0
        milestones.append(
            {
                "bf_percent": round(bf, 1),
                "target_weight_kg": target_w,
                "weeks_from_start": weeks,
                "forecast_date": (start_date + timedelta(days=weeks * 7)).isoformat(),
            }
        )
    return milestones
