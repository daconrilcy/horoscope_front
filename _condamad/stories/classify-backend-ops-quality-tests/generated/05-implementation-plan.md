# Implementation Plan

## Findings

- The story directory exists but generated capsule files were absent before implementation.
- `backend/pyproject.toml` already collects all concerned tests through the standard backend pytest roots.
- The safest ownership decision is to keep the standard backend suite unchanged and persist owner/command metadata for quality and ops groups.

## Planned Changes

- Persist before and after inventories for the concerned files.
- Create one Markdown ownership registry with exact file rows, owners, commands, OS/subprocess dependencies, and collection decision.
- Add a backend unit guard that parses the registry and compares it to the filesystem inventory.
- Add `RG-015` because the registry/guard creates a durable invariant.
- Complete traceability and final evidence.

## Tests

- `pytest -q app/tests/unit/test_backend_quality_test_ownership.py`
- `pytest --collect-only -q --ignore=.tmp-pytest`
- targeted integration checks listed in the story
- Ruff format/check

## No Legacy Stance

- No marker, hidden suite, compatibility wrapper, fallback, or duplicate registry.
- Backend standard pytest scope remains unchanged, so no user approval is needed.

## Rollback

- Remove the new registry/evidence files, the new guard test, and the `RG-015` row.
