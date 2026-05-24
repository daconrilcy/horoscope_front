# Validation Evidence — CS-249

## Commands

| Command | Result | Notes |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\CS-249-chart-object-capability-taxonomy-matrix\00-story.md --root .` | PASS_WITH_REPAIR | Script created a derived capsule; generated files were copied into the target CS-249 capsule without changing `00-story.md`. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-249-chart-object-capability-taxonomy-matrix` | PASS | Capsule structure valid after repair. |
| `.\.venv\Scripts\Activate.ps1; ruff format <changed CS-249 python files>` | PASS | Scoped formatting only. |
| `.\.venv\Scripts\Activate.ps1; ruff check <changed CS-249 python files>` | PASS | Import order fixed, then clean. |
| `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -m pytest -q backend\tests\unit\domain\astrology\test_chart_object_capability_taxonomy.py backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\architecture\test_api_contract_neutrality.py` | PASS | `21 passed in 4.03s`. |
| `rg -n "if .*object_type\|\.object_type ==\|match .*object_type" backend\app\domain\astrology -g "*.py"` | PASS | No unmanaged branch matches. Exit code 1 means no matches. |
| `rg -n "LotCalculator\|AsteroidCalculator\|ChironCalculator\|MidpointCalculator" backend\app\domain\astrology backend\tests -g "*.py"` | PASS | No new family calculators. Exit code 1 means no matches. |
| `rg -n "ChartObjectCapability\|decision_status\|needs-user-decision" backend\app\domain\astrology\runtime backend\tests -g "*.py"` | PASS | Matches limited to canonical runtime module and tests/API neutrality guard. |
| `.\.venv\Scripts\Activate.ps1; ruff check backend` | PASS | Backend lint clean. |
| `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -m pytest -q backend\tests` | PASS | `913 passed, 201 deselected in 26.21s`. |
| `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "from app.main import app; assert 'ChartObjectCapabilityTaxonomy' not in str(app.openapi())"` | PASS | Matrix absent from OpenAPI. |
| `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "from app.main import app; assert not any('capability-taxonomy' in getattr(r, 'path', '') or 'capability_taxonomy' in getattr(r, 'path', '') for r in app.routes)"` | PASS | No taxonomy route. |
| `git diff --check` | PASS | Only Git CRLF warnings for existing dirty files. |

## Skipped

- Local dev server was not started: CS-249 is an internal backend-domain matrix with no HTTP behavior change; `TestClient`, `app.routes` and `app.openapi()` covered app import and route availability.
