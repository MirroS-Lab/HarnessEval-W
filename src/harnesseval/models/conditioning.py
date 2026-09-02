"""Shared base for native action- and camera-conditioned models."""

from __future__ import annotations

from typing import Any

from .base import BaseVideoModel


class ConditionedVideoModel(BaseVideoModel):
    """Conditioned models consume a full control sequence instead of text turns."""

    default_workers = 1

    def generate(
        self,
        prompt: str,
        image: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        raise NotImplementedError(
            "use generate_with_actions() or generate_with_poses()"
        )
