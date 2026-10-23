from datetime import date

from BodyCoach.plan import propose_plan


def test_worked_example_week_one() -> None:
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
    assert plan.bmr == 1739
    assert plan.multiplier == 1.4
    assert plan.tdee == 2435
    assert plan.calories == 2000
    assert plan.protein_g == 175
    assert plan.target_bf_percent == 12
    assert plan.phase == "cut"
    assert [phase.name for phase in plan.phases] == ["cut", "reverse", "bulk"]
