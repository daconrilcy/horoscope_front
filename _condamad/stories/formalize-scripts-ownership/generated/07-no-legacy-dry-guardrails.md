# No Legacy / DRY Guardrails

## Canonical destination

- The single script ownership registry is `scripts/ownership-index.md`.
- The executable guard is `backend/app/tests/unit/test_scripts_ownership.py`.

## Forbidden patterns

- A second script ownership registry under `_condamad/` or `docs/`.
- Wildcard registry rows that cover multiple scripts.
- Duplicate rows for the same script path.
- Script relocation, wrapper, alias, shim, fallback, or re-export.
- Marking `stripe-listen-webhook.sh` as supported without an explicit user
  decision.

## Required negative evidence

- `pytest -q app/tests/unit/test_scripts_ownership.py` must fail if:
  - a script exists without a row;
  - a row points to a missing script;
  - a script has duplicate rows;
  - required columns drift;
  - the before/after snapshots diverge.
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts backend/app/tests/unit/test_scripts_ownership.py`
  must not reveal active compatibility behavior introduced by this story.

## Allowed historical references

- Audit files may mention the historical flat namespace or legacy findings.
- The route-removal guard may keep its split forbidden script name in the test.

## Review checklist

- One row per `rg --files scripts` path.
- One registry only.
- No script movement.
- `stripe-listen-webhook.sh` still has `needs-user-decision`.
- Final evidence classifies any legacy wording hits.
