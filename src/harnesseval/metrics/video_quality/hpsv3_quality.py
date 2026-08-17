"""HPSv3 human preference score — Qwen2-VL-7B based preference model."""
import os
import tempfile
from contextlib import contextmanager
from typing import Dict, Any, List

import numpy as np
import torch
from PIL import Image

# Patch: ensure VideoInput is available in transformers.image_utils for HPSv3 compatibility
import transformers.image_utils as _img_utils
if not hasattr(_img_utils, "VideoInput"):
    _img_utils.VideoInput = List[np.ndarray]

from ..base import BaseMetric
from ..weight_utils import get_weights_dir

class HPSv3QualityMetric(BaseMetric):
    def __init__(self, device="cuda"):
        super().__init__(device)
        from hpsv3.inference import HPSv3RewardInferencer

        hpsv3_dir = get_weights_dir("HPSv3")
        checkpoint_path = os.path.join(hpsv3_dir, "HPSv3.safetensors")
        config_path = os.path.join(hpsv3_dir, "HPSv3_7B_local.yaml")

        # Use local Qwen2-VL weights if available
        local_qwen = os.path.join(get_weights_dir(), "Qwen2-VL-7B-Instruct")
        if os.path.isdir(local_qwen):
            os.environ["HF_HUB_OFFLINE"] = "1"
            import yaml
            with open(config_path) as f:
                cfg = yaml.safe_load(f)
            cfg["model_name_or_path"] = local_qwen
            tmp_cfg = os.path.join(hpsv3_dir, "_HPSv3_7B_resolved.yaml")
            with open(tmp_cfg, "w") as f:
                yaml.dump(cfg, f)
            config_path = tmp_cfg

        self.inferencer = HPSv3RewardInferencer(
            config_path=config_path,
            checkpoint_path=checkpoint_path,
            device=device,
        )

    @property
    def name(self):
        return "hpsv3_quality"

    def compute(self, frames: List[Image.Image], **kwargs) -> Dict[str, Any]:
        with self.prepare_cpu(frames) as prepared:
            return self.compute_prepared(prepared)

    @contextmanager
    def prepare_cpu(self, frames: List[Image.Image], *, executor=None):
        with tempfile.TemporaryDirectory(prefix=f"hpsv3_{os.getpid()}_") as tmp_dir:
            tmp_paths = [os.path.join(tmp_dir, f"frame_{i}.png") for i in range(len(frames))]

            def save_frame(item):
                i, frame = item
                p = os.path.join(tmp_dir, f"frame_{i}.png")
                frame.save(p)
                return p

            items = list(enumerate(frames))
            if executor is not None:
                list(executor.map(save_frame, items))
            else:
                for item in items:
                    save_frame(item)
            prompts = [""] * len(tmp_paths)
            batch = self.inferencer.prepare_batch(
                tmp_paths,
                prompts,
                move_to_device=False,
            )
            yield batch

    def compute_prepared(self, batch) -> Dict[str, Any]:
        with torch.no_grad():
            rewards = self.inferencer.reward_prepared(batch)
        raw_scores = [rewards[i][0].item() for i in range(len(rewards))]
        return {
            f"{self.name}_score": float(np.mean(raw_scores)),
            f"{self.name}_raw_scores": raw_scores,
        }
