# Implementation plan - CS-018

## Current findings

- `backend/app/prediction` is already absent.
- `backend/app/tests/unit/test_daily_prediction_guardrails.py` already contains
  final extinction checks:
  - `test_prediction_legacy_namespace_is_not_importable`
  - `test_prediction_legacy_namespace_has_no_files`
  - `test_prediction_legacy_import_paths_are_removed`
- No active import `app.prediction` was found under backend runtime or tests.
- The CS-012 allowlist remains only as a historical `_condamad` artifact.

## Selected approach

Keep the existing canonical guard in place and complete persistent evidence for
the story. Avoid touching runtime code because the repository already satisfies
the target invariant.

## Files to modify

- CONDAMAD generated evidence files for CS-018.
- `guard-before.md` and `guard-after.md`.
- `_condamad/stories/story-status.md` after validation.

## Tests and checks

- Targeted guard pytest.
- Service and API regression tests named by the story.
- Legacy folder and import scans.
- Ruff check and format check on the guard file.
- Diff review.

## No Legacy stance

No compatibility path is permitted. The only accepted `app.prediction` references
are historical `_condamad` evidence references.

## Rollback strategy

Revert only this story's generated evidence/status files. No runtime rollback is
expected because no runtime code change is planned.
