"""WBench-style model interface for HarnessEval generation adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from ..io import atomic_write_json, read_json


REQUEST_SCHEMA = "harnesseval.model_generation_request"
OUTPUT_SCHEMA = "harnesseval.model_output"


class BaseVideoModel(ABC):
    """Base class for models that generate HarnessEval rollouts.

    The interface follows WBench's ``BaseVideoModel`` contract while consuming
    HarnessEval's structured case and output request formats.
    """

    default_workers = 1

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def generate(
        self,
        prompt: str,
        image: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate one video and return ``code`` and ``video_path``."""

    @abstractmethod
    def generate_case(
        self,
        case: dict[str, Any],
        job: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate one HarnessEval case into the output path in ``job``."""

    def get_model_info(self) -> dict[str, Any]:
        return {"model_name": self.model_name, "class": self.__class__.__name__}

    @staticmethod
    def _resolve_path(value: Any, root: Path) -> Path:
        path = Path(str(value)).expanduser()
        return path.resolve() if path.is_absolute() else (root / path).resolve()

    @staticmethod
    def _case_index(
        manifest: dict[str, Any], manifest_path: Path
    ) -> dict[str, dict[str, Any]]:
        cases = manifest.get("cases") if isinstance(manifest, dict) else None
        if not isinstance(cases, list):
            raise ValueError(f"manifest has no cases array: {manifest_path}")
        index: dict[str, dict[str, Any]] = {}
        for case in cases:
            if not isinstance(case, dict) or not case.get("case_id"):
                raise ValueError(f"manifest contains an invalid case: {manifest_path}")
            case_id = str(case["case_id"])
            if case_id in index:
                raise ValueError(f"duplicate case in manifest: {case_id}")
            index[case_id] = case
        return index

    @staticmethod
    def _is_complete(job: dict[str, Any], model_id: str, root: Path) -> bool:
        video = BaseVideoModel._resolve_path(job.get("output_video"), root)
        metadata = BaseVideoModel._resolve_path(job.get("metadata"), root)
        if not video.is_file() or video.stat().st_size == 0 or not metadata.is_file():
            return False
        try:
            value = read_json(metadata)
        except (OSError, ValueError):
            return False
        return (
            value.get("case_id") == job.get("case_id")
            and (value.get("model_id") or value.get("model_slug")) == model_id
        )

    @staticmethod
    def _validate_job(case: dict[str, Any], job: dict[str, Any]) -> None:
        case_id = str(case["case_id"])
        if str(job.get("case_id") or "") != case_id:
            raise ValueError(f"job/case id mismatch for {case_id}")
        if job.get("taxonomy") != case.get("taxonomy"):
            raise ValueError(f"job/case taxonomy mismatch for {case_id}")
        action = (case.get("interaction") or {}).get("action") or {}
        if job.get("action") != action:
            raise ValueError(f"job/case action mismatch for {case_id}")
        observation = (case.get("world") or {}).get("initial_observation")
        case_image = (
            observation.get("path") if isinstance(observation, dict) else observation
        )
        if str(job.get("initial_observation") or "") != str(case_image or ""):
            raise ValueError(f"job/case initial observation mismatch for {case_id}")

    def run_request(
        self, request_path: Path, *, workers: int | None = None
    ) -> dict[str, Any]:
        """Execute a model-adapter request produced by ``harnesseval generate``."""

        request_path = request_path.expanduser().resolve(strict=True)
        request = read_json(request_path)
        if request.get("schema_version") != REQUEST_SCHEMA:
            raise ValueError(f"request schema must be {REQUEST_SCHEMA}: {request_path}")
        jobs = request.get("jobs")
        if not isinstance(jobs, list) or not all(isinstance(job, dict) for job in jobs):
            raise ValueError(
                f"request jobs must be an array of objects: {request_path}"
            )

        generation_root = self._resolve_path(
            request.get("generation_root") or request_path.parent,
            request_path.parent,
        )
        manifest_path = self._resolve_path(request.get("manifest"), request_path.parent)
        manifest = read_json(manifest_path.resolve(strict=True))
        cases = self._case_index(manifest, manifest_path)
        model_id = str(request.get("model_id") or "")
        if not model_id:
            raise ValueError(f"request has no model_id: {request_path}")
        if any(str(job.get("model_id") or "") != model_id for job in jobs):
            raise ValueError(f"request/job model_id mismatch: {request_path}")

        requested_workers = self.default_workers if workers is None else workers
        if requested_workers < 1:
            raise ValueError("workers must be positive")

        def run(job: dict[str, Any]) -> dict[str, Any]:
            case_id = str(job.get("case_id") or "")
            case = cases.get(case_id)
            if case is None:
                raise ValueError(f"request case is absent from manifest: {case_id}")
            self._validate_job(case, job)
            if self._is_complete(job, model_id, generation_root):
                return {"case_id": case_id, "status": "skipped"}

            output_video = self._resolve_path(job.get("output_video"), generation_root)
            metadata_path = self._resolve_path(job.get("metadata"), generation_root)
            if output_video.parent != metadata_path.parent:
                raise ValueError(f"video and metadata directories differ for {case_id}")
            output_video.parent.mkdir(parents=True, exist_ok=True)

            resolved_job = {
                **job,
                "output_dir": str(output_video.parent),
                "output_video": str(output_video),
                "metadata": str(metadata_path),
            }
            result = self.generate_case(case, resolved_job)
            if result.get("code") != 0:
                raise RuntimeError(str(result.get("error") or "generation failed"))
            result_video = self._resolve_path(result.get("video_path"), generation_root)
            if result_video != output_video:
                raise ValueError(
                    f"model wrote an unexpected output for {case_id}: {result_video}"
                )
            if not output_video.is_file() or output_video.stat().st_size == 0:
                raise RuntimeError(f"model produced no video for {case_id}")

            action = (case.get("interaction") or {}).get("action") or {}
            metadata: dict[str, Any] = {
                "schema_version": OUTPUT_SCHEMA,
                "case_id": case_id,
                "action_id": action.get("action_id", case_id),
                "model": request.get("model"),
                "model_id": model_id,
                "model_slug": model_id,
                "taxonomy": case["taxonomy"],
                "input_image": job.get("initial_observation"),
                "output_video": output_video.name,
                "adapter_request": str(request_path),
                "generator": self.get_model_info(),
            }
            for key in ("prompt", "provider", "generation", "segments"):
                if key in result:
                    metadata[key] = result[key]
            atomic_write_json(metadata_path, metadata)
            return {"case_id": case_id, "status": "completed"}

        outcomes: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []
        pool_size = max(1, min(requested_workers, len(jobs) or 1))
        with ThreadPoolExecutor(max_workers=pool_size) as pool:
            futures = {pool.submit(run, job): job for job in jobs}
            for future in as_completed(futures):
                job = futures[future]
                try:
                    outcomes.append(future.result())
                except Exception as exc:  # noqa: BLE001 - report every failed case
                    failures.append(
                        {
                            "case_id": str(job.get("case_id") or ""),
                            "error": repr(exc),
                        }
                    )

        counts = Counter(item["status"] for item in outcomes)
        return {
            "schema_version": "harnesseval.model_generation_execution",
            "status": "failed" if failures else "passed",
            "model": self.model_name,
            "model_id": model_id,
            "requested": len(jobs),
            "completed": counts["completed"],
            "skipped": counts["skipped"],
            "failed": len(failures),
            "failures": sorted(failures, key=lambda item: item["case_id"]),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(model={self.model_name})>"
