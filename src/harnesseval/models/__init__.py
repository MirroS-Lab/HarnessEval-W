"""Video generation model registry, following the WBench package layout."""

from __future__ import annotations

from typing import Any

from .action.sana_wm_streaming import SanaWMStreamingModel
from .base import BaseVideoModel
from .camera.hy_worldplay import HYWorldPlayModel
from .text.seedance import SeedanceModel

MODEL_REGISTRY: dict[str, type[BaseVideoModel]] = {
    "seedance": SeedanceModel,
    "seedance-2.0": SeedanceModel,
    "sana-wm-streaming": SanaWMStreamingModel,
    "sana_wm_streaming": SanaWMStreamingModel,
    "hy-worldplay": HYWorldPlayModel,
    "hy-worldplay-1.5": HYWorldPlayModel,
    "hy_worldplay_1_5": HYWorldPlayModel,
}


def register_model(name: str, cls: type[BaseVideoModel]) -> None:
    MODEL_REGISTRY[name.lower()] = cls


def get_model(name: str, **kwargs: Any) -> BaseVideoModel:
    normalized = name.lower()
    if normalized not in MODEL_REGISTRY:
        available = ", ".join(sorted(MODEL_REGISTRY))
        raise ValueError(f"unknown model: {name}. Available: {available}")
    return MODEL_REGISTRY[normalized](**kwargs)


def list_models() -> list[str]:
    return sorted(MODEL_REGISTRY)


__all__ = [
    "BaseVideoModel",
    "HYWorldPlayModel",
    "SanaWMStreamingModel",
    "SeedanceModel",
    "get_model",
    "list_models",
    "register_model",
]
