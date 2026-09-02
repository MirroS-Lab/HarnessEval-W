"""Media operations shared by multi-turn video model adapters."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Protocol, Sequence


class VideoMedia(Protocol):
    """Minimal media interface needed by a chained video generator."""

    def extract_last_frame(self, video_path: Path, output_path: Path) -> None: ...

    def concatenate(self, segment_paths: Sequence[Path], output_path: Path) -> None: ...


class FFmpegMedia:
    """Extract and concatenate Seedance segments without re-encoding them."""

    def __init__(self, ffmpeg_bin: str = "ffmpeg") -> None:
        self.ffmpeg_bin = ffmpeg_bin

    def _run(self, command: list[str], operation: str) -> None:
        try:
            completed = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
        except OSError as exc:
            raise RuntimeError(f"{operation} could not start: {exc}") from exc
        if completed.returncode != 0:
            detail = completed.stderr.strip()[-4000:]
            raise RuntimeError(f"{operation} failed: {detail or 'ffmpeg error'}")

    def extract_last_frame(self, video_path: Path, output_path: Path) -> None:
        video_path = video_path.expanduser().resolve(strict=True)
        output_path = output_path.expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = output_path.with_name(
            f".{output_path.stem}.{os.getpid()}.tmp{output_path.suffix}"
        )
        temporary.unlink(missing_ok=True)
        try:
            self._run(
                [
                    self.ffmpeg_bin,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-i",
                    str(video_path),
                    "-map",
                    "0:v:0",
                    "-vf",
                    "reverse",
                    "-frames:v",
                    "1",
                    str(temporary),
                ],
                "last-frame extraction",
            )
            if not temporary.is_file() or temporary.stat().st_size == 0:
                raise RuntimeError("last-frame extraction produced no image")
            os.replace(temporary, output_path)
        finally:
            temporary.unlink(missing_ok=True)

    def concatenate(
        self, segment_paths: Sequence[Path], output_path: Path
    ) -> None:
        if not segment_paths:
            raise ValueError("cannot concatenate an empty segment list")
        resolved = [path.expanduser().resolve(strict=True) for path in segment_paths]
        if any(path.stat().st_size == 0 for path in resolved):
            raise RuntimeError("cannot concatenate an empty video segment")

        output_path = output_path.expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if len(resolved) == 1:
            temporary = output_path.with_name(
                f".{output_path.stem}.{os.getpid()}.tmp{output_path.suffix}"
            )
            temporary.unlink(missing_ok=True)
            try:
                shutil.copyfile(resolved[0], temporary)
                os.replace(temporary, output_path)
            finally:
                temporary.unlink(missing_ok=True)
            return

        with tempfile.TemporaryDirectory(
            dir=output_path.parent,
            prefix=f".{output_path.stem}.concat.",
        ) as temporary_directory:
            work = Path(temporary_directory)
            entries = []
            for index, source in enumerate(resolved, start=1):
                link = work / f"segment_{index:06d}.mp4"
                link.symlink_to(source)
                entries.append(f"file '{link.name}'")
            manifest = work / "segments.txt"
            manifest.write_text("\n".join(entries) + "\n", encoding="utf-8")
            combined = work / "combined.mp4"
            self._run(
                [
                    self.ffmpeg_bin,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "1",
                    "-i",
                    str(manifest),
                    "-map",
                    "0:v:0",
                    "-c",
                    "copy",
                    "-movflags",
                    "+faststart",
                    str(combined),
                ],
                "video concatenation",
            )
            if not combined.is_file() or combined.stat().st_size == 0:
                raise RuntimeError("video concatenation produced no output")
            os.replace(combined, output_path)
