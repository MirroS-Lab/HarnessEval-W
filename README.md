<p align="center">
  <img src="assets/mirros-logo.png" alt="HarnessEval logo" width="200">
</p>

<h1 align="center">HarnessEval-W</h1>
<p align="center">
  <b>Agentifying the Evaluation of
Visual Worlds</b>
</p>

<p align="center">
  <i>The era of harnessed benchmarking: evaluation defines the taste of evolution.</i>
</p>

<p align="center">
  <a href="https://arxiv.org/abs/2608.16859"><img alt="Paper" src="https://img.shields.io/badge/arXiv-Paper-b31b1b?logo=arxiv&logoColor=white"></a>
  <a href="https://mirros-lab.github.io/HarnessEval-W"><img alt="Project Page" src="https://img.shields.io/badge/Project-Page-5F38FF"></a>
  <a href="https://mirros.ai/blog/harnesseval"><img alt="Blog" src="https://img.shields.io/badge/MirroS-Blog-745AE8"></a>
  <a href="https://mirros-lab.github.io/HarnessEval-W#leaderboard"><img alt="Leaderboard" src="https://img.shields.io/badge/🏆-Leaderboard-C9A227"></a>
</p>


<!-- <p align="center">
  <a href="#overview">Overview</a> |
  <a href="#how-it-works">Method</a> |
  <a href="#installation">Installation</a> |
  <a href="#usage">Usage</a> |
  <a href="#extending-harnesseval">Contributing</a> |
  <a href="#citation">Citation</a>
</p> -->


<p align="center">
  <img src="assets/fig_teaser.png" alt="HarnessEval overview" width="100%">
</p>

## Overview

A benchmark should deliver more than a scalar score: what makes an evaluation trustworthy is the **reasoning that justifies the score**. This is especially critical for world models, where judging a rollout requires understanding whether physics, causality, and world state evolve correctly. Humans spot such violations naturally, yet no existing benchmark automates this capability: metrics are computed brute-force, leaving no reasoning chain that can be examined or verified.

**HarnessEval** is an agentified evaluation pipeline that brings the harness paradigm from the LLM ecosystem to world model benchmarking. Rather than applying a fixed rubric, HarnessEval interprets the context of each evaluation case, decomposes the evaluation question into measurable sub-questions, and spawns specialized sub-agents, each equipped with tailored context and diagnostic tools to reason over its own sub-question. The parent agent then validates the gathered evidence and aggregates it into the final verdict. Every evaluation becomes a **transparent evidence tree** whose complete reasoning chain justifies the result.

## News

- [2026/08/18] 📄 [Paper](https://arxiv.org/pdf/2608.16859) now available. 
- [2026/08/18] 🌐 [Homepage](https://mirros-lab.github.io/HarnessEval-W) with leaderboard-ready reports and benchmark resources is live. 
- [2026/08/18] 🚀 Released the full HarnessEval benchmark, evaluation code, fixed plans, and metric backends.

## How It Works

<p align="center">
  <img src="assets/fig_pipeline.png" alt="HarnessEval pipeline" width="100%">
</p>

1. **Case-specific skill routing.** Given a case (initial world, action, probe intent), the planner routes it to the skills that can legitimately evaluate it — and records an evidence-grounded reason for every skill it skips.
2. **Sub-agent reasoning.** Each skill decomposes its evaluation into measurable sub-questions, each answered by a dedicated sub-agent against rollout evidence.
3. **Validated aggregation.** The parent agent validates the collected evidence and aggregates it into the case score. The full trace — every question, answer, score, and supporting frame — is saved as an auditable case card.

Routing depends only on the case context, never on the model being evaluated, so every model faces the same questions on the same cases.

## Installation

Create three environments:

- `harnesseval-main`: launcher / CLI
- `harnesseval-metrics`: metric backends
- `harnesseval-pavrm`: physical-plausibility backend

```bash
git clone --branch main --single-branch https://github.com/mirros-lab/harnesseval-w.git
cd harnesseval-w
conda env create -f docs/installation/main.environment.yml
conda env create -f docs/installation/metrics.environment.yml
conda env create -f docs/installation/pavrm.environment.yml
conda activate harnesseval-main
```

Configure credentials and paths:

```bash
cp config/example.env harnesseval.env
set -a; . ./harnesseval.env; set +a
```

The bundled demo in `runs/example/results_example` can be evaluated immediately after setup.

## Usage

Evaluate a model's generated results:

```bash
# Evaluate generated videos and write run outputs.
harnesseval eval \
  --results runs/example/results_example/generation \
  --model-id seedance-2.0-standard \
  --run-root runs/example/results_example/run \
  --manifest runs/example/results_example/manifest.json \
  --plan-root benchmark/plans
```

Check a completed run:

```bash
# Verify that an existing run has all expected scores.
harnesseval verify run \
  --eval-root runs/example/results_example/run/harnesseval/models/seedance-2.0-standard/evaluation \
  --manifest runs/example/results_example/manifest.json \
  --model seedance-2.0-standard
```

Or use the bundled demo end to end:

```bash
# Run the bundled demo from the example directory.
cd runs/example/results_example
# Evaluate the demo outputs.
harnesseval eval --results generation --model-id seedance-2.0-standard --run-root run --manifest manifest.json --plan-root ../../benchmark/plans
# Verify the demo run.
harnesseval verify run --eval-root run/harnesseval/models/seedance-2.0-standard/evaluation --manifest manifest.json --model seedance-2.0-standard
```

## What You Get

The bundled example already produces scores. A completed evaluation writes:

```
runs/example/results_example/run/harnesseval/models/<model-id>/evaluation/
├── summary.json           # overall and per-family scores
├── leaderboard_latest.json
├── leaderboard_latest.csv
└── LEADERBOARD.md
```

Per-case artifacts and caches live under `run/harnesseval/metric_cache/` and `run/harnesseval/models/<model-id>/`.

## Extending HarnessEval

HarnessEval is a living benchmark, and contributions are welcome.

- **Submit a new case** with a new world, action, or probe family.
- **Submit a new skill** when a case needs a new kind of evaluation.

Keep submissions aligned with the existing benchmark format so they can plug into the bundled flow.

## TODO


- [ ] Hosted submission & evaluation service (submit videos, get scores)
- [ ] Full cases on HuggingFace
- [ ] Subset cases & weights on HuggingFace
- [x] Model generation example
- [x] Evaluation code & example release
- [x] ArXiv paper, homepage with interactive leaderboard, blog release


## Acknowledgments

This project builds upon the following excellent works:

- [VBench](https://github.com/Vchitect/VBench) — Video quality metrics
- [WBench](https://github.com/meituan-longcat/WBench) — World model benchmark
- [WorldScore](https://github.com/haoyi-duan/WorldScore) - World model benchmark
- [Cosmos](https://github.com/NVIDIA/cosmos) - Open source world model
- [Lingbot World](https://github.com/Robbyant/lingbot-world) - Open source world model
- [MiniMax H3](https://github.com/MiniMax-AI/MiniMax-H3) - Open source world model
- ... and many other excellent open-source projects

## Citation

If you find HarnessEval useful, please cite:

```bibtex
@article{mirros2026harnessevalw,
  title   = {HarnessEval-W: Agentifying the Evaluation of Visual Worlds},
  author  = {{MirroS Team}},
  journal = {arXiv preprint arXiv:2608.16859},
  year    = {2026}
}
```

## License
We release our code under the Apache 2.0 License.
