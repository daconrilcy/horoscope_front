# Implementation Plan

## Repository findings

- The routeurs `public/predictions.py` and `internal/llm/qa.py` already consume `app.domain.prediction.persisted_snapshot` and `app.domain.prediction.public_projection` in the current worktree.
- `rg -n "app\.prediction" backend/app/api -g "*.py"` returns zero hits.
- The existing guard file checks global legacy prediction imports, but did not include a dedicated API-scope guard for CS-017.

## Selected approach

- Preserve route behavior and imports because the current code is already converged to canonical owners.
- Add an AST guard dedicated to `backend/app/api/**/*.py` so `app.prediction` cannot return under API.
- Persist OpenAPI snapshots and an import audit in the story capsule.
- Complete CONDAMAD traceability and final evidence.

## Files to modify

- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/**`
- `_condamad/stories/story-status.md`

## Files to delete

- None.

## Tests to add or update

- Add `test_api_prediction_routers_do_not_import_legacy_prediction_namespace`.

## Risk assessment

- Low runtime risk: no API handler behavior is changed.
- Main review risk: the route import convergence appears pre-existing in the dirty worktree; evidence records current canonical state and adds regression protection.

## Rollback strategy

- Revert the guard test and CONDAMAD CS-017 artifacts if review rejects this story closure; no runtime code rollback is required.
