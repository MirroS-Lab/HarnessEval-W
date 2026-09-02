"""Small subprocess helper for local model runtimes."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable


CommandRunner = Callable[[list[str], Path, dict[str, str], Path], None]


def configured_path(
    value: str | Path | None,
    environment_name: str,
    *,
    default: str | Path | None = None,
) -> Path:
    """Read a model path from an argument, environment variable, or default."""

    for candidate in (value, os.getenv(environment_name), default):
        if candidate is not None and str(candidate).strip():
            return Path(candidate).expanduser()
    raise ValueError(f"set {environment_name}")


def run_command(
    command: list[str], cwd: Path, environment: dict[str, str], log_path: Path
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    if completed.returncode:
        tail = log_path.read_text(encoding="utf-8", errors="replace")[-4000:]
        raise RuntimeError(
            f"model process exited with {completed.returncode}: {tail.strip()}"
        )


def publish_video(source: Path, destination: Path) -> None:
    if not source.is_file() or source.stat().st_size == 0:
        raise RuntimeError(f"model produced no video: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    try:
        shutil.copyfile(source, temporary)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
