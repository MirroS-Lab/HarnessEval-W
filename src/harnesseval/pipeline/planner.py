"""LLM-based case-level skill planner for HarnessEval."""

from __future__ import annotations

import base64
import json
import mimetypes
import random
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from ..io import atomic_write_json, file_digest, read_json, value_digest
from ..protocols import CORE_SKILLS, FAMILIES, SKILLS, SKILL_SPECS


PLANNER_VERSION = "harnesseval.planner.v1"
PROMPT_VERSION = "worlddojo.v2_planner.prompt.v8"
PLAN_SCHEMA = "harnesseval.skill_plan"
RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}
VALID_ROLES = {"observation", "core", "diagnostic"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class PlannerConfig:
    output_root: Path
    model: str
    base_url: str
    api_key: str | None = None
    wire_api: str = "responses"
    timeout: float = 120.0
    retries: int = 2
    assets_root: Path | None = None


@dataclass(frozen=True)
class PlanTask:
    case: dict[str, Any]
    output_path: Path
    input_digest: str
    status: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case["case_id"],
            "probe_family": self.case["taxonomy"]["probe_family"],
            "output": str(self.output_path),
            "input_digest": self.input_digest,
            "status": self.status,
            "reason": self.reason,
        }


def load_cases(manifests: Iterable[Path]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    sources: dict[str, Path] = {}
    for manifest_path in manifests:
        manifest = read_json(manifest_path)
        cases = manifest.get("cases") if isinstance(manifest, dict) else None
        if not isinstance(cases, list):
            raise ValueError(f"manifest has no cases array: {manifest_path}")
        for case in cases:
            if not isinstance(case, dict) or not case.get("case_id"):
                raise ValueError(f"manifest contains an invalid case: {manifest_path}")
            case_id = str(case["case_id"])
            family = str((case.get("taxonomy") or {}).get("probe_family") or "")
            if family not in FAMILIES:
                raise ValueError(
                    f"case {case_id!r} has unsupported HarnessEval family {family!r}"
                )
            if case_id in by_id and by_id[case_id] != case:
                raise ValueError(
                    f"case {case_id!r} differs between {sources[case_id]} and {manifest_path}"
                )
            by_id[case_id] = case
            sources[case_id] = manifest_path
    return [by_id[case_id] for case_id in sorted(by_id)]


def initial_observation_path(
    case: dict[str, Any], assets_root: Path | None
) -> Path | None:
    observation = (case.get("world") or {}).get("initial_observation")
    raw_path = observation.get("path") if isinstance(observation, dict) else observation
    if not isinstance(raw_path, str) or not raw_path:
        return None
    path = Path(raw_path)
    candidates = [path] if path.is_absolute() else []
    if assets_root is not None and not path.is_absolute():
        candidates.append(assets_root / path)
    localization = (case.get("non_model_facing") or {}).get(
        "initial_observation_localization"
    ) or {}
    for key in ("localized_path", "source_path", "original_path"):
        value = localization.get(key) if isinstance(localization, dict) else None
        if not value:
            continue
        candidate = Path(str(value))
        candidates.append(
            candidate
            if candidate.is_absolute() or assets_root is None
            else assets_root / candidate
        )
    return next((candidate.resolve() for candidate in candidates if candidate.is_file()), None)


def plan_path(output_root: Path, family: str, case_id: str) -> Path:
    return output_root / family / f"{case_id}.skill_plan.json"


def skill_catalog() -> list[dict[str, Any]]:
    catalog = []
    for skill_id in SKILLS:
        item = {
            "skill_id": skill_id,
            "default_role": SKILL_SPECS[skill_id]["default_role"],
            "question": SKILL_SPECS[skill_id]["question"],
        }
        core_for = [
            family for family in FAMILIES if skill_id in CORE_SKILLS.get(family, ())
        ]
        if core_for:
            item["core_for"] = core_for
        diagnostic_for = SKILL_SPECS[skill_id].get("diagnostic_for")
        if diagnostic_for:
            item["diagnostic_for"] = list(diagnostic_for)
        catalog.append(item)
    return catalog


def planner_messages(case: dict[str, Any]) -> list[dict[str, str]]:
    system = "\n".join(
        [
            "You are an evaluation skill planner.",
            "Given the complete case definition, initial world observation, and skill catalog, "
            "design a comprehensive evaluation plan for the generated result.",
            "Consider general visual quality, motion quality, consistency, physical plausibility, "
            "and the case-specific world behavior and constraints.",
            "Catalog core_for and diagnostic_for fields indicate primary use, not an allowlist; "
            "select outside them only when the case gives a concrete reason.",
            "Choose the applicable skills and ground each reason in the case requirements.",
            "Return one JSON object and no surrounding prose.",
        ]
    )
    payload = {
        "case": case,
        "skill_catalog": skill_catalog(),
        "output_schema": {
            "selected_skills": [
                {
                    "skill_id": "skill id from the catalog",
                    "role": "one of observation, core, diagnostic",
                    "reason": "short case-grounded reason",
                    "parameters": {},
                }
            ],
            "skipped_skills": [
                {"skill_id": "skill id from the catalog", "reason": "short reason"}
            ],
        },
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(payload, indent=2, ensure_ascii=False)},
    ]


def planner_input_digest(case: dict[str, Any], config: PlannerConfig) -> str:
    image = initial_observation_path(case, config.assets_root)
    return value_digest(
        {
            "planner_version": PLANNER_VERSION,
            "prompt_version": PROMPT_VERSION,
            "model": config.model,
            "wire_api": config.wire_api,
            "case": case,
            "initial_observation_sha256": file_digest(image) if image else None,
            "skill_catalog": skill_catalog(),
        }
    )


def _image_data_url(path: Path | None) -> str | None:
    if path is None:
        return None
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def _responses_input(
    messages: list[dict[str, str]], image_url: str | None
) -> list[dict[str, Any]]:
    converted = []
    for message in messages:
        content: list[dict[str, Any]] = [
            {"type": "input_text", "text": message["content"]}
        ]
        if message["role"] == "user" and image_url:
            content.append({"type": "input_image", "image_url": image_url})
        converted.append(
            {
                "role": "developer" if message["role"] == "system" else message["role"],
                "content": content,
            }
        )
    return converted


def _chat_messages(
    messages: list[dict[str, str]], image_url: str | None
) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for message in messages:
        if message["role"] != "user" or not image_url:
            converted.append(message)
            continue
        converted.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": message["content"]},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        )
    return converted


def _request_targets(config: PlannerConfig) -> tuple[list[str], dict[str, Any]]:
    base_url = config.base_url.rstrip("/")
    wire_api = config.wire_api.lower()
    if wire_api in {"responses", "response"}:
        urls = (
            [base_url]
            if base_url.endswith("/responses")
            else [f"{base_url}/responses", f"{base_url}/v1/responses"]
        )
        body = {
            "model": config.model,
            "input": [],
            "temperature": 0,
            "max_output_tokens": 1800,
            "text": {"format": {"type": "json_object"}},
        }
    elif wire_api in {"chat", "chat_completions", "chat/completions"}:
        urls = (
            [base_url]
            if base_url.endswith("/chat/completions")
            else [f"{base_url}/chat/completions", f"{base_url}/v1/chat/completions"]
        )
        body = {
            "model": config.model,
            "messages": [],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
    else:
        raise ValueError(f"unsupported planner wire API: {config.wire_api}")
    return urls, body


def _post_json(
    url: str, headers: dict[str, str], body: dict[str, Any], timeout: float
) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(response.status)
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        raw = exc.read().decode("utf-8", errors="replace")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = {"error": raw[:1000]}
    return status, value if isinstance(value, dict) else {"response": value}


def _response_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str) and response["output_text"].strip():
        return response["output_text"]
    choices = response.get("choices") or []
    if choices and isinstance(choices[0], dict):
        content = (choices[0].get("message") or {}).get("content")
        if isinstance(content, str) and content.strip():
            return content
    chunks = []
    for item in response.get("output") or []:
        if not isinstance(item, dict):
            continue
        for content in item.get("content") or []:
            text = content.get("text") if isinstance(content, dict) else None
            if isinstance(text, str):
                chunks.append(text)
    if chunks:
        return "\n".join(chunks)
    raise ValueError("planner response has no output text")


def _extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[-1]
        if stripped.endswith("```"):
            stripped = stripped[:-3].strip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("planner response is not a JSON object") from None
        value = json.loads(stripped[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("planner response JSON must be an object")
    return value


def call_llm_planner(case: dict[str, Any], config: PlannerConfig) -> dict[str, Any]:
    messages = planner_messages(case)
    image_url = _image_data_url(initial_observation_path(case, config.assets_root))
    urls, body = _request_targets(config)
    body = dict(body)
    if config.wire_api.lower() in {"responses", "response"}:
        body["input"] = _responses_input(messages, image_url)
    else:
        body["messages"] = _chat_messages(messages, image_url)

    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"

    started = time.monotonic()
    attempts = []
    last_error = None
    for url in urls:
        for attempt in range(1, max(1, config.retries + 1) + 1):
            attempt_started = time.monotonic()
            try:
                status, response = _post_json(url, headers, body, config.timeout)
                error = None
            except (TimeoutError, urllib.error.URLError) as exc:
                status, response, error = None, {}, repr(exc)
            attempts.append(
                {
                    "attempt": attempt,
                    "url": url,
                    "status_code": status,
                    "error": error,
                    "elapsed_seconds": round(time.monotonic() - attempt_started, 6),
                }
            )
            if status is not None and status < 400:
                candidate = _extract_json_object(_response_text(response))
                candidate["planner"] = {
                    "type": "openai_compatible",
                    "version": PLANNER_VERSION,
                    "prompt_version": PROMPT_VERSION,
                    "model": config.model,
                    "wire_api": config.wire_api,
                    "request_url": url,
                    "response_id": response.get("id"),
                    "response_model": response.get("model"),
                    "usage": response.get("usage"),
                    "elapsed_seconds": round(time.monotonic() - started, 6),
                    "attempt_count": len(attempts),
                }
                return candidate
            last_error = error or json.dumps(response, ensure_ascii=False)[:1000]
            if status is not None and status not in RETRYABLE_STATUS_CODES:
                break
            if attempt <= config.retries:
                time.sleep(
                    min(0.5 * (2 ** (attempt - 1)), 8.0)
                    + random.uniform(0.0, 0.25)
                )
        if attempts and attempts[-1]["status_code"] not in {404, 405}:
            break
    raise RuntimeError(f"planner request failed: {last_error}")


def build_plan(
    candidate: dict[str, Any], case: dict[str, Any], input_digest: str
) -> dict[str, Any]:
    selected = []
    seen = set()
    errors = []
    for raw in candidate.get("selected_skills") or []:
        if not isinstance(raw, dict):
            errors.append({"reason": "selection_is_not_an_object"})
            continue
        skill_id = str(raw.get("skill_id") or "")
        role = str(raw.get("role") or "")
        if skill_id not in SKILL_SPECS:
            errors.append({"skill_id": skill_id, "reason": "unknown_skill"})
        elif skill_id in seen:
            errors.append({"skill_id": skill_id, "reason": "duplicate_skill"})
        elif role not in VALID_ROLES:
            errors.append({"skill_id": skill_id, "reason": "invalid_role", "role": role})
        else:
            selected.append(
                {
                    "skill_id": skill_id,
                    "role": role,
                    "reason": str(raw.get("reason") or "planner selected"),
                    "parameters": raw.get("parameters")
                    if isinstance(raw.get("parameters"), dict)
                    else {},
                }
            )
            seen.add(skill_id)

    role_counts = Counter(item["role"] for item in selected)
    if not role_counts["core"]:
        errors.append({"reason": "missing_core_skill"})
    if not role_counts["observation"]:
        errors.append({"reason": "missing_observation_skill"})
    if errors:
        raise ValueError(
            "planner returned an invalid skill plan: "
            + json.dumps(errors, ensure_ascii=False)
        )

    order = {skill_id: index for index, skill_id in enumerate(SKILLS)}
    selected.sort(key=lambda item: order[item["skill_id"]])
    skipped = []
    for raw in candidate.get("skipped_skills") or []:
        if not isinstance(raw, dict):
            continue
        skill_id = str(raw.get("skill_id") or "")
        if skill_id in SKILL_SPECS and skill_id not in seen:
            skipped.append(
                {"skill_id": skill_id, "reason": str(raw.get("reason") or "not selected")}
            )

    family = str(case["taxonomy"]["probe_family"])
    return {
        "schema_version": PLAN_SCHEMA,
        "planner_version": PLANNER_VERSION,
        "created_at": utc_now(),
        "routing_mode": "llm_case",
        "input_digest": input_digest,
        "case_id": str(case["case_id"]),
        "taxonomy": {
            "primary_axis": str(case["taxonomy"]["primary_axis"]),
            "probe_family": family,
        },
        "planner": candidate.get("planner") if isinstance(candidate.get("planner"), dict) else {},
        "selected_skills": selected,
        "selected_skill_ids": [item["skill_id"] for item in selected],
        "skipped_skills": skipped,
        "validation": {
            "status": "ok",
            "registered_skill_count": len(SKILLS),
            "selected_skill_count": len(selected),
            "selection_source": "planner",
            "selection_modified": False,
        },
    }


def plan_tasks(
    cases: Iterable[dict[str, Any]], config: PlannerConfig, *, refresh: bool = False
) -> list[PlanTask]:
    tasks = []
    for case in cases:
        family = str(case["taxonomy"]["probe_family"])
        case_id = str(case["case_id"])
        output_path = plan_path(config.output_root, family, case_id)
        input_digest = planner_input_digest(case, config)
        if refresh:
            status, reason = "pending", "refresh requested"
        elif not output_path.is_file():
            status, reason = "pending", "no existing plan"
        else:
            existing = read_json(output_path)
            if (
                existing.get("schema_version") == PLAN_SCHEMA
                and existing.get("planner_version") == PLANNER_VERSION
                and existing.get("input_digest") == input_digest
                and existing.get("case_id") == case_id
            ):
                status, reason = "cached", "identical plan already exists"
            else:
                status, reason = "stale", "existing plan was made from different inputs"
        tasks.append(PlanTask(case, output_path, input_digest, status, reason))
    return tasks


def task_summary(tasks: Iterable[PlanTask], *, details: bool = False) -> dict[str, Any]:
    items = list(tasks)
    status_counts = Counter(task.status for task in items)
    family_counts = Counter(task.case["taxonomy"]["probe_family"] for task in items)
    result: dict[str, Any] = {
        "schema_version": "harnesseval.plan_tasks",
        "task_count": len(items),
        "status_counts": dict(sorted(status_counts.items())),
        "family_counts": dict(sorted(family_counts.items())),
    }
    if details:
        result["tasks"] = [task.to_dict() for task in items]
    return result


def execute_plan_tasks(
    tasks: Iterable[PlanTask], config: PlannerConfig, *, workers: int = 4
) -> dict[str, Any]:
    tasks = list(tasks)
    eligible = [task for task in tasks if task.status == "pending"]
    written = []
    failures = []

    def run(task: PlanTask) -> str:
        candidate = call_llm_planner(task.case, config)
        plan = build_plan(candidate, task.case, task.input_digest)
        atomic_write_json(task.output_path, plan)
        return str(task.output_path.resolve())

    with ThreadPoolExecutor(max_workers=max(1, min(workers, len(eligible) or 1))) as pool:
        futures = {pool.submit(run, task): task for task in eligible}
        for future in as_completed(futures):
            task = futures[future]
            try:
                written.append(future.result())
            except Exception as exc:  # noqa: BLE001 - each failed plan is reported
                failures.append(
                    {
                        "case_id": task.case["case_id"],
                        "probe_family": task.case["taxonomy"]["probe_family"],
                        "error": repr(exc),
                    }
                )

    status_counts = Counter(task.status for task in tasks)
    return {
        "schema_version": "harnesseval.plan_execution",
        "created_at": utc_now(),
        "requested": len(tasks),
        "eligible": len(eligible),
        "written": len(written),
        "cached": status_counts["cached"],
        "stale_not_refreshed": status_counts["stale"],
        "failed": len(failures),
        "failures": failures,
        "written_paths": sorted(written),
    }


def write_plan_audit(
    output_root: Path, plan: dict[str, Any], execution: dict[str, Any]
) -> Path:
    audit_path = output_root.resolve() / "PLAN_AUDIT.json"
    atomic_write_json(
        audit_path,
        {
            "schema_version": "harnesseval.plan_run_audit",
            "created_at": utc_now(),
            "plan": plan,
            "execution": {k: v for k, v in execution.items() if k != "written_paths"},
        },
    )
    return audit_path
