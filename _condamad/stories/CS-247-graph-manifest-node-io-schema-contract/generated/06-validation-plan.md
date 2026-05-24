# Validation Plan

## Targeted checks

```bash
python -B -m pytest -q tests/unit/domain/astrology/test_calculation_graph_manifest.py tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py tests/unit/domain/astrology/test_natal_calculation_graph_definition.py tests/architecture/test_api_contract_neutrality.py
```

## Architecture / negative scans

```bash
rg -n "GraphManifest|NodeIOSchema|calculation_graph_manifest" backend/app/domain/astrology/runtime backend/tests/unit/domain/astrology -g "*.py"
rg -n "GraphManifest|NodeIOSchema|graph-manifest|node-io-schema|calculation_graph_manifest" backend/app/api frontend -g "*.py" -g "*.ts" -g "*.tsx"
python -B -c "from app.main import app; assert 'CalculationGraphManifest' not in str(app.openapi())"
python -B -c "from app.main import app; assert not any('graph-manifest' in getattr(r, 'path', '') for r in app.routes)"
```

## Lint / static checks

```bash
ruff check .
```

## Full regression checks

```bash
python -B -m pytest -q tests
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
