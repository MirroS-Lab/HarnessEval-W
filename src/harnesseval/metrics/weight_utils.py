"""
Model weight management.

All weights are stored under the project root weights/ directory.
Directory structure:
    weights/
    ├── clip/               # CLIP models (ViT-L/14, ViT-B/32)
    ├── clip-vit-base-patch16/  # HuggingFace CLIP (for subject_consistency)
    ├── torch_hub/          # DINOv2 (torch.hub cache)
    ├── aesthetic/          # LAION aesthetic scoring head
    ├── pyiqa/              # MUSIQ via pyiqa
    ├── dreamsim/           # DreamSim perceptual model
    ├── raft/               # RAFT optical flow (raft-things.pth)
    ├── amt/                # AMT-S frame interpolation (amt-s.pth)
    ├── transnetv2/         # TransNetV2 (transnetv2-pytorch-weights.pth)
    └── HPSv3/              # HPSv3 (HPSv3.safetensors + config)
"""
import os
from pathlib import Path

from ..paths import PROJECT_ROOT


def get_weights_dir(subdir: str = "") -> str:
    """Get weight subdirectory path (auto-creates)."""
    root = Path(
        os.environ.get("HARNESSEVAL_WEIGHTS_ROOT", PROJECT_ROOT / "weights")
    )
    path = root / subdir if subdir else root
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def setup_torch_hub_dir():
    """Set torch.hub cache to project-local weights/torch_hub/."""
    import torch
    hub_dir = get_weights_dir("torch_hub")
    torch.hub.set_dir(hub_dir)
    return hub_dir
