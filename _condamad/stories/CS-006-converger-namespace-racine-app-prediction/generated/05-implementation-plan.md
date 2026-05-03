# Implementation Plan - CS-006

## Findings

- `backend/app/prediction` contains engine, services, infra-facing adapters, public projection and templates.
- `engine_orchestrator.py` is application orchestration and has active consumers in services, jobs and tests.
- `backend/app/services/prediction` already exists and is the canonical owner for daily prediction use cases.

## Selected batch

Move `engine_orchestrator.py` to `backend/app/services/prediction/engine_orchestrator.py`.

This batch is coherent because it changes the orchestration owner without forcing the whole pure engine migration. The moved module may still import pure engine internals from `app.prediction` until a later batch moves those internals.

## Changes

- Move `engine_orchestrator.py`.
- Replace imports from `app.prediction.engine_orchestrator` with `app.services.prediction.engine_orchestrator`.
- Add/update guardrails in `test_daily_prediction_guardrails.py`.
- Persist before/after inventory and mapping.

## Tests

- `pytest -q app/tests/unit/test_engine_orchestrator.py`
- `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`
- `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py`
- `ruff check app tests`

## Rollback

Revert the move and import rewiring for the orchestrator batch only; keep the generated capsule evidence if it documents a blocked state.
