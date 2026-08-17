#!/usr/bin/env bash
set -euo pipefail
umask 0002

PROJECT_ROOT=${HARNESSEVAL_PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}
DEST_ROOT=${HARNESSEVAL_METRIC_WEIGHT_DEST:-$PROJECT_ROOT/weights}
REPOSITORY=${HARNESSEVAL_METRIC_WEIGHT_REPOSITORY:-meituan-longcat/WBench-weights}
REVISION=${HARNESSEVAL_METRIC_WEIGHT_REVISION:-1c5fde9aed33c2659a620e244d0151b7741e237d}
HF=${HARNESSEVAL_HF_BIN:-hf}
PYTHON=${HARNESSEVAL_HF_PYTHON:-python3}
HF_HOME_DIR=${HARNESSEVAL_HF_HOME:-$PROJECT_ROOT/cache/huggingface}
HF_XET_CACHE_DIR=${HARNESSEVAL_HF_XET_CACHE:-$HF_HOME_DIR/xet}
LOG_ROOT=${HARNESSEVAL_METRICS_LOG_DIR:-$PROJECT_ROOT/logs/metrics}
STATUS_PATH=${HARNESSEVAL_METRIC_WEIGHT_HF_STATUS:-$LOG_ROOT/weights_hf_download.status}
AUDIT_PATH=${HARNESSEVAL_METRIC_WEIGHT_HF_AUDIT:-$LOG_ROOT/weights_hf_download_audit.json}
DOWNLOAD_RETRIES=${HARNESSEVAL_METRIC_WEIGHT_HF_RETRIES:-3}

INCLUDES=(
  'clip/*'
  'aesthetic/*'
  'pyiqa/*'
  'amt/*'
  'HPSv3/*'
  'Qwen2-VL-7B-Instruct/*'
  'qwen3vl-a3b-visual-plausibility/*'
  'megasam/*'
)
EXCLUDES=(
  'megasam/torch_hub_checkpoints/metric_depth_vit_large_800k.pth'
)

mkdir -p "$DEST_ROOT" "$LOG_ROOT" "$HF_HOME_DIR" "$HF_XET_CACHE_DIR"
rm -f "$STATUS_PATH"

record_status() {
  local status=$?
  printf '%s\n' "$status" >"$STATUS_PATH"
}
trap record_status EXIT

log() {
  printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*"
}

[[ -x "$HF" ]] || {
  echo "missing Hugging Face CLI: $HF" >&2
  exit 2
}
[[ -x "$PYTHON" ]] || {
  echo "missing Hugging Face Python: $PYTHON" >&2
  exit 2
}

download_args=()
for pattern in "${INCLUDES[@]}"; do
  download_args+=(--include "$pattern")
done
for pattern in "${EXCLUDES[@]}"; do
  download_args+=(--exclude "$pattern")
done

download_passed=0
for attempt in $(seq 1 "$DOWNLOAD_RETRIES"); do
  log "downloading frozen WBench metric weights from Hugging Face ($attempt/$DOWNLOAD_RETRIES)"
  if env \
    HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}" \
    HF_HOME="$HF_HOME_DIR" \
    HF_XET_CACHE="$HF_XET_CACHE_DIR" \
    HF_HUB_ENABLE_HF_TRANSFER=0 \
    HF_XET_HIGH_PERFORMANCE=1 \
    HF_XET_NUM_CONCURRENT_RANGE_GETS="${HF_XET_NUM_CONCURRENT_RANGE_GETS:-8}" \
    "$HF" download "$REPOSITORY" \
      --revision "$REVISION" \
      --local-dir "$DEST_ROOT" \
      --max-workers "${HARNESSEVAL_METRIC_WEIGHT_HF_WORKERS:-2}" \
      --format agent \
      "${download_args[@]}"; then
    download_passed=1
    break
  fi
  log "metric weight download attempt $attempt failed; completed files will be reused"
done
if [[ "$download_passed" != 1 ]]; then
  echo "metric weight download failed after $DOWNLOAD_RETRIES attempts" >&2
  exit 1
fi

log "auditing frozen WBench metric weight sizes and LFS SHA256 values"
HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}" "$PYTHON" - \
  "$DEST_ROOT" "$REPOSITORY" "$REVISION" "$AUDIT_PATH" <<'PY'
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from huggingface_hub import HfApi

root = Path(sys.argv[1])
repository = sys.argv[2]
revision = sys.argv[3]
audit_path = Path(sys.argv[4])
groups = {
    "clip",
    "aesthetic",
    "pyiqa",
    "amt",
    "HPSv3",
    "Qwen2-VL-7B-Instruct",
    "qwen3vl-a3b-visual-plausibility",
    "megasam",
}
excluded = {
    "megasam/torch_hub_checkpoints/metric_depth_vit_large_800k.pth",
}

started = time.monotonic()
api = HfApi(endpoint=os.environ.get("HF_ENDPOINT", "https://hf-mirror.com"))
info = api.model_info(repository, revision=revision, files_metadata=True)
if info.sha != revision:
    raise SystemExit(f"metric weight revision mismatch: {info.sha} != {revision}")

records = []
violations = []
for sibling in sorted(info.siblings, key=lambda item: item.rfilename):
    relative = sibling.rfilename
    if relative.split("/", 1)[0] not in groups or relative in excluded:
        continue
    path = root / relative
    expected_size = int(sibling.size)
    expected_sha256 = sibling.lfs.sha256 if sibling.lfs else None
    actual_size = path.stat().st_size if path.is_file() else None
    actual_sha256 = None
    error = None
    if actual_size is None:
        error = "missing"
    elif actual_size != expected_size:
        error = "size_mismatch"
    elif expected_sha256:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
                digest.update(chunk)
        actual_sha256 = digest.hexdigest()
        if actual_sha256 != expected_sha256:
            error = "sha256_mismatch"
    row = {
        "path": relative,
        "expected_size": expected_size,
        "actual_size": actual_size,
        "expected_sha256": expected_sha256,
        "actual_sha256": actual_sha256,
        "error": error,
    }
    records.append(row)
    if error:
        violations.append(row)

audit = {
    "schema_version": "harnesseval.metric_weight_hf_audit",
    "status": "passed" if not violations else "failed",
    "repository": repository,
    "revision": revision,
    "file_count": len(records),
    "expected_bytes": sum(row["expected_size"] for row in records),
    "lfs_file_count": sum(row["expected_sha256"] is not None for row in records),
    "violation_count": len(violations),
    "violations": violations,
    "files": records,
    "elapsed_seconds": round(time.monotonic() - started, 3),
}
audit_path.parent.mkdir(parents=True, exist_ok=True)
temporary = audit_path.with_suffix(audit_path.suffix + ".tmp")
temporary.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
temporary.replace(audit_path)
print(json.dumps({key: audit[key] for key in (
    "status", "file_count", "expected_bytes", "lfs_file_count",
    "violation_count", "elapsed_seconds"
)}, sort_keys=True))
if violations:
    raise SystemExit(1)
PY

date -u +%FT%TZ >"$LOG_ROOT/weights_hf_verified_at.txt"
log "frozen WBench metric weight Hugging Face audit passed"
