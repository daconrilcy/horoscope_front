# Cross Import Guard After Evidence

## State after implementation

- Guard file: `backend/app/tests/unit/test_backend_test_helper_imports.py`
- Updated root expression: `Path(__file__).resolve().parents[3]`
- Expected backend root: `C:\dev\horoscope_front\backend`
- Asserted test roots:
  - `app/tests`
  - `tests`

## Guard behavior

- `test_backend_root_resolves_backend_directory` proves the root is the backend directory and contains `pyproject.toml`.
- `test_backend_test_roots_cover_app_and_backend_tests` proves both backend test roots are in `TEST_ROOTS` and exist.
- `test_backend_tests_do_not_import_executable_test_modules` keeps the AST zero-hit guard for imports from executable `test_*.py` modules.

## Commands run

| Command | Working directory | Result | Evidence |
|---|---|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_test_helper_imports.py` | repo root | PASS | `3 passed in 0.66s`. |
| `.\.venv\Scripts\Activate.ps1; cd backend; rg -n "from app\.tests\.(integration|unit|regression)\.test_|from tests\.(integration|unit|regression)\.test_" app/tests tests -g "test_*.py"` | repo root | PASS | zero hits; `rg` exit status 1 is expected for no matches. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | repo root | PASS | `1242 files left unchanged`. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | `All checks passed!`. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | PASS | `3481 passed, 12 skipped in 682.51s`. |
