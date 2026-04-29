# Implementation Plan

## Current finding

The story capsule initially contained only `00-story.md`. Audit evidence reports 64 backend test files outside the configured `testpaths`, and `backend/pyproject.toml` references missing `app/ai_engine/tests`.

## Selected approach

Update `backend/pyproject.toml` so the standard pytest command covers the retained backend test roots directly, then add a pytest guard that loads the configured `testpaths`, checks they exist, invokes pytest collect-only, and compares collected test files with the static backend test-file inventory. The embedded `app/domain/llm/prompting/tests/test_qualified_context.py` file is treated as an exact opt-in exception because collecting its package imports an obsolete `tests/__init__.py` that requires a missing local data file.

## Files to modify

- `backend/pyproject.toml`
- `backend/app/tests/unit/test_backend_pytest_collection.py`
- `_condamad/stories/collect-retained-backend-tests/generated/*.md`
- Story evidence snapshots under `_condamad/stories/collect-retained-backend-tests/`

## Tests to add or update

- Add `backend/app/tests/unit/test_backend_pytest_collection.py`.

## Deletion candidates

None. Remove only the nonexistent `testpaths` entry from configuration.

## No Legacy stance

No alternate pytest configuration, compatibility collection script, or silent opt-in list will be introduced. Exceptions must be explicit in `uncollected-tests-after.md`; the only current exception is `app/domain/llm/prompting/tests/test_qualified_context.py`.

## Rollback strategy

Revert the `testpaths` edit and remove the new guard/evidence files if the story is abandoned. Do not touch unrelated `_condamad` story directories.
