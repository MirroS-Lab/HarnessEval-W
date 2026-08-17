#!/usr/bin/env python3
"""Serve the merged HarnessEval-W site and collect pending leaderboard submissions."""

from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
from io import BytesIO
import json
import os
import re
import time
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parent
PENDING_DIR = ROOT / "leaderboard" / "submissions" / "pending"
MAX_JSON_BODY_BYTES = 2 * 1024 * 1024
MAX_UPLOAD_BODY_BYTES = 25 * 1024 * 1024
FORM_FIELD_KEYS = ("model_name", "model_link", "team_name", "contact_email", "model_type", "accessibility")
DATA_SITE_ORIGIN = os.environ.get("HARNESSEVAL_DATA_SITE", "http://127.0.0.1:8770").rstrip("/")
DATA_PROXY_PREFIX = "/data-source"
DATA_CASE_CACHE_SECONDS = 300
DATA_CASE_CACHE: dict[str, object] = {"expires_at": 0.0, "payload": None}
DATA_OUTPUT_CACHE: dict[str, object] = {"expires_at": 0.0, "payload": None}
DATA_GALLERY_INDEX_CACHE: dict[str, object] = {"expires_at": 0.0, "payload": None}
DATA_OUTPUT_CASE_CACHE: dict[str, dict[str, object]] = {}
DATA_SCORE_CACHE: dict[str, dict[str, object]] = {}


def humanize(value: object) -> str:
  text = re.sub(r"[_\s]+", " ", str(value or "")).strip()
  return text.title() if text else "Not specified"


def upstream_data_url(path: object) -> str:
  value = str(path or "")
  if not value:
    return ""
  return value if value.startswith(("http://", "https://")) else urljoin(f"{DATA_SITE_ORIGIN}/", value.lstrip("/"))


def public_data_url(path: object) -> str:
  value = str(path or "").strip()
  if not value:
    return ""

  parsed_value = urlparse(value)
  if parsed_value.scheme or parsed_value.netloc:
    parsed_origin = urlparse(DATA_SITE_ORIGIN)
    if parsed_value.scheme != parsed_origin.scheme or parsed_value.netloc != parsed_origin.netloc:
      return value
    value = parsed_value.path
    if parsed_value.query:
      value = f"{value}?{parsed_value.query}"

  return f"{DATA_PROXY_PREFIX}/{value.lstrip('/')}"


def fetch_remote_json(path: str) -> object:
  request = Request(
    upstream_data_url(path),
    headers={
      "Accept": "application/json",
      "User-Agent": "HarnessEval-W merged site data proxy",
    },
  )
  with urlopen(request, timeout=25) as response:
    raw = response.read()
  return json.loads(raw.decode("utf-8"))


def gallery_index() -> dict:
  now = time.time()
  cached = DATA_GALLERY_INDEX_CACHE.get("payload")
  if cached is not None and now < float(DATA_GALLERY_INDEX_CACHE.get("expires_at") or 0):
    return cached  # type: ignore[return-value]

  remote = fetch_remote_json("/api/gallery-index")
  if not isinstance(remote, dict):
    raise ValueError("data site returned an invalid gallery index")
  DATA_GALLERY_INDEX_CACHE["payload"] = remote
  DATA_GALLERY_INDEX_CACHE["expires_at"] = now + DATA_CASE_CACHE_SECONDS
  return remote


def normalize_score_path(value: object) -> str:
  text = str(value or "").strip()
  if not text:
    raise ValueError("missing score path")

  parsed_origin = urlparse(DATA_SITE_ORIGIN)
  parsed_value = urlparse(text)
  if parsed_value.scheme or parsed_value.netloc:
    if parsed_value.scheme != parsed_origin.scheme or parsed_value.netloc != parsed_origin.netloc:
      raise ValueError("score path must belong to the data site")
    text = parsed_value.path
    if parsed_value.query:
      text = f"{text}?{parsed_value.query}"

  if not text.startswith("/api/scores/"):
    raise ValueError("score path must start with /api/scores/")
  return text


def normalized_model_output_score(path: str) -> dict:
  normalized_path = normalize_score_path(path)
  now = time.time()
  cached = DATA_SCORE_CACHE.get(normalized_path)
  if cached is not None and now < float(cached.get("expires_at") or 0):
    return cached["payload"]  # type: ignore[return-value]

  remote = fetch_remote_json(normalized_path)
  if not isinstance(remote, dict):
    raise ValueError("data site returned an invalid score payload")

  DATA_SCORE_CACHE[normalized_path] = {
    "payload": remote,
    "expires_at": now + DATA_CASE_CACHE_SECONDS,
  }
  return remote


def normalize_data_case(case: dict) -> dict:
  source_tags = case.get("source_tags") if isinstance(case.get("source_tags"), dict) else {}
  action = case.get("action") if isinstance(case.get("action"), dict) else {}
  chunks = action.get("chunks") if isinstance(action.get("chunks"), list) else []
  scene = source_tags.get("scene") or case.get("id")
  family = str(case.get("family") or "unknown_family")
  action_text = str(action.get("text") or "").strip()
  action_type = str(action.get("type") or "").strip()
  chunk_text = "; ".join(
    f"{chunk.get('id')}: {' + '.join(str(item) for item in chunk.get('actions', [])) or '-'}"
    for chunk in chunks
    if isinstance(chunk, dict)
  )
  action_summary = action_text or chunk_text or humanize(action_type)

  return {
    "id": case.get("id"),
    "title": humanize(scene),
    "family": family,
    "type": family,
    "axis": case.get("axis"),
    "cohort": case.get("cohort"),
    "origin": case.get("origin"),
    "originLabel": case.get("origin_label"),
    "scene": scene,
    "perspective": source_tags.get("perspective"),
    "style": source_tags.get("appearance") or source_tags.get("style") or source_tags.get("domain"),
    "subject": source_tags.get("subject") or source_tags.get("law_family"),
    "image": public_data_url(case.get("image_url")),
    "prompt": action_summary,
    "actionType": action_type,
    "actionChunkCount": len(chunks),
    "sourceTags": source_tags,
    "expectedOutcome": case.get("expected_outcome") if isinstance(case.get("expected_outcome"), list) else [],
    "protectedAnchors": case.get("protected_anchors") if isinstance(case.get("protected_anchors"), list) else [],
    "negativeConstraints": case.get("negative_constraints") if isinstance(case.get("negative_constraints"), list) else [],
    "meanScore": case.get("mean_score"),
    "resultCount": case.get("result_count"),
  }


def normalize_output_result(result: dict) -> dict:
  return {
    "model": result.get("model"),
    "modelSlug": result.get("model_slug"),
    "score": result.get("score"),
    "status": result.get("status"),
    "video": public_data_url(result.get("video_url")),
    "poster": public_data_url(result.get("first_frame_url") or result.get("last_frame_url")),
    "scorePath": result.get("score_url"),
    "scoreType": result.get("score_type"),
    "scoreVersion": result.get("score_version"),
    "scoreFormula": result.get("score_formula"),
    "scoreSource": result.get("score_source"),
    "coreScore": result.get("core_score"),
    "coreSkills": result.get("core_skills") if isinstance(result.get("core_skills"), list) else [],
    "observationScore": result.get("observation_score"),
    "observationCount": result.get("observation_count"),
    "routingMode": result.get("routing_mode"),
    "selectedSkills": result.get("selected_skills") if isinstance(result.get("selected_skills"), list) else [],
    "skills": [
      {
        "id": skill.get("id"),
        "role": skill.get("role"),
        "score": skill.get("score"),
        "status": skill.get("status"),
        "reason": skill.get("reason"),
      }
      for skill in result.get("skills") or []
      if isinstance(skill, dict)
    ],
  }


def normalize_skill_plan(plan: object) -> dict:
  if not isinstance(plan, dict):
    return {}

  return {
    "routingMode": plan.get("routing_mode"),
    "plannerVersion": plan.get("planner_version"),
    "selectedSkillIds": plan.get("selected_skill_ids") if isinstance(plan.get("selected_skill_ids"), list) else [],
    "coreSkillIds": plan.get("core_skill_ids") if isinstance(plan.get("core_skill_ids"), list) else [],
    "diagnosticSkillIds": plan.get("diagnostic_skill_ids") if isinstance(plan.get("diagnostic_skill_ids"), list) else [],
    "observationSkillIds": plan.get("observation_skill_ids") if isinstance(plan.get("observation_skill_ids"), list) else [],
    "selectedSkills": [
      {
        "id": skill.get("skill_id") or skill.get("id"),
        "role": skill.get("role"),
        "reason": skill.get("reason"),
        "parameters": skill.get("parameters") if isinstance(skill.get("parameters"), dict) else {},
      }
      for skill in plan.get("selected_skills") or []
      if isinstance(skill, dict)
    ],
    "skippedSkills": [
      {
        "id": skill.get("skill_id") or skill.get("id"),
        "reason": skill.get("reason"),
      }
      for skill in plan.get("skipped_skills") or []
      if isinstance(skill, dict)
    ],
  }


def normalize_model_output_case(case: dict) -> dict:
  source_tags = case.get("source_tags") if isinstance(case.get("source_tags"), dict) else {}
  action = case.get("action") if isinstance(case.get("action"), dict) else {}
  chunks = action.get("chunks") if isinstance(action.get("chunks"), list) else []
  scene = source_tags.get("scene") or case.get("id")
  family = str(case.get("family") or "unknown_family")
  results = [
    normalize_output_result(result)
    for result in case.get("results") or []
    if isinstance(result, dict)
  ]
  image = public_data_url(case.get("image_url"))

  return {
    "id": case.get("id"),
    "title": humanize(scene),
    "family": family,
    "axis": case.get("axis"),
    "cohort": case.get("cohort"),
    "origin": case.get("origin"),
    "originLabel": case.get("origin_label"),
    "scene": scene,
    "image": image,
    "poster": image,
    "action": {
      "type": action.get("type"),
      "text": action.get("text"),
      "chunks": [
        {
          "id": chunk.get("id"),
          "actions": chunk.get("actions") if isinstance(chunk.get("actions"), list) else [],
        }
        for chunk in chunks
        if isinstance(chunk, dict)
      ],
    },
    "skillPlan": normalize_skill_plan(case.get("skill_plan")),
    "meanScore": case.get("mean_score"),
    "resultCount": case.get("result_count") or len(results),
    "results": results,
  }


def normalized_data_cases() -> dict:
  now = time.time()
  cached = DATA_CASE_CACHE.get("payload")
  if cached is not None and now < float(DATA_CASE_CACHE.get("expires_at") or 0):
    return cached  # type: ignore[return-value]

  remote = gallery_index()

  families = []
  for family in remote.get("families") or []:
    if not isinstance(family, dict):
      continue
    family_id = str(family.get("id") or "")
    if not family_id:
      continue
    families.append({"id": family_id, "label": humanize(family_id), "count": family.get("count")})

  cases = [normalize_data_case(item) for item in remote.get("cases") or [] if isinstance(item, dict)]
  payload = {
    "source": DATA_SITE_ORIGIN,
    "datasetId": remote.get("dataset_id"),
    "title": remote.get("title"),
    "subtitle": remote.get("subtitle"),
    "caseCount": remote.get("case_count") or len(cases),
    "families": families,
    "cases": cases,
  }
  DATA_CASE_CACHE["payload"] = payload
  DATA_CASE_CACHE["expires_at"] = now + DATA_CASE_CACHE_SECONDS
  return payload


def normalized_model_output_cases() -> dict:
  now = time.time()
  cached = DATA_OUTPUT_CACHE.get("payload")
  if cached is not None and now < float(DATA_OUTPUT_CACHE.get("expires_at") or 0):
    return cached  # type: ignore[return-value]

  remote = gallery_index()

  families = []
  for family in remote.get("families") or []:
    if not isinstance(family, dict):
      continue
    family_id = str(family.get("id") or "")
    if not family_id:
      continue
    families.append({"id": family_id, "label": humanize(family_id), "count": family.get("count")})

  cases = [
    normalize_model_output_case(item)
    for item in remote.get("cases") or []
    if isinstance(item, dict) and (item.get("result_count") or item.get("results"))
  ]
  payload = {
    "source": DATA_SITE_ORIGIN,
    "datasetId": remote.get("dataset_id"),
    "title": remote.get("title"),
    "subtitle": remote.get("subtitle"),
    "caseCount": len(cases),
    "families": families,
    "cases": cases,
  }
  DATA_OUTPUT_CACHE["payload"] = payload
  DATA_OUTPUT_CACHE["expires_at"] = now + DATA_CASE_CACHE_SECONDS
  return payload


def normalized_model_output_case(case_id: str) -> dict:
  normalized_id = str(case_id or "").strip()
  if not re.fullmatch(r"[A-Za-z0-9_.-]+", normalized_id):
    raise ValueError("invalid case id")

  now = time.time()
  cached = DATA_OUTPUT_CASE_CACHE.get(normalized_id)
  if cached is not None and now < float(cached.get("expires_at") or 0):
    return cached["payload"]  # type: ignore[return-value]

  remote = fetch_remote_json(f"/api/cases/{quote(normalized_id, safe='')}")
  if not isinstance(remote, dict) or not remote.get("results"):
    raise ValueError("data site returned an invalid model output case")
  payload = normalize_model_output_case(remote)
  DATA_OUTPUT_CASE_CACHE[normalized_id] = {
    "payload": payload,
    "expires_at": now + DATA_CASE_CACHE_SECONDS,
  }
  return payload


def utc_now() -> str:
  return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(value: str) -> str:
  slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
  return slug[:48] or "submission"


def json_response(handler: SimpleHTTPRequestHandler, status: int, payload: dict, *, compact: bool = False) -> None:
  if compact:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
  else:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
  try:
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)
  except (BrokenPipeError, ConnectionResetError):
    return


def extract_overall(submission: dict) -> object:
  if "overall" in submission:
    return submission["overall"]
  if "total_score" in submission:
    return submission["total_score"]
  if "total_m_score" in submission:
    return submission["total_m_score"]
  scores = submission.get("scores")
  if isinstance(scores, dict) and "overall" in scores:
    return scores["overall"]
  return None


def validate_submission(submission: object) -> list[str]:
  if not isinstance(submission, dict):
    return ["submission must be a JSON object"]

  errors: list[str] = []
  for key in ("model_name", "model_link", "model_type"):
    if not str(submission.get(key, "")).strip():
      errors.append(f"missing required key: {key}")

  overall = extract_overall(submission)
  if overall in (None, ""):
    errors.append("missing overall score: use overall, total_score, total_m_score, or scores.overall")
  else:
    try:
      numeric = float(overall)
      if numeric < 0 or numeric > 100:
        errors.append("overall score must be in the 0-100 range")
    except (TypeError, ValueError):
      errors.append("overall score must be numeric")

  return errors


def parse_json_object(raw: bytes, source: str) -> object:
  try:
    return json.loads(raw.decode("utf-8"))
  except UnicodeDecodeError as error:
    raise ValueError(f"{source} must be UTF-8") from error
  except json.JSONDecodeError as error:
    raise ValueError(f"invalid JSON in {source}: {error.msg}") from error


def merge_form_fields(submission: object, fields: dict[str, str]) -> object:
  if not isinstance(submission, dict):
    return submission

  merged = dict(submission)
  for key in FORM_FIELD_KEYS:
    value = fields.get(key, "").strip()
    if value:
      merged[key] = value
  return merged


def parse_client_field(raw_client: str) -> object:
  if not raw_client.strip():
    return None
  try:
    return json.loads(raw_client)
  except json.JSONDecodeError:
    return {"raw": raw_client}


def is_safe_zip_path(name: str) -> bool:
  path = PurePosixPath(name)
  return not path.is_absolute() and ".." not in path.parts and all(path.parts)


def extract_verification_files(zip_bytes: bytes, target_dir: Path) -> list[str]:
  written: list[str] = []
  with ZipFile(BytesIO(zip_bytes)) as archive:
    for info in archive.infolist():
      if info.is_dir() or not info.filename.startswith("verification/"):
        continue
      if not is_safe_zip_path(info.filename):
        continue

      relative = PurePosixPath(info.filename)
      destination = target_dir.joinpath(*relative.parts)
      destination.parent.mkdir(parents=True, exist_ok=True)
      destination.write_bytes(archive.read(info))
      written.append(str(destination.relative_to(ROOT)))
  return written


def parse_multipart_submission(content_type: str, body: bytes) -> tuple[object, object, dict]:
  header = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8")
  message = BytesParser(policy=policy.default).parsebytes(header + body)
  if not message.is_multipart():
    raise ValueError("expected multipart/form-data")

  fields: dict[str, str] = {}
  upload: dict | None = None
  for part in message.iter_parts():
    if part.get_content_disposition() != "form-data":
      continue

    name = part.get_param("name", header="content-disposition") or ""
    filename = part.get_filename()
    data = part.get_payload(decode=True) or b""

    if filename:
      upload = {
        "field": name,
        "filename": filename,
        "content_type": part.get_content_type(),
        "bytes": data,
      }
      continue

    charset = part.get_content_charset() or "utf-8"
    fields[name] = data.decode(charset, errors="replace").strip()

  if not upload:
    raise ValueError("missing submission file")

  filename = str(upload["filename"])
  suffix = Path(filename).suffix.lower()
  content_type_lower = str(upload["content_type"]).lower()

  if suffix == ".zip" or "zip" in content_type_lower:
    try:
      with ZipFile(BytesIO(upload["bytes"])) as archive:
        try:
          submission_bytes = archive.read("leaderboard_submission.json")
        except KeyError as error:
          raise ValueError("ZIP must contain leaderboard_submission.json at the root") from error
    except BadZipFile as error:
      raise ValueError("submission ZIP is invalid") from error

    submission = parse_json_object(submission_bytes, "leaderboard_submission.json")
    upload["kind"] = "zip"
    upload["stored_name"] = "submission.zip"
  else:
    submission = parse_json_object(upload["bytes"], filename or "submission file")
    upload["kind"] = "json"
    upload["stored_name"] = "uploaded_leaderboard_submission.json"

  return merge_form_fields(submission, fields), parse_client_field(fields.get("client", "")), upload


class LeaderboardHandler(SimpleHTTPRequestHandler):
  server_version = "HarnessEvalMergedSite/1.0"

  def __init__(self, *args, **kwargs):
    super().__init__(*args, directory=str(ROOT), **kwargs)

  def log_message(self, format: str, *args) -> None:
    timestamp = utc_now()
    print(f"[{timestamp}] {self.address_string()} {format % args}", flush=True)

  def proxy_data_source(self, source_path: str, query: str = "") -> None:
    if not source_path.startswith(("/files/", "/assets/", "/artifacts/")):
      self.send_error(HTTPStatus.NOT_FOUND, "unknown data source path")
      return

    suffix = f"?{query}" if query else ""
    request_headers = {
      "Accept": self.headers.get("Accept", "*/*"),
      "User-Agent": "HarnessEval-W merged site media proxy",
    }
    for header in ("Range", "If-Range", "If-Modified-Since", "If-None-Match"):
      value = self.headers.get(header)
      if value:
        request_headers[header] = value

    request = Request(upstream_data_url(f"{source_path}{suffix}"), headers=request_headers)
    try:
      response = urlopen(request, timeout=60)
    except HTTPError as error:
      response = error
    except (OSError, URLError) as error:
      self.send_error(HTTPStatus.BAD_GATEWAY, f"data source request failed: {error}")
      return

    with response:
      self.send_response(response.status)
      for header in (
        "Content-Type",
        "Content-Length",
        "Content-Range",
        "Accept-Ranges",
        "Cache-Control",
        "ETag",
        "Last-Modified",
      ):
        value = response.headers.get(header)
        if value:
          self.send_header(header, value)
      self.end_headers()
      while True:
        chunk = response.read(1024 * 1024)
        if not chunk:
          break
        try:
          self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
          break

  def do_GET(self) -> None:
    parsed = urlparse(self.path)
    path = unquote(parsed.path)

    if path.startswith(f"{DATA_PROXY_PREFIX}/"):
      source_path = parsed.path[len(DATA_PROXY_PREFIX):]
      self.proxy_data_source(source_path, parsed.query)
      return

    if path == "/api/health":
      json_response(self, HTTPStatus.OK, {"status": "ok", "pending_dir": str(PENDING_DIR)})
      return

    if path == "/api/data-cases":
      try:
        json_response(self, HTTPStatus.OK, normalized_data_cases())
      except Exception as error:
        json_response(self, HTTPStatus.BAD_GATEWAY, {"error": f"could not load data site cases: {error}"})
      return

    if path == "/api/model-output-cases":
      try:
        json_response(self, HTTPStatus.OK, normalized_model_output_cases(), compact=True)
      except Exception as error:
        json_response(self, HTTPStatus.BAD_GATEWAY, {"error": f"could not load model output cases: {error}"})
      return

    if path == "/api/model-output-case":
      query = parse_qs(parsed.query)
      case_id = (query.get("id") or [""])[0]
      try:
        json_response(self, HTTPStatus.OK, normalized_model_output_case(case_id), compact=True)
      except ValueError as error:
        json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(error)})
      except Exception as error:
        json_response(self, HTTPStatus.BAD_GATEWAY, {"error": f"could not load model output case: {error}"})
      return

    if path == "/api/model-output-score":
      query = parse_qs(parsed.query)
      score_path = (query.get("path") or query.get("url") or [""])[0]
      try:
        json_response(self, HTTPStatus.OK, normalized_model_output_score(score_path), compact=True)
      except Exception as error:
        json_response(self, HTTPStatus.BAD_GATEWAY, {"error": f"could not load model output score: {error}"})
      return

    if path.startswith("/submissions/") or path.startswith("/leaderboard/submissions/"):
      self.send_error(HTTPStatus.FORBIDDEN, "pending submissions are not public")
      return

    if path.endswith(".py") or path.endswith(".log"):
      self.send_error(HTTPStatus.FORBIDDEN, "server files are not public")
      return

    super().do_GET()

  def do_POST(self) -> None:
    parsed = urlparse(self.path)
    if parsed.path != "/api/submissions":
      json_response(self, HTTPStatus.NOT_FOUND, {"error": "unknown endpoint"})
      return

    content_type = self.headers.get("Content-Type", "")
    content_type_lower = content_type.lower()
    if "application/json" not in content_type_lower and "multipart/form-data" not in content_type_lower:
      json_response(self, HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "expected application/json or multipart/form-data"})
      return

    try:
      content_length = int(self.headers.get("Content-Length", "0"))
    except ValueError:
      json_response(self, HTTPStatus.BAD_REQUEST, {"error": "invalid Content-Length"})
      return

    if content_length <= 0:
      json_response(self, HTTPStatus.BAD_REQUEST, {"error": "empty request body"})
      return

    max_body_bytes = MAX_JSON_BODY_BYTES if "application/json" in content_type_lower else MAX_UPLOAD_BODY_BYTES
    if content_length > max_body_bytes:
      json_response(self, HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "submission payload is too large"})
      return

    try:
      body = self.rfile.read(content_length)
      upload = None
      if "application/json" in content_type_lower:
        payload = parse_json_object(body, "request body")
        submission = payload.get("submission") if isinstance(payload, dict) else payload
        client = payload.get("client") if isinstance(payload, dict) else None
        submission_mode = "json"
      else:
        payload = None
        submission, client, upload = parse_multipart_submission(content_type, body)
        submission_mode = f"multipart_{upload['kind']}"
    except ValueError as error:
      json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(error)})
      return

    errors = validate_submission(submission)
    if errors:
      json_response(self, HTTPStatus.BAD_REQUEST, {"error": "; ".join(errors)})
      return

    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    received_at = utc_now()
    model_name = str(submission.get("model_name", "submission")).strip()
    submission_id = f"{received_at.replace(':', '').replace('-', '')}-{slugify(model_name)}-{uuid.uuid4().hex[:8]}"
    target_dir = PENDING_DIR / submission_id

    try:
      target_dir.mkdir(mode=0o755, parents=False, exist_ok=False)
      submission_path = target_dir / "leaderboard_submission.json"
      metadata_path = target_dir / "pending_metadata.json"
      submission_path.write_text(json.dumps(submission, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

      upload_metadata = None
      if upload:
        upload_path = target_dir / str(upload["stored_name"])
        upload_path.write_bytes(upload["bytes"])
        verification_files = extract_verification_files(upload["bytes"], target_dir) if upload["kind"] == "zip" else []
        upload_metadata = {
          "kind": upload["kind"],
          "filename": upload["filename"],
          "content_type": upload["content_type"],
          "stored_as": str(upload_path.relative_to(ROOT)),
          "verification_files": verification_files,
        }

      metadata_path.write_text(
        json.dumps(
          {
            "submission_id": submission_id,
            "status": "pending",
            "submission_mode": submission_mode,
            "received_at": received_at,
            "remote_addr": self.client_address[0],
            "user_agent": self.headers.get("User-Agent", ""),
            "client": client,
            "upload": upload_metadata,
            "storage": {
              "submission": str(submission_path.relative_to(ROOT)),
              "metadata": str(metadata_path.relative_to(ROOT)),
            },
          },
          ensure_ascii=False,
          indent=2,
        )
        + "\n",
        encoding="utf-8",
      )
    except OSError as error:
      json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"could not save submission: {error}"})
      return

    json_response(
      self,
      HTTPStatus.ACCEPTED,
      {
        "status": "pending",
        "submission_id": submission_id,
        "message": "submission saved for review; leaderboard data was not updated",
      },
    )


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--host", default="127.0.0.1", help="bind host")
  parser.add_argument("--port", type=int, default=8953, help="bind port")
  return parser.parse_args()


def main() -> None:
  args = parse_args()
  os.chdir(ROOT)
  PENDING_DIR.mkdir(parents=True, exist_ok=True)
  server = ThreadingHTTPServer((args.host, args.port), LeaderboardHandler)
  print(f"Serving {ROOT} on http://{args.host}:{args.port}", flush=True)
  print(f"Pending submissions: {PENDING_DIR}", flush=True)
  server.serve_forever()


if __name__ == "__main__":
  main()
