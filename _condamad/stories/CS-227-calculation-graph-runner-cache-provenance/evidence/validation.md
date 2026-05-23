## CS-227 Final Evidence

### Runner
- Added `backend/app/domain/astrology/runtime/calculation_graph_runner.py`.
- Added `CalculationGraphRunner`, `CalculationGraphContext`, `CalculationNodeRegistry`,
  `CalculationNodeResult`, `CalculationGraphExecutionResult` and
  `CalculationGraphExecutionError`.
- Graph validation runs before calculators through `validate_calculation_graph_definition`.
- Linear and convergent fake graphs execute in deterministic topological order.

### Cache and Provenance
- Cache is local to one `run` call and only reuses outputs already present in the
  per-run value map.
- Initial context values are copied into an immutable mapping and are not mutated.
- Node results expose `input_keys`, `output_key`, `calculator`, `cache_hit` and stable
  runtime errors.
- Provenance exposes `node_code`, `input_keys`, `output_key`, `output` and `calculator`
  by node.

### AC Traceability
| AC | Evidence |
|---|---|
| AC1 | `test_linear_graph_executes_in_topological_order_and_collects_outputs`; `execution_order`. |
| AC2 | `test_invalid_graph_is_validated_before_any_calculator_runs`; calculator calls remain empty. |
| AC3 | `CalculationNodeRegistry`; `test_unknown_calculator_has_stable_error`; runner source guard. |
| AC4 | `result.outputs` assertions in linear and convergent tests. |
| AC5 | `test_missing_required_runtime_input_has_stable_error`. |
| AC6 | `test_cache_is_local_to_one_run_and_initial_context_is_not_mutated`; runner cache scan. |
| AC7 | `test_provenance_exposes_node_inputs_output_and_calculator`. |
| AC8 | `test_cache_is_local_to_one_run_and_initial_context_is_not_mutated`. |
| AC9 | Full backend tests passed; no intentional change to existing astrology calculators/services by this story. |
| AC10 | `backend/tests/architecture/test_api_contract_neutrality.py`; API evidence file. |
| AC11 | Runner source guard and targeted scans; no dynamic lookup in runner. |
| AC12 | Linear graph unit test. |
| AC13 | Convergent graph unit test. |
| AC14 | `test_unknown_calculator_has_stable_error`. |
| AC15 | `test_failing_calculator_has_stable_error`. |
| AC16 | No frontend, DB or migration file modified by this story. |

### Validations
- Review-fix iteration 1 corrected stale evidence/test wording, then reran:
  - `.\.venv\Scripts\Activate.ps1; ruff format backend\tests\architecture\test_api_contract_neutrality.py`
    - PASS: 1 file left unchanged.
  - `.\.venv\Scripts\Activate.ps1; ruff check backend\tests\architecture\test_api_contract_neutrality.py backend\app\domain\astrology\runtime\calculation_graph_runner.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py`
    - PASS: all checks passed.
  - `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\unit\domain\astrology\test_calculation_graph_runner.py backend\tests\unit\domain\astrology\test_calculation_graph_validator.py backend\tests\architecture\test_api_contract_neutrality.py`
    - PASS: 21 passed.
  - `.\.venv\Scripts\Activate.ps1; ruff check backend`
    - PASS: all checks passed.
  - `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests`
    - PASS: 827 passed, 200 deselected.
- `.\.venv\Scripts\Activate.ps1; ruff format backend\app\domain\astrology\runtime\calculation_graph_runner.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py`
  - PASS: 2 files reformatted, then unchanged after final edit.
- `.\.venv\Scripts\Activate.ps1; ruff check backend\app\domain\astrology\runtime\calculation_graph_runner.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py`
  - PASS: all checks passed.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\unit\domain\astrology\test_calculation_graph_runner.py`
  - PASS: 9 passed.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\unit\domain\astrology\test_calculation_graph_runner.py backend\tests\unit\domain\astrology\test_calculation_graph_validator.py backend\tests\architecture\test_api_contract_neutrality.py`
  - PASS: 21 passed.
- `.\.venv\Scripts\Activate.ps1; ruff check backend`
  - PASS: all checks passed.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests`
  - PASS: 827 passed, 200 deselected.

### Notes
- The requested skill path `.agents/skills/condamad-review-fix-story/SKILL.md` was absent.
- The CS-227 capsule had no `generated/` files and the requested prepare/validate scripts were absent.
- A wide dynamic-import scan reports pre-existing lazy exports in runtime and interpretation
  package `__init__.py` files plus existing test literals. The new runner has no dynamic import,
  magical lookup, global cache or workflow dependency.
