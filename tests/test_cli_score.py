from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from harnesseval.cli import DEFAULT_MANIFEST, build_parser
from harnesseval.score import _video_from_metadata


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def score_inputs(tmp_path: Path) -> tuple[Path, Path, dict, dict]:
    video = tmp_path / "output.mp4"
    video.write_bytes(b"video-content")
    metadata_path = tmp_path / "metadata.json"
    write_json(
        metadata_path,
        {
            "output_video": video.name,
        },
    )
    plan = {
        "case_id": "case-1",
        "taxonomy": {"probe_family": "drift_resistance"},
    }
    bundle = {
        "video": {
            "path": str(video),
            "size_bytes": video.stat().st_size,
            "mtime_ns": video.stat().st_mtime_ns,
        }
    }
    return video, metadata_path, plan, bundle


def test_default_manifest_is_the_six_case_release_manifest() -> None:
    manifest = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["summary"]["case_count"] == 6

    args = build_parser().parse_args(
        ["generate", "--adapter", "adapter.json", "--model", "model"]
    )
    assert args.manifest == DEFAULT_MANIFEST


def test_score_cache_ignores_video_mtime(tmp_path: Path) -> None:
    video, metadata_path, plan, bundle = score_inputs(tmp_path)
    original_mtime = video.stat().st_mtime_ns
    os.utime(video, ns=(original_mtime + 1_000_000, original_mtime + 1_000_000))

    _, resolved_video, _ = _video_from_metadata(
        metadata_path, "model-1", plan, bundle
    )

    assert resolved_video == video.resolve()


def test_score_video_mismatch_reports_identity(tmp_path: Path) -> None:
    _, metadata_path, plan, bundle = score_inputs(tmp_path)
    other_video = tmp_path / "other.mp4"
    other_video.write_bytes(b"other")
    bundle["video"]["path"] = str(other_video)

    with pytest.raises(
        ValueError,
        match=r"generation/cache video mismatch.*model-1.*drift_resistance.*case-1",
    ):
        _video_from_metadata(metadata_path, "model-1", plan, bundle)
