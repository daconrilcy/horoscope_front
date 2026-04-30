# Cross Import Guard Baseline

## Baseline captured before implementation

- Guard file: `backend/app/tests/unit/test_backend_test_helper_imports.py`
- Current root expression: `Path(__file__).resolve().parents[2]`
- Resolved value for `parents[2]`: `C:\dev\horoscope_front\backend\app`
- Expected backend root: `C:\dev\horoscope_front\backend`

## Consequence

With `BACKEND_ROOT` resolved to `backend/app`, `TEST_ROOTS = (BACKEND_ROOT / "app" / "tests", BACKEND_ROOT / "tests")` does not cover `backend/tests`.

## Commands run

| Command | Working directory | Result | Evidence |
|---|---|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_test_helper_imports.py` | repo root | PASS | `1 passed in 0.54s`; this proves the old guard passes despite incomplete root coverage. |
| `.\.venv\Scripts\Activate.ps1; cd backend; rg -n "from app\.tests\.(integration|unit|regression)\.test_|from tests\.(integration|unit|regression)\.test_" app/tests tests -g "test_*.py"` | repo root | PASS | zero hits; `rg` exit status 1 is expected for no matches. |
| PowerShell parent inspection of `backend\app\tests\unit\test_backend_test_helper_imports.py` | repo root | PASS | `parents[2]=C:\dev\horoscope_front\backend\app`; `parents[3]=C:\dev\horoscope_front\backend`. |
