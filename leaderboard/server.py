#!/usr/bin/env python3
"""Serve the leaderboard and collect pending JSON submissions."""

from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
from io import BytesIO
import json
import os
import re
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parent
PENDING_DIR = ROOT / "submissions" / "pending"
MAX_JSON_BODY_BYTES = 2 * 1024 * 1024
MAX_UPLOAD_BODY_BYTES = 25 * 1024 * 1024
FORM_FIELD_KEYS = ("model_name", "model_link", "team_name", "contact_email", "model_type", "accessibility")


def utc_now() -> str:
  return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(value: str) -> str:
  slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
  return slug[:48] or "submission"


def json_response(handler: SimpleHTTPRequestHandler, status: int, payload: dict) -> None:
  body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
  handler.send_response(status)
  handler.send_header("Content-Type", "application/json; charset=utf-8")
  handler.send_header("Content-Length", str(len(body)))
  handler.send_header("Cache-Control", "no-store")
  handler.end_headers()
  handler.wfile.write(body)


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
  server_version = "HarnessEvalLeaderboard/1.0"

  def __init__(self, *args, **kwargs):
    super().__init__(*args, directory=str(ROOT), **kwargs)

  def log_message(self, format: str, *args) -> None:
    timestamp = utc_now()
    print(f"[{timestamp}] {self.address_string()} {format % args}", flush=True)

  def do_GET(self) -> None:
    parsed = urlparse(self.path)
    path = unquote(parsed.path)

    if path == "/api/health":
      json_response(self, HTTPStatus.OK, {"status": "ok", "pending_dir": str(PENDING_DIR)})
      return

    if path.startswith("/submissions/"):
      self.send_error(HTTPStatus.FORBIDDEN, "pending submissions are not public")
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
  parser.add_argument("--port", type=int, default=8922, help="bind port")
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
