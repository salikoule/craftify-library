"""Map BodyProfile → propose_plan kwargs."""

from __future__ import annotations

from typing import Any


def plan_kwargs_from_profile(profile: Any) -> dict:
    return {
        "sex": profile.sex,
        "born": profile.date_of_birth,
        "height_cm": profile.height_cm,
        "weight_kg": profile.start_weight_kg,
        "waist_cm": profile.waist_cm,
        "neck_cm": profile.neck_cm,
        "hip_cm": profile.hip_cm,
        "training_days": profile.training_days,
        "daily_steps": profile.daily_steps,
        "start": profile.start_date,
        "outcome": profile.outcome,
        "chain_gain": profile.chain_gain,
        "dexa_bf_percent": getattr(profile, "dexa_bf_percent", None),
        "dexa_ffm_kg": getattr(profile, "dexa_ffm_kg", None),
        "dexa_rmr_kcal": getattr(profile, "dexa_rmr_kcal", None),
    }
