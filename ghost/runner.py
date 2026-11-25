"""Runner: full matrix (documents x injections x profiles) + baselines.
No I/O except the caller's report step.
"""
from __future__ import annotations

from .corpus import DOCUMENTS
from .evaluator import evaluate
from .harness import PROFILES, MockAgent
from .injections import INJECTIONS
from .models import Result


def run_all(profiles: tuple[str, ...] = PROFILES,
            include_baseline: bool = True,
            injection_ids: tuple[str, ...] | None = None,
            doc_ids: tuple[str, ...] | None = None) -> list[Result]:
    docs = [d for d in DOCUMENTS if doc_ids is None or d.id in doc_ids]
    injections = [i for i in INJECTIONS if injection_ids is None or i.id in injection_ids]
    if doc_ids and not docs:
        raise ValueError(f"unknown document(s): {sorted(set(doc_ids) - {d.id for d in DOCUMENTS})}")
    if injection_ids and not injections:
        raise ValueError(f"unknown injection(s): {sorted(set(injection_ids) - {i.id for i in INJECTIONS})}")
    results: list[Result] = []
    for doc in docs:
        for profile in profiles:
            if include_baseline:
                agent = MockAgent(profile)
                trace = agent.run(doc, None, f"{doc.id}:BASELINE:{profile}")
                results.append(evaluate(trace, None))
            for injection in injections:
                agent = MockAgent(profile)
                trace = agent.run(doc, injection, f"{doc.id}:{injection.id}:{profile}")
                results.append(evaluate(trace, injection))
    return results


def summarise(results: list[Result]) -> dict:
    injected = [r for r in results if r.injection_id != "BASELINE"]
    baselines = [r for r in results if r.injection_id == "BASELINE"]
    total = len(injected)
    followed = sum(1 for r in injected if r.verdict.value == "FOLLOWED")
    by_profile: dict[str, dict[str, int]] = {}
    for r in injected:
        by_profile.setdefault(r.agent_profile, {"total": 0, "followed": 0})
        by_profile[r.agent_profile]["total"] += 1
        if r.verdict.value == "FOLLOWED":
            by_profile[r.agent_profile]["followed"] += 1
    return {
        "total": total,
        "followed": followed,
        "follow_rate": round(followed / total, 3) if total else 0,
        "baselines": len(baselines),
        "baseline_violations": sum(1 for r in baselines if r.verdict.value != "IGNORED"),
        "by_profile": by_profile,
    }
