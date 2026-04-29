# Implementation Plan

## Initial repository findings

- Baseline scan found 44 files matching `test_story_*.py`.
- The story capsule was missing generated files; it was generated before code changes.
- The first coherent migration lot was the three `backend/app/tests/unit` services structure guards; the user then asked to finish the catalogue while context was fresh.
- Existing guardrail registry RG-001 to RG-011 is present; this story creates a durable catalogue invariant.

## Proposed changes

- Persist before and after inventories.
- Persist a complete mapping for every baseline story-numbered file.
- Rename all 44 baseline story-numbered files to durable backend guard names.
- Rename remaining `def test_story_*` functions to invariant-based names.
- Add `test_backend_story_guard_names.py` to block any backend `test_story_*.py` reintroduction.
- Add RG-012 to the shared regression guardrail registry.

## Files to modify

- `_condamad/stories/reclassify-story-regression-guards/story-test-inventory-before.md`
- `_condamad/stories/reclassify-story-regression-guards/story-test-inventory-after.md`
- `_condamad/stories/reclassify-story-regression-guards/story-guard-mapping.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/unit/test_backend_story_guard_names.py`
- 44 renamed backend test files listed in `story-guard-mapping.md`.

## Files to delete

- None by content deletion. All `test_story_*.py` files are renamed as migration batches.

## Tests to add or update

- Add `backend/app/tests/unit/test_backend_story_guard_names.py`.
- Update the entitlement structure guard self-exclusion to use `Path(__file__).name`.
- Update one doc-conformity self-reference and several story-numbered function names.

## Risk assessment

- Main risk: broad rename breaks collection. Mitigation: targeted tests, collect-only, and full suite.
- Main regression risk: assertion drift during rename. Mitigation: no assertion changes beyond filename self-reference and targeted tests run.

## Rollback strategy

- Rename migrated files back to their original names and relax the zero-story guard only if validation exposes an unexpected collection issue.
