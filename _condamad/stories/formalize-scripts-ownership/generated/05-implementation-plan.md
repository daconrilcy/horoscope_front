# Implementation Plan

## Current finding

`rg --files scripts` lists 20 current root script files. The audit expected 21
historically, but `scripts/validate_route_removal_audit.py` is already absent
and guarded by `backend/app/tests/unit/test_scripts_ownership.py`.

## Selected approach

- Use the current filesystem inventory as source of truth.
- Add one Markdown registry at `scripts/ownership-index.md`.
- Extend the existing script guard test to parse the registry and compare it to
  `scripts/`.
- Keep the existing route-removal reintroduction test.
- Add a new regression guardrail row for script ownership.

## Files to modify

- `scripts/ownership-index.md`
- `backend/app/tests/unit/test_scripts_ownership.py`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/formalize-scripts-ownership/*`

## Tests to add or update

- Extend `test_scripts_ownership.py` with:
  - exact inventory coverage;
  - duplicate row rejection;
  - required column validation;
  - blocked decision for `stripe-listen-webhook.sh`;
  - before/after inventory equality.

## No Legacy stance

No wrapper, alias, alternate registry, script relocation, or compatibility path
is introduced. `stripe-listen-webhook.sh` remains present only with an explicit
`needs-user-decision` ownership decision.

## Rollback strategy

Revert the registry, test extension, snapshots, and generated evidence files.
No runtime script behavior is changed.
