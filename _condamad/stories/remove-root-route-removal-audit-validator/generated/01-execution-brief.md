# Execution Brief — remove-root-route-removal-audit-validator

## Primary objective

Remove the one-off root script `scripts/validate_route_removal_audit.py` only after classifying it as `dead`, update historical CONDAMAD references that advertised the removed root command, and add a deterministic guard that fails if the root script returns.

## Boundaries

- Scope is limited to root script inventory, historical CONDAMAD references, capsule evidence, and the script ownership guard.
- No backend or frontend runtime behavior may change.
- Do not relocate the validator or preserve it through a wrapper, alias, fallback, or re-export.
- Do not decide anything about `scripts/stripe-listen-webhook.sh`.

## Execution rules

- Read `../00-story.md` completely before editing code.
- Read all required generated capsule files before implementation.
- Run `git status --short` before and after code changes.
- Preserve unrelated user changes.
- Implement only the current story.
- Do not introduce compatibility wrappers, aliases, silent fallbacks, duplicate active paths, or legacy import routes unless explicitly required by the story.
- Record implementation and validation evidence in `10-final-evidence.md`.
- Keep `RG-001` and `RG-015` evidence explicit.

## Halt conditions

- Stop if a production, backend test, frontend, docs, generated contract, CI, or public runbook consumer requires the root command.
- Stop if deletion would require a replacement command or new dependency.

## Done when

- Every AC in `03-acceptance-traceability.md` has code evidence and validation evidence.
- Commands in `06-validation-plan.md` have been run or explicitly documented as not run with reason and risk.
- `10-final-evidence.md` is complete.
