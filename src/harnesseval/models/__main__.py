"""Execute a registered model against a HarnessEval generation request."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import get_model, list_models


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m harnesseval.models")
    parser.add_argument("--model", choices=list_models(), required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--workers", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = get_model(args.model).run_request(args.request, workers=args.workers)
    except Exception as exc:  # noqa: BLE001 - command reports setup failures as JSON
        print(json.dumps({"status": "failed", "error": repr(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
