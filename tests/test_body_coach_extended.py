"""Coach math and proposal rules beyond AE1."""

from datetime import date

import pytest

from BodyCoach.adapt import adapt_calories, trend_rate_kg
from BodyCoach.plan import navy_bf, propose_plan


def test_navy_bf_male_worked_example() -> None:
    bf = navy_bf("male", 175, 94, 40, None)
    assert bf is not None
    assert 21 <= bf <= 23


def test_ae2_gain_muscle_at_high_bf_routes_to_cut_chain() -> None:
    plan = propose_plan(
        sex="male",
        born=date(1994, 12, 7),
        height_cm=175,
        weight_kg=79.5,
        waist_cm=94,
        neck_cm=40,
        hip_cm=None,
        training_days=4,
        daily_steps=10_000,
        start=date(2026, 10, 19),
        outcome="gain_muscle",
        chain_gain=False,
    )
    assert plan.phase == "cut"
    assert plan.phases[0].name == "cut"
    assert any(p.name == "bulk" for p in plan.phases)


def test_trend_rate_needs_five_weeks() -> None:
    assert trend_rate_kg([70.0, 69.5, 69.0, 68.5, 68.0]) is not None
    assert trend_rate_kg([70.0, 69.5, 69.0, None, 68.0]) is None


def test_ae5_too_fast_cut_adds_calories() -> None:
    chosen = 0.4
    trend = -0.7  # faster than 1.5 * 0.4 = 0.6 loss per week (negative)
    result = adapt_calories(
        phase="cut",
        current_calories=2000,
        chosen_rate_kg=chosen,
        trend_rate_kg=trend,
        slow_streak=0,
        bmr=1739,
        maintenance=2435,
    )
    assert result.next_calories == 2100
    assert "150%" in result.reason


def test_female_navy_requires_hip() -> None:
    assert navy_bf("female", 165, 70, 35, None) is None
    bf = navy_bf("female", 165, 70, 35, 95)
    assert bf is not None


def test_reverse_phase_currently_flat_maintenance_pending_r21() -> None:
    """Documents gap: R21 ramp (+⅓ gap × 2) not implemented yet."""
    plan = propose_plan(
        sex="male",
        born=date(1994, 12, 7),
        height_cm=175,
        weight_kg=79.5,
        waist_cm=94,
        neck_cm=40,
        hip_cm=None,
        training_days=4,
        daily_steps=10_000,
        start=date(2026, 10, 19),
        outcome="lose_fat",
        chain_gain=True,
    )
    reverse = next(p for p in plan.phases if p.name == "reverse")
    cut = next(p for p in plan.phases if p.name == "cut")
    assert reverse.calories > cut.calories
    assert reverse.calories == 2440
