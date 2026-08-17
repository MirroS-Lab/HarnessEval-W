"""Protocol aggregation kept separate from metric execution."""

from __future__ import annotations

import math
from typing import Any, Iterable

from .protocols import CORE_SKILLS, EvaluationProtocol, canonical_family


def clean_float(value: Any) -> Any:
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return round(value, 6)
    if isinstance(value, dict):
        return {key: clean_float(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean_float(item) for item in value]
    return value


def numeric(value: Any) -> float | None:
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def mean_valid(values: Iterable[Any]) -> float | None:
    valid = [float(value) for value in values if numeric(value) is not None]
    return round(sum(valid) / len(valid), 6) if valid else None


def soft_threshold(value: float, low: float, high: float) -> float:
    if value <= low:
        return 0.0
    if value >= high:
        return 1.0
    return (value - low) / (high - low)


def skill_result(
    skill_id: str,
    status: str,
    score: float | None,
    metrics: dict[str, Any] | None = None,
    diagnostics: dict[str, Any] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    return clean_float(
        {
            "skill_id": skill_id,
            "status": status,
            "score": score,
            "metrics": metrics or {},
            "diagnostics": diagnostics or {},
            "notes": notes or [],
        }
    )


def skills_by_id(skills: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(skill["skill_id"]): skill for skill in skills}


def aggregate_case_score(
    skills: list[dict[str, Any]],
    probe_family: str,
    core_skill_ids: list[str] | tuple[str, ...] | None,
    routing_mode: str | None,
) -> dict[str, Any]:
    by_id = skills_by_id(skills)
    selected_ids = list(core_skill_ids or CORE_SKILLS.get(canonical_family(probe_family), ()))
    core = [by_id[skill_id] for skill_id in selected_ids if skill_id in by_id]
    if not core:
        observation_ids = {
            "render_quality_inspector",
            "render_physical_plausibility_inspector",
            "motion_quality_inspector",
            "appearance_consistency_inspector",
            "physical_plausibility_inspector",
        }
        core = [skill for skill in skills if skill.get("skill_id") not in observation_ids]
    valid = [skill for skill in core if numeric(skill.get("score")) is not None]
    if not valid:
        return {
            "score": None,
            "status": "invalid",
            "score_type": "taxonomy_core",
            "core_skill_ids": [skill.get("skill_id") for skill in core],
            "weights": {},
            "routing_mode": routing_mode,
        }
    weight = 1.0 / len(valid)
    weights = {str(skill["skill_id"]): weight for skill in valid}
    score = round(sum(float(skill["score"]) * weight for skill in valid), 6)
    statuses = {skill.get("status") for skill in core}
    if "failed" in statuses:
        status = "partial_failed"
    elif "invalid" in statuses:
        status = "partial_invalid"
    elif any(str(value).endswith("judge_required") for value in statuses):
        status = "proxy_judge_required"
    else:
        status = "ok"
    return {
        "score": score,
        "status": status,
        "score_type": "taxonomy_core",
        "core_skill_ids": [skill.get("skill_id") for skill in core],
        "weights": weights,
        "routing_mode": routing_mode,
    }


def aggregate_observation_quality(
    skills: list[dict[str, Any]], protocol: EvaluationProtocol
) -> dict[str, Any]:
    by_id = skills_by_id(skills)
    dimensions = {
        skill_id: (by_id.get(skill_id) or {}).get("score")
        for skill_id in protocol.observation_skills
    }
    complete = all(numeric(value) is not None for value in dimensions.values())
    evidence_score = mean_valid(dimensions.values()) if complete else None
    return clean_float(
        {
            "status": "ok" if complete else "invalid_evidence",
            "dimensions": dimensions,
            "evidence_score": evidence_score,
            "score_type": "observation_evidence",
        }
    )


def aggregate_evidence_adjusted_score(
    case_score: dict[str, Any],
    observation_quality: dict[str, Any],
    video_validity: dict[str, Any] | None,
) -> dict[str, Any]:
    core = numeric(case_score.get("score"))
    if core is None:
        return {
            "score": None,
            "status": case_score.get("status"),
            "score_type": "evidence_adjusted_cap",
        }
    caps = [
        value
        for value in (
            (video_validity or {}).get("score"),
            observation_quality.get("evidence_score"),
        )
        if numeric(value) is not None
    ]
    if not caps:
        return {
            "score": core,
            "status": case_score.get("status"),
            "score_type": "evidence_adjusted_cap",
        }
    cap = min(float(value) for value in caps)
    adjusted = round(min(core, cap), 6)
    status = case_score.get("status")
    if adjusted < core:
        status = f"{status}_evidence_capped" if status else "evidence_capped"
    return {
        "score": adjusted,
        "status": status,
        "score_type": "evidence_adjusted_cap",
        "cap": round(cap, 6),
    }
