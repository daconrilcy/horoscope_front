# CS-228 Final Evidence

## Graph Execution

- `build_natal_result` uses `CalculationGraphRunner` with `natal_chart_v1`.
- Natal node resolution is explicit through `build_natal_calculation_node_registry`.
- Node adapters are in `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` and delegate to existing calculators/builders.

## AC Traceability

| AC | Evidence |
|---|---|
| AC1, AC10 | `test_natal_calculation_graph_execution.py::test_build_natal_result_executes_natal_chart_v1_through_runner` |
| AC2 | `test_natal_calculation_graph_execution.py::test_natal_node_registry_resolves_every_graph_calculator` |
| AC3, AC7 | Adapter tests and scan: no dynamic lookup and no legacy projection source in graph adapters. |
| AC4, AC14 | `python -B -m pytest -q backend/tests` -> `833 passed, 201 deselected`. |
| AC5, AC6, AC11 | `test_natal_result_chart_objects.py`, `test_natal_result_contract.py`, public OpenAPI smoke. |
| AC8 | `test_node_failure_message_contains_node_code`. |
| AC9 | `test_build_natal_result_is_thin_graph_facade`. |
| AC12 | `test_api_contract_neutrality.py` and `app.openapi()` evidence. |
| AC13 | No frontend, DB or migration file was intentionally changed by CS-228. |
| AC15 | This evidence directory contains final validation, OpenAPI/routes and graph migration proof. |

## Commands

- `.\.venv\Scripts\Activate.ps1; ruff format <modified python files>` -> OK.
- `.\.venv\Scripts\Activate.ps1; ruff check backend` -> OK.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py backend/tests/integration/astrology` -> `44 passed, 5 deselected`.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend/tests/architecture/test_api_contract_neutrality.py` -> `2 passed`.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend/tests` -> `833 passed, 201 deselected`.
- `rg -n "natal_result\.planet_positions|natal_result\.dignity_results|natal_result\.advanced_conditions" backend/app/domain/astrology/runtime backend/app/domain/astrology/natal_calculation.py -g "*.py"` -> PASS: no matches.
- `rg -n "chart_objects" backend/app/api frontend/src` -> PASS: no matches.
- `rg -n "importlib|eval\(|globals\(|networkx|igraph|graphlib|celery|prefect|airflow" backend/app/domain/astrology/runtime/natal_calculation_nodes.py backend/app/domain/astrology/runtime/natal_calculation_registry.py backend/app/domain/astrology/natal_calculation.py -g "*.py"` -> PASS: no matches.

## Notes

- The requested skill file `.agents/skills/condamad-dev-story/SKILL.md` was not present.
- The capsule did not contain required `generated/*.md` files, and the requested `condamad_prepare.py` / `condamad_validate.py` scripts were not present.
- A broader dynamic-lookup scan over all `backend/app/domain/astrology` still finds pre-existing lazy imports in package `__init__.py` files, outside the CS-228 adapters/registry.

## Final Review Cycle

- 2026-05-23 review iteration 1: no actionable implementation, AC, guardrail or evidence issue found.
- Fresh validations were rerun from the repository root after activating `.venv`.
- 2026-05-23 brief-alignment pass: fixed a validation gap in
  `test_calculation_graph_runner.py` so the runner source guard resolves its module from
  `__file__` and passes when pytest is launched from `backend` after venv activation.
- Fresh validations after the alignment fix:
  - `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` -> OK.
  - `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/unit/domain/astrology/test_calculation_graph_runner.py tests/unit/domain/astrology/test_natal_calculation_graph_definition.py tests/unit/domain/astrology/test_natal_calculation_graph_execution.py tests/unit/domain/astrology/test_natal_result_chart_objects.py tests/unit/domain/astrology/test_natal_result_contract.py tests/unit/domain/astrology/test_chart_object_runtime_architecture.py tests/integration/astrology` -> `44 passed, 5 deselected`.
  - `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/architecture/test_api_contract_neutrality.py` -> `2 passed`.
  - `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests` -> `833 passed, 201 deselected`.
