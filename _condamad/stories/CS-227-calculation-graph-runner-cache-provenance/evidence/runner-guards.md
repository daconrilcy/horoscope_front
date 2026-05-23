## CS-227 Runner Guards

### Registry and Runtime Surface
- Calculators are resolved only through `CalculationNodeRegistry.get`.
- `CalculationGraphRunner.run` receives an explicit `CalculationGraphDefinition` and
  `CalculationGraphContext`.
- No API, DB, frontend, migration or production natal pipeline integration was added by CS-227.

### Scans
Command:

```powershell
rg -n "CalculationGraphRunner|CalculationGraphContext|CalculationNodeRegistry" backend\app\domain\astrology backend\tests -g "*.py"
```

Result:

```text
PASS: symbols found in calculation_graph_runner.py and test_calculation_graph_runner.py.
```

Command:

```powershell
rg -n "cache:|_cache|global_cache|persistent_cache" backend\app\domain\astrology\runtime\calculation_graph_runner.py
```

Result:

```text
PASS: no matches.
```

Command:

```powershell
rg -n "importlib|eval\(|globals\(|networkx|igraph|graphlib|celery|prefect|airflow" backend\app\domain\astrology backend\tests -g "*.py"
```

Result:

```text
Existing matches outside the CS-227 runner:
- backend\app\domain\astrology\runtime\__init__.py lazy exports.
- backend\app\domain\astrology\interpretation\__init__.py lazy exports.
- backend\tests\llm_orchestration\test_eval_harness.py path fragments.
- backend\tests\unit\domain\astrology\test_natal_calculation_graph_definition.py existing guard literals.
```

Conclusion:

- The CS-227 runner has no dynamic import, `eval`, `globals`, workflow dependency, global cache
  or persistent cache.
- Wide-scan matches are pre-existing and not introduced by this story.
