# Guard after - CS-018

## Final guard

Canonical guard file:

- `backend/app/tests/unit/test_daily_prediction_guardrails.py`

## Enforced invariants

- `test_prediction_legacy_namespace_is_not_importable` blocks an importable
  `app.prediction` package.
- `test_prediction_legacy_namespace_has_no_files` blocks any recreated
  `backend/app/prediction` directory.
- `test_prediction_legacy_import_paths_are_removed` scans runtime and collected
  tests by AST and fails on `from app.prediction...` or `import app.prediction...`.
- `test_api_prediction_routers_do_not_import_legacy_prediction_namespace`
  protects the API prediction boundary.

## Repository scan result before validation

- `rg --files backend/app/prediction`: no files; the path is absent.
- `rg -n "from app\.prediction|import app\.prediction" backend/app backend/tests backend/app/tests -g "*.py"`: zero active Python hits.

## Historical exceptions

Only `_condamad` artifacts keep textual references to `app.prediction` for audit
and story evidence. They are not runtime code and are not collected tests.
