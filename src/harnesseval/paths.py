"""Stable paths for the HarnessEval evaluation tree."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = PROJECT_ROOT / "benchmark"
DEPENDENCIES_ROOT = Path(
    os.environ.get("HARNESSEVAL_DEPENDENCIES_ROOT", PROJECT_ROOT / "cache/dependencies")
).expanduser().resolve()


def project_path(relative: str | Path) -> Path:
    """Resolve a project-relative path without depending on the working directory."""

    return (PROJECT_ROOT / relative).resolve()
