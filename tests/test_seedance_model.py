from __future__ import annotations

import base64
import json
import threading
from pathlib import Path
from typing import Any

import pytest

from harnesseval.models.text.prompt_builder import (
    prompt_for_case,
    prompt_for_turn,
    turns_for_case,
)
from harnesseval.models.text.seedance import SeedanceModel, image_data_url


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT_ROOT / "runs/example/results_example/manifest.json"


class FakeSeedanceClient:
    def __init__(self, *, fail_on_call: int | None = None) -> None:
        self.records: list[dict[str, Any]] = []
        self.fail_on_call = fail_on_call
        self._lock = threading.Lock()

    @property
    def payloads(self) -> list[dict[str, Any]]:
        return [record["payload"] for record in self.records]

    def generate(
        self,
        *,
        endpoint_id: str,
        payload: dict[str, Any],
        output_path: Path,
    ) -> dict[str, Any]:
        with self._lock:
            call_number = len(self.records) + 1
            self.records.append(
                {
                    "payload": payload,
                    "output_path": str(output_path),
                    "call_number": call_number,
                }
            )
        if call_number == self.fail_on_call:
            raise RuntimeError(f"offline failure at call {call_number}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(f"offline-seedance-video-{call_number}".encode())
        return {
            "name": "seedance",
            "base_url": "https://example.invalid/api/v3",
            "endpoint_id": endpoint_id,
            "task_id": f"task-{call_number}",
        }


class FakeVideoMedia:
    def __init__(self) -> None:
        self.extractions: list[tuple[Path, Path]] = []
        self.concatenations: list[tuple[list[Path], Path]] = []

    def extract_last_frame(self, video_path: Path, output_path: Path) -> None:
        self.extractions.append((video_path, output_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"last-frame:" + video_path.read_bytes())

    def concatenate(self, segment_paths: list[Path], output_path: Path) -> None:
        paths = list(segment_paths)
        self.concatenations.append((paths, output_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"|".join(path.read_bytes() for path in paths))


def load_cases() -> list[dict[str, Any]]:
    cases = json.loads(MANIFEST.read_text(encoding="utf-8"))["cases"]
    assert len(cases) == 6
    assert sum(len(turns_for_case(case)) for case in cases) == 28
    return cases


def materialize_case(case: dict[str, Any]) -> dict[str, Any]:
    materialized = json.loads(json.dumps(case))
    initial = materialized["world"]["initial_observation"]
    initial["path"] = str((PROJECT_ROOT / initial["path"]).resolve())
    return materialized


def job_for_case(
    case: dict[str, Any], root: Path, *, model_id: str = "seedance-test"
) -> dict[str, Any]:
    taxonomy = case["taxonomy"]
    output_dir = (
        root
        / "outputs"
        / taxonomy["primary_axis"]
        / taxonomy["probe_family"]
        / model_id
        / case["case_id"]
    )
    return {
        "case_id": case["case_id"],
        "action_id": (case.get("interaction") or {})
        .get("action", {})
        .get("action_id", case["case_id"]),
        "taxonomy": taxonomy,
        "model": "seedance-2.0",
        "model_id": model_id,
        "initial_observation": case["world"]["initial_observation"]["path"],
        "action": case["interaction"]["action"],
        "output_dir": str(output_dir),
        "output_video": str(output_dir / "output.mp4"),
        "metadata": str(output_dir / "metadata.json"),
    }


def data_url_bytes(value: str) -> bytes:
    return base64.b64decode(value.split(",", 1)[1])


def test_prompt_builder_covers_six_cases() -> None:
    cases = load_cases()
    prompts = [prompt_for_case(case) for case in cases]
    turn_prompts = []
    for case in cases:
        turns = turns_for_case(case)
        chunks = case["interaction"]["action"].get("chunks") or []
        assert len(turns) == (len(chunks) or 1)
        if chunks:
            assert [turn["action_chunk"] for turn in turns] == chunks
            assert [turn["action"]["chunks"] for turn in turns] == [
                [chunk] for chunk in chunks
            ]
        turn_prompts.extend(prompt_for_turn(case, turn) for turn in turns)

    assert len(prompts) == 6
    assert len(turn_prompts) == 28
    assert all(prompt.strip() for prompt in prompts + turn_prompts)


def test_image_data_url_uses_actual_media_type(tmp_path: Path) -> None:
    image = tmp_path / "first-frame.png"
    image.write_bytes(b"png")
    assert image_data_url(image).startswith("data:image/png;base64,")


def test_seedance_runs_six_case_request_with_fake_client(tmp_path: Path) -> None:
    materialized = [materialize_case(case) for case in load_cases()]
    jobs = [job_for_case(case, tmp_path) for case in materialized]

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"cases": materialized}), encoding="utf-8")
    request_path = tmp_path / "request.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_version": "harnesseval.model_generation_request",
                "adapter_id": "seedance-2.0",
                "model": "seedance-2.0",
                "model_id": "seedance-test",
                "manifest": str(manifest_path),
                "generation_root": str(tmp_path),
                "outputs_root": str(tmp_path / "outputs"),
                "jobs": jobs,
            }
        ),
        encoding="utf-8",
    )

    client = FakeSeedanceClient()
    media = FakeVideoMedia()
    model = SeedanceModel(
        endpoint_id="ep-offline-test",
        api_key="test-key",
        base_url="https://example.invalid/api/v3",
        client=client,
        media=media,
    )
    result = model.run_request(request_path, workers=4)

    assert result["status"] == "passed"
    assert result["requested"] == 6
    assert result["completed"] == 6
    assert result["failed"] == 0
    expected_turns = sum(len(turns_for_case(case)) for case in materialized)
    assert expected_turns == 28
    assert len(client.payloads) == expected_turns
    assert len(media.extractions) == expected_turns
    assert len(media.concatenations) == 6
    records_by_output = {
        Path(record["output_path"]).resolve(): record for record in client.records
    }
    cases_by_id = {case["case_id"]: case for case in materialized}
    for job in jobs:
        case = cases_by_id[job["case_id"]]
        turns = turns_for_case(case)
        output_dir = Path(job["output_dir"])
        metadata = json.loads(Path(job["metadata"]).read_text(encoding="utf-8"))
        assert metadata["case_id"] == job["case_id"]
        assert metadata["model_id"] == "seedance-test"
        assert metadata["prompt"]
        assert metadata["generation"]["turn_count"] == len(turns)
        assert len(metadata["segments"]) == len(turns)
        assert len(metadata["provider"]["task_ids"]) == len(turns)
        assert Path(job["output_video"]).is_file()

        previous_frame = None
        for index, (summary, turn) in enumerate(
            zip(metadata["segments"], turns), start=1
        ):
            segment_dir = output_dir / "segments" / f"segment_{index:03d}"
            segment_video = segment_dir / "output.mp4"
            last_frame = segment_dir / "last_frame.png"
            segment_metadata_path = segment_dir / "metadata.json"
            segment_metadata = json.loads(
                segment_metadata_path.read_text(encoding="utf-8")
            )
            assert summary["turn_index"] == index
            assert summary["chunk_id"] == turn["turn_id"]
            assert summary["segment_video"] == (
                f"segments/segment_{index:03d}/output.mp4"
            )
            assert segment_metadata["case_id"] == job["case_id"]
            assert segment_metadata["turn_id"] == turn["turn_id"]
            assert segment_metadata["task_id"]
            assert not {
                "input_image_sha256",
                "generation_digest",
                "output_video_sha256",
                "last_frame_sha256",
            }.intersection(segment_metadata)
            assert segment_video.is_file()
            assert last_frame.is_file()
            assert (segment_dir / "prompt.txt").read_text(encoding="utf-8") == (
                segment_metadata["prompt"] + "\n"
            )

            record = records_by_output[segment_video.resolve()]
            payload = record["payload"]
            assert payload["content"][0]["text"] == segment_metadata["prompt"]
            input_bytes = data_url_bytes(payload["content"][1]["image_url"]["url"])
            expected_input = (
                Path(job["initial_observation"])
                if previous_frame is None
                else previous_frame
            )
            assert input_bytes == expected_input.read_bytes()
            previous_frame = last_frame

    resumed = model.run_request(request_path, workers=4)
    assert resumed["status"] == "passed"
    assert resumed["completed"] == 0
    assert resumed["skipped"] == 6
    assert len(client.payloads) == expected_turns
    assert len(media.concatenations) == 6


def test_seedance_resumes_completed_turns_after_failure(tmp_path: Path) -> None:
    case = materialize_case(load_cases()[0])
    job = job_for_case(case, tmp_path)
    turns = turns_for_case(case)
    assert len(turns) == 8

    media = FakeVideoMedia()
    failing_client = FakeSeedanceClient(fail_on_call=3)
    failing_model = SeedanceModel(
        endpoint_id="ep-offline-test",
        api_key="test-key",
        base_url="https://example.invalid/api/v3",
        client=failing_client,
        media=media,
    )
    with pytest.raises(RuntimeError, match=r"turn 3/8 .* failed"):
        failing_model.generate_case(case, job)

    segments_root = Path(job["output_dir"]) / "segments"
    assert (segments_root / "segment_001/metadata.json").is_file()
    assert (segments_root / "segment_002/metadata.json").is_file()
    assert not (segments_root / "segment_003/metadata.json").exists()

    resumed_client = FakeSeedanceClient()
    resumed_model = SeedanceModel(
        endpoint_id="ep-offline-test",
        api_key="test-key",
        base_url="https://example.invalid/api/v3",
        client=resumed_client,
        media=media,
    )
    result = resumed_model.generate_case(case, job)

    assert result["code"] == 0
    assert len(result["segments"]) == 8
    assert len(resumed_client.payloads) == 6
    assert Path(resumed_client.records[0]["output_path"]).parent.name == "segment_003"
    chained_input = data_url_bytes(
        resumed_client.payloads[0]["content"][1]["image_url"]["url"]
    )
    assert chained_input == (segments_root / "segment_002/last_frame.png").read_bytes()
    assert Path(job["output_video"]).is_file()
