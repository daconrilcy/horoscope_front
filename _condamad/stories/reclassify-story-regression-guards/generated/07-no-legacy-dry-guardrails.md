# No Legacy / DRY Guardrails

## Forbidden unless explicitly approved

- New backend test files named `test_story_*.py`.
- Removing a story-numbered guard that protects an active surface without replacement evidence.
- Duplicating a guard assertion in both an old story-numbered file and a durable target file.
- Adding compatibility wrappers, transitional aliases, re-export modules, or silent fallbacks.

## Canonical destinations

- Durable mapping owner: `_condamad/stories/reclassify-story-regression-guards/story-guard-mapping.md`.
- Reintroduction guard: `backend/app/tests/unit/test_backend_story_guard_names.py`.
- Migrated catalogue:
  - `backend/app/tests/unit/test_backend_services_llm_structure_guard.py`
  - `backend/app/tests/unit/test_backend_entitlement_structure_guard.py`
  - `backend/app/tests/unit/test_backend_services_structure_guard.py`
  - All other durable targets listed in `story-guard-mapping.md`.

## Required negative evidence

- `rg --files backend -g 'test_story_*.py'` must return zero backend files.
- `rg -n "^\s*(async\s+)?def test_story_" backend -g 'test_*.py'` must return zero backend test functions.
- `pytest -q app/tests/unit/test_backend_story_guard_names.py` must fail if an unmapped story-numbered file appears.
- Migrated old filenames must be absent from the backend tree.

## Exceptions

- Historical story-numbered names may appear only in `_condamad` mapping/evidence as source references.

## Review checklist

- Every baseline file is listed in the mapping.
- Every row is `migrated`.
- Every `migrated` row points to an existing canonical target.
- The first batch did not alter assertions beyond the renamed file self-reference.
