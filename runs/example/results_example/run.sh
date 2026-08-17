#!/usr/bin/env bash
set -euo pipefail

TEST_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$TEST_ROOT/../.." && pwd)

export MODEL_ID=seedance-2.0-standard
export GENERATION_ROOT="$TEST_ROOT/generation"
export RUN_ROOT="$TEST_ROOT/run"
export MANIFEST="$TEST_ROOT/manifest.json"
export PLAN_ROOT="$PROJECT_ROOT/benchmark/plans"
export GPUS=${GPUS:-0}
export PYTHONDONTWRITEBYTECODE=1
export HARNESSEVAL_METRICS_PYTHON=${HARNESSEVAL_METRICS_PYTHON:-python}
export PAVRM_PYTHON=${PAVRM_PYTHON:-python}
export HARNESSEVAL_WEIGHTS_ROOT=${HARNESSEVAL_WEIGHTS_ROOT:-"$PROJECT_ROOT/cache/weights"}
export HARNESSEVAL_DEPENDENCIES_ROOT=${HARNESSEVAL_DEPENDENCIES_ROOT:-"$PROJECT_ROOT/cache/dependencies"}
export VLM_CONFIG=${VLM_CONFIG:-"$PROJECT_ROOT/examples/v2_vlm_backend_config.json"}
export PYTHONPATH="$HARNESSEVAL_DEPENDENCIES_ROOT/HPSv3${PYTHONPATH:+:$PYTHONPATH}"

exec "$PROJECT_ROOT/tools/run_model_eval_pool.sh" "$@"
