## CS-225 Final Evidence

### Contracts

- Added `CalculationGraphDefinition`, `CalculationNodeDefinition`,
  `CalculationInputDefinition`, `CalculationNodeStatus`,
  `CalculationGraphValidationError` and `CalculationGraphValidationResult`.
- Added explicit node dependencies, optional dependencies and output keys.
- Calculation graph remains distinct from astrological graph in
  `docs/architecture/astrology-calculation-graph.md`.

### AC Traceability

| AC | Evidence |
|---|---|
| AC1 | `test_calculation_graph_contracts.py`: immutable dataclasses exist. |
| AC2 | `test_calculation_graph_contracts.py`: node contract exposes output, dependencies and calculator id. |
| AC3 | `test_calculation_graph_validator.py`: empty node code, duplicate node code, duplicate input key, duplicate output, unknown dependency and cycles rejected. |
| AC4 | No calculator execution; scan on new modules for `importlib`, `__import__` and `build_natal_result` returned no matches. |
| AC5 | Documentation states that calculation graph is declarative and distinct from astrological graph. |
| AC6 | `test_api_contract_neutrality.py` passes; OpenAPI smoke returns 200. |
| AC7 | `test_calculation_graph_validator.py`: deterministic topological order. |
| AC8 | Documentation exists and is asserted by `test_calculation_graph_contracts.py`. |

### Validation

- `.\.venv\Scripts\Activate.ps1; python -B -m ruff format <modified python files>`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B -m ruff check <modified python files>`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B -m ruff check backend`: PASS.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -m ruff format tests\unit\domain\astrology\test_calculation_graph_validator.py`: PASS, 1 file left unchanged.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -m ruff check tests\unit\domain\astrology\test_calculation_graph_validator.py`: PASS.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -m pytest -q tests\unit\domain\astrology\test_calculation_graph_contracts.py tests\unit\domain\astrology\test_calculation_graph_validator.py`: PASS, 15 passed.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -m ruff format --check .`: PASS, 1553 files already formatted.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -m ruff check .`: PASS.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -m pytest -q tests\unit\domain\astrology\test_calculation_graph_contracts.py tests\unit\domain\astrology\test_calculation_graph_validator.py tests\architecture\test_api_contract_neutrality.py`: PASS, 17 passed.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -m pytest -q tests`: PASS, 811 passed, 200 deselected.
- `rg -n "networkx|igraph|graphlib" backend\app\domain\astrology backend\tests -g "*.py"`: PASS, no matches.
- `rg -n "importlib|__import__|build_natal_result|FastAPI|sqlalchemy|settings|llm|frontend" backend\app\domain\astrology\runtime\calculation_graph_contracts.py backend\app\domain\astrology\runtime\calculation_graph_validator.py`: PASS, no matches.
- `rg -n "calculation_graph|CalculationGraph" backend\app\api frontend backend\migrations -g "*.py" -g "*.ts" -g "*.tsx"`: PASS, no matches.

### Scope

- No natal pipeline migration.
- No API, DB, migrations or frontend changes.
- No external graph dependency.
- `condamad-dev-story` skill path and its prepare/validate scripts were absent in this workspace; capsule contained `00-story.md` and `generated/11-story-writing-review.md`.
