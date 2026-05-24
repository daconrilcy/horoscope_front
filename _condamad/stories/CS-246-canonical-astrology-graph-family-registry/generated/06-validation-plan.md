# Validation Plan

## Targeted checks

```bash
python -B -m pytest -q backend\tests\unit\domain\astrology\test_astrology_graph_family_registry.py backend\tests\unit\domain\astrology\test_natal_calculation_graph_definition.py backend\tests\architecture\test_api_contract_neutrality.py
```

## Architecture / negative scans

```bash
rg -n "transit_chart_v1|synastry_chart_v1|natal_chart_v1" backend\app\domain\astrology\runtime backend\tests\unit\domain\astrology -g "*.py"
rg -n "graph-family|graph_family|AstrologyGraphFamily" backend\app\api frontend backend\migrations -g "*.py" -g "*.ts" -g "*.tsx"
rg -n "astrology_graph_family_registry|ASTROLOGY_GRAPH_FAMILY_REGISTRY" backend\app backend\tests -g "*.py"
python -B -m pytest -q backend\tests\architecture\test_astrology_runtime_boundary.py::test_structural_runtime_does_not_expose_interpretive_fields
```

## Lint / static checks

```bash
ruff format backend\app\domain\astrology\runtime\astrology_graph_family_registry.py backend\tests\unit\domain\astrology\test_astrology_graph_family_registry.py backend\tests\architecture\test_api_contract_neutrality.py backend\tests\architecture\test_astrology_runtime_boundary.py
ruff check backend
```

## Full regression checks

```bash
python -B -m pytest -q backend\tests
python -B -c "from app.main import app; assert 'AstrologyGraphFamily' not in str(app.openapi())"
python -B -c "from app.main import app; assert not any('graph-family' in getattr(r, 'path', '') or 'graph_family' in getattr(r, 'path', '') for r in app.routes)"
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
