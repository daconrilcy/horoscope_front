# Validation Plan

Run after activating `.\.venv\Scripts\Activate.ps1`.

## Targeted checks

```powershell
python -B -m pytest -q backend\tests\unit\domain\astrology\test_calculation_graph_execution_trace.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py backend\tests\architecture\test_api_contract_neutrality.py
```

## Architecture / negative scans

```powershell
rg -n "ExecutionTrace|redaction_policy|provenance_ref" backend\app\domain\astrology\runtime backend\tests\unit\domain\astrology -g "*.py"
rg -n "ExecutionTrace|execution-trace|replay_snapshot|raw_input|raw_output" backend\app\api frontend backend\alembic -g "*.py" -g "*.ts" -g "*.tsx"
rg -n "ExecutionTrace|CalculationGraphExecutionTrace|execution-trace|execution_trace|replay_snapshot" backend\app\api frontend backend\migrations -g "*.py" -g "*.ts" -g "*.tsx"
```

## API neutrality proof

```powershell
$env:PYTHONPATH='backend'
python -B -c "from app.main import app; assert 'ExecutionTrace' not in str(app.openapi())"
python -B -c "from app.main import app; assert not any('execution-trace' in getattr(r, 'path', '') for r in app.routes)"
```

## Lint / static checks

```powershell
ruff format backend\app\domain\astrology\runtime\calculation_graph_execution_trace.py backend\app\domain\astrology\runtime\calculation_graph_runner.py backend\tests\unit\domain\astrology\test_calculation_graph_execution_trace.py backend\tests\unit\domain\astrology\test_calculation_graph_runner.py backend\tests\architecture\test_api_contract_neutrality.py
ruff check backend
```

## Full regression checks

```powershell
python -B -m pytest -q backend\tests
```

## Rule for skipped commands

If a command cannot be run, record exact command, reason, risk and compensating evidence.
