"""Base class for native camera-conditioned AR models."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from ..conditioning import ConditionedVideoModel
from ..text.prompt_builder import prompt_for_case


class CameraConditionedModel(ConditionedVideoModel):
    @abstractmethod
    def build_pose_trajectory(self, case: dict[str, Any]) -> dict[str, Any]:
        """Convert a case into this model's complete native pose trajectory."""

    @abstractmethod
    def generate_with_poses(
        self,
        image: str,
        poses: dict[str, Any],
        output_path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run one native AR rollout over the complete pose trajectory."""

    def generate_case(
        self, case: dict[str, Any], job: dict[str, Any]
    ) -> dict[str, Any]:
        conditioning = self.build_pose_trajectory(case)
        prompt = prompt_for_case(case)
        result = self.generate_with_poses(
            image=str(job["initial_observation"]),
            poses=conditioning["poses"],
            output_path=str(job["output_video"]),
            prompt=prompt,
            perspective=conditioning["perspective"],
            video_length=conditioning["video_length"],
            total_latents=conditioning["total_latents"],
        )
        result["prompt"] = prompt
        result["generation"] = {
            "conditioning": "native_pose_trajectory",
            "turn_count": conditioning["turn_count"],
            "latents_per_turn": conditioning["latents_per_turn"],
            "total_latents": conditioning["total_latents"],
            "video_length": conditioning["video_length"],
            "perspective": conditioning["perspective"],
            **(result.get("generation") or {}),
        }
        return result
