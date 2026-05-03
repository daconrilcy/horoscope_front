# Removal Audit - Bash Stripe Listener

## Decision context

The user decision for this story rejects Git Bash / WSL support for the local Stripe CLI listener. The canonical development environment is Windows / PowerShell, and `scripts/stripe-listen-webhook.ps1` is the only supported local listener.

## Classification table

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `scripts/stripe-listen-webhook.sh` | root script | historical-facade | Baseline found ownership row, runbook Bash example, and tests preserving parity. No backend runtime consumer. | `scripts/stripe-listen-webhook.ps1` | delete | `reference-baseline.txt`; user decision in `00-story.md`; `reference-after.txt` proves no active hit and no file inventory hit. | Developers using Git Bash/WSL lose this non-canonical helper; accepted by user decision. |
| Git Bash / WSL runbook path | documentation support path | historical-facade | Baseline found active support text in `docs/billing-webhook-local-testing.md`. | Windows / PowerShell runbook command | replace-consumer | Updated runbook; `reference-after.txt` records no active docs/scripts/tests hit. | External users may need to run the PowerShell command instead. |

## Remaining hit policy

- Historical hits under `_condamad/audits/**` are allowed.
- This story's `reference-baseline.txt`, `00-story.md`, `removal-audit.md`, and generated evidence may mention the removed path as historical proof.
- Active hits under `scripts`, `docs`, or `backend/app/tests` are not allowed after implementation.
