from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from harnesseval.models.action.actions import case_to_actions
from harnesseval.models.action.sana_wm_streaming import (
    FPS as SANA_FPS,
    FRAMES_PER_TURN,
    SanaWMStreamingModel,
    actions_to_dsl,
)
from harnesseval.models.camera.hy_worldplay import HYWorldPlayModel
from harnesseval.models.camera.hy_worldplay.poses import LATENTS_PER_TURN, case_to_poses
from harnesseval.models.navigation import navigation_turns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT_ROOT / "runs/example/results_example/manifest.json"
def six_cases() -> list[dict[str, Any]]:
    source = json.loads(MANIFEST.read_text(encoding="utf-8"))["cases"]
    selected = []
    for raw_case in source:
        case = json.loads(json.dumps(raw_case))
        image = PROJECT_ROOT / case["world"]["initial_observation"]["path"]
        case["world"]["initial_observation"]["path"] = str(image.resolve())
        selected.append(case)
    assert len(selected) == 6
    assert sum(len(navigation_turns(case)) for case in selected) == 28
    return selected


def build_request(
    tmp_path: Path,
    cases: list[dict[str, Any]],
    *,
    model: str,
    model_id: str,
) -> tuple[Path, list[dict[str, Any]]]:
    jobs = []
    for case in cases:
        taxonomy = case["taxonomy"]
        output_dir = (
            tmp_path
            / "outputs"
            / taxonomy["primary_axis"]
            / taxonomy["probe_family"]
            / model_id
            / case["case_id"]
        )
        jobs.append(
            {
                "case_id": case["case_id"],
                "taxonomy": taxonomy,
                "model": model,
                "model_id": model_id,
                "initial_observation": case["world"]["initial_observation"]["path"],
                "action": case["interaction"]["action"],
                "output_dir": str(output_dir),
                "output_video": str(output_dir / "output.mp4"),
                "metadata": str(output_dir / "metadata.json"),
            }
        )
    manifest = tmp_path / f"{model_id}-manifest.json"
    manifest.write_text(json.dumps({"cases": cases}), encoding="utf-8")
    request = tmp_path / f"{model_id}-request.json"
    request.write_text(
        json.dumps(
            {
                "schema_version": "harnesseval.model_generation_request",
                "model": model,
                "model_id": model_id,
                "manifest": str(manifest),
                "generation_root": str(tmp_path),
                "jobs": jobs,
            }
        ),
        encoding="utf-8",
    )
    return request, jobs


def option(command: list[str], name: str) -> str:
    return command[command.index(name) + 1]


class FakeRunner:
    def __init__(self, model: str) -> None:
        self.model = model
        self.calls: list[dict[str, Any]] = []

    def __call__(
        self,
        command: list[str],
        cwd: Path,
        environment: dict[str, str],
        log_path: Path,
    ) -> None:
        self.calls.append({"command": command, "cwd": cwd, "environment": environment})
        output_dir = Path(
            option(command, "--output_dir" if self.model == "sana" else "--output_path")
        )
        filename = "harnesseval_streaming.mp4" if self.model == "sana" else "gen.mp4"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / filename).write_bytes(f"offline-{self.model}".encode())


def fake_sana_runtime(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo = tmp_path / "sana"
    (repo / "inference_video_scripts/wm").mkdir(parents=True)
    (repo / "inference_video_scripts/wm/inference_sana_wm_streaming.py").write_text("")
    config = repo / "configs/sana_wm/sana_wm_streaming_1600m_720p.yaml"
    config.parent.mkdir(parents=True)
    config.write_text("model: offline\n")
    model_root = tmp_path / "sana-model"
    (model_root / "sana_dit").mkdir(parents=True)
    (model_root / "sana_dit/model.pt").write_bytes(b"model")
    for directory in ("ltx2_causal_vae", "refiner_diffusers", "gemma3_12b"):
        (model_root / directory).mkdir()
    encoder = tmp_path / "gemma-2-2b-it"
    encoder.mkdir()
    return repo, model_root, encoder


def fake_hy_runtime(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo = tmp_path / "hy-worldplay"
    (repo / "hyvideo").mkdir(parents=True)
    (repo / "hyvideo/generate.py").write_text("")
    base_model = tmp_path / "hunyuan-video-1.5"
    base_model.mkdir()
    (base_model / "config.json").write_text("{}")
    checkpoint = tmp_path / "hy-action.safetensors"
    checkpoint.write_bytes(b"model")
    return repo, base_model, checkpoint


def test_native_model_paths_use_portable_configuration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    for name in (
        "SANA_WM_PYTHON",
        "SANA_WM_RUNTIME_ROOT",
        "SANA_WM_MODEL_ROOT",
        "SANA_WM_STAGE1_TEXT_ENCODER_ROOT",
        "HY_WORLDPLAY_PYTHON",
        "HY_WORLDPLAY_RUNTIME_ROOT",
        "HY_WORLDPLAY_BASE_MODEL",
        "HY_WORLDPLAY_ACTION_CHECKPOINT",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(ValueError, match="SANA_WM_MODEL_ROOT"):
        SanaWMStreamingModel()
    with pytest.raises(ValueError, match="HY_WORLDPLAY_BASE_MODEL"):
        HYWorldPlayModel()

    sana_model_root = tmp_path / "sana-model"
    sana_encoder = tmp_path / "sana-encoder"
    hy_base_model = tmp_path / "hy-base-model"
    hy_checkpoint = tmp_path / "hy-action.safetensors"
    monkeypatch.setenv("SANA_WM_MODEL_ROOT", str(sana_model_root))
    monkeypatch.setenv("SANA_WM_STAGE1_TEXT_ENCODER_ROOT", str(sana_encoder))
    monkeypatch.setenv("HY_WORLDPLAY_BASE_MODEL", str(hy_base_model))
    monkeypatch.setenv("HY_WORLDPLAY_ACTION_CHECKPOINT", str(hy_checkpoint))

    sana = SanaWMStreamingModel()
    hy = HYWorldPlayModel()
    assert sana.python == Path(sys.executable)
    assert sana.runtime_root == PROJECT_ROOT / "third_party/SANA"
    assert sana.model_root == sana_model_root
    assert sana.stage1_text_encoder == sana_encoder
    assert hy.python == Path(sys.executable)
    assert hy.runtime_root == PROJECT_ROOT / "third_party/HY-WorldPlay"
    assert hy.base_model == hy_base_model
    assert hy.action_checkpoint == hy_checkpoint


def test_full_conditioning_sequences_cover_six_cases() -> None:
    cases = six_cases()
    assert sum(case_to_actions(case)["turn_count"] for case in cases) == 28
    assert LATENTS_PER_TURN == 12
    assert sum(case_to_poses(case)["total_latents"] for case in cases) == 336

    offscreen = next(
        case
        for case in cases
        if case["taxonomy"]["probe_family"] == "offscreen_evolution"
    )
    actions = case_to_actions(offscreen)["actions"]
    assert [action["token"] for action in actions] == [
        "left",
        "left",
        "W",
        None,
        "S",
        "right",
        "right",
        None,
    ]
    assert FRAMES_PER_TURN / SANA_FPS == 2
    assert actions_to_dsl(actions) == ("a-48,a-48,w-48,none-48,s-48,d-48,d-48,none-48")


def test_sana_runs_one_native_ar_call_per_case(tmp_path: Path) -> None:
    cases = six_cases()
    request, jobs = build_request(
        tmp_path, cases, model="sana-wm-streaming", model_id="sana-test"
    )
    repo, model_root, encoder = fake_sana_runtime(tmp_path)
    runner = FakeRunner("sana")
    model = SanaWMStreamingModel(
        python=sys.executable,
        runtime_root=repo,
        model_root=model_root,
        stage1_text_encoder=encoder,
        command_runner=runner,
    )

    result = model.run_request(request, workers=1)

    assert result["status"] == "passed"
    assert result["requested"] == result["completed"] == 6
    assert len(runner.calls) == 6
    cases_by_id = {case["case_id"]: case for case in cases}
    assert (
        sum(
            len(option(call["command"], "--action").split(",")) for call in runner.calls
        )
        == 28
    )
    for call in runner.calls:
        command = call["command"]
        case_id = Path(option(command, "--output_dir")).parent.name
        actions = case_to_actions(cases_by_id[case_id])["actions"]
        assert option(command, "--action") == actions_to_dsl(actions)
        assert (
            int(option(command, "--num_frames")) == len(actions) * FRAMES_PER_TURN + 1
        )
        assert int(option(command, "--fps")) == SANA_FPS
    assert (
        sum(
            json.loads(Path(job["metadata"]).read_text())["generation"]["turn_count"]
            for job in jobs
        )
        == 28
    )


def test_hy_runs_one_native_ar_call_per_case(tmp_path: Path) -> None:
    cases = six_cases()
    request, jobs = build_request(
        tmp_path, cases, model="hy-worldplay-1.5", model_id="hy-test"
    )
    repo, base_model, checkpoint = fake_hy_runtime(tmp_path)
    runner = FakeRunner("hy")
    model = HYWorldPlayModel(
        python=sys.executable,
        runtime_root=repo,
        base_model=base_model,
        action_checkpoint=checkpoint,
        command_runner=runner,
    )

    result = model.run_request(request, workers=1)

    assert result["status"] == "passed"
    assert result["requested"] == result["completed"] == 6
    assert len(runner.calls) == 6
    cases_by_id = {case["case_id"]: case for case in cases}
    pose_count = 0
    for call in runner.calls:
        command = call["command"]
        case_id = Path(option(command, "--output_path")).parent.name
        expected = case_to_poses(cases_by_id[case_id])
        poses = json.loads(Path(option(command, "--pose")).read_text())
        pose_count += len(poses)
        assert poses == expected["poses"]
        assert int(option(command, "--video_length")) == expected["video_length"]
        assert option(command, "--model_type") == "ar"
        assert option(command, "--transformer_resident_ar_rollout") == "true"
    assert pose_count == 336
    assert (
        sum(
            json.loads(Path(job["metadata"]).read_text())["generation"]["turn_count"]
            for job in jobs
        )
        == 28
    )
