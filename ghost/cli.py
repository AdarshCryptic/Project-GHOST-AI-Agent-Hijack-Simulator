"""CLI: python -m ghost run [--profile PROFILE] [--injection INJ-01] [--document DOC-01] [--format md|json] [--out FILE] [--fail-on-follow]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .corpus import DOCUMENTS
from .harness import PROFILES
from .injections import INJECTIONS
from .report import to_markdown
from .runner import run_all, summarise

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"


def _result_dict(r) -> dict:
    # Explicit allowlist — never dump __dict__ wholesale.
    return {
        "scenario_id": r.scenario_id,
        "injection_id": r.injection_id,
        "injection_type": r.injection_type,
        "agent_profile": r.agent_profile,
        "verdict": r.verdict.value,
        "permission_violated": r.permission_violated.value if r.permission_violated else None,
        "severity": r.severity,
        "canary_found": r.canary_found,
        "tool_calls": r.tool_calls,
        "notes": r.notes,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ghost", description="GHOST — AI agent hijack simulator (harmless, sandboxed)")
    p.add_argument("--version", action="version", version=f"ghost {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="run the injection matrix")
    run.add_argument("--profile", choices=list(PROFILES), default=None, help="run one profile only")
    run.add_argument("--injection", choices=[i.id for i in INJECTIONS], default=None, help="run one injection only")
    run.add_argument("--document", choices=[d.id for d in DOCUMENTS], default=None, help="run one document only")
    run.add_argument("--format", choices=["md", "json"], default="md", help="output format on stdout")
    run.add_argument("--out", default=None, help="report filename, written to reports/ only, e.g. run.md")
    run.add_argument("--no-baseline", action="store_true", help="skip baseline control runs")
    run.add_argument("--fail-on-follow", action="store_true", help="exit 1 if any injection was followed (CI gate)")
    sub.add_parser("list", help="list injections and profiles")
    args = p.parse_args(argv)

    if args.cmd == "list":
        for inj in INJECTIONS:
            print(f"{inj.id}  {inj.type.value:20} {inj.name}  [{inj.severity}] -> {inj.target_permission.value}")
        print("profiles:", ", ".join(PROFILES))
        print("documents:", ", ".join(d.id for d in DOCUMENTS))
        return 0

    profiles = (args.profile,) if args.profile else PROFILES
    try:
        results = run_all(
            profiles,
            include_baseline=not args.no_baseline,
            injection_ids=(args.injection,) if args.injection else None,
            doc_ids=(args.document,) if args.document else None,
        )
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    summary = summarise(results)
    if args.format == "json":
        print(json.dumps({"summary": summary, "results": [_result_dict(r) for r in results]}, indent=2))
    else:
        print(to_markdown(results))

    if args.out:
        if Path(args.out).is_absolute() or ".." in Path(args.out).parts or "/" in args.out:
            print("error: --out must be a plain filename like run.md", file=sys.stderr)
            return 2
        out = (REPORTS_DIR / args.out).resolve()
        if not out.is_relative_to(REPORTS_DIR.resolve()) or out.suffix not in {".md", ".json"}:
            print("error: --out must be a .md or .json file inside reports/", file=sys.stderr)
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.suffix == ".json":
            out.write_text(json.dumps({"summary": summary, "results": [_result_dict(r) for r in results]}, indent=2), encoding="utf-8")
        else:
            out.write_text(to_markdown(results), encoding="utf-8")
            json_path = out.with_suffix(".json")
            json_path.write_text(json.dumps({"summary": summary, "results": [_result_dict(r) for r in results]}, indent=2), encoding="utf-8")
            print(f"\nWrote {out} and {json_path}")
            print("\nSummary:", summary)
            return 1 if args.fail_on_follow and summary["followed"] else 0
        print(f"\nWrote {out}")
    print("\nSummary:", summary)
    return 1 if args.fail_on_follow and summary["followed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
