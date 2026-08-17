"""Command line entry points used by HarnessEval."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from .io import atomic_write_json, read_json, value_digest
from .paths import PROJECT_ROOT
from .protocols import FAMILIES, SKILLS
from .report import build_report, load_scores, write_report_artifacts
from .validation import validate_reference_vectors, validate_run


def emit(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def command_plan(args: argparse.Namespace) -> int:
    from .pipeline.planner import (
        PlannerConfig,
        execute_plan_tasks,
        load_cases,
        plan_tasks,
        task_summary,
        write_plan_audit,
    )

    manifests = args.manifests or [PROJECT_ROOT / "benchmark/manifest_selected_330.clean.json"]
    output_root = args.output_root.resolve()
    model = args.model or os.getenv("OPENAI_MODEL") or ""
    base_url = args.base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not args.dry_run and not model:
        emit({"error": "harnesseval plan requires --model or OPENAI_MODEL"})
        return 2

    cases = load_cases(manifests)
    if args.case_ids:
        requested = set(args.case_ids)
        cases = [case for case in cases if str(case["case_id"]) in requested]
    if args.limit:
        cases = cases[: args.limit]

    config = PlannerConfig(
        output_root,
        model=model or "<unset>",
        base_url=base_url,
        api_key=api_key,
        wire_api=args.wire_api,
        timeout=args.timeout,
        retries=args.retries,
        assets_root=args.assets_root,
    )
    tasks = plan_tasks(
        cases,
        config,
        refresh=args.refresh,
    )
    plan = task_summary(tasks, details=args.details)
    if args.dry_run:
        emit({"plan": plan, "execute_required": True})
        return 0

    execution = execute_plan_tasks(tasks, config, workers=args.workers)
    audit_path = write_plan_audit(output_root, plan, execution)
    emit({"plan": plan, "execution": execution, "audit": str(audit_path)})
    return 1 if execution["failed"] or execution["stale_not_refreshed"] else 0


def command_inventory(args: argparse.Namespace) -> int:
    from .pipeline.inventory import build_inventory, write_inventory

    rows, audit = build_inventory(
        args.manifests,
        args.generation_root,
        args.models,
        assets_root=args.assets_root,
        workers=args.workers,
        full_decode=args.full_decode,
    )
    payload: dict[str, Any] = {"audit": audit, "execute_required": not args.execute}
    if args.execute:
        payload["artifacts"] = write_inventory(args.output_root, rows, audit)
        payload["execute_required"] = False
    emit(payload)
    return 0 if audit["status"] == "passed" else 1


def command_run_skills(args: argparse.Namespace) -> int:
    from .pipeline.backends import build_backends
    from .pipeline.runner import (
        execute_skill_tasks,
        plan_skill_tasks,
        prepare_drift_stage_tasks,
        task_summary,
    )

    cache_root = args.cache_root.resolve()
    tasks = plan_skill_tasks(
        args.inventory_root,
        args.manifests,
        args.plan_root,
        cache_root,
        skill_ids=set(args.skills or ()),
        model_ids=set(args.models or ()),
        case_ids=set(args.case_ids or ()),
        limit=args.limit,
        shard_count=args.shard_count,
        shard_index=args.shard_index,
    )
    shard = {
        "count": args.shard_count,
        "index": args.shard_index,
        "key": "round_robin(skill_id, probe_family, sorted case_id)",
    }
    plan = {**task_summary(tasks, details=args.details), "shard": shard}
    if not args.execute:
        emit({"plan": plan, "execute_required": True})
        return 0
    if not tasks:
        raise ValueError("no HarnessEval skill tasks matched the requested filters")
    if args.backend_config is None:
        raise ValueError("--execute requires --backend-config")

    config_path = args.backend_config.resolve(strict=True)
    run_context = {
        "shard": shard,
        "filters": {
            "skills": sorted(set(args.skills or ())),
            "models": sorted(set(args.models or ())),
            "case_ids": sorted(set(args.case_ids or ())),
            "limit": args.limit,
        },
        "backend_config": str(config_path),
        "drift_stage": args.drift_stage,
    }
    if args.audit_path:
        audit_path = args.audit_path.resolve()
    else:
        labels = run_context["filters"]["skills"]
        skill_label = labels[0] if len(labels) == 1 else "multi-skill"
        run_id = value_digest(run_context)[:12]
        audit_path = (
            cache_root
            / "run_audits"
            / skill_label
            / f"shard-{args.shard_index:03d}-of-{args.shard_count:03d}.{run_id}.json"
        )

    backends = build_backends(
        {task.skill_id for task in tasks},
        read_json(config_path),
        cache_root=cache_root,
        config_root=config_path.parent,
    )
    if args.drift_stage:
        drift = backends.get("drift_degradation_analyzer")
        if drift is None or not hasattr(drift, "prepare_stage"):
            raise ValueError("--drift-stage requires staged Drift backend mode")
        audit = prepare_drift_stage_tasks(
            tasks,
            drift,
            args.drift_stage,
            workers=args.workers,
            audit_path=audit_path,
            run_context=run_context,
        )
    else:
        audit = execute_skill_tasks(
            tasks,
            backends,
            cache_root,
            workers=args.workers,
            analyze_workers=args.analyze_workers,
            audit_path=audit_path,
            run_context=run_context,
        )
    emit({"plan": plan, "execution": {k: v for k, v in audit.items() if k != "outcomes"}})
    return 0 if audit["status"] == "passed" else 2


def command_score(args: argparse.Namespace) -> int:
    from .score import execute_score_tasks, plan_score_tasks, task_summary

    generation_root = args.generation_root.resolve()
    plan_root = args.plan_root.resolve()
    cache_root = args.cache_root.resolve()
    eval_root = args.eval_root.resolve()
    tasks = plan_score_tasks(
        generation_root,
        plan_root,
        cache_root,
        eval_root,
        models=set(args.models or ()),
        families=set(args.families or ()),
        limit=args.limit,
    )
    plan = task_summary(tasks, details=args.details)
    if args.plan_out:
        atomic_write_json(args.plan_out.resolve(), plan)
    if not args.execute:
        emit({"plan": plan, "execute_required": True})
        return 0

    execution = execute_score_tasks(
        tasks,
        eval_root,
        refresh_stale=args.refresh_stale,
    )
    scores = load_scores(eval_root)
    report = build_report(scores)
    atomic_write_json(eval_root / "summary.json", report)
    write_report_artifacts(eval_root, report)
    run_audit = {
        "schema_version": "harnesseval.score_run_audit",
        "plan": task_summary(tasks),
        "execution": {k: v for k, v in execution.items() if k != "written_paths"},
        "score_count": len(scores),
        "report_score_count": report["score_count"],
        "scoring_policy": report["scoring_policy"],
        "runtime_inputs": {
            "generation_root": str(generation_root),
            "plan_root": str(plan_root),
            "cache_root": str(cache_root),
        },
    }
    atomic_write_json(eval_root / "RUN_AUDIT.json", run_audit)
    emit({"plan": task_summary(tasks), "execution": execution, "report": report})
    return 1 if execution["stale_not_refreshed"] else 0


def command_eval(args: argparse.Namespace) -> int:
    if args.eval_command is None:
        command = [str(PROJECT_ROOT / "tools/run_model_eval_pool.sh")]
        if args.prepare_only:
            command.append("--prepare-only")
        if args.status:
            command.append("--status")
        environment = os.environ.copy()
        values = {
            "GENERATION_ROOT": args.results,
            "MODEL_ID": args.model_id,
            "RUN_ROOT": args.run_root,
            "MANIFEST": args.manifest,
            "PLAN_ROOT": args.plan_root,
            "GPUS": args.gpus,
        }
        for name, value in values.items():
            if value is not None:
                environment[name] = str(value)
        environment.setdefault(
            "MANIFEST", str(PROJECT_ROOT / "benchmark/manifest_selected_330.json")
        )
        environment.setdefault("PLAN_ROOT", str(PROJECT_ROOT / "benchmark/plans"))
        if args.model_id:
            environment.setdefault("RUN_ROOT", str(PROJECT_ROOT / "runs" / args.model_id))
        return subprocess.run(command, check=False, env=environment).returncode
    if args.eval_command == "inventory":
        return command_inventory(args)
    if args.eval_command == "run-skills":
        return command_run_skills(args)
    if args.eval_command == "score":
        return command_score(args)
    raise AssertionError(args.eval_command)


def command_verify(args: argparse.Namespace) -> int:
    if args.verify_command == "spec":
        report = validate_reference_vectors(args.spec.resolve())
    elif args.verify_command == "run":
        report = validate_run(
            args.eval_root.resolve(),
            (path.resolve() for path in args.manifests),
            expected_models=args.models,
            json_roots=(path.resolve() for path in args.json_roots or ()),
        )
    else:
        raise AssertionError(args.verify_command)
    if args.output:
        atomic_write_json(args.output.resolve(), report)
    emit(report)
    return 0 if report.get("status") == "passed" else 1


def command_generate(args: argparse.Namespace) -> int:
    from .model_adapter import model_id_from_reference, run_model_adapter

    model_id = args.model_id or model_id_from_reference(args.model)
    output_root = args.output_root or PROJECT_ROOT / "runs" / model_id
    result = run_model_adapter(
        adapter_path=args.adapter,
        model=args.model,
        model_id=model_id,
        manifest=args.manifest,
        output_root=output_root,
        assets_root=args.assets_root,
        case_ids=set(args.case_ids or ()),
        limit=args.limit,
        workers=args.workers,
        full_decode=args.full_decode,
    )
    emit(result)
    return 0 if result["status"] == "passed" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="harnesseval")
    commands = parser.add_subparsers(dest="command", required=True)

    plan = commands.add_parser("plan")
    plan.add_argument(
        "--manifest",
        type=Path,
        action="append",
        dest="manifests",
    )
    plan.add_argument("--output-root", "--output", type=Path, required=True)
    plan.add_argument("--model")
    plan.add_argument("--base-url")
    plan.add_argument("--api-key")
    plan.add_argument(
        "--wire-api",
        choices=("responses", "chat", "chat_completions", "chat/completions"),
        default="responses",
    )
    plan.add_argument("--assets-root", type=Path, default=PROJECT_ROOT)
    plan.add_argument("--case-id", action="append", dest="case_ids")
    plan.add_argument("--limit", type=int, default=0)
    plan.add_argument("--workers", type=int, default=4)
    plan.add_argument("--timeout", type=float, default=120.0)
    plan.add_argument("--retries", type=int, default=2)
    plan.add_argument("--refresh", action="store_true")
    plan.add_argument("--details", action="store_true")
    plan.add_argument("--dry-run", action="store_true")

    generate = commands.add_parser("generate")
    generate.add_argument("--adapter", type=Path, required=True)
    generate.add_argument("--model", required=True)
    generate.add_argument("--model-id")
    generate.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "benchmark/manifest_selected_330.json",
    )
    generate.add_argument("--output-root", "--output", type=Path)
    generate.add_argument("--assets-root", type=Path, default=PROJECT_ROOT)
    generate.add_argument("--case-id", action="append", dest="case_ids")
    generate.add_argument("--limit", type=int, default=0)
    generate.add_argument("--workers", type=int, default=16)
    generate.add_argument("--full-decode", action="store_true")

    evaluation = commands.add_parser("eval")
    evaluation.add_argument("--results", "--generation-root", type=Path)
    evaluation.add_argument("--model-id")
    evaluation.add_argument("--run-root", type=Path)
    evaluation.add_argument("--manifest", type=Path)
    evaluation.add_argument("--plan-root", type=Path)
    evaluation.add_argument("--gpus")
    evaluation.add_argument("--prepare-only", action="store_true")
    evaluation.add_argument("--status", action="store_true")
    eval_commands = evaluation.add_subparsers(dest="eval_command")

    inventory = eval_commands.add_parser("inventory")
    inventory.add_argument("--manifest", type=Path, action="append", dest="manifests", required=True)
    inventory.add_argument("--generation-root", type=Path, required=True)
    inventory.add_argument("--assets-root", type=Path)
    inventory.add_argument("--model", action="append", dest="models", required=True)
    inventory.add_argument("--output-root", type=Path, required=True)
    inventory.add_argument("--workers", type=int, default=16)
    inventory.add_argument("--full-decode", action="store_true")
    inventory.add_argument("--execute", action="store_true")

    run_skills = eval_commands.add_parser("run-skills")
    run_skills.add_argument("--manifest", type=Path, action="append", dest="manifests", required=True)
    run_skills.add_argument("--inventory-root", type=Path, required=True)
    run_skills.add_argument("--plan-root", type=Path, required=True)
    run_skills.add_argument("--cache-root", type=Path, required=True)
    run_skills.add_argument("--backend-config", type=Path)
    run_skills.add_argument("--skill", action="append", dest="skills", choices=SKILLS)
    run_skills.add_argument("--model", action="append", dest="models")
    run_skills.add_argument("--case-id", action="append", dest="case_ids")
    run_skills.add_argument("--limit", type=int, default=0)
    run_skills.add_argument("--shard-count", type=int, default=1)
    run_skills.add_argument("--shard-index", type=int, default=0)
    run_skills.add_argument("--workers", type=int, default=16)
    run_skills.add_argument("--analyze-workers", type=int, default=16)
    run_skills.add_argument("--stage1-workers", type=int, dest="analyze_workers", help=argparse.SUPPRESS)
    run_skills.add_argument("--drift-stage", choices=("physical", "render", "motion", "clip"))
    run_skills.add_argument("--audit-path", type=Path)
    run_skills.add_argument("--details", action="store_true")
    run_skills.add_argument("--execute", action="store_true")

    score = eval_commands.add_parser("score")
    score.add_argument("--generation-root", type=Path, required=True)
    score.add_argument("--plan-root", type=Path, required=True)
    score.add_argument("--cache-root", type=Path, required=True)
    score.add_argument("--eval-root", type=Path, required=True)
    score.add_argument("--model", action="append", dest="models")
    score.add_argument("--family", action="append", dest="families", choices=FAMILIES)
    score.add_argument("--limit", type=int, default=0)
    score.add_argument("--plan-out", type=Path)
    score.add_argument("--details", action="store_true")
    score.add_argument("--refresh-stale", action="store_true")
    score.add_argument("--execute", action="store_true")

    verify = commands.add_parser("verify")
    verify_commands = verify.add_subparsers(dest="verify_command", required=True)
    reference = verify_commands.add_parser("spec")
    reference.add_argument("--spec", type=Path, default=PROJECT_ROOT / "docs/skills.md")
    reference.add_argument("--output", type=Path)
    run = verify_commands.add_parser("run")
    run.add_argument("--eval-root", type=Path, required=True)
    run.add_argument("--manifest", type=Path, action="append", dest="manifests", required=True)
    run.add_argument("--model", action="append", dest="models")
    run.add_argument("--json-root", type=Path, action="append", dest="json_roots")
    run.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "plan":
        return command_plan(args)
    if args.command == "generate":
        return command_generate(args)
    if args.command == "eval":
        return command_eval(args)
    if args.command == "verify":
        return command_verify(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
