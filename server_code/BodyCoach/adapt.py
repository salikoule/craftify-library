"""Weekly calorie adaptation (R16 simplified)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AdaptationResult:
    next_calories: int
    reason: str
    trend_rate_kg: float | None


def adapt_calories(
    *,
    phase: str,
    current_calories: int,
    chosen_rate_kg: float,
    trend_rate_kg: float | None,
    slow_streak: int,
    bmr: int,
    maintenance: int,
) -> AdaptationResult:
    floor = max(bmr, maintenance - 800)
    if phase == "recomp":
        if trend_rate_kg is not None and trend_rate_kg > 0.0025 * 80:
            return AdaptationResult(current_calories + 100, "Weight rose faster than recomp band. +100 kcal.", trend_rate_kg)
        if slow_streak >= 2 and trend_rate_kg is not None and trend_rate_kg < -0.005 * 80:
            return AdaptationResult(max(floor, current_calories - 100), "Two check-ins with fast loss on recomp. −100 kcal.", trend_rate_kg)
        return AdaptationResult(current_calories, "Recomp hold. Trend within guardrails.", trend_rate_kg)

    if phase == "bulk":
        if trend_rate_kg is not None and trend_rate_kg < chosen_rate_kg * 0.6:
            next_cal = min(maintenance + 600, current_calories + 100)
            return AdaptationResult(next_cal, "Gain slower than 60% of target rate. +100 kcal.", trend_rate_kg)
        if trend_rate_kg is not None and trend_rate_kg > chosen_rate_kg * 1.5:
            return AdaptationResult(max(maintenance, current_calories - 100), "Gain faster than 150% of target rate. −100 kcal.", trend_rate_kg)
        return AdaptationResult(current_calories, "Bulk hold. Trend matches the plan.", trend_rate_kg)

    # cut / reverse treated as cut for adaptation except reverse holds maintenance steps
    if phase == "reverse":
        return AdaptationResult(current_calories, "Reverse diet week — calories follow the maintenance ramp.", trend_rate_kg)

    if trend_rate_kg is None:
        return AdaptationResult(current_calories, "Not enough complete weeks for a trend yet. Hold week-1 target.", None)

    if trend_rate_kg < -chosen_rate_kg * 1.5:
        return AdaptationResult(min(maintenance, current_calories + 100), "Loss faster than 150% of chosen rate. +100 kcal.", trend_rate_kg)
    if trend_rate_kg > -chosen_rate_kg * 0.6:
        if slow_streak >= 2:
            return AdaptationResult(max(floor, current_calories - 100), "Two check-ins under 60% of target loss. −100 kcal.", trend_rate_kg)
        return AdaptationResult(current_calories, "Loss slower than target but only one week — hold calories.", trend_rate_kg)
    return AdaptationResult(current_calories, "Cut hold. Trend matches the chosen rate.", trend_rate_kg)


def trend_rate_kg(weekly_avgs: list[float | None]) -> float | None:
    """R16: needs 5+ weeks with data; compare 3-week blocks."""
    usable = [v for v in weekly_avgs if v is not None]
    if len(usable) < 5:
        return None
    recent = sum(usable[-3:]) / 3
    prior = sum(usable[-5:-2]) / 3
    return round((recent - prior) / 2, 3)
