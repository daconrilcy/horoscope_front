# Execution Brief

## Story

- Story key: `harden-local-dev-stack-script`
- Source: `_condamad/stories/harden-local-dev-stack-script/00-story.md`
- Objective: make `scripts/start-dev-stack.ps1` start backend and frontend without Stripe by default, while keeping Stripe available through an explicit `-WithStripe` switch.

## Boundaries

- Modify only the local dev stack script, focused tests/ownership metadata, documentation, and CONDAMAD evidence.
- Do not change backend/frontend ports.
- Do not modify `scripts/stripe-listen-webhook.ps1` or `scripts/stripe-listen-webhook.sh`.
- Do not add dependencies.

## Preflight

- Read root `AGENTS.md`.
- Read `_condamad/stories/regression-guardrails.md` and apply `RG-015` and `RG-023`.
- Inspect `scripts/start-dev-stack.ps1`, `scripts/stripe-listen-webhook.ps1`, script ownership, docs, and existing script tests before editing.

## Write Rules

- Keep PowerShell behavior explicit: no silent fallback when `-WithStripe` is requested.
- Reuse `scripts/stripe-listen-webhook.ps1`; do not inline listener behavior.
- Add deterministic pytest guards for default/no-Stripe behavior and explicit Stripe behavior.
- Add French top-level comments/docstrings for new or significantly modified Python files.

## Done Conditions

- All ACs in `00-story.md` have implementation and validation evidence.
- Targeted pytest guards pass from `backend` after venv activation.
- Story validation/lint commands pass after venv activation.
- Final evidence and traceability files are complete.

## Halt Conditions

- Required files are inaccessible.
- Validation cannot run because the venv or dependencies cannot be made available safely.
- The implementation would require changing Stripe listener scripts or adding dependencies.
