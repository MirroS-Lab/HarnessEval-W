"""UniDepth helpers used by the MegaSAM adapter."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
from safetensors.torch import load_file


LONG_DIM = 640
UNIDEPTH_REVISION = "1d0d3c52f60b5164629d279bb9a7546458e6dcc4"


def find_unidepth_weights(weights_root: Path) -> Path:
    explicit = os.environ.get("HARNESSEVAL_UNIDEPTH_WEIGHTS")
    if explicit:
        path = Path(explicit)
        if path.exists():
            return path
    snapshot = (
        weights_root
        / "huggingface"
        / "hub"
        / "models--lpiccinelli--unidepth-v2-vitl14"
        / "snapshots"
        / UNIDEPTH_REVISION
        / "model.safetensors"
    )
    if snapshot.exists():
        return snapshot
    candidates = sorted(
        (weights_root / "huggingface" / "hub" / "models--lpiccinelli--unidepth-v2-vitl14").glob(
            "snapshots/*/model.safetensors"
        )
    )
    if candidates:
        return candidates[-1]
    raise FileNotFoundError(
        "UniDepth model.safetensors not found. Set HARNESSEVAL_UNIDEPTH_WEIGHTS or populate "
        f"{weights_root}/huggingface/hub/models--lpiccinelli--unidepth-v2-vitl14/."
    )


def load_unidepth_model(unidepth_root: Path, weights_root: Path, device: torch.device) -> Any:
    if str(unidepth_root) not in sys.path:
        sys.path.insert(0, str(unidepth_root))
    from unidepth.models import UniDepthV2

    config_path = unidepth_root / "configs" / "config_v2_vitl14.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    model = UniDepthV2(config)
    weights_path = find_unidepth_weights(weights_root)
    state = load_file(str(weights_path), device="cpu")
    info = model.load_state_dict(state, strict=False)
    print(
        f"[UNIDEPTH] loaded {weights_path} "
        f"(missing={len(info.missing_keys)}, unexpected={len(info.unexpected_keys)})",
        flush=True,
    )
    return model.to(device).eval()


def resize_rgb(rgb: np.ndarray) -> np.ndarray:
    if rgb.shape[1] > rgb.shape[0]:
        final_w = LONG_DIM
        final_h = int(round(LONG_DIM * rgb.shape[0] / rgb.shape[1]))
    else:
        final_w = int(round(LONG_DIM * rgb.shape[1] / rgb.shape[0]))
        final_h = LONG_DIM
    return cv2.resize(rgb, (final_w, final_h), cv2.INTER_AREA)
