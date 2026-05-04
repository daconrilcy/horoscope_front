# Validation Plan

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Working directory for backend commands: `backend/`.

## Commands

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted guard and engine tests | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_engine_orchestrator.py` | `backend/` | yes | all tests pass |
| API regression | `pytest -q app/tests/integration/test_daily_prediction_api.py` | `backend/` | yes | all tests pass |
| Removed folder scan | `rg --files app/prediction` | `backend/` | yes | no files; missing path accepted as zero-file evidence |
| Active import scan | `rg -n "from app\.prediction\|import app\.prediction" app tests -g "*.py"` | `backend/` | yes | zero-hit |
| External backend tests import scan | `rg -n "from app\.prediction\|import app\.prediction" ..\backend\tests -g "*.py"` | `backend/` | yes | zero-hit |
| Python importability | `python -c "import importlib.util; assert importlib.util.find_spec('app.prediction') is None; import app.main"` | `backend/` | yes | command exits 0 |
| Lint | `ruff check app tests` | `backend/` | yes | no lint errors |
| Format check | `ruff format --check app tests` | `backend/` | yes | already formatted |
| Full regression | `pytest -q` | `backend/` | conditional | should pass; document timeout if environment prevents completion |
| Diff check | `git diff --check` | repo root | yes | no whitespace errors |
