# GHOST

**Generative Hijack Observation & Safety Testing**

A Python red-team engine that injects controlled, harmless adversarial instructions into test documents, measures whether an agent follows them, and maps the resulting permission violations.

> Safe by design: every payload's only effect is a canary marker (`GHOST-CANARY-…`). No network, no subprocess, no real secrets, no real exfiltration. All tools run in a temporary sandbox.

## Quick start

```bash
python -m ghost run
python -m ghost list
python -m ghost run --profile hardened
python -m ghost run --injection INJ-05 --document DOC-01 --format json
python -m ghost run --profile hardened --fail-on-follow   # exit 1 if any injection is followed
python -m ghost run --out run.md
```

## First run

84 scenarios — 4 documents × 6 injections × 3 agent profiles, plus 12 baseline controls:

| Profile | Followed |
|---|---|
| vulnerable | 24 / 24 |
| selective | 8 / 24 |
| hardened | 0 / 24 |

Baselines: 0 violations — a clean run with no injection does not trigger a privileged tool call.

## Injections

| ID | Type | Permission | Severity |
|---|---|---|---|
| INJ-01 | Direct override | write | high |
| INJ-02 | Indirect embedded | write | medium |
| INJ-03 | Fake authority / roleplay | exec | high |
| INJ-04 | Tool lure | write | medium |
| INJ-05 | Data exfiltration lure | network | critical |
| INJ-06 | Chained read → write | escalation | critical |

## Pipeline

`docs/PIPELINE.md` — corpus → injection → harness → evaluator → permission map → report.

## Design

`docs/DESIGN.md` — Ghost Terminal theme: `#0B0F0E`, `#00E5A0`, `#FF3B5C`. Space Grotesk / Inter / JetBrains Mono.

## Tests

```bash
python -m pytest tests/ -q
```
