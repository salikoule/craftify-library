"""Calorie, macro, and phase proposal. Pure functions, no database."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, timedelta

from .dexa import build_bf_milestones, resolve_body_composition


def age_on(born: date, on: date) -> int:
    years = on.year - born.year
    if (on.month, on.day) < (born.month, born.day):
        years -= 1
    return years


def navy_bf(sex: str, height_cm: float, waist_cm: float, neck_cm: float, hip_cm: float | None) -> float | None:
    if waist_cm <= neck_cm or height_cm <= 0:
        return None
    if sex == "female":
        if hip_cm is None:
            return None
        denom = 1.29579 - 0.35004 * math.log10(waist_cm + hip_cm - neck_cm) + 0.22100 * math.log10(height_cm)
    else:
        denom = 1.0324 - 0.19077 * math.log10(waist_cm - neck_cm) + 0.15456 * math.log10(height_cm)
    if denom <= 0:
        return None
    return 495 / denom - 450


def bmr(sex: str, weight_kg: float, height_cm: float, years: int) -> int:
    offset = 5 if sex == "male" else -161
    return round(10 * weight_kg + 6.25 * height_cm - 5 * years + offset)


def activity_multiplier(training_days: int, daily_steps: int) -> float:
    raw = 1.2 + 0.025 * training_days + daily_steps / 100_000
    return round(min(raw, 1.6), 3)


def nearest_10(value: float) -> int:
    return int(round(value / 10.0) * 10)


@dataclass
class Phase:
    name: str
    start: date
    end: date | None
    calories: int
    summary: str


@dataclass
class PlanProposal:
    bmr: int
    multiplier: float
    tdee: int
    calories: int
    protein_g: int
    fat_g: int
    carbs_g: int
    bf_percent: float | None
    target_bf_percent: float | None
    target_weight_kg: float | None
    weekly_rate_kg: float
    reason: str
    phase: str
    phases: list[Phase]
    forecast_end: date | None
    weight_series: list[tuple[str, float]]
    navy_bf_percent: float | None = None
    bmr_source: str = "mifflin"
    bmr_mifflin: int | None = None
    bf_milestones: list[dict] = field(default_factory=list)


def clamp_protein_per_kg(phase: str, value: float | None) -> float:
    """Cut/reverse/recomp: 2.0–2.4 g/kg. Bulk: 1.6–2.2 g/kg."""
    if phase == "bulk":
        default = 1.9
        lo, hi = 1.6, 2.2
    else:
        default = 2.2
        lo, hi = 2.0, 2.4
    chosen = default if value is None else value
    return round(min(hi, max(lo, chosen)), 2)


def protein_per_kg_for_phase(
    phase: str,
    *,
    protein_g_per_kg_cut: float | None = None,
    protein_g_per_kg_bulk: float | None = None,
) -> float:
    if phase == "bulk":
        return clamp_protein_per_kg("bulk", protein_g_per_kg_bulk)
    return clamp_protein_per_kg("cut", protein_g_per_kg_cut)


def macro_targets(
    calories: int,
    weight_kg: float,
    phase: str,
    *,
    protein_g_per_kg_cut: float | None = None,
    protein_g_per_kg_bulk: float | None = None,
) -> tuple[int, int, int]:
    rate = protein_per_kg_for_phase(
        phase,
        protein_g_per_kg_cut=protein_g_per_kg_cut,
        protein_g_per_kg_bulk=protein_g_per_kg_bulk,
    )
    return _macros(calories, weight_kg, rate)


def bulk_bf_ceiling(sex: str) -> float:
    return 16.0 if sex == "male" else 26.0


def _macros(calories: int, weight_kg: float, protein_per_kg: float) -> tuple[int, int, int]:
    protein = round(protein_per_kg * weight_kg)
    fat = round((calories * 0.25) / 9)
    carbs = round((calories - protein * 4 - fat * 9) / 4)
    if carbs < 0:
        fat = max(0, round((calories - protein * 4) / 9))
        carbs = max(0, round((calories - protein * 4 - fat * 9) / 4))
    return protein, fat, carbs


def propose_plan(
    *,
    sex: str,
    born: date,
    height_cm: float,
    weight_kg: float,
    waist_cm: float,
    neck_cm: float,
    hip_cm: float | None,
    training_days: int,
    daily_steps: int,
    start: date,
    outcome: str,
    chain_gain: bool,
    dexa_bf_percent: float | None = None,
    dexa_ffm_kg: float | None = None,
    dexa_rmr_kcal: int | None = None,
) -> PlanProposal:
    years = age_on(born, start)
    mifflin = bmr(sex, weight_kg, height_cm, years)
    metabolic = int(dexa_rmr_kcal) if dexa_rmr_kcal is not None else mifflin
    bmr_source = "dexa_rmr" if dexa_rmr_kcal is not None else "mifflin"
    multiplier = activity_multiplier(training_days, daily_steps)
    maintenance = round(metabolic * multiplier)
    navy = navy_bf(sex, height_cm, waist_cm, neck_cm, hip_cm)
    body_fat, ffm_kg, comp_source = resolve_body_composition(
        weight_kg=weight_kg,
        navy_bf=navy,
        dexa_bf_percent=dexa_bf_percent,
        dexa_ffm_kg=dexa_ffm_kg,
    )

    if outcome == "recomp":
        calories = nearest_10(maintenance)
        start_bf = None if body_fat is None else round(body_fat, 1)
        goal_bf = None if start_bf is None else max(10.0 if sex == "male" else 18.0, start_bf - 3.0)
        protein, fat, carbs = _macros(calories, weight_kg, clamp_protein_per_kg("cut", None))
        reason = "Recomp holds maintenance. Scale weight stays near start while tape BF trends toward "
        reason += f"{goal_bf:.0f}%" if goal_bf is not None else "your waist-led goal"
        reason += " (about 3 points over ~24 weeks if check-ins stay on plan)."
        if comp_source.startswith("dexa"):
            reason += f" Body fat baseline uses DEXA ({start_bf}%)."
        return PlanProposal(
            bmr=metabolic,
            multiplier=multiplier,
            tdee=maintenance,
            calories=calories,
            protein_g=protein,
            fat_g=fat,
            carbs_g=carbs,
            bf_percent=start_bf,
            target_bf_percent=round(goal_bf, 1) if goal_bf is not None else None,
            target_weight_kg=round(weight_kg, 1),
            weekly_rate_kg=0,
            reason=reason,
            phase="recomp",
            phases=[Phase("recomp", start, None, calories, "Maintenance calories. No scheduled bulk.")],
            forecast_end=None,
            weight_series=[("Now", round(weight_kg, 1))],
            navy_bf_percent=None if navy is None else round(navy, 1),
            bmr_source=bmr_source,
            bmr_mifflin=mifflin,
            bf_milestones=[],
        )

    cut_rate = 0.005 * weight_kg
    target_bf = None
    target_weight = None
    lean = ffm_kg if ffm_kg is not None else (weight_kg * (1 - body_fat / 100) if body_fat is not None else None)
    if body_fat is not None and outcome == "lose_fat":
        proposed = 12.0 if sex == "male" and body_fat > 15 else 22.0 if sex == "female" and body_fat > 25 else max(body_fat - 2, 10 if sex == "male" else 18)
        target_bf = proposed
        if lean is not None:
            target_weight = lean / (1 - target_bf / 100)
    elif outcome == "gain_muscle" and body_fat is not None and (
        (sex == "male" and body_fat > 18) or (sex == "female" and body_fat > 28)
    ):
        target_bf = 12.0 if sex == "male" else 22.0
        if lean is not None:
            target_weight = lean / (1 - target_bf / 100)
        chain_gain = True
        outcome = "lose_fat"

    if outcome == "gain_muscle" and target_weight is None:
        rate = 0.0025 * weight_kg
        surplus = rate * 7700 / 7
        calories = nearest_10(maintenance + surplus)
        protein, fat, carbs = macro_targets(calories, weight_kg, "bulk")
        end = start + timedelta(days=12 * 7)
        return PlanProposal(
            bmr=metabolic,
            multiplier=multiplier,
            tdee=maintenance,
            calories=calories,
            protein_g=protein,
            fat_g=fat,
            carbs_g=carbs,
            bf_percent=None if body_fat is None else round(body_fat, 1),
            target_bf_percent=None,
            target_weight_kg=round(weight_kg + rate * 12, 1),
            weekly_rate_kg=round(rate, 3),
            reason="Bulk at 0.25% of body weight per week for 12 weeks.",
            phase="bulk",
            phases=[Phase("bulk", start, end, calories, "Surplus for 12 weeks, then maintenance.")],
            forecast_end=end,
            weight_series=[("Start", round(weight_kg, 1)), ("Week 12", round(weight_kg + rate * 12, 1))],
            navy_bf_percent=None if navy is None else round(navy, 1),
            bmr_source=bmr_source,
            bmr_mifflin=mifflin,
            bf_milestones=[],
        )

    deficit = cut_rate * 7700 / 7
    calories = nearest_10(maintenance - deficit)
    protein, fat, carbs = _macros(calories, weight_kg, 2.2)
    weeks = 19
    if target_weight is not None:
        weeks = max(1, round((weight_kg - target_weight) / cut_rate))
    cut_end = start + timedelta(days=weeks * 7)
    reverse_end = cut_end + timedelta(days=21)
    bulk_rate = 0.0025 * (target_weight or weight_kg)
    bulk_end = reverse_end + timedelta(days=12 * 7) if chain_gain else None
    maintenance_10 = nearest_10(maintenance)
    phases = [
        Phase("cut", start, cut_end, calories, f"Lose about {cut_rate:.2f} kg per week."),
        Phase("reverse", cut_end, reverse_end, maintenance_10, "Three weeks back to maintenance."),
    ]
    if chain_gain and bulk_end is not None:
        bulk_calories = nearest_10(maintenance + bulk_rate * 7700 / 7)
        phases.append(Phase("bulk", reverse_end, bulk_end, bulk_calories, "Then gain about 0.25% of body weight per week."))
    series: list[tuple[str, float]] = []
    for week in range(0, weeks + 1, max(1, weeks // 8)):
        series.append((f"W{week}", round(weight_kg - cut_rate * week, 1)))
    if series[-1][0] != f"W{weeks}":
        series.append((f"W{weeks}", round(target_weight or weight_kg - cut_rate * weeks, 1)))
    bf_text = f"{body_fat:.1f}% body fat" if body_fat is not None else "body fat not measured yet"
    target_text = f"{target_bf:.0f}%" if target_bf is not None else "the weight target"
    reason = f"Cut toward {target_text}. You are starting at {bf_text}. Week 1 is {calories:,} kcal."
    if comp_source.startswith("dexa"):
        reason += f" Targets use DEXA fat-free mass ({lean:.1f} kg)."
        if navy is not None:
            gap = round(body_fat - navy, 1)
            reason += (
                f" Navy tape reads ~{navy:.1f}% at baseline; we add {gap:+.1f} pts to weekly tape"
                " so check-ins sit on the same scale as DEXA targets."
            )
    if bmr_source == "dexa_rmr":
        reason += f" TDEE uses your measured RMR {metabolic} kcal (Mifflin would be {mifflin})."
    milestones: list[dict] = []
    if body_fat is not None and target_bf is not None and lean is not None and outcome == "lose_fat":
        milestones = build_bf_milestones(
            sex=sex,
            start_bf=body_fat,
            goal_bf=target_bf,
            ffm_kg=lean,
            start_weight_kg=weight_kg,
            weekly_rate_kg=cut_rate,
            start_date=start,
        )
    return PlanProposal(
        bmr=metabolic,
        multiplier=multiplier,
        tdee=maintenance,
        calories=calories,
        protein_g=protein,
        fat_g=fat,
        carbs_g=carbs,
        bf_percent=None if body_fat is None else round(body_fat, 1),
        target_bf_percent=None if target_bf is None else round(target_bf, 1),
        target_weight_kg=None if target_weight is None else round(target_weight, 1),
        weekly_rate_kg=round(cut_rate, 3),
        reason=reason,
        phase="cut",
        phases=phases,
        forecast_end=bulk_end or reverse_end,
        weight_series=series,
        navy_bf_percent=None if navy is None else round(navy, 1),
        bmr_source=bmr_source,
        bmr_mifflin=mifflin,
        bf_milestones=milestones,
    )
