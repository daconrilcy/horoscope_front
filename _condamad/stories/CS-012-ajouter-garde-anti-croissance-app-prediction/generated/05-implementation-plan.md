# Implementation Plan - CS-012

## Current findings

- `backend/app/tests/unit/test_daily_prediction_guardrails.py` already contains prediction
  regression guards and a hardcoded Python file inventory.
- Current targeted scan of `backend/app/prediction` returns zero active hits for API,
  FastAPI, SQLAlchemy, LLM narrator, `AIEngineAdapter`, and settings imports.
- CS-007 and CS-009 already removed the exceptions mentioned in the story source.

## Selected approach

- Move the prediction Python inventory source of truth into
  `prediction-namespace-allowlist.md`.
- Make `test_daily_prediction_guardrails.py` read that artefact.
- Add a focused AST guard for API/settings/LLM runtime forbidden dependencies.
- Add a test that active exception rows must have an exit condition.

## Files to modify

- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md`
- CONDAMAD generated evidence files for CS-012.
- `_condamad/stories/story-status.md` after validation.

## Tests to run

- `ruff check app/tests/unit/test_daily_prediction_guardrails.py`
- `pytest -q app/tests/unit/test_daily_prediction_guardrails.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py`
- Story scans listed in `06-validation-plan.md`.

## No Legacy stance

- No compatibility shim or exception wildcard.
- No runtime fallback.
- No active import exception unless it has an explicit exit story.

## Rollback strategy

Revert the test and CS-012 artefacts only; no application behavior is changed.
