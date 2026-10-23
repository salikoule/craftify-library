"""Build the week-by-week tracker rows shown in the UI."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from .dexa import calibrated_navy_bf, navy_dexa_offset
from .plan import macro_targets, navy_bf, propose_plan
from .plan_kwargs import plan_kwargs_from_profile
from .targets import bf_from_planned_waist, planned_waist_cm, recomp_bf_goal, waist_for_navy_bf

RECOMP_HORIZON_WEEKS = 24


@dataclass
class WeekRow:
    week: int
    week_start: date
    phase: str
    target_weight_kg: float | None
    target_bf_percent: float | None
    target_calories: int
    protein_g: int
    fat_g: int
    carbs_g: int
    actual_weight_kg: float | None
    weight_delta_kg: float | None
    waist_cm: float | None
    neck_cm: float | None
    bf_percent: float | None
    bf_delta: float | None
    training_sessions: int | None
    daily_steps: int | None
    training_feel: str | None
    adherence: str | None
    trend_rate_kg: float | None
    status: str
    notes: str | None
    check_in_date: date | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "week": self.week,
            "week_start": self.week_start.isoformat(),
            "week_end": (self.week_start + timedelta(days=6)).isoformat(),
            "phase": self.phase,
            "target_weight_kg": self.target_weight_kg,
            "target_bf_percent": self.target_bf_percent,
            "target_calories": self.target_calories,
            "protein_g": self.protein_g,
            "fat_g": self.fat_g,
            "carbs_g": self.carbs_g,
            "actual_weight_kg": self.actual_weight_kg,
            "weight_delta_kg": self.weight_delta_kg,
            "waist_cm": self.waist_cm,
            "neck_cm": self.neck_cm,
            "bf_percent": self.bf_percent,
            "bf_delta": self.bf_delta,
            "training_sessions": self.training_sessions,
            "daily_steps": self.daily_steps,
            "training_feel": self.training_feel,
            "adherence": self.adherence,
            "trend_rate_kg": self.trend_rate_kg,
            "status": self.status,
            "notes": self.notes,
            "check_in_date": self.check_in_date.isoformat() if self.check_in_date else None,
        }


def monday_of_week(day: date) -> date:
    """Monday starting the Mon–Sun week that contains ``day``."""
    return day - timedelta(days=day.weekday())


def _phase_name(week_start: date, phases: list[dict[str, Any]]) -> str:
    if not phases:
        return "cut"
    first_start = date.fromisoformat(phases[0]["start"])
    if week_start < first_start:
        return phases[0]["name"]
    for phase in phases:
        start = date.fromisoformat(phase["start"])
        end = date.fromisoformat(phase["end"]) if phase.get("end") else None
        if week_start < start:
            continue
        if end is None or week_start <= end:
            return phase["name"]
    return phases[-1]["name"]


def _macros(calories: int, weight_kg: float, protein_per_kg: float = 2.2) -> tuple[int, int, int]:
    protein = round(protein_per_kg * weight_kg)
    fat = round((calories * 0.25) / 9)
    carbs = round((calories - protein * 4 - fat * 9) / 4)
    if carbs < 0:
        fat = max(0, round((calories - protein * 4) / 9))
        carbs = max(0, round((calories - protein * 4 - fat * 9) / 4))
    return protein, fat, carbs


def _coach_state(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def week_index_for(today: date, start: date) -> int:
    anchor = monday_of_week(start)
    if today < anchor:
        return 1
    return 1 + (today - anchor).days // 7


def macro_weight_kg(
    *,
    start_weight: float,
    target_weight: float | None,
    actual: float | None,
    prior_week_avgs: list[float | None],
) -> float:
    """R5: three-week average when available, else actual, else this week's target, else start."""
    usable = [v for v in prior_week_avgs if v is not None]
    if len(usable) >= 3:
        return round(sum(usable[-3:]) / 3, 2)
    if actual is not None:
        return actual
    if target_weight is not None:
        return target_weight
    return start_weight


def average_weight_in_week(weights: list[tuple[date, float]], week_start_monday: date) -> float | None:
    """``week_start_monday`` is the Monday; the window is Mon–Sun inclusive."""
    end = week_start_monday + timedelta(days=6)
    values = [kg for logged, kg in weights if week_start_monday <= logged <= end]
    if len(values) < 4:
        return round(sum(values) / len(values), 2) if values else None
    return round(sum(values) / len(values), 2)


def build_schedule(
    *,
    profile: Any,
    weights: list[Any],
    logs: list[Any],
    today: date | None = None,
) -> list[dict[str, Any]]:
    today = today or date.today()
    phases = json.loads(profile.phases_json)
    proposal = propose_plan(**plan_kwargs_from_profile(profile))
    end = profile.forecast_end or profile.start_date + timedelta(days=35 * 7)
    first_monday = monday_of_week(profile.start_date)
    weight_pairs = [(row.logged_on, row.weight_kg) for row in weights]
    logs_by_week = {row.week_index: row for row in logs}
    state = _coach_state(getattr(profile, "coach_state_json", None))
    issued: dict[str, int] = state.get("issued_calories", {})
    weekly_rate = state.get("weekly_rate_kg", proposal.weekly_rate_kg)
    bf_offset: float | None = state.get("navy_dexa_offset")
    if bf_offset is None and getattr(profile, "dexa_bf_percent", None) is not None:
        anchor_navy = state.get("navy_bf_percent") or proposal.navy_bf_percent
        if anchor_navy is not None:
            bf_offset = navy_dexa_offset(
                dexa_bf_percent=float(profile.dexa_bf_percent),
                navy_bf_percent=float(anchor_navy),
            )
    start_bf = proposal.bf_percent
    target_bf = proposal.target_bf_percent
    protein_cut = getattr(profile, "protein_g_per_kg_cut", None)
    protein_bulk = getattr(profile, "protein_g_per_kg_bulk", None)
    use_dexa_bf_plan = getattr(profile, "dexa_bf_percent", None) is not None
    goal_waist = None
    if target_bf is not None and profile.outcome != "recomp" and not use_dexa_bf_plan:
        goal_waist = waist_for_navy_bf(
            profile.sex,
            profile.height_cm,
            profile.neck_cm,
            target_bf,
            profile.hip_cm,
        )

    rows: list[WeekRow] = []
    week_avgs: list[float | None] = []
    week = 1
    week_start = first_monday
    cut_weeks = max(1, round((profile.start_weight_kg - (proposal.target_weight_kg or profile.start_weight_kg)) / weekly_rate)) if weekly_rate else 19

    while week_start <= end and week <= 52:
        phase = _phase_name(week_start, phases)
        phase_entry = next((p for p in phases if p["name"] == phase), phases[0])
        base_calories = int(phase_entry["calories"])
        calories = int(issued.get(str(week), base_calories if week == 1 else issued.get(str(week - 1), base_calories)))

        if profile.outcome == "recomp":
            target_weight = round(profile.start_weight_kg, 1)
        elif phase == "cut" and proposal.target_weight_kg is not None:
            target_weight = round(profile.start_weight_kg - weekly_rate * (week - 1), 1)
            target_weight = max(proposal.target_weight_kg, target_weight)
        elif phase == "bulk" and proposal.target_weight_kg is not None:
            bulk_rate = 0.0025 * proposal.target_weight_kg
            target_weight = round(proposal.target_weight_kg + bulk_rate * max(0, week - cut_weeks - 3), 1)
        else:
            target_weight = proposal.target_weight_kg

        if profile.outcome == "recomp" and start_bf is not None:
            goal = target_bf if target_bf is not None else recomp_bf_goal(start_bf, profile.sex)
            progress = min(1.0, (week - 1) / max(RECOMP_HORIZON_WEEKS - 1, 1))
            target_bf_week = round(start_bf + (goal - start_bf) * progress, 1)
        elif phase == "cut" and start_bf is not None and target_bf is not None:
            if use_dexa_bf_plan:
                progress = min(1.0, (week - 1) / max(cut_weeks, 1))
                target_bf_week = round(start_bf + (target_bf - start_bf) * progress, 1)
            elif goal_waist is not None:
                planned_waist = planned_waist_cm(
                    start_waist=profile.waist_cm,
                    goal_waist=goal_waist,
                    week=week,
                    total_weeks=cut_weeks,
                )
                target_bf_week = bf_from_planned_waist(
                    profile.sex,
                    profile.height_cm,
                    profile.neck_cm,
                    planned_waist,
                    profile.hip_cm,
                )
            else:
                progress = min(1.0, (week - 1) / max(cut_weeks, 1))
                target_bf_week = round(start_bf + (target_bf - start_bf) * progress, 1)
        elif phase in {"reverse", "bulk"}:
            target_bf_week = target_bf
        else:
            target_bf_week = target_bf

        actual_from_scale = average_weight_in_week(weight_pairs, week_start)
        log = logs_by_week.get(week)
        actual = log.avg_weight_kg if log and log.avg_weight_kg is not None else actual_from_scale

        macro_weight = macro_weight_kg(
            start_weight=profile.start_weight_kg,
            target_weight=target_weight,
            actual=actual,
            prior_week_avgs=week_avgs,
        )
        protein, fat, carbs = macro_targets(
            calories,
            macro_weight,
            phase,
            protein_g_per_kg_cut=protein_cut,
            protein_g_per_kg_bulk=protein_bulk,
        )
        week_avgs.append(actual)
        weight_delta = None
        if actual is not None and target_weight is not None:
            weight_delta = round(actual - target_weight, 2)

        waist = log.waist_cm if log else None
        neck = log.neck_cm if log else None
        bf = log.bf_percent if log else None
        if bf is None and waist and neck:
            bf_val = navy_bf(profile.sex, profile.height_cm, waist, neck, profile.hip_cm)
            bf = round(bf_val, 1) if bf_val is not None else None
        if bf is not None:
            bf = calibrated_navy_bf(navy_bf_percent=bf, offset=bf_offset)
        bf_delta = round(bf - target_bf_week, 1) if bf is not None and target_bf_week is not None else None

        status = "planned"
        if week_start <= today:
            if log:
                status = log.status or "logged"
            elif actual_from_scale:
                status = "partial"
            elif week_start + timedelta(days=6) < today:
                status = "missed"
            else:
                status = "current" if week == week_index_for(today, profile.start_date) else "due"

        rows.append(
            WeekRow(
                week=week,
                week_start=week_start,
                phase=phase,
                target_weight_kg=target_weight,
                target_bf_percent=target_bf_week,
                target_calories=calories,
                protein_g=protein,
                fat_g=fat,
                carbs_g=carbs,
                actual_weight_kg=actual,
                weight_delta_kg=weight_delta,
                waist_cm=waist,
                neck_cm=neck,
                bf_percent=bf,
                bf_delta=bf_delta,
                training_sessions=log.training_sessions if log else None,
                daily_steps=log.daily_steps if log else None,
                training_feel=log.training_feel if log else None,
                adherence=log.adherence if log else None,
                trend_rate_kg=log.trend_rate_kg if log else None,
                status=status,
                notes=log.notes if log else None,
                check_in_date=log.check_in_date if log else None,
            )
        )
        week += 1
        week_start += timedelta(days=7)

    return [row.as_dict() for row in rows]
