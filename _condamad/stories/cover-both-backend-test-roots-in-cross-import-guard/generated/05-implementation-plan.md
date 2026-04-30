# Implementation Plan

## Findings

- Current `BACKEND_ROOT = Path(__file__).resolve().parents[2]` resolves to `backend/app`.
- Current `TEST_ROOTS` therefore resolves to `backend/app/app/tests` and `backend/app/tests`; `backend/tests` is missed.
- The AST import guard is otherwise the right canonical owner.

## Planned changes

- Change `BACKEND_ROOT` to `parents[3]`.
- Add one assertion that the backend root contains `pyproject.toml`.
- Add one assertion that `TEST_ROOTS` maps to `app/tests` and `tests` and both exist.
- Keep the existing AST import scan.
- Persist before/after evidence artifacts.

## Files to modify

- `backend/app/tests/unit/test_backend_test_helper_imports.py`
- Story evidence files under `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/`

## No Legacy stance

- No allowlist.
- No duplicate guard.
- No compatibility path.

## Rollback

- Revert only this story's changes if the guard cannot pass; do not touch unrelated user changes.
