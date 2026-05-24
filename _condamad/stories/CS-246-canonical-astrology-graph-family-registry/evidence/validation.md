# CS-246 Validation Evidence

All Python commands were run after activating `.\.venv\Scripts\Activate.ps1`.

## Formatting and lint

- `ruff format` on the registry module and targeted registry/API architecture tests - PASS.
- `ruff check backend\tests\unit\domain\astrology\test_astrology_graph_family_registry.py --fix` - PASS, one import-order issue fixed.
- `ruff check backend` - PASS.

## Tests

- Targeted registry, natal graph, API neutrality and runtime boundary pytest - PASS, 23 passed.
- `python -B -m pytest -q backend\tests` - PASS, 881 passed, 201 deselected.

## API neutrality

- `python -B -c "from app.main import app; assert 'AstrologyGraphFamily' not in str(app.openapi())"` - PASS.
- `python -B -c "from app.main import app; assert not any('graph-family' in getattr(r, 'path', '') or 'graph_family' in getattr(r, 'path', '') for r in app.routes)"` - PASS.

## Scans

- Runtime registry family-code scan - PASS, expected matches are limited to runtime registry/natal graph/tests.
- Public API, frontend and migration registry-exposure scan - PASS, no matches; exit code 1 means no matches.
- `rg -n "astrology_graph_family_registry|ASTROLOGY_GRAPH_FAMILY_REGISTRY" backend\app backend\tests -g "*.py"` - PASS, matches only canonical runtime module and targeted tests.

## Review/fix iteration evidence

- Iteration 1 fixed AC4 coverage: `profection_v1` is a temporal family and is now included in the astronomical proof
  blocker test and registry status.
- Iteration 2 fixed blocker evidence completeness: blocked families now carry the explicit cache policy blocker required
  by the source brief.

## Skipped

- `rg ... backend\alembic ...` was not retained because this repository uses `backend\migrations`, and `backend\alembic` does not exist.
