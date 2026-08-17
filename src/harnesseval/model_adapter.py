"""Run an external model command against the HarnessEval generation contract."""

from __future__ import annotations

import copy
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from .io import atomic_write_json, file_digest, read_json
from .paths import PROJECT_ROOT
from .pipeline.inventory import VideoProbe, build_inventory, probe_video, write_inventory
from .pipeline.planner import initial_observation_path, load_cases


ADAPTER_SCHEMA = "harnesseval.command_model_adapter"
REQUEST_SCHEMA = "harnesseval.model_generation_request"
AUDIT_SCHEMA = "harnesseval.model_generation_audit"
MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def model_id_from_reference(model: str) -> str:
    value = Path(model.rstrip("/")).name or model
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
    if not value:
        raise ValueError("cannot derive --model-id from the model reference")
    return value


def _load_adapter(path: Path) -> dict[str, Any]:
    path = path.resolve(strict=True)
    value = read_json(path)
    if not isinstance(value, dict) or value.get("schema_version") != ADAPTER_SCHEMA:
        raise ValueError(f"adapter schema must be {ADAPTER_SCHEMA}: {path}")
    command = value.get("command")
    if not isinstance(command, list) or not command or not all(
        isinstance(item, str) and item for item in command
    ):
        raise ValueError("adapter command must be a non-empty JSON string array")
    environment = value.get("environment") or {}
    if not isinstance(environment, dict) or not all(
        isinstance(key, str) and isinstance(item, str)
        for key, item in environment.items()
    ):
        raise ValueError("adapter environment must map strings to strings")
    return {**value, "path": path, "environment": environment}


def _selected_cases(
    manifest: Path, case_ids: set[str], limit: int
) -> list[dict[str, Any]]:
    if limit < 0:
        raise ValueError("limit cannot be negative")
    cases = load_cases([manifest])
    known = {str(case["case_id"]) for case in cases}
    missing = sorted(case_ids - known)
    if missing:
        raise ValueError(f"unknown HarnessEval case: {missing[0]}")
    selected = [case for case in cases if not case_ids or case["case_id"] in case_ids]
    return selected[:limit] if limit else selected


def _materialize_cases(
    cases: list[dict[str, Any]], assets_root: Path
) -> list[dict[str, Any]]:
    materialized = []
    for source in cases:
        case = copy.deepcopy(source)
        initial = initial_observation_path(case, assets_root)
        if initial is None:
            raise FileNotFoundError(
                f"missing initial observation for {case['case_id']}"
            )
        case["world"]["initial_observation"]["path"] = str(initial)
        materialized.append(case)
    return materialized


def _job(case: dict[str, Any], root: Path, model: str, model_id: str) -> dict[str, Any]:
    taxonomy = case["taxonomy"]
    output_dir = (
        root
        / "outputs"
        / taxonomy["primary_axis"]
        / taxonomy["probe_family"]
        / model_id
        / case["case_id"]
    )
    action = (case.get("interaction") or {}).get("action") or {}
    return {
        "case_id": case["case_id"],
        "action_id": action.get("action_id", case["case_id"]),
        "taxonomy": taxonomy,
        "model": model,
        "model_id": model_id,
        "initial_observation": case["world"]["initial_observation"]["path"],
        "action": action,
        "output_dir": str(output_dir),
        "output_video": str(output_dir / "output.mp4"),
        "metadata": str(output_dir / "metadata.json"),
    }


def _complete(job: dict[str, Any]) -> bool:
    video = Path(job["output_video"])
    metadata = Path(job["metadata"])
    if not video.is_file() or video.stat().st_size == 0 or not metadata.is_file():
        return False
    try:
        value = read_json(metadata)
    except (OSError, ValueError):
        return False
    return (
        value.get("case_id") == job["case_id"]
        and (value.get("model_id") or value.get("model_slug")) == job["model_id"]
    )


def _format(value: str, fields: dict[str, str]) -> str:
    try:
        return os.path.expandvars(value).format_map(fields)
    except KeyError as exc:
        raise ValueError(f"unknown adapter placeholder: {exc.args[0]}") from exc


def run_model_adapter(
    *,
    adapter_path: Path,
    model: str,
    model_id: str,
    manifest: Path,
    output_root: Path,
    assets_root: Path = PROJECT_ROOT,
    case_ids: set[str] | None = None,
    limit: int = 0,
    workers: int = 16,
    full_decode: bool = False,
    video_probe: VideoProbe = probe_video,
) -> dict[str, Any]:
    """Execute one batch model command and validate its generated rollouts."""

    if not MODEL_ID_PATTERN.fullmatch(model_id):
        raise ValueError("model_id must use only letters, numbers, '.', '_' or '-'")
    adapter = _load_adapter(adapter_path)
    manifest = manifest.resolve(strict=True)
    assets_root = assets_root.resolve(strict=True)
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    state_root = output_root / ".harnesseval" / model_id
    state_root.mkdir(parents=True, exist_ok=True)

    cases = _materialize_cases(
        _selected_cases(manifest, case_ids or set(), limit), assets_root
    )
    if not cases:
        raise ValueError("no HarnessEval cases matched the generation request")
    jobs = [_job(case, output_root, model, model_id) for case in cases]
    pending = [job for job in jobs if not _complete(job)]
    selection_manifest = state_root / "manifest.json"
    pending_manifest = state_root / "pending_manifest.json"
    request_path = state_root / "request.json"
    log_path = state_root / "adapter.log"
    inventory_root = state_root / "inventory"
    audit_path = state_root / "ADAPTER_AUDIT.json"
    source = read_json(manifest)
    atomic_write_json(selection_manifest, {**source, "cases": cases})
    pending_ids = {job["case_id"] for job in pending}
    atomic_write_json(
        pending_manifest,
        {**source, "cases": [case for case in cases if case["case_id"] in pending_ids]},
    )
    request = {
        "schema_version": REQUEST_SCHEMA,
        "adapter_id": str(adapter.get("adapter_id") or adapter["path"].stem),
        "model": model,
        "model_id": model_id,
        "manifest": str(pending_manifest),
        "generation_root": str(output_root),
        "outputs_root": str(output_root / "outputs"),
        "jobs": pending,
    }
    atomic_write_json(request_path, request)

    fields = {
        "adapter_root": str(adapter["path"].parent),
        "project_root": str(PROJECT_ROOT),
        "model": model,
        "model_id": model_id,
        "manifest": str(pending_manifest),
        "source_manifest": str(manifest),
        "request": str(request_path),
        "generation_root": str(output_root),
        "outputs_root": str(output_root / "outputs"),
    }
    command = [_format(item, fields) for item in adapter["command"]]
    cwd_value = _format(str(adapter.get("working_directory") or "{adapter_root}"), fields)
    cwd = Path(cwd_value).expanduser().resolve(strict=True)
    environment = os.environ.copy()
    environment.update(
        {key: _format(value, fields) for key, value in adapter["environment"].items()}
    )
    returncode = 0
    error = None
    if pending:
        try:
            with log_path.open("a", encoding="utf-8") as log:
                completed = subprocess.run(
                    command,
                    cwd=cwd,
                    env=environment,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=float(adapter.get("timeout_seconds") or 0) or None,
                    check=False,
                )
            returncode = completed.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            returncode = 1
            error = str(exc)

    for job in pending:
        video = Path(job["output_video"])
        metadata = Path(job["metadata"])
        if video.is_file() and video.stat().st_size > 0 and not metadata.exists():
            atomic_write_json(
                metadata,
                {
                    "schema_version": "harnesseval.model_output",
                    "case_id": job["case_id"],
                    "action_id": job["action_id"],
                    "model": model,
                    "model_id": model_id,
                    "taxonomy": job["taxonomy"],
                    "input_image": job["initial_observation"],
                    "output_video": "output.mp4",
                    "adapter_request": str(request_path),
                },
            )

    rows, inventory = build_inventory(
        [selection_manifest],
        output_root,
        [model_id],
        assets_root=assets_root,
        workers=workers,
        full_decode=full_decode,
        video_probe=video_probe,
    )
    artifacts = write_inventory(inventory_root, rows, inventory)
    status = "passed" if returncode == 0 and inventory["status"] == "passed" else "failed"
    audit = {
        "schema_version": AUDIT_SCHEMA,
        "status": status,
        "adapter": str(adapter["path"]),
        "adapter_sha256": file_digest(adapter["path"]),
        "model": model,
        "model_id": model_id,
        "generation_root": str(output_root),
        "case_count": len(jobs),
        "executed_case_count": len(pending),
        "skipped_case_count": len(jobs) - len(pending),
        "command": command,
        "returncode": returncode,
        "error": error,
        "log": str(log_path),
        "request": str(request_path),
        "inventory": inventory,
        "artifacts": artifacts,
    }
    atomic_write_json(audit_path, audit)
    return {**audit, "audit": str(audit_path)}
