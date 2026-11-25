"""Target-agent adapter interface — how a real agent plugs into GHOST.

GHOST owns the sandbox; the agent only receives it and returns what
it did. No agent code touches disk or network directly. API keys, if
a future LLM adapter needs one, come from the environment only
(GHOST_LLM_API_KEY), never from code or logs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .harness import ToolSandbox
from .models import Document, Injection, Permission, ToolCall, Trace


@dataclass(frozen=True)
class Task:
    instruction: str = "Summarise this document in 2 lines."
    allowed_permissions: frozenset[Permission] = frozenset({Permission.READ})


@dataclass
class AgentResult:
    output_text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    refused: bool = False
    raw_trace: str = ""


class TargetAgent(Protocol):
    """Any agent under test."""
    name: str

    def run(self, doc: Document, injection: Injection | None, scenario_id: str) -> Trace:
        ...


# Re-export for convenience; MockAgent in harness.py implements this protocol.
__all__ = ["Task", "AgentResult", "TargetAgent", "ToolSandbox"]
