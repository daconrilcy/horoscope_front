# CONDAMAD Audit Report - scripts-ops

## Scope

- Domain target: `scripts/`
- Archetype: `legacy-surface-audit` with No Legacy / DRY / ownership dimensions.
- Mode: read-only for application code; only audit artifacts under `_condamad/audits/**` are created.
- Trigger: re-audit after implementation of stories derived from `_condamad/audits/scripts-ops/2026-05-02-1847`.
- Guardrails consulted: `_condamad/stories/regression-guardrails.md`, especially `RG-023` and `RG-024`.

## Executive Verdict

The scripts domain is materially cleaner than the previous audit. The one-off root validator was removed, every current root script is covered by `scripts/ownership-index.md`, local stack startup no longer requires Stripe by default, the LLM readiness cache is repo-relative, the load-test manifest separates destructive privacy scenarios, and the natal cross-tool tool is guarded as dev-only.

One decision remains open: `scripts/stripe-listen-webhook.sh` is still present and documented for Git Bash or WSL while the repository target development OS remains Windows / PowerShell. This is now explicitly recorded and guarded as `needs-user-decision`, so it is controlled debt rather than silent legacy.

## Findings

| ID | Severity | Summary | Status |
|---|---|---|
| F-001 | Medium | `scripts/stripe-listen-webhook.sh` remains an active Bash variant beside the canonical PowerShell listener. | needs-user-decision |
| F-002 | Info | Root script ownership is now explicit and guarded by registry coverage. | closed-from-prior-audit |
| F-003 | Info | The root route-removal validator is absent from active script/doc/backend/frontend surfaces. | closed-from-prior-audit |
| F-004 | Info | Local dev stack startup is documented and Stripe is opt-in via `-WithStripe`. | closed-from-prior-audit |
| F-005 | Info | LLM release readiness no longer contains the previous local absolute cache path. | closed-from-prior-audit |
| F-006 | Info | Critical load scenarios are grouped and destructive privacy load is excluded from defaults. | closed-from-prior-audit |
| F-007 | Info | `natal-cross-tool-report-dev.py` is guarded as dev-only and is the only runtime-adjacent golden fixture consumer. | closed-from-prior-audit |

## Current Script Classification

| Surface | Classification | Evidence |
|---|---|---|
| `scripts/ownership-index.md` | canonical governance registry | E-002, E-003, E-004 |
| `scripts/start-dev-stack.ps1` | supported dev entrypoint | E-004, E-008 |
| `scripts/llm-release-readiness.ps1` | supported LLM release ops | E-004, E-009 |
| `scripts/load-test-critical.ps1` | supported perf tool with grouped scenarios | E-004, E-010 |
| `scripts/natal-cross-tool-report-dev.py` | dev-only diagnostic tool | E-004, E-011 |
| `scripts/stripe-listen-webhook.ps1` | canonical local Stripe listener for Windows / PowerShell | E-004, E-012 |
| `scripts/stripe-listen-webhook.sh` | active Bash variant awaiting support decision | E-004, E-012 |

## Legacy / Obsolete Candidates

| Surface | Decision | Evidence | Blocker |
|---|---|---|---|
| `scripts/validate_route_removal_audit.py` | deleted / closed | E-006, E-007 | none for active repo surfaces |
| `scripts/stripe-listen-webhook.sh` | needs-user-decision | E-012 | Decide whether Git Bash / WSL support is intentionally supported in this Windows / PowerShell repository. |

## Recommended Order

1. Decide whether the Bash Stripe listener is part of the supported dev surface.
2. If yes, update `scripts/ownership-index.md` from `needs-user-decision` to supported cross-platform policy and keep dual-script parity tests.
3. If no, remove `scripts/stripe-listen-webhook.sh`, update docs/tests, and keep `scripts/stripe-listen-webhook.ps1` as the only supported listener.

## Validation Notes

- Application code was not changed.
- Targeted backend guard tests passed after activating `.venv`.
- Audit artifact validation passed after activating `.venv`.
