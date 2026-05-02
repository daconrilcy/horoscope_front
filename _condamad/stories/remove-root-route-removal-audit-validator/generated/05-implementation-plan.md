# Implementation Plan

## Findings

- `scripts/validate_route_removal_audit.py` is a one-off validator introduced by the historical facade route removal story.
- The baseline scan shows no backend runtime, frontend, public docs, generated contract, or CI consumer.
- Remaining references are historical CONDAMAD/audit evidence plus the current removal story.

## Planned changes

- Persist `reference-baseline.txt` and `removal-audit.md`.
- Delete `scripts/validate_route_removal_audit.py`.
- Update the historical story capsule so it no longer advertises the removed root command as executable.
- Add `backend/app/tests/unit/test_scripts_ownership.py` to fail on reintroduction.
- Register that scripts test in `ops-quality-test-ownership.md` to satisfy RG-015.
- Persist `reference-after.txt` after edits and complete final evidence.

## No Legacy stance

- No wrapper, alias, fallback, relocation, or replacement command is allowed.
- The old root script path must be absent from active scripts, backend, frontend, and docs.

## Rollback

- Restore the deleted script and historical references only if validation proves an active external or first-party consumer that requires the root command.
