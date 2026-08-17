#!/usr/bin/env python3
"""Run one HarnessEval model on a single machine with one or more GPUs."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from harnesseval.io import atomic_write_json  # noqa: E402
from harnesseval.pipeline import runner as skill_runner  # noqa: E402
from harnesseval.pipeline.inventory import build_inventory, write_inventory  # noqa: E402


DRIFT_SKILL = "drift_degradation_analyzer"
VLM_SKILLS = (
    "intentional_change_verifier_vlm",
    "physical_response_verifier_vlm",
    "offscreen_evolution_verifier",
)


@dataclass(frozen=True)
class Job:
    name: str
    skill: str
    interpreter: str = "metrics"
    drift_stage: str | None = None


GPU_JOBS = (
    Job("render", "render_quality_inspector"),
    Job("drift-render", DRIFT_SKILL, drift_stage="render"),
    Job("motion", "motion_quality_inspector"),
    Job("drift-motion", DRIFT_SKILL, drift_stage="motion"),
    Job("appearance", "appearance_consistency_inspector"),
    Job("physical", "physical_plausibility_inspector", "pavrm"),
    Job("drift-physical", DRIFT_SKILL, "pavrm", "physical"),
    Job("viewpoint", "viewpoint_trajectory_verifier"),
    Job("return", "return_consistency_verifier"),
    Job("drift-clip", DRIFT_SKILL, drift_stage="clip"),
)


def parse_gpus(value: str) -> list[str]:
    gpus = [gpu.strip() for gpu in value.split(",") if gpu.strip()]
    if not gpus or len(gpus) != len(set(gpus)):
        raise ValueError("--gpus must contain unique GPU IDs")
    if any(not gpu.isdigit() for gpu in gpus):
        raise ValueError("GPU IDs must be non-negative integers")
    return gpus


def paths_for(args: argparse.Namespace) -> dict[str, Path]:
    root = args.harnesseval_root
    model_root = root / "models" / args.model_id
    return {
        "inventory": model_root / "inventory",
        "cache": root / "metric_cache",
        "evaluation": model_root / "evaluation",
        "backend_config": model_root / "backend_config.json",
        "lock": model_root / ".eval.lock",
    }


@contextmanager
def evaluation_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o664)
    except FileExistsError as error:
        raise RuntimeError(f"evaluation is already running: {path}") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as lock:
            lock.write(f"{os.getpid()}\n")
        yield
    finally:
        path.unlink(missing_ok=True)


def backend_config(args: argparse.Namespace) -> dict[str, Any]:
    common = {
        "mode": "local",
        "weights_root": str(args.weights_root),
    }
    return {
        "skills": {
            "render_quality_inspector": dict(common),
            "motion_quality_inspector": dict(common),
            "appearance_consistency_inspector": dict(common),
            "physical_plausibility_inspector": {
                **common,
                "model_path": str(
                    args.weights_root / "qwen3vl-a3b-visual-plausibility"
                ),
            },
            "viewpoint_trajectory_verifier": {
                **common,
                "weights_root": str(args.weights_root / "megasam"),
            },
            "physical_law_validator": {"mode": "local"},
            DRIFT_SKILL: {"mode": "staged_local"},
            "return_consistency_verifier": {"mode": "local"},
        },
        "clip": {
            "mode": "local",
            "download_root": str(args.weights_root / "clip"),
        },
    }


def environment(args: argparse.Namespace, gpu: str | None = None) -> dict[str, str]:
    result = os.environ.copy()
    python_path = [str(SRC_ROOT), str(PROJECT_ROOT)]
    if inherited := result.get("PYTHONPATH"):
        python_path.append(inherited)
    result.update(
        {
            "PYTHONPATH": os.pathsep.join(python_path),
            "PYTHONUNBUFFERED": "1",
            "TOKENIZERS_PARALLELISM": "false",
            "HARNESSEVAL_WEIGHTS_ROOT": str(args.weights_root),
        }
    )
    result.setdefault(
        "HARNESSEVAL_DEPENDENCIES_ROOT",
        str(PROJECT_ROOT / "cache/dependencies"),
    )
    if gpu is not None:
        result["CUDA_VISIBLE_DEVICES"] = gpu
        result["HARNESSEVAL_MEGASAM_TMPDIR"] = str(
            Path(tempfile.gettempdir()) / "harnesseval" / f"gpu-{gpu}"
        )
    if args.api_key_file.is_file():
        api_key = args.api_key_file.read_text(encoding="utf-8").strip()
        if api_key:
            result["HARNESSEVAL_VLM_API_KEY"] = api_key
    return result


def prepare(args: argparse.Namespace, paths: dict[str, Path]) -> None:
    rows, audit = build_inventory(
        [args.manifest],
        args.generation_root,
        [args.model_id],
        assets_root=PROJECT_ROOT,
    )
    write_inventory(paths["inventory"], rows, audit)
    if audit.get("status") != "passed":
        raise RuntimeError("generation inventory failed")
    atomic_write_json(paths["backend_config"], backend_config(args))
    print(f"prepared {audit['valid_rollout_count']} rollouts", flush=True)


def skill_cases(
    args: argparse.Namespace, paths: dict[str, Path], skill: str
) -> list[str]:
    tasks = skill_runner.plan_skill_tasks(
        paths["inventory"],
        [args.manifest],
        args.plan_root,
        paths["cache"],
        skill_ids={skill},
        model_ids={args.model_id},
    )
    return sorted({task.case_id for task in tasks})


def skill_command(
    args: argparse.Namespace,
    paths: dict[str, Path],
    job: Job,
    case_ids: list[str],
) -> list[str]:
    python = args.pavrm_python if job.interpreter == "pavrm" else args.metrics_python
    command = [
        str(python),
        "-m",
        "harnesseval.cli",
        "eval",
        "run-skills",
        "--manifest",
        str(args.manifest),
        "--inventory-root",
        str(paths["inventory"]),
        "--plan-root",
        str(args.plan_root),
        "--cache-root",
        str(paths["cache"]),
        "--backend-config",
        str(paths["backend_config"]),
        "--model",
        args.model_id,
        "--skill",
        job.skill,
        "--execute",
    ]
    if job.drift_stage:
        command.extend(("--drift-stage", job.drift_stage))
    for case_id in case_ids:
        command.extend(("--case-id", case_id))
    return command


def run_gpu_job(
    args: argparse.Namespace,
    paths: dict[str, Path],
    job: Job,
    gpus: list[str],
    case_ids: list[str],
) -> None:
    if not case_ids:
        print(f"[{job.name}] no selected cases", flush=True)
        return
    active_gpus = gpus[: min(len(gpus), len(case_ids))]
    groups = [case_ids[index :: len(active_gpus)] for index in range(len(active_gpus))]
    print(
        f"[{job.name}] {len(case_ids)} cases on {len(active_gpus)} GPU(s)",
        flush=True,
    )
    processes = [
        (
            gpu,
            subprocess.Popen(
                skill_command(args, paths, job, group),
                cwd=PROJECT_ROOT,
                env=environment(args, gpu),
            ),
        )
        for gpu, group in zip(active_gpus, groups, strict=True)
    ]
    try:
        failures = []
        for gpu, process in processes:
            return_code = process.wait()
            if return_code:
                failures.append((gpu, return_code))
    except KeyboardInterrupt:
        for _, process in processes:
            process.terminate()
        for _, process in processes:
            process.wait()
        raise
    if failures:
        raise RuntimeError(f"{job.name} failed: {failures}")


def run_command(command: list[str], args: argparse.Namespace) -> None:
    subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=environment(args),
        check=True,
    )


def common_skill_command(
    args: argparse.Namespace, paths: dict[str, Path], config: Path
) -> list[str]:
    return [
        str(args.metrics_python),
        "-m",
        "harnesseval.cli",
        "eval",
        "run-skills",
        "--manifest",
        str(args.manifest),
        "--inventory-root",
        str(paths["inventory"]),
        "--plan-root",
        str(args.plan_root),
        "--cache-root",
        str(paths["cache"]),
        "--backend-config",
        str(config),
        "--model",
        args.model_id,
        "--execute",
    ]


def finalize(args: argparse.Namespace, paths: dict[str, Path]) -> None:
    local = common_skill_command(args, paths, paths["backend_config"])
    run_command([*local, "--skill", DRIFT_SKILL], args)
    run_command([*local, "--skill", "physical_law_validator"], args)

    vlm = common_skill_command(args, paths, args.vlm_config)
    for skill in VLM_SKILLS:
        vlm.extend(("--skill", skill))
    run_command(vlm, args)

    run_command(
        [
            sys.executable,
            "-m",
            "harnesseval.cli",
            "eval",
            "score",
            "--generation-root",
            str(args.generation_root),
            "--plan-root",
            str(args.plan_root),
            "--cache-root",
            str(paths["cache"]),
            "--eval-root",
            str(paths["evaluation"]),
            "--model",
            args.model_id,
            "--refresh-stale",
            "--execute",
        ],
        args,
    )


def status(paths: dict[str, Path], model_id: str) -> dict[str, Any]:
    inventory = paths["inventory"] / "INPUT_AUDIT.json"
    summary = paths["evaluation"] / "summary.json"
    return {
        "model_id": model_id,
        "prepared": inventory.is_file(),
        "complete": summary.is_file(),
        "inventory": str(inventory),
        "evaluation": str(paths["evaluation"]),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--harnesseval-root", type=Path, required=True)
    result.add_argument("--generation-root", type=Path, required=True)
    result.add_argument("--manifest", type=Path, required=True)
    result.add_argument("--plan-root", type=Path, required=True)
    result.add_argument("--model-id", required=True)
    result.add_argument("--gpus", default="0")
    result.add_argument("--metrics-python", type=Path, default=Path(sys.executable))
    result.add_argument("--pavrm-python", type=Path, default=Path(sys.executable))
    result.add_argument("--weights-root", type=Path, default=PROJECT_ROOT / "weights")
    result.add_argument(
        "--vlm-config",
        type=Path,
        default=PROJECT_ROOT / "examples/vlm_backend_config.json",
    )
    result.add_argument(
        "--api-key-file",
        type=Path,
        default=PROJECT_ROOT / "secrets/api_key.txt",
    )
    result.add_argument("--prepare-only", action="store_true")
    result.add_argument("--status", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    args.harnesseval_root = args.harnesseval_root.expanduser().resolve()
    args.generation_root = args.generation_root.expanduser().resolve(strict=True)
    args.manifest = args.manifest.expanduser().resolve(strict=True)
    args.plan_root = args.plan_root.expanduser().resolve(strict=True)
    args.weights_root = args.weights_root.expanduser().resolve()
    args.vlm_config = args.vlm_config.expanduser().resolve()
    args.api_key_file = args.api_key_file.expanduser().resolve()
    paths = paths_for(args)

    if args.status:
        print(json.dumps(status(paths, args.model_id), ensure_ascii=False, indent=2))
        return 0

    with evaluation_lock(paths["lock"]):
        prepare(args, paths)
        if args.prepare_only:
            return 0

        gpus = parse_gpus(args.gpus)
        cases_by_skill: dict[str, list[str]] = {}
        for job in GPU_JOBS:
            if job.skill not in cases_by_skill:
                cases_by_skill[job.skill] = skill_cases(args, paths, job.skill)
            run_gpu_job(args, paths, job, gpus, cases_by_skill[job.skill])
        finalize(args, paths)
    print(f"evaluation written to {paths['evaluation']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
