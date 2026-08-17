#!/usr/bin/env python3
"""Run a small HarnessEval inventory check against existing model outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
for import_root in (SRC_ROOT, PROJECT_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from harnesseval.io import atomic_write_json, read_json  # noqa: E402
from harnesseval.pipeline.inventory import (  # noqa: E402
    VideoProbe,
    build_inventory,
    load_manifest_cases,
    probe_video,
    write_inventory,
)
from harnesseval.protocols import FAMILIES  # noqa: E402


def rollout_dir(generation_root: Path, case: dict[str, Any], model_id: str) -> Path:
    taxonomy = case["taxonomy"]
    return (
        generation_root
        / "outputs"
        / str(taxonomy["primary_axis"])
        / str(taxonomy["probe_family"])
        / model_id
        / str(case["case_id"])
    )


def has_complete_rollout(
    generation_root: Path, case: dict[str, Any], model_id: str
) -> bool:
    root = rollout_dir(generation_root, case, model_id)
    return (root / "metadata.json").is_file() and (root / "output.mp4").is_file()


def select_cases(
    cases: Iterable[dict[str, Any]],
    generation_root: Path,
    model_id: str,
    *,
    case_count: int,
    families: set[str] | None = None,
    case_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    if case_count <= 0:
        raise ValueError("case_count must be positive")
    selected = []
    family_filter = families or set()
    case_filter = case_ids or set()
    for case in cases:
        case_id = str(case["case_id"])
        family = str(case["taxonomy"]["probe_family"])
        if family_filter and family not in family_filter:
            continue
        if case_filter and case_id not in case_filter:
            continue
        if has_complete_rollout(generation_root, case, model_id):
            selected.append(case)

    if case_filter:
        found_ids = {str(case["case_id"]) for case in selected}
        missing = sorted(case_filter - found_ids)
        if missing:
            raise RuntimeError(
                "requested case IDs have no complete rollout: " + ", ".join(missing[:8])
            )
    if len(selected) < case_count:
        scope = "matching filters" if family_filter or case_filter else "manifest"
        raise RuntimeError(
            f"found {len(selected)} complete rollout(s) in {scope}; need {case_count}"
        )
    return selected[:case_count]


def write_smoke_manifest(
    path: Path,
    *,
    source_manifest: Path,
    model_id: str,
    cases: list[dict[str, Any]],
) -> None:
    atomic_write_json(
        path,
        {
            "schema_version": "harnesseval.smoke_manifest",
            "source_manifest": str(source_manifest.resolve()),
            "model_id": model_id,
            "case_count": len(cases),
            "cases": cases,
        },
    )


def link_selected_rollouts(
    *,
    source_generation_root: Path,
    target_generation_root: Path,
    cases: list[dict[str, Any]],
    model_id: str,
) -> None:
    for case in cases:
        source = rollout_dir(source_generation_root, case, model_id)
        target = rollout_dir(target_generation_root, case, model_id)
        target.mkdir(parents=True, exist_ok=True)
        for filename in ("metadata.json", "output.mp4"):
            source_file = (source / filename).resolve(strict=True)
            target_file = target / filename
            if target_file.exists() or target_file.is_symlink():
                target_file.unlink()
            target_file.symlink_to(source_file)


def run_inventory_smoke(
    *,
    manifest: Path,
    generation_root: Path,
    model_id: str,
    output_root: Path,
    assets_root: Path,
    case_count: int = 1,
    families: set[str] | None = None,
    case_ids: set[str] | None = None,
    workers: int = 4,
    full_decode: bool = False,
    video_probe: VideoProbe = probe_video,
) -> dict[str, Any]:
    manifest = manifest.resolve(strict=True)
    source_generation_root = generation_root.resolve(strict=True)
    assets_root = assets_root.resolve()
    output_root = output_root.resolve()

    manifest_payload = read_json(manifest)
    if not isinstance(manifest_payload, dict):
        raise ValueError(f"manifest is not a JSON object: {manifest}")
    cases, manifest_issues = load_manifest_cases([manifest])
    if manifest_issues:
        raise ValueError(f"manifest has validation issues: {manifest_issues[:3]}")

    selected = select_cases(
        cases,
        source_generation_root,
        model_id,
        case_count=case_count,
        families=families,
        case_ids=case_ids,
    )
    smoke_manifest = output_root / "manifest.json"
    smoke_generation_root = output_root / "generation"
    write_smoke_manifest(
        smoke_manifest,
        source_manifest=manifest,
        model_id=model_id,
        cases=selected,
    )
    link_selected_rollouts(
        source_generation_root=source_generation_root,
        target_generation_root=smoke_generation_root,
        cases=selected,
        model_id=model_id,
    )

    rows, audit = build_inventory(
        [smoke_manifest],
        smoke_generation_root,
        [model_id],
        assets_root=assets_root,
        workers=workers,
        full_decode=full_decode,
        video_probe=video_probe,
    )
    artifacts = write_inventory(output_root / "inventory", rows, audit)
    selected_rows = [
        {
            "case_id": str(case["case_id"]),
            "primary_axis": str(case["taxonomy"]["primary_axis"]),
            "probe_family": str(case["taxonomy"]["probe_family"]),
            "source_rollout_dir": str(
                rollout_dir(source_generation_root, case, model_id)
            ),
            "smoke_rollout_dir": str(rollout_dir(smoke_generation_root, case, model_id)),
        }
        for case in selected
    ]
    return {
        "schema_version": "harnesseval.inventory_smoke",
        "status": audit["status"],
        "model_id": model_id,
        "source_generation_root": str(source_generation_root),
        "generation_root": str(smoke_generation_root),
        "manifest": str(smoke_manifest),
        "selected_cases": selected_rows,
        "artifacts": artifacts,
        "audit": audit,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "benchmark/manifest_selected_330.json",
    )
    parser.add_argument("--generation-root", type=Path, required=True)
    parser.add_argument("--model", required=True, dest="model_id")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--assets-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--case-count", type=int, default=1)
    parser.add_argument("--family", action="append", choices=FAMILIES, dest="families")
    parser.add_argument("--case-id", action="append", dest="case_ids")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--full-decode", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    case_ids = set(args.case_ids or ())
    case_count = max(args.case_count, len(case_ids)) if case_ids else args.case_count
    result = run_inventory_smoke(
        manifest=args.manifest,
        generation_root=args.generation_root,
        model_id=args.model_id,
        output_root=args.output_root,
        assets_root=args.assets_root,
        case_count=case_count,
        families=set(args.families or ()),
        case_ids=case_ids,
        workers=args.workers,
        full_decode=args.full_decode,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
