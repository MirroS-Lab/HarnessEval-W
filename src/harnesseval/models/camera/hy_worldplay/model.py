"""HY-WorldPlay 1.5 adapter using one native AR rollout per case."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from ....io import atomic_write_json
from ...process import CommandRunner, configured_path, publish_video, run_command
from ..base import CameraConditionedModel
from .poses import case_to_poses


class HYWorldPlayModel(CameraConditionedModel):
    """Run the official HY-WorldPlay AR pipeline over a complete pose path."""

    def __init__(
        self,
        *,
        python: str | Path | None = None,
        runtime_root: str | Path | None = None,
        base_model: str | Path | None = None,
        action_checkpoint: str | Path | None = None,
        seed: int | None = None,
        device: str | None = None,
        command_runner: CommandRunner = run_command,
    ) -> None:
        super().__init__(model_name="hy-worldplay-1.5")
        project_root = Path(__file__).resolve().parents[5]
        self.python = configured_path(
            python, "HY_WORLDPLAY_PYTHON", default=sys.executable
        )
        self.runtime_root = configured_path(
            runtime_root,
            "HY_WORLDPLAY_RUNTIME_ROOT",
            default=project_root / "third_party/HY-WorldPlay",
        )
        self.base_model = configured_path(base_model, "HY_WORLDPLAY_BASE_MODEL")
        self.action_checkpoint = configured_path(
            action_checkpoint, "HY_WORLDPLAY_ACTION_CHECKPOINT"
        )
        self.seed = (
            seed if seed is not None else int(os.getenv("HY_WORLDPLAY_SEED", "42"))
        )
        self.device = (
            device if device is not None else os.getenv("HY_WORLDPLAY_DEVICE", "")
        )
        self._run_command = command_runner

    def get_model_info(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "class": self.__class__.__name__,
            "conditioning": "camera_pose",
            "rollout": "native_ar",
        }

    def build_pose_trajectory(self, case: dict[str, Any]) -> dict[str, Any]:
        return case_to_poses(case)

    def _entry(self) -> Path:
        entry = self.runtime_root / "hyvideo/generate.py"
        required = (
            self.python,
            entry,
            self.base_model / "config.json",
            self.action_checkpoint,
        )
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise FileNotFoundError(f"missing HY-WorldPlay runtime path: {missing[0]}")
        return entry.resolve()

    @staticmethod
    def _resize_image(source: Path, destination: Path) -> None:
        from PIL import Image

        with Image.open(source) as image:
            image.convert("RGB").resize((832, 480), Image.Resampling.LANCZOS).save(
                destination
            )

    def generate_with_poses(
        self,
        image: str,
        poses: dict[str, Any],
        output_path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        entry = self._entry()
        image_path = Path(image).expanduser().resolve(strict=True)
        destination = Path(output_path).expanduser().resolve()
        runtime_dir = destination.parent / "hy_worldplay"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        resized_image = runtime_dir / "input.png"
        pose_path = runtime_dir / "poses.json"
        raw_video = runtime_dir / "gen.mp4"
        raw_video.unlink(missing_ok=True)

        self._resize_image(image_path, resized_image)
        atomic_write_json(pose_path, poses)
        video_length = int(kwargs["video_length"])
        command = [
            str(self.python.resolve()),
            "-m",
            "torch.distributed.run",
            "--nproc_per_node=1",
            str(entry),
            "--prompt",
            str(kwargs.get("prompt") or ""),
            "--image_path",
            str(resized_image),
            "--resolution",
            "480p",
            "--aspect_ratio",
            "16:9",
            "--video_length",
            str(video_length),
            "--seed",
            str(self.seed),
            "--rewrite",
            "false",
            "--sr",
            "false",
            "--save_pre_sr_video",
            "false",
            "--pose",
            str(pose_path),
            "--output_path",
            str(runtime_dir),
            "--model_path",
            str(self.base_model.resolve()),
            "--action_ckpt",
            str(self.action_checkpoint.resolve()),
            "--few_step",
            "true",
            "--num_inference_steps",
            "4",
            "--model_type",
            "ar",
            "--height",
            "480",
            "--width",
            "832",
            "--use_vae_parallel",
            "false",
            "--use_sageattn",
            "false",
            "--use_fp8_gemm",
            "false",
            "--transformer_resident_ar_rollout",
            "true",
        ]
        environment = os.environ.copy()
        current_pythonpath = environment.get("PYTHONPATH", "")
        environment.update(
            {
                "PYTHONNOUSERSITE": "1",
                "PYTHONPATH": os.pathsep.join(
                    part
                    for part in (str(self.runtime_root.resolve()), current_pythonpath)
                    if part
                ),
            }
        )
        if self.device:
            environment["CUDA_VISIBLE_DEVICES"] = self.device.replace("cuda:", "")
        self._run_command(
            command,
            self.runtime_root.resolve(),
            environment,
            runtime_dir / "run.log",
        )
        publish_video(raw_video, destination)
        return {
            "code": 0,
            "video_path": str(destination),
            "generation": {
                "rollout": "native_ar",
                "model_type": "ar",
                "ar_chunk_latents": 4,
                "ar_chunks_per_turn": 3,
                "num_inference_steps": 4,
            },
        }
