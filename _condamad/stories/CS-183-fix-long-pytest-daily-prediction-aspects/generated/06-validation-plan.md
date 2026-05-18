# Validation Plan

## Tests ciblés

- `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest app/tests/integration/test_daily_prediction_api.py::test_daily_prediction_nominal_200 -q --long`
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest app/tests/integration/test_daily_prediction_api.py -q --long`
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest app/tests/unit/test_natal_structural_v3.py -q`
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest app/tests/regression/test_engine_non_regression.py::test_case_type -q --long`

## Static checks

- `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format <changed files>`
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff check .`

## Broader check

- `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q --long`

Le broader check est coûteux; il sera lancé si les validations ciblées stabilisent la surface.
