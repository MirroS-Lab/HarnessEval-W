"""Seedance 2.0 submit, poll, and download API client."""

from __future__ import annotations

import json
import os
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}


class SeedanceAPIClient:
    """Client for the BytePlus/Volcengine content-generation task API."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = 1800.0,
        poll_interval: float = 10.0,
        retries: int = 4,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.retries = max(retries, 0)

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _request_json(
        self,
        method: str,
        url: str,
        *,
        payload: dict[str, Any] | None = None,
        timeout: float = 60.0,
    ) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        delay = 1.0
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            request = urllib.request.Request(
                url,
                data=body,
                headers=self.headers,
                method=method,
            )
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    text = response.read().decode("utf-8")
                value = json.loads(text) if text.strip() else {}
                if not isinstance(value, dict):
                    raise ValueError("API response is not a JSON object")
                return value
            except urllib.error.HTTPError as exc:
                message = exc.read().decode("utf-8", errors="replace")
                if exc.code not in RETRYABLE_STATUS_CODES or attempt >= self.retries:
                    raise RuntimeError(
                        f"{method} {url} failed: {exc.code} {message}"
                    ) from exc
                last_error = exc
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                if attempt >= self.retries:
                    raise RuntimeError(f"{method} {url} failed: {exc}") from exc
                last_error = exc
            time.sleep(delay)
            delay = min(delay * 2, 8.0)
        raise RuntimeError(f"{method} {url} failed: {last_error}")

    def _download(self, url: str, output: Path, timeout: float = 120.0) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        delay = 1.0
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            tmp_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    dir=str(output.parent),
                    prefix=output.name + ".",
                    suffix=".tmp",
                    delete=False,
                ) as tmp:
                    tmp_path = Path(tmp.name)
                    request = urllib.request.Request(url, method="GET")
                    with urllib.request.urlopen(request, timeout=timeout) as response:
                        while chunk := response.read(1024 * 1024):
                            tmp.write(chunk)
                    tmp.flush()
                    os.fsync(tmp.fileno())
                if tmp_path.stat().st_size == 0:
                    raise RuntimeError("downloaded video is empty")
                tmp_path.replace(output)
                return
            except (urllib.error.URLError, TimeoutError, OSError, RuntimeError) as exc:
                last_error = exc
                if attempt >= self.retries:
                    raise RuntimeError(f"download failed: {url}: {exc}") from exc
            finally:
                if tmp_path is not None and tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
            time.sleep(delay)
            delay = min(delay * 2, 8.0)
        raise RuntimeError(f"download failed: {url}: {last_error}")

    def generate(
        self,
        *,
        endpoint_id: str,
        payload: dict[str, Any],
        output_path: Path,
    ) -> dict[str, Any]:
        submit_url = self.base_url + "/contents/generations/tasks"
        task = self._request_json("POST", submit_url, payload=payload)
        task_id = task.get("id") or task.get("task_id")
        if not task_id:
            raise RuntimeError(f"Seedance submission missing task id: {task}")

        task_url = f"{submit_url}/{task_id}"
        deadline = time.monotonic() + self.timeout
        while True:
            state = self._request_json("GET", task_url)
            status = str(state.get("status") or "").lower()
            if status in {"succeeded", "success"}:
                content = state.get("content") or {}
                video_url = (
                    content.get("video_url") if isinstance(content, dict) else None
                )
                if not video_url:
                    raise RuntimeError(f"Seedance task has no video_url: {state}")
                self._download(str(video_url), output_path)
                return {
                    "name": "seedance",
                    "base_url": self.base_url,
                    "endpoint_id": endpoint_id,
                    "task_id": str(task_id),
                }
            if status in {"failed", "cancelled", "canceled"}:
                raise RuntimeError(f"Seedance task failed: {state}")
            if time.monotonic() > deadline:
                raise TimeoutError(f"Seedance task timed out: {task_id}")
            time.sleep(self.poll_interval)
