# CS-248 Validation Evidence

## Commands Run

| Command | Result | Notes |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\CS-248-calculation-graph-execution-trace-contract\00-story.md --root . --story-key CS-248-calculation-graph-execution-trace-contract --with-optional` | PASS | Capsule generated files created; helper lowercases the generated key but files live in the target capsule on Windows. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-248-calculation-graph-execution-trace-contract` | PASS | Required generated capsule files present. |
| `ruff format backend\app\domain\astrology\runtime\calculation_graph_execution_trace.py backend\app\domain\astrology\runtime\calculation_graph_runner.py backend\tests\unit\domain\astrology\test_calculation_graph_execution_trace.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py backend\tests\architecture\test_api_contract_neutrality.py` | PASS | 3 files reformatted, 2 unchanged. |
| `python -B -m pytest -q backend\tests\unit\domain\astrology\test_calculation_graph_execution_trace.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py backend\tests\architecture\test_api_contract_neutrality.py` | PASS | 23 passed. |
| `rg -n "ExecutionTrace\|redaction_policy\|provenance_ref" backend\app\domain\astrology\runtime backend\tests\unit\domain\astrology -g "*.py"` | PASS | Trace symbols limited to runtime module, runner hook and unit tests. |
| `rg -n "ExecutionTrace\|execution-trace\|replay_snapshot\|raw_input\|raw_output" backend\app\api frontend backend\alembic -g "*.py" -g "*.ts" -g "*.tsx"` | PASS_WITH_LIMITATIONS | No CS-248 trace exposure found. Existing unrelated `raw_output` appears in admin prompts frontend; `backend\alembic` path is absent in this repo. |
| `python -B -c "from app.main import app; assert 'ExecutionTrace' not in str(app.openapi())"` | PASS | Run with `PYTHONPATH=backend`. |
| `python -B -c "from app.main import app; assert not any('execution-trace' in getattr(r, 'path', '') for r in app.routes)"` | PASS | Run with `PYTHONPATH=backend`. |
| `rg -n "ExecutionTrace\|CalculationGraphExecutionTrace\|execution-trace\|execution_trace\|replay_snapshot" backend\app\api frontend backend\migrations -g "*.py" -g "*.ts" -g "*.tsx"` | PASS_WITH_LIMITATIONS | No execution trace public exposure. Existing unrelated LLM replay migrations remain outside CS-248. |
| `ruff check backend` | PASS | All checks passed. |
| `python -B -m pytest -q backend\tests` | PASS | 904 passed, 201 deselected. |
| `git diff --check` | PASS | Only line-ending warnings reported. |
| `python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py .\_condamad\stories\CS-248-calculation-graph-execution-trace-contract\00-story.md` | PASS | Review/fix cycle on 2026-05-24; venv activated. |
| `python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict .\_condamad\stories\CS-248-calculation-graph-execution-trace-contract\00-story.md` | PASS | Review/fix cycle on 2026-05-24; venv activated. |
| `ruff check backend\app\domain\astrology\runtime\calculation_graph_execution_trace.py backend\app\domain\astrology\runtime\calculation_graph_runner.py backend\tests\unit\domain\astrology\test_calculation_graph_execution_trace.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py backend\tests\architecture\test_api_contract_neutrality.py` | PASS | Review/fix cycle on 2026-05-24; all checks passed. |
| `python -B -m pytest -q backend\tests\unit\domain\astrology\test_calculation_graph_execution_trace.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py backend\tests\architecture\test_api_contract_neutrality.py` | PASS | Review/fix cycle on 2026-05-24; 23 passed. |
| `ruff check backend` | PASS | Review/fix cycle on 2026-05-24; all checks passed. |
| `python -B -m pytest -q backend\tests` | PASS | Review/fix cycle on 2026-05-24; 904 passed, 201 deselected. |
| `python -B -c "from app.main import app; assert 'ExecutionTrace' not in str(app.openapi())"` | PASS | Review/fix cycle on 2026-05-24; run with `PYTHONPATH=backend`. |
| `python -B -c "from app.main import app; assert not any('execution-trace' in getattr(r, 'path', '') for r in app.routes)"` | PASS | Review/fix cycle on 2026-05-24; run with `PYTHONPATH=backend`. |
| `rg -n "ExecutionTrace\|redaction_policy\|provenance_ref" backend\app\domain\astrology\runtime backend\tests\unit\domain\astrology -g "*.py"` | PASS | Review/fix cycle on 2026-05-24; symbols limited to runtime module, runner hook and tests. |
| `rg -n "ExecutionTrace\|CalculationGraphExecutionTrace\|execution-trace\|execution_trace\|replay_snapshot" backend\app\api frontend backend\migrations -g "*.py" -g "*.ts" -g "*.tsx"` | PASS_WITH_LIMITATIONS | Review/fix cycle on 2026-05-24; only unrelated LLM replay migrations matched. |

## Notes

- All Python commands were run after activating `.\.venv\Scripts\Activate.ps1`.
- No frontend, API router, DB model or migration file was modified by CS-248.
- Pre-existing worktree changes from CS-246/CS-247 and architecture files remain unrelated and were not reverted.
- Implementation review/fix iteration 1 ended CLEAN with no code correction required.
