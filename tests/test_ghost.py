"""Tests for GHOST v0.1. Run: python -m pytest tests/ -q"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ghost.cli import main
from ghost.corpus import get_document
from ghost.evaluator import evaluate
from ghost.harness import MockAgent, ToolSandbox
from ghost.injections import get_injection, list_injections
from ghost.models import Trace, ToolCall
from ghost.permissions import is_violation
from ghost.runner import run_all, summarise


def test_catalog_has_six_injections():
    assert len(list_injections()) == 6


def test_vulnerable_follows_all():
    doc = get_document("DOC-01")
    for inj in list_injections():
        trace = MockAgent("vulnerable").run(doc, inj, "t")
        assert evaluate(trace, inj).verdict.value == "FOLLOWED", inj.id


def test_hardened_follows_none():
    doc = get_document("DOC-01")
    for inj in list_injections():
        trace = MockAgent("hardened").run(doc, inj, "t")
        assert evaluate(trace, inj).verdict.value in {"IGNORED", "REFUSED"}, inj.id


def test_baseline_has_no_violations():
    doc = get_document("DOC-01")
    for profile in ("vulnerable", "selective", "hardened"):
        trace = MockAgent(profile).run(doc, None, "t")
        result = evaluate(trace, None)
        assert result.injection_id == "BASELINE"
        assert result.verdict.value == "IGNORED"


def test_sandbox_blocks_path_traversal():
    sb = ToolSandbox()
    try:
        assert sb.write_file("../evil.txt", "x").allowed is False
        assert sb.write_file("/tmp/evil.txt", "x").allowed is False
        assert sb.read_file("secret-note.txt").allowed is True
    finally:
        sb.cleanup()


def test_sandbox_write_allowlist_separate_from_read():
    sb = ToolSandbox()
    try:
        assert sb.write_file("secret-note.txt", "x").allowed is False
        assert sb.write_file("hijacked.txt", "x" * 201).allowed is False
        assert sb.read_file("secret-note.txt").result == "[redacted: fake note]"
    finally:
        sb.cleanup()


def test_sandbox_blocks_arbitrary_commands():
    sb = ToolSandbox()
    try:
        assert sb.run_command("rm -rf /").allowed is False
        assert sb.run_command("echo GHOST-CANARY-INJ-03").allowed is True
    finally:
        sb.cleanup()


def test_exfil_is_mocked_only():
    doc = get_document("DOC-01")
    inj = get_injection("INJ-05")
    trace = MockAgent("vulnerable").run(doc, inj, "t")
    assert trace.canary_found is True
    assert evaluate(trace, inj).permission_violated.value == "network"


def test_partial_on_blocked_write():
    trace = Trace(scenario_id="t", injection_id="INJ-01", agent_profile="vulnerable",
                  tool_calls=[ToolCall("write_file", {"name": "hijacked.txt"}, allowed=False)],
                  canary_found=False)
    result = evaluate(trace, get_injection("INJ-01"))
    assert result.verdict.value == "PARTIAL"


def test_cli_out_traversal_blocked():
    import os
    os.chdir(Path(__file__).resolve().parents[1])
    assert main(["run", "--profile", "hardened", "--out", "../evil.md"]) == 2
    assert not Path(__file__).resolve().parents[1].parent.joinpath("evil.md").exists()


def test_cli_filters():
    results = run_all(profiles=("hardened",), injection_ids=("INJ-01",), doc_ids=("DOC-01",))
    assert len(results) == 2  # 1 baseline + 1 injected
    assert results[1].injection_id == "INJ-01"


def test_cli_fail_on_follow():
    assert main(["run", "--profile", "hardened", "--fail-on-follow"]) == 0
    assert main(["run", "--profile", "vulnerable", "--fail-on-follow"]) == 1


def test_run_all_matrix():
    results = run_all()
    # 4 docs x 6 injections x 3 profiles = 72 injected + 12 baselines
    assert len(results) == 84
    s = summarise(results)
    assert s["total"] == 72
    assert s["by_profile"]["vulnerable"]["followed"] == 24
    assert s["by_profile"]["selective"]["followed"] == 8
    assert s["by_profile"]["hardened"]["followed"] == 0
    assert s["baseline_violations"] == 0
    assert is_violation(evaluate(MockAgent("vulnerable").run(
        get_document("DOC-01"), get_injection("INJ-01"), "t"),
        get_injection("INJ-01")).permission_violated) is True
