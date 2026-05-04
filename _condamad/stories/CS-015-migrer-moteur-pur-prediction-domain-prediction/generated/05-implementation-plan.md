# Implementation Plan

## Current architecture finding

At preflight, `backend/app/prediction` is absent and `backend/app/domain/prediction` already exists in tracked code. `backend/app/services/prediction/engine_orchestrator.py` and related service modules import `app.domain.prediction`.

## Selected approach

Treat the code migration as already present in the working tree and complete the story by validating the invariant, preserving persistent evidence, and updating CONDAMAD tracking. Do not recreate legacy paths to simulate a move.

## Files to modify

- Generate and complete CS-015 capsule files under `generated/`.
- Add `domain-prediction-before.md` and `domain-prediction-after.md`.
- Update CS-015 task/status metadata in `00-story.md`.
- Update CS-015 row in `_condamad/stories/story-status.md`.

## Tests and checks

- `pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/unit/test_transit_signal_v3.py`
- `pytest -q tests/unit/prediction/test_public_astro_foundation.py`
- `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`
- Targeted `rg` scans for forbidden imports.
- `ruff check app/domain/prediction app/services/prediction app/tests/unit/test_daily_prediction_guardrails.py`

## No Legacy stance

No compatibility facade, alias, fallback, shim, or re-export under `app.prediction` is allowed. Existing guard tests already block package recreation and legacy imports.

## Rollback strategy

If a validation reveals an actual active legacy path, update the active consumer to the canonical `app.domain.prediction` path or stop if the change crosses CS-015 scope.
