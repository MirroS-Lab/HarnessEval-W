"""Seedance 2.0 text/image-conditioned video model."""

from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path
from typing import Any

from ...io import (
    atomic_write_json,
    atomic_write_text,
    read_json,
)
from ..base import BaseVideoModel
from ..media import FFmpegMedia, VideoMedia
from .api_client import SeedanceAPIClient
from .prompt_builder import prompt_for_case, prompt_for_turn, turns_for_case


DEFAULT_BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3"
DEFAULT_PROVIDER_MODEL = "doubao-seedance-2-0-260128"
SEGMENT_SCHEMA = "harnesseval.model_output_segment"


def _read_config_value(
    direct: str,
    file_value: str,
    *,
    name: str,
) -> str:
    if direct.strip():
        return direct.strip()
    if file_value.strip():
        path = Path(file_value).expanduser().resolve(strict=True)
        value = path.read_text(encoding="utf-8").strip()
        if value:
            return value
    raise ValueError(f"set {name} or {name}_FILE")


def image_data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


class SeedanceModel(BaseVideoModel):
    """Seedance 2.0 I2V model via the content-generation task API."""

    def __init__(
        self,
        *,
        endpoint_id: str = "",
        endpoint_file: str = "",
        api_key: str = "",
        api_key_file: str = "",
        base_url: str = "",
        provider_model_name: str = "",
        resolution: str = "",
        ratio: str = "",
        duration: int | None = None,
        timeout: float | None = None,
        poll_interval: float | None = None,
        retries: int | None = None,
        client: SeedanceAPIClient | None = None,
        media: VideoMedia | None = None,
    ):
        super().__init__(model_name="seedance")
        self.endpoint_id = _read_config_value(
            endpoint_id or os.getenv("SEEDANCE_MODEL_ENDPOINT_ID", ""),
            endpoint_file or os.getenv("SEEDANCE_ENDPOINT_FILE", ""),
            name="SEEDANCE_MODEL_ENDPOINT_ID",
        )
        if not self.endpoint_id.startswith("ep-"):
            raise ValueError("SEEDANCE_MODEL_ENDPOINT_ID must start with 'ep-'")
        resolved_api_key = _read_config_value(
            api_key or os.getenv("SEEDANCE_API_KEY", ""),
            api_key_file or os.getenv("SEEDANCE_API_KEY_FILE", ""),
            name="SEEDANCE_API_KEY",
        )
        self.base_url = base_url or os.getenv("SEEDANCE_BASE_URL", DEFAULT_BASE_URL)
        self.provider_model_name = provider_model_name or os.getenv(
            "SEEDANCE_PROVIDER_MODEL_NAME", DEFAULT_PROVIDER_MODEL
        )
        self.resolution = resolution or os.getenv("SEEDANCE_RESOLUTION", "480p")
        self.ratio = ratio or os.getenv("SEEDANCE_RATIO", "adaptive")
        self.duration = duration or int(os.getenv("SEEDANCE_DURATION", "4"))
        self.default_workers = max(int(os.getenv("SEEDANCE_WORKERS", "8")), 1)
        self._client = client or SeedanceAPIClient(
            base_url=self.base_url,
            api_key=resolved_api_key,
            timeout=(
                timeout
                if timeout is not None
                else float(os.getenv("SEEDANCE_TIMEOUT", "1800"))
            ),
            poll_interval=(
                poll_interval
                if poll_interval is not None
                else float(os.getenv("SEEDANCE_POLL_INTERVAL", "10"))
            ),
            retries=(
                retries
                if retries is not None
                else int(os.getenv("SEEDANCE_REQUEST_RETRIES", "4"))
            ),
        )
        self._media = media or FFmpegMedia(os.getenv("SEEDANCE_FFMPEG_BIN", "ffmpeg"))

    def get_model_info(self) -> dict[str, Any]:
        return {
            "model_name": "seedance-2.0",
            "provider_model_name": self.provider_model_name,
            "base_url": self.base_url,
            "class": self.__class__.__name__,
            "conditioning": "text_image_to_video",
            "multi_turn": "last_frame_chaining",
        }

    def generate(
        self,
        prompt: str,
        image: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if not image:
            return {"code": -1, "error": "Seedance 2.0 requires a first-frame image"}
        image_path = Path(image).expanduser().resolve(strict=True)
        output_value = kwargs.get("output_path")
        if not output_value:
            return {"code": -1, "error": "Seedance output_path is required"}
        output_path = Path(str(output_value)).expanduser().resolve()
        payload = {
            "model": self.endpoint_id,
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": image_data_url(image_path)},
                    "role": "first_frame",
                },
            ],
            "resolution": kwargs.get("resolution", self.resolution),
            "ratio": kwargs.get("ratio", self.ratio),
            "duration": kwargs.get("duration", self.duration),
            "watermark": False,
            "generate_audio": False,
        }
        provider = self._client.generate(
            endpoint_id=self.endpoint_id,
            payload=payload,
            output_path=output_path,
        )
        provider["provider_model_name"] = self.provider_model_name
        return {
            "code": 0,
            "video_path": str(output_path),
            "provider": provider,
            "generation": {
                "resolution": payload["resolution"],
                "ratio": payload["ratio"],
                "duration": payload["duration"],
                "watermark": False,
                "generate_audio": False,
            },
        }

    def _segment_identity(
        self,
        *,
        case: dict[str, Any],
        turn: dict[str, Any],
        turn_count: int,
        prompt: str,
        input_image: Path,
        output_dir: Path,
    ) -> dict[str, Any]:
        action = (case.get("interaction") or {}).get("action") or {}
        return {
            "schema_version": SEGMENT_SCHEMA,
            "case_id": str(case.get("case_id") or ""),
            "action_id": str(action.get("action_id") or case.get("case_id") or ""),
            "turn_index": turn["turn_index"],
            "turn_count": turn_count,
            "turn_id": turn["turn_id"],
            "action_chunk": (
                turn["action_chunk"]
                if turn["action_chunk"] is not None
                else turn["action"]
            ),
            "prompt": prompt,
            "input_image": self._relative_path(input_image, output_dir),
            "model": {
                "endpoint_id": self.endpoint_id,
                "provider_model_name": self.provider_model_name,
                "base_url": self.base_url,
                "resolution": self.resolution,
                "ratio": self.ratio,
                "duration": self.duration,
                "watermark": False,
                "generate_audio": False,
            },
        }

    @staticmethod
    def _relative_path(path: Path, output_dir: Path) -> str:
        try:
            return path.relative_to(output_dir).as_posix()
        except ValueError:
            return str(path)

    @staticmethod
    def _resumable_segment(
        *,
        metadata_path: Path,
        prompt_path: Path,
        segment_video: Path,
        last_frame: Path,
        expected_identity: dict[str, Any],
    ) -> dict[str, Any] | None:
        required = (metadata_path, prompt_path, segment_video, last_frame)
        if not all(path.is_file() and path.stat().st_size > 0 for path in required):
            return None
        try:
            metadata = read_json(metadata_path)
            if not isinstance(metadata, dict):
                return None
            if metadata.get("schema_version") != SEGMENT_SCHEMA:
                return None
            if any(
                metadata.get(key) != value for key, value in expected_identity.items()
            ):
                return None
            if metadata.get("prompt_file") != prompt_path.name:
                return None
            if metadata.get("output_video") != segment_video.name:
                return None
            if metadata.get("last_frame") != last_frame.name:
                return None
            if (
                prompt_path.read_text(encoding="utf-8")
                != expected_identity["prompt"] + "\n"
            ):
                return None
        except (OSError, ValueError):
            return None
        return metadata

    def _segment_summary(
        self,
        metadata: dict[str, Any],
        metadata_path: Path,
        segment_video: Path,
        last_frame: Path,
        output_dir: Path,
    ) -> dict[str, Any]:
        return {
            "turn_index": metadata["turn_index"],
            "chunk_id": metadata["turn_id"],
            "action_chunk": metadata["action_chunk"],
            "prompt": metadata["prompt"],
            "task_id": metadata.get("task_id"),
            "provider": metadata.get("provider"),
            "generation": metadata.get("generation"),
            "segment_video": self._relative_path(segment_video, output_dir),
            "last_frame": self._relative_path(last_frame, output_dir),
            "metadata": self._relative_path(metadata_path, output_dir),
        }

    def generate_case(
        self,
        case: dict[str, Any],
        job: dict[str, Any],
    ) -> dict[str, Any]:
        case_id = str(case.get("case_id") or "")
        turns = turns_for_case(case)
        turn_count = len(turns)
        output_dir = Path(str(job["output_dir"])).expanduser().resolve()
        output_video = Path(str(job["output_video"])).expanduser().resolve()
        segments_root = output_dir / "segments"
        segments_root.mkdir(parents=True, exist_ok=True)
        current_image = (
            Path(str(job["initial_observation"])).expanduser().resolve(strict=True)
        )

        segment_paths = []
        segment_summaries = []
        prompts = []
        for turn in turns:
            turn_index = int(turn["turn_index"])
            turn_id = str(turn["turn_id"])
            segment_dir = segments_root / f"segment_{turn_index:03d}"
            segment_dir.mkdir(parents=True, exist_ok=True)
            segment_video = segment_dir / "output.mp4"
            last_frame = segment_dir / "last_frame.png"
            prompt_path = segment_dir / "prompt.txt"
            metadata_path = segment_dir / "metadata.json"
            prompt = prompt_for_turn(case, turn)
            prompts.append(prompt)
            segment_identity = self._segment_identity(
                case=case,
                turn=turn,
                turn_count=turn_count,
                prompt=prompt,
                input_image=current_image,
                output_dir=output_dir,
            )
            metadata = self._resumable_segment(
                metadata_path=metadata_path,
                prompt_path=prompt_path,
                segment_video=segment_video,
                last_frame=last_frame,
                expected_identity=segment_identity,
            )
            if metadata is None:
                atomic_write_text(prompt_path, prompt + "\n")
                try:
                    result = self.generate(
                        prompt=prompt,
                        image=str(current_image),
                        output_path=str(segment_video),
                    )
                except Exception as exc:
                    raise RuntimeError(
                        f"Seedance turn {turn_index}/{turn_count} ({turn_id}) "
                        f"failed for {case_id}: {exc}"
                    ) from exc
                if result.get("code") != 0:
                    raise RuntimeError(
                        f"Seedance turn {turn_index}/{turn_count} ({turn_id}) "
                        f"failed for {case_id}: "
                        f"{result.get('error', 'generation failed')}"
                    )
                try:
                    self._media.extract_last_frame(segment_video, last_frame)
                except Exception as exc:
                    raise RuntimeError(
                        f"Seedance last-frame extraction failed at turn "
                        f"{turn_index}/{turn_count} ({turn_id}) for {case_id}: {exc}"
                    ) from exc

                provider = result.get("provider") or {}
                generation = result.get("generation") or {}
                metadata = {
                    **segment_identity,
                    "prompt_file": prompt_path.name,
                    "output_video": segment_video.name,
                    "last_frame": last_frame.name,
                    "task_id": (
                        provider.get("task_id") if isinstance(provider, dict) else None
                    ),
                    "provider": provider,
                    "generation": generation,
                }
                atomic_write_json(metadata_path, metadata)

            segment_paths.append(segment_video)
            segment_summaries.append(
                self._segment_summary(
                    metadata,
                    metadata_path,
                    segment_video,
                    last_frame,
                    output_dir,
                )
            )
            current_image = last_frame

        try:
            self._media.concatenate(segment_paths, output_video)
        except Exception as exc:
            raise RuntimeError(
                f"Seedance segment concatenation failed for {case_id}: {exc}"
            ) from exc

        task_ids = [
            segment.get("task_id")
            for segment in segment_summaries
            if segment.get("task_id")
        ]
        return {
            "code": 0,
            "video_path": str(output_video),
            "prompt": prompt_for_case(case),
            "provider": {
                "name": "seedance",
                "endpoint_id": self.endpoint_id,
                "task_ids": task_ids,
            },
            "generation": {
                "mode": "multi_turn_last_frame_chaining",
                "turn_count": turn_count,
                "prompts": prompts,
                "resolution": self.resolution,
                "ratio": self.ratio,
                "segment_duration": self.duration,
                "requested_total_duration": self.duration * turn_count,
                "watermark": False,
                "generate_audio": False,
            },
            "segments": segment_summaries,
        }
