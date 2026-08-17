"""Pure implementation of the HarnessEval formulas."""

from __future__ import annotations

from typing import Any

from .skills.skill_render_quality import (
    result_from_metrics as render_quality_result,
    score_components as render_quality_score,
)
from .skills.skill_motion_quality import (
    result_from_metrics as motion_quality_result,
    score_components as motion_quality_score,
)
from .skills.skill_appearance_consistency import (
    result_from_metrics as appearance_consistency_result,
    score_components as appearance_consistency_score,
)
from .skills.skill_physical_plausibility import (
    result_from_metrics as physical_plausibility_result,
    score_components as physical_plausibility_score,
)
from .skills.skill_drift_degradation import result_from_chunks as _drift_result
from .skills.skill_return_consistency import (
    frame_similarity as _return_frame_similarity,
    result_from_evidence as _return_result,
)


def quality_dimensions(metrics: dict[str, Any]) -> dict[str, float | None]:
    return {
        "render_quality": render_quality_score(metrics),
        "motion_quality": motion_quality_score(metrics),
        "appearance_quality": appearance_consistency_score(metrics),
        "physical_quality": physical_plausibility_score(metrics),
    }


def observation_skills(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        render_quality_result(metrics),
        motion_quality_result(metrics),
        appearance_consistency_result(metrics),
        physical_plausibility_result(metrics),
    ]


def drift_skill(chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Compatibility adapter for callers that have not moved to the skill module."""

    return _drift_result(chunks)


def frame_similarity(components: dict[str, Any]) -> float:
    """Compatibility adapter for callers that have not moved to the skill module."""

    return _return_frame_similarity(components)


def return_skill(bundle: dict[str, Any]) -> dict[str, Any]:
    """Compatibility adapter for callers that have not moved to the skill module."""

    return _return_result(bundle)
