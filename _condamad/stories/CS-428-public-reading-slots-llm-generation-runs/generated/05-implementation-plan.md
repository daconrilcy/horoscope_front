# Implementation Plan

## Initial repository findings

- Existing public natal interpretation persistence remains in `UserNatalInterpretationModel`; story scope forbids physical deletion or frontend cutover.
- CS-427 product dimensions exist in `backend/app/domain/theme_natal/product_contract.py`.
- `backend/tests/integration` is deselected without `--long`; integration evidence must use the repository's long-test flag.

## Implemented changes

- Added canonical SQLAlchemy models for `theme_natal_reading_slots` and `llm_generation_runs`.
- Added Alembic revision `20260601_0142` with slot/run tables, accepted-only lookup indexes and idempotence unique constraints.
- Added `ThemeNatalReadingSlotService` for slot claim, run idempotence, accepted publication, rejected-run recording, public accepted-only lookup/list, and quota-after-publication gating.
- Added integration and unit tests for schema, accepted-only reads, rejected payload stability, chart identity, client request idempotence and quota gating.

## Files modified

- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/models/theme_natal_reading_slot.py`
- `backend/app/infra/db/models/llm_generation_run.py`
- `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`
- `backend/migrations/versions/20260601_0142_create_theme_natal_reading_slots.py`
- `backend/tests/integration/test_theme_natal_reading_slots.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/**`
- `_condamad/stories/story-status.md`

## Files deleted

- Removed accidental preparation artifact `_condamad/stories/cs-428/` after verifying its resolved path stayed inside the workspace.

## Risk assessment

- No frontend, provider call, prompt, public API cutover, mass migration, or legacy deletion was introduced.
- Full backend pytest was not run; targeted story and guardrail suites passed.

## Rollback strategy

- Revert the new model/service/test files, remove the `20260601_0142` migration, and restore the CS-428 status row to `ready-to-dev`.
