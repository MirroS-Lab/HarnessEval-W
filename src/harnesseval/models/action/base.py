"""Base class for native action-conditioned AR models."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from ..conditioning import ConditionedVideoModel
from ..text.prompt_builder import prompt_for_case
from .actions import case_to_actions


class ActionConditionedModel(ConditionedVideoModel):
    @abstractmethod
    def generate_with_actions(
        self,
        image: str,
        actions: list[dict[str, Any]],
        output_path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run one native AR rollout over the complete action sequence."""

    def generate_case(
        self, case: dict[str, Any], job: dict[str, Any]
    ) -> dict[str, Any]:
        conditioning = case_to_actions(case)
        prompt = prompt_for_case(case)
        result = self.generate_with_actions(
            image=str(job["initial_observation"]),
            actions=conditioning["actions"],
            output_path=str(job["output_video"]),
            prompt=prompt,
            perspective=conditioning["perspective"],
        )
        result["prompt"] = prompt
        result["generation"] = {
            "conditioning": "native_action_sequence",
            "turn_count": conditioning["turn_count"],
            "perspective": conditioning["perspective"],
            "actions": conditioning["actions"],
            **(result.get("generation") or {}),
        }
        return result
