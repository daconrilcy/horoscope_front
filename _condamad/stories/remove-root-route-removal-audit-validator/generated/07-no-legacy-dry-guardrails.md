# No Legacy / DRY Guardrails

## Forbidden unless explicitly required by the story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior

## Required when relevant

- One canonical path per responsibility
- Negative search evidence for removed symbols or imports
- Tests or architecture guards that fail if a legacy path is reintroduced
- Explicit errors instead of silent fallback for missing canonical configuration

## Story-specific forbidden paths

- `scripts/validate_route_removal_audit.py`
- Any replacement wrapper, alias, fallback, or re-export that keeps the root command executable.

## Canonical evidence after removal

- Historical proof remains in `_condamad/stories/remove-historical-facade-routes/generated/10-final-evidence.md`.
- The current removal decision is persisted in `_condamad/stories/remove-root-route-removal-audit-validator/removal-audit.md`.
- The durable guard is `backend/app/tests/unit/test_scripts_ownership.py`.

## Required negative evidence

- `rg -n "validate_route_removal_audit.py" scripts backend frontend docs`
- `rg -n "validate_route_removal_audit.py" _condamad/stories/remove-historical-facade-routes`
- `pytest -q app/tests/unit/test_scripts_ownership.py`

## Reviewer questions

- Did we delete the legacy path or only move the problem?
- Did we preserve an old path “temporarily”?
- Did any test import the old namespace?
- Did any doc, registry, or config still reference the old path?
