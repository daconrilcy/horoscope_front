# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `regression-guardrails.md` and `story-status.md` modified; CS-017 and CS-018 story directories untracked.
- AGENTS.md considered: `AGENTS.md`.
- Capsule generated: yes, via `condamad_prepare.py` with venv activated.

## Search evidence

- `rg -n "app\.prediction" backend/app/api -g "*.py"`: zero hits before implementation edits.
- Routeurs inspected: `public/predictions.py`, `internal/llm/qa.py`.
- Canonical owners observed: `app.domain.prediction` for projection/snapshot DTOs and `app.services.prediction` for service helpers.

## Implementation notes

- Added AST guard `test_api_prediction_routers_do_not_import_legacy_prediction_namespace`.
- Persisted `openapi-before.json` and `openapi-after.json`; they are identical.
- Added `api-import-audit.md`.
- Updated CS-017 status and task checkboxes to ready for review.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `python -B .agents/skills/condamad-dev-story/scripts/condamad_prepare.py ...` | PASS | venv activated |
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | PASS | 16 passed after format |
| `pytest -q app/tests/integration/test_daily_prediction_api.py` | PASS | 25 passed |
| `pytest -q app/tests/integration/test_horoscope_daily_variant_narration.py` | PASS | 2 passed |
| `rg -n "app\.prediction" app/api -g "*.py"` | PASS | zero hits |
| `ruff format app/tests/unit/test_daily_prediction_guardrails.py` | PASS | 1 file reformatted |
| `pytest -q` | PASS | 3595 passed, 12 skipped |
| `ruff format --check .` | PASS | 1255 files already formatted |
| `ruff check .` | PASS | all checks passed |

## Issues encountered

- First full `pytest -q` attempt timed out after 10 minutes with no useful output; second attempt completed successfully in 11:37.

## Final `git status --short`

- Recorded in `10-final-evidence.md`.
