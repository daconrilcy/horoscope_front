## CS-225 Graph Dependency Scan Evidence

### External Graph Dependencies

Command:

```powershell
rg -n "networkx|igraph|graphlib" backend\app\domain\astrology backend\tests -g "*.py"
```

Result:

```text
PASS: no matches
```

### Calculation Graph Symbols

Command:

```powershell
rg -n "CalculationGraphDefinition|CalculationNodeDefinition" backend\app\domain\astrology\runtime backend\tests -g "*.py"
```

Result:

```text
PASS: matches limited to calculation graph contracts, validator and CS-225 tests.
```

### Dynamic Import / Runtime Execution Guard

Command:

```powershell
rg -n "importlib|__import__|build_natal_result|FastAPI|sqlalchemy|settings|llm|frontend" backend\app\domain\astrology\runtime\calculation_graph_contracts.py backend\app\domain\astrology\runtime\calculation_graph_validator.py
```

Result:

```text
PASS: no matches
```

Note: the wider story scan on `backend\app\domain\astrology\runtime` reports a
pre-existing `importlib` usage in `runtime/__init__.py`; it is outside the new
CS-225 modules and is not used by the calculation graph contracts or validator.

### API / DB / Frontend Surface Scan

Commands:

```powershell
rg -n "calculation_graph|CalculationGraph" backend\app\api frontend -g "*.py" -g "*.ts" -g "*.tsx"
rg -n "calculation_graph|CalculationGraph" backend\migrations -g "*.py"
```

Result:

```text
PASS: no matches
```
