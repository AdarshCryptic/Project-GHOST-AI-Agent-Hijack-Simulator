"""Markdown report generator — pure text, no dependencies."""
from __future__ import annotations

from .models import Result
from .runner import summarise


def to_markdown(results: list[Result]) -> str:
    s = summarise(results)
    lines = [
        "# GHOST — Run Report",
        "",
        f"Total injected scenarios: **{s['total']}** | Followed: **{s['followed']}** "
        f"| Follow rate: **{s['follow_rate']:.1%}**",
        f"Baselines: **{s['baselines']}** | Baseline violations: **{s['baseline_violations']}**",
        "",
        "## By agent profile",
        "",
        "| Profile | Followed / Total |",
        "|---|---|",
    ]
    for profile, v in sorted(s["by_profile"].items()):
        lines.append(f"| {profile} | {v['followed']} / {v['total']} |")
    lines += ["", "## Results", "", "| Injection | Type | Profile | Verdict | Permission | Severity |", "|---|---|---|---|---|---|"]
    for r in results:
        if r.injection_id == "BASELINE":
            continue
        perm = r.permission_violated.value if r.permission_violated else "-"
        lines.append(f"| {r.injection_id} | {r.injection_type} | {r.agent_profile} | {r.verdict.value} | {perm} | {r.severity} |")
    lines += ["", "_All payloads are harmless canaries. No data left the sandbox._", ""]
    return "\n".join(lines)
