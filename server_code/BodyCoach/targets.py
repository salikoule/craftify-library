"""Align Navy tape targets with planned weight paths."""

from __future__ import annotations

from .plan import navy_bf


def waist_for_navy_bf(
    sex: str,
    height_cm: float,
    neck_cm: float,
    target_bf: float,
    hip_cm: float | None = None,
) -> float | None:
    """Waist (cm) that yields ``target_bf`` with fixed neck/height — for planning demos and BF tgt column."""
    lo = neck_cm + 0.5
    hi = 160.0
    best = None
    for _ in range(48):
        mid = (lo + hi) / 2
        bf = navy_bf(sex, height_cm, mid, neck_cm, hip_cm)
        if bf is None:
            return None
        best = mid
        if bf > target_bf:
            hi = mid
        else:
            lo = mid
    return round(best, 1) if best is not None else None


def planned_waist_cm(*, start_waist: float, goal_waist: float, week: int, total_weeks: int) -> float:
    if total_weeks <= 1:
        return goal_waist
    progress = min(1.0, max(0.0, (week - 1) / (total_weeks - 1)))
    return round(start_waist + (goal_waist - start_waist) * progress, 1)


def bf_from_planned_waist(
    sex: str,
    height_cm: float,
    neck_cm: float,
    waist_cm: float,
    hip_cm: float | None = None,
) -> float | None:
    bf = navy_bf(sex, height_cm, waist_cm, neck_cm, hip_cm)
    return round(bf, 1) if bf is not None else None


def recomp_bf_goal(start_bf: float, sex: str) -> float:
    floor = 10.0 if sex == "male" else 18.0
    return round(max(floor, start_bf - 3.0), 1)
