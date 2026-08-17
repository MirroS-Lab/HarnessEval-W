#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PYTHON=${HARNESSEVAL_METRICS_PYTHON:-python}
DEPENDENCIES_ROOT=${HARNESSEVAL_DEPENDENCIES_ROOT:-$PROJECT_ROOT/cache/dependencies}

sync_repo() {
  local url=$1 ref=$2 destination=$3 recursive=${4:-0}
  if [[ ! -d "$destination/.git" ]]; then
    mkdir -p "$(dirname "$destination")"
    git clone --filter=blob:none --no-checkout "$url" "$destination"
  fi
  git -C "$destination" fetch --depth 1 origin "$ref"
  git -C "$destination" checkout --detach FETCH_HEAD
  if [[ "$recursive" == 1 ]]; then
    git -C "$destination" submodule update --init --recursive --depth 1
  fi
}

command -v "$PYTHON" >/dev/null
command -v git >/dev/null
mkdir -p "$DEPENDENCIES_ROOT"

sync_repo https://github.com/princeton-vl/RAFT.git \
  2888e15a51fa41140771d3f498ed8023cff098d1 "$DEPENDENCIES_ROOT/RAFT"
sync_repo https://github.com/MCG-NKU/AMT.git \
  70f988fbfc0d3d458beba1ee49caf876e57968fe "$DEPENDENCIES_ROOT/AMT"
sync_repo https://github.com/MizzenAI/HPSv3.git \
  bd0c5fcb5f587617b0169c07222ab78d01e2f3c2 "$DEPENDENCIES_ROOT/HPSv3"
sync_repo https://github.com/mega-sam/mega-sam.git \
  a27b4e633c5cc0828a62ed943ef9f6505705fd3f "$DEPENDENCIES_ROOT/mega-sam" 1
sync_repo https://github.com/LiheYoung/Depth-Anything.git \
  1d03336771fe09c5398ffdd211441e33941a97dc "$DEPENDENCIES_ROOT/Depth-Anything"
sync_repo https://github.com/lpiccinelli-eth/UniDepth.git \
  8d8cfe4c7ee15297099983607febf0d4f32eb3d6 "$DEPENDENCIES_ROOT/UniDepth"
sync_repo https://github.com/facebookresearch/dinov2.git \
  7764ea0f912e53c92e82eb78a2a1631e92725fc8 "$DEPENDENCIES_ROOT/dinov2"

mkdir -p "$DEPENDENCIES_ROOT/mega-sam/torchhub"
ln -sfn "$DEPENDENCIES_ROOT/dinov2" \
  "$DEPENDENCIES_ROOT/mega-sam/torchhub/facebookresearch_dinov2_main"

"$PYTHON" -m pip install \
  "setuptools==80.9.0" \
  "torch==2.5.1" \
  "torchvision==0.20.1" \
  "transformers==4.51.3" \
  "numpy==1.26.4" \
  "opencv-python==4.11.0.86" \
  "av==17.1.0" \
  "pyiqa==0.1.15.post2" \
  "dreamsim==0.2.1" \
  "open-clip-torch==3.3.0" \
  "clip @ git+https://github.com/openai/CLIP.git@d05afc436d78f1c48dc0dbf8e5980a9d471f35f6" \
  "easydict==1.13" \
  "omegaconf==2.3.0" \
  "hydra-core==1.3.2" \
  "iopath==0.1.10" \
  "qwen-vl-utils==0.0.14" \
  "safetensors>=0.5" \
  "scipy>=1.11" \
  "ninja>=1.11"

"$PYTHON" -m pip install --no-deps -e "$DEPENDENCIES_ROOT/HPSv3"
"$PYTHON" -m pip install --no-build-isolation -e "$DEPENDENCIES_ROOT/mega-sam/base"

HARNESSEVAL_DEPENDENCIES_ROOT="$DEPENDENCIES_ROOT" "$PYTHON" - <<'PY'
from harnesseval.metrics.video_quality import get_dynamic_degree_metric
from harnesseval.metrics.video_quality import get_motion_smoothness_metric
from hpsv3.inference import HPSv3RewardInferencer

assert get_dynamic_degree_metric()
assert get_motion_smoothness_metric()
assert HPSv3RewardInferencer
print("HarnessEval metric dependencies installed")
PY
