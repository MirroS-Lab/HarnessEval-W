#!/usr/bin/env bash
# Run HarnessEval on one machine with one or more GPUs.
set -euo pipefail
umask 0002

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

require() {
  local name=$1 hint=$2
  if [[ -z "${!name:-}" ]]; then
    echo "error: \$$name is not set. $hint" >&2
    echo "       see config/example.env" >&2
    exit 2
  fi
}

require MODEL_ID "A stable id for the model under evaluation, e.g. MODEL_ID=my_world_model."
require RUN_ROOT   "Writable directory for evaluation output."
require GENERATION_ROOT "Directory containing generated model outputs."
require MANIFEST   "Benchmark manifest to evaluate."
require PLAN_ROOT  "Directory containing fixed HarnessEval skill plans."

PYTHON=${PYTHON:-python}
HARNESSEVAL_METRICS_PYTHON=${HARNESSEVAL_METRICS_PYTHON:-$PYTHON}
PAVRM_PYTHON=${PAVRM_PYTHON:-$PYTHON}
HARNESSEVAL_WEIGHTS_ROOT=${HARNESSEVAL_WEIGHTS_ROOT:-$PROJECT_ROOT/weights}
API_KEY_FILE=${API_KEY_FILE:-$PROJECT_ROOT/secrets/api_key.txt}
LIGHTWEIGHT=0
for arg in "$@"; do
  case "$arg" in
    --prepare-only|--status) LIGHTWEIGHT=1 ;;
  esac
done

if [[ "$LIGHTWEIGHT" == 0 ]]; then
  require HARNESSEVAL_METRICS_PYTHON "Interpreter for the metric environment."
  require PAVRM_PYTHON  "Interpreter for the PAVRM / visual-plausibility environment."
  require HARNESSEVAL_WEIGHTS_ROOT "Root of the downloaded metric weights."
  require API_KEY_FILE  "File containing the VLM API key used by the four judge skills."
fi
HARNESSEVAL_ROOT=${HARNESSEVAL_ROOT:-$RUN_ROOT/harnesseval}
VLM_CONFIG=${VLM_CONFIG:-$PROJECT_ROOT/examples/vlm_backend_config.json}
GPUS=${GPUS:-0}

cd "$PROJECT_ROOT"
exec "$PYTHON" tools/run_model_eval_pool.py \
  --harnesseval-root "$HARNESSEVAL_ROOT" \
  --manifest "$MANIFEST" \
  --generation-root "$GENERATION_ROOT" \
  --model-id "$MODEL_ID" \
  --gpus "$GPUS" \
  --api-key-file "$API_KEY_FILE" \
  --metrics-python "$HARNESSEVAL_METRICS_PYTHON" \
  --pavrm-python "$PAVRM_PYTHON" \
  --weights-root "$HARNESSEVAL_WEIGHTS_ROOT" \
  --vlm-config "$VLM_CONFIG" \
  --plan-root "$PLAN_ROOT" \
  "$@"
