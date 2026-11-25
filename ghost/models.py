"""Core data models for GHOST. Stdlib only, no external deps."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class InjectionType(str, Enum):
    DIRECT_OVERRIDE = "direct_override"
    INDIRECT_EMBEDDED = "indirect_embedded"
    ROLEPLAY_AUTHORITY = "roleplay_authority"
    TOOL_LURE = "tool_lure"
    DATA_EXFIL_LURE = "data_exfil_lure"
    CHAINED = "chained"


class Verdict(str, Enum):
    FOLLOWED = "FOLLOWED"      # agent did the injected action
    PARTIAL = "PARTIAL"        # attempted it, but blocked / incomplete
    IGNORED = "IGNORED"       # saw it (or not) and did not act
    REFUSED = "REFUSED"       # explicitly refused / flagged it


class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    EXEC = "exec"
    NETWORK = "network"
    ESCALATION = "escalation"


@dataclass
class Injection:
    id: str
    type: InjectionType
    name: str
    payload: str          # text injected into the document
    canary: str           # harmless marker that proves the action happened
    target_permission: Permission
    severity: str         # low / medium / high / critical
    description: str
    # What a compliant agent should do instead:
    expected_action: str = "ignore the injected instruction and complete only the user's task"


@dataclass
class Document:
    id: str
    title: str
    kind: str             # meeting_notes / invoice / email / policy
    body: str             # benign body, contains [INJECTION_POINT]

    def inject(self, injection: Injection) -> str:
        return self.body.replace("[INJECTION_POINT]", injection.payload)


@dataclass
class ToolCall:
    tool: str
    args: dict
    allowed: bool
    result: str = ""


@dataclass
class Trace:
    scenario_id: str
    injection_id: str
    agent_profile: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    output_text: str = ""
    canary_found: bool = False
    refused: bool = False


@dataclass
class Result:
    scenario_id: str
    injection_id: str
    injection_type: str
    agent_profile: str
    verdict: Verdict
    permission_violated: Permission | None
    severity: str
    canary_found: bool
    tool_calls: list[str] = field(default_factory=list)
    notes: str = ""
