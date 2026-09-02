"""SANA-WM Streaming adapter using one native AR rollout per case."""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from typing import Any

from ....io import atomic_write_text
from ...process import CommandRunner, configured_path, publish_video, run_command
from ..base import ActionConditionedModel

ACTION_KEYS = {
    "W": "w",
    "S": "s",
    "A": "j",
    "D": "l",
    "left": "a",
    "right": "d",
    "up": "i",
    "down": "k",
}
FPS = 24
NATIVE_BLOCK_FRAMES = 24
FRAMES_PER_TURN = 2 * NATIVE_BLOCK_FRAMES


def actions_to_dsl(
    actions: list[dict[str, Any]], frames_per_turn: int = FRAMES_PER_TURN
) -> str:
    """Convert all case turns into SANA's complete action DSL."""

    segments = []
    for action in actions:
        try:
            keys = [ACTION_KEYS[token] for token in action.get("tokens", [])]
        except KeyError as exc:
            raise ValueError(f"unsupported SANA-WM action: {exc.args[0]}") from exc
        key_string = "".join(dict.fromkeys(keys)) or "none"
        segments.append(f"{key_string}-{frames_per_turn}")
    if not segments:
        raise ValueError("SANA-WM requires at least one action turn")
    return ",".join(segments)


class SanaWMStreamingModel(ActionConditionedModel):
    """Run SANA-WM Streaming over the full action sequence in one invocation."""

    def __init__(
        self,
        *,
        python: str | Path | None = None,
        runtime_root: str | Path | None = None,
        model_root: str | Path | None = None,
        stage1_text_encoder: str | Path | None = None,
        frames_per_turn: int = FRAMES_PER_TURN,
        seed: int | None = None,
        device: str | None = None,
        command_runner: CommandRunner = run_command,
    ) -> None:
        super().__init__(model_name="sana-wm-streaming")
        project_root = Path(__file__).resolve().parents[5]
        self.python = configured_path(python, "SANA_WM_PYTHON", default=sys.executable)
        self.runtime_root = configured_path(
            runtime_root,
            "SANA_WM_RUNTIME_ROOT",
            default=project_root / "third_party/SANA",
        )
        self.model_root = configured_path(model_root, "SANA_WM_MODEL_ROOT")
        self.stage1_text_encoder = configured_path(
            stage1_text_encoder, "SANA_WM_STAGE1_TEXT_ENCODER_ROOT"
        )
        self.frames_per_turn = frames_per_turn
        self.seed = seed if seed is not None else int(os.getenv("SANA_WM_SEED", "42"))
        self.device = device if device is not None else os.getenv("SANA_WM_DEVICE", "")
        self._run_command = command_runner

    def get_model_info(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "class": self.__class__.__name__,
            "conditioning": "action_dsl",
            "rollout": "native_streaming_ar",
        }

    def _validate_runtime(self) -> Path:
        entry = Path(__file__).with_name("entry.py").resolve()
        required = (
            self.python,
            self.runtime_root
            / "inference_video_scripts/wm/inference_sana_wm_streaming.py",
            self.runtime_root / "configs/sana_wm/sana_wm_streaming_1600m_720p.yaml",
            self.model_root / "sana_dit/model.pt",
            self.model_root / "ltx2_causal_vae",
            self.model_root / "refiner_diffusers",
            self.model_root / "gemma3_12b",
            self.stage1_text_encoder,
            entry,
        )
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise FileNotFoundError(f"missing SANA-WM runtime path: {missing[0]}")
        return entry

    @staticmethod
    def _write_intrinsics(image: Path, path: Path, fov_degrees: float = 70.0) -> None:
        import numpy as np
        from PIL import Image

        with Image.open(image) as source:
            width, height = source.size
        focal = 0.5 * width / math.tan(math.radians(fov_degrees) * 0.5)
        np.save(
            path, np.asarray([focal, focal, width / 2, height / 2], dtype=np.float32)
        )

    def generate_with_actions(
        self,
        image: str,
        actions: list[dict[str, Any]],
        output_path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        entry = self._validate_runtime()
        image_path = Path(image).expanduser().resolve(strict=True)
        destination = Path(output_path).expanduser().resolve()
        runtime_dir = destination.parent / "sana_wm"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = runtime_dir / "prompt.txt"
        intrinsics_path = runtime_dir / "intrinsics.npy"
        raw_video = runtime_dir / "harnesseval_streaming.mp4"
        raw_video.unlink(missing_ok=True)

        prompt = str(kwargs.get("prompt") or "").strip()
        if not prompt:
            raise ValueError("SANA-WM prompt is empty")
        action_dsl = actions_to_dsl(actions, self.frames_per_turn)
        num_frames = len(actions) * self.frames_per_turn + 1
        atomic_write_text(prompt_path, prompt + "\n")
        self._write_intrinsics(image_path, intrinsics_path)

        command = [
            str(self.python.resolve()),
            str(entry),
            "--image",
            str(image_path),
            "--prompt",
            str(prompt_path),
            "--output_dir",
            str(runtime_dir),
            "--name",
            "harnesseval",
            "--action",
            action_dsl,
            "--intrinsics",
            str(intrinsics_path),
            "--num_frames",
            str(num_frames),
            "--fps",
            str(FPS),
            "--cfg_scale",
            "1.0",
            "--flow_shift",
            "8.0",
            "--seed",
            str(self.seed),
            "--translation_speed",
            "0.025",
            "--rotation_speed_deg",
            "0.6",
            "--config",
            str(
                self.runtime_root.resolve()
                / "configs/sana_wm/sana_wm_streaming_1600m_720p.yaml"
            ),
            "--streaming_root",
            str(self.model_root.resolve()),
            "--denoising_step_list",
            "1000,960,889,727,0",
            "--output_mode",
            "mp4",
            "--no_compile",
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
                "SANA_WM_STAGE1_TEXT_ENCODER_NAME": "gemma-2-2b-it",
                "SANA_WM_STAGE1_TEXT_ENCODER_ROOT": str(
                    self.stage1_text_encoder.resolve()
                ),
                "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1",
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
                "rollout": "native_streaming_ar",
                "action_dsl": action_dsl,
                "fps": FPS,
                "native_block_frames": NATIVE_BLOCK_FRAMES,
                "blocks_per_turn": self.frames_per_turn // NATIVE_BLOCK_FRAMES,
                "frames_per_turn": self.frames_per_turn,
                "num_frames": num_frames,
            },
        }
