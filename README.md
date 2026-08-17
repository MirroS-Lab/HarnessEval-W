# HarnessEval-W merged site

Merged release site for **HarnessEval-W: Skill-Orchestrated Benchmarking for Interactive World Models**.

HarnessEval-W is MirroS's next-generation evaluation benchmark built around reusable Skills
and focuses on interactive world models. HarnessEval-W remains the benchmark's executable case
and Skill-routing runtime.

- `/` serves the integrated project site, leaderboard, and pending-review submission form.
- `/leaderboard/` remains available as the copied legacy leaderboard page, but the public
  navigation now uses the integrated same-page sections.
- Pending submissions are stored under `leaderboard/submissions/pending/`.
- The merged server reads the 330-case / 16-model dataset from the local selector at
  `http://127.0.0.1:8770` by default. Override it with `HARNESSEVAL_DATA_SITE` when needed.

The full-bleed hero uses three disjoint six-image sets derived from real benchmark cases. The
initial set is rendered in HTML as a static fallback; later sets are decoded before staggered
crossfades and remain frozen for reduced-motion or data-saver users.

## Regenerate the dataset gallery

The gallery builder reads the source benchmark data from the repository root, copies deployable media into this directory, and verifies the 228-card snapshot.

```bash
node scripts/build-gallery-data.mjs
```

Expected distribution:

```text
semantic: 90
navigation: 55
physical: 59
persistence: 24
```

## Run locally

```bash
cd ../../worlddojo_refactored/runs/v2_selected_330_20260811/selector
SELECTOR_USE_CACHED_INDEX=1 ./start.sh

cd ../../../../demo_dqy/site_merged_leaderboard
python3 server.py --host 127.0.0.1 --port 8953
```

Open `http://127.0.0.1:8953/`.

The site has no application build step. `index.html`, `styles.css`, `script.js`, and `assets/` are the complete deployable package.
