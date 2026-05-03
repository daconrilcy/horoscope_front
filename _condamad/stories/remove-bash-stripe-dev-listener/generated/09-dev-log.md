# Dev Log

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Source story: `_condamad/stories/remove-bash-stripe-dev-listener/00-story.md`
- `AGENTS.md`: read at repository root.
- Regression guardrails: read; applicable `RG-023`, `RG-024`.
- Initial `git status --short`: command emitted permission warnings for artifact cache folders; no dirty file lines were returned.

## Baseline

- Baseline scan captured before implementation in `reference-baseline.txt`.
- Initial active hits were the Bash script, ownership row, runbook Git Bash/WSL text, and tests that expected the Bash listener.

## Implementation

- Deleted `scripts/stripe-listen-webhook.sh`.
- Removed the Bash listener row and `blocked-support-decision` meaning from `scripts/ownership-index.md`.
- Updated the local Stripe runbook to state dev-only Windows / PowerShell support.
- Updated tests to guard PowerShell-only listener behavior and Bash absence.

## Validation

- Targeted pytest: PASS, 14 tests passed.
- Ruff format check and lint: PASS.
- Story validate/lint: PASS.
- Full backend `pytest -q`: timed out after 604 seconds; targeted guards passed.
- Active forbidden scan after implementation: no hits.
